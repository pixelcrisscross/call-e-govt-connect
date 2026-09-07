import json
from app.database import SessionLocal
from app.models import CallRecord, AnalysisResult
from sentence_transformers import SentenceTransformer

# Load a small, fast, free model – no API key needed
model = SentenceTransformer("all-MiniLM-L6-v2")

def get_embedding(text: str) -> list:
    """Generate embedding using local SentenceTransformer."""
    return model.encode(text).tolist()

def update_embeddings_for_all():
    db = SessionLocal()
    try:
        records = db.query(CallRecord).all()
        if not records:
            print("No call records to embed.")
            return
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
        print(f"✅ Embeddings generated for {len(records)} records using local model.")
    except Exception as e:
        db.rollback()
        print(f"❌ Error: {e}")
    finally:
        db.close()