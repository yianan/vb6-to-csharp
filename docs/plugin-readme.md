# vb6-to-csharp

End-to-end VB6 → C# (ASP.NET Core) + TypeScript (Vite + React) migration toolkit.

## Quick start

In any directory containing a VB6 project (`.vbp`, `.frm`, `.bas`):

```
/vb6-migrate
```

Claude will:
1. Inventory the VB6 source (`docs/vb6-inventory.{json,md}`).
2. Ask 3-5 architecture questions via the `vb6-migration-architect` subagent.
3. Write a phased plan file.
4. After your approval, scaffold backend + frontend and translate forms one by one.

## Smaller commands

- `/vb6-inventory` — just the inventory step. Useful for sizing a migration without committing.
- `/vb6-translate-form <path>` — translate a single `.frm` to a React page + needed API endpoints. Useful for iteratively porting an existing project.

## What's inside

### Slash commands (`commands/`)

- `vb6-migrate.md` — end-to-end orchestrator
- `vb6-inventory.md` — inventory step
- `vb6-translate-form.md` — single-form translation

### Subagent (`agents/`)

- `vb6-migration-architect.md` — turns an inventory into a phased plan via a short interview

### Skills (`skills/`)

Auto-loaded as their trigger conditions hit during a migration:

| Skill | Triggers |
|---|---|
| `vb6-language-mapping` | reading `.frm`/`.bas`/`.cls` |
| `vb6-error-handling` | seeing `On Error Goto`, `Resume Next`, or `Err.` |
| `vb6-data-types` | `Variant`, `Currency`, `ReDim`, `Option Base` |
| `vb6-form-controls` | reading `.frm` files for translation |
| `vb6-ado-patterns` | seeing `ADODB.Connection`, `Recordset`, inline SQL |
| `vb6-frm-parser` | needing to parse `.frm` structure |
| `dotnet-sqlite-scaffold` | scaffolding the backend (Phase 1) |
| `vite-react-crud-scaffold` | scaffolding the frontend (Phase 3) |
| `mssql-bak-to-sqlite` | data migration when user opted in |

## Provenance

Built alongside a real VB6 → modern-stack migration of a library-management app at `/Users/yiannis/Projects/library`. Every skill contains real examples from that migration; the seed app is the smoke-test bed. As you exercise the plugin on new codebases, please update the relevant skill's "examples" section with what you learned and any new gotchas.

## Status

- ✅ Slash commands and agent in place
- ✅ Core skills written (language, error handling, data types, controls, ADO, frm parser)
- ✅ Scaffold skills written (dotnet-sqlite, vite-react)
- ⚠️  `mssql-bak-to-sqlite` skill is documentation only — pattern is correct but not yet run end-to-end
- ⚠️  No automated tests yet; verification is "run /vb6-migrate against the seed library app from a clean directory and check output"

## Next steps

- Run `/vb6-migrate` against another VB6 codebase (anything from VB6 sample/demo apps) to harden the plugin.
- Exercise `mssql-bak-to-sqlite` against a real `.bak`.
- Add a `templates/backend/` and `templates/frontend/` directory with copy-able scaffolds (currently the skills tell Claude what to write; templates would speed it up).
- Consider a `vb6-uml-extractor` skill that produces a Mermaid diagram of the form-to-form navigation graph.
