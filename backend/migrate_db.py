import sqlite3
import os
import sys

# Add parent directory to path to allow imports from app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import engine, Base, SQLALCHEMY_DATABASE_URL
from app.models import node, task  # Import models to register them

# Extract path from SQLALCHEMY_DATABASE_URL for raw sqlite3 connection
# Assumes format "sqlite:///./filename" or "sqlite:///absolute/path"
if SQLALCHEMY_DATABASE_URL.startswith("sqlite:///"):
    db_path = SQLALCHEMY_DATABASE_URL.replace("sqlite:///", "")
    if db_path.startswith("."):
        # Resolve relative path relative to this script or CWD? 
        # app/database.py uses ./sql_app.db which implies CWD where python is run.
        # usually backend root.
        DB_FILE = os.path.abspath(db_path)
    else:
        DB_FILE = db_path
else:
    # Fallback/Default if not sqlite
    DB_FILE = os.path.join(os.path.dirname(__file__), "sql_app.db")

def migrate():
    # If DB file doesn't exist, create it with all tables
    if not os.path.exists(DB_FILE):
        print(f"{DB_FILE} not found. Creating new database...")
        Base.metadata.create_all(bind=engine)
        print("Database created successfully.")
        return

    # If DB exists, check for schema updates
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    try:
        cursor.execute("PRAGMA table_info(nodes)")
        columns = [info[1] for info in cursor.fetchall()]

        cursor.execute("PRAGMA table_info(tasks)")
        task_columns = [info[1] for info in cursor.fetchall()]

        if "is_enabled" not in task_columns:
            print("Adding 'is_enabled' column to 'tasks' table...")
            cursor.execute("ALTER TABLE tasks ADD COLUMN is_enabled INTEGER DEFAULT 1")
            conn.commit()
            print("Added 'is_enabled' column.")            
    except Exception as e:
        print(f"Migration failed: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    migrate()
