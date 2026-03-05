"""
connectors/gemini.py - Google Gemini API connector
"""

import os


def is_configured():
    return bool(os.getenv("GEMINI_API_KEY", "").strip())


def get_models():
    return [
        {"id": "gemini-2.0-flash",      "name": "Gemini 2.0 Flash"},
        {"id": "gemini-2.0-flash-lite",  "name": "Gemini 2.0 Flash Lite"},
        {"id": "gemini-2.5-flash",       "name": "Gemini 2.5 Flash"},
        {"id": "gemini-flash-latest",    "name": "Gemini Flash Latest"},
    ]


def chat(prompt, model="gemini-2.0-flash-lite", history=None):
    try:
        from google import genai
    except ImportError:
        raise RuntimeError("Gemini package not installed. Run: pip install google-genai")

    api_key = os.getenv("GEMINI_API_KEY", "").strip()
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY not set in .env file")

    client = genai.Client(api_key=api_key)
    response = client.models.generate_content(
        model=model,
        contents=prompt
    )

    text = response.text
    try:
        input_tokens  = response.usage_metadata.prompt_token_count
        output_tokens = response.usage_metadata.candidates_token_count
    except Exception:
        input_tokens  = len(prompt.split()) * 4 // 3
        output_tokens = len(text.split()) * 4 // 3

    return text, input_tokens, output_tokens