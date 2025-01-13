import sqlite3
import datetime

database = 'conversations.db'


def init_db():
    connection = sqlite3.connect(database)
    cursor = connection.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS conversations (
            id INTEGER PRIMARY KEY,
            user_id TEXT,
            question TEXT,
            response TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    connection.commit()
    connection.close()


def get_db():
    return sqlite3.connect(database)


def log_conversation(user_id, question, response):
    connection = get_db()
    cursor = connection.cursor()
    cursor.execute(
        '''
        INSERT INTO conversations (user_id, question, response)
        VALUES (?, ?, ?)
        ''',
        (user_id, question, response)
    )
    connection.commit()
    connection.close()

def get_user_summary(user_id):
    connection = get_db()
    cursor = connection.cursor()
    cursor.execute(
        '''
        SELECT question, response, timestamp
        FROM conversations
        WHERE user_id = ?
        ''',
        (user_id,)
    )
    results = cursor.fetchall()
    connection.close()

    summary = f"Summary for User {user_id}:\n\n"
    for question, response, timestamp in results:
        summary += f"Q: {question}\nA: {response}\nTime: {timestamp}\n\n"
    return summary

def get_todays_queries():
    """Retrieve today's queries from the database."""
    db = get_db()
    print("getting queries")
    cursor = db.cursor()

    # Calculate the start of the day
    start_of_day = datetime.datetime.combine(datetime.date.today(), datetime.time.min)
    cursor.execute(
        '''
        SELECT user_id, question, response, timestamp
        FROM conversations
        WHERE timestamp >= ?
        ''',
        (start_of_day,)
    )
    summary = []
    results = cursor.fetchall()
    for user_id, question, response, timestamp in results:
        summary.append(f"ID: {user_id}\nQ: {question}\nA: {response}\nTime: {timestamp}\n\n")

    return len(summary), summary

