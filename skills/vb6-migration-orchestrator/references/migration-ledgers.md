# Migration Ledgers

Keep these ledgers current during migration. They prevent a "working app" from hiding unmigrated forms, silent semantic changes, or user-deferred work.

Update ledgers after every implementation slice, not only during the final audit. Each slice report should summarize which ledger rows changed and which tests or smoke steps prove the change.

## Compatibility Ledger

Use these columns:

| Source file | Source procedure/control | Legacy behavior | Target file/method/component | Parity status | Tests | Deferred cleanup | Status |
|---|---|---|---|---|---|---|---|

Allowed statuses:

- migrated
- partial
- user-deferred
- blocked
- not applicable

Each migrated or intentionally redesigned row needs target behavior plus verification, or an explicit accepted deferral.

## Semantic Ledger

Use this when the source contains language/runtime behavior that can silently change.

| Source file | Construct | Legacy behavior | Modern decision | Test or verification | Risk if wrong |
|---|---|---|---|---|---|

Common constructs:

- `On Error GoTo`
- `On Error Resume Next`
- `Collection`
- `Option Base`
- explicit `LBound`/`UBound`
- `Variant`
- default properties
- DAO/ADO cursor navigation
- positional grid/list subitems
- `Currency`, `Date`, `Null`, `Empty`, and `Nothing`

## Remaining-Work Ledger

Use this at every checkpoint and before declaring completion.

| Legacy item | Why it remains | Owner/next action | Blocking dependency | User decision |
|---|---|---|---|---|

Before completion, each row should be gone, user-deferred, blocked with a concrete reason, or marked not applicable.

## Slice Report Linkage

Every row changed during a slice should be referenced from `docs/slice-reports.md`, including:

- source item covered
- target file or workflow
- tests run
- result
- user decision or deferral when applicable
