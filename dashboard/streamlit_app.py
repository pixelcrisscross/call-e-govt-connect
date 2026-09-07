import sys
import json
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import streamlit as st
import pyarrow as pa
from app.database import SessionLocal
from app.models import CallRecord, AnalysisResult, Insight
from collections import Counter
import datetime


def display_text(value, default="N/A"):
    if value is None or value == "":
        return default
    if isinstance(value, str):
        return value
    if isinstance(value, (int, float, bool)):
        return str(value)
    return json.dumps(value, ensure_ascii=True, sort_keys=True)


def display_date(value):
    if value is None:
        return datetime.datetime.utcnow().strftime("%Y-%m-%d")
    if hasattr(value, "strftime"):
        return value.strftime("%Y-%m-%d")
    return str(value)[:10]

st.set_page_config(page_title="Municipal Insights Dashboard", layout="wide")
st.title("🏛️ Municipal Incident Intelligence Dashboard")

db = SessionLocal()

# ---- Fetch records ----
records = db.query(CallRecord).order_by(CallRecord.created_at.desc()).all()

if records:
    # Extract simple data (no datetime objects for charts)
    issues = []
    sentiments = []
    dates = []

    for r in records:
        structured = r.structured_result if isinstance(r.structured_result, dict) else {}
        issues.append(display_text(structured.get("issue_type")))
        sentiments.append(display_text(r.sentiment, "unknown"))
        dates.append(display_date(r.created_at))

    date_counts = Counter(dates)

    # Issue counts
    issue_counts = Counter(issues)

    # Sentiment counts
    sentiment_counts = Counter(sentiments)

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("📊 Call Volume Over Time")
        if date_counts:
            sorted_dates = sorted(date_counts.items())
            date_table = pa.Table.from_pydict({
                "date": [date for date, _ in sorted_dates],
                "calls": [int(count) for _, count in sorted_dates],
            })
            st.vega_lite_chart(
                {
                    "$schema": "https://vega.github.io/schema/vega-lite/v5.json",
                    "data": {"values": date_table},
                    "mark": "bar",
                    "encoding": {
                        "x": {"field": "date", "type": "temporal", "title": "Date"},
                        "y": {"field": "calls", "type": "quantitative", "title": "Calls"},
                    },
                },
                use_container_width=True,
            )
        else:
            st.write("No data.")

    with col2:
        st.subheader("📌 Issue Distribution")
        if issue_counts:
            issue_table = pa.Table.from_pydict({
                "issue": list(issue_counts.keys()),
                "calls": [int(count) for count in issue_counts.values()],
            })
            st.vega_lite_chart(
                {
                    "$schema": "https://vega.github.io/schema/vega-lite/v5.json",
                    "data": {"values": issue_table},
                    "mark": "bar",
                    "encoding": {
                        "x": {"field": "issue", "type": "nominal", "title": "Issue"},
                        "y": {"field": "calls", "type": "quantitative", "title": "Calls"},
                    },
                },
                use_container_width=True,
            )
        else:
            st.write("No issues.")

    st.subheader("😊 Sentiment Breakdown")
    if sentiment_counts:
        st.write(sentiment_counts)
    else:
        st.write("No sentiment data.")

    st.subheader("📋 Recent Calls")
    # Create a simple list of dicts for the table
    recent = []
    for rec in records[:10]:
        structured = rec.structured_result if isinstance(rec.structured_result, dict) else {}
        recent.append({
            "City": display_text(structured.get("city")),
            "Issue": display_text(structured.get("issue_type")),
            "Severity": display_text(structured.get("severity")),
            "Sentiment": display_text(rec.sentiment, "unknown"),
            "Summary": display_text(rec.summary, "")
        })
    st.dataframe(pa.Table.from_pydict({
        column: [row[column] for row in recent]
        for column in recent[0]
    }))

else:
    st.info("No call records yet.")

# ---- Clusters ----
analyses = db.query(AnalysisResult).all()
if analyses and any(a.cluster_id is not None for a in analyses):
    st.subheader("📦 Clusters")
    cluster_counts = Counter([a.cluster_id for a in analyses if a.cluster_id is not None])
    if cluster_counts:
        st.write(dict(cluster_counts))
    else:
        st.write("No clusters.")

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