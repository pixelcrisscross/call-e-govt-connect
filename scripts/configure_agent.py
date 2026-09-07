import sys
import os
from pathlib import Path

# Add the project root to Python path so we can import app
sys.path.append(str(Path(__file__).parent.parent))

from app.services.calle_agent import configure_agent

if __name__ == "__main__":
    webhook_url = os.getenv("WEBHOOK_URL")
    if not webhook_url:
        raise SystemExit("WEBHOOK_URL must be set in .env before configuring the agent.")
    configure_agent(webhook_url)