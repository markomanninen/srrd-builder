#!/usr/bin/env python3
"""
SRRD-Builder CLI Main Entry Point
"""

import argparse
import sys
from pathlib import Path


def create_parser():
    """Create the main argument parser"""
    parser = argparse.ArgumentParser(
        prog="srrd", description="Scientific Research Requirement Document Builder"
    )

    parser.add_argument("--version", action="version", version="%(prog)s 0.1.0")

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # srrd init command
    init_parser = subparsers.add_parser(
        "init", help="Initialize SRRD in current Git repository"
    )
    init_parser.add_argument(
        "--domain",
        choices=["physics", "cs", "bio", "general"],
        default="general",
        help="Research domain (default: general)",
    )
    init_parser.add_argument(
        "--template",
        choices=["minimal", "standard", "full"],
        default="standard",
        help="Template complexity (default: standard)",
    )
    init_parser.add_argument(
        "--force",
        action="store_true",
        help="Force initialization even if .srrd directory exists",
    )

    # srrd switch command
    switch_parser = subparsers.add_parser(
        "switch", help="Switch MCP context to current project"
    )

    # srrd reset command
    reset_parser = subparsers.add_parser(
        "reset", help="Reset/clear global MCP launcher (disable all MCP tools)"
    )

    # srrd generate command with subcommands
    generate_parser = subparsers.add_parser(
        "generate", help="LaTeX compilation and build automation"
    )

    generate_subparsers = generate_parser.add_subparsers(
        dest="subcommand", help="Generation actions"
    )

    # generate pdf subcommand
    pdf_parser = generate_subparsers.add_parser(
        "pdf", help="Compile LaTeX document to PDF"
    )
    pdf_parser.add_argument("input", help="Input .tex file to compile")
    pdf_parser.add_argument(
        "--output", help="Output directory (default: same as input)"
    )

    # generate template subcommand
    template_parser = generate_subparsers.add_parser(
        "template", help="Generate LaTeX template (no AI content)"
    )
    template_parser.add_argument(
        "template_type",
        choices=["proposal", "paper", "thesis"],
        help="Type of template to generate",
    )
    template_parser.add_argument("--title", required=True, help="Document title")
    template_parser.add_argument(
        "--output",
        default="work/drafts/",
        help="Output directory (default: work/drafts/)",
    )

    # srrd status command
    status_parser = subparsers.add_parser(
        "status", help="Check SRRD server and project status"
    )

    # srrd publish command
    publish_parser = subparsers.add_parser(
        "publish", help="Move finalized work from drafts to publications"
    )
    publish_parser.add_argument(
        "draft_name", help="Name of draft to publish (without .tex extension)"
    )
    publish_parser.add_argument(
        "--version", default="v1.0", help="Publication version (default: v1.0)"
    )
    publish_parser.add_argument(
        "--force", action="store_true", help="Overwrite existing publication"
    )

    # srrd configure command
    configure_parser = subparsers.add_parser(
        "configure", help="Configure MCP server for IDEs (Claude Desktop, VS Code)"
    )
    configure_parser.add_argument(
        "--claude", action="store_true", help="Configure Claude Desktop"
    )
    configure_parser.add_argument(
        "--vscode", action="store_true", help="Configure VS Code"
    )
    configure_parser.add_argument(
        "--all", action="store_true", help="Configure all supported IDEs"
    )
    configure_parser.add_argument(
        "--force", action="store_true", help="Overwrite existing configuration"
    )
    configure_parser.add_argument(
        "--status",
        dest="show_status",
        action="store_true",
        help="Show current configuration status",
    )

    tool_parser = subparsers.add_parser(
        "tool", help="Execute a context-aware MCP tool directly from the CLI"
    )
    tool_parser.add_argument(
        "tool_name",
        help="The name of the tool to execute (e.g., clarify_research_goals)",
    )
    tool_parser.add_argument(
        "tool_args",
        nargs=argparse.REMAINDER,
        help='Arguments for the tool (e.g., --research-area "AI"). Use --help for tool-specific options.',
    )

    return parser


def main():
    """Main CLI entry point"""
    parser = create_parser()

    # Special handling for the 'tool' command to allow for dynamic help messages
    if len(sys.argv) > 2 and sys.argv[1] == "tool" and "--help" in sys.argv:
        # Let the tool handler manage the --help message
        from srrd_builder.cli.commands.tool import handle_tool

        # We need a dummy args object for the handler
        args = argparse.Namespace(
            command="tool", tool_name=sys.argv[2], tool_args=["--help"]
        )
        return handle_tool(args)

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    # Import command handlers
    if args.command == "init":
        from srrd_builder.cli.commands.init import handle_init

        return handle_init(args)
    elif args.command == "switch":
        from srrd_builder.cli.commands.switch import handle_switch

        return handle_switch(args)
    elif args.command == "reset":
        from srrd_builder.cli.commands.reset import handle_reset

        return handle_reset(args)
    elif args.command == "generate":
        from srrd_builder.cli.commands.generate import handle_generate

        return handle_generate(args)
    elif args.command == "status":
        from srrd_builder.cli.commands.status import handle_status

        return handle_status(args)
    elif args.command == "publish":
        from srrd_builder.cli.commands.publish import handle_publish

        return handle_publish(args)
    elif args.command == "configure":
        from srrd_builder.cli.commands.configure import handle_configure

        return handle_configure(args)
    elif args.command == "tool":
        from srrd_builder.cli.commands.tool import handle_tool

        return handle_tool(args)
    else:
        print(f"Unknown command: {args.command}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
