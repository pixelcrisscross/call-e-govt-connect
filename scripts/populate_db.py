# scripts/populate_db.py
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.database import SessionLocal
from app.models import CallRecord
from datetime import datetime

db = SessionLocal()
samples = [
    ("pothole on Main", "Springfield", "Main St", "pothole", "high"),
    ("streetlight broken", "Springfield", "Oak St", "streetlight", "medium"),
    ("garbage overflow", "Riverside", "River Rd", "garbage", "low"),
]

for transcript, city, location, issue, severity in samples:
    call_id = f"manual_{city}_{issue}"
    if db.query(CallRecord).filter_by(calle_call_id=call_id).first():
        continue
    rec = CallRecord(
        calle_call_id=call_id,
        transcript=transcript,
        structured_result={
            "city": city,
            "location": location,
            "issue_type": issue,
            "severity": severity
        },
        created_at=datetime.utcnow()
    )
    db.add(rec)
db.commit()
db.close()
print("✅ Sample records inserted.")