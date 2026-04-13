import sqlite3
conn = sqlite3.connect('database.db')
cursor = conn.cursor()

# 1. Add bio column to worker_requests
try:
    cursor.execute("ALTER TABLE worker_requests ADD COLUMN bio TEXT")
    print("Added bio column to worker_requests")
except sqlite3.OperationalError:
    print("bio column already exists in worker_requests")

# 2. Create portfolio_images table
cursor.execute('''
CREATE TABLE IF NOT EXISTS portfolio_images (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    worker_id INTEGER,
    request_id INTEGER,
    image_path TEXT NOT NULL,
    FOREIGN KEY (worker_id) REFERENCES workers (id),
    FOREIGN KEY (request_id) REFERENCES worker_requests (id)
)
''')
print("Created portfolio_images table")

conn.commit()
conn.close()
