import unittest
import asyncio
from unittest.mock import MagicMock, patch

from work.code.mcp.tools.message_box import send_message, read_messages

class TestMessageBox(unittest.TestCase):
    def test_send_message(self):
        # Mock server and mongo_storage
        mock_server = MagicMock()
        mock_mongo_storage = MagicMock()
        mock_server.mongo_storage = mock_mongo_storage

        # Patch sys.modules to return the mock server
        with patch.dict('sys.modules', {'work.code.mcp.mcp_server': MagicMock(global_server_instance=mock_server)}):
            # Run the async function
            result = asyncio.run(send_message(sender="test_sender", recipient="test_recipient", message="test_message"))

            # Assert that the save_message method was called with the correct arguments
            mock_mongo_storage.save_message.assert_called_once_with("test_sender", "test_recipient", "test_message")

            # Assert that the function returns the correct message
            self.assertEqual(result, "Message sent successfully.")

    def test_read_messages(self):
        # Mock server and mongo_storage
        mock_server = MagicMock()
        mock_mongo_storage = MagicMock()
        mock_server.mongo_storage = mock_mongo_storage

        # Set the return value of the get_messages method
        mock_mongo_storage.get_messages.return_value = [{"sender": "test_sender", "recipient": "test_recipient", "message": "test_message"}]

        # Patch sys.modules to return the mock server
        with patch.dict('sys.modules', {'work.code.mcp.mcp_server': MagicMock(global_server_instance=mock_server)}):
            # Run the async function
            result = asyncio.run(read_messages(recipient="test_recipient"))

            # Assert that the get_messages method was called with the correct arguments
            mock_mongo_storage.get_messages.assert_called_once_with("test_recipient")

            # Assert that the function returns the correct messages
            self.assertEqual(result, "[{'sender': 'test_sender', 'recipient': 'test_recipient', 'message': 'test_message'}]")

if __name__ == '__main__':
    unittest.main()
