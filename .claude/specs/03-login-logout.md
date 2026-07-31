# Spec: Login and Logout

## Overview
This step implements user authentication for the Spendly application, completing the authentication system begun in Step 2 (Registration). Users will be able to securely log in with their email and password, and log out of their sessions. This builds upon the existing user registration system and database schema, providing the core authentication functionality needed for personalized expense tracking.

## Depends on
- Step 1: Database setup (users table with email, password_hash fields)
- Step 2: Registration (user registration form, user creation, password hashing)

## Routes
- GET /login - displays login form - public
- POST /login - processes login form submission, authenticates user, creates session - public
- GET /logout - logs out user, clears session, redirects to landing page - logged-in

## Database changes
No database changes required. The existing users table already contains the necessary fields:
- id (INTEGER PRIMARY KEY)
- name (TEXT NOT NULL)
- email (TEXT UNIQUE NOT NULL)
- password_hash (TEXT NOT NULL)
- created_at (TEXT DEFAULT CURRENT_TIMESTAMP)

The existing get_user_by_email() function in database/db.py can be used for authentication.

## Templates
- Create: None (login.html template already exists)
- Modify:
  - templates/login.html: Add form processing logic (already has form structure, needs to handle form submission and display errors)
  - templates/base.html: Add session-based user information to navigation bar (show user name when logged in, show login/register links when not)
  - templates/landing.html: Modify to show personalized content when user is logged in (optional enhancement)

## Files to create
- None (all required templates and database functions already exist)
- Updates needed to existing files:
  - app.py: Add POST handler for /login route, implement /logout route functionality
  - templates/base.html: Add conditional navigation based on login state
  - templates/login.html: Enhance to show validation errors and handle form submission properly

## New dependencies
No new dependencies. The application already uses:
- Flask (for sessions and routing)
- werkzeug.security (for password hashing, already used in registration)

## Rules for implementation
- No SQLAlchemy or ORMs - use parameterized queries only
- Passwords must be hashed with werkzeug.security (already implemented in registration)
- Use Flask sessions for session management (set secret key in app.py)
- Use CSS variables from existing style.css - never hardcode hex values
- All templates must extend base.html
- Implement proper session security:
  - Set session cookie to HTTP-only
  - Set appropriate session timeout
  - Regenerate session ID on login
- Validate form input (email format, password presence)
- Use flash messages for user feedback (success/error messages)
- On successful login, redirect to profile page (or expenses dashboard when implemented)
- On logout, clear session and redirect to landing page
- Handle edge cases: invalid credentials, already logged-in users accessing login page

## Definition of done
A specific testable checklist. Each item must be something that can be verified by running the app:

1. User registration flow still works correctly (register -> login)
2. New user can register at /register.com with email and password, then immediately log in with those credentials
3. Existing user can log in with correct email and password
4. Login fails with appropriate error message for:
   - Non-existent email
   - Incorrect password
   - Missing email or password
5. After successful login, user is redirected to profile page (or equivalent)
6. User's name appears in navigation bar when logged in
7. Login and register links disappear from navigation when logged in
8. Logout button/link appears in navigation when logged in
9. Clicking logout clears the session and redirects to landing page
10. After logout, login and register links reappear in navigation
11. Attempting to access profile page while logged out redirects to login page
12. Passwords are securely hashed in the database (verify using SQLite CLI or database browser)
13. Session cookies are HTTP-only and have appropriate security settings
14. Fixes to existing login.html template to properly display validation errors
15. Application runs without errors on http://localhost:5001
16. All existing functionality (registration, landing page, terms, privacy) continues to work