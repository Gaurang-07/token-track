"""
connectors/groq.py - Groq API connector
"""

import os


def is_configured():
    return bool(os.getenv("GROQ_API_KEY", "").strip())


def get_models():
    return [
        {"id": "llama-3.3-70b-versatile", "name": "Llama 3.3 70B"},
        {"id": "llama-3.1-8b-instant",    "name": "Llama 3.1 8B"},
        {"id": "mixtral-8x7b-32768",       "name": "Mixtral 8x7B"},
        {"id": "gemma2-9b-it",             "name": "Gemma 2 9B"},
    ]


def chat(prompt, model="llama-3.3-70b-versatile", history=None):
    from groq import Groq
    
    api_key = os.getenv("GROQ_API_KEY", "").strip()
    if not api_key:
        raise RuntimeError("GROQ_API_KEY not set in .env file")

    client = Groq(api_key=api_key)

    messages = [{"role": "user", "content": prompt}]

    response = client.chat.completions.create(
        model=model,
        messages=messages,
        max_tokens=1024,
    )

    text         = response.choices[0].message.content
    input_tokens  = response.usage.prompt_tokens
    output_tokens = response.usage.completion_tokens

    return text, input_tokens, output_tokens