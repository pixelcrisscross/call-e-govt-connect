import openai
import json
from app.config import settings
from app.database import SessionLocal
from app.models import CallRecord

openai.api_key = settings.OPENAI_API_KEY

def analyze_call(record_id: int):
    db = SessionLocal()
    record = db.query(CallRecord).filter(CallRecord.id == record_id).first()
    if not record:
        return

    prompt = f"""
    Given the following citizen call transcript and structured data:
    Transcript: {record.transcript}
    Structured: {json.dumps(record.structured_result)}
    Provide:
    1. A one‑sentence summary.
    2. Sentiment (positive, neutral, negative).
    3. Up to 3 key topics (keywords or short phrases).
    Return as JSON with keys: summary, sentiment, topics.
    """
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3
        )
        result = json.loads(response.choices[0].message.content)
        record.summary = result.get("summary")
        record.sentiment = result.get("sentiment")
        record.topics = result.get("topics", [])
        db.commit()
    except Exception as e:
        print(f"LLM analysis failed for record {record_id}: {e}")
    finally:
        db.close()