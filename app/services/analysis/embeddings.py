import openai
import json
from app.database import SessionLocal
from app.models import CallRecord, AnalysisResult

def get_embedding(text: str) -> list:
    response = openai.Embedding.create(
        input=text,
        model="text-embedding-ada-002"
    )
    return response["data"][0]["embedding"]

def update_embeddings_for_all():
    db = SessionLocal()
    records = db.query(CallRecord).all()
    for rec in records:
        text = f"{rec.transcript} {rec.structured_result.get('issue_type','')}"
        emb = get_embedding(text)
        analysis = db.query(AnalysisResult).filter_by(call_id=rec.id).first()
        if not analysis:
            analysis = AnalysisResult(call_id=rec.id, embedding=json.dumps(emb))
            db.add(analysis)
        else:
            analysis.embedding = json.dumps(emb)
        db.commit()
    db.close()