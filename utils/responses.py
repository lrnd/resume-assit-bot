from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("OPENAI_API_KEY not found in environment variables.")

client = OpenAI(api_key=api_key)
previous_responses = []
model = "gpt-4o-mini"

def generate_response(query, contexts):
    """Generate a detailed response using GPT with multiple relevant contexts."""

    restricted_keywords = ["image", "picture", "photo", "diagram", "sound", "video", "music", "audio"]
    if any(keyword in query.lower() for keyword in restricted_keywords):
        return "I am designed to answer text-based questions only. Requests for images, sounds, or other non-text outputs are not supported."

    global previous_responses
    combined_context = "\n".join([f"- {context}" for context, _ in contexts])
    #print(combined_context)
    previous_responses_text = "\n".join(previous_responses)
    prompt = f"""
    Question: {query}
    Context:
    {combined_context}
    Answer the question based on the provided context. Avoid repeating phrases and ensure the response is well-elaborated and unique. Consider previous answers and avoid duplicating them. Keep the responses concise and not too long.
    Previous Responses:
    {previous_responses_text}
    """
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "You are a helpful assistant. Your name is ChatterBox. You will answer questions for me about my Resume, my name is Sean"},
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
