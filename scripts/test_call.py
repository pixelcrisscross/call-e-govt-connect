import sys
import json
import os
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from calle import CalleClient
from app.config import settings

client = CalleClient(api_key=settings.CALLE_API_KEY)
CITIZEN_PHONE = os.getenv("CITIZEN_PHONE")
if not CITIZEN_PHONE:
    raise SystemExit("Set CITIZEN_PHONE in .env before making a test call.")

# Use a simple goal without schema
call = client.calls.create_and_wait(
    task=f"Call {CITIZEN_PHONE} and say 'Hello, this is a test call.'",
    recipient={"phone": CITIZEN_PHONE},
)

print(json.dumps(call, indent=2, default=str))