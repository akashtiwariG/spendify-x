"""
Script to seed a single dummy Indian user into the Spendly database.
Creates a user with:
- Realistic Indian first + last name
- Email derived from name with random 2-3 digit number suffix
- Password: "password123" hashed with werkzeug's generate_password_hash
- Checks if email already exists, regenerates if needed
- Prints id, name, and email of created user
"""
import os
import sqlite3
from werkzeug.security import generate_password_hash
import random
from datetime import datetime

DATABASE = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'spendly.db')

def get_db_connection():
    """Create a direct SQLite connection."""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    # Enable foreign key constraints
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def init_db():
    """Creates all tables using CREATE TABLE IF NOT EXISTS."""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
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
        conn.commit()
    finally:
        conn.close()

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
    init_db()

    # Generate unique user
    max_attempts = 10
    for attempt in range(max_attempts):
        name = generate_indian_name()
        email = generate_email_from_name(name)

        # Check if email already exists
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM users WHERE email = ?", (email,))
            existing = cursor.fetchone()

            if not existing:
                # Email is unique, create the user
                password_hash = generate_password_hash('password123')
                created_at = datetime.now().isoformat()

                cursor.execute('''
                    INSERT INTO users (name, email, password_hash, created_at)
                    VALUES (?, ?, ?, ?)
                ''', (name, email, password_hash, created_at))

                user_id = cursor.lastrowid
                conn.commit()

                # Print the required information
                print(f"id: {user_id}")
                print(f"name: {name}")
                print(f"email: {email}")
                return
            else:
                # Email exists, try again
                continue
        finally:
            conn.close()

    # If we couldn't generate a unique email after max attempts
    raise Exception("Failed to generate unique email after maximum attempts")

if __name__ == "__main__":
    seed_user()