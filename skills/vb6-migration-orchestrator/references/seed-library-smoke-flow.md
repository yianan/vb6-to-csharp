# Seed library smoke flow

The worked migration used one script that exercised the complete primary workflow, not isolated health checks:

1. Log in as seeded admin.
2. Confirm `/api/auth/me`.
3. Change password and change it back.
4. Create a book and member.
5. Issue a book and assert available copies decrement.
6. Return the book and assert no fine plus copies restored.
7. Issue another loan, force it overdue in SQLite, preview fine, return with fine.
8. List and pay the fine.
9. Edit and soft-delete the book.
10. Create a librarian.
11. Log out and assert `/api/auth/me` returns 401.

Pattern to reuse: each smoke step should prove one migrated VB6 form or business invariant. Use direct database mutation only to create hard-to-reach states such as overdue loans.
