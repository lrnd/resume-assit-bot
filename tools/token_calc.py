from docx import Document

PRICING_PER_1M_TOKENS = {
    "input": 0.150,  # $0.150 per 1M input tokens
    "output": 0.600  # $0.600 per 1M output tokens
}
OUTPUT_TOKEN_FACTOR = 0.5  # Assume output tokens are 50% of input tokens

def estimate_tokens(text):
    """Estimate the number of tokens in a text based on character count."""
    avg_chars_per_token = 4  # Average characters per token
    return len(text) // avg_chars_per_token

def calculate_cost(input_tokens, output_tokens):
    """Calculate the cost of processing the given number of tokens."""
    input_cost = (input_tokens / 1_000_000) * PRICING_PER_1M_TOKENS["input"]
    output_cost = (output_tokens / 1_000_000) * PRICING_PER_1M_TOKENS["output"]
    return input_cost + output_cost

def parse_and_estimate_tokens_cost(file_path):
    """Parse the Word document and estimate its token count."""
    doc = Document(file_path)
    document_text = "\n".join([para.text.strip() for para in doc.paragraphs if para.text.strip()])
    estimated_tokens = estimate_tokens(document_text)
    cost = calculate_cost(estimated_tokens, estimated_tokens*OUTPUT_TOKEN_FACTOR)
    print(f"Estimated tokens in the document: {estimated_tokens}")
    print(f"Estimated cost USD: {cost}")
    return document_text, estimated_tokens


def main():
    """Main function to process a Word resume and save contexts."""
    file_path = input("Enter the path to the Word document resume: ").strip()
    parse_and_estimate_tokens_cost(file_path)

if __name__ == "__main__":
    main()
