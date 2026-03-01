"""
connectors/gemini.py - Google Gemini API connector
"""

import os


def is_configured():
    return bool(os.getenv("GEMINI_API_KEY", "").strip())


def get_models():
    return [
        {"id": "gemini-2.0-flash",        "name": "Gemini 2.0 Flash"},
        {"id": "gemini-2.0-flash-lite",    "name": "Gemini 2.0 Flash Lite"},
        {"id": "gemini-1.5-flash-latest",  "name": "Gemini 1.5 Flash"},
        {"id": "gemini-1.5-pro-latest",    "name": "Gemini 1.5 Pro"},
    ]


def chat(prompt, model="gemini-2.0-flash", history=None):
    """
    Send a prompt to Gemini and return (response_text, input_tokens, output_tokens).
    """
    try:
        import google.generativeai as genai
    except ImportError:
        raise RuntimeError("Gemini package not installed. Run: pip install google-generativeai")

    api_key = os.getenv("GEMINI_API_KEY", "").strip()
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY not set in .env file")

    genai.configure(api_key=api_key)
    gen_model = genai.GenerativeModel(model)

    # Build history for multi-turn
    chat_history = []
    if history:
        for h in history:
            chat_history.append({"role": "user",  "parts": [h["prompt"]]})
            chat_history.append({"role": "model", "parts": [h["response"]]})

    session = gen_model.start_chat(history=chat_history)
    response = session.send_message(prompt)

    text = response.text

    # Gemini returns token counts in usage_metadata
    try:
        input_tokens  = response.usage_metadata.prompt_token_count
        output_tokens = response.usage_metadata.candidates_token_count
    except Exception:
        # Estimate if metadata unavailable
        input_tokens  = len(prompt.split()) * 4 // 3
        output_tokens = len(text.split()) * 4 // 3

    return text, input_tokens, output_tokens
