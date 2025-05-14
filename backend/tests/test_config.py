import pytest
import os
from app.config import (
    Settings,
    get_settings,
    DatabaseSettings,
    APISettings,
    SecuritySettings,
    LoggingSettings
)

def test_settings_creation():
    settings = Settings()
    assert isinstance(settings, Settings)
    assert isinstance(settings.database, DatabaseSettings)
    assert isinstance(settings.api, APISettings)
    assert isinstance(settings.security, SecuritySettings)
    assert isinstance(settings.logging, LoggingSettings)

def test_database_settings():
    settings = DatabaseSettings()
    assert settings.database_url is not None
    assert settings.echo is False
    assert settings.pool_size > 0
    assert settings.max_overflow >= 0
    assert settings.pool_timeout >= 0
    assert settings.pool_recycle >= 0

def test_database_settings_custom():
    os.environ["DATABASE_URL"] = "postgresql://test:test@localhost:5432/test"
    os.environ["DATABASE_ECHO"] = "true"
    os.environ["DATABASE_POOL_SIZE"] = "20"
    
    settings = DatabaseSettings()
    assert settings.database_url == "postgresql://test:test@localhost:5432/test"
    assert settings.echo is True
    assert settings.pool_size == 20

def test_api_settings():
    settings = APISettings()
    assert settings.title is not None
    assert settings.description is not None
    assert settings.version is not None
    assert settings.debug is False
    assert settings.host is not None
    assert settings.port > 0
    assert settings.reload is False

def test_api_settings_custom():
    os.environ["API_TITLE"] = "Test API"
    os.environ["API_DESCRIPTION"] = "Test Description"
    os.environ["API_VERSION"] = "1.0.0"
    os.environ["API_DEBUG"] = "true"
    os.environ["API_HOST"] = "0.0.0.0"
    os.environ["API_PORT"] = "8000"
    os.environ["API_RELOAD"] = "true"
    
    settings = APISettings()
    assert settings.title == "Test API"
    assert settings.description == "Test Description"
    assert settings.version == "1.0.0"
    assert settings.debug is True
    assert settings.host == "0.0.0.0"
    assert settings.port == 8000
    assert settings.reload is True

def test_security_settings():
    settings = SecuritySettings()
    assert settings.secret_key is not None
    assert settings.algorithm is not None
    assert settings.access_token_expire_minutes > 0
    assert settings.refresh_token_expire_days > 0
    assert settings.cors_origins is not None

def test_security_settings_custom():
    os.environ["SECRET_KEY"] = "test_secret_key"
    os.environ["ALGORITHM"] = "HS512"
    os.environ["ACCESS_TOKEN_EXPIRE_MINUTES"] = "30"
    os.environ["REFRESH_TOKEN_EXPIRE_DAYS"] = "7"
    os.environ["CORS_ORIGINS"] = "http://localhost:3000,http://localhost:8000"
    
    settings = SecuritySettings()
    assert settings.secret_key == "test_secret_key"
    assert settings.algorithm == "HS512"
    assert settings.access_token_expire_minutes == 30
    assert settings.refresh_token_expire_days == 7
    assert len(settings.cors_origins) == 2
    assert "http://localhost:3000" in settings.cors_origins
    assert "http://localhost:8000" in settings.cors_origins

def test_logging_settings():
    settings = LoggingSettings()
    assert settings.level is not None
    assert settings.format is not None
    assert settings.file is not None
    assert settings.max_size > 0
    assert settings.backup_count > 0

def test_logging_settings_custom():
    os.environ["LOG_LEVEL"] = "DEBUG"
    os.environ["LOG_FORMAT"] = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    os.environ["LOG_FILE"] = "test.log"
    os.environ["LOG_MAX_SIZE"] = "10485760"
    os.environ["LOG_BACKUP_COUNT"] = "5"
    
    settings = LoggingSettings()
    assert settings.level == "DEBUG"
    assert settings.format == "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    assert settings.file == "test.log"
    assert settings.max_size == 10485760
    assert settings.backup_count == 5

def test_get_settings():
    settings = get_settings()
    assert isinstance(settings, Settings)
    assert settings is get_settings()  # Test singleton pattern

def test_settings_validation():
    with pytest.raises(ValueError):
        DatabaseSettings(database_url="invalid_url")
    
    with pytest.raises(ValueError):
        APISettings(port=-1)
    
    with pytest.raises(ValueError):
        SecuritySettings(access_token_expire_minutes=0)
    
    with pytest.raises(ValueError):
        LoggingSettings(level="INVALID_LEVEL")

def test_settings_environment_variables():
    # Test that environment variables are properly loaded
    os.environ["DATABASE_URL"] = "postgresql://test:test@localhost:5432/test"
    os.environ["API_TITLE"] = "Test API"
    os.environ["SECRET_KEY"] = "test_secret_key"
    os.environ["LOG_LEVEL"] = "DEBUG"
    
    settings = get_settings()
    assert settings.database.database_url == "postgresql://test:test@localhost:5432/test"
    assert settings.api.title == "Test API"
    assert settings.security.secret_key == "test_secret_key"
    assert settings.logging.level == "DEBUG"

def test_settings_default_values():
    # Clear environment variables
    for key in os.environ:
        if key.startswith(("DATABASE_", "API_", "SECRET_", "LOG_")):
            del os.environ[key]
    
    settings = get_settings()
    assert settings.database.database_url is not None
    assert settings.api.title is not None
    assert settings.security.secret_key is not None
    assert settings.logging.level is not None 