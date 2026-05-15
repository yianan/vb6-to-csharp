---
name: vb6-migration-orchestrator
description: "Run the end-to-end VB6 to C# migration workflow in Codex: inventory a VB6 app, choose the migration architecture, scaffold backend/frontend, translate forms, verify flows, and feed project-specific gotchas back into the plugin. Use when the user asks to migrate, plan, inventory, or demo a VB6-to-C# migration."
---

# VB6 migration orchestrator

Use this skill as the Codex-visible equivalent of the plugin's Claude slash commands and architect agent.

## Workflow

0. **Separate source from output.** Treat the VB6 checkout as read-only source input. Do not write generated migration artifacts into the VB6 source repo unless the user explicitly asks for an in-place experiment.

   Propose a separate migration workspace/repo before inventory or implementation. Sensible default:
   - Source repo: the directory containing the VB6 `.vbp` / `.frm` files.
   - Target repo: a sibling directory named `<source-folder>-csharp` or `<source-folder>-migration`.
   - Generated docs: `<target-repo>/docs/`
   - Generated backend: `<target-repo>/backend/`
   - Generated frontend: `<target-repo>/frontend/`
   - Generated scripts: `<target-repo>/scripts/`

   Present these paths to the user and allow edits before proceeding. If the target path already exists, ask whether to reuse it or choose another target path. Do not suggest cleaning, archiving, or deleting files from the VB6 source repo as the normal fresh-start path.

1. **Inventory first.** Run the bundled inventory helper against the VB6 source repo, writing output into the target repo's docs directory. Resolve the script path relative to this `SKILL.md` file:

   ```sh
   mkdir -p <target-repo>/docs
   python3 <skill-dir>/scripts/vb6_inventory.py <source-repo> --out <target-repo>/docs
   ```

   It writes `<target-repo>/docs/vb6-inventory.json`, `<target-repo>/docs/vb6-inventory.md`, and `<target-repo>/docs/source-application-brief.md`. Read all three before proposing architecture.

2. **Create governed documentation before implementation.** Read `references/governance-documentation.md` and `references/pre-migration-design-brief.md`, then write `<target-repo>/docs/migration-governance-brief.md`.
   It must document the existing application, old-system diagrams, new-system diagrams, and source-to-target mappings for screens, code modules, data assets, dependencies, workflows, tests, and accepted deferrals.

3. **Present the documents before asking for approval.** Do not merely say that docs were written. The user should not have to go hunting through files before the gate.

   Provide an in-chat review packet with:
   - the absolute source repo path and target repo path
   - the absolute paths of `<target-repo>/docs/source-application-brief.md` and `<target-repo>/docs/migration-governance-brief.md`
   - a concise but complete source-application brief summary
   - old-system Mermaid diagram(s)
   - proposed new-system Mermaid diagram(s)
   - screen/form mapping table
   - code module/procedure mapping table
   - database/file/query mapping table
   - dependency/risk mapping table
   - open questions and assumptions

   If the environment can open local files, offer to open the generated Markdown files in the user's editor or preview app, and do so when the user asks. If the documents are too long for a single response, present the most decision-relevant sections in-chat and explicitly state which detailed sections remain in the file.

4. **Ask for review before proceeding.** After presenting the review packet, ask:

   "Have you reviewed the source application brief and migration governance brief? What questions or corrections do you have, and do you approve proceeding with implementation?"

   Treat questions or corrections as a stop signal: revise the docs and present the changed sections before asking again. Do not begin Phase 1 implementation until the user explicitly approves. Record the approval in the governance brief or `<target-repo>/docs/migration-notes.md`.

5. **Ask only architecture questions that matter.** Default to the proven demo stack unless the user has a reason to vary it:
   - ASP.NET Core LTS + EF Core + SQLite
   - Vite + React + TypeScript
   - cookie auth for browser CRUD apps
   - fresh seed unless a real `.bak` or production data migration is in scope; for `.bak` migrations, use the `mssql-bak-to-sqlite` skill or Claude's `/vb6-migrate-data` command

