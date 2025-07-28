# Enhanced Message System Implementation Plan

## Current State Analysis
This is a **fresh implementation** - no existing messages to migrate. The current message box implementation (`work/code/mcp/tools/message_box.py`) provides basic messaging with:
- `send_message(sender, recipient, message)` - Basic message sending
- `read_messages(recipient)` - Read all messages for a user  
- Simple MongoDB storage via `MongoStorage` class

**Critical Missing Features:**
- No flood protection or rate limiting
- No way to view raw message/file content (LLM clients summarize/synthesize)
- No browser GUI or CLI access for exact content

## Enhanced System Requirements

### Core Functionality Gaps
1. **User Management**: No user registration or discovery system
2. **Recipient Selection**: Users cannot see available recipients 
3. **Subscription System**: No way to manage who can message whom
4. **Message Status**: No read/unread tracking
5. **File Attachments**: Cannot share research files with messages
6. **Message Filtering**: No search or filtering capabilities
7. **Flood Protection**: No rate limiting or spam prevention
8. **Content Access**: No way to view exact message/file content (LLM clients modify content)

### Use Case Flow (From Zero State)

#### Initial Setup
1. **User A (First User)**:
   - Starts Claude with MCP server
   - Claude calls `register_user("researcher_alice")` 
   - User registered but no recipients available

2. **User B Joins**:
   - Starts Claude instance with same MongoDB
   - Claude calls `register_user("researcher_bob")`
   - Calls `discover_users()` → sees ["researcher_alice"]
   - Calls `subscribe_to_user("researcher_alice")` to enable messaging

#### Messaging Workflow
3. **Send Message**:
   - User B: "Send message to researcher_alice about findings"
   - Claude calls `send_message("researcher_bob", "researcher_alice", "Found patterns...")`

4. **Receive Messages**:
   - User A calls `read_messages("researcher_alice")` → sees unread message
   - User A calls `mark_message_read(message_id)` to update status

5. **File Sharing**:
   - User A: "Share analysis.txt with researcher_bob"
   - Claude calls `send_message_with_file("researcher_alice", "researcher_bob", "Analysis results", "/path/to/analysis.txt")`
   - File content stored in message (research is local-only)
   - Tool returns: "Message sent. View exact content: `srrd message view msg_12345` or http://localhost:8080/message/msg_12345"

6. **Content Access**:
   - User B receives summary in Claude but needs exact content
   - Uses CLI: `srrd message view msg_12345` → shows raw message + file content
   - Or opens browser: `http://localhost:8080/message/msg_12345` → web GUI view

## Implementation Plan

### Phase 1: Core Infrastructure (High Priority)
1. **Flood Protection System**:
   - Rate limiting: max 10 messages/minute per user
   - Message size limits: 10MB message, 50MB attachments
   - Subscription limits: max 100 subscriptions per user
   - Database indexes for performance

2. **Content Access Infrastructure**:
   - Extend `web_server.py` with message viewing endpoints
   - Add CLI commands: `srrd message view <id>`, `srrd message list <user>`
   - MCP tools return CLI command links for exact content access

3. **Database Schema Enhancement**:
   - `users` collection: Store registered users + rate limit tracking
   - `subscriptions` collection: Manage user relationships  
   - `messages` collection: Add fields for status, attachments, timestamps, unique IDs

4. **New MCP Tools**:
   - `register_user(username)` - Register new user in system
   - `discover_users()` - List all registered users
   - `get_my_subscriptions(username)` - Show subscribed users for recipient selection
   - `subscribe_to_user(subscriber, target)` - Enable messaging to user (with flood check)
   - `unsubscribe_from_user(subscriber, target)` - Disable messaging

### Phase 2: Enhanced Messaging (High Priority)
5. **Message Status System**:
   - `mark_message_read(message_id)` - Update message status
   - `get_unread_count(username)` - Count unread messages  
   - Update `read_messages()` to show read/unread status + CLI links

6. **File Attachment Support**:
   - `send_message_with_file(sender, recipient, message, file_path)` - Attach file content (with flood check)
   - All message tools return: "Message ID: msg_12345. View: `srrd message view msg_12345`"
   - Store file content in database (local research sharing)

### Phase 3: Advanced Features (Medium Priority)
7. **Message Filtering & Search**:
   - `filter_messages(recipient, sender=None, unread_only=False, date_range=None)` + CLI links
   - `search_messages(recipient, query)` - Search message content + CLI links

8. **Message Management**:
   - `delete_message(message_id)` - Remove message (with confirmation)
   - `get_conversation(user1, user2)` - Get message thread + CLI links

### Phase 4: Testing and Documentation (Low Priority)
8. **Testing**:
   - Unit tests for all new MCP tools
   - Integration tests for messaging workflows
   - MongoDB mock testing setup

9. **Documentation**:
   - Update project README with messaging system usage
   - Create user guide for messaging features
   - Document MongoDB setup requirements

## Technical Specifications

### Database Schema

#### Users Collection
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

