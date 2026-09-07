import openai
import json
from app.database import SessionLocal
from app.models import CallRecord, AnalysisResult, Insight
from collections import Counter

def generate_insights():
    db = SessionLocal()
    # Aggregate by cluster
    clusters = {}
    records = db.query(CallRecord).all()
    for rec in records:
        analysis = db.query(AnalysisResult).filter_by(call_id=rec.id).first()
        if not analysis or analysis.cluster_id is None:
            continue
        cid = analysis.cluster_id
        if cid not in clusters:
            clusters[cid] = {"count": 0, "sentiments": [], "issues": []}
        clusters[cid]["count"] += 1
        clusters[cid]["sentiments"].append(rec.sentiment or "neutral")
        clusters[cid]["issues"].append(rec.structured_result.get("issue_type", "unknown"))

    insights = []
    for cid, data in clusters.items():
        # Compute sentiment score (positive=1, neutral=0.5, negative=0)
        sentiment_score = sum(
            1.0 if s=="positive" else 0.5 if s=="neutral" else 0.0
            for s in data["sentiments"]
        ) / len(data["sentiments"]) if data["sentiments"] else 0.5
        top_issue = Counter(data["issues"]).most_common(1)[0][0]
        prompt = f"""
        Cluster {cid} has {data['count']} reports, mostly about '{top_issue}', with average sentiment score {sentiment_score:.2f}.
        Suggest one actionable policy gap or improvement recommendation. Keep it concise.
        """
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.5
            )
            suggestion = response.choices[0].message.content.strip()
            priority = "high" if sentiment_score < 0.4 else "medium"
            insight = Insight(
                cluster_id=cid,
                title=f"Cluster {cid} – {top_issue}",
                description=suggestion,
                priority=priority
            )
            db.add(insight)
        except Exception as e:
            print(f"Insight generation failed for cluster {cid}: {e}")
    db.commit()
    db.close()
    return insights