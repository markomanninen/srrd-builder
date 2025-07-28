import sys
import os
from pathlib import Path

# Add mcp directory to path to allow imports
current_dir = Path(__file__).parent.parent
sys.path.insert(0, str(current_dir))

from utils.context_decorator import context_aware_tool

# Access to server instance for mongo_storage (following existing pattern)
_server_instance = None

def set_server_instance(server):
    """Set the server instance for accessing mongo_storage"""
    global _server_instance
    _server_instance = server

def get_mongo_storage():
    """Get MongoDB storage from server instance"""
    if _server_instance and hasattr(_server_instance, 'mongo_storage'):
        return _server_instance.mongo_storage
    return None

@context_aware_tool(
    name="register_user",
    description="Register a new user in the messaging system.",
    parameters={
        "type": "object",
        "properties": {
            "username": {"type": "string", "description": "The username to register."},
        },
        "required": ["username"],
    },
)
async def register_user(username: str) -> str:
    """
    Register a new user in the messaging system.
    """
    try:
        mongo_storage = get_mongo_storage()
        if not mongo_storage:
            return "Error: MongoStorage not initialized."
        result = mongo_storage.register_user(username)
        return result
    except Exception as e:
        return f"Error registering user: {e}"

@context_aware_tool(
    name="discover_users",
    description="Discover all registered users in the messaging system.",
    parameters={
        "type": "object",
        "properties": {},
        "required": [],
    },
)
async def discover_users() -> str:
    """
    Discover all registered users in the messaging system.
    """
    try:
        mongo_storage = get_mongo_storage()
        if not mongo_storage:
            return "Error: MongoStorage not initialized."
        users = mongo_storage.get_all_users()
        if not users:
            return "No users found. Register users first with register_user tool."
        user_list = [f"- {user['username']} (last active: {user['last_active']})" for user in users]
        return f"Found {len(users)} users:\n" + "\n".join(user_list)
    except Exception as e:
        return f"Error discovering users: {e}"

@context_aware_tool(
    name="subscribe_to_user",
    description="Subscribe to another user to enable messaging.",
    parameters={
        "type": "object",
        "properties": {
            "subscriber": {"type": "string", "description": "The username of the subscriber."},
            "target": {"type": "string", "description": "The username to subscribe to."},
        },
        "required": ["subscriber", "target"],
    },
)
async def subscribe_to_user(subscriber: str, target: str) -> str:
    """
    Subscribe to another user to enable messaging.
    """
    try:
        mongo_storage = get_mongo_storage()
        if not mongo_storage:
            return "Error: MongoStorage not initialized."
        result = mongo_storage.subscribe_user(subscriber, target)
        return result
    except Exception as e:
        return f"Error subscribing to user: {e}"

@context_aware_tool(
    name="unsubscribe_from_user",
    description="Unsubscribe from another user.",
    parameters={
        "type": "object",
        "properties": {
            "subscriber": {"type": "string", "description": "The username of the subscriber."},
            "target": {"type": "string", "description": "The username to unsubscribe from."},
        },
        "required": ["subscriber", "target"],
    },
)
async def unsubscribe_from_user(subscriber: str, target: str) -> str:
    """
    Unsubscribe from another user.
    """
    try:
        mongo_storage = get_mongo_storage()
        if not mongo_storage:
            return "Error: MongoStorage not initialized."
        result = mongo_storage.unsubscribe_user(subscriber, target)
        return result
    except Exception as e:
        return f"Error unsubscribing from user: {e}"

@context_aware_tool(
    name="get_my_subscriptions",
    description="Get list of users you are subscribed to.",
    parameters={
        "type": "object",
        "properties": {
            "username": {"type": "string", "description": "Your username."},
        },
        "required": ["username"],
    },
)
async def get_my_subscriptions(username: str) -> str:
    """
    Get list of users you are subscribed to.
    """
    try:
        mongo_storage = get_mongo_storage()
        if not mongo_storage:
            return "Error: MongoStorage not initialized."
        subscriptions = mongo_storage.get_subscriptions(username)
        if not subscriptions:
            return f"No subscriptions found for {username}. Use subscribe_to_user to add subscriptions."
        sub_list = [f"- {sub['target']} (subscribed: {sub['subscribed_at']})" for sub in subscriptions]
        return f"Subscriptions for {username}:\n" + "\n".join(sub_list)
    except Exception as e:
        return f"Error getting subscriptions: {e}"

