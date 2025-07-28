# SRRD-Builder Message System Documentation

## Overview

The SRRD-Builder messaging system provides comprehensive communication tools for research collaboration. It enables researchers to register, discover other users, send messages with file attachments, and manage communication through both MCP tools and web interfaces.

## System Architecture

The messaging system consists of:

- **13 MCP Tools** for programmatic access via Claude
- **CLI Commands** for exact content viewing (`srrd message`)
- **Web Interface** (`messaging.html`) for browser-based access
- **MongoDB Storage** with rate limiting and flood protection
- **WebSocket Integration** for real-time updates

## Features

### ✅ Core Functionality

#### User Management
- **User Registration**: Register new users in the system
- **User Discovery**: Find all registered users for collaboration
- **Subscription System**: Subscribe/unsubscribe to enable messaging between users
- **Subscription Management**: View and manage your subscriptions

#### Messaging
- **Basic Messaging**: Send text messages between subscribed users
- **File Attachments**: Share research files with messages (up to 50MB)
- **Message Status**: Track read/unread status for all messages
- **Message Filtering**: Filter by sender, read status, date ranges
- **Content Access**: View exact message content via CLI and web interface

#### Security & Limits
- **Rate Limiting**: 10 messages/minute, 100 messages/day per user
- **Size Limits**: 10MB message content, 50MB file attachments
- **Subscription Limits**: Maximum 100 subscriptions per user
- **Flood Protection**: Prevents message abuse and spam

## MCP Tools Reference

### User Management Tools

#### `register_user(username)`
Register a new user in the messaging system.
- **Parameters**: `username` (string) - Username to register
- **Returns**: Registration confirmation or last_active update

#### `discover_users()`
List all registered users in the system.
- **Returns**: List of all users with last activity timestamps

#### `subscribe_to_user(subscriber, target)`
Subscribe to a user to enable messaging.
- **Parameters**: 
  - `subscriber` (string) - Your username
  - `target` (string) - Username to subscribe to
- **Returns**: Subscription confirmation
- **Note**: Required before sending messages

#### `unsubscribe_from_user(subscriber, target)`
Unsubscribe from a user to disable messaging.
- **Parameters**:
  - `subscriber` (string) - Your username  
  - `target` (string) - Username to unsubscribe from
- **Returns**: Unsubscription confirmation

#### `get_my_subscriptions(username)`
View all your current subscriptions.
- **Parameters**: `username` (string) - Your username
- **Returns**: List of subscribed users with timestamps

### Messaging Tools

#### `send_message(sender, recipient, message)`
Send a text message to another user.
- **Parameters**:
  - `sender` (string) - Your username
  - `recipient` (string) - Target username
  - `message` (string) - Message content
- **Returns**: Message ID with CLI and web links for exact content access
- **Note**: Requires subscription to recipient

#### `send_message_with_file(sender, recipient, message, file_path)`
Send a message with file attachment.
- **Parameters**:
  - `sender` (string) - Your username
  - `recipient` (string) - Target username
  - `message` (string) - Message content
  - `file_path` (string) - Path to file to attach
- **Returns**: Message ID with file info and access links
- **Limits**: Files up to 50MB, supports all text and binary formats

#### `read_messages(username, unread_only=False, sender=None)`
Read messages for a user with filtering options.
- **Parameters**:
  - `username` (string) - Username to read messages for
  - `unread_only` (boolean, optional) - Show only unread messages
  - `sender` (string, optional) - Filter by specific sender
- **Returns**: Formatted list of messages with CLI/web access links

#### `mark_message_read(message_id, username)`
Mark a specific message as read.
- **Parameters**:
  - `message_id` (string) - Message ID to mark as read
  - `username` (string) - Your username
- **Returns**: Confirmation of read status update

#### `get_unread_count(username)`
Get count of unread messages.
- **Parameters**: `username` (string) - Username to check
- **Returns**: Number of unread messages

### Web Interface Tools

