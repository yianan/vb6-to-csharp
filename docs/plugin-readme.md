# vb6-to-csharp

End-to-end VB6 → C# (ASP.NET Core) + TypeScript (Vite + React) migration toolkit.

## Quick start

From, or pointing at, any directory containing a VB6 project (`.vbp`, `.frm`, `.bas`):

```
/vb6-migrate
```

Claude will:
1. Treat the VB6 checkout as read-only source input.
2. Propose a separate target repo such as `<source-folder>-csharp` or `<source-folder>-migration`, and let you edit the defaults.
3. Inventory the VB6 source into `<target-repo>/docs/vb6-inventory.{json,md}` and ask you to approve the source understanding.
4. Present migration options for stack, data, auth, UI strategy, hosting, packaging, tests, parity tracking, and final build behavior.
5. Write and present the governance brief, migration options, test plan, ledgers, and decision log.
6. Ask for implementation approval before scaffolding backend/frontend code.
7. Translate in slices, updating parity ledgers, test results, and slice reports after each slice.
8. Run full tests and the parity auditor before asking for final build approval.
9. Build the final product only after approval, then update closeout docs and ask for final acceptance.

## Smaller commands

- `/vb6-inventory` — just the inventory step. Useful for sizing a migration without committing.
- `/vb6-translate-form <path>` — translate a single `.frm` to a React page + needed API endpoints. Useful for iteratively porting an existing project.
- `/vb6-migrate-data <path-to-backup.bak>` — restore and migrate SQL Server backup data into the migrated SQLite database.
- `/vb6-package-desktop [mac|wsl2-windows|both]` — package a migrated ASP.NET Core + React app as a Tauri desktop app.

## What's inside

### Slash commands (`commands/`)

- `vb6-migrate.md` — end-to-end orchestrator
- `vb6-inventory.md` — inventory step
- `vb6-translate-form.md` — single-form translation
- `vb6-migrate-data.md` — SQL Server `.bak` to SQLite data migration workflow
- `vb6-package-desktop.md` — Tauri desktop packaging for macOS and WSL2 Windows NSIS builds

### Subagent (`agents/`)

- `vb6-migration-architect.md` — turns inventory/options/test choices into a phased plan via a short interview

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
| `tauri-dotnet-sidecar-packaging` | desktop packaging with an ASP.NET Core sidecar, macOS builds, and WSL2 Windows NSIS builds |

## Provenance

Built alongside a real VB6 → modern-stack migration of a library-management app at `/Users/yiannis/Projects/library`. Every skill contains real examples from that migration; the seed app is the smoke-test bed. As you exercise the plugin on new codebases, please update the relevant skill's "examples" section with what you learned and any new gotchas.

## Status

- ✅ Slash commands and agent in place
- ✅ Core skills written (language, error handling, data types, controls, ADO, frm parser)
- ✅ Scaffold skills written (dotnet-sqlite, vite-react)
- ✅ Desktop packaging skill written (Tauri + ASP.NET Core sidecar, macOS, WSL2 Windows)
- ⚠️  `mssql-bak-to-sqlite` skill is documentation only — pattern is correct but not yet run end-to-end
- ⚠️  Plugin self-tests are still light; verification is "run /vb6-migrate against the seed library app from a clean source repo and separate target repo, then check gate behavior and generated evidence"

## Next steps

- Run `/vb6-migrate` against another VB6 codebase (anything from VB6 sample/demo apps) to harden the plugin.
- Exercise `mssql-bak-to-sqlite` against a real `.bak`.
- Add a `templates/backend/` and `templates/frontend/` directory with copy-able scaffolds (currently the skills tell Claude what to write; templates would speed it up).
- Consider a `vb6-uml-extractor` skill that produces a Mermaid diagram of the form-to-form navigation graph.
