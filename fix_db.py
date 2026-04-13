import sqlite3

def fix_db():
    try:
        conn = sqlite3.connect('database.db')
        # Check if avatar column exists
        cursor = conn.execute("PRAGMA table_info(worker_requests)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'avatar' not in columns:
            print("Adding 'avatar' column to worker_requests table...")
            conn.execute("ALTER TABLE worker_requests ADD COLUMN avatar TEXT")
            conn.commit()
            print("Column added successfully.")
        else:
            print("Column 'avatar' already exists.")
            
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    fix_db()
