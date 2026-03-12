"""
Shared AI client that supports OpenAI and Google Gemini interchangeably.

Priority:
  1. OpenAI  – when OPENAI_API_KEY is set and is not a placeholder value.
  2. Gemini  – when GEMINI_API_KEY is set and is not a placeholder value.
  3. Raises  – if neither key is usable (callers should fall back to templates).
"""

import openai


def _is_placeholder(key: str, prefix: str) -> bool:
    return not key or key.startswith(prefix)


def _strip_markdown_fences(raw: str) -> str:
    """Strip optional markdown code fences and return the inner text."""
    if "```" in raw:
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    return raw.strip()


def call_ai(prompt: str, openai_key: str = "", gemini_key: str = "",
            max_tokens: int = 4000) -> str:
    """Send *prompt* to whichever AI provider is configured and return raw text.

    OpenAI is preferred when both keys are present.
    The returned text may be a JSON string wrapped in markdown code fences –
    callers should use :func:`extract_json_block` to clean it before parsing.

    Raises :class:`ValueError` if neither key is usable.
    """
    if not _is_placeholder(openai_key, "sk-your"):
        client = openai.OpenAI(api_key=openai_key)
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=max_tokens,
        )
        return response.choices[0].message.content.strip()

    if not _is_placeholder(gemini_key, "your-gemini"):
        import google.generativeai as genai  # optional dependency

        genai.configure(api_key=gemini_key)
        model = genai.GenerativeModel(
            "gemini-1.5-flash",
            generation_config={"temperature": 0.7, "max_output_tokens": max_tokens},
        )
        response = model.generate_content(prompt)
        return response.text.strip()

    raise ValueError("No valid AI API key configured.")


def has_ai_key(openai_key: str = "", gemini_key: str = "") -> bool:
    """Return True if at least one usable AI key is present."""
    return (
        not _is_placeholder(openai_key, "sk-your")
        or not _is_placeholder(gemini_key, "your-gemini")
    )


def active_provider(openai_key: str = "", gemini_key: str = "") -> str:
    """Return a human-readable label for the active AI provider."""
    if not _is_placeholder(openai_key, "sk-your"):
        return "OpenAI (GPT-3.5)"
    if not _is_placeholder(gemini_key, "your-gemini"):
        return "Google Gemini 1.5 Flash"
    return "şablon (API anahtarı yok)"


extract_json_block = _strip_markdown_fences
