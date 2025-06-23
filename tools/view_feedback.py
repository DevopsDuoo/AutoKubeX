# tools/view_feedback.py
import sqlite3

conn = sqlite3.connect("models/feedback.db")
cursor = conn.cursor()

for row in cursor.execute("SELECT id, prompt, rating, timestamp FROM feedback ORDER BY timestamp DESC"):
    print(row)

conn.close()