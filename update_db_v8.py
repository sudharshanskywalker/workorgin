import sqlite3
conn = sqlite3.connect('database.db')
cursor = conn.cursor()

# 1. Add user_id to worker_requests
try:
    cursor.execute("ALTER TABLE worker_requests ADD COLUMN user_id INTEGER")
    print("Added user_id column to worker_requests")
except sqlite3.OperationalError:
    print("user_id column already exists in worker_requests")

# 2. Add user_id to workers
try:
    cursor.execute("ALTER TABLE workers ADD COLUMN user_id INTEGER")
    print("Added user_id column to workers")
except sqlite3.OperationalError:
    print("user_id column already exists in workers")

# 3. Add email column to workers if not present (to help link existing data)
try:
    cursor.execute("ALTER TABLE workers ADD COLUMN email TEXT")
    print("Added email column to workers")
except sqlite3.OperationalError:
    print("email column already exists in workers")

conn.commit()
conn.close()
