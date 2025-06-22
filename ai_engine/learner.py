import sqlite3

def log_incident(pod_name, namespace, issue, timestamp):
    conn = sqlite3.connect("models/history.db")
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS incidents
                 (timestamp TEXT, namespace TEXT, pod_name TEXT, issue TEXT)''')
    c.execute("INSERT INTO incidents VALUES (?, ?, ?, ?)", (timestamp, namespace, pod_name, issue))
    conn.commit()
    conn.close()

def get_recent_issues():
    conn = sqlite3.connect("models/history.db")
    c = conn.cursor()
    c.execute("SELECT * FROM incidents ORDER BY timestamp DESC LIMIT 10")
    rows = c.fetchall()
    conn.close()
    return rows