import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    """Central place for all API keys and model config, with fallback support."""

    GROQ_API_KEYS: list[str] = [
        key for key in [
            os.getenv("GROQ_API_KEY_1"),
            os.getenv("GROQ_API_KEY_2"),
            os.getenv("GROQ_API_KEY_3"),
            os.getenv("GROQ_API_KEY_4"),
        ] if key  # filters out None/empty if you only set 2-3 keys
    ]

    PRIMARY_MODEL: str = os.getenv("PRIMARY_MODEL", "llama-3.3-70b-versatile")
    FALLBACK_MODEL: str = os.getenv("FALLBACK_MODEL", "llama-3.1-8b-instant")

    def __init__(self):
        if not self.GROQ_API_KEYS:
            raise RuntimeError(
                "No Groq API keys found. Set at least GROQ_API_KEY_1 in your .env file."
            )


settings = Settings()