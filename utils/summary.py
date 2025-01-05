import json
from utils.embeddings import get_embeddings

def load_summary(summary_file):
    """Load the summarized resume from a JSON file."""
    with open(summary_file, "r") as f:
        return json.load(f)

def initialise_summary():
    """Load summary and generate embeddings."""
    summary_file_path = "summary.json"
    summary = load_summary(summary_file_path)
    summary_chunks = [f"{key}: {value}" for key, value in summary.items()]
    summary_embeddings = get_embeddings(summary_chunks)
    return summary, summary_chunks, summary_embeddings
