import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import streamlit as st
import pandas as pd
from app.database import SessionLocal
from app.models import CallRecord, AnalysisResult, Insight

st.set_page_config(page_title="Municipal Insights Dashboard", layout="wide")
st.title("🏛️ Municipal Incident Intelligence Dashboard")

db = SessionLocal()

# ---- Call Records ----
records = db.query(CallRecord).all()
if records:
    df = pd.DataFrame([{
        "id": r.id,
        "city": r.structured_result.get("city", "N/A"),
        "issue": r.structured_result.get("issue_type", "N/A"),
        "severity": r.structured_result.get("severity", "N/A"),
        "sentiment": r.sentiment or "unknown",
        "summary": r.summary or "",
        "created": r.created_at
    } for r in records])

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("📊 Call Volume Over Time")
        st.line_chart(df.groupby(pd.to_datetime(df["created"]).dt.date).size())

    with col2:
        st.subheader("📌 Issue Distribution")
        st.bar_chart(df["issue"].value_counts())

    st.subheader("😊 Sentiment Breakdown")
    st.write(df["sentiment"].value_counts())

    st.subheader("📋 Recent Calls")
    st.dataframe(df.sort_values("created", ascending=False).head(10)[["city", "issue", "severity", "sentiment", "summary"]])
else:
    st.info("No call records yet.")

# ---- Clusters ----
analyses = db.query(AnalysisResult).all()
if analyses and any(a.cluster_id is not None for a in analyses):
    st.subheader("📦 Clusters")
    cluster_df = pd.DataFrame([{"call_id": a.call_id, "cluster": a.cluster_id} for a in analyses if a.cluster_id is not None])
    st.write(cluster_df.groupby("cluster").size().reset_index(name="count"))

# ---- Insights ----
insights = db.query(Insight).all()
if insights:
    st.subheader("💡 Actionable Insights")
    for ins in insights:
        with st.expander(f"{ins.title} (Priority: {ins.priority})"):
            st.write(ins.description)
else:
    st.info("No insights generated yet.")

db.close()