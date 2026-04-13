import sqlite3

def update_db():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    
    # Create bookings table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS bookings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        worker_id INTEGER NOT NULL,
        user_id INTEGER NOT NULL,
        timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
        status TEXT DEFAULT 'Pending',
        FOREIGN KEY (worker_id) REFERENCES workers (id),
        FOREIGN KEY (user_id) REFERENCES users (id)
    )
    ''')
    
    # Add aadhaar to workers table if not exists
    try:
        cursor.execute('ALTER TABLE workers ADD COLUMN aadhaar TEXT')
    except sqlite3.OperationalError:
        print("aadhaar column already exists in workers")

    conn.commit()
    conn.close()
    print("Database updated: Bookings table created, Aadhaar added to workers.")

if __name__ == '__main__':
    update_db()
