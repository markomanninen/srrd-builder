#!/usr/bin/env python3
"""
CLI Message Command Tests
Tests for the CLI message viewing functionality.
"""

import unittest
import tempfile
import os
from unittest.mock import MagicMock, patch, Mock
from datetime import datetime
from argparse import Namespace

# Import the command handler
import sys
sys.path.insert(0, 'srrd_builder/cli/commands')
from message import (
    handle_message_view, handle_message_list, handle_message_conversation,
    handle_message_stats, format_message_content, format_message_list
)

class TestCLIMessage(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures"""
        self.mock_storage = MagicMock()
        self.sample_message = {
            'message_id': 'msg_12345',
            'sender': 'alice',
            'recipient': 'bob',
            'message': 'Hello Bob, how are you?',
            'timestamp': datetime.utcnow(),
            'read_status': False,
            'read_at': None,
            'size_bytes': 100,
            'attachments': [
                {
                    'filename': 'test.txt',
                    'content': 'Test file content',
                    'size': 17,
                    'mime_type': 'text/plain'
                }
            ]
        }
        
    @patch('message.get_mongo_storage')
    def test_message_view_success(self, mock_get_storage):
        """Test successful message viewing"""
        mock_get_storage.return_value = self.mock_storage
        self.mock_storage.get_message_by_id.return_value = self.sample_message
        
        args = Namespace(message_id='msg_12345')
        
        with patch('builtins.print') as mock_print:
            result = handle_message_view(args)
            
            self.assertEqual(result, 0)
            self.mock_storage.get_message_by_id.assert_called_once_with('msg_12345')
            self.mock_storage.close.assert_called_once()
            
            # Check that message content was printed
            printed_output = ''.join(call.args[0] for call in mock_print.call_args_list)
            self.assertIn('MESSAGE ID: msg_12345', printed_output)
            self.assertIn('FROM: alice', printed_output)
            self.assertIn('TO: bob', printed_output)
            self.assertIn('Hello Bob, how are you?', printed_output)
            self.assertIn('test.txt', printed_output)
            self.assertIn('Test file content', printed_output)

    @patch('message.get_mongo_storage')
    def test_message_view_not_found(self, mock_get_storage):
        """Test viewing non-existent message"""
        mock_get_storage.return_value = self.mock_storage
        self.mock_storage.get_message_by_id.return_value = None
        
        args = Namespace(message_id='msg_nonexistent')
        
        with patch('builtins.print') as mock_print:
            result = handle_message_view(args)
            
            self.assertEqual(result, 0)
            printed_output = ''.join(call.args[0] for call in mock_print.call_args_list)
            self.assertIn('Message not found', printed_output)

    @patch('message.get_mongo_storage')
    def test_message_list_success(self, mock_get_storage):
        """Test successful message listing"""
        mock_get_storage.return_value = self.mock_storage
        messages = [self.sample_message.copy() for _ in range(3)]
        messages[1]['read_status'] = True  # Make one message read
        self.mock_storage.get_messages.return_value = messages
        
        args = Namespace(
            username='bob',
            unread=False,
            sender=None,
            limit=20
        )
        
        with patch('builtins.print') as mock_print:
            result = handle_message_list(args)
            
            self.assertEqual(result, 0)
            self.mock_storage.get_messages.assert_called_once_with(
                recipient='bob',
                unread_only=False,
                sender=None
            )
            
            printed_output = ''.join(call.args[0] for call in mock_print.call_args_list)
            self.assertIn('Messages for bob', printed_output)
            self.assertIn('2 unread, 3 total', printed_output)
            self.assertIn('📬 UNREAD', printed_output)
            self.assertIn('📭 read', printed_output)

    @patch('message.get_mongo_storage')
    def test_message_list_unread_only(self, mock_get_storage):
        """Test listing only unread messages"""
        mock_get_storage.return_value = self.mock_storage
        unread_message = self.sample_message.copy()
        self.mock_storage.get_messages.return_value = [unread_message]
        
        args = Namespace(
            username='bob',
            unread=True,
            sender=None,
            limit=20
        )
        
        with patch('builtins.print') as mock_print:
            result = handle_message_list(args)
            
            self.assertEqual(result, 0)
            self.mock_storage.get_messages.assert_called_once_with(
                recipient='bob',
                unread_only=True,
                sender=None
            )

    @patch('message.get_mongo_storage')
    def test_message_conversation_success(self, mock_get_storage):
        """Test successful conversation viewing"""
        mock_get_storage.return_value = self.mock_storage
        
        # Messages from alice to bob
        msg1 = self.sample_message.copy()
        msg1['timestamp'] = datetime(2024, 1, 1, 10, 0)
        
        # Messages from bob to alice
        msg2 = {
            'message_id': 'msg_67890',
            'sender': 'bob',
            'recipient': 'alice',
            'message': 'Hi Alice, I am good!',
            'timestamp': datetime(2024, 1, 1, 10, 5),
            'read_status': True,
            'attachments': []
        }
        
        # Mock the two separate calls
        self.mock_storage.get_messages.side_effect = [[msg2], [msg1]]
        
        args = Namespace(user1='alice', user2='bob')
        
        with patch('builtins.print') as mock_print:
            result = handle_message_conversation(args)
            
            self.assertEqual(result, 0)
            # Should be called twice (both directions)
            self.assertEqual(self.mock_storage.get_messages.call_count, 2)
            
            printed_output = ''.join(call.args[0] for call in mock_print.call_args_list)
            self.assertIn('Conversation between alice and bob', printed_output)
            self.assertIn('alice → bob', printed_output)
            self.assertIn('bob → alice', printed_output)

    @patch('message.get_mongo_storage')
    def test_message_stats_success(self, mock_get_storage):
        """Test successful message statistics"""
        mock_get_storage.return_value = self.mock_storage
        
        # Mock received messages
        received_messages = [self.sample_message.copy() for _ in range(5)]
        self.mock_storage.get_messages.return_value = received_messages
        
        # Mock sent messages
        sent_messages = [self.sample_message.copy() for _ in range(3)]
        self.mock_storage.db.messages.find.return_value = sent_messages
        
        # Mock unread count and subscriptions
        self.mock_storage.get_unread_count.return_value = 2
        self.mock_storage.get_subscriptions.return_value = [
            {'target': 'alice', 'subscribed_at': datetime.utcnow()}
        ]
        
        args = Namespace(username='bob')
        
        with patch('builtins.print') as mock_print:
            result = handle_message_stats(args)
            
            self.assertEqual(result, 0)
            
            printed_output = ''.join(call.args[0] for call in mock_print.call_args_list)
            self.assertIn('Message Statistics for bob', printed_output)
            self.assertIn('Messages received: 5', printed_output)
            self.assertIn('Messages sent: 3', printed_output)
            self.assertIn('Unread messages: 2', printed_output)
            self.assertIn('Subscriptions: 1', printed_output)

    @patch('message.get_mongo_storage')
    def test_storage_initialization_failure(self, mock_get_storage):
        """Test handling of storage initialization failure"""
        mock_get_storage.return_value = None
        
        args = Namespace(message_id='msg_12345')
        result = handle_message_view(args)
        
        self.assertEqual(result, 1)

    def test_format_message_content(self):
        """Test message content formatting"""
        formatted = format_message_content(self.sample_message)
        
        self.assertIn('MESSAGE ID: msg_12345', formatted)
        self.assertIn('FROM: alice', formatted)
        self.assertIn('TO: bob', formatted)
        self.assertIn('STATUS: UNREAD', formatted)
        self.assertIn('Hello Bob, how are you?', formatted)
        self.assertIn('ATTACHMENTS (1):', formatted)
        self.assertIn('test.txt', formatted)
        self.assertIn('Test file content', formatted)

    def test_format_message_content_none(self):
        """Test formatting when message is None"""
        formatted = format_message_content(None)
        self.assertEqual(formatted, "Message not found.")

    def test_format_message_list(self):
        """Test message list formatting"""
        messages = [self.sample_message.copy() for _ in range(2)]
        messages[1]['read_status'] = True
        messages[1]['message_id'] = 'msg_67890'
        
        formatted = format_message_list(messages, 'bob')
        
        self.assertIn('Messages for bob (1 unread, 2 total)', formatted)
        self.assertIn('📬 UNREAD msg_12345', formatted)
        self.assertIn('📭 read msg_67890', formatted)
        self.assertIn('📎 1 files', formatted)  # Attachment indicator

    def test_format_message_list_empty(self):
        """Test formatting empty message list"""
        formatted = format_message_list([], 'bob')
        self.assertEqual(formatted, "No messages found.")

if __name__ == '__main__':
    unittest.main()