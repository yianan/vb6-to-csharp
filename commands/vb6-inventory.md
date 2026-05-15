---
description: Inventory a VB6 source project; produce vb6-inventory.{json,md} and source-application-brief.md under the selected target repo docs directory.
---

Scan the VB6 source directory for VB6 source files and produce a structured inventory. For the full migration workflow, write inventory output into the separate target repo's `docs/` directory, not into the VB6 source repo.

If no source/target paths are provided, default to:

- Source repo: current working directory if it contains the VB6 `.vbp` / `.frm` files.
- Target repo: sibling directory named `<source-folder>-csharp` or `<source-folder>-migration`.
- Inventory output: `<target-repo>/docs/`.

Show these defaults to the user before writing if the command is part of a governed migration flow.

## Files to look for

- `*.vbp` — project file. Tells you startup form, references (look for `Reference=*\\G{…}` for COM types in use), object dependencies (`Object={…}#1.0#0; X.OCX`), form list, modules.
- `*.frm` — form files. See the `vb6-frm-parser` skill for the file format.
- `*.bas` — code modules. Often holds globals like `Public con As New ADODB.Connection`.
- `*.cls` — class modules.
- `*.ctl`, `*.vbg` — user controls and project groups.
- `*.frx`, `*.res`, images, icons — binary resources. Note them but you won't translate them directly.
- `*.mdb`, `*.accdb`, `*.bak`, `*.db`, `*.sqlite*` — legacy databases or backup/data files. Note location for the data-migration path if needed later.

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

`<target-repo>/docs/vb6-inventory.json`:
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

`<target-repo>/docs/vb6-inventory.md` — human-readable version of the same content with markdown tables and short prose.

`<target-repo>/docs/source-application-brief.md` — reviewable source-application documentation with:

- existing system Mermaid diagrams
- screen/form inventory
- code module inventory
- database/data asset inventory
- external dependency mapping placeholders
- initial risk register
- target mapping placeholders for the migration governance brief

The user must review this source brief and the migration governance brief before implementation begins.

## Tips

- VB6 form code lives below the line `Attribute VB_Name = "FormName"` in the `.frm` file. Above that are control declarations.
- Control declarations look like `Begin VB.TextBox txtUsername … End`. Nested `Begin … End` for child controls.
- VB6 strings are quoted with `"`. Doubled `""` is an escape. Concatenation uses `&` (proper) or `+` (works for strings, brittle for `Variant`).
- An MSFlexGrid populated by code (no `DataSource`) is read-only; an MSADODC bound via `DataSource` is data-bound.

Be thorough but concise. The architect agent reads this and will design the rewrite from it; missing a form means missing a feature.
