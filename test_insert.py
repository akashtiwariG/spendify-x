import os
import sqlite3
from werkzeug.security import generate_password_hash
from datetime import datetime

DATABASE = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'spendly.db')

def test_insert():
    print(f"Using database: {DATABASE}")

    # Direct connection (no Flask g object)
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    cursor = conn.cursor()

    # Check current state
    cursor.execute("SELECT COUNT(*) FROM users")
    count = cursor.fetchone()[0]
    print(f"Current user count: {count}")

    # Generate test user data
    name = "Test User"
    email = "test@example.com"
    password_hash = generate_password_hash('password123')
    created_at = datetime.now().isoformat()

    print(f"Attempting to insert: {name}, {email}")

    try:
        cursor.execute('''
            INSERT INTO users (name, email, password_hash, created_at)
            VALUES (?, ?, ?, ?)
        ''', (name, email, password_hash, created_at))

        user_id = cursor.lastrowid
        print(f"Insert successful, user_id: {user_id}")

        conn.commit()
        print("Commit successful")

        # Verify
        cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
        user = cursor.fetchone()
        print(f"Verified insert: {dict(user)}")

    except Exception as e:
        print(f"Error during insert: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    test_insert()