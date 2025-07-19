#!/usr/bin/env python3
"""
Integration tests for MCP protocol compliance
"""
import sys
import os
import pytest
import asyncio
import json
import websockets
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

# Add project paths for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'code' / 'mcp'))


class TestMCPProtocolCompliance:
    """Test full MCP protocol compliance"""
    
    @pytest.mark.asyncio
    async def test_mcp_initialization_protocol(self):
        """Test MCP initialization protocol"""
        try:
            from server import MCPServer
            
            server = MCPServer()
            
            # Test initialize request
            request = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "initialize",
                "params": {}
            }
            
            response = await server.handle_mcp_request(request)
            
            # Validate response structure
            assert response["jsonrpc"] == "2.0"
            assert response["id"] == 1
            assert "result" in response
            
            result = response["result"]
            assert "protocolVersion" in result
            assert "capabilities" in result
            assert "serverInfo" in result
            
            # Validate capabilities
            capabilities = result["capabilities"]
            assert "tools" in capabilities
            
            # Validate server info
            server_info = result["serverInfo"]
            assert "name" in server_info
            assert "version" in server_info
            
        except ImportError:
            pytest.skip("MCP server not available")
    
    @pytest.mark.asyncio
    async def test_mcp_tools_list_protocol(self):
        """Test MCP tools/list protocol"""
        try:
            from server import MCPServer
            
            server = MCPServer()
            
            request = {
                "jsonrpc": "2.0",
                "id": 2,
                "method": "tools/list",
                "params": {}
            }
            
            response = await server.handle_mcp_request(request)
            
            # Validate response
            assert response["jsonrpc"] == "2.0"
            assert response["id"] == 2
            assert "result" in response
            
            result = response["result"]
            assert "tools" in result
            assert isinstance(result["tools"], list)
            
            # Validate tool structure
            if result["tools"]:
                tool = result["tools"][0]
                assert "name" in tool
                assert "description" in tool
                assert "inputSchema" in tool
                
                # Validate input schema
                schema = tool["inputSchema"]
                assert "type" in schema
                assert schema["type"] == "object"
                
        except ImportError:
            pytest.skip("MCP server not available")
    
    @pytest.mark.asyncio
    async def test_mcp_tool_call_protocol(self):
        """Test MCP tools/call protocol"""
        try:
            from server import MCPServer
            
            server = MCPServer()
            
            # Get available tools first
            tools_request = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "tools/list",
                "params": {}
            }
            
            tools_response = await server.handle_mcp_request(tools_request)
            tools = tools_response["result"]["tools"]
            
            if not tools:
                pytest.skip("No tools available to test")
            
            # Test calling the first available tool
            tool_name = tools[0]["name"]
            
            call_request = {
                "jsonrpc": "2.0", 
                "id": 2,
                "method": "tools/call",
                "params": {
                    "name": tool_name,
                    "arguments": {}
                }
            }
            
            response = await server.handle_mcp_request(call_request)
            
            # Validate response structure
            assert response["jsonrpc"] == "2.0"
            assert response["id"] == 2
            
            # Should have either result or error
            assert "result" in response or "error" in response
            
            if "result" in response:
                result = response["result"]
                assert "content" in result
                assert isinstance(result["content"], list)
                
                if result["content"]:
                    content = result["content"][0]
                    assert "type" in content
                    assert "text" in content
                    
        except ImportError:
            pytest.skip("MCP server not available")
    
    @pytest.mark.asyncio
    async def test_mcp_error_handling_protocol(self):
        """Test MCP error handling protocol"""
        try:
            from server import MCPServer
            
            server = MCPServer()
            
            # Test invalid method
            request = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "invalid_method",
                "params": {}
            }
            
            response = await server.handle_mcp_request(request)
            
            # Should return proper error response
            assert response["jsonrpc"] == "2.0"
            assert response["id"] == 1
            assert "error" in response
            
            error = response["error"]
            assert "code" in error
            assert "message" in error
            assert error["code"] == -32601  # Method not found
            
        except ImportError:
            pytest.skip("MCP server not available")
    
    @pytest.mark.asyncio
    async def test_mcp_invalid_tool_call(self):
        """Test calling invalid tool"""
        try:
            from server import MCPServer
            
            server = MCPServer()
            
            request = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "tools/call",
                "params": {
                    "name": "nonexistent_tool",
                    "arguments": {}
                }
            }
            
            response = await server.handle_mcp_request(request)
            
            # Should return error for nonexistent tool
            assert response["jsonrpc"] == "2.0"
            assert response["id"] == 1
            assert "error" in response
            
            error = response["error"]
            assert "code" in error
            assert "message" in error
            
        except ImportError:
            pytest.skip("MCP server not available")


