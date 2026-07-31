import sqlite3
import os

DATABASE = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'spendly.db')

def check_user_exists(user_id):
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, email FROM users WHERE id = ?", (user_id,))
    user = cursor.fetchone()
    conn.close()
    return user

if __name__ == "__main__":
    user_id = 2
    user = check_user_exists(user_id)
    if user:
        print(f"User found: {user['id']} - {user['name']} ({user['email']})")
    else:
        print(f"No user found with id {user_id}")