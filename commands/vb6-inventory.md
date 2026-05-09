---
description: Inventory the VB6 project in the current directory; produce docs/vb6-inventory.{json,md}.
---

Scan the current working directory for VB6 source files and produce a structured inventory.

## Files to look for

- `*.vbp` — project file. Tells you startup form, references (look for `Reference=*\\G{…}` for COM types in use), object dependencies (`Object={…}#1.0#0; X.OCX`), form list, modules.
- `*.frm` — form files. See the `vb6-frm-parser` skill for the file format.
- `*.bas` — code modules. Often holds globals like `Public con As New ADODB.Connection`.
- `*.cls` — class modules.
- `*.frx` — binary form resources (icons, embedded images). Note them but you won't translate them directly.
- `*.bak` next to a `database/` directory — likely a SQL Server backup. Note location for the `mssql-bak-to-sqlite` skill if needed later.

## Per-form record

For each `.frm`, capture:

- **name** (file basename minus `.frm`)
- **purpose** (one sentence — infer from form caption + button labels + behavior)
- **controls** — list of control type + name (`TextBox username`, `CommandButton btnLogin`, `MSFlexGrid grdMembers`, …)
- **events** — list of `<Control>_<Event>` handler names you find in the code section
- **sql_queries** — every `rs.Open "select …"` / `con.Execute "insert …"` / similar. Note string-concat injection patterns explicitly; the destination C# code must use parameterized LINQ instead.
- **opens_forms** — which other forms this one shows (`SomeForm.Show` / `Load`)
- **calls_modules** — module functions used (e.g. `connect()` from `library.bas`)

## Schema inference

From the SQL queries across all forms, build a tables-and-columns inventory. Note ambiguous types (VB6 freely casts `Variant`s) — flag them for the architecture interview.

## Output

`docs/vb6-inventory.json`:
```json
{
  "project": { "name": "...", "startup_form": "...", "references": [...], "ocx_objects": [...] },
  "forms": [ { "name": "...", "purpose": "...", "controls": [...], "events": [...], "sql_queries": [...], "opens_forms": [...] } ],
  "modules": [ { "name": "library.bas", "globals": [...], "functions": [...] } ],
  "schema": { "tables": [ { "name": "book1", "columns": [...] } ] },
  "external_dependencies": [ "MSFlexGrid.OCX", "MSDatGrd.ocx", "MSADODC.OCX", "DataReport1.Dsr" ],
  "smells": [ "SQL injection in every query", "plaintext passwords in `login` table", ... ]
}
```

`docs/vb6-inventory.md` — human-readable version of the same content with markdown tables and short prose.

## Tips

- VB6 form code lives below the line `Attribute VB_Name = "FormName"` in the `.frm` file. Above that are control declarations.
- Control declarations look like `Begin VB.TextBox txtUsername … End`. Nested `Begin … End` for child controls.
- VB6 strings are quoted with `"`. Doubled `""` is an escape. Concatenation uses `&` (proper) or `+` (works for strings, brittle for `Variant`).
- An MSFlexGrid populated by code (no `DataSource`) is read-only; an MSADODC bound via `DataSource` is data-bound.

Be thorough but concise. The architect agent reads this and will design the rewrite from it; missing a form means missing a feature.
