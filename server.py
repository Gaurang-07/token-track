"""
server.py - HTTP server with dashboard + chat API endpoints.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
import json
import os
import sys
import threading
import webbrowser
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from urllib.parse import urlparse, parse_qs

# Load .env before anything else
def load_env():
    print("DEBUG - GROQ_API_KEY:", os.getenv("GROQ_API_KEY", "NOT FOUND"))
print("DEBUG - Python path:", sys.path)
try:
    import groq
    print("DEBUG - groq imported OK, version:", groq.__version__)
except Exception as e:
    print("DEBUG - groq import failed:", e)
    env_path = Path(__file__).parent / ".env"
    if env_path.exists():
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, _, val = line.partition("=")
                    os.environ.setdefault(key.strip(), val.strip())

load_env()

from storage import load_all_logs, save_entry, clear_logs
from aggregator import aggregate
import connectors.groq as groq_connector
import connectors.gemini as gemini_connector


def get_dashboard_html():
    html_path = Path(__file__).parent / "dashboard.html"
    if html_path.exists():
        return html_path.read_text(encoding="utf-8")
    return "<h1>dashboard.html not found</h1>"


def build_stats():
    logs = load_all_logs()
    data = aggregate(logs)
    data["providers_status"] = {
        "groq":   groq_connector.is_configured(),
        "gemini": gemini_connector.is_configured(),
    }
    data["groq_models"]   = groq_connector.get_models()
    data["gemini_models"] = gemini_connector.get_models()

    # Demo mode if no real logs
    if not logs:
        data["is_demo"] = True
        data = _inject_demo(data)
    else:
        data["is_demo"] = False

    return data


def _inject_demo(data):
    """Inject realistic demo stats when no logs exist."""
    import random
    from datetime import datetime, timedelta
    random.seed(7)

    now = datetime.now()
    fake_logs = []
    providers = [("groq", "llama-3.3-70b-versatile"), ("gemini", "gemini-1.5-flash")]
    prompts = [
        "Write a login system with JWT auth",
        "Yes", "Do it", "Continue",
        "Build a full CRUD REST API",
        "Fix the bug", "OK",
        "Refactor this to async",
        "Add unit tests",
        "Explain this code to me",
    ]
    for i in range(60):
        provider, model = random.choice(providers)
        inp = random.randint(500, 8000)
        out = random.randint(200, 1500)
        fake_logs.append({
            "provider": provider, "model": model,
            "prompt": random.choice(prompts),
            "input_tokens": inp, "output_tokens": out,
            "total_tokens": inp + out,
            "date": (now - timedelta(days=random.randint(0, 14))).strftime("%Y-%m-%d"),
            "timestamp": (now - timedelta(days=random.randint(0, 14))).isoformat(),
        })

    return aggregate(fake_logs) | {"is_demo": True,
        "providers_status": data["providers_status"],
        "groq_models": data["groq_models"],
        "gemini_models": data["gemini_models"]}


class Handler(BaseHTTPRequestHandler):

    def log_message(self, *args): pass  # suppress logs

    def do_GET(self):
        path = urlparse(self.path).path
        if path in ("/", "/index.html"):
            self._html(get_dashboard_html())
        elif path == "/api/stats":
            self._json(build_stats())
        elif path == "/api/logs":
            self._json(load_all_logs())
        elif path == "/api/clear":
            clear_logs()
            self._json({"ok": True})
        else:
            self.send_response(404); self.end_headers()

    def do_POST(self):
        path = urlparse(self.path).path
        length = int(self.headers.get("Content-Length", 0))
        body = json.loads(self.rfile.read(length)) if length else {}

        if path == "/api/chat":
            self._handle_chat(body)
        else:
            self.send_response(404); self.end_headers()

    def _handle_chat(self, body):
        provider = body.get("provider", "groq")
        model    = body.get("model", "")
        prompt   = body.get("prompt", "").strip()
        history  = body.get("history", [])

        if not prompt:
            self._json({"error": "Empty prompt"}, 400); return

        try:
            if provider == "groq":
                text, inp, out = groq_connector.chat(prompt, model, history)
            elif provider == "gemini":
                text, inp, out = gemini_connector.chat(prompt, model, history)
            else:
                self._json({"error": f"Unknown provider: {provider}"}); return

            entry = save_entry(provider, model, prompt, text, inp, out, inp + out)
            self._json({"response": text, "input_tokens": inp,
                        "output_tokens": out, "total_tokens": inp + out,
                        "entry_id": entry["id"]})
        except Exception as e:
            self._json({"error": str(e)}, 500)

    def _html(self, content):
        b = content.encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(b)))
        self.end_headers()
        self.wfile.write(b)

    def _json(self, data, code=200):
        b = json.dumps(data, default=str).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Content-Length", str(len(b)))
        self.end_headers()
        self.wfile.write(b)


def run(port=3456, open_browser=True):
    print(f"\n{'─'*52}")
    print(f"  TokenTrack — Multi-AI Token Analytics")
    print(f"{'─'*52}")
    print(f"  Groq   : {'✓ configured' if groq_connector.is_configured() else '✗ add GROQ_API_KEY to .env'}")
    print(f"  Gemini : {'✓ configured' if gemini_connector.is_configured() else '✗ add GEMINI_API_KEY to .env'}")
    print(f"\n  Dashboard → http://localhost:{port}")
    print(f"  Press Ctrl+C to stop\n")

    server = HTTPServer(("localhost", port), Handler)
    if open_browser:
        threading.Timer(0.6, lambda: webbrowser.open(f"http://localhost:{port}")).start()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n  Stopped. Bye!")
        server.shutdown()
