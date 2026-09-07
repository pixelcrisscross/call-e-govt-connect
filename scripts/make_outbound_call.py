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
    raise SystemExit("Set CITIZEN_PHONE in .env before making an outbound call.")

RECIPIENT = {
    "phone": CITIZEN_PHONE,
    "region": "IN",
    "locale": "en-IN"
}

RESULT_SCHEMA = {
    "type": "object",
    "required": ["city", "location", "issue_type", "severity"],
    "properties": {
        "city": {"type": "string"},
        "location": {"type": "string"},
        "issue_type": {"type": "string"},
        "severity": {"type": "string", "enum": ["low", "medium", "high", "emergency"]}
    }
}

GOAL = """
You are a government assistant named Sahayak calling a citizen to collect an incident report.
Ask:
1. What issue are they reporting?
2. Which city and street address?
3. How severe is it (low, medium, high, emergency)?
Confirm the details and end the call.
Return the structured result.
"""

print(f"📞 Calling {CITIZEN_PHONE}...")

# Temporarily comment out webhook_url to isolate the call
call = client.calls.create_and_wait(
    task=GOAL,
    recipient=RECIPIENT,
    result_schema=RESULT_SCHEMA,
    webhook_url=settings.WEBHOOK_URL,   # <-- COMMENT THIS FOR NOW
)

print("\n📋 Full API response:")
print(json.dumps(call, indent=2, default=str))

if call.get("status") == "completed":
    print("\n✅ Call succeeded!")
    print("Structured result:", call.get("structured_result"))
else:
    print("\n❌ Call failed.")
    if "failure_code" in call:
        print("Failure code:", call["failure_code"])
    if "failure_message" in call:
        print("Failure message:", call["failure_message"])
    if "recipients" in call:
        for rcp in call["recipients"]:
            print(f"Recipient {rcp.get('id')}: status {rcp.get('status')}")
            if "attempts" in rcp:
                for att in rcp["attempts"]:
                    print(f"  Attempt: {att.get('failure_code')} - {att.get('failure_message')}")