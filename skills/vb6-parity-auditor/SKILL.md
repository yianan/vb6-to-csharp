---
name: vb6-parity-auditor
description: Audit a migrated VB6 application for parity gaps before declaring completion. Use after inventory and implementation, or during review, to compare VB6 source inventory against migrated routes, endpoints, tests, smoke scripts, compatibility ledgers, semantic ledgers, and remaining-work ledgers. Finds missed forms, modal/helper workflows, menu handlers, double-click handlers, data operations, role-gated actions, and semantic hazards.
---

# VB6 Parity Auditor

Use this as the final completion gate for a VB6-to-modern-stack migration, or as a review pass when a migrated app appears to work but may have hidden gaps.

## Inputs To Read

Prefer these files when present:

- `docs/vb6-inventory.json`
- `docs/vb6-inventory.md`
- `docs/form-mapping.md`
- `docs/migration-notes.md`
- `docs/compatibility-ledger.md`
- `docs/semantic-ledger.md`
- `docs/remaining-work-ledger.md`
- `scripts/smoke.sh` or equivalent smoke workflow
- backend route/endpoint/controller files
- frontend route/page/layout files
- backend and frontend tests

Then inspect the original VB6 source directly for anything the inventory may have missed:

- `.vbp` and `.vbg` project entry points.
- `.frm`, `.bas`, `.cls`, and `.ctl` files.
- `Form.Show`, `Load`, `Unload`, menu handlers, toolbar handlers, double-click handlers, timer handlers, and modal helper forms.
- DAO/ADO/SQL operations, schema creation code, and database files.
- Semantic hazards: `On Error`, `Resume Next`, default properties, `Variant`, `Collection`, `Option Base`, `LBound`, `UBound`, `ReDim Preserve`, `Currency`, `Date`, `Null`, `Empty`, `Nothing`, and positional grid/list indexes.

## Audit Method

1. Build the source checklist.
   - Start from `docs/vb6-inventory.json` if present.
   - Add any missing source items found by direct grep/sweep.
   - Include non-obvious workflows: helper forms, confirmation dialogs, selection dialogs, page-jump/filter dialogs, password prompts, menu actions, and row double-click actions.

2. Build the target checklist.
   - Frontend routes/pages/tabs/modals.
   - Backend endpoints/services.
   - Data import/seed paths.
   - Tests and smoke-script steps.
   - Ledgers and documented deferrals.

3. Match every source item to one target outcome:
   - migrated
   - intentionally redesigned
   - covered by another route/workflow
   - user-deferred
   - blocked with a concrete reason
   - not applicable
   - missing

4. Check semantic hazards.
   - Every risky VB6 construct should have a modern decision and a test, smoke step, characterization note, or explicit deferral.
   - Pay special attention to one-based indexes, DAO/ADO cursor paging, `On Error Resume Next`, password confirmations, money/date calculations, and status/permission changes.

5. Check verification coverage.
   - The smoke script should exercise real workflows, not only health checks.
   - It should cover startup/public flow, login, CRUD, search/paging, modal/helper workflows, money/quantity/status mutation, role-gated actions, and password/account changes when present.
   - Tests should cover extracted business rules and semantic hazards that are easy to regress.

## Report Shape

Write or return a concise parity audit report with these sections:

1. Executive verdict
   - `Complete`, `Complete with accepted deferrals`, `Not complete`, or `Blocked`.
   - One paragraph explaining why.

2. Findings
   - Ordered by severity.
   - Use `P0`, `P1`, `P2`, `P3`.
   - Include source file/procedure and target file/test/smoke reference where possible.

3. Source-to-target coverage table

| Source item | Legacy behavior | Target coverage | Verification | Status |
|---|---|---|---|---|

4. Semantic hazard table

| Source construct | Risk | Modern decision | Verification | Status |
|---|---|---|---|---|

5. Missing or weak verification
   - Tests/smoke steps to add before completion.

6. Accepted deferrals and blockers
   - Include owner/next action where known.

7. Completion recommendation
   - What must happen before the migration can honestly be called done.

## Severity Guide

- `P0`: source workflow is missing, destructive/security-sensitive behavior is wrong, data can be corrupted, or a formerly public/private access boundary changed without approval.
- `P1`: important workflow exists but lacks key behavior, backend enforcement, or verification.
- `P2`: parity likely but weakly documented/tested, or lower-risk helper flow is missing.
- `P3`: cleanup, naming, documentation, or polish that does not block parity.

## Guardrails

- Do not treat a passing build as parity.
- Do not treat a single CRUD route as covering every VB6 form that touched that table. Confirm buttons, menu actions, modal flows, double-click actions, and helper dialogs.
- Do not mark a source item complete unless it has target behavior plus verification, or an explicit accepted deferral.
- Do not silently accept frontend-only authorization for sensitive actions; backend/API behavior must enforce it.
- Do not assume the inventory is complete. Sweep the VB6 source before final judgment.
