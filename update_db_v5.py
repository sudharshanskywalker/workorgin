import sqlite3
conn = sqlite3.connect('database.db')
cursor = conn.cursor()

# 1. Add status column to worker_requests if it doesn't exist
try:
    cursor.execute("ALTER TABLE worker_requests ADD COLUMN status TEXT DEFAULT 'pending'")
    print("Added status column to worker_requests")
except sqlite3.OperationalError:
    print("status column already exists in worker_requests")

# 2. Add status column to workers if it doesn't exist (default 'approved')
try:
    cursor.execute("ALTER TABLE workers ADD COLUMN status TEXT DEFAULT 'approved'")
    print("Added status column to workers")
except sqlite3.OperationalError:
    print("status column already exists in workers")

conn.commit()
conn.close()
