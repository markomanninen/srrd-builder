#!/usr/bin/env python3
"""
Message System Integration Tests
Tests the complete messaging system with real MongoDB database.
"""

import unittest
import asyncio
import os
import tempfile
import sys
from pathlib import Path

# Add the MCP code directory to Python path
sys.path.insert(0, str(Path(__file__).parents[2] / "code" / "mcp"))

class TestMessagingIntegration(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Set up test class with real MongoDB connection"""
        # Set test environment variables
        os.environ['MONGO_URI'] = 'mongodb://localhost:27017/'
        os.environ['MONGO_DB_NAME'] = 'test_mcp_messages'
        os.environ['MAX_MESSAGE_SIZE'] = '1048576'  # 1MB for testing
        os.environ['MAX_ATTACHMENT_SIZE'] = '5242880'  # 5MB for testing
        os.environ['DAILY_MESSAGE_LIMIT'] = '10'  # Lower limit for testing
        os.environ['MAX_SUBSCRIPTIONS'] = '5'  # Lower limit for testing
        
    def setUp(self):
        """Set up each test with fresh database"""
        try:
            from storage.mongo_storage import MongoStorage
            self.mongo_storage = MongoStorage(db_name='test_mcp_messages')
            
            # Clean up any existing test data
            self.mongo_storage.db.users.delete_many({})
            self.mongo_storage.db.messages.delete_many({})
            self.mongo_storage.db.subscriptions.delete_many({})
            
        except Exception as e:
            self.skipTest(f"MongoDB not available: {e}")
    
    def tearDown(self):
        """Clean up after each test"""
        if hasattr(self, 'mongo_storage') and self.mongo_storage:
            # Clean up test data
            self.mongo_storage.db.users.delete_many({})
            self.mongo_storage.db.messages.delete_many({})
            self.mongo_storage.db.subscriptions.delete_many({})
            self.mongo_storage.close()

    def test_user_registration_real_db(self):
        """Test user registration with real database"""
        # Register first user
        result1 = self.mongo_storage.register_user("alice")
        self.assertIn("registered successfully", result1)
        
        # Register second user
        result2 = self.mongo_storage.register_user("bob")
        self.assertIn("registered successfully", result2)
        
        # Try to register same user again
        result3 = self.mongo_storage.register_user("alice")
        self.assertIn("updated last_active", result3)
        
        # Verify users in database
        users = self.mongo_storage.get_all_users()
        self.assertEqual(len(users), 2)
        usernames = [user['username'] for user in users]
        self.assertIn("alice", usernames)
        self.assertIn("bob", usernames)

    def test_subscription_system_real_db(self):
        """Test subscription system with real database"""
        # Register users
        self.mongo_storage.register_user("alice")
        self.mongo_storage.register_user("bob")
        self.mongo_storage.register_user("charlie")
        
        # Alice subscribes to Bob
        result1 = self.mongo_storage.subscribe_user("alice", "bob")
        self.assertIn("Successfully subscribed", result1)
        
        # Alice subscribes to Charlie
        result2 = self.mongo_storage.subscribe_user("alice", "charlie")
        self.assertIn("Successfully subscribed", result2)
        
        # Try duplicate subscription
        with self.assertRaises(Exception) as context:
            self.mongo_storage.subscribe_user("alice", "bob")
        self.assertIn("Already subscribed", str(context.exception))
        
        # Get Alice's subscriptions
        subs = self.mongo_storage.get_subscriptions("alice")
        self.assertEqual(len(subs), 2)
        targets = [sub['target'] for sub in subs]
        self.assertIn("bob", targets)
        self.assertIn("charlie", targets)
        
        # Unsubscribe from Bob
        result3 = self.mongo_storage.unsubscribe_user("alice", "bob")
        self.assertIn("Successfully unsubscribed", result3)
        
        # Verify subscription removed
        subs_after = self.mongo_storage.get_subscriptions("alice")
        self.assertEqual(len(subs_after), 1)
        self.assertEqual(subs_after[0]['target'], "charlie")

    def test_messaging_system_real_db(self):
        """Test complete messaging system with real database"""
        # Setup users and subscription
        self.mongo_storage.register_user("alice")
        self.mongo_storage.register_user("bob")
        self.mongo_storage.subscribe_user("alice", "bob")
        
        # Send message from Alice to Bob
        message_id = self.mongo_storage.save_message("alice", "bob", "Hello Bob!")
        self.assertTrue(message_id.startswith("msg_"))
        
        # Bob reads messages
        messages = self.mongo_storage.get_messages("bob")
        self.assertEqual(len(messages), 1)
        
        message = messages[0]
        self.assertEqual(message['sender'], "alice")
        self.assertEqual(message['recipient'], "bob")
        self.assertEqual(message['message'], "Hello Bob!")
        self.assertEqual(message['message_id'], message_id)
        self.assertFalse(message['read_status'])
        
        # Check unread count
        unread_count = self.mongo_storage.get_unread_count("bob")
        self.assertEqual(unread_count, 1)
        
        # Mark as read
        result = self.mongo_storage.mark_message_read(message_id, "bob")
        self.assertIn("marked as read", result)
        
        # Check unread count after marking read
        unread_count_after = self.mongo_storage.get_unread_count("bob")
        self.assertEqual(unread_count_after, 0)
        
        # Get specific message by ID
        specific_message = self.mongo_storage.get_message_by_id(message_id)
        self.assertIsNotNone(specific_message)
        self.assertTrue(specific_message['read_status'])

    def test_file_attachment_real_db(self):
        """Test file attachments with real database"""
        # Setup
        self.mongo_storage.register_user("alice")
        self.mongo_storage.register_user("bob")
        self.mongo_storage.subscribe_user("alice", "bob")
        
        # Create test attachment
        attachment = {
            'filename': 'test.txt',
            'content': 'This is test file content for integration testing',
            'size': 47,
            'mime_type': 'text/plain'
        }
        
        # Send message with attachment
        message_id = self.mongo_storage.save_message(
            "alice", "bob", "Here's the test file", [attachment]
        )
        
        # Retrieve message and verify attachment
        message = self.mongo_storage.get_message_by_id(message_id)
        self.assertIsNotNone(message)
        self.assertEqual(len(message['attachments']), 1)
        
        stored_attachment = message['attachments'][0]
        self.assertEqual(stored_attachment['filename'], 'test.txt')
        self.assertEqual(stored_attachment['content'], 'This is test file content for integration testing')
        self.assertEqual(stored_attachment['size'], 47)
        self.assertEqual(stored_attachment['mime_type'], 'text/plain')

    def test_rate_limiting_real_db(self):
        """Test rate limiting with real database"""
        # Setup
        self.mongo_storage.register_user("alice")
        self.mongo_storage.register_user("bob")
        self.mongo_storage.subscribe_user("alice", "bob")
        
        # Send messages up to daily limit (10 in test config)
        message_ids = []
        for i in range(10):
            message_id = self.mongo_storage.save_message("alice", "bob", f"Message {i+1}")
            message_ids.append(message_id)
        
        # Try to send one more message (should fail)
        with self.assertRaises(Exception) as context:
            self.mongo_storage.save_message("alice", "bob", "This should fail")
        self.assertIn("Daily message limit reached", str(context.exception))
        
        # Verify all 10 messages were sent
        messages = self.mongo_storage.get_messages("bob")
        self.assertEqual(len(messages), 10)

    def test_subscription_limits_real_db(self):
        """Test subscription limits with real database"""
        # Register users
        self.mongo_storage.register_user("alice")
        for i in range(10):  # Create more users than the limit (5)
            self.mongo_storage.register_user(f"user{i}")
        
        # Subscribe up to limit
        for i in range(5):
            result = self.mongo_storage.subscribe_user("alice", f"user{i}")
            self.assertIn("Successfully subscribed", result)
        
        # Try to exceed limit
        with self.assertRaises(Exception) as context:
            self.mongo_storage.subscribe_user("alice", "user5")
        self.assertIn("Subscription limit reached", str(context.exception))

    def test_message_filtering_real_db(self):
        """Test message filtering with real database"""
        # Setup multiple users
        self.mongo_storage.register_user("alice")
        self.mongo_storage.register_user("bob")
        self.mongo_storage.register_user("charlie")
        self.mongo_storage.subscribe_user("bob", "alice")
        self.mongo_storage.subscribe_user("charlie", "alice")
        
        # Send messages from different senders to Alice
        msg1 = self.mongo_storage.save_message("bob", "alice", "Message from Bob")
        msg2 = self.mongo_storage.save_message("charlie", "alice", "Message from Charlie")
        msg3 = self.mongo_storage.save_message("bob", "alice", "Another message from Bob")
        
        # Mark one message as read
        self.mongo_storage.mark_message_read(msg1, "alice")
        
        # Test filtering by sender
        bob_messages = self.mongo_storage.get_messages("alice", sender="bob")
        self.assertEqual(len(bob_messages), 2)
        for msg in bob_messages:
            self.assertEqual(msg['sender'], "bob")
        
        charlie_messages = self.mongo_storage.get_messages("alice", sender="charlie")
        self.assertEqual(len(charlie_messages), 1)
        self.assertEqual(charlie_messages[0]['sender'], "charlie")
        
        # Test filtering by unread status
        unread_messages = self.mongo_storage.get_messages("alice", unread_only=True)
        self.assertEqual(len(unread_messages), 2)  # msg2 and msg3
        for msg in unread_messages:
            self.assertFalse(msg['read_status'])

    def test_message_size_limits_real_db(self):
        """Test message size limits with real database"""
        # Setup
        self.mongo_storage.register_user("alice")
        self.mongo_storage.register_user("bob")
        self.mongo_storage.subscribe_user("alice", "bob")
        
        # Create message that exceeds size limit
        large_message = "x" * (1048576 + 1)  # 1MB + 1 byte (exceeds test limit)
        
        with self.assertRaises(Exception) as context:
            self.mongo_storage.save_message("alice", "bob", large_message)
        self.assertIn("Message too large", str(context.exception))
        
        # Test attachment size limit
        large_attachment = {
            'filename': 'large.txt',
            'content': "x" * (5242880 + 1),  # 5MB + 1 byte
            'size': 5242881,
            'mime_type': 'text/plain'
        }
        
        with self.assertRaises(Exception) as context:
            self.mongo_storage.save_message("alice", "bob", "Small message", [large_attachment])
        self.assertIn("Attachment large.txt too large", str(context.exception))

    def test_subscription_required_for_messaging_real_db(self):
        """Test that subscription is required for messaging"""
        # Setup users without subscription
        self.mongo_storage.register_user("alice")
        self.mongo_storage.register_user("bob")
        
        # Try to send message without subscription
        with self.assertRaises(Exception) as context:
            self.mongo_storage.save_message("alice", "bob", "This should fail")
        self.assertIn("Not subscribed to bob", str(context.exception))

if __name__ == '__main__':
    # Skip tests if MongoDB is not available
    try:
        from pymongo import MongoClient
        client = MongoClient('mongodb://localhost:27017/', serverSelectionTimeoutMS=2000)
        client.admin.command('ismaster')
        client.close()
        print("MongoDB is available - running integration tests")
        unittest.main()
    except Exception as e:
        print(f"MongoDB not available - skipping integration tests: {e}")
        print("To run these tests, ensure MongoDB is running on localhost:27017")