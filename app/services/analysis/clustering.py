from sklearn.cluster import KMeans
import numpy as np
import json
from app.database import SessionLocal
from app.models import AnalysisResult

def perform_clustering(n_clusters=5):
    db = SessionLocal()
    analyses = db.query(AnalysisResult).all()
    if len(analyses) < n_clusters:
        print("Not enough data for clustering.")
        db.close()
        return
    embeddings = [np.array(json.loads(a.embedding)) for a in analyses]
    X = np.vstack(embeddings)
    kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    labels = kmeans.fit_predict(X)
    for analysis, label in zip(analyses, labels):
        analysis.cluster_id = int(label)
    db.commit()
    db.close()
    print(f"Clustering done, {n_clusters} clusters.")