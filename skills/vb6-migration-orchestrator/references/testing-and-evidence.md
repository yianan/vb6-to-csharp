# Testing And Evidence Standard

Use this reference whenever planning, implementing, or closing a migration. Build success alone is not enough evidence.

## Required Artifacts

- `docs/test-plan.md`
- `docs/test-results.md`
- `docs/slice-reports.md`
- `docs/final-build-report.md`
- `docs/migration-closeout.md`

## Test Plan

`docs/test-plan.md` must describe:

- selected backend test approach
- selected frontend test approach
- smoke-test workflow coverage
- data import or seed validation
- semantic hazard tests
- parity audit inputs
- final build validation

Every source workflow that matters should map to at least one test, smoke step, characterization note, manual verification entry, or accepted deferral.

## Test Results

`docs/test-results.md` must record each command run:

| Time | Command | Purpose | Result | Notes |
|---|---|---|---|---|

Include pass/fail status, useful output summaries, and links/paths to logs when generated.

## Slice Reports

`docs/slice-reports.md` must be updated after every implementation slice:

| Slice | Source coverage | Target changes | Tests run | Result | Parity changes | Open items |
|---|---|---|---|---|---|---|

If a slice fails tests, record the failure and fix before moving to the next slice unless the user explicitly accepts a deferral.

## Final Build Report

`docs/final-build-report.md` must include:

- approved build target
- build commands
- environment/runtime versions
- test/parity verdict used as input
- artifact paths
- checksums when practical
- unresolved accepted deferrals
- rebuild command

## Closeout

`docs/migration-closeout.md` must summarize:

- source repo and commit/hash
- target repo and commit/hash
- selected stack/options
- generated artifact paths
- final build artifact paths
- final test results
- parity verdict
- accepted deferrals
- known limitations
- run/rebuild/retest instructions
- reproducibility notes

