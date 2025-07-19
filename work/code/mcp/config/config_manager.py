"""
Configuration Manager for SRRD Builder MCP Server
Handles application settings, environment variables, and configuration loading
"""

import os
import json
from pathlib import Path
from typing import Dict, Any, Optional, List
from dataclasses import dataclass

# Optional YAML support
try:
    import yaml
    YAML_SUPPORT = True
except ImportError:
    YAML_SUPPORT = False

@dataclass
class DatabaseConfig:
    """Database configuration settings"""
    sqlite_path: str = "data/srrd_builder.db"
    enable_wal: bool = True
    timeout: int = 30

@dataclass
class VectorConfig:
    """Vector database configuration"""
    backend: str = "chromadb"
    persist_directory: str = "../../../.srrd/knowledge.db"
    embedding_model: str = "all-MiniLM-L6-v2"
    max_chunk_size: int = 1000
    chunk_overlap: int = 100

@dataclass
class GitConfig:
    """Git configuration settings"""
    auto_commit: bool = True
    commit_message_template: str = "SRRD Builder auto-commit: {timestamp}"
    backup_branches: bool = True

@dataclass
class AIConfig:
    """AI model configuration"""
    openai_api_key: Optional[str] = None
    model_name: str = "gpt-3.5-turbo"
    max_tokens: int = 2000
    temperature: float = 0.7

@dataclass
class ServerConfig:
    """MCP Server configuration"""
    host: str = "localhost"
    port: int = 8080
    enable_logging: bool = True
    log_level: str = "INFO"
    log_file: str = "logs/mcp_server.log"

