from openai import OpenAI
import numpy as np
import os
from dotenv import load_dotenv
from flask import Flask, render_template, request
import json

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("OPENAI_API_KEY not found in environment variables.")

# Set up OpenAI Client
client = OpenAI(api_key=api_key)
previous_responses = []

# Flask app setup
app = Flask(__name__)

# Load the resume summary and embeddings
summary_file_path = "test.json"  # Replace with actual path
summary = None
summary_chunks = []
summary_embeddings = []

def load_summary(summary_file):
    """Load the summarized resume from a JSON file."""
    with open(summary_file, "r") as f:
        return json.load(f)

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

def generate_response(query, contexts):
    """Generate a detailed response using GPT with multiple relevant contexts."""

    restricted_keywords = ["image", "picture", "photo", "diagram", "sound", "video", "music", "audio"]
    if any(keyword in query.lower() for keyword in restricted_keywords):
        return "I am designed to answer text-based questions only. Requests for images, sounds, or other non-text outputs are not supported."

    global previous_responses
    combined_context = "\n".join([f"- {context}" for context, _ in contexts])
    previous_responses_text = "\n".join(previous_responses)
    prompt = f"""
    Question: {query}
    Context:
    {combined_context}
    Answer the question based on the provided context. Avoid repeating phrases and ensure the response is well-elaborated and unique. Consider previous answers and avoid duplicating them.
    Previous Responses:
    {previous_responses_text}
    """
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=300,
        temperature=0.7
    )
    answer = response.choices[0].message.content
    previous_responses.append(answer)
    # Limit stored responses to avoid excessive memory usage
    if len(previous_responses) > 10:
        previous_responses.pop(0)
    return answer

@app.route('/')
def home():
    """Render the home page with the Q&A interface."""
    return render_template('index.html')

@app.route('/ask', methods=['POST'])
def ask_question():
    print("handling question")
    """Handle a question from the web interface and return the answer."""
    query = request.form.get("query", "").strip()
    if not query:
        return {"error": "No query provided."}, 400

    # Find the most relevant chunks
    top_contexts = find_similar_chunks(query, summary_embeddings, summary_chunks, top_n=3)
    response = generate_response(query, top_contexts)
    return {"response": response}

def initialize():
    """Load the summary and embeddings during initialization."""
    global summary, summary_chunks, summary_embeddings
    summary = load_summary(summary_file_path)
    summary_chunks = [f"{key}: {value}" for key, value in summary.items()]
    summary_embeddings = get_embeddings(summary_chunks)

if __name__ == "__main__":
    initialize()
    app.run(debug=True, host="0.0.0.0", port=5000)
