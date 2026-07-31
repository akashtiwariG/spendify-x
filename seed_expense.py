#!/usr/bin/env python3
"""
Seed expenses for a user.
Usage: python seed_expense.py <user_id> <count> <months>
Example: python seed_expense.py 2 5 3
"""

import sys
import sqlite3
import os
import random
from datetime import datetime, timedelta

DATABASE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'spendly.db')

def get_db():
    """Returns a SQLite connection with row_factory and foreign keys enabled."""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    # Enable foreign key constraints
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def user_exists(user_id):
    """Check if a user exists in the database."""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM users WHERE id = ?", (user_id,))
    user = cursor.fetchone()
    conn.close()
    return user is not None

def get_expense_categories():
    """Return list of expense categories as per spec."""
    return ['Food', 'Transport', 'Bills', 'Health', 'Entertainment', 'Shopping', 'Other']

def generate_random_date(months_back):
    """Generate a random date within the last N months."""
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30 * months_back)
    # Generate random date between start_date and end_date
    time_between = end_date - start_date
    days_between = time_between.days
    random_days = random.randrange(days_between)
    random_date = start_date + timedelta(days=random_days)
    return random_date.strftime('%Y-%m-%d')

def generate_expense_description(category):
    """Generate a realistic description based on category."""
    descriptions = {
        'Food': [
            'Lunch at restaurant', 'Groceries from supermarket', 'Coffee and pastry',
            'Dinner with friends', 'Breakfast cafe', 'Snack from vending machine',
            'Food delivery', 'Fruits and vegetables', 'Meat and poultry', 'Bakery items'
        ],
        'Transport': [
            'Taxi ride', 'Bus ticket', 'Metro pass', 'Fuel for car', 'Parking fee',
            'Ride-sharing service', 'Train ticket', 'Auto-rickshaw fare', 'Toll charges', 'Vehicle maintenance'
        ],
        'Bills': [
            'Electricity bill', 'Water bill', 'Internet bill', 'Mobile phone recharge',
            'Gas cylinder', 'DTH recharge', 'Maintenance charge', 'Property tax', 'Insurance premium', 'Subscription service'
        ],
        'Health': [
            'Pharmacy medicines', 'Doctor consultation', 'Medical tests',
            'Health checkup', 'Pharmacy supplies', 'Fitness membership'
        ],
        'Entertainment': [
            'Movie ticket', 'Streaming subscription', 'Concert tickets',
            'Gaming expenses', 'Books and magazines', 'Amusement park'
        ],
        'Shopping': [
            'Clothing purchase', 'Electronics accessories', 'Home supplies',
            'Personal care products', 'Gift purchase', 'Footwear'
        ],
        'Other': [
            'Stationery items', 'Household repairs', 'Donation/charity',
            'Pet care expenses', 'Laundry services', 'Miscellaneous expenses'
        ]
    }

    category_descs = descriptions.get(category, descriptions['Other'])
    return random.choice(category_descs)

def generate_expense_amount(category):
    """Generate a realistic amount based on category."""
    ranges = {
        'Food': (5.0, 50.0),
        'Transport': (10.0, 100.0),
        'Bills': (50.0, 500.0),
        'Health': (10.0, 200.0),
        'Entertainment': (10.0, 100.0),
        'Shopping': (20.0, 500.0),
        'Other': (5.0, 100.0)
    }

    low, high = ranges.get(category, (5.0, 50.0))
    # Generate amount with 2 decimal places
    amount = round(random.uniform(low, high), 2)
    # Make it more realistic by rounding to common values
    if amount < 20:
        amount = round(amount, 1)
    elif amount < 100:
        amount = round(amount / 5) * 5  # Round to nearest 5
    else:
        amount = round(amount / 10) * 10  # Round to nearest 10

    return max(amount, 1.0)  # Ensure minimum amount of 1.0

def seed_expenses(user_id, count, months):
    """Seed expenses for the given user."""
    if not user_exists(user_id):
        print(f"Error: User with ID {user_id} does not exist.")
        return False

    conn = get_db()
    cursor = conn.cursor()

    categories = get_expense_categories()
    expenses_added = 0

    try:
        for i in range(count):
            category = random.choice(categories)
            amount = generate_expense_amount(category)
            description = generate_expense_description(category)
            date = generate_random_date(months)

            cursor.execute('''
                INSERT INTO expenses (user_id, amount, description, date, category)
                VALUES (?, ?, ?, ?, ?)
            ''', (user_id, amount, description, date, category))

            expenses_added += 1
            print(f"Added expense {expenses_added}: {description} - ${amount:.2f} ({category}) on {date}")

        conn.commit()
        print(f"\nSuccessfully added {expenses_added} expenses for user ID {user_id}.")
        return True

    except Exception as e:
        conn.rollback()
        print(f"Error seeding expenses: {e}")
        return False
    finally:
        conn.close()

def main():
    if len(sys.argv) != 4:
        print("Usage: python seed_expense.py <user_id> <count> <months>")
        print("Example: python seed_expense.py 2 5 3")
        sys.exit(1)

    try:
        user_id = int(sys.argv[1])
        count = int(sys.argv[2])
        months = int(sys.argv[3])

        if count <= 0:
            print("Error: Count must be a positive integer.")
            sys.exit(1)

        if months <= 0:
            print("Error: Months must be a positive integer.")
            sys.exit(1)

    except ValueError:
        print("Error: All arguments must be integers.")
        sys.exit(1)

    print(f"Seeding {count} expenses for user ID {user_id} over the past {months} months...")
    success = seed_expenses(user_id, count, months)

    if success:
        print("Seeding completed successfully.")
    else:
        print("Seeding failed.")
        sys.exit(1)

if __name__ == "__main__":
    main()