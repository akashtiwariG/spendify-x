# Spec: Delete Expense

## Overview
This feature lets authenticated users permanently remove one of their own expenses from Spendly. Deletion is the final CRUD operation on the `expenses` table and is the only way users can take a mistake or duplicate row out of their history. It is implemented as a POST-only route guarded by `@login_required`, scoped to the currently logged-in user via `session['user_id']`, and triggered by delete buttons on both the expense list (`templates/expenses/index.html`) and the expense detail page (`templates/expenses/detail.html`). A `confirm()` dialog in the browser protects against accidental clicks, and the database helper enforces ownership at the SQL layer so users can never delete another user's row.

## Depends on
- Step 1: Database Setup (01-database-setup.md) — the `expenses` table with `ON DELETE CASCADE` on `user_id`
- Step 2: Registration (02-registration.md) — the `users` table so expenses can be linked to an owner
- Step 3: Login and Logout (03-login-logout.md) — session handling so the route can identify the current user
- Step 7: Add Expense (07-add-expense.md) — there must be at least one row in `expenses` to delete
- Step 8: Edit Expense (08-edit-expense.md) — the detail page that hosts the delete form

## Routes
- `POST /expenses/<int:id>/delete` — delete the expense whose `id` belongs to `session['user_id']`; redirect to `/expenses` with a flashed success or error message — logged-in
- No `GET` is supported for this route. A `GET` to `/expenses/<id>/delete` must return 405 Method Not Allowed (Flask's default for an unhandled method on a `methods=["POST"]` route).

## Database changes
- No new tables, columns, or constraints. Uses the existing `expenses` table and the existing `delete_expense(expense_id, user_id)` function in `database/db.py` (lines 223-229) which already scopes the `DELETE` by both `id` and `user_id` with parameterised placeholders.

## Templates
- Create: none
- Modify:
  - `templates/expenses/index.html` — ensure each row has a delete form (POST to `url_for('delete_expense', id=expense.id)`) with a `confirm()` `onsubmit` guard. Already present at lines 63-69; verify it renders correctly and is wired to the new route.
  - `templates/expenses/detail.html` — already contains the delete form at lines 11-13. **Pre-existing bug to fix in this step:** the file currently ends with two `{% endblock %}` tags (line 53 duplicates the closer on line 54 in the saved form, and one sits outside any block). Remove the duplicate/unmatched `{% endblock %}` so the template is well-formed.

## Files to create
- None. The route, DB helper, and template delete forms already exist.

## New dependencies
- No new dependencies. Uses Flask, sqlite3, and `werkzeug.security` (all already in `requirements.txt`).

## Rules for implementation
- No SQLAlchemy or ORMs — use the existing `delete_expense()` function in `database/db.py` with parameterised queries
- Passwords (where touched) are hashed with `werkzeug.security` — n/a for this step
- Use CSS variables from `static/css/style.css`; never hardcode hex values in CSS or templates
- All templates must `{% extends "base.html" %}`
- The route must be wrapped in `@login_required` and rely on `session['user_id']` to scope the delete — never accept a `user_id` from the form or query string
- The route must accept **only POST** (declare `methods=["POST"]`). Browsers prefetching or following a link must not be able to delete a row.
- Before deleting, call `get_expense_by_id_and_user(id, session['user_id'])` to verify the expense exists and is owned by the current user. If it does not, flash "Expense not found." (error) and redirect to `/expenses` — do not attempt the delete.
- Use the `delete_expense(id, session['user_id'])` helper. The helper already scopes by both `id` and `user_id` in the WHERE clause, so a mismatched ownership is impossible at the SQL layer.
- On success, flash "Expense deleted successfully." (success) and redirect to `expenses_index` (`/expenses`).
- On failure (helper returns `False`, which should not happen given the pre-check but is defensive), flash "Failed to delete expense." (error) and redirect to `expenses_index`.
- The delete form on every page must use `method="POST"` and `action="{{ url_for('delete_expense', id=expense.id) }}"`.
- Every delete button must use `onsubmit="return confirm('Are you sure you want to delete this expense?');"` (or an equivalent JS confirmation) to prevent accidental deletion.
- Delete actions are exposed in two places only: the expenses list (per-row icon button) and the expense detail page (text "Delete" button). Do not add delete buttons to the profile or analytics pages.
- After deletion, the user is redirected to `/expenses`, **not** to the detail page (which would 404).
- No new SQL — go through `database/db.py` only.
- The flash category for success messages must be `success`; for errors, `error`. The base template already styles `.flash-success` and `.flash-error`.

## Definition of done
1. `POST /expenses/<id>/delete` for an expense owned by the logged-in user returns a 302 redirect to `/expenses` and removes the row from the `expenses` table
2. After a successful delete, a success flash "Expense deleted successfully." is visible on `/expenses`
3. `POST /expenses/<id>/delete` for an expense owned by **another** user returns 302 to `/expenses` and does **not** delete the row; the row is still present
4. `POST /expenses/<id>/delete` for a non-existent `id` returns 302 to `/expenses` and flashes "Expense not found."
5. `GET /expenses/<id>/delete` returns 405 Method Not Allowed (not 200, not 500)
6. Submitting the delete form while not logged in redirects to `/login` (handled by `@login_required`)
7. The expenses list (`/expenses`) shows a delete icon button on every row that posts to `url_for('delete_expense', id=...)`
8. The expense detail page (`/expenses/<id>`) shows a delete button that posts to the same endpoint
9. Both delete buttons trigger a `confirm()` dialog before submitting
10. After a delete, the totals on `/profile` (total, average, count, category breakdown) reflect the removed row
11. After a delete, the new row count is correct on `/expenses` (the deleted row is no longer in the table or any filter result)
12. The route and helper are untouched by any client — `user_id` is read from `session`, never from form input or query params
13. `templates/expenses/detail.html` is well-formed (exactly one `{% endblock %}` per child block, no duplicate or orphaned `{% endblock %}`)
14. `templates/expenses/index.html` and `templates/expenses/detail.html` both extend `base.html`
15. The application starts and runs without errors on http://localhost:5001
