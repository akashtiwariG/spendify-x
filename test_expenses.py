#!/usr/bin/env python3
"""
Test script to verify expense tracking functionality
"""
import os
import sys
from datetime import date, timedelta

# Add the current directory to the path so we can import our modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database.db import get_db, init_db, seed_db, get_user_by_email, create_user, get_expenses_by_user, get_expense_by_id_and_user, create_expense, update_expense, delete_expense, get_expense_summary, get_expense_by_category
from werkzeug.security import generate_password_hash

def test_expense_functionality():
    """Test the expense tracking functionality"""
    print("Testing expense tracking functionality...")

    # Initialize database
    with app.app_context():
        init_db()
        seed_db()

    # Get test user
    test_user = get_user_by_email('demo@spendly.com')
    if not test_user:
        # Create test user if demo user doesn't exist
        user_id = create_user('Test User', 'test@example.com', generate_password_hash('testpass123'))
        test_user = get_user_by_id(user_id)
        print(f"Created test user: {test_user['name']} (ID: {test_user['id']})")
    else:
        print(f"Using existing user: {test_user['name']} (ID: {test_user['id']})")

    user_id = test_user['id']

    # Test creating an expense
    today = date.today().isoformat()
    expense_id = create_expense(
        user_id=user_id,
        amount=25.50,
        category='Food',
        date=today,
        description='Lunch at restaurant'
    )
    print(f"Created expense with ID: {expense_id}")

    # Test retrieving the expense
    expense = get_expense_by_id_and_user(expense_id, user_id)
    if expense:
        print(f"Retrieved expense: {expense['description']} - ₹{expense['amount']} ({expense['category']})")
    else:
        print("Failed to retrieve expense")
        return False

    # Test updating the expense
    updated = update_expense(
        expense_id=expense_id,
        user_id=user_id,
        amount=30.00,
        category='Food',
        date=today,
        description='Updated lunch expense'
    )
    if updated:
        print("Expense updated successfully")
    else:
        print("Failed to update expense")
        return False

    # Verify the update
    expense = get_expense_by_id_and_user(expense_id, user_id)
    if expense and expense['amount'] == 30.00:
        print(f"Expense updated to: ₹{expense['amount']}")
    else:
        print("Expense update verification failed")
        return False

    # Test getting expenses by user
    expenses = get_expenses_by_user(user_id)
    print(f"Found {len(expenses)} expenses for user")

    # Test getting expenses with filters
    food_expenses = get_expenses_by_user(user_id, category='Food')
    print(f"Found {len(food_expenses)} food expenses")

    # Test expense summary
    summary = get_expense_summary(user_id)
    print(f"Expense summary: {summary['count']} expenses, total: ₹{summary['total']:.2f}")

    # Test category breakdown
    categories = get_expense_by_category(user_id)
    print(f"Expense categories: {len(categories)} categories")
    for cat in categories:
        print(f"  {cat['category']}: ₹{cat['total']:.2f} ({cat['count']} expenses)")

    # Test deleting the expense
    deleted = delete_expense(expense_id, user_id)
    if deleted:
        print("Expense deleted successfully")
    else:
        print("Failed to delete expense")
        return False

    # Verify deletion
    expense = get_expense_by_id_and_user(expense_id, user_id)
    if expense is None:
        print("Expense deletion verified")
    else:
        print("Expense deletion verification failed")
        return False

    print("All tests passed!")
    return True

if __name__ == "__main__":
    # Import app here to avoid circular imports
    from app import app

    with app.app_context():
        success = test_expense_functionality()
        if success:
            print("\n✅ All expense functionality tests passed!")
            sys.exit(0)
        else:
            print("\n❌ Some tests failed!")
            sys.exit(1)