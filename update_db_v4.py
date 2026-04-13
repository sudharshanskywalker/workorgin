import sqlite3
conn = sqlite3.connect('database.db')
cursor = conn.cursor()
try:
    cursor.execute('ALTER TABLE worker_requests ADD COLUMN cv TEXT')
    print("Added cv column to worker_requests")
except sqlite3.OperationalError:
    print("cv column already exists in worker_requests")
conn.commit()
conn.close()
