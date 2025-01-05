import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from utils.embeddings import find_similar_chunks
from utils.responses import generate_response
from utils.summary import initialise_summary

load_dotenv()

EMAIL_HOST = os.getenv("EMAIL_HOST")
EMAIL_PORT = int(os.getenv("EMAIL_PORT", 587))
EMAIL_USERNAME = os.getenv("EMAIL_USERNAME")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
RECIPIENT_EMAIL = os.getenv("RECIPIENT_EMAIL", EMAIL_USERNAME)

PASSWORD = os.getenv("ACCESS_PASSWORD", "securepassword")  # Set this in your .env file

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "default-secret-key")  # Ensure this is set securely

# initialise summary and embeddings
summary, summary_chunks, summary_embeddings = initialise_summary()

@app.route('/')
def login():
    """Render the login page."""
    if 'authenticated' in session:
        return redirect(url_for('home'))
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def authenticate():
    """Authenticate the user."""
    password = request.form.get("password")
    if password == PASSWORD:
        session['authenticated'] = True
        return redirect(url_for('home'))
    else:
        return render_template('login.html', error="Invalid password")

#@app.route('/logout')
#def logout():
#    """Log the user out."""
#    session.pop('authenticated', None)
#    return redirect(url_for('login'))

@app.route('/home')
def home():
    """Render the chatbot interface."""
    if 'authenticated' not in session:
        return redirect(url_for('login'))
    return render_template('index.html')

@app.route('/ask', methods=['POST'])
def ask_question():
    """Handle the chatbot queries."""

    if 'authenticated' not in session:
        return jsonify({"error": "Unauthorized"}), 401

    data = request.get_json()
    query = data.get("query", "").strip()
    if not query:
        return jsonify({"error": "No query provided."}), 400
    # Find the most relevant chunks
    top_contexts = find_similar_chunks(query, summary_embeddings, summary_chunks, top_n=3)
    response = generate_response(query, top_contexts)
    return jsonify({"response": response})

@app.route('/report-bug', methods=['POST'])
def report_bug():
    """Handle bug report submission and send it via email."""

    if 'authenticated' not in session:
        return jsonify({"error": "Unauthorized"}), 401

    data = request.get_json()
    description = data.get("description", "").strip()

    if not description:
        return jsonify({"error": "Bug description is required"}), 400

    # Construct the email
    subject = "Bug Report from ChatterBox"
    body = f"A bug report has been submitted:\n\n{description}"
    message = MIMEMultipart()
    message["From"] = EMAIL_USERNAME
    message["To"] = RECIPIENT_EMAIL
    message["Subject"] = subject
    message.attach(MIMEText(body, "plain"))

    # Send the email
    try:
        with smtplib.SMTP(EMAIL_HOST, EMAIL_PORT) as server:
            server.starttls()
            server.login(EMAIL_USERNAME, EMAIL_PASSWORD)
            server.sendmail(EMAIL_USERNAME, RECIPIENT_EMAIL, message.as_string())
        return jsonify({"message": "Bug report submitted successfully"}), 200
    except Exception as e:
        print(f"Error sending email: {e}")
        return jsonify({"error": "Failed to send the bug report"}), 500
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