@context_aware_tool(
    name="send_message",
    description="Sends a message to another user (requires subscription).",
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
    Sends a message to another user (requires subscription).
    """
    try:
        mongo_storage = get_mongo_storage()
        if not mongo_storage:
            return "Error: MongoStorage not initialized."
        message_id = mongo_storage.save_message(sender, recipient, message)
        
        # Get web server settings
        web_host = os.environ.get('WEB_SERVER_HOST', 'localhost')
        web_port = os.environ.get('WEB_SERVER_PORT', '8080')
        
        return f"Message sent successfully. ID: {message_id}\nView content: srrd message view {message_id} --user {recipient}\nWeb GUI: http://{web_host}:{web_port}/messaging.html#view=message&messageId={message_id}&viewer={recipient}"
    except Exception as e:
        return f"Error sending message: {e}"

@context_aware_tool(
    name="send_message_with_file",
    description="Sends a message with file attachment to another user.",
    parameters={
        "type": "object",
        "properties": {
            "sender": {"type": "string", "description": "The name of the sender."},
            "recipient": {"type": "string", "description": "The name of the recipient."},
            "message": {"type": "string", "description": "The content of the message."},
            "file_path": {"type": "string", "description": "Path to the file to attach."},
        },
        "required": ["sender", "recipient", "message", "file_path"],
    },
)
async def send_message_with_file(sender: str, recipient: str, message: str, file_path: str) -> str:
    """
    Sends a message with file attachment to another user.
    """
    try:
        mongo_storage = get_mongo_storage()
        if not mongo_storage:
            return "Error: MongoStorage not initialized."
            
        # Check if file exists
        if not os.path.exists(file_path):
            return f"Error: File {file_path} not found."
            
        # Read file content
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                file_content = f.read()
        except UnicodeDecodeError:
            # Try binary mode for non-text files
            with open(file_path, 'rb') as f:
                file_content = f.read().decode('utf-8', errors='ignore')
                
        # Create attachment
        filename = os.path.basename(file_path)
        attachment = {
            'filename': filename,
            'content': file_content,
            'size': len(file_content),
            'mime_type': 'text/plain'  # Simple mime type detection
        }
        
        message_id = mongo_storage.save_message(sender, recipient, message, [attachment])
        
        # Get web server settings
        web_host = os.environ.get('WEB_SERVER_HOST', 'localhost')
        web_port = os.environ.get('WEB_SERVER_PORT', '8080')
        
        return f"Message with file sent successfully. ID: {message_id}\nAttached: {filename} ({len(file_content)} bytes)\nView content: srrd message view {message_id} --user {recipient}\nWeb GUI: http://{web_host}:{web_port}/messaging.html#view=message&messageId={message_id}&viewer={recipient}"
    except Exception as e:
        return f"Error sending message with file: {e}"

@context_aware_tool(
    name="read_messages",
    description="Reads messages for a user with CLI links for exact content.",
    parameters={
        "type": "object",
        "properties": {
            "recipient": {"type": "string", "description": "The name of the recipient."},
            "unread_only": {"type": "boolean", "description": "Show only unread messages.", "default": False},
            "sender": {"type": "string", "description": "Filter by specific sender."},
        },
        "required": ["recipient"],
    },
)
async def read_messages(recipient: str, unread_only: bool = False, sender: str = None) -> str:
    """
    Reads messages for a user with CLI links for exact content.
    """
    try:
        mongo_storage = get_mongo_storage()
        if not mongo_storage:
            return "Error: MongoStorage not initialized."
        messages = mongo_storage.get_messages(recipient, unread_only, sender)
        
        if not messages:
            filter_str = ""
            if unread_only:
                filter_str += " unread"
            if sender:
                filter_str += f" from {sender}"
            return f"No{filter_str} messages found for {recipient}."
            
        # Get web server settings
        web_host = os.environ.get('WEB_SERVER_HOST', 'localhost')
        web_port = os.environ.get('WEB_SERVER_PORT', '8080')
        
        message_list = []
        for msg in messages[:10]:  # Limit to 10 most recent
            status = "📬 UNREAD" if not msg['read_status'] else "📭 read"
            
            # Show full message content
            message_content = msg['message']
            
            # Add attachment content if present
            if msg.get('attachments'):
                attachment_details = []
                for att in msg['attachments']:
                    attachment_details.append(f"📎 {att['filename']} ({att['size']} bytes):\n{att['content']}")
                if attachment_details:
                    message_content += f"\n\nAttachments:\n" + "\n\n".join(attachment_details)
            
            message_list.append(
                f"{status} {msg['message_id']} from {msg['sender']} at {msg['timestamp']}\n"
                f"Message: {message_content}\n"
                f"CLI: srrd message view {msg['message_id']} --user {recipient} | Web: http://{web_host}:{web_port}/messaging.html#view=message&messageId={msg['message_id']}&viewer={recipient}"
            )
            
        total_count = len(messages)
        unread_count = mongo_storage.get_unread_count(recipient)
        
        return f"Messages for {recipient} ({unread_count} unread, {total_count} total):\n\n" + "\n\n".join(message_list)
    except Exception as e:
        return f"Error reading messages: {e}"

@context_aware_tool(
    name="mark_message_read",
    description="Mark a message as read.",
    parameters={
        "type": "object",
        "properties": {
            "message_id": {"type": "string", "description": "The ID of the message to mark as read."},
            "recipient": {"type": "string", "description": "The recipient username."},
        },
        "required": ["message_id", "recipient"],
    },
)
async def mark_message_read(message_id: str, recipient: str) -> str:
    """
    Mark a message as read.
    """
    try:
        mongo_storage = get_mongo_storage()
        if not mongo_storage:
            return "Error: MongoStorage not initialized."
        result = mongo_storage.mark_message_read(message_id, recipient)
        return result
    except Exception as e:
        return f"Error marking message as read: {e}"

@context_aware_tool(
    name="get_unread_count",
    description="Get count of unread messages for a user.",
    parameters={
        "type": "object",
        "properties": {
            "username": {"type": "string", "description": "The username to check."},
        },
        "required": ["username"],
    },
)
async def get_unread_count(username: str) -> str:
    """
    Get count of unread messages for a user.
    """
    try:
        mongo_storage = get_mongo_storage()
        if not mongo_storage:
            return "Error: MongoStorage not initialized."
        count = mongo_storage.get_unread_count(username)
        return f"{username} has {count} unread messages."
    except Exception as e:
        return f"Error getting unread count: {e}"

@context_aware_tool(
    name="view_message_web",
    description="Get message content for web viewing (returns JSON format).",
    parameters={
        "type": "object",
        "properties": {
            "message_id": {"type": "string", "description": "The ID of the message to view."},
            "viewer": {"type": "string", "description": "Username of the person viewing the message (to mark as read)."},
        },
        "required": ["message_id"],
    },
)
async def view_message_web(message_id: str, viewer: str = None) -> str:
    """
    Get message content for web viewing (returns JSON format).
    """
    try:
        mongo_storage = get_mongo_storage()
        if not mongo_storage:
            return '{"error": "MongoStorage not initialized"}'
        
        message = mongo_storage.get_message_by_id(message_id)
        if not message:
            return f'{{"error": "Message {message_id} not found"}}'
        
        # Mark message as read if the viewer is the recipient and it's unread
        if viewer and viewer == message['recipient'] and not message['read_status']:
            try:
                mongo_storage.mark_message_read(message_id, viewer)
                message['read_status'] = True  # Update the message dict
                from datetime import datetime
                message['read_at'] = datetime.utcnow()
            except Exception as e:
                # Don't fail the whole operation if marking as read fails
                pass
        
        # Convert datetime objects to strings for JSON serialization
        message_json = dict(message)
        if 'timestamp' in message_json:
            message_json['timestamp'] = message_json['timestamp'].isoformat()
        if 'read_at' in message_json and message_json['read_at']:
            message_json['read_at'] = message_json['read_at'].isoformat()
        
        import json
        return json.dumps(message_json, default=str)
    except Exception as e:
        return f'{{"error": "Error viewing message: {e}"}}'

@context_aware_tool(
    name="list_messages_web",
    description="List messages for web viewing with filters (returns JSON format).",
    parameters={
        "type": "object",
        "properties": {
            "username": {"type": "string", "description": "Username to list messages for."},
            "unread_only": {"type": "boolean", "description": "Show only unread messages.", "default": False},
            "sender": {"type": "string", "description": "Filter by specific sender."},
            "limit": {"type": "integer", "description": "Maximum number of messages.", "default": 20},
        },
        "required": ["username"],
    },
)
async def list_messages_web(username: str, unread_only: bool = False, sender: str = None, limit: int = 20) -> str:
    """
    List messages for web viewing with filters (returns JSON format).
    """
    try:
        mongo_storage = get_mongo_storage()
        if not mongo_storage:
            return '{"error": "MongoStorage not initialized"}'
            
        messages = mongo_storage.get_messages(username, unread_only, sender)
        
        # Limit results
        if len(messages) > limit:
            messages = messages[:limit]
        
        unread_count = mongo_storage.get_unread_count(username)
        
        # Convert datetime objects to strings
        messages_json = []
        for msg in messages:
            msg_json = dict(msg)
            if 'timestamp' in msg_json:
                msg_json['timestamp'] = msg_json['timestamp'].isoformat()
            if 'read_at' in msg_json and msg_json['read_at']:
                msg_json['read_at'] = msg_json['read_at'].isoformat()
            messages_json.append(msg_json)
        
        result = {
            "messages": messages_json,
            "total_count": len(messages),
            "unread_count": unread_count,
            "showing_limited": len(messages) > limit
        }
        
        import json
        return json.dumps(result, default=str)
    except Exception as e:
        return f'{{"error": "Error listing messages: {e}"}}'

@context_aware_tool(
    name="get_conversation_web",
    description="Get conversation between two users for web viewing (returns JSON format).",
    parameters={
        "type": "object",
        "properties": {
            "user1": {"type": "string", "description": "First user."},
            "user2": {"type": "string", "description": "Second user."},
        },
        "required": ["user1", "user2"],
    },
)
async def get_conversation_web(user1: str, user2: str) -> str:
    """
    Get conversation between two users for web viewing (returns JSON format).
    """
    try:
        mongo_storage = get_mongo_storage()
        if not mongo_storage:
            return '{"error": "MongoStorage not initialized"}'
        
        # Get messages between the two users (both directions)
        messages1 = mongo_storage.get_messages(recipient=user1, sender=user2)
        messages2 = mongo_storage.get_messages(recipient=user2, sender=user1)
        
        # Combine and sort by timestamp
        all_messages = messages1 + messages2
        all_messages.sort(key=lambda x: x['timestamp'])
        
        # Convert datetime objects to strings
        messages_json = []
        for msg in all_messages:
            msg_json = dict(msg)
            if 'timestamp' in msg_json:
                msg_json['timestamp'] = msg_json['timestamp'].isoformat()
            if 'read_at' in msg_json and msg_json['read_at']:
                msg_json['read_at'] = msg_json['read_at'].isoformat()
            messages_json.append(msg_json)
        
        result = {
            "conversation": messages_json,
            "participant1": user1,
            "participant2": user2,
            "message_count": len(messages_json)
        }
        
        import json
        return json.dumps(result, default=str)
    except Exception as e:
        return f'{{"error": "Error getting conversation: {e}"}}'

def register_message_tools(server):
    """Register message tools with the MCP server"""
    # Set server instance for accessing mongo_storage
    set_server_instance(server)
    # Basic messaging tools
    server.register_tool(
        "register_user",
        "Register a new user in the messaging system",
        {
            "type": "object",
            "properties": {
                "username": {"type": "string", "description": "The username to register"}
            },
            "required": ["username"]
        },
        register_user
    )
    
    server.register_tool(
        "discover_users", 
        "Discover all registered users in the messaging system",
        {
            "type": "object",
            "properties": {},
            "required": []
        },
        discover_users
    )
    
    server.register_tool(
        "subscribe_to_user",
        "Subscribe to another user to enable messaging",
        {
            "type": "object", 
            "properties": {
                "subscriber": {"type": "string", "description": "The username of the subscriber"},
                "target": {"type": "string", "description": "The username to subscribe to"}
            },
            "required": ["subscriber", "target"]
        },
        subscribe_to_user
    )
    
    server.register_tool(
        "unsubscribe_from_user",
        "Unsubscribe from another user", 
        {
            "type": "object",
            "properties": {
                "subscriber": {"type": "string", "description": "The username of the subscriber"},
                "target": {"type": "string", "description": "The username to unsubscribe from"}
            },
            "required": ["subscriber", "target"]
        },
        unsubscribe_from_user
    )
    
    server.register_tool(
        "get_my_subscriptions",
        "Get list of users you are subscribed to",
        {
            "type": "object",
            "properties": {
                "username": {"type": "string", "description": "Your username"}
            },
            "required": ["username"]
        },
        get_my_subscriptions
    )
    
    # Core messaging tools
    server.register_tool(
        "send_message",
        "Send a message to another user (requires subscription)",
        {
            "type": "object",
            "properties": {
                "sender": {"type": "string", "description": "The name of the sender"},
                "recipient": {"type": "string", "description": "The name of the recipient"},
                "message": {"type": "string", "description": "The content of the message"}
            },
            "required": ["sender", "recipient", "message"]
        },
        send_message
    )
    
    server.register_tool(
        "send_message_with_file",
        "Send a message with file attachment to another user",
        {
            "type": "object",
            "properties": {
                "sender": {"type": "string", "description": "The name of the sender"},
                "recipient": {"type": "string", "description": "The name of the recipient"},
                "message": {"type": "string", "description": "The content of the message"},
                "file_path": {"type": "string", "description": "Path to the file to attach"}
            },
            "required": ["sender", "recipient", "message", "file_path"]
        },
        send_message_with_file
    )
    
    server.register_tool(
        "read_messages",
        "Read messages for a user with CLI links for exact content",
        {
            "type": "object",
            "properties": {
                "recipient": {"type": "string", "description": "The name of the recipient"},
                "unread_only": {"type": "boolean", "description": "Show only unread messages", "default": False},
                "sender": {"type": "string", "description": "Filter by specific sender"}
            },
            "required": ["recipient"]
        },
        read_messages
    )
    
    server.register_tool(
        "mark_message_read",
        "Mark a message as read",
        {
            "type": "object",
            "properties": {
                "message_id": {"type": "string", "description": "The ID of the message to mark as read"},
                "recipient": {"type": "string", "description": "The recipient username"}
            },
            "required": ["message_id", "recipient"]
        },
        mark_message_read
    )
    
    server.register_tool(
        "get_unread_count",
        "Get count of unread messages for a user",
        {
            "type": "object",
            "properties": {
                "username": {"type": "string", "description": "The username to check"}
            },
            "required": ["username"]
        },
        get_unread_count
    )
    
    # Web interface tools (JSON responses)
    server.register_tool(
        "view_message_web",
        "Get message content for web viewing (returns JSON format)",
        {
            "type": "object",
            "properties": {
                "message_id": {"type": "string", "description": "The ID of the message to view"},
                "viewer": {"type": "string", "description": "Username of the person viewing the message (to mark as read)"}
            },
            "required": ["message_id"]
        },
        view_message_web
    )
    
    server.register_tool(
        "list_messages_web",
        "List messages for web viewing with filters (returns JSON format)",
        {
            "type": "object",
            "properties": {
                "username": {"type": "string", "description": "Username to list messages for"},
                "unread_only": {"type": "boolean", "description": "Show only unread messages", "default": False},
                "sender": {"type": "string", "description": "Filter by specific sender"},
                "limit": {"type": "integer", "description": "Maximum number of messages", "default": 20}
            },
            "required": ["username"]
        },
        list_messages_web
    )
    
    server.register_tool(
        "get_conversation_web",
        "Get conversation between two users for web viewing (returns JSON format)",
        {
            "type": "object",
            "properties": {
                "user1": {"type": "string", "description": "First user"},
                "user2": {"type": "string", "description": "Second user"}
            },
            "required": ["user1", "user2"]
        },
        get_conversation_web
    )