#### `view_message_web(message_id)`
Get message data for web interface display.
- **Parameters**: `message_id` (string) - Message ID to view
- **Returns**: JSON formatted message data with attachments

#### `list_messages_web(username, unread_only=False, sender=None)`
Get messages list for web interface.
- **Parameters**: Same as `read_messages`
- **Returns**: JSON formatted message list

#### `get_conversation_web(user1, user2)`
Get conversation thread between two users.
- **Parameters**:
  - `user1` (string) - First username
  - `user2` (string) - Second username  
- **Returns**: JSON formatted conversation thread

## CLI Commands

### `srrd message view <message_id>`
View exact content of a specific message including file attachments.

```bash
srrd message view msg_12345
```

### `srrd message list <username> [--unread] [--from=<sender>] [--limit=<n>]`
List messages for a user with filtering options.

```bash
# List all messages
srrd message list alice

# List only unread messages
srrd message list alice --unread

# List messages from specific sender
srrd message list alice --from=bob

# Limit number of messages shown
srrd message list alice --limit=10
```

### `srrd message conversation <user1> <user2>`
View conversation thread between two users.

```bash
srrd message conversation alice bob
```

### `srrd message stats <username>`
Show messaging statistics for a user.

```bash
srrd message stats alice
```

## Web Interface

### Accessing the Web Interface

1. Start the web server:
   ```bash
   python3 web_server.py --project-path /path/to/project --port 8080
   ```

2. Open messaging interface:
   ```
   http://localhost:8080/frontend/messaging.html
   ```

### URL Parameters

The web interface supports hash-based parameters for deep linking:

- **View Message**: `#view=message&messageId=msg_12345`
- **List Messages**: `#view=list&username=alice&unread=true`
- **Conversation**: `#view=conversation&user1=alice&user2=bob`

### Features

- **Real-time Updates**: WebSocket connection for live message updates
- **File Download**: Direct download of message attachments
- **Responsive Design**: Works on desktop and mobile devices
- **Search & Filter**: Client-side message filtering and search
- **Message Status**: Visual indicators for read/unread messages

## Database Schema

### Collections

#### users
```json
{
  "_id": ObjectId,
  "username": "researcher_alice",
  "registered_at": ISODate,
  "last_active": ISODate,
  "rate_limit": {
    "messages_sent_today": 0,
    "last_message_time": ISODate,
    "subscription_count": 0
  }
}
```

#### subscriptions
```json
{
  "_id": ObjectId,
  "subscriber": "researcher_alice",
  "target": "researcher_bob",
  "subscribed_at": ISODate
}
```

#### messages
```json
{
  "_id": ObjectId,
  "message_id": "msg_12345",
  "sender": "researcher_alice", 
  "recipient": "researcher_bob",
  "message": "Content here...",
  "timestamp": ISODate,
  "read_status": false,
  "read_at": ISODate,
  "size_bytes": 2048,
  "attachments": [
    {
      "filename": "analysis.txt",
      "content": "file content as string",
      "size": 1024,
      "mime_type": "text/plain"
    }
  ]
}
```

## Configuration

### Environment Variables

```env
# MongoDB Configuration
MONGO_URI=mongodb://localhost:27017/
MONGO_DB_NAME=mcp_messages
MONGO_COLLECTION_PREFIX=srrd_

# Message System Settings
MAX_MESSAGE_SIZE=10485760        # 10MB
MAX_ATTACHMENT_SIZE=52428800     # 50MB
MESSAGE_RETENTION_DAYS=365
DAILY_MESSAGE_LIMIT=100
RATE_LIMIT_WINDOW=60            # seconds
MAX_SUBSCRIPTIONS=100

# Web Server Settings
WEB_SERVER_PORT=8080
WEB_SERVER_HOST=localhost
```

### Required Dependencies

```txt
pymongo>=4.0.0
python-dotenv>=0.19.0
```

## Setup Instructions

### 1. Install Dependencies
```bash
pip install pymongo python-dotenv
```

