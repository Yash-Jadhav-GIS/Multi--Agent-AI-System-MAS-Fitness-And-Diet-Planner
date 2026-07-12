from groq import Groq
from app.config import settings


class LLMClient:
    """
    Wraps Groq API calls with automatic key rotation and model fallback,
    so a single bad/rate-limited key or model doesn't break the user experience.
    """

    def __init__(self):
        self.api_keys = settings.GROQ_API_KEYS
        self.models = [settings.PRIMARY_MODEL, settings.FALLBACK_MODEL]

    def generate(self, prompt: str, system: str = "You are a helpful fitness and diet assistant.") -> str:
        """
        Try each API key with the primary model first, then the fallback model,
        rotating through keys on failure. Raises RuntimeError only if everything fails.
        """
        last_error = None

        for model in self.models:
            for key in self.api_keys:
                try:
                    client = Groq(api_key=key)
                    response = client.chat.completions.create(
                        model=model,
                        messages=[
                            {"role": "system", "content": system},
                            {"role": "user", "content": prompt},
                        ],
                    )
                    return response.choices[0].message.content
                except Exception as e:
                    last_error = e
                    continue  # try next key, then next model

        raise RuntimeError(f"All Groq keys/models failed. Last error: {last_error}")


llm_client = LLMClient()