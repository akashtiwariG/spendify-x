# Spec: Backend Routes for Profile Page

## Overview
This specification details the backend implementation for the profile management functionality in Spendly. Building upon the authentication system (registration, login/logout) and the profile page design, this spec defines the server-side route handlers that enable users to view and modify their profile information securely. These routes handle GET requests to display the profile and POST requests to update user data (name, email, password) with proper validation, authentication, and error handling.

## Depends on
- Step 1: Database setup (01-database-setup.md) - requires the users table and database functions
- Step 2: Registration (02-registration.md) - requires user registration and password hashing
- Step 3: Login and Logout (03-login-logout.md) - requires authentication system and session management
- Step 4: Profile Page Design (04-profile-page-design.md) - requires the frontend template and navigation

## Routes
- GET /profile - displays the user's profile page - requires login
- POST /profile/update-name - handles form submission to update the user's name - requires login
- POST /profile/update-email - handles form submission to update the user's email - requires login
- POST /profile/change-password - handles form submission to change the user's password - requires login

## Database changes
No database changes required. The existing users table already contains the necessary fields:
- id (INTEGER PRIMARY KEY)
- name (TEXT NOT NULL)
- email (TEXT UNIQUE NOT NULL)
- password_hash (TEXT NOT NULL)
- created_at (TEXT DEFAULT CURRENT_TIMESTAMP)

The following existing database functions will be used:
- get_user_by_id() - to retrieve current user data
- get_user_by_email() - to check email uniqueness during email updates
- update_user_name() - to update user's name
- update_user_email() - to update user's email (with built-in uniqueness check)
- update_user_password() - to update user's password hash

## Templates
- Modify: templates/profile.html - ensure form actions point to correct routes
  - Update name form: action="{{ url_for('update_name') }}" method="POST"
  - Update email form: action="{{ url_for('update_email') }}" method="POST" 
  - Change password form: action="{{ url_for('change_password') }}" method="POST"

## Files to create
- None (all files already exist or will be modified)

## Files to modify
- app.py: Implement route handlers for:
  - GET /profile (lines ~152-159)
  - POST /profile/update-name (lines ~162-174) 
  - POST /profile/update-email (lines ~176-191)
  - POST /profile/change-password (lines ~193-220)
- templates/profile.html: Ensure form actions are correct (if not already)

## New dependencies
No new dependencies. The application already uses:
- Flask (for sessions, routing, decorators)
- werkzeug.security (for password hashing, already used in registration)
- sqlite3 (standard library, already used in database/db.py)
- Flask session management (already configured)

## Rules for implementation
- No SQLAlchemy or ORMs - use parameterized queries only via existing database/db.py functions
- All route handlers must require authentication using the @login_required decorator
- Passwords must be hashed using werkzeug.security.generate_password_hash and checked with werkzeug.security.check_password_hash
- Use CSS variables from static/css/style.css; never hardcode hex values in CSS or templates
- All templates must extend base.html
- Validate input on the server side:
  - Name: not empty after trimming whitespace
  - Email: not empty, valid format, not already taken by another user
  - Password: not empty, minimum length 8 characters, confirmation matches
- Prevent duplicate email registration by checking for existing email before updating a user's email
- Provide clear error messages to the user via Flask's flash messaging system
- Implement proper session security:
  - Regenerate session ID on login (already implemented in login route)
  - Use Flask's built-in session management with appropriate timeout
- On successful profile update, show a success message and refresh the profile view
- On successful password change, show a success message and keep user logged in (or require re-login - either is acceptable for this application)
- Handle edge cases: already logged-in users accessing routes, invalid form submissions, database errors
- Use flash messages for user feedback (success/error messages)
- Redirect appropriately after form submissions (typically back to profile page)
- Ensure database connections are properly managed (handled by existing get_db() and decorator patterns)

## Definition of done
A specific testable checklist. Each item must be something that can be verified by running the app:

1. GET /profile displays the profile page correctly when the user is logged in, showing the user's name, email, and forms to update name, email, and change password
2. GET /profile redirects to the login page when the user is not logged in
3. POST /profile/update-name validates the name input (not empty) and updates the user's name in the database
4. POST /profile/update-email validates the email input (valid format, not empty, not already taken by another user) and updates the user's email in the database
5. POST /profile/change-password validates the current password (correct), new password (not empty, minimum length 8), and confirm new password (matches new password), then updates the password hash in the database
6. After a successful profile update (name or email), the user sees a success message and the updated information is reflected on the profile page
7. After a successful password change, the user sees a success message and can use the new password for subsequent logins
8. Attempting to update email with an already existing email shows an appropriate error message
9. All form submissions display appropriate error messages for invalid input (missing fields, format errors, etc.)
10. The navigation bar in base.html shows a "Profile" link when the user is logged in, and hides it when logged out (from step 4)
11. All existing functionality (registration, login, logout, landing page, terms, privacy) continues to work without errors
12. Application runs without errors on http://localhost:5001
13. Passwords are securely hashed in the database (verify using SQLite CLI or database browser)
14. Session cookies are HTTP-only and have appropriate security settings (from step 3)