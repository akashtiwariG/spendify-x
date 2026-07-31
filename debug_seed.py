import os
import sqlite3
from werkzeug.security import generate_password_hash
import random
from datetime import datetime

# Get the absolute path to the database
BASE_DIR = os.path.dirname(os.path.abspath('.'))
DATABASE = os.path.join(BASE_DIR, 'spendly.db')
print(f"Script directory: {os.path.dirname(os.path.abspath(__file__))}")
print(f"Base directory: {BASE_DIR}")
print(f"Database path: {DATABASE}")
print(f"Database exists: {os.path.exists(DATABASE)}")
print(f"Database absolute path: {os.path.abspath(DATABASE)}")

# Connect and see what's there
conn = sqlite3.connect(DATABASE)
conn.row_factory = sqlite3.Row
c = conn.cursor()
c.execute('SELECT COUNT(*) FROM users')
count = c.fetchone()[0]
print(f"Current user count in {DATABASE}: {count}")
c.execute('SELECT id, name, email FROM users')
rows = c.fetchall()
for row in rows:
    print(f"  {dict(row)}")
conn.close()

# Now try to insert
print("\nAttempting to insert...")
conn = sqlite3.connect(DATABASE)
conn.row_factory = sqlite3.Row
c = conn.cursor()
name = "Debug User"
email = "debug@example.com"
password_hash = generate_password_hash('password123')
created_at = datetime.now().isoformat()
print(f"Inserting: {name}, {email}")
try:
    c.execute('INSERT INTO users (name, email, password_hash, created_at) VALUES (?, ?, ?, ?)',
              (name, email, password_hash, created_at))
    user_id = c.lastrowid
    print(f"Insert executed, lastrowid: {user_id}")
    conn.commit()
    print("Committed")
except Exception as e:
    print(f"Error: {e}")

# Check again
c.execute('SELECT COUNT(*) FROM users')
count = c.fetchone()[0]
print(f"User count after insert: {count}")
conn.close()