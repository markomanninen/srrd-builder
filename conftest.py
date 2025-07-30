#!/usr/bin/env python3
"""
Pytest configuration and shared fixtures for SRRD-Builder tests
"""
import sys
import os
import pytest
import tempfile
import json
from pathlib import Path
from unittest.mock import Mock, patch

# Add project paths to Python path for imports
PROJECT_ROOT = Path(__file__).parent
MCP_CODE_PATH = PROJECT_ROOT / 'work' / 'code' / 'mcp'

# Add paths for imports
sys.path.insert(0, str(MCP_CODE_PATH))
sys.path.insert(0, str(PROJECT_ROOT))

# Mock chromadb to prevent import errors
sys.modules["chromadb"] = Mock()


@pytest.fixture(scope="session")
def project_root():
    """Fixture providing the project root directory"""
    return PROJECT_ROOT


@pytest.fixture(scope="session") 
def mcp_code_path():
    """Fixture providing the MCP code directory"""
    return MCP_CODE_PATH


@pytest.fixture
def temp_project_dir():
    """Fixture providing a temporary directory for test projects"""
    with tempfile.TemporaryDirectory(prefix="srrd_test_") as temp_dir:
        yield Path(temp_dir)


@pytest.fixture
def srrd_test_project(temp_project_dir):
    """Fixture providing a complete SRRD test project structure"""
    project_path = temp_project_dir
    
    # Create .srrd directory
    srrd_dir = project_path / '.srrd'
    srrd_dir.mkdir(parents=True, exist_ok=True)
    
    # Create config file
    config = {
        "name": "Test SRRD Project",
        "description": "Test project for unit/integration testing",
        "domain": "software_testing",
        "version": "1.0.0",
        "created": "2025-07-19"
    }
    
    config_file = srrd_dir / 'config.json'
    with open(config_file, 'w') as f:
        json.dump(config, f, indent=2)
    
    # Create directory structure
    (srrd_dir / 'data').mkdir(exist_ok=True)
    (srrd_dir / 'logs').mkdir(exist_ok=True)
    (project_path / 'work').mkdir(exist_ok=True)
    (project_path / 'data').mkdir(exist_ok=True)
    
    yield project_path


@pytest.fixture
def mock_environment_context(srrd_test_project):
    """Fixture providing mocked environment variables for context detection"""
    config_path = srrd_test_project / '.srrd' / 'config.json'
    
    env_vars = {
        'SRRD_PROJECT_PATH': str(srrd_test_project),
        'SRRD_CONFIG_PATH': str(config_path),
        'SRRD_TEST_MODE': 'true'
    }
    
    with patch.dict(os.environ, env_vars):
        yield srrd_test_project


@pytest.fixture
def mock_no_context():
    """Fixture providing environment with no SRRD context"""
    # Clear SRRD-related environment variables
    with patch.dict(os.environ, {}, clear=True):
        with tempfile.TemporaryDirectory() as temp_dir:
            original_cwd = os.getcwd()
            try:
                os.chdir(temp_dir)  # Change to directory without .srrd
                yield Path(temp_dir)
            finally:
                os.chdir(original_cwd)


@pytest.fixture
def mcp_server():
    """Fixture providing an MCP server instance for testing"""
    try:
        from server import MCPServer
        server = MCPServer()
        yield server
    except ImportError:
        pytest.skip("MCP server not available")


@pytest.fixture
def claude_mcp_server():
    """Fixture providing a Claude MCP server instance for testing"""
    try:
        from mcp_server import ClaudeMCPServer
        server = ClaudeMCPServer()
        yield server
    except ImportError:
        pytest.skip("Claude MCP server not available")


@pytest.fixture
def context_detector():
    """Fixture providing a context detector instance for testing"""
    try:
        from utils.context_detector import ContextDetector
        detector = ContextDetector()
        # Clear cache before each test
        detector.clear_cache()
        yield detector
    except ImportError:
        pytest.skip("Context detector not available")


@pytest.fixture
def project_manager(srrd_test_project):
    """Fixture providing a project manager instance for testing"""
    try:
        from storage.project_manager import ProjectManager
        pm = ProjectManager(str(srrd_test_project))
        yield pm
    except ImportError:
        pytest.skip("Project manager not available")


@pytest.fixture
def git_manager(srrd_test_project):
    """Fixture providing a git manager instance for testing"""
    try:
        from storage.git_manager import GitManager
        gm = GitManager(str(srrd_test_project))
        yield gm
    except ImportError:
        pytest.skip("Git manager not available")


@pytest.fixture
def sqlite_manager(temp_project_dir):
    """Fixture providing a SQLite manager instance for testing"""
    try:
        from storage.sqlite_manager import SQLiteManager
        db_path = temp_project_dir / 'test.db'
        sm = SQLiteManager(str(db_path))
        yield sm
    except ImportError:
        pytest.skip("SQLite manager not available")


