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

The architect agent (`vb6-migration-architect`) supports planning, but this command owns the gate sequence. Do not let the architect or scaffolding steps skip user approvals.

## Workflow

0. **Gate 0: source and target approval.** Identify the source repo and propose a separate target repo before writing artifacts.

   Sensible defaults:
   - Source repo: the current working directory if it contains the VB6 `.vbp` / `.frm` files.
   - Target repo: sibling directory named `<source-folder>-csharp` or `<source-folder>-migration`.
   - Generated docs: `<target-repo>/docs/`
   - Generated backend: `<target-repo>/backend/`
   - Generated frontend: `<target-repo>/frontend/`
   - Generated scripts: `<target-repo>/scripts/`

   Present these defaults to the user and allow edits before proceeding. Offer these choices: use proposed target repo, choose another target path, use an existing empty target repo, or stop. If the target path already exists, ask whether to reuse it or choose another target path. Do not create the target repo or generated folders until the user approves. Do not suggest cleaning, archiving, or deleting files from the VB6 source repo as the normal fresh-start path.

1. **Gate 1: inventory approval.** Run inventory only after Gate 0 approval: scan the source repo's `*.frm`, `*.bas`, `*.cls`, `*.ctl`, `*.vbp`, `*.vbg`, data files, resources, and COM/OCX references. Save the result to `<target-repo>/docs/vb6-inventory.json`, `<target-repo>/docs/vb6-inventory.md`, and `<target-repo>/docs/source-application-brief.md`.

   Present an in-chat inventory review packet with the detected app name, startup form, form/module/data/dependency counts, major risks, old-system diagram, and uncertainty list. Ask whether the source understanding is accurate. If the user corrects it, update the source brief/inventory notes before proceeding.

2. **Gate 2: migration options approval.** Present a decision worksheet before writing the migration plan. Include recommendations, alternatives, rationale, risks, and output impact for:
   - Backend: ASP.NET Core + EF Core; MVC; minimal API; service split
   - Frontend: React + TypeScript; Vue; Svelte; Razor Pages; Blazor
   - Database: SQLite; SQL Server; Postgres; Access import path
   - Data strategy: fresh seed; migrate `.bak`; hybrid; defer data
   - Auth: single admin; no auth; roles; preserve legacy login
   - UI strategy: web-native workflows; pixel-ish form clone; hybrid
   - Hosting: local dev; deployable web app; desktop wrapper
   - Packaging: none initially; Tauri desktop; Docker; installer
   - Backend tests: xUnit API/service tests; smoke only; integration-heavy
   - Frontend tests: Playwright smoke flows; Vitest component tests; manual only
   - Parity tracking: update per slice; additional final audit depth if requested
   - Build gate: explicit final approval; auto-build after tests

   Write selected choices to `<target-repo>/docs/migration-options.md` and `<target-repo>/docs/decision-log.md`.

3. **Gate 3: governance plan approval.** Before implementation, create `<target-repo>/docs/migration-governance-brief.md`, `<target-repo>/docs/test-plan.md`, and initial ledgers using the orchestrator references. It must include:
   - existing app overview and old-system Mermaid diagrams
   - proposed new-system Mermaid diagrams
   - screen/form-to-route mapping
   - code module/procedure-to-target mapping
   - database/file/query-to-entity/import mapping
   - COM/OCX/resource replacement or deferral mapping
   - semantic hazards and verification plan
   - selected migration options
   - review gates, ledgers, test plan, audit criteria, and repeatability evidence

   Do not merely write docs and ask the user to go find them. Present an in-chat review packet before asking for approval:
   - absolute source repo and target repo paths
   - absolute paths to `<target-repo>/docs/source-application-brief.md` and `<target-repo>/docs/migration-governance-brief.md`
   - selected options from `<target-repo>/docs/migration-options.md`
   - source-application summary
   - old-system Mermaid diagram(s)
   - new-system Mermaid diagram(s)
   - screen/form mapping table
   - code module/procedure mapping table
   - database/file/query mapping table
   - dependency/risk mapping table
   - open questions and assumptions

   If local file opening is available, offer to open the generated Markdown files in the user's editor or preview app, and do so when asked. If the docs are too long for one response, include the decision-critical sections in-chat and state where the full details are stored.

   Then ask: "Have you reviewed the source application brief, migration options, governance brief, and test plan? What questions or corrections do you have, and do you approve proceeding to implementation planning in the proposed target repo?" Treat questions or corrections as a stop signal: revise the docs, present the changed sections, and ask again. Do not proceed until they explicitly confirm. Record the approval decision.

