# Spec: Add Expense

## Overview
This feature lets authenticated users record a new expense in Spendly by submitting a form with the amount, category, date, and an optional description. It is the entry point for all spending data in the application — every other expense-related feature (list, edit, delete, summary, analytics) depends on data that this step introduces. The route, template, and database function for adding an expense are the first CRUD operations on the `expenses` table and form the foundation of the user's personal financial history.

## Depends on
- Step 1: Database Setup (01-database-setup.md) — requires the `expenses` table schema and the `init_db()` initialiser
- Step 2: Registration (02-registration.md) — requires the `users` table so expenses can be linked via `user_id`
- Step 3: Login and Logout (03-login-logout.md) — requires session handling so the route can identify the current user
- An authenticated session — the `/expenses/add` route uses `@login_required`

## Routes
- `GET /expenses/add` — show the "Add Expense" form — logged-in
- `POST /expenses/add` — validate the form, persist a new expense for the logged-in user, redirect to the expense list on success — logged-in

## Database changes
- No new tables, columns, or constraints. Uses the existing `expenses` table (`id`, `user_id`, `amount`, `category`, `date`, `description`, `created_at`) and the existing `create_expense(user_id, amount, category, date, description)` function in `database/db.py`.

## Templates
- Create: `templates/expenses/add.html` — the form page with amount, category, date, and description fields. A small inline script pre-fills the date input with today's date.
- Modify: `templates/expenses/index.html` — already includes an "Add Expense" link/button that points to the new route. No further change strictly required, but verify the link is present.

## Files to create
- `templates/expenses/add.html` — the form template
- (No new Python files — the route and DB function already exist in `app.py` and `database/db.py`)

## New dependencies
- No new dependencies. Uses Flask, sqlite3, and `werkzeug.security` (already in `requirements.txt`).

## Rules for implementation
- No SQLAlchemy or ORMs — use the existing `create_expense()` function in `database/db.py` with parameterised queries
- Passwords (where touched) are hashed with `werkzeug.security` — n/a for this step
- Use CSS variables from `static/css/style.css`; never hardcode hex values in CSS or templates
- All templates must `{% extends "base.html" %}`
- The route must be wrapped in `@login_required` and rely on `session['user_id']` to scope writes to the current user — never trust a `user_id` from the form
- Server-side validation: `amount` is required and must be a positive number (`> 0`); `category` is required; `date` is required and must be in `YYYY-MM-DD` format
- On validation failure, re-render the form with a flashed error message; do not redirect
- On success, flash a success message and redirect to `expenses_index` (`/expenses`)
- Use the predefined category list: Food, Transport, Bills, Health, Entertainment, Shopping, Other
- The `description` field is optional; persist an empty string or `NULL` if omitted
- Sanitise/format the amount with `float()`; reject non-numeric or non-positive input
- No new SQL — go through `database/db.py` only

## Definition of done
1. `GET /expenses/add` returns 200 and renders the form when the user is logged in
2. `GET /expenses/add` redirects to `/login` when the user is not logged in
3. `POST /expenses/add` with a valid form (positive amount, selected category, YYYY-MM-DD date) creates a new row in the `expenses` table scoped to `session['user_id']` and redirects to `/expenses`
4. After a successful add, the new expense appears in the expenses list on `/expenses`
5. `POST /expenses/add` with a missing `amount`, `category`, or `date` re-renders the form and flashes an error
6. `POST /expenses/add` with a non-numeric or non-positive `amount` re-renders the form and flashes "Amount must be a positive number."
7. `POST /expenses/add` with a date that is not a valid calendar date or not in `YYYY-MM-DD` format re-renders the form and flashes a date error
8. After a failed validation, the form is re-rendered (not redirected) so the user can correct the input
9. Submitting without being logged in redirects to `/login` (handled by `@login_required`)
10. The new expense is linked to the logged-in user only — `user_id` is read from the session, never from the form
11. The category `<select>` only offers the seven allowed categories: Food, Transport, Bills, Health, Entertainment, Shopping, Other
12. The date input is pre-filled with today's date on page load
13. The form uses POST and points its action at `url_for('add_expense')`
14. `templates/expenses/add.html` extends `base.html`
15. The application starts and runs without errors on http://localhost:5001
