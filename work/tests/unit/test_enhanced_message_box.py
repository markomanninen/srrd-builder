#!/usr/bin/env python3
"""
Enhanced Message Box Tests
Tests for the enhanced messaging system with user registration, subscriptions, and file attachments.
"""

import unittest
import asyncio
import os
import tempfile
from unittest.mock import MagicMock, patch, Mock
from datetime import datetime, timedelta

# Import the tools to test
from work.code.mcp.tools.message_box import (
    register_user, discover_users, subscribe_to_user, unsubscribe_from_user,
    get_my_subscriptions, send_message, send_message_with_file, read_messages,
    mark_message_read, get_unread_count
)

class TestEnhancedMessageBox(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures"""
        # Mock server and mongo_storage
        self.mock_server = MagicMock()
        self.mock_mongo_storage = MagicMock()
        self.mock_server.mongo_storage = self.mock_mongo_storage
        
        # Mock environment variables
        self.env_patch = patch.dict(os.environ, {
            'WEB_SERVER_HOST': 'localhost',
            'WEB_SERVER_PORT': '8080'
        })
        self.env_patch.start()
        
    def tearDown(self):
        """Clean up after tests"""
        self.env_patch.stop()

    def test_register_user_success(self):
        """Test successful user registration"""
        self.mock_mongo_storage.register_user.return_value = "User alice registered successfully"
        
        with patch('work.code.mcp.tools.message_box.get_mongo_storage', return_value=self.mock_mongo_storage):
            result = asyncio.run(register_user("alice"))
            
            self.mock_mongo_storage.register_user.assert_called_once_with("alice")
            self.assertEqual(result, "User alice registered successfully")

    def test_register_user_existing(self):
        """Test registering existing user updates last_active"""
        self.mock_mongo_storage.register_user.return_value = "User alice updated last_active"
        
        with patch('work.code.mcp.tools.message_box.get_mongo_storage', return_value=self.mock_mongo_storage):
            result = asyncio.run(register_user("alice"))
            
            self.mock_mongo_storage.register_user.assert_called_once_with("alice")
            self.assertEqual(result, "User alice updated last_active")

    def test_discover_users_success(self):
        """Test discovering users"""
        mock_users = [
            {"username": "alice", "last_active": datetime.utcnow()},
            {"username": "bob", "last_active": datetime.utcnow()}
        ]
        self.mock_mongo_storage.get_all_users.return_value = mock_users
        
        with patch('work.code.mcp.tools.message_box.get_mongo_storage', return_value=self.mock_mongo_storage):
            result = asyncio.run(discover_users())
            
            self.mock_mongo_storage.get_all_users.assert_called_once()
            self.assertIn("Found 2 users:", result)
            self.assertIn("alice", result)
            self.assertIn("bob", result)

    def test_discover_users_empty(self):
        """Test discovering users when none exist"""
        self.mock_mongo_storage.get_all_users.return_value = []
        
        with patch('work.code.mcp.tools.message_box.get_mongo_storage', return_value=self.mock_mongo_storage):
            result = asyncio.run(discover_users())
            
            self.mock_mongo_storage.get_all_users.assert_called_once()
            self.assertEqual(result, "No users found. Register users first with register_user tool.")

    def test_subscribe_to_user_success(self):
        """Test successful subscription"""
        self.mock_mongo_storage.subscribe_user.return_value = "Successfully subscribed to bob"
        
        with patch('work.code.mcp.tools.message_box.get_mongo_storage', return_value=self.mock_mongo_storage):
            result = asyncio.run(subscribe_to_user("alice", "bob"))
            
            self.mock_mongo_storage.subscribe_user.assert_called_once_with("alice", "bob")
            self.assertEqual(result, "Successfully subscribed to bob")

    def test_subscribe_to_user_already_subscribed(self):
        """Test subscribing to already subscribed user"""
        self.mock_mongo_storage.subscribe_user.side_effect = Exception("Already subscribed to bob")
        
        with patch('work.code.mcp.tools.message_box.get_mongo_storage', return_value=self.mock_mongo_storage):
            result = asyncio.run(subscribe_to_user("alice", "bob"))
            
            self.assertIn("Error subscribing to user: Already subscribed to bob", result)

    def test_unsubscribe_from_user_success(self):
        """Test successful unsubscription"""
        self.mock_mongo_storage.unsubscribe_user.return_value = "Successfully unsubscribed from bob"
        
        with patch('work.code.mcp.tools.message_box.get_mongo_storage', return_value=self.mock_mongo_storage):
            result = asyncio.run(unsubscribe_from_user("alice", "bob"))
            
            self.mock_mongo_storage.unsubscribe_user.assert_called_once_with("alice", "bob")
            self.assertEqual(result, "Successfully unsubscribed from bob")

    def test_get_my_subscriptions_success(self):
        """Test getting subscriptions"""
        mock_subscriptions = [
            {"target": "bob", "subscribed_at": datetime.utcnow()},
            {"target": "charlie", "subscribed_at": datetime.utcnow()}
        ]
        self.mock_mongo_storage.get_subscriptions.return_value = mock_subscriptions
        
        with patch('work.code.mcp.tools.message_box.get_mongo_storage', return_value=self.mock_mongo_storage):
            result = asyncio.run(get_my_subscriptions("alice"))
            
            self.mock_mongo_storage.get_subscriptions.assert_called_once_with("alice")
            self.assertIn("Subscriptions for alice:", result)
            self.assertIn("bob", result)
            self.assertIn("charlie", result)

    def test_get_my_subscriptions_empty(self):
        """Test getting subscriptions when none exist"""
        self.mock_mongo_storage.get_subscriptions.return_value = []
        
        with patch('work.code.mcp.tools.message_box.get_mongo_storage', return_value=self.mock_mongo_storage):
            result = asyncio.run(get_my_subscriptions("alice"))
            
            self.assertEqual(result, "No subscriptions found for alice. Use subscribe_to_user to add subscriptions.")

    def test_send_message_success(self):
        """Test successful message sending"""
        self.mock_mongo_storage.save_message.return_value = "msg_12345678"
        
        with patch('work.code.mcp.tools.message_box.get_mongo_storage', return_value=self.mock_mongo_storage):
            result = asyncio.run(send_message("alice", "bob", "Hello Bob!"))
            
            self.mock_mongo_storage.save_message.assert_called_once_with("alice", "bob", "Hello Bob!")
            self.assertIn("Message sent successfully. ID: msg_12345678", result)
            self.assertIn("srrd message view msg_12345678", result)
            self.assertIn("http://localhost:8080/message/msg_12345678", result)

    def test_send_message_rate_limit_error(self):
        """Test message sending with rate limit error"""
        self.mock_mongo_storage.save_message.side_effect = Exception("Rate limit exceeded")
        
        with patch('work.code.mcp.tools.message_box.get_mongo_storage', return_value=self.mock_mongo_storage):
            result = asyncio.run(send_message("alice", "bob", "Hello Bob!"))
            
            self.assertIn("Error sending message: Rate limit exceeded", result)

    def test_send_message_with_file_success(self):
        """Test successful message sending with file attachment"""
        # Create a temporary file
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as temp_file:
            temp_file.write("This is test file content")
            temp_file_path = temp_file.name
        
        try:
            self.mock_mongo_storage.save_message.return_value = "msg_87654321"
            
            with patch('work.code.mcp.tools.message_box.get_mongo_storage', return_value=self.mock_mongo_storage):
                result = asyncio.run(send_message_with_file("alice", "bob", "Here's the file", temp_file_path))
                
                # Check that save_message was called with attachment
                args, kwargs = self.mock_mongo_storage.save_message.call_args
                self.assertEqual(len(args), 4)  # sender, recipient, message, attachments
                self.assertEqual(args[0], "alice")
                self.assertEqual(args[1], "bob")
                self.assertEqual(args[2], "Here's the file")
                self.assertEqual(len(args[3]), 1)  # One attachment
                attachment = args[3][0]
                self.assertEqual(attachment['filename'], os.path.basename(temp_file_path))
                self.assertEqual(attachment['content'], "This is test file content")
                self.assertEqual(attachment['size'], 25)
                self.assertEqual(attachment['mime_type'], 'text/plain')
                
                self.assertIn("Message with file sent successfully. ID: msg_87654321", result)
                self.assertIn("25 bytes", result)  # File size
                self.assertIn("srrd message view msg_87654321", result)
        finally:
            os.unlink(temp_file_path)

    def test_send_message_with_file_not_found(self):
        """Test sending message with non-existent file"""
        with patch('work.code.mcp.tools.message_box.get_mongo_storage', return_value=self.mock_mongo_storage):
            result = asyncio.run(send_message_with_file("alice", "bob", "File", "/nonexistent/file.txt"))
            
            self.assertIn("Error: File /nonexistent/file.txt not found.", result)

    def test_read_messages_success(self):
        """Test reading messages"""
        mock_messages = [
            {
                'message_id': 'msg_12345',
                'sender': 'bob',
                'message': 'Hello Alice!',
                'timestamp': datetime.utcnow(),
                'read_status': False,
                'attachments': []
            },
            {
                'message_id': 'msg_67890',
                'sender': 'charlie',
                'message': 'Hi there!',
                'timestamp': datetime.utcnow(),
                'read_status': True,
                'attachments': [{'filename': 'doc.txt'}]
            }
        ]
        self.mock_mongo_storage.get_messages.return_value = mock_messages
        self.mock_mongo_storage.get_unread_count.return_value = 1
        
        with patch('work.code.mcp.tools.message_box.get_mongo_storage', return_value=self.mock_mongo_storage):
            result = asyncio.run(read_messages("alice"))
            
            self.mock_mongo_storage.get_messages.assert_called_once_with("alice", False, None)
            self.assertIn("Messages for alice (1 unread, 2 total):", result)
            self.assertIn("📬 UNREAD msg_12345", result)
            self.assertIn("📭 read msg_67890", result)
            self.assertIn("📎 1 files", result)  # Attachment indicator

    def test_read_messages_empty(self):
        """Test reading messages when none exist"""
        self.mock_mongo_storage.get_messages.return_value = []
        
        with patch('work.code.mcp.tools.message_box.get_mongo_storage', return_value=self.mock_mongo_storage):
            result = asyncio.run(read_messages("alice"))
            
            self.assertEqual(result, "No messages found for alice.")

    def test_read_messages_unread_only(self):
        """Test reading only unread messages"""
        mock_messages = [
            {
                'message_id': 'msg_12345',
                'sender': 'bob',
                'message': 'Hello Alice!',
                'timestamp': datetime.utcnow(),
                'read_status': False,
                'attachments': []
            }
        ]
        self.mock_mongo_storage.get_messages.return_value = mock_messages
        self.mock_mongo_storage.get_unread_count.return_value = 1
        
        with patch('work.code.mcp.tools.message_box.get_mongo_storage', return_value=self.mock_mongo_storage):
            result = asyncio.run(read_messages("alice", unread_only=True))
            
            self.mock_mongo_storage.get_messages.assert_called_once_with("alice", True, None)
            self.assertIn("📬 UNREAD msg_12345", result)

    def test_mark_message_read_success(self):
        """Test marking message as read"""
        self.mock_mongo_storage.mark_message_read.return_value = "Message msg_12345 marked as read"
        
        with patch('work.code.mcp.tools.message_box.get_mongo_storage', return_value=self.mock_mongo_storage):
            result = asyncio.run(mark_message_read("msg_12345", "alice"))
            
            self.mock_mongo_storage.mark_message_read.assert_called_once_with("msg_12345", "alice")
            self.assertEqual(result, "Message msg_12345 marked as read")

    def test_get_unread_count_success(self):
        """Test getting unread count"""
        self.mock_mongo_storage.get_unread_count.return_value = 5
        
        with patch('work.code.mcp.tools.message_box.get_mongo_storage', return_value=self.mock_mongo_storage):
            result = asyncio.run(get_unread_count("alice"))
            
            self.mock_mongo_storage.get_unread_count.assert_called_once_with("alice")
            self.assertEqual(result, "alice has 5 unread messages.")

    def test_mongo_storage_not_initialized(self):
        """Test tools when MongoDB storage is not initialized"""
        with patch('work.code.mcp.tools.message_box.get_mongo_storage', return_value=None):
            result = asyncio.run(register_user("alice"))
            
            self.assertEqual(result, "Error: MongoStorage not initialized.")

if __name__ == '__main__':
    unittest.main()