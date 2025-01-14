import os
import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from dotenv import load_dotenv
from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash, send_file
from utils.embeddings import find_similar_chunks
from utils.responses import generate_response
from utils.summary import initialise_summary
from utils.user_db import init_db, log_conversation, get_user_summary, get_todays_queries
from utils.email import send_email

load_dotenv(override=True)

PASSWD = os.getenv("ACCESS_PASSWD", "securepassword")  # Set this in your .env file
ADMIN_PASSWD = os.getenv("ADMIN_PASSWD", "securepassword")  # Set this in your .env file

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "default-secret-key")  # Ensure this is set securely

init_db()

# initialise summary and embeddings
summary, summary_chunks, summary_embeddings = initialise_summary()

# wrap to check for admin
def admin_required(f):
    def wrap(*args, **kwargs):
        if not session.get('is_admin'):
            flash("You must be logged in as an admin to access this page.", "danger")
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    wrap.__name__ = f.__name__  # Preserve function name for Flask
    return wrap

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

    if password == PASSWD:
        session['authenticated'] = True
        return redirect(url_for('home'))
    elif password == ADMIN_PASSWD:
        session['authenticated'] = True
        session['is_admin'] = True
        return redirect(url_for('admin_dash'))
    else:
        return render_template('login.html', error="Invalid password")


@app.route('/logout', methods=['GET'])
def logout():
    if 'authenticated' in session:
        session.pop('authenticated')
    return redirect(url_for('login'))


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

    user_id = request.remote_addr
    data = request.get_json()
    query = data.get("query", "").strip()
    if not query:
        return jsonify({"error": "No query provided."}), 400
    # Find the most relevant chunks
    top_contexts = find_similar_chunks(query, summary_embeddings, summary_chunks, top_n=3)
    response = generate_response(query, top_contexts)

    log_conversation(user_id, query, response)

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

    subject = "Bug Report from ChatterBox"
    body = f"A bug report has been submitted:\n\n{description}"
    if send_email(subject, body):
        return jsonify({"message": "Bug report submitted successfully"}), 200
    else:
        return jsonify({"error": "Failed to send the bug report"}), 500

def send_update_email():
    """Send an update email with today's queries."""
    query_count, query_list = get_todays_queries()

    if query_count > 0:
        subject = f"Daily Update - {datetime.datetime.now().strftime('%Y-%m-%d')}"
        body = f"You had {query_count} new queries today:\n\n{query_list}"
        send_email(subject, body)


@app.route('/admin/dash')
@admin_required
def admin_dash():
    return render_template('admin_dash.html')


@app.route('/admin/logout')
def admin_logout():
    """Log out the admin and clear the session."""
    session.pop('is_admin', None)
    flash("Logged out successfully.", "success")
    return redirect(url_for('login'))


@app.route('/admin/download_db', methods=['GET'])
@admin_required
def download_db():
    """Download the database snapshot (protected route)."""
    try:
        return send_file('conversations.db', as_attachment=True)
    except FileNotFoundError:
        flash("Database file not found.", "danger")
        return redirect(url_for('admin_dash'))


@app.route('/admin/upload_resume', methods=['POST'])
@admin_required
def upload_resume():
    """Upload a new resume (protected route)."""
    if 'file' not in request.files:
        flash('No file part.', 'danger')
        return redirect(url_for('admin_dash'))
    file = request.files['file']
    if file.filename == '':
        flash('No selected file.', 'danger')
        return redirect(url_for('admin_dash'))
    if file and file.filename.endswith('.pdf'):
        try:
            file.save('static/resume.pdf')
            flash('Resume uploaded successfully.', 'success')
        except Exception as e:
            flash(f"Error uploading file: {e}", 'danger')
    else:
        flash('Invalid file type. Please upload a PDF.', 'danger')
    return redirect(url_for('admin_dash'))


if __name__ == "__main__":
    scheduler = BackgroundScheduler()
    scheduler.add_job(func=send_update_email, trigger='cron', hour=23, minute=59)
    scheduler.start()
    app.run(debug=True, host="0.0.0.0", port=5000)
