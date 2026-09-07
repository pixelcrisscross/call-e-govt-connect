import json
import google.generativeai as genai
from app.config import settings
from app.database import SessionLocal
from app.models import CallRecord, AnalysisResult, Insight
from collections import Counter

genai.configure(api_key=settings.GEMINI_API_KEY)
model = genai.GenerativeModel(settings.GEMINI_MODEL)

def generate_insights():
    db = SessionLocal()
    try:
        clusters = {}
        records = db.query(CallRecord).all()
        for rec in records:
            analysis = db.query(AnalysisResult).filter_by(call_id=rec.id).first()
            if not analysis or analysis.cluster_id is None:
                continue
            cid = analysis.cluster_id
            if cid not in clusters:
                clusters[cid] = {"count": 0, "sentiments": [], "issues": []}
            structured = rec.structured_result if isinstance(rec.structured_result, dict) else {}
            clusters[cid]["count"] += 1
            clusters[cid]["sentiments"].append(rec.sentiment or "neutral")
            clusters[cid]["issues"].append(structured.get("issue_type", "unknown"))

        for cid, data in clusters.items():
            sentiment_score = sum(
                1.0 if s == "positive" else 0.5 if s == "neutral" else 0.0
                for s in data["sentiments"]
            ) / len(data["sentiments"]) if data["sentiments"] else 0.5
            top_issue = Counter(data["issues"]).most_common(1)[0][0]
            prompt = f"""
            Cluster {cid} has {data['count']} reports, mostly about '{top_issue}', with average sentiment score {sentiment_score:.2f}.
            Suggest one actionable policy gap or improvement recommendation. Keep it concise.
            """
            response = model.generate_content(prompt)
            suggestion = response.text.strip()
            priority = "high" if sentiment_score < 0.4 else "medium"
            insight = db.query(Insight).filter_by(cluster_id=cid).first()
            if insight is None:
                insight = Insight(cluster_id=cid)
                db.add(insight)
            insight.title = f"Cluster {cid} - {top_issue}"
            insight.description = suggestion
            insight.priority = priority
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()