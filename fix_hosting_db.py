import sqlite3
import os

basedir = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.path.join(basedir, 'database.db')

def fix_db():
    conn = sqlite3.connect(DATABASE)
    cur = conn.cursor()

    print("Checking and fixing database schema...")

    # 1. Create missing tables
    tables = {
        "reviews": """
            CREATE TABLE IF NOT EXISTS reviews (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                worker_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                rating INTEGER NOT NULL,
                comment TEXT,
                timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (worker_id) REFERENCES workers (id),
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        """,
        "portfolio_images": """
            CREATE TABLE IF NOT EXISTS portfolio_images (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                worker_id INTEGER NOT NULL,
                image_path TEXT NOT NULL,
                FOREIGN KEY (worker_id) REFERENCES workers (id)
            )
        """,
        "booking_requests": """
            CREATE TABLE IF NOT EXISTS booking_requests (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                worker_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                status TEXT DEFAULT 'Pending',
                timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (worker_id) REFERENCES workers (id),
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        """
    }

    for table_name, schema in tables.items():
        cur.execute(schema)
        print(f"Verified/Created table: {table_name}")

    # 2. Add missing columns to existing tables
    # Workers table
    cur.execute("PRAGMA table_info(workers)")
    worker_cols = [col[1] for col in cur.fetchall()]
    
    if 'user_id' not in worker_cols:
        cur.execute("ALTER TABLE workers ADD COLUMN user_id INTEGER REFERENCES users(id)")
        print("Added user_id to workers")
    if 'work_hours' not in worker_cols:
        cur.execute("ALTER TABLE workers ADD COLUMN work_hours TEXT")
        print("Added work_hours to workers")
    if 'status' not in worker_cols:
        cur.execute("ALTER TABLE workers ADD COLUMN status TEXT DEFAULT 'approved'")
        print("Added status to workers")

    # Users table
    cur.execute("PRAGMA table_info(users)")
    user_cols = [col[1] for col in cur.fetchall()]
    if 'phone' not in user_cols:
        cur.execute("ALTER TABLE users ADD COLUMN phone TEXT")
        print("Added phone to users")

    # Worker requests table
    cur.execute("PRAGMA table_info(worker_requests)")
    req_cols = [col[1] for col in cur.fetchall()]
    if 'bio' not in req_cols:
        cur.execute("ALTER TABLE worker_requests ADD COLUMN bio TEXT")
        print("Added bio to worker_requests")

    conn.commit()
    conn.close()
    print("Database fix completed successfully!")

if __name__ == "__main__":
    fix_db()
