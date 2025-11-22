"""
Lightweight settings loader for model provider configuration.
Environment-driven, re-evaluated on each call to avoid stale values in tests.
"""

from pydantic_settings import BaseSettings
from pydantic import ConfigDict


class Settings(BaseSettings):
    model_provider: str = "stub"  # stub | ollama (future: openai/anthropic)
    ollama_enabled: bool = False
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3.1:8b"

    model_config = ConfigDict(env_file=".env", extra="ignore")


def get_settings() -> Settings:
    """Return fresh settings (re-read env)."""
    return Settings()
