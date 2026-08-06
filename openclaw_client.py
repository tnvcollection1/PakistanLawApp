import os
import requests

OPENCLAW_API_KEY = os.environ.get("OPENCLAW_API_KEY")
OPENCLAW_BASE_URL = os.environ.get("OPENCLAW_BASE_URL", "https://api.openclaw.ai/v1")

def chat_completions(messages, model="gpt-4o", temperature=0.7):
    headers = {
        "Authorization": f"Bearer {OPENCLAW_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": model,
        "messages": messages,
        "temperature": temperature
    }
    resp = requests.post(f"{OPENCLAW_BASE_URL}/chat/completions", json=payload, headers=headers, timeout=120)
    resp.raise_for_status()
    return resp.json()