6. **Write a phased plan before broad edits.** Include:
   - source app inventory summary
   - startup screen and public/private entry points
   - smells to fix, especially SQL injection, plaintext passwords, globals, denormalized tables, missing transactions
   - semantic hazards to test: `On Error`, default properties, arrays/bounds, `Collection`, `Variant`, DAO/ADO cursors, UI row indexes
   - target architecture and target repo directory tree
   - old-system and new-system Mermaid diagrams
   - form-to-route mapping table
   - code-module-to-service/component mapping table
   - database/file/query-to-entity/import mapping table
   - dependency replacement/deferral table
   - data import/export path for `.mdb`, `.accdb`, or `.bak` files when present
   - build sequence, phases 0-8
   - verification flows that exercise every migrated form

7. **Execute in thin vertical slices.**
   - Phase 0: initialize the target repo if needed, verify SDKs/runtime, decide whether WSL2-specific local `dotnet`/Node paths are needed, and record environment quirks in `<target-repo>/docs/migration-notes.md`.
   - Phase 1: scaffold backend with `dotnet-sqlite-scaffold`.
   - Phase 2: translate schema and data access with `vb6-ado-patterns`; put multi-write business logic in services with transactions.
   - Phase 3: scaffold frontend with `vite-react-crud-scaffold`.
   - Phase 4: translate one form by hand, then reuse the pattern for the rest.
   - Phase 5: add README, form mapping, compatibility ledger, semantic ledger, remaining-work ledger, and a smoke script.
   - Phase 6: if the user chose desktop wrapper / Tauri, run `tauri-dotnet-sidecar-packaging` to add macOS packaging and WSL2 Windows NSIS build support.
   - Phase 7: run `vb6-parity-auditor` and close every blocking parity gap or record an explicit accepted deferral.
   - Phase 8: update plugin skills only with generalized lessons backed by the codebase.

8. **Track ledgers while migrating.**
   - Compatibility ledger: every VB6 form/procedure/control that matters, where it landed, parity status, and tests.
   - Semantic ledger: source constructs whose behavior can silently change in C# or React.
   - Remaining-work ledger: anything deferred, blocked, not applicable, or still unmigrated.

9. **Verify with a real smoke flow.** Keep the smoke script close to the app's primary workflows, not just `/health`.
   Include startup/public flows, login, CRUD, search/paging, modal/helper workflows, money/quantity/status changes, password confirmations, and role-gated actions when present.

10. **Audit parity before completion.** Use `vb6-parity-auditor` after implementation and smoke testing.
   Do not call the migration done until the audit verdict is `Complete`, `Complete with accepted deferrals`, or `Blocked` with concrete external blockers.

## References

- For a proven form-to-route reduction pattern, read `references/seed-library-form-mapping.md`.
- For verification flow shape, read `references/seed-library-smoke-flow.md`.
- For governed documentation requirements, read `references/governance-documentation.md`.
- For the required planning shape, read `references/pre-migration-design-brief.md`.
- For compatibility/semantic/remaining-work tracking, read `references/migration-ledgers.md`.
- For WSL2 runtime and smoke-test details, read `references/wsl2-runtime-notes.md`.
- For Tauri desktop packaging with an ASP.NET Core sidecar, invoke `tauri-dotnet-sidecar-packaging`.
- For final parity review, invoke the `vb6-parity-auditor` skill.

## Guardrails

- Treat migration as a rewrite with preserved behavior, not a line-by-line port.
- Keep legacy VB6 source and generated target implementation in separate repositories/directories by default.
- Do not carry SQL concatenation, global mutable ADO state, plaintext auth, or denormalized lookup copies forward.
- Do not invent requirements when a form is unclear. Mark it as an open question.
- Prefer deterministic inventory output over freehand summaries; patch the helper when it misses a repeatable VB6 pattern.
- Do not skip the source/governance document review gate, even for demos.
- Do not ask the user whether they have read generated docs until you have presented the review packet in-chat or opened the files for them.
- Do not clean, archive, or delete the source repo as the default way to get a fresh run. Use a new target repo/path instead.
- Do not call the migration complete while unmapped forms, helper dialogs, menu handlers, double-click handlers, or modal confirmations remain outside the compatibility ledger.
