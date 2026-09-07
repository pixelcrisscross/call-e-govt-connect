import json
import google.generativeai as genai
from app.config import settings
from app.database import SessionLocal
from app.models import CallRecord, AnalysisResult

genai.configure(api_key=settings.GEMINI_API_KEY)

def get_embedding(text: str) -> list:
    # Use Gemini's embedding model
    result = genai.embed_content(
        model=settings.GEMINI_EMBEDDING_MODEL,
        content=text,
        task_type="retrieval_document"
    )
    return result["embedding"]

def update_embeddings_for_all():
    db = SessionLocal()
    try:
        records = db.query(CallRecord).all()
        for rec in records:
            structured = rec.structured_result if isinstance(rec.structured_result, dict) else {}
            text = f"{rec.transcript or ''} {structured.get('issue_type', '')}"
            emb = get_embedding(text)
            analysis = db.query(AnalysisResult).filter_by(call_id=rec.id).first()
            if not analysis:
                analysis = AnalysisResult(call_id=rec.id, embedding=json.dumps(emb))
                db.add(analysis)
            else:
                analysis.embedding = json.dumps(emb)
            db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()