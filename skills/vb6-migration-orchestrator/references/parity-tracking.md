# Parity Tracking Standard

Parity is tracked continuously during migration and audited at the end. Do not wait until the final audit to discover missing forms or workflows.

## Continuous Ledgers

Update these after every implementation slice:

- `docs/compatibility-ledger.md`
- `docs/semantic-ledger.md`
- `docs/remaining-work-ledger.md`

The compatibility ledger tracks whether every source form, procedure, control, workflow, and data operation has a target outcome and verification.

The semantic ledger tracks VB6 behavior that can silently change in C# or React, including `On Error`, `Resume Next`, `Variant`, default properties, `Collection`, arrays/bounds, DAO/ADO cursors, positional grid/list indexes, `Currency`, `Date`, `Null`, `Empty`, and `Nothing`.

The remaining-work ledger tracks unmigrated, deferred, blocked, or not-applicable items with owner/next action and user decision.

## Slice Reporting

Every slice report must say how parity changed:

- rows moved from planned to implemented
- risks moved from open to verified
- new gaps discovered
- deferrals accepted or rejected
- tests/smoke steps that prove coverage

## Final Parity Audit

Run the `vb6-parity-auditor` after implementation and tests. It must compare:

- `docs/vb6-inventory.json`
- `docs/compatibility-ledger.md`
- `docs/semantic-ledger.md`
- `docs/remaining-work-ledger.md`
- `docs/test-results.md`
- `docs/slice-reports.md`
- target routes/components/endpoints/services
- smoke scripts and tests
- direct VB6 source sweeps

The audit verdict must be one of:

- `Complete`
- `Complete with accepted deferrals`
- `Blocked`
- `Incomplete`

Do not declare the migration done or ask for final product build approval while the verdict is `Incomplete`.

