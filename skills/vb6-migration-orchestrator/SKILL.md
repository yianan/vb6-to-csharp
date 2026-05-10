---
name: vb6-migration-orchestrator
description: Run the end-to-end VB6 to C# migration workflow in Codex: inventory a VB6 app, choose the migration architecture, scaffold backend/frontend, translate forms, verify flows, and feed project-specific gotchas back into the plugin. Use when the user asks to migrate, plan, inventory, or demo a VB6-to-C# migration.
---

# VB6 migration orchestrator

Use this skill as the Codex-visible equivalent of the plugin's Claude slash commands and architect agent.

## Workflow

1. **Inventory first.** Run the bundled inventory helper from the VB6 project root. Resolve the script path relative to this `SKILL.md` file:

   ```sh
   python3 <skill-dir>/scripts/vb6_inventory.py . --out docs
   ```

   It writes `docs/vb6-inventory.json` and `docs/vb6-inventory.md`. Read both before proposing architecture.

2. **Ask only architecture questions that matter.** Default to the proven demo stack unless the user has a reason to vary it:
   - ASP.NET Core LTS + EF Core + SQLite
   - Vite + React + TypeScript
   - cookie auth for browser CRUD apps
   - fresh seed unless a real `.bak` or production data migration is in scope; for `.bak` migrations, use the `mssql-bak-to-sqlite` skill or Claude's `/vb6-migrate-data` command

3. **Write a phased plan before broad edits.** Include:
   - source app inventory summary
   - startup screen and public/private entry points
   - smells to fix, especially SQL injection, plaintext passwords, globals, denormalized tables, missing transactions
   - semantic hazards to test: `On Error`, default properties, arrays/bounds, `Collection`, `Variant`, DAO/ADO cursors, UI row indexes
   - target architecture and directory tree
   - form-to-route mapping table
   - data import/export path for `.mdb`, `.accdb`, or `.bak` files when present
   - build sequence, phases 0-6
   - verification flows that exercise every migrated form

4. **Execute in thin vertical slices.**
   - Phase 0: verify SDKs/runtime, decide whether WSL2-specific local `dotnet`/Node paths are needed, and record environment quirks in `docs/migration-notes.md`.
   - Phase 1: scaffold backend with `dotnet-sqlite-scaffold`.
   - Phase 2: translate schema and data access with `vb6-ado-patterns`; put multi-write business logic in services with transactions.
   - Phase 3: scaffold frontend with `vite-react-crud-scaffold`.
   - Phase 4: translate one form by hand, then reuse the pattern for the rest.
   - Phase 5: add README, form mapping, compatibility ledger, semantic ledger, remaining-work ledger, and a smoke script.
   - Phase 6: run `vb6-parity-auditor` and close every blocking parity gap or record an explicit accepted deferral.
   - Phase 7: update plugin skills only with generalized lessons backed by the codebase.

5. **Track ledgers while migrating.**
   - Compatibility ledger: every VB6 form/procedure/control that matters, where it landed, parity status, and tests.
   - Semantic ledger: source constructs whose behavior can silently change in C# or React.
   - Remaining-work ledger: anything deferred, blocked, not applicable, or still unmigrated.

6. **Verify with a real smoke flow.** Keep the smoke script close to the app's primary workflows, not just `/health`.
   Include startup/public flows, login, CRUD, search/paging, modal/helper workflows, money/quantity/status changes, password confirmations, and role-gated actions when present.

7. **Audit parity before completion.** Use `vb6-parity-auditor` after implementation and smoke testing.
   Do not call the migration done until the audit verdict is `Complete`, `Complete with accepted deferrals`, or `Blocked` with concrete external blockers.

## References

- For a proven form-to-route reduction pattern, read `references/seed-library-form-mapping.md`.
- For verification flow shape, read `references/seed-library-smoke-flow.md`.
- For the required planning shape, read `references/pre-migration-design-brief.md`.
- For compatibility/semantic/remaining-work tracking, read `references/migration-ledgers.md`.
- For WSL2 runtime and smoke-test details, read `references/wsl2-runtime-notes.md`.
- For final parity review, invoke the `vb6-parity-auditor` skill.

## Guardrails

- Treat migration as a rewrite with preserved behavior, not a line-by-line port.
- Do not carry SQL concatenation, global mutable ADO state, plaintext auth, or denormalized lookup copies forward.
- Do not invent requirements when a form is unclear. Mark it as an open question.
- Prefer deterministic inventory output over freehand summaries; patch the helper when it misses a repeatable VB6 pattern.
- Do not call the migration complete while unmapped forms, helper dialogs, menu handlers, double-click handlers, or modal confirmations remain outside the compatibility ledger.
