import sqlite3
import os

DATABASE = '/Users/fusean/code/FYH/chatingAPP/chat.db'

def fix_db():
    print(f"Checking database at {DATABASE}")
    if not os.path.exists(DATABASE):
        print("Database file not found!")
        return

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    try:
        # Check groups table columns
        cursor.execute("PRAGMA table_info(groups)")
        columns = [column[1] for column in cursor.fetchall()]
        print(f"Current columns in groups: {columns}")
        
        if 'avatar_path' not in columns:
            print("Adding avatar_path column...")
            cursor.execute("ALTER TABLE groups ADD COLUMN avatar_path TEXT")
            
        if 'invite_token' not in columns:
            print("Adding invite_token column...")
            cursor.execute("ALTER TABLE groups ADD COLUMN invite_token TEXT")
            
        # Check group_message_reads table
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='group_message_reads'")
        if not cursor.fetchone():
            print("Creating group_message_reads table...")
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS group_message_reads (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    message_id INTEGER NOT NULL,
                    user_name TEXT NOT NULL,
                    read_time TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (message_id) REFERENCES group_messages(id),
                    FOREIGN KEY (user_name) REFERENCES users(s_name)
                )
            ''')
            
        conn.commit()
        print("Database schema update completed successfully.")
        
    except Exception as e:
        print(f"Error updating database: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    fix_db()