@pytest.fixture
def vector_manager():
    """Fixture providing a vector manager instance for testing"""
    try:
        from storage.vector_manager import VectorManager
        vm = VectorManager()
        yield vm
    except ImportError:
        pytest.skip("Vector manager not available")


@pytest.fixture(scope="session")
def test_bibliography_references():
    """Fixture providing test bibliography references"""
    return [
        {
            "title": "Context-Aware Research Management Systems",
            "authors": ["Dr. Jane Smith", "Prof. John Doe"],
            "year": 2025,
            "journal": "Journal of Research Management",
            "doi": "10.1234/jrm.2025.001"
        },
        {
            "title": "Automated Testing in Scientific Software",
            "authors": ["Dr. Alice Johnson"],
            "year": 2024,
            "journal": "Software Testing Review",
            "doi": "10.5678/str.2024.042"
        },
        {
            "title": "MCP Protocol Implementation Best Practices",
            "authors": ["Prof. Bob Wilson", "Dr. Carol Brown"],
            "year": 2025,
            "journal": "Protocol Engineering Quarterly",
            "doi": "10.9012/peq.2025.015"
        }
    ]


# Pytest hooks and configuration

def pytest_configure(config):
    """Configure pytest with custom settings"""
    # Register custom markers
    config.addinivalue_line(
        "markers", "unit: Unit tests for individual components"
    )
    config.addinivalue_line(
        "markers", "integration: Integration tests for component interaction"
    )
    config.addinivalue_line(
        "markers", "validation: Validation tests for performance and deployment"
    )
    config.addinivalue_line(
        "markers", "asyncio: Tests that use asyncio"
    )
    config.addinivalue_line(
        "markers", "slow: Tests that take a long time to run"
    )
    config.addinivalue_line(
        "markers", "network: Tests that require network access"
    )
    config.addinivalue_line(
        "markers", "storage: Tests that require storage components"
    )
    config.addinivalue_line(
        "markers", "mcp: Tests that require MCP protocol functionality"
    )


def pytest_collection_modifyitems(config, items):
    """Modify test collection to add markers based on test location"""
    for item in items:
        # Add markers based on file path
        test_path = str(item.fspath)
        
        if "/unit/" in test_path:
            item.add_marker(pytest.mark.unit)
        elif "/integration/" in test_path:
            item.add_marker(pytest.mark.integration)
        elif "/validation/" in test_path:
            item.add_marker(pytest.mark.validation)
        
        # Add storage marker for storage-related tests
        if "storage" in test_path.lower():
            item.add_marker(pytest.mark.storage)
        
        # Add mcp marker for MCP-related tests
        if "mcp" in test_path.lower() or "server" in test_path.lower():
            item.add_marker(pytest.mark.mcp)
        
        # Add asyncio marker for async tests
        if item.get_closest_marker("asyncio"):
            item.add_marker(pytest.mark.asyncio)


def pytest_runtest_setup(item):
    """Setup for individual test runs"""
    # Skip tests that require unavailable components
    markers = [marker.name for marker in item.iter_markers()]
    
    if "storage" in markers:
        try:
            import sqlite3
        except ImportError:
            pytest.skip("SQLite not available")
    
    if "network" in markers:
        try:
            import websockets
        except ImportError:
            pytest.skip("WebSocket library not available")


# Helper functions for tests

class MockArgs:
    """Mock arguments class for CLI command testing"""
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

def create_mock_mcp_request(method, params=None, request_id=1):
    """Helper function to create mock MCP requests"""
    return {
        "jsonrpc": "2.0",
        "id": request_id,
        "method": method,
        "params": params or {}
    }


def assert_mcp_response_valid(response, request_id=None):
    """Helper function to validate MCP response structure"""
    assert "jsonrpc" in response
    assert response["jsonrpc"] == "2.0"
    
    if request_id is not None:
        assert "id" in response
        assert response["id"] == request_id
    
    # Should have either result or error
    assert "result" in response or "error" in response
    
    if "error" in response:
        error = response["error"]
        assert "code" in error
        assert "message" in error
        assert isinstance(error["code"], int)
        assert isinstance(error["message"], str)
    
    if "result" in response:
        # Result format depends on the specific request
        assert response["result"] is not None


@pytest.fixture(scope="session", autouse=True)
def cleanup_session():
    """Cleanup fixture that runs at session level to prevent hanging"""
    yield
    
    # Force cleanup of any remaining tasks
    import asyncio
    import threading
    import time
    import os
    
    try:
        # Force exit without waiting for lingering threads
        os._exit(0)
    except Exception:
        pass