4. **Gate 4: implementation approval.** Before scaffolding or writing implementation code, show exact folders/files/projects to create, commands to run, the first slice, expected tests, and ledgers to update. Ask for approval to begin implementation.

5. **Gate 5: slice execution and reporting.** After approval, run phases sequentially:
   - **Phase 0**: initialize the target repo if needed, verify SDKs (`dotnet --version` ≥ 10, `node --version` ≥ 20). Install with `brew install dotnet` if needed. Capture macOS/Windows/Linux quirks into the target repo's `docs/migration-notes.md`.
   - **Phase 1**: scaffold backend per `dotnet-sqlite-scaffold`. Define entities + `DbContext` from the inventoried schema, normalizing denormalized VB6 tables. Initial migration. Seed.
   - **Phase 2**: per-resource endpoints. As you translate inline-SQL queries from `.bas`/`.frm`, load `vb6-ado-patterns` and rewrite to LINQ. Wrap multi-statement business logic (issue/return-style flows) in services with explicit transactions.
   - **Phase 3**: scaffold frontend per `vite-react-crud-scaffold`. Wire auth, router, layout, reusable `<DataGrid>` and `<Dialog>` components.
   - **Phase 4**: translate forms one by one. First form is hand-written (validates the pattern); subsequent forms reuse the pattern. Use `vb6-form-controls` to map controls.
   - **Phase 5**: README, form-mapping doc, compatibility ledger, semantic ledger, remaining-work ledger, and end-to-end smoke test script.
   - **Phase 6**: if the user chose desktop wrapper / Tauri, load `tauri-dotnet-sidecar-packaging`; add sidecar packaging scripts, macOS build docs, and WSL2 Windows NSIS build docs.
   - **Phase 7**: load `vb6-parity-auditor`; compare VB6 inventory/source against migrated routes, endpoints, tests, smoke flows, ledgers, and any packaging verification. Fix blocking findings or record explicit accepted deferrals.
   - **Phase 8**: feed any new gotchas back into the relevant skill files.

   After every slice, update `<target-repo>/docs/compatibility-ledger.md`, `<target-repo>/docs/semantic-ledger.md`, `<target-repo>/docs/remaining-work-ledger.md`, `<target-repo>/docs/test-results.md`, `<target-repo>/docs/slice-reports.md`, and the decision log when decisions or deferrals changed. Report source coverage, target files changed, tests added/run, pass/fail summary, parity status changes, open gaps, blockers, deferrals, and user decisions needed.

6. **Gate 6: full test and parity audit.** Run the agreed backend/frontend/build/smoke/data validation tests. Record commands and results in `<target-repo>/docs/test-results.md`. Run `vb6-parity-auditor` and write `<target-repo>/docs/parity-audit-report.md`. Do not continue to final build approval on `Incomplete`.

7. **Gate 7: final product build approval.** Only after tests pass and parity is `Complete`, `Complete with accepted deferrals`, or `Blocked` with concrete external blockers, ask whether to build the final product artifact. Record build commands, environment versions, artifact paths, checksums when practical, and unresolved accepted deferrals in `<target-repo>/docs/final-build-report.md`.

8. **Gate 8: closeout documentation and final acceptance.** After the final build succeeds, update `<target-repo>/docs/migration-closeout.md`, `<target-repo>/README.md`, final reports, ledgers, and decision log. Present a final handoff packet and ask for final acceptance. Record acceptance in `<target-repo>/docs/decision-log.md`.

9. **Continuous user steering.** At any point, if the user changes a decision, adds/removes scope, asks for more tests, rejects a deferral, changes packaging, pauses, resumes, stops, or asks for docs to be regenerated: stop forward motion, record the change in `<target-repo>/docs/decision-log.md`, update impacted docs/code/tests/ledgers, present the impact, and ask for renewed approval when scope, architecture, parity, tests, packaging, or build output changes.

10. **Skill upkeep.** Throughout execution, when you hit a VB6 quirk that's not yet documented (a strange `Option Base 1` index, an `On Error Resume Next` pattern, a default-property gotcha), add a `[skill: <skill-name>]`-tagged note to the target repo's `docs/migration-notes.md` and update the skill's `SKILL.md` if the pattern is general. **Never** invent a skill from training data without a real example from the codebase you're migrating.

## Arguments

If the user passes notes after the command (`$ARGUMENTS`), incorporate them into your inventory pass and surface them in the architect's interview ("the user mentioned: …").

## Tone

This is a multi-day task. Keep the user in the loop with phase summaries; don't go silent for an hour. After each phase, post a 1-paragraph status and ask whether to proceed or pause for review.
