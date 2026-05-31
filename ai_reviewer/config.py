import os
from pathlib import Path
from dotenv import load_dotenv

# Find and load the .env file from the workspace/project root
env_path = Path(__file__).resolve().parents[1] / ".env"
load_dotenv(dotenv_path=env_path)

class ConfigError(Exception):
    """Exception raised when config is invalid or missing required variables."""
    pass

class Config:
    """Manages project configurations and environment variables."""

    # Default model configuration
    DEFAULT_GEMINI_MODEL = "gemini-2.5-flash"
    DEFAULT_OPENAI_MODEL = "gpt-4o-mini"

    @staticmethod
    def get_provider() -> str:
        """
        Determines the AI provider to use.
        Priority:
        1. AI_PROVIDER env variable ('gemini' or 'openai')
        2. Auto-detect based on available keys (GEMINI_API_KEY takes precedence)
        """
        provider = os.getenv("AI_PROVIDER")
        if provider:
            provider = provider.lower().strip()
            if provider not in ("gemini", "openai"):
                raise ConfigError(
                    f"Unsupported AI_PROVIDER '{provider}'. "
                    "Please set AI_PROVIDER to either 'gemini' or 'openai'."
                )
            return provider

        # Auto-detect
        if os.getenv("GEMINI_API_KEY"):
            return "gemini"
        elif os.getenv("OPENAI_API_KEY"):
            return "openai"
        
        # Default fallback
        return "gemini"

    @classmethod
    def get_api_key(cls, provider: str) -> str:
        """Gets the API key for the chosen provider or raises an error."""
        if provider == "gemini":
            key = os.getenv("GEMINI_API_KEY")
            if not key:
                raise ConfigError(
                    "Google Gemini API Key not found.\n"
                    "Please set the GEMINI_API_KEY environment variable, or add it to a .env file.\n"
                    "Get a free key from Google AI Studio: https://aistudio.google.com/"
                )
            return key
        elif provider == "openai":
            key = os.getenv("OPENAI_API_KEY")
            if not key:
                raise ConfigError(
                    "OpenAI API Key not found.\n"
                    "Please set the OPENAI_API_KEY environment variable, or add it to a .env file.\n"
                    "Get an OpenAI key: https://platform.openai.com/"
                )
            return key
        else:
            raise ConfigError(f"Unknown AI Provider: {provider}")

    @classmethod
    def get_model(cls, provider: str) -> str:
        """Gets the model name configured for the provider."""
        if provider == "gemini":
            return os.getenv("GEMINI_MODEL", cls.DEFAULT_GEMINI_MODEL)
        elif provider == "openai":
            return os.getenv("OPENAI_MODEL", cls.DEFAULT_OPENAI_MODEL)
        else:
            raise ConfigError(f"Unknown AI Provider: {provider}")
