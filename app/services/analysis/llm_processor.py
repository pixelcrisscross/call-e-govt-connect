import json
import google.generativeai as genai
from app.config import settings
from app.database import SessionLocal
from app.models import CallRecord

genai.configure(api_key=settings.GEMINI_API_KEY)
model = genai.GenerativeModel(settings.GEMINI_MODEL)

def analyze_call(record_id: int):
    db = SessionLocal()
    try:
        record = db.query(CallRecord).filter(CallRecord.id == record_id).first()
        if not record:
            return

        structured = record.structured_result if isinstance(record.structured_result, dict) else {}
        prompt = f"""
        Given the following citizen call transcript and structured data:
        Transcript: {record.transcript}
        Structured: {json.dumps(structured)}
        Provide:
        1. A one-sentence summary.
        2. Sentiment (positive, neutral, negative).
        3. Up to 3 key topics (keywords or short phrases).
        Return as JSON with keys: summary, sentiment, topics.
        """
        response = model.generate_content(prompt)
        response_text = (response.text or "").strip()
        if response_text.startswith("```"):
            response_text = response_text.strip("`").removeprefix("json").strip()
        result = json.loads(response_text)
        if not isinstance(result, dict):
            raise ValueError("LLM response must be a JSON object")
        record.summary = result.get("summary")
        record.sentiment = result.get("sentiment")
        record.topics = result.get("topics", []) if isinstance(result.get("topics", []), list) else []
        db.commit()
    except Exception as e:
        print(f"LLM analysis failed for record {record_id}: {e}")
    finally:
        db.close()