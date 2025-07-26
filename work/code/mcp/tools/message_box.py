import sys
from pathlib import Path

# Add mcp directory to path to allow imports
current_dir = Path(__file__).parent.parent
sys.path.insert(0, str(current_dir))

from utils.context_decorator import context_aware_tool

@context_aware_tool(
    name="send_message",
    description="Sends a message to another user.",
    parameters={
        "type": "object",
        "properties": {
            "sender": {"type": "string", "description": "The name of the sender."},
            "recipient": {"type": "string", "description": "The name of the recipient."},
            "message": {"type": "string", "description": "The content of the message."},
        },
        "required": ["sender", "recipient", "message"],
    },
)
async def send_message(sender: str, recipient: str, message: str) -> str:
    """
    Sends a message to another user.
    """
    try:
        server = sys.modules["work.code.mcp.mcp_server"].global_server_instance
        if not server.mongo_storage:
            return "Error: MongoStorage not initialized."
        server.mongo_storage.save_message(sender, recipient, message)
        return "Message sent successfully."
    except Exception as e:
        return f"Error sending message: {e}"

@context_aware_tool(
    name="read_messages",
    description="Reads messages for a user.",
    parameters={
        "type": "object",
        "properties": {
            "recipient": {"type": "string", "description": "The name of the recipient."},
        },
        "required": ["recipient"],
    },
)
async def read_messages(recipient: str) -> str:
    """
    Reads messages for a user.
    """
    try:
        server = sys.modules["work.code.mcp.mcp_server"].global_server_instance
        if not server.mongo_storage:
            return "Error: MongoStorage not initialized."
        messages = server.mongo_storage.get_messages(recipient)
        return str(messages)
    except Exception as e:
        return f"Error reading messages: {e}"
