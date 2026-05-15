---
description: Plan and execute a full VB6 → C#/TypeScript migration from a VB6 source repo into a separate target repo.
argument-hint: "[optional notes about the migration]"
---

You are migrating a VB6 codebase to a modern stack: ASP.NET Core (LTS) + EF Core + SQLite for the backend, and Vite + React + TypeScript for the frontend.

Treat the VB6 checkout as read-only source input. Generated migration documentation, backend code, frontend code, scripts, tests, ledgers, and packaging files should go into a separate target repo/workspace unless the user explicitly requests an in-place experiment.

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
- `vb6-parity-auditor` — final parity audit before declaring the migration complete
- `tauri-dotnet-sidecar-packaging` — package the migrated app as a Tauri desktop app with macOS and WSL2 Windows build paths

The architect agent (`vb6-migration-architect`) will own the planning. You execute the resulting plan.

## Workflow

0. **Source/target decision.** Identify the source repo and propose a separate target repo before writing artifacts.

   Sensible defaults:
   - Source repo: the current working directory if it contains the VB6 `.vbp` / `.frm` files.
   - Target repo: sibling directory named `<source-folder>-csharp` or `<source-folder>-migration`.
   - Generated docs: `<target-repo>/docs/`
   - Generated backend: `<target-repo>/backend/`
   - Generated frontend: `<target-repo>/frontend/`
   - Generated scripts: `<target-repo>/scripts/`

   Present these defaults to the user and allow edits before proceeding. If the target path already exists, ask whether to reuse it or choose another target path. Do not suggest cleaning, archiving, or deleting files from the VB6 source repo as the normal fresh-start path.

1. **Inventory.** First run `/vb6-inventory` (or call its logic inline): scan the source repo's `*.frm`, `*.bas`, `*.cls`, `*.ctl`, `*.vbp`, `*.vbg`, data files, resources, and COM/OCX references. For each form, record purpose, control list, event handlers, and any inline SQL queries. Infer the database schema from those queries. Save the result to `<target-repo>/docs/vb6-inventory.json`, `<target-repo>/docs/vb6-inventory.md`, and `<target-repo>/docs/source-application-brief.md`.

2. **Governance documentation.** Before implementation, create `<target-repo>/docs/migration-governance-brief.md` using the orchestrator references. It must include:
   - existing app overview and old-system Mermaid diagrams
   - proposed new-system Mermaid diagrams
   - screen/form-to-route mapping
   - code module/procedure-to-target mapping
   - database/file/query-to-entity/import mapping
   - COM/OCX/resource replacement or deferral mapping
   - semantic hazards and verification plan
   - review gates, ledgers, audit criteria, and repeatability evidence

3. **User review gate.** Do not merely write docs and ask the user to go find them. Present an in-chat review packet before asking for approval:
   - absolute source repo and target repo paths
   - absolute paths to `<target-repo>/docs/source-application-brief.md` and `<target-repo>/docs/migration-governance-brief.md`
   - source-application summary
   - old-system Mermaid diagram(s)
   - new-system Mermaid diagram(s)
   - screen/form mapping table
   - code module/procedure mapping table
   - database/file/query mapping table
   - dependency/risk mapping table
   - open questions and assumptions

   If local file opening is available, offer to open the generated Markdown files in the user's editor or preview app, and do so when asked. If the docs are too long for one response, include the decision-critical sections in-chat and state where the full details are stored.

   Then ask: "Have you reviewed the source application brief and migration governance brief? What questions or corrections do you have, and do you approve proceeding with implementation in the proposed target repo?" Treat questions or corrections as a stop signal: revise the docs, present the changed sections, and ask again. Do not proceed to implementation until they explicitly confirm. Record the approval decision.

4. **Architecture interview.** Launch the `vb6-migration-architect` subagent with the inventory and governance brief as input. The subagent uses `AskUserQuestion` to decide:
   - Frontend framework (React / Vue / Svelte / vanilla TS)
   - Data migration strategy (fresh seed / migrate `.bak` / hybrid)
   - Auth model (single admin / multi-user with roles / no auth)
   - Hosting (local only / deployable / desktop wrapper)

5. **Plan.** The subagent writes a project-specific plan file (mirror the structure used in the seed library-app migration: phases 0–8, old/new diagrams, target architecture diagram, schema, form-route mapping table, code/data/dependency mapping tables, build sequence, verification plan, and parity audit gate). The plan goes wherever the user is invoking `/plan` — typically `~/.claude/plans/<plan-name>.md`. Call `ExitPlanMode` to surface it for approval.

6. **Execute.** After approval, run phases sequentially:
   - **Phase 0**: initialize the target repo if needed, verify SDKs (`dotnet --version` ≥ 10, `node --version` ≥ 20). Install with `brew install dotnet` if needed. Capture macOS/Windows/Linux quirks into the target repo's `docs/migration-notes.md`.
   - **Phase 1**: scaffold backend per `dotnet-sqlite-scaffold`. Define entities + `DbContext` from the inventoried schema, normalizing denormalized VB6 tables. Initial migration. Seed.
   - **Phase 2**: per-resource endpoints. As you translate inline-SQL queries from `.bas`/`.frm`, load `vb6-ado-patterns` and rewrite to LINQ. Wrap multi-statement business logic (issue/return-style flows) in services with explicit transactions.
   - **Phase 3**: scaffold frontend per `vite-react-crud-scaffold`. Wire auth, router, layout, reusable `<DataGrid>` and `<Dialog>` components.
   - **Phase 4**: translate forms one by one. First form is hand-written (validates the pattern); subsequent forms reuse the pattern. Use `vb6-form-controls` to map controls.
   - **Phase 5**: README, form-mapping doc, compatibility ledger, semantic ledger, remaining-work ledger, and end-to-end smoke test script.
   - **Phase 6**: if the user chose desktop wrapper / Tauri, load `tauri-dotnet-sidecar-packaging`; add sidecar packaging scripts, macOS build docs, and WSL2 Windows NSIS build docs.
   - **Phase 7**: load `vb6-parity-auditor`; compare VB6 inventory/source against migrated routes, endpoints, tests, smoke flows, ledgers, and any packaging verification. Fix blocking findings or record explicit accepted deferrals.
   - **Phase 8**: feed any new gotchas back into the relevant skill files.

7. **Completion gate.** Do not call the migration complete until the parity audit verdict is `Complete`, `Complete with accepted deferrals`, or `Blocked` with concrete external blockers.

8. **Skill upkeep.** Throughout execution, when you hit a VB6 quirk that's not yet documented (a strange `Option Base 1` index, an `On Error Resume Next` pattern, a default-property gotcha), add a `[skill: <skill-name>]`-tagged note to the target repo's `docs/migration-notes.md` and update the skill's `SKILL.md` if the pattern is general. **Never** invent a skill from training data without a real example from the codebase you're migrating.

## Arguments

If the user passes notes after the command (`$ARGUMENTS`), incorporate them into your inventory pass and surface them in the architect's interview ("the user mentioned: …").

## Tone

This is a multi-day task. Keep the user in the loop with phase summaries; don't go silent for an hour. After each phase, post a 1-paragraph status and ask whether to proceed or pause for review.
