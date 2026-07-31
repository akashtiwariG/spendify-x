"""
Debug version of seed user script to see what's happening with database writes.
"""
import os
import sqlite3
from werkzeug.security import generate_password_hash
import random
from datetime import datetime

DATABASE = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'spendly.db')

def get_db_connection():
    """Create a direct SQLite connection (bypassing Flask's g object)."""
    print(f"[DEBUG] Connecting to database: {DATABASE}")
    conn = sqlite3.connect(DATABASE)
    print(f"[DEBUG] Connection established: {id(conn)}")
    conn.row_factory = sqlite3.Row
    # Enable foreign key constraints
    conn.execute("PRAGMA foreign_keys = ON")
    print(f"[DEBUG] Foreign keys enabled")
    return conn

def init_db():
    """Creates all tables using CREATE TABLE IF NOT EXISTS."""
    print(f"[DEBUG] Initializing database")
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        # Check current state before creating tables
        cursor.execute("SELECT COUNT(*) FROM users")
        count_before = cursor.fetchone()[0]
        print(f"[DEBUG] User count before table creation: {count_before}")

        # Create users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        print(f"[DEBUG] Users table ensured")

        # Create expenses table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS expenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                amount REAL NOT NULL,
                category TEXT NOT NULL,
                date TEXT NOT NULL,
                description TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
            )
        ''')
        print(f"[DEBUG] Expenses table ensured")

        # Check state after creating tables
        cursor.execute("SELECT COUNT(*) FROM users")
        count_after = cursor.fetchone()[0]
        print(f"[DEBUG] User count after table creation: {count_after}")

        conn.commit()
        print(f"[DEBUG] Database initialization committed")
    except Exception as e:
        print(f"[DEBUG] Error during initialization: {e}")
        raise
    finally:
        conn.close()
        print(f"[DEBUG] Connection closed after init")

def generate_indian_name():
    """Generate a realistic Indian first and last name."""
    indian_first_names = [
        'Aarav', 'Vivaan', 'Aditya', 'Vihaan', 'Arjun', 'Reyansh', 'Ayaan', 'Krishna',
        'Ishaan', 'Shaurya', 'Atharv', 'Naima', 'Ivra', 'Myra', 'Siya', 'Priya',
        'Ananya', 'Fatima', 'Zoya', 'Aisha', 'Diya', 'Myrah', 'Ira', 'Aashi',
        'Rohan', 'Siddharth', 'Advait', 'Atharva', 'Isaac', 'Zayn', 'Kian', 'Neil',
        'Advik', 'Laksh', 'Dhruv', 'Yuvi', 'Veer', 'Samarth', 'Mitansh', 'Shivansh',
        'Aanya', 'Aarna', 'Aditi', 'Ananya', 'Fatima', 'Zoya', 'Aisha', 'Diya',
        'Myrah', 'Ira', 'Aashi', 'Kiara', 'Navya', 'Prisha', 'Riya', 'Saisha',
        'Shaanvi', 'Shanaya', 'Shravya', 'Siona', 'Tanvi', 'Tara', 'Zara', 'Zoya'
    ]

    indian_last_names = [
        'Patel', 'Sharma', 'Gupta', 'Verma', 'Shah', 'Jain', 'Kumar', 'Singh',
        'Reddy', 'Iyer', 'Agarwal', 'Joshi', 'Mehta', 'Desai', 'Khan', 'Malik',
        'Kaur', 'Kapoor', 'Khanna', 'Malhotra', 'Mishra', 'Pandey', 'Pradhan',
        'Rao', 'Sen', 'Sharma', 'Shukla', 'Singh', 'Sinha', 'Tripathi', 'Varma',
        'Yadav', 'Zaveri', 'Agarwal', 'Agrawal', 'Ahuja', 'Arora', 'Bansal',
        'Bhargava', 'Chabra', 'Chadha', 'Chopra', 'Chugh', 'Dhir', 'Dua',
        'Gandhi', 'Gill', 'Gulati', 'Gupta', 'Jain', 'Kataria', 'Khurana',
        'Kohli', 'Kumar', 'Lamba', 'Madhok', 'Malhotra', 'Madaan', 'Mehra',
        'Miglani', 'Munjal', 'Nagra', 'Pahuja', 'Passi', 'Plaha', 'Saini',
        'Sethi', 'Shergill', 'Sodhi', 'Sood', 'Suri', 'Tandon', 'Taneja',
        'Tandon', 'Tuli', 'Vaid', 'Vohra', 'Wadhwa', 'Walia'
    ]

    first_name = random.choice(indian_first_names)
    last_name = random.choice(indian_last_names)
    return f"{first_name} {last_name}"

def generate_email_from_name(name):
    """Generate email from name with random 2-3 digit number."""
    # Extract first and last name, convert to lowercase, remove spaces
    parts = name.lower().split()
    if len(parts) >= 2:
        first, last = parts[0], parts[-1]
    else:
        # If only one name, use it twice or add a common suffix
        first = parts[0]
        last = "kumar" if first not in ['kumar', 'singh'] else "kumar"

    # Generate random 2-3 digit number
    num = random.randint(10, 999)

    # Common email domains
    domains = ['gmail.com', 'yahoo.com', 'hotmail.com', 'outlook.com']
    domain = random.choice(domains)

    return f"{first}.{last}{num}@{domain}"

def seed_user():
    # Initialize database first (creates tables if they don't exist)
    print("[DEBUG] Starting seed_user function")
    init_db()

    # Generate unique user
    max_attempts = 10
    for attempt in range(max_attempts):
        name = generate_indian_name()
        email = generate_email_from_name(name)
        print(f"[DEBUG] Attempt {attempt+1}: Trying name='{name}', email='{email}'")

        # Check if email already exists
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM users WHERE email = ?", (email,))
            existing = cursor.fetchone()

            if not existing:
                # Email is unique, create the user
                print(f"[DEBUG] Email is unique, proceeding to insert")
                password_hash = generate_password_hash('password123')
                created_at = datetime.now().isoformat()
                print(f"[DEBUG] Password hash generated, created_at={created_at}")

                cursor.execute('''
                    INSERT INTO users (name, email, password_hash, created_at)
                    VALUES (?, ?, ?, ?)
                ''', (name, email, password_hash, created_at))

                user_id = cursor.lastrowid
                print(f"[DEBUG] Insert executed, lastrowid={user_id}")

                # Commit immediately and check
                conn.commit()
                print(f"[DEBUG] Transaction committed")

                # Verify it was written by reading back immediately
                cursor.execute("SELECT id, name, email FROM users WHERE id = ?", (user_id,))
                inserted_user = cursor.fetchone()
                if inserted_user:
                    print(f"[DEBUG] Verified insert: {dict(inserted_user)}")
                else:
                    print(f"[DEBUG] WARNING: Could not verify insert for ID {user_id}")

                print(f"Successfully inserted user with ID {user_id}")

                # Print the required information
                print(f"id: {user_id}")
                print(f"name: {name}")
                print(f"email: {email}")
                return
            else:
                print(f"[DEBUG] Email {email} already exists (ID: {existing[0]}), attempt {attempt+1}")
        except Exception as e:
            print(f"[DEBUG] Error during database operation: {e}")
            raise
        finally:
            conn.close()
            print(f"[DEBUG] Connection closed")

    print("Failed to generate unique email after maximum attempts")

if __name__ == "__main__":
    seed_user()