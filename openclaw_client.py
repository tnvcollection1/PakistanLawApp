# OpenClaw API Client
from dotenv import load_dotenv
load_dotenv()

import os
OPENCLAW_API_KEY = os.getenv("OPENCLAW_API_KEY")
print(f"[OpenClaw] API key loaded: {OPENCLAW_API_KEY[:4]}..." if OPENCLAW_API_KEY else "[OpenClaw] API key not set")
