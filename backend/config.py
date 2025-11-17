"""
Configuration module for the Agentic Development System.
Loads environment variables and provides settings.
"""
import os
from typing import List
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # ============================================
    # LLM Configuration
    # ============================================
    LLM_API_KEY: str = Field(..., description="LLM API key")
    LLM_BASE_URL: str = Field(default="https://api.groq.com/openai/v1", description="LLM base URL")
    LLM_MODEL: str = Field(default="llama-3.1-70b-versatile", description="LLM model name")
    LLM_TEMPERATURE: float = Field(default=0.7, description="LLM temperature")
    LLM_MAX_TOKENS: int = Field(default=8000, description="Max tokens per request")

    # ============================================
    # Daytona Configuration
    # ============================================
    DAYTONA_API_KEY: str = Field(..., description="Daytona API key")
    DAYTONA_API_URL: str = Field(default="https://app.daytona.io/api", description="Daytona API URL")
    DAYTONA_TARGET: str = Field(default="default", description="Daytona target")

    # ============================================
    # OpenHands Configuration
    # ============================================
    SANDBOX_RUNTIME_CONTAINER_IMAGE: str = Field(
        default="ghcr.io/all-hands-ai/runtime:0.38-nikolaik",
        description="Sandbox container image"
    )
    WORKSPACE_BASE: str = Field(default="/workspace", description="Workspace base path")
    WORKSPACE_MOUNT_PATH: str = Field(default="./workspace", description="Host workspace mount path")
    WORKSPACE_MOUNT_PATH_IN_SANDBOX: str = Field(default="/workspace", description="Sandbox workspace path")

    # ============================================
    # Application Configuration
    # ============================================
    APP_PORT: int = Field(default=3000, description="Frontend port")
    BACKEND_PORT: int = Field(default=3001, description="Backend port")
    NGINX_PORT: int = Field(default=80, description="Nginx port")

    # ============================================
    # Logging Configuration
    # ============================================
    LOG_LEVEL: str = Field(default="INFO", description="Logging level")
    DEBUG: bool = Field(default=False, description="Debug mode")
    LOG_ALL_EVENTS: bool = Field(default=False, description="Log all events")

    # ============================================
    # Security Configuration
    # ============================================
    ALLOWED_ORIGINS: str = Field(
        default="http://localhost,http://localhost:80,http://localhost:3000",
        description="Allowed CORS origins"
    )
    JWT_SECRET: str = Field(default="change-this-secret", description="JWT secret key")
    SESSION_TIMEOUT: int = Field(default=3600, description="Session timeout in seconds")

    # ============================================
    # Agent Configuration
    # ============================================
    AGENT_MAX_ITERATIONS: int = Field(default=100, description="Max agent iterations")
    AGENT_TIMEOUT: int = Field(default=600, description="Agent timeout in seconds")
    SANDBOX_TIMEOUT: int = Field(default=900, description="Sandbox timeout in seconds")
    FILE_UPLOAD_MAX_SIZE_MB: int = Field(default=100, description="Max file upload size in MB")

    @property
    def allowed_origins_list(self) -> List[str]:
        """Parse ALLOWED_ORIGINS into a list."""
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",")]

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True
        extra = "allow"  # Allow extra fields from .env (e.g., GEMINI_API_KEY, CODE_SERVER_PASSWORD)


# Create settings instance
settings = Settings()


# Validate critical settings
def validate_settings():
    """Validate that critical settings are configured."""
    errors = []

    if not settings.LLM_API_KEY:
        errors.append("LLM_API_KEY is not set")

    if not settings.DAYTONA_API_KEY:
        errors.append("DAYTONA_API_KEY is not set")

    if settings.JWT_SECRET == "change-this-secret":
        print("⚠️  Warning: Using default JWT_SECRET. Please change in production!")

    if errors:
        raise ValueError(f"Configuration errors: {', '.join(errors)}")

    print("✅ Configuration validated successfully")


# Run validation on import
try:
    validate_settings()
except Exception as e:
    print(f"❌ Configuration validation failed: {e}")
    raise