#### Subscriptions Collection  
```json
{
  "_id": ObjectId,
  "subscriber": "researcher_alice",
  "target": "researcher_bob", 
  "subscribed_at": ISODate
}
```

#### Enhanced Messages Collection
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

### Environment Variables
```env
# MongoDB Configuration
MONGO_URI=mongodb://localhost:27017/
MONGO_DB_NAME=mcp_messages
MONGO_COLLECTION_PREFIX=srrd_

# Message System Settings  
MAX_MESSAGE_SIZE=10485760
MAX_ATTACHMENT_SIZE=52428800
MESSAGE_RETENTION_DAYS=365
DAILY_MESSAGE_LIMIT=100
RATE_LIMIT_WINDOW=60
MAX_SUBSCRIPTIONS=100

# Web Server Settings
WEB_SERVER_PORT=8080
WEB_SERVER_HOST=localhost
```

### MCP Tool Definitions
All tools will use `@context_aware_tool` decorator and follow existing patterns in `message_box.py`.

**Tool Response Format:**
All messaging tools return CLI command links for exact content access:
```
"Message sent successfully. ID: msg_12345
View content: srrd message view msg_12345
Web GUI: http://localhost:8080/message/msg_12345"
```

### CLI Commands to Add
```bash
# View exact message content
srrd message view <message_id>

# List messages for user  
srrd message list <username> [--unread] [--from=<sender>]

# View conversation between users
srrd message conversation <user1> <user2>

# Message statistics
srrd message stats <username>
```

### Web Server Endpoints to Add
```
GET /message/<message_id>     - View message with attachments
GET /messages/<username>      - List user's messages  
GET /conversation/<user1>/<user2> - View conversation
GET /api/message/<message_id> - JSON API for message data
```

## Implementation Tasks

### High Priority
- [ ] Update `requirements.txt` with MongoDB dependencies
- [ ] Document required `.env` variables for MongoDB setup  
- [ ] Implement user registration tool
- [ ] Implement user discovery tool
- [ ] Implement subscription management tools
- [ ] Enhance send_message tool with file attachment support

### Medium Priority  
- [ ] Add message status tracking tools
- [ ] Add message filtering and search tools
- [ ] Update MongoDB schema for new collections

### Low Priority
- [ ] Create comprehensive test suite for messaging system
- [ ] Update project documentation with messaging system usage

## Success Criteria
1. Users can discover and subscribe to other researchers
2. Messages support file attachments for sharing research
3. Message status tracking works (read/unread)
4. All functionality accessible via MCP tools callable by Claude
5. System works with multiple concurrent users on shared MongoDB
6. Comprehensive test coverage for all messaging features

## Success Criteria
1. Users can discover and subscribe to other researchers with flood protection
2. Messages support file attachments for sharing research with size limits
3. Message status tracking works (read/unread) with rate limiting
4. All functionality accessible via MCP tools callable by Claude
5. **Critical**: CLI commands and web GUI provide exact message/file content access
6. **Critical**: MCP tools return CLI command links for content access
7. System handles multiple concurrent users with proper rate limiting
8. Comprehensive test coverage for all messaging and flood protection features

## Implementation Status

### ✅ Completed Features

**🔧 MCP Tools (13 total):**
- **User Management**: `register_user`, `discover_users`, `subscribe_to_user`, `unsubscribe_from_user`, `get_my_subscriptions`
- **Core Messaging**: `send_message`, `send_message_with_file`, `read_messages`, `mark_message_read`, `get_unread_count`
- **Web Interface**: `view_message_web`, `list_messages_web`, `get_conversation_web` (JSON responses)

**💻 CLI Commands:**
- `srrd message view <message_id>` - View exact message + file content
- `srrd message list <username> [--unread] [--from=<sender>]` - List with filters
- `srrd message conversation <user1> <user2>` - View conversation thread
- `srrd message stats <username>` - Message statistics

**🌐 Web Interface:**
- `http://localhost:8080/frontend/messaging.html` - Full web GUI
- URL hash parameters for deep linking (e.g., `#view=message&messageId=msg_12345`)
- WebSocket integration with MCP server
- Responsive design with real-time content access

**🛡️ Security & Limits:**
- Rate limiting: 10 messages/minute, 100/day per user
- File size limits: 10MB message, 50MB attachments
- Subscription limits: max 100 per user
- MongoDB indexes for performance

**📱 Frontend Integration:**
- Added to research framework under "Research Collaboration" act
- Two categories: "Research Messaging" and "User Management"
- Tools accessible via `frontend/index.html` interface

**✅ Testing:**
- Comprehensive pytest suite for all messaging functionality
- CLI command testing with mocks
- MCP registration testing
- Rate limiting and edge case coverage

### 🔧 Architecture Notes
- Uses existing `@context_aware_tool` decorator pattern
- Follows same server instance access pattern as other tools
- MongoDB storage integrated with existing MCP server
- No global variables or architectural changes needed

