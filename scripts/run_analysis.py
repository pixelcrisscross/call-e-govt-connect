import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.services.analysis.embeddings import update_embeddings_for_all
from app.services.analysis.clustering import perform_clustering
from app.services.analysis.insights import generate_insights


if __name__ == "__main__":
    print("Generating embeddings...")
    update_embeddings_for_all()
    print("Clustering incidents...")
    perform_clustering()
    print("Generating actionable insights...")
    generate_insights()
    print("Analysis pipeline complete.")
