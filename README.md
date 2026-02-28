# TokenTrack 🔥

> Multi-AI token analytics & chat dashboard — Groq + Gemini, all in one place.

Track token usage across multiple AI providers, chat with any model, and see exactly which prompts cost the most.

**All data stays local. Nothing is sent anywhere.**

---

## Features

- 📊 **Analytics dashboard** — total tokens, per-provider breakdown, daily trends, top prompts
- 💬 **Multi-AI chat** — chat with Groq (Llama, Mixtral) or Gemini, tokens tracked automatically
- 🕘 **Full history** — every conversation logged with token counts
- 🎭 **Demo mode** — works out of the box without API keys

---

## Setup

**1. Install dependencies**
```bash
pip install groq google-generativeai
```

**2. Add your API keys to `.env`**
```
GROQ_API_KEY=your_groq_key_here
GEMINI_API_KEY=your_gemini_key_here
```

Get free keys from:
- Groq: https://console.groq.com
- Gemini: https://aistudio.google.com/app/apikey

**3. Run**
```bash
python main.py
```

Opens at `http://localhost:3456`

---

## Project Structure

```
token-track/
├── .env                  ← API keys (never commit this)
├── .gitignore
├── main.py               ← Entry point
├── server.py             ← HTTP server + API routes
├── aggregator.py         ← Token stats engine
├── storage.py            ← Reads/writes logs.json
├── connectors/
│   ├── groq.py           ← Groq integration
│   └── gemini.py         ← Gemini integration
├── logs.json             ← Auto-created chat history
└── dashboard.html        ← Browser UI
```

---

## Options

```bash
python main.py --port 8080    # custom port
python main.py --no-open      # don't auto-open browser
```

---

## Privacy

- Runs entirely on `localhost`
- `logs.json` is local and gitignored
- `.env` is gitignored — never committed
