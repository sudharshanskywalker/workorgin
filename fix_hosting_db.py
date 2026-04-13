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
                worker_id INTEGER,
                request_id INTEGER,
                image_path TEXT NOT NULL,
                FOREIGN KEY (worker_id) REFERENCES workers (id),
                FOREIGN KEY (request_id) REFERENCES worker_requests (id)
            )
        """,
        "bookings": """
            CREATE TABLE IF NOT EXISTS bookings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                worker_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                status TEXT DEFAULT 'Pending',
                timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (worker_id) REFERENCES workers (id),
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        """,
        "notifications": """
            CREATE TABLE IF NOT EXISTS notifications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                message TEXT NOT NULL,
                timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
                is_read INTEGER DEFAULT 0,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        """
    }

    for table_name, schema in tables.items():
        cur.execute(schema)
        print(f"Verified/Created table: {table_name}")

    # Ensure portfolio_images has request_id column (for older deployments)
    cur.execute("PRAGMA table_info(portfolio_images)")
    port_cols = [col[1] for col in cur.fetchall()]
    if 'request_id' not in port_cols:
        cur.execute("ALTER TABLE portfolio_images ADD COLUMN request_id INTEGER REFERENCES worker_requests(id)")
        print("Added request_id to portfolio_images")

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
    if 'email' not in worker_cols:
        cur.execute("ALTER TABLE workers ADD COLUMN email TEXT")
        print("Added email to workers")
    if 'skills' not in worker_cols:
        cur.execute("ALTER TABLE workers ADD COLUMN skills TEXT")
        print("Added skills to workers")
    if 'hourly_rate' not in worker_cols:
        cur.execute("ALTER TABLE workers ADD COLUMN hourly_rate INTEGER DEFAULT 0")
        print("Added hourly_rate to workers")
    if 'dob' not in worker_cols:
        cur.execute("ALTER TABLE workers ADD COLUMN dob TEXT")
        print("Added dob to workers")
    if 'age' not in worker_cols:
        cur.execute("ALTER TABLE workers ADD COLUMN age INTEGER")
        print("Added age to workers")
    if 'phone' not in worker_cols:
        cur.execute("ALTER TABLE workers ADD COLUMN phone TEXT")
        print("Added phone to workers")
    if 'aadhaar' not in worker_cols:
        cur.execute("ALTER TABLE workers ADD COLUMN aadhaar TEXT")
        print("Added aadhaar to workers")

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
    if 'dob' not in req_cols:
        cur.execute("ALTER TABLE worker_requests ADD COLUMN dob TEXT")
        print("Added dob to worker_requests")
    if 'age' not in req_cols:
        cur.execute("ALTER TABLE worker_requests ADD COLUMN age INTEGER")
        print("Added age to worker_requests")
    if 'phone' not in req_cols:
        cur.execute("ALTER TABLE worker_requests ADD COLUMN phone TEXT")
        print("Added phone to worker_requests")
    if 'skills' not in req_cols:
        cur.execute("ALTER TABLE worker_requests ADD COLUMN skills TEXT")
        print("Added skills to worker_requests")
    if 'user_id' not in req_cols:
        cur.execute("ALTER TABLE worker_requests ADD COLUMN user_id INTEGER REFERENCES users(id)")
        print("Added user_id to worker_requests")
    if 'status' not in req_cols:
        cur.execute("ALTER TABLE worker_requests ADD COLUMN status TEXT DEFAULT 'pending'")
        print("Added status to worker_requests")
    if 'cv' not in req_cols:
        cur.execute("ALTER TABLE worker_requests ADD COLUMN cv TEXT")
        print("Added cv to worker_requests")

    conn.commit()
    conn.close()
    print("Database fix completed successfully!")

if __name__ == "__main__":
    fix_db()