## Implementation Notes
- **Fresh implementation** - no migration needed
- **Flood protection** prevents abuse with proper rate limiting
- **Content access** via CLI/web ensures users get exact content (LLM clients modify content)
- All MCP tool responses include CLI command links for exact content viewing
- **Consistent patterns** - follows existing tool registration and server access patterns

---

## NEXT PHASE: User Authentication System

### Current Authentication Gap
The current system requires manual `--user` parameters and `viewer` inputs, which creates UX friction and security concerns:
- CLI: `srrd message view msg_123 --user markom`
- Web GUI: Manual username entry in forms
- MCP Tools: Manual sender/viewer parameters

### Authentication System Requirements

#### 1. **User Registration with Password**
**Goal**: Replace manual username entry with secure login system

**Storage**: Global SRRD configuration (~/.srrd/config.json)
```json
{
  "messaging": {
    "current_user": {
      "username": "markom",
      "password_hash": "bcrypt$2b$12$...",
      "registered_at": "2025-01-28T10:30:00Z",
      "default_settings": {
        "auto_mark_read": true,
        "web_host": "localhost",
        "web_port": "8080"
      }
    }
  }
}
```

#### 2. **Authentication Flow**
**Initial Setup**:
1. `srrd message register` - Register username/password (first time)
2. `srrd message login` - Authenticate existing user
3. `srrd message logout` - Clear authentication
4. `srrd message whoami` - Show current user

**Session Management**:
- Authentication persists across CLI/Web sessions
- Password stored as bcrypt hash in global config
- Session timeout configurable (default: 24h)

#### 3. **Interface Simplification**

**CLI Commands (No --user needed)**:
```bash
# After login, user context is automatic
srrd message view msg_123                    # Auto-uses logged-in user
srrd message list                           # Shows current user's messages  
srrd message send alice "Hello"             # Auto-sets sender
```

**Web GUI (No manual username entry)**:
```javascript
// Current user loaded automatically from server
http://localhost:8080/messaging.html#view=message&messageId=msg_123
// No viewer parameter needed - uses authenticated user
```

**MCP Tools (Auto-context)**:
```python
# Tools automatically use authenticated user context
@context_aware_tool(name="read_messages", ...)
async def read_messages(unread_only: bool = False, sender: str = None) -> str:
    current_user = get_authenticated_user()  # From config
    # recipient parameter removed - uses current_user
```

#### 4. **Implementation Plan**

**Simple Direct Implementation**:
1. **Authentication Service**:
   ```python
   # work/code/mcp/utils/auth_manager.py
   class MessageAuthManager:
       def register_user(username, password) -> bool
       def authenticate(username, password) -> bool  
       def get_current_user() -> Optional[str]
       def logout() -> bool
   ```

2. **CLI Authentication Commands**:
   ```bash
   srrd message register         # Username/password setup
   srrd message login           # Authenticate user  
   srrd message logout          # Clear session
   srrd message whoami          # Show current user
   ```

3. **Update All Interfaces**:
   - **MCP Tools**: Remove sender/recipient parameters, use authenticated user
   - **CLI Commands**: Remove `--user` parameters completely
   - **Web GUI**: Remove username input fields, auto-load from server

**User Experience**:
```bash
$ srrd message register
Username: markom
Password: ********
✅ User registered and logged in

$ srrd message view msg_123
✅ [Message content displayed - auto-uses markom]
```

#### 6. **Technical Specifications**

**Config File Structure**:
```json
{
  "messaging_auth": {
    "current_session": {
      "username": "markom", 
      "session_token": "uuid4_token",
      "expires_at": "2025-01-29T10:30:00Z"
    },
    "users": {
      "markom": {
        "password_hash": "bcrypt$2b$12$...",
        "created_at": "2025-01-28T10:30:00Z",
        "last_login": "2025-01-28T12:00:00Z",
        "settings": {
          "auto_mark_read": true,
          "default_web_port": "8080"
        }
      }
    }
  }
}
```

**Environment Variables**:
```env
# Authentication Settings
MESSAGE_AUTH_ENABLED=true
MESSAGE_SESSION_TIMEOUT=86400  # 24 hours
MESSAGE_PASSWORD_MIN_LENGTH=8
MESSAGE_MAX_LOGIN_ATTEMPTS=3
```

#### 5. **Success Criteria**
- ✅ Users register once with username/password
- ✅ All CLI commands work without `--user` parameters
- ✅ Web GUI loads user context automatically
- ✅ MCP tools use authenticated user context
- ✅ Session management with secure password storage

#### 6. **Implementation Tasks**

**Simple Task List**:
- [ ] Create `MessageAuthManager` class with bcrypt hashing
- [ ] Add authentication CLI commands (`register/login/logout/whoami`)
- [ ] Store user credentials in global SRRD config
- [ ] Update ALL MCP tools to use authenticated user (remove manual parameters)
- [ ] Update ALL CLI commands to remove `--user` parameters
- [ ] Update web GUI to auto-load user context from server

**Result**: Clean, simple authentication system where you register/login once and everything works automatically.