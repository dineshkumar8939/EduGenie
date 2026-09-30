import os
from typing import Optional

from google import genai
from google.genai import types


class GeminiError(RuntimeError):
    """Raised when Gemini cannot be used successfully."""


_client: Optional[genai.Client] = None


def get_client() -> genai.Client:
    global _client

    if _client is not None:
        return _client

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise GeminiError(
            "GEMINI_API_KEY is not configured. Copy .env.example to .env "
            "and add your Gemini API key."
        )

    _client = genai.Client(api_key=api_key)
    return _client


def generate_text(
    prompt: str,
    *,
    temperature: float = 0.4,
    max_output_tokens: int = 1200,
) -> str:
    client = get_client()
    model = os.getenv("GEMINI_MODEL", "gemini-3.8-flash")

    try:
        response = client.models.generate_content(
            model=model,
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=temperature,
                max_output_tokens=max_output_tokens,
                candidate_count=1,
            ),
        )
    except Exception as exc:
        raise GeminiError(f"Gemini request failed: {exc}") from exc

    text = getattr(response, "text", None)
    if not text:
        raise GeminiError("Gemini returned an empty response.")

    return text.strip()