### 2. Configure MongoDB
```bash
# Install MongoDB locally or use MongoDB Atlas
# Ensure MongoDB is running on localhost:27017
```

### 3. Configure Environment
```bash
# Copy example environment file
cp .env.example .env

# Edit .env with your MongoDB settings
MONGO_URI=mongodb://localhost:27017/
MONGO_DB_NAME=mcp_messages
```

### 4. Start the System
```bash
# Start MCP server with web interface
python3 web_server.py --project-path /path/to/project --port 8080
```

### 5. Test Functionality
```bash
# Test MCP server integration
python3 test_mcp_server_integration.py

# Test CLI commands
srrd message --help

# Test messaging integration (requires MongoDB)
python3 -m pytest work/tests/integration/test_messaging_integration.py
```

## Usage Examples

### Basic Workflow

1. **Register Users**:
   ```python
   # Via Claude with MCP tools
   register_user("researcher_alice")
   register_user("researcher_bob")
   ```

2. **Discover and Subscribe**:
   ```python
   discover_users()  # See available users
   subscribe_to_user("alice", "bob")  # Alice subscribes to Bob
   ```

3. **Send Messages**:
   ```python
   send_message("alice", "bob", "Hello Bob!")
   send_message_with_file("alice", "bob", "Here's the analysis", "/path/to/file.txt")
   ```

4. **Read Messages**:
   ```python
   read_messages("bob")  # Bob reads messages
   mark_message_read("msg_12345", "bob")  # Mark as read
   ```

5. **Access Exact Content**:
   ```bash
   # Via CLI for exact content
   srrd message view msg_12345
   
   # Via web browser
   http://localhost:8080/frontend/messaging.html#view=message&messageId=msg_12345
   ```

## Testing

### Unit Tests
```bash
python3 -m pytest work/tests/unit/test_enhanced_message_box.py -v
```

### Integration Tests
```bash
# Requires MongoDB running
python3 -m pytest work/tests/integration/test_messaging_integration.py -v
```

### MCP Server Test
```bash
python3 test_mcp_server_integration.py
```

## Troubleshooting

### Common Issues

1. **"MongoDB not available"**
   - Ensure MongoDB is running on localhost:27017
   - Check MONGO_URI in .env file
   - Install pymongo: `pip install pymongo`

2. **"Tool not found"**
   - Restart MCP server to reload tools
   - Check tools are registered: `python3 test_mcp_server_integration.py`

3. **"Rate limit exceeded"**
   - Wait for rate limit window to reset
   - Check DAILY_MESSAGE_LIMIT in .env
   - Use `get_unread_count` to check status

4. **"Not subscribed to user"**
   - Use `subscribe_to_user` before sending messages
   - Check subscriptions with `get_my_subscriptions`

5. **File attachment errors**
   - Check file exists and is readable
   - Verify file size under MAX_ATTACHMENT_SIZE (50MB)
   - Ensure proper file permissions

### Debugging

Enable debug logging:
```bash
export SRRD_DEBUG=1
python3 web_server.py --project-path /path/to/project --port 8080
```

Check server logs for detailed error information.

## Limitations

- **Local Storage**: All data stored in local MongoDB (research collaboration focus)
- **File Size**: 50MB attachment limit to prevent storage issues
- **Rate Limiting**: Daily limits prevent abuse but may limit heavy usage
- **MongoDB Required**: Full functionality requires MongoDB installation
- **Single Server**: No distributed/clustered setup support

## Security Considerations

- **No Authentication**: System assumes trusted local environment  
- **File Access**: CLI and web tools can access any message content
- **Rate Limiting**: Prevents flooding but not sophisticated attacks
- **Local Network**: Web interface accessible to local network by default

For production use, implement proper authentication and access controls.

## Support

For issues and feature requests:
1. Check troubleshooting section above
2. Review test files for usage examples
3. Examine MCP tool implementations in `work/code/mcp/tools/message_box.py`
4. Create GitHub issues for bugs or enhancement requests