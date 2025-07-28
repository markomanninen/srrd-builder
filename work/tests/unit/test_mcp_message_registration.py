#!/usr/bin/env python3
"""
MCP Message Tool Registration Tests
Tests that message tools are properly registered with the MCP server.
"""

import unittest
import asyncio
from unittest.mock import MagicMock, patch

# Import the registration function
import sys
sys.path.insert(0, 'work/code/mcp')
from tools.message_box import register_message_tools, set_server_instance, get_mongo_storage

class TestMCPMessageRegistration(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures"""
        self.mock_server = MagicMock()
        self.mock_server.tools = {}
        self.mock_server.mongo_storage = MagicMock()
        
        # Mock the register_tool method
        def mock_register_tool(name, description, parameters, handler):
            self.mock_server.tools[name] = {
                'description': description,
                'parameters': parameters,
                'handler': handler
            }
        self.mock_server.register_tool = mock_register_tool

    def test_register_message_tools(self):
        """Test that all message tools are registered"""
        register_message_tools(self.mock_server)
        
        # Check that tools were registered
        expected_tools = [
            'register_user',
            'discover_users', 
            'subscribe_to_user',
            'unsubscribe_from_user',
            'get_my_subscriptions',
            'send_message',
            'send_message_with_file',
            'read_messages',
            'mark_message_read',
            'get_unread_count',
            'view_message_web',
            'list_messages_web',
            'get_conversation_web'
        ]
        
        for tool_name in expected_tools:
            self.assertIn(tool_name, self.mock_server.tools, f"Tool {tool_name} not registered")
            
            # Check that each tool has required fields
            tool = self.mock_server.tools[tool_name]
            self.assertIn('description', tool)
            self.assertIn('parameters', tool)
            self.assertIn('handler', tool)
            
            # Check that parameters follow MCP schema format
            params = tool['parameters']
            self.assertIn('type', params)
            self.assertEqual(params['type'], 'object')
            self.assertIn('properties', params)
            self.assertIn('required', params)

    def test_server_instance_setting(self):
        """Test that server instance is properly set"""
        register_message_tools(self.mock_server)
        
        # Check that mongo_storage is accessible
        mongo_storage = get_mongo_storage()
        self.assertEqual(mongo_storage, self.mock_server.mongo_storage)

    def test_tool_handlers_are_callable(self):
        """Test that all registered tool handlers are callable"""
        register_message_tools(self.mock_server)
        
        for tool_name, tool_data in self.mock_server.tools.items():
            handler = tool_data['handler']
            self.assertTrue(callable(handler), f"Handler for {tool_name} is not callable")

    def test_tool_parameter_schemas(self):
        """Test that tool parameter schemas are valid"""
        register_message_tools(self.mock_server)
        
        # Test specific tool schemas
        register_user_tool = self.mock_server.tools['register_user']
        self.assertEqual(register_user_tool['parameters']['required'], ['username'])
        self.assertIn('username', register_user_tool['parameters']['properties'])
        
        send_message_tool = self.mock_server.tools['send_message']
        self.assertEqual(set(send_message_tool['parameters']['required']), 
                        {'sender', 'recipient', 'message'})
        
        send_file_tool = self.mock_server.tools['send_message_with_file']
        self.assertEqual(set(send_file_tool['parameters']['required']),
                        {'sender', 'recipient', 'message', 'file_path'})

    def test_no_mongo_storage_handling(self):
        """Test handling when mongo_storage is not available"""
        # Create server without mongo_storage
        server_no_mongo = MagicMock()
        server_no_mongo.tools = {}
        server_no_mongo.mongo_storage = None
        
        def mock_register_tool(name, description, parameters, handler):
            server_no_mongo.tools[name] = {
                'description': description,
                'parameters': parameters,
                'handler': handler
            }
        server_no_mongo.register_tool = mock_register_tool
        
        # Should still register tools
        register_message_tools(server_no_mongo)
        self.assertGreater(len(server_no_mongo.tools), 0)
        
        # Set server instance
        set_server_instance(server_no_mongo)
        
        # Should return None for mongo_storage
        mongo_storage = get_mongo_storage()
        self.assertIsNone(mongo_storage)

    def test_tool_execution_with_mongo_storage(self):
        """Test that tools can execute with mongo_storage"""
        register_message_tools(self.mock_server)
        
        # Mock mongo_storage methods
        self.mock_server.mongo_storage.register_user.return_value = "User registered"
        
        # Get and execute a tool
        register_user_handler = self.mock_server.tools['register_user']['handler']
        
        # Execute the tool
        result = asyncio.run(register_user_handler("test_user"))
        
        # Check that mongo_storage method was called
        self.mock_server.mongo_storage.register_user.assert_called_once_with("test_user")
        self.assertEqual(result, "User registered")

    def test_tool_execution_without_mongo_storage(self):
        """Test that tools handle missing mongo_storage gracefully"""
        # Create server without mongo_storage
        server_no_mongo = MagicMock()
        server_no_mongo.tools = {}
        server_no_mongo.mongo_storage = None
        
        def mock_register_tool(name, description, parameters, handler):
            server_no_mongo.tools[name] = {
                'description': description,
                'parameters': parameters, 
                'handler': handler
            }
        server_no_mongo.register_tool = mock_register_tool
        
        register_message_tools(server_no_mongo)
        
        # Execute a tool without mongo_storage
        register_user_handler = server_no_mongo.tools['register_user']['handler']
        result = asyncio.run(register_user_handler("test_user"))
        
        # Should return error message
        self.assertIn("MongoStorage not initialized", result)

    def test_web_tools_return_json(self):
        """Test that web tools return JSON format"""
        register_message_tools(self.mock_server)
        
        # Mock mongo_storage to return None (message not found)
        self.mock_server.mongo_storage.get_message_by_id.return_value = None
        
        # Execute web tool
        view_message_handler = self.mock_server.tools['view_message_web']['handler']
        result = asyncio.run(view_message_handler("msg_test"))
        
        # Should return JSON error
        self.assertIn('{"error":', result)
        self.assertIn("not found", result)

if __name__ == '__main__':
    unittest.main()