# Spec: Date Filter for Profile Page

## Overview
This feature adds expense summary and filtering capabilities to the user profile page in Spendly. Users can view their total expenses, average spending, and category breakdowns, with the ability to filter by date range to analyze spending patterns over specific periods. This enhances the profile page from purely account management to include financial insights, providing users with a quick overview of their spending habits directly on their profile.

## Depends on
- Step 4: Profile Page Design (04-profile-page-design.md) - requires the profile page template and structure
- Step 5: Backend Routes for Profile Page (05-backend-routes-profile.md) - requires the existing profile route and update handlers
- The expense tracking functionality (already implemented in the application) - requires the expenses table and related database functions

## Routes
- No new routes (modifies existing GET /profile route to accept query parameters for date filtering)

## Database changes
- No database changes required. Uses existing expenses table and database functions:
  - get_expense_summary() for overall statistics
  - get_expense_by_category() for category breakdown

## Templates
- Modify: templates/profile.html - add expense summary section with date filter form and display of expenses data

## Files to create
- None (all files already exist)

## New dependencies
- No new dependencies. The application already uses:
  - Flask (for handling request arguments)
  - sqlite3 (standard library, used via database/db.py)
  - werkzeug.security (already used for password hashing)

## Rules for implementation
- No SQLAlchemy or ORMs - use parameterized queries only via existing database/db.py functions
- Use CSS variables from static/css/style.css; never hardcode hex values in CSS or templates
- All templates must extend base.html
- Validate date inputs on the server side (ensure valid YYYY-MM-DD format, start_date <= end_date)
- Handle cases where no expenses exist for the selected date range gracefully
- Use Flask's flash messaging system for error messages (e.g., invalid date format)
- On initial load or when no filter is applied, show data for all time (or optionally a default period like last 30 days)
- Ensure the date filter form preserves values when submitting
- Implement proper error handling for invalid date formats
- Maintain existing functionality for name/email/password updates
- Format currency amounts appropriately (consistent with existing application)

## Definition of done
A specific testable checklist. Each item must be something that can be verified by running the app:
1. GET /profile displays the profile page correctly when the user is logged in, showing the user's name, email, and forms to update name, email, and change password
2. GET /profile now includes an expense summary section showing total expenses, average expense, and expense count
3. GET /profile includes a date filter form with start date and end date inputs and a filter button
4. When date filters are applied, the expense summary updates to reflect only expenses within the selected date range
5. When no dates are provided, the expense summary shows all-time data (or a sensible default)
6. Invalid date formats (non-YYYY-MM-DD) show appropriate error messages
7. Start date after end date shows appropriate validation error
8. The expense summary includes a breakdown by category when expenses exist
9. When no expenses exist for the selected period, appropriate "no data" messages are displayed
10. All existing profile functionality (name, email, password updates) continues to work without errors
11. Application runs without errors on http://localhost:5001
12. The date filter form uses GET method and preserves values in the input fields after submission
13. The expense summary uses currency formatting (consistent with existing application)