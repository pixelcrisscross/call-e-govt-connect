from sqlalchemy import Column, Integer, String, Float, DateTime, Text, JSON
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class CallRecord(Base):
    __tablename__ = "call_records"
    id = Column(Integer, primary_key=True, index=True)
    calle_call_id = Column(String, unique=True, index=True)
    transcript = Column(Text)
    structured_result = Column(JSON)   # city, location, issue_type, severity
    summary = Column(Text, nullable=True)
    sentiment = Column(String, nullable=True)
    topics = Column(JSON, nullable=True)       # list of strings
    created_at = Column(DateTime, default=datetime.utcnow)

class AnalysisResult(Base):
    __tablename__ = "analysis_results"
    id = Column(Integer, primary_key=True)
    call_id = Column(Integer, index=True)
    embedding = Column(Text)          # store JSON‑encoded list
    cluster_id = Column(Integer, nullable=True)

class Insight(Base):
    __tablename__ = "insights"
    id = Column(Integer, primary_key=True)
    cluster_id = Column(Integer, nullable=True)
    title = Column(String)
    description = Column(Text)
    priority = Column(String)  # high/medium/low
    created_at = Column(DateTime, default=datetime.utcnow)