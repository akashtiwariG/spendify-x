# Spec: Registration

## Overview
The registration feature allows new users to create an account by providing their name, email, and password. This is the first step in user authentication, enabling users to save their expenses and access personalized features in subsequent steps of the Spendly application.

## Depends on
Step 1: Database setup (01-database-setup.md) - requires the users table to store user credentials.

## Routes
- POST /register - handles user registration form submission - public (accessible without login)

## Database changes
No database changes. The users table was created in step 1 with appropriate columns (id, name, email, password_hash, created_at) and constraints (unique email). Registration will insert new users into this existing table.

## Templates
- Modify: templates/register.html - enhance error display to show validation errors (e.g., email already exists, password mismatch) passed from the view.

## Files to create
None

## New dependencies
No new dependencies. The application already uses `werkzeug.security` for password hashing (imported in database/db.py).

## Rules for implementation
- No SQLAlchemy or ORMs - use raw SQLite3 queries via the existing database/db.py module.
- Use parameterized queries only; never use string formatting in SQL.
- Passwords must be hashed using `werkzeug.security.generate_password_hash`.
- Use CSS variables from styles.css; never hardcode hex values in CSS.
- All templates must extend base.html.
- Validate input on the server side (email format, password strength, etc.).
- Prevent duplicate email registration by checking for existing email before insertion.
- Provide clear error messages to the user via the template.

## Definition of done
- [ ] GET /register displays the registration form correctly.
- [ ] POST /register validates input (name, email, password) and shows appropriate error messages for invalid input.
- [ ] POST /register creates a new user with a hashed password when email is unique and input is valid.
- [ ] After successful registration, the user is redirected to the login page (or shown a success message).
- [ ] Attempting to register with an existing email shows an error message.
- [ ] Password is stored as a hash in the database, not plain text.
- [ ] Application starts without errors and the registration feature works as expected.