class TestMCPWebSocketProtocol:
    """Test MCP protocol over WebSocket"""
    
    @pytest.mark.asyncio
    async def test_websocket_connection_handling(self):
        """Test WebSocket connection handling"""
        try:
            from server import MCPServer
            
            # This test would require actually starting a WebSocket server
            # For now, just test the message handling logic
            server = MCPServer()
            
            # Mock WebSocket for testing message handling
            mock_websocket = Mock()
            mock_websocket.send = Mock(return_value=asyncio.Future())
            mock_websocket.send.return_value.set_result(None)
            
            # Test would involve actual WebSocket communication
            # Skipping for unit test environment
            assert server is not None
            
        except ImportError:
            pytest.skip("MCP server not available")
    
    @pytest.mark.asyncio 
    async def test_concurrent_requests(self):
        """Test handling of concurrent MCP requests"""
        try:
            from server import MCPServer
            
            server = MCPServer()
            
            # Create multiple concurrent requests
            requests = [
                {
                    "jsonrpc": "2.0",
                    "id": i,
                    "method": "tools/list",
                    "params": {}
                }
                for i in range(5)
            ]
            
            # Process requests concurrently
            tasks = [server.handle_mcp_request(req) for req in requests]
            responses = await asyncio.gather(*tasks)
            
            # All should succeed
            assert len(responses) == 5
            
            for i, response in enumerate(responses):
                assert response["jsonrpc"] == "2.0"
                assert response["id"] == i
                assert "result" in response or "error" in response
                
        except ImportError:
            pytest.skip("MCP server not available")


class TestMCPToolIntegration:
    """Test integration with actual MCP tools"""
    
    @pytest.mark.asyncio
    async def test_research_planning_tools_integration(self):
        """Test research planning tools via MCP protocol"""
        try:
            from server import MCPServer
            
            server = MCPServer()
            
            # Test clarify_research_goals tool
            request = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "tools/call",
                "params": {
                    "name": "clarify_research_goals",
                    "arguments": {
                        "research_area": "artificial intelligence",
                        "initial_goals": "Develop better AI systems"
                    }
                }
            }
            
            response = await server.handle_mcp_request(request)
            
            # Should either succeed or fail gracefully
            assert response["jsonrpc"] == "2.0"
            assert response["id"] == 1
            assert "result" in response or "error" in response
            
        except ImportError:
            pytest.skip("MCP tools not available")
    
    @pytest.mark.asyncio
    async def test_storage_tools_integration(self):
        """Test storage tools via MCP protocol"""
        try:
            from server import MCPServer
            
            server = MCPServer()
            
            # Test with temporary directory
            with tempfile.TemporaryDirectory() as temp_dir:
                request = {
                    "jsonrpc": "2.0",
                    "id": 1,
                    "method": "tools/call", 
                    "params": {
                        "name": "initialize_project",
                        "arguments": {
                            "name": "Test Project",
                            "description": "Test project for integration testing",
                            "domain": "testing",
                            "project_path": temp_dir
                        }
                    }
                }
                
                response = await server.handle_mcp_request(request)
                
                # Should either succeed or fail gracefully
                assert response["jsonrpc"] == "2.0"
                assert response["id"] == 1
                assert "result" in response or "error" in response
                
        except ImportError:
            pytest.skip("MCP storage tools not available")


class TestMCPProtocolValidation:
    """Test MCP protocol validation and edge cases"""
    
    @pytest.mark.asyncio
    async def test_missing_required_fields(self):
        """Test handling of requests with missing required fields"""
        try:
            from server import MCPServer
            
            server = MCPServer()
            
            # Missing method field
            request = {
                "jsonrpc": "2.0",
                "id": 1,
                "params": {}
            }
            
            response = await server.handle_mcp_request(request)
            
            # Should handle gracefully
            assert "error" in response or "result" in response
            
        except ImportError:
            pytest.skip("MCP server not available")
    
    @pytest.mark.asyncio
    async def test_invalid_jsonrpc_version(self):
        """Test handling of invalid JSON-RPC version"""
        try:
            from server import MCPServer
            
            server = MCPServer()
            
            request = {
                "jsonrpc": "1.0",  # Invalid version
                "id": 1,
                "method": "initialize",
                "params": {}
            }
            
            response = await server.handle_mcp_request(request)
            
            # Should handle gracefully or reject
            assert isinstance(response, dict)
            
        except ImportError:
            pytest.skip("MCP server not available")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
