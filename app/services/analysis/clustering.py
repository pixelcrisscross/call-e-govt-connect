from sklearn.cluster import KMeans
import numpy as np
import json
from app.database import SessionLocal
from app.models import AnalysisResult

def perform_clustering(n_clusters=5):
    db = SessionLocal()
    try:
        analyses = [a for a in db.query(AnalysisResult).all() if a.embedding]
        if len(analyses) < 2:
            print("Not enough data for clustering.")
            return
        cluster_count = min(max(2, n_clusters), len(analyses))
        embeddings = [np.asarray(json.loads(a.embedding), dtype=float) for a in analyses]
        if len({embedding.shape for embedding in embeddings}) != 1:
            raise ValueError("All embeddings must have the same dimensions")
        X = np.vstack(embeddings)
        kmeans = KMeans(n_clusters=cluster_count, random_state=42, n_init=10)
        labels = kmeans.fit_predict(X)
        for analysis, label in zip(analyses, labels):
            analysis.cluster_id = int(label)
        db.commit()
        print(f"Clustering done, {cluster_count} clusters.")
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()