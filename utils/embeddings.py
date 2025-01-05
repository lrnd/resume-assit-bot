import numpy as np
from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("OPENAI_API_KEY not found in environment variables.")


client = OpenAI(api_key=api_key)

def get_embeddings(texts):
    """Generate embeddings for a list of texts using OpenAI API."""
    response = client.embeddings.create(
        input=texts,
        model="text-embedding-ada-002"
    )
    return [data.embedding for data in response.data]

def find_similar_chunks(query, embeddings, chunks, top_n=3):
    """Find the top N most relevant chunks based on cosine similarity."""
    # Embed the query
    query_embedding = get_embeddings([query])[0]

    # Compute cosine similarity
    embeddings = np.array(embeddings)  # Ensure embeddings are a NumPy array
    similarities = np.dot(embeddings, query_embedding) / (
        np.linalg.norm(embeddings, axis=1) * np.linalg.norm(query_embedding)
    )

    # Get indices of top N most similar chunks
    top_indices = np.argsort(similarities)[-top_n:][::-1]
    return [(chunks[idx], similarities[idx]) for idx in top_indices]
