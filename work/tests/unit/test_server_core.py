#!/usr/bin/env python3
"""
Unit tests for MCP server core functionality
"""
import sys
import os
import pytest
import asyncio
import json
from pathlib import Path
from unittest.mock import Mock, patch

# Add project paths for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'code' / 'mcp'))

from server import MCPServer
from mcp_server import ClaudeMCPServer

class TestMCPServer:
    """Test MCP server core functionality"""
    
    def test_server_initialization(self):
        """Test server initialization"""
        server = MCPServer()
        assert server is not None
        assert hasattr(server, 'tools')
        assert hasattr(server, 'port')
    
    def test_server_with_custom_port(self):
        """Test server initialization with custom port"""
        server = MCPServer(port=9999)
        assert server.port == 9999
    
    def test_server_tool_registration(self):
        """Test tool registration functionality"""
        server = MCPServer()
        
        # Mock tool registration
        server.register_tool(
            name="test_tool",
            description="Test tool",
            parameters={"param": "string"},
            handler=lambda x: "result"
        )
        
        assert "test_tool" in server.tools
        assert server.tools["test_tool"]["description"] == "Test tool"
    
    @pytest.mark.asyncio
    async def test_list_tools_mcp(self):
        """Test MCP tool listing"""
        server = MCPServer()
        tools_info = await server.list_tools_mcp()
        
        assert "tools" in tools_info
        assert isinstance(tools_info["tools"], list)
        # Should have multiple tools registered
        assert len(tools_info["tools"]) > 0
    
    @pytest.mark.asyncio
    async def test_handle_mcp_request_initialize(self):
        """Test MCP initialize request handling"""
        server = MCPServer()
        
        request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {}
        }
        
        response = await server.handle_mcp_request(request)
        
        assert response["jsonrpc"] == "2.0"
        assert response["id"] == 1
        assert "result" in response
        assert response["result"]["protocolVersion"] == "2024-11-05"
    
    @pytest.mark.asyncio
    async def test_handle_mcp_request_tools_list(self):
        """Test MCP tools/list request handling"""
        server = MCPServer()
        
        request = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/list",
            "params": {}
        }
        
        response = await server.handle_mcp_request(request)
        
        assert response["jsonrpc"] == "2.0"
        assert response["id"] == 2
        assert "result" in response
        assert "tools" in response["result"]


class TestClaudeMCPServer:
    """Test Claude-specific MCP server functionality"""
    
    def test_claude_server_initialization(self):
        """Test Claude MCP server initialization"""
        server = ClaudeMCPServer()
        assert server is not None
        assert hasattr(server, 'tools')
        assert hasattr(server, 'running')
    
    def test_claude_server_tool_registration(self):
        """Test Claude server tool registration"""
        server = ClaudeMCPServer()
        
        # Should have tools registered
        assert len(server.tools) > 0
        
        # Check for specific expected tools
        expected_tools = [
            'clarify_research_goals',
            'suggest_methodology', 
            'simulate_peer_review',
            'check_quality_gates'
        ]
        
        for tool in expected_tools:
            assert tool in server.tools
    
    def test_claude_server_list_tools_format(self):
        """Test Claude server tool listing format"""
        server = ClaudeMCPServer()
        tools_info = server.list_tools_mcp()
        
        assert "tools" in tools_info
        assert isinstance(tools_info["tools"], list)
        
        # Check tool format
        if tools_info["tools"]:
            tool = tools_info["tools"][0]
            assert "name" in tool
            assert "description" in tool
            assert "inputSchema" in tool


class TestServerErrorHandling:
    """Test server error handling scenarios"""
    
    @pytest.mark.asyncio
    async def test_invalid_method_request(self):
        """Test handling of invalid method requests"""
        server = MCPServer()
        
        request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "invalid_method",
            "params": {}
        }
        
        response = await server.handle_mcp_request(request)
        
        assert response["jsonrpc"] == "2.0"
        assert response["id"] == 1
        assert "error" in response
        assert response["error"]["code"] == -32601  # Method not found
    
    @pytest.mark.asyncio
    async def test_malformed_request(self):
        """Test handling of malformed requests"""
        server = MCPServer()
        
        # Missing required fields
        request = {
            "method": "initialize"
            # Missing jsonrpc, id
        }
        
        response = await server.handle_mcp_request(request)
        
        # Should handle gracefully
        assert "error" in response or "result" in response


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
