import sqlite3
from datetime import datetime
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "feedback.db")

def init_feedback_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
      CREATE TABLE IF NOT EXISTS feedback (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        prompt TEXT,
        cluster_snapshot TEXT,
        ai_response TEXT,
        rating INTEGER,
        timestamp TEXT
      )
    """)
    conn.commit()
    conn.close()

def store_feedback(prompt, cluster_snapshot, ai_response, rating):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
      INSERT INTO feedback (prompt, cluster_snapshot, ai_response, rating, timestamp)
      VALUES (?, ?, ?, ?, ?)
    """, (prompt, cluster_snapshot, ai_response, rating, datetime.now().isoformat()))
    conn.commit()
    conn.close()

def get_all_feedback():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT * FROM feedback ORDER BY timestamp DESC")
    rows = c.fetchall()
    conn.close()
    return rows

# Initialize on import
init_feedback_db()
