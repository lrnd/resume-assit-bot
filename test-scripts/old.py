from openai import OpenAI
import numpy as np
import json

client = OpenAI(api_key="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")
previous_responses = []

# Set up OpenAI API key

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
    global previous_responses
    combined_context = "\n".join([f"- {context}" for context, _ in contexts])
    previous_responses_text = "\n".join(previous_responses)
    prompt = f"""
    Question: {query}
    Context:
    {combined_context}
    Answer the question based on the provided context. Avoid repeating phrases and ensure the response is well-elaborated and unique. Consider previous answers and avoid duplicating them. If asked about how you were made answer that you are a LLM that has been modified by Sean to act as his resume. Avoid elaborating too far from the context given
    Previous Responses:
    {previous_responses_text}
    """
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a helpful assistant for Sean Taylor to answer questions about his resume."},
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

def chatbot(summary_file):
    """Run the chatbot to answer questions about the summarized resume."""
    summary = load_summary(summary_file)
    print("Resume summary loaded successfully.")

    # Embed the summary
    print("Embedding the resume summary...")
    summary_chunks = [f"{key}: {value}" for key, value in summary.items()]
    summary_embeddings = get_embeddings(summary_chunks)
    print("Summary embedding complete.")

    while True:
        query = input("\nEnter your question about the resume (or type 'exit' to quit): ").strip()
        if query.lower() == 'exit':
            print("Goodbye!")
            break

        # Find the most relevant chunks
        top_contexts = find_similar_chunks(query, summary_embeddings, summary_chunks, top_n=3)
        for i, (context, similarity) in enumerate(top_contexts):
            print(f"Context {i+1}: {context} (Similarity: {similarity:.2f})")

        # Generate a detailed response
        detailed_answer = generate_response(query, top_contexts)
        print(f"\nGenerated Answer: {detailed_answer}")

def main():
    """Main function to run the chatbot."""
    summary_file = input("Enter the path to the summarized resume (JSON file): ").strip()
    chatbot(summary_file)

if __name__ == "__main__":
    main()
