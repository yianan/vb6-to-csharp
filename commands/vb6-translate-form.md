---
description: Translate one VB6 .frm file to a React page + the API endpoint(s) it needs.
argument-hint: <path-to-form.frm>
---

Translate the VB6 form at `$ARGUMENTS` into:

1. A React page in `frontend/src/pages/<PageName>.tsx`
2. Any new API endpoint(s) it needs in `backend/Library.Api/Endpoints/<Resource>Endpoints.cs`
3. Any new DbContext entities + migration if the form touches a table that doesn't exist yet

## Steps

1. **Parse** the `.frm` per the `vb6-frm-parser` skill: extract controls, event handlers, and inline SQL.
2. **Map controls** per the `vb6-form-controls` skill (TextBox → `<input>`, MSFlexGrid → `<DataGrid>`, etc.).
3. **Translate SQL** per the `vb6-ado-patterns` skill. Inline `"select * from x where y='" + textbox.Text + "'"` patterns become parameterized LINQ. Multi-statement business logic (e.g. issue book = decrement copies + insert loan row) becomes a service method wrapped in `db.Database.BeginTransactionAsync()`.
4. **Compose the page** per the `vite-react-crud-scaffold` skill. Use the existing `<DataGrid>` and `<Dialog>` shared components if they're already in the frontend.
5. **Update the form-mapping doc** at `docs/form-mapping.md` — add or update the row for this form.
6. **Run the smoke test** (`./scripts/smoke.sh`) if the form's flow is in there.

## Naming

- React page: PascalCase noun, e.g. `BooksPage.tsx`, `ChangePasswordPage.tsx` (singular *form*, plural *resource*).
- API endpoints: `Resource` is the plural noun used in the URL: `/api/books`, `/api/loans`.
- VB6 form names like `entire_book_details1.frm` and `Member_full_details2.frm` are usually just grid views — fold them into the list page of the corresponding resource (`BooksPage`, `MembersPage`) rather than creating a separate route.

## Don't blindly mirror layout

VB6 forms are absolute-positioned and reflect 1990s-era UX. Re-create the *function*, not the pixel layout. Group related fields, use a 2-column form grid, and put grids inside the list page rather than on their own routes.
