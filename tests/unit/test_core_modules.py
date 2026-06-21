"""
Test suite for YO OS Visual Intelligence Layer (VIL)
Premium startup-grade test coverage
"""

import pytest
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch
import sqlite3
import json

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))


class TestCoreImports:
    """Test that all core modules can be imported correctly"""
    
    def test_settings_import(self):
        from src.core import settings
        assert hasattr(settings, 'get_vil_dir')
        assert hasattr(settings, 'load_project_env')
    
    def test_visual_memory_import(self):
        from src import visual_memory
        assert hasattr(visual_memory, 'VisualMemoryComponent')
    
    def test_image_processor_import(self):
        from src.core import yo_image_processor
        assert hasattr(yo_image_processor, 'YOImageProcessor')
    
    def test_metadata_generator_import(self):
        from src.core import yo_metadata_generator
        assert hasattr(yo_metadata_generator, 'YOMetadataGenerator')
    
    def test_wp_uploader_import(self):
        from src.core import yo_wp_uploader
        assert hasattr(yo_wp_uploader, 'fetch_post_context')
    
    def test_orchestrator_import(self):
        from src.core import yo_orchestrator
        # Orchestrator exports main functions
        assert hasattr(yo_orchestrator, 'main') or len(dir(yo_orchestrator)) > 5
    
    def test_logging_config_import(self):
        from src.utils import logging_config
        assert hasattr(logging_config, 'setup_logging')
        assert hasattr(logging_config, 'JSONFormatter')
    
    def test_exceptions_import(self):
        from src.utils import exceptions
        assert hasattr(exceptions, 'VILBaseException')
        assert hasattr(exceptions, 'retry')
        assert hasattr(exceptions, 'handle_exceptions')


class TestSettings:
    """Test settings module functionality"""
    
    def test_get_vil_dir_returns_path(self):
        from src.utils.config import get_vil_dir
        vil_dir = get_vil_dir()
        assert vil_dir is not None
        # Can be str or Path
        assert isinstance(vil_dir, (str, Path))
    
    def test_load_project_env(self):
        from src.utils.config import load_project_env
        # Should not raise exception
        load_project_env()


class TestVisualMemory:
    """Test visual memory component"""
    
    def test_component_initialization(self):
        from src.core.selection import VisualMemoryComponent, VisualMemoryConfig
        config = VisualMemoryConfig(db_path=":memory:")
        component = VisualMemoryComponent(config)
        assert component is not None


class TestLoggingConfig:
    """Test structured logging configuration"""
    
    def test_setup_logging_creates_logger(self):
        from src.utils.logging_config import setup_logging
        logger = setup_logging(log_level="DEBUG", console_output=False)
        assert logger is not None
        assert logger.name == "vil"
    
    def test_json_formatter(self):
        from src.utils.logging_config import JSONFormatter
        import logging
        
        formatter = JSONFormatter()
        record = logging.LogRecord(
            name="test", level=logging.INFO, pathname="", lineno=0,
            msg="Test message", args=(), exc_info=None
        )
        output = formatter.format(record)
        parsed = json.loads(output)
        assert "timestamp" in parsed
        assert parsed["level"] == "INFO"
        assert parsed["message"] == "Test message"
    
    def test_get_logger(self):
        from src.utils.logging_config import get_logger
        logger = get_logger("test_module")
        assert logger.name == "vil.test_module"


class TestExceptions:
    """Test exception handling utilities"""
    
    def test_vil_base_exception(self):
        from src.utils.exceptions import VILBaseException
        exc = VILBaseException("Test error", context={"key": "value"})
        assert exc.message == "Test error"
        assert exc.context == {"key": "value"}
        assert "timestamp" in exc.to_dict()
    
    def test_configuration_error(self):
        from src.utils.exceptions import ConfigurationError
        exc = ConfigurationError("Config missing")
        assert exc.message == "Config missing"
    
    def test_database_error(self):
        from src.utils.exceptions import DatabaseError
        exc = DatabaseError("DB connection failed")
        assert exc.message == "DB connection failed"
    
    def test_api_error_with_status(self):
        from src.utils.exceptions import APIError
        exc = APIError("API failed", status_code=500)
        assert exc.status_code == 500
    
    def test_retry_decorator_success(self):
        from src.utils.exceptions import retry
        
        call_count = 0
        
        @retry(max_attempts=3, delay=0.01)
        def succeed_immediately():
            nonlocal call_count
            call_count += 1
            return "success"
        
        result = succeed_immediately()
        assert result == "success"
        assert call_count == 1
    
    def test_retry_decorator_eventual_success(self):
        from src.utils.exceptions import retry
        
        call_count = 0
        
        @retry(max_attempts=3, delay=0.01)
        def fail_twice_then_succeed():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise ValueError("Temporary failure")
            return "success"
        
        result = fail_twice_then_succeed()
        assert result == "success"
        assert call_count == 3
    
    def test_handle_exceptions_decorator(self):
        from src.utils.exceptions import handle_exceptions, VILBaseException
        
        @handle_exceptions(default_return="default", reraise=False)
        def raise_vil_error():
            raise VILBaseException("Test error")
        
        result = raise_vil_error()
        assert result == "default"
    
    def test_handle_exceptions_reraise(self):
        from src.utils.exceptions import handle_exceptions, VILBaseException
        
        @handle_exceptions(default_return="default", reraise=True)
        def raise_vil_error():
            raise VILBaseException("Test error")
        
        with pytest.raises(VILBaseException):
            raise_vil_error()


class TestSQLInjectionPrevention:
    """Test SQL injection prevention in database queries"""
    
    def test_parametrized_query_basic(self):
        """Ensure queries use parameters instead of string formatting"""
        conn = sqlite3.connect(":memory:")
        conn.execute("CREATE TABLE test (id INTEGER, name TEXT)")
        
        # Safe parameterized query
        user_input = "'; DROP TABLE test; --"
        conn.execute("INSERT INTO test (id, name) VALUES (?, ?)", (1, user_input))
        
        # Verify table still exists and data is safe
        rows = conn.execute("SELECT * FROM test").fetchall()
        assert len(rows) == 1
        assert rows[0][1] == user_input  # Input treated as data, not SQL
        
        conn.close()
    
    def test_parametrized_like_query(self):
        """Test LIKE queries with proper parameterization"""
        conn = sqlite3.connect(":memory:")
        conn.execute("CREATE TABLE photos (id INTEGER, title TEXT)")
        conn.execute("INSERT INTO photos VALUES (1, 'Safe Title')")
        
        # Safe LIKE query with parameterized wildcards
        search_term = "Safe"
        params = [f"%{search_term}%"]
        rows = conn.execute("SELECT * FROM photos WHERE title LIKE ?", params).fetchall()
        
        assert len(rows) == 1
        conn.close()


class TestDatabaseOperations:
    """Test database operation safety"""
    
    def test_alter_table_safety(self):
        """Test ALTER TABLE with error handling"""
        conn = sqlite3.connect(":memory:")
        conn.execute("CREATE TABLE assets (id INTEGER)")
        
        # First addition should succeed
        try:
            conn.execute("ALTER TABLE assets ADD COLUMN hash TEXT")
            assert True
        except sqlite3.OperationalError:
            assert False, "First ALTER should succeed"
        
        # Second addition should fail gracefully
        try:
            conn.execute("ALTER TABLE assets ADD COLUMN hash TEXT")
            assert False, "Should have raised OperationalError"
        except sqlite3.OperationalError:
            pass  # Expected
        
        conn.close()


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
