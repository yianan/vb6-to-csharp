---
description: Plan and execute a full VB6 → C#/TypeScript migration of the current project.
argument-hint: [optional notes about the migration]
---

You are migrating a VB6 codebase in the current working directory to a modern stack: ASP.NET Core (LTS) + EF Core + SQLite for the backend, and Vite + React + TypeScript for the frontend.

You have these skills available; load them as their auto-trigger conditions hit during the migration:

- `vb6-language-mapping` — VB6 ↔ C# syntax/semantics
- `vb6-error-handling` — `On Error Goto` / `Resume Next` / `Err` → `try`/`catch`
- `vb6-data-types` — `Variant`, `Currency`, 1-based arrays, `Option Base`, `Date`
- `vb6-form-controls` — TextBox / MSFlexGrid / MSADODC / DataGrid → React equivalents
- `vb6-ado-patterns` — global `ADODB.Connection`/`Recordset` + inline SQL → DI'd `DbContext` + parameterized LINQ
- `vb6-frm-parser` — `.frm` file format reference
- `dotnet-sqlite-scaffold` — exact ASP.NET Core 10 + EF Core + SQLite + cookie auth recipe
- `vite-react-crud-scaffold` — exact Vite + React + TanStack Query CRUD page recipe
- `mssql-bak-to-sqlite` — restore a SQL Server `.bak` and migrate data into SQLite

The architect agent (`vb6-migration-architect`) will own the planning. You execute the resulting plan.

## Workflow

1. **Inventory.** First run `/vb6-inventory` (or call its logic inline): scan `*.frm`, `*.bas`, `*.cls`, `*.vbp`. For each form, record purpose, control list, event handlers, and any inline SQL queries. Infer the database schema from those queries. Save the result to `docs/vb6-inventory.json` and a human-readable `docs/vb6-inventory.md`.

2. **Architecture interview.** Launch the `vb6-migration-architect` subagent with the inventory as input. The subagent uses `AskUserQuestion` to decide:
   - Frontend framework (React / Vue / Svelte / vanilla TS)
   - Data migration strategy (fresh seed / migrate `.bak` / hybrid)
   - Auth model (single admin / multi-user with roles / no auth)
   - Hosting (local only / deployable / desktop wrapper)

3. **Plan.** The subagent writes a project-specific plan file (mirror the structure used in the seed library-app migration: phases 0–6, target architecture diagram, schema, form-route mapping table, build sequence, verification plan). The plan goes wherever the user is invoking `/plan` — typically `~/.claude/plans/<plan-name>.md`. Call `ExitPlanMode` to surface it for approval.

4. **Execute.** After approval, run phases sequentially:
   - **Phase 0**: verify SDKs (`dotnet --version` ≥ 10, `node --version` ≥ 20). Install with `brew install dotnet` if needed. Capture macOS/Windows/Linux quirks into the project's `docs/migration-notes.md`.
   - **Phase 1**: scaffold backend per `dotnet-sqlite-scaffold`. Define entities + `DbContext` from the inventoried schema, normalizing denormalized VB6 tables. Initial migration. Seed.
   - **Phase 2**: per-resource endpoints. As you translate inline-SQL queries from `.bas`/`.frm`, load `vb6-ado-patterns` and rewrite to LINQ. Wrap multi-statement business logic (issue/return-style flows) in services with explicit transactions.
   - **Phase 3**: scaffold frontend per `vite-react-crud-scaffold`. Wire auth, router, layout, reusable `<DataGrid>` and `<Dialog>` components.
   - **Phase 4**: translate forms one by one. First form is hand-written (validates the pattern); subsequent forms reuse the pattern. Use `vb6-form-controls` to map controls.
   - **Phase 5**: README, form-mapping doc, end-to-end smoke test script.
   - **Phase 6**: feed any new gotchas back into the relevant skill files.

5. **Skill upkeep.** Throughout execution, when you hit a VB6 quirk that's not yet documented (a strange `Option Base 1` index, an `On Error Resume Next` pattern, a default-property gotcha), add a `[skill: <skill-name>]`-tagged note to `docs/migration-notes.md` and update the skill's `SKILL.md` if the pattern is general. **Never** invent a skill from training data without a real example from the codebase you're migrating.

## Arguments

If the user passes notes after the command (`$ARGUMENTS`), incorporate them into your inventory pass and surface them in the architect's interview ("the user mentioned: …").

## Tone

This is a multi-day task. Keep the user in the loop with phase summaries; don't go silent for an hour. After each phase, post a 1-paragraph status and ask whether to proceed or pause for review.