class ConfigManager:
    """Manages configuration for the SRRD Builder MCP Server"""
    
    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path or self._get_default_config_path()
        self.database = DatabaseConfig()
        self.vector = VectorConfig()
        self.git = GitConfig()
        self.ai = AIConfig()
        self.server = ServerConfig()
        self._load_config()
        self._load_environment_variables()
    
    def _get_default_config_path(self) -> str:
        """Get the default configuration file path"""
        # Use local config file - MCP server runs in project context
        config_path = "config/default_config.json"
        
        if os.path.exists(config_path):
            return config_path
        
        return config_path  # Return default path even if it doesn't exist
    
    def _load_config(self):
        """Load configuration from file"""
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r') as f:
                    if (self.config_path.endswith('.yaml') or self.config_path.endswith('.yml')) and YAML_SUPPORT:
                        config_data = yaml.safe_load(f)
                    else:
                        config_data = json.load(f)
                
                self._apply_config_data(config_data)
            else:
                print(f"Config file not found at {self.config_path}, using defaults")
        
        except Exception as e:
            print(f"Error loading config from {self.config_path}: {e}")
            print("Using default configuration")
    
    def _apply_config_data(self, config_data: Dict[str, Any]):
        """Apply configuration data to settings"""
        if 'database' in config_data:
            db_config = config_data['database']
            self.database.sqlite_path = db_config.get('sqlite_path', self.database.sqlite_path)
            self.database.enable_wal = db_config.get('enable_wal', self.database.enable_wal)
            self.database.timeout = db_config.get('timeout', self.database.timeout)
        
        if 'vector' in config_data:
            vector_config = config_data['vector']
            self.vector.backend = vector_config.get('backend', self.vector.backend)
            self.vector.persist_directory = vector_config.get('persist_directory', self.vector.persist_directory)
            self.vector.embedding_model = vector_config.get('embedding_model', self.vector.embedding_model)
            self.vector.max_chunk_size = vector_config.get('max_chunk_size', self.vector.max_chunk_size)
            self.vector.chunk_overlap = vector_config.get('chunk_overlap', self.vector.chunk_overlap)
        
        if 'git' in config_data:
            git_config = config_data['git']
            self.git.auto_commit = git_config.get('auto_commit', self.git.auto_commit)
            self.git.commit_message_template = git_config.get('commit_message_template', self.git.commit_message_template)
            self.git.backup_branches = git_config.get('backup_branches', self.git.backup_branches)
        
        if 'ai' in config_data:
            ai_config = config_data['ai']
            self.ai.openai_api_key = ai_config.get('openai_api_key', self.ai.openai_api_key)
            self.ai.model_name = ai_config.get('model_name', self.ai.model_name)
            self.ai.max_tokens = ai_config.get('max_tokens', self.ai.max_tokens)
            self.ai.temperature = ai_config.get('temperature', self.ai.temperature)
        
        if 'server' in config_data:
            server_config = config_data['server']
            self.server.host = server_config.get('host', self.server.host)
            self.server.port = server_config.get('port', self.server.port)
            self.server.enable_logging = server_config.get('enable_logging', self.server.enable_logging)
            self.server.log_level = server_config.get('log_level', self.server.log_level)
            self.server.log_file = server_config.get('log_file', self.server.log_file)
    
    def _load_environment_variables(self):
        """Load configuration from environment variables"""
        # Database settings
        if os.getenv('SRRD_DB_PATH'):
            self.database.sqlite_path = os.getenv('SRRD_DB_PATH')
        
        # Vector database settings - FIXED TO USE PROJECT PATH
        if os.getenv('SRRD_VECTOR_DIR'):
            self.vector.persist_directory = os.getenv('SRRD_VECTOR_DIR')
        elif os.getenv('SRRD_PROJECT_PATH'):
            # Use project-specific path if available
            project_path = os.getenv('SRRD_PROJECT_PATH')
            self.vector.persist_directory = os.path.join(project_path, '.srrd', 'knowledge.db')
        
        if os.getenv('SRRD_EMBEDDING_MODEL'):
            self.vector.embedding_model = os.getenv('SRRD_EMBEDDING_MODEL')
        
        # AI settings
        if os.getenv('OPENAI_API_KEY'):
            self.ai.openai_api_key = os.getenv('OPENAI_API_KEY')
        if os.getenv('SRRD_AI_MODEL'):
            self.ai.model_name = os.getenv('SRRD_AI_MODEL')
        
        # Server settings
        if os.getenv('SRRD_SERVER_PORT'):
            try:
                self.server.port = int(os.getenv('SRRD_SERVER_PORT'))
            except ValueError:
                pass
        if os.getenv('SRRD_LOG_LEVEL'):
            self.server.log_level = os.getenv('SRRD_LOG_LEVEL')
    
    def get_config_dict(self) -> Dict[str, Any]:
        """Get configuration as dictionary"""
        return {
            'database': {
                'sqlite_path': self.database.sqlite_path,
                'enable_wal': self.database.enable_wal,
                'timeout': self.database.timeout
            },
            'vector': {
                'backend': self.vector.backend,
                'persist_directory': self.vector.persist_directory,
                'embedding_model': self.vector.embedding_model,
                'max_chunk_size': self.vector.max_chunk_size,
                'chunk_overlap': self.vector.chunk_overlap
            },
            'git': {
                'auto_commit': self.git.auto_commit,
                'commit_message_template': self.git.commit_message_template,
                'backup_branches': self.git.backup_branches
            },
            'ai': {
                'openai_api_key': self.ai.openai_api_key,
                'model_name': self.ai.model_name,
                'max_tokens': self.ai.max_tokens,
                'temperature': self.ai.temperature
            },
            'server': {
                'host': self.server.host,
                'port': self.server.port,
                'enable_logging': self.server.enable_logging,
                'log_level': self.server.log_level,
                'log_file': self.server.log_file
            }
        }
    
    def save_config(self, output_path: Optional[str] = None):
        """Save current configuration to file"""
        output_path = output_path or self.config_path
        
        try:
            config_dict = self.get_config_dict()
            
            # Ensure directory exists
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            with open(output_path, 'w') as f:
                if (output_path.endswith('.yaml') or output_path.endswith('.yml')) and YAML_SUPPORT:
                    yaml.dump(config_dict, f, default_flow_style=False, indent=2)
                else:
                    json.dump(config_dict, f, indent=2)
            
            print(f"Configuration saved to {output_path}")
        
        except Exception as e:
            print(f"Error saving configuration to {output_path}: {e}")
    
    def validate_config(self) -> List[str]:
        """Validate configuration and return list of issues"""
        issues = []
        
        # Check database path
        db_dir = os.path.dirname(self.database.sqlite_path)
        if db_dir and not os.path.exists(db_dir):
            try:
                os.makedirs(db_dir, exist_ok=True)
            except Exception:
                issues.append(f"Cannot create database directory: {db_dir}")
        
        # Check vector database directory
        if not os.path.exists(self.vector.persist_directory):
            try:
                os.makedirs(self.vector.persist_directory, exist_ok=True)
            except Exception:
                issues.append(f"Cannot create vector database directory: {self.vector.persist_directory}")
        
        # Check log directory
        log_dir = os.path.dirname(self.server.log_file)
        if log_dir and not os.path.exists(log_dir):
            try:
                os.makedirs(log_dir, exist_ok=True)
            except Exception:
                issues.append(f"Cannot create log directory: {log_dir}")
        
        # Check AI configuration
        if not self.ai.openai_api_key:
            issues.append("OpenAI API key not configured - AI features may not work")
        
        return issues
    
    def setup_directories(self):
        """Create necessary directories based on configuration"""
        directories = [
            os.path.dirname(self.database.sqlite_path),
            self.vector.persist_directory,
            os.path.dirname(self.server.log_file),
            "data",
            "logs",
            "backups"
        ]
        
        for directory in directories:
            if directory and not os.path.exists(directory):
                try:
                    os.makedirs(directory, exist_ok=True)
                    print(f"Created directory: {directory}")
                except Exception as e:
                    print(f"Failed to create directory {directory}: {e}")

# Global configuration instance
config = ConfigManager()
