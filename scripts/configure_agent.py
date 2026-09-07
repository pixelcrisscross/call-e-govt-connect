import sys
from pathlib import Path

# Add the project root to Python path so we can import app
sys.path.append(str(Path(__file__).parent.parent))

from app.services.calle_agent import configure_agent

if __name__ == "__main__":
    # Replace with your public webhook URL (use ngrok)
    WEBHOOK_URL = "https://your-ngrok.ngrok-free.app/webhook/call-e"
    configure_agent(WEBHOOK_URL)