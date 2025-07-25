"""
SRRD Tool Command - Execute MCP tools directly from the CLI
"""

import argparse
import asyncio
import importlib
import json
import sys
from pathlib import Path


# Helper to find the 'work/code/mcp' directory
def find_mcp_path():
    package_root = Path(__file__).parent.parent.parent.parent
    mcp_path = package_root / "work" / "code" / "mcp"
    return mcp_path


# Ensure MCP modules can be imported
mcp_path = find_mcp_path()
if str(mcp_path) not in sys.path:
    sys.path.insert(0, str(mcp_path))

# We only need the server class to inspect its tools
from mcp_server import ClaudeMCPServer


def get_server_tools_schema() -> list:
    """Instantiates the server in-memory to get the list of tools and their schemas."""
    server = ClaudeMCPServer()
    tools_info = server.list_tools_mcp()
    return tools_info.get("tools", [])


def generate_parser_from_schema(tool_schema: dict) -> argparse.ArgumentParser:
    """Dynamically creates an ArgumentParser for a tool from its JSON schema."""
    parser = argparse.ArgumentParser(
        prog=f"srrd tool {tool_schema['name']}",
        description=tool_schema["description"],
        formatter_class=argparse.RawTextHelpFormatter,
    )

    properties = tool_schema.get("inputSchema", {}).get("properties", {})
    required = tool_schema.get("inputSchema", {}).get("required", [])

    for param_name, details in properties.items():
        arg_name = f'--{param_name.replace("_", "-")}'
        arg_kwargs = {
            "help": details.get("description", ""),
            "required": param_name in required,
        }

        param_type = details.get("type")
        if param_type == "boolean":
            arg_kwargs["action"] = "store_true"
        elif param_type == "integer":
            arg_kwargs["type"] = int
        elif param_type == "number":
            arg_kwargs["type"] = float
        elif param_type in ["object", "array"]:
            arg_kwargs["type"] = json.loads
            arg_kwargs[
                "help"
            ] += '\n(Note: provide as a JSON string, e.g., \'{"key":"value"}\')'
        else:  # Default to string
            arg_kwargs["type"] = str

        if "default" in details:
            arg_kwargs["default"] = details["default"]

        parser.add_argument(arg_name, **arg_kwargs)

    return parser


async def run_tool(tool_name: str, tool_args: dict):
    """Dynamically imports and runs an async MCP tool."""
    # This dynamic import loop makes the CLI robust to new tool modules
    tool_found = False
    tool_modules = [
        "research_planning",
        "quality_assurance",
        "document_generation",
        "search_discovery",
        "storage_management",
        "methodology_advisory",
        "novel_theory_development",
        "research_continuity",
    ]

    for module_name in tool_modules:
        try:
            tool_module = importlib.import_module(f"tools.{module_name}")

            # Tools can be named `tool_name` or `tool_name_tool`
            func_name = tool_name
            if not hasattr(tool_module, func_name):
                func_name = f"{tool_name}_tool"

            if hasattr(tool_module, func_name):
                func_to_call = getattr(tool_module, func_name)

                print(f"🚀 Executing tool '{tool_name}'...")
                # The @context_aware decorator handles project context automatically
                result = await func_to_call(**tool_args)

                print("\n✅ Tool executed successfully. Result:")
                print("-" * 40)
                # Pretty-print the result
                if isinstance(result, (dict, list)):
                    print(json.dumps(result, indent=2))
                elif isinstance(result, str) and result.strip().startswith(("{", "[")):
                    try:
                        print(json.dumps(json.loads(result), indent=2))
                    except json.JSONDecodeError:
                        print(result)  # Print as-is if not valid JSON
                else:
                    print(result)
                print("-" * 40)
                tool_found = True
                break
        except ImportError:
            continue

    if not tool_found:
        print(
            f"❌ Error: Could not locate the handler function for tool '{tool_name}'."
        )
        return 1

    return 0


def handle_tool(args):
    """Handle 'srrd tool' command using dynamic schema discovery."""
    tool_name = args.tool_name
    tool_args_list = args.tool_args

    print("🔍 Discovering available tools from server...")
    all_schemas = get_server_tools_schema()
    print(f"✅ Discovered {len(all_schemas)} tools.")

    tool_schema = next((t for t in all_schemas if t["name"] == tool_name), None)

    if not tool_schema:
        print(f"❌ Error: Tool '{tool_name}' not found on the server.")
        print("\nAvailable tools are:")
        for t in sorted(all_schemas, key=lambda x: x["name"]):
            print(f"  - {t['name']}")
        return 1

    parser = generate_parser_from_schema(tool_schema)

    try:
        parsed_args = parser.parse_args(tool_args_list)
        args_dict = vars(parsed_args)
    except SystemExit:
        # argparse calls sys.exit() on --help or error, which is the desired behavior.
        return 0
    except argparse.ArgumentError as e:
        print(f"❌ Argument Error: {e}")
        return 1

    try:
        return asyncio.run(run_tool(tool_name, args_dict))
    except Exception as e:
        print(f"❌ An error occurred while running the tool: {e}")
        return 1
