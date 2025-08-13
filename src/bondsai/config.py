"""Configuration management for BondsAI."""

import os
from typing import Optional
from dotenv import load_dotenv


class Config:
    """Configuration manager for BondsAI."""
    
    def __init__(self):
        """Initialize configuration with environment variables."""
        load_dotenv()
        
        # Required configuration
        self.openai_api_key = self._get_required_env("OPENAI_API_KEY")
        
        # Optional configuration with defaults
        self.openai_model = self._get_env("OPENAI_MODEL", "gpt-4o-mini")
        self.openai_temperature = float(self._get_env("OPENAI_TEMPERATURE", "0.7"))
        self.openai_max_tokens = int(self._get_env("OPENAI_MAX_TOKENS", "1000"))
    
    def _get_required_env(self, key: str) -> str:
        """Get a required environment variable."""
        value = os.getenv(key)
        if not value:
            raise ValueError(f"Required environment variable {key} is not set")
        return value
    
    def _get_env(self, key: str, default: str) -> str:
        """Get an optional environment variable with a default value."""
        return os.getenv(key, default)
    
    def validate(self) -> None:
        """Validate the configuration."""
        if not self.openai_api_key:
            raise ValueError("OPENAI_API_KEY is required")
        
        if self.openai_temperature < 0 or self.openai_temperature > 2:
            raise ValueError("OPENAI_TEMPERATURE must be between 0 and 2")
        
        if self.openai_max_tokens < 1:
            raise ValueError("OPENAI_MAX_TOKENS must be greater than 0")


# Global configuration instance
config = Config()
