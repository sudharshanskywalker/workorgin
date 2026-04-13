import sqlite3

def view_database():
    try:
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        
        # Get all table names
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        print("\n=== Database Content ===\n")
        
        for table in tables:
            table_name = table[0]
            if table_name == 'sqlite_sequence':
                continue
                
            print(f"--- Table: {table_name} ---")
            
            # Get column names
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = [col[1] for col in cursor.fetchall()]
            print(f"Columns: {', '.join(columns)}")
            
            # Get data
            cursor.execute(f"SELECT * FROM {table_name}")
            rows = cursor.fetchall()
            
            if not rows:
                print("(No data)")
            else:
                for row in rows:
                    print(row)
            print("\n")
            
        conn.close()
        print("=== End of Database Content ===")
        
    except sqlite3.Error as e:
        print(f"Error accessing database: {e}")

if __name__ == "__main__":
    view_database()
