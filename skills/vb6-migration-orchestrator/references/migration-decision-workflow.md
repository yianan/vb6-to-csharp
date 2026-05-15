# Governed Migration Decision Workflow

Use this workflow for every end-to-end VB6 migration. The goal is to make the user feel in control while leaving a durable audit trail of choices, approvals, tests, parity status, and final build evidence.

## Continuous User Steering

The user may steer the migration at any point. They may change a prior decision, add or remove requirements, ask for more tests, reject a deferral, change packaging, pause, resume, stop, or ask for docs to be regenerated.

When that happens:

1. Stop forward motion.
2. Treat the request as a change request.
3. Identify impacted docs, code, tests, ledgers, build outputs, and parity status.
4. Record the change in `docs/decision-log.md`.
5. Update affected artifacts.
6. Present the changed sections and impact summary.
7. Ask for renewed approval when the change affects architecture, scope, parity, tests, packaging, or final build output.

Do not infer approval from silence.

## Required Gates

### Gate 0: Source And Target Approval

Before creating a target repo or generated files, present:

- detected source repo
- proposed target repo
- proposed generated folders
- whether the target repo will be initialized with git
- what will and will not be written to the source repo

Present choices:

| Choice | Meaning |
|---|---|
| Use proposed target repo | Create/use the sibling target path |
| Choose different target path | User provides another path |
| Use existing empty target repo | Use a repo the user already prepared |
| Stop | Do nothing |

No generated repo creation until the user approves the location.

### Gate 1: Inventory Approval

After target location approval, only run inventory. Generate:

- `docs/vb6-inventory.json`
- `docs/vb6-inventory.md`
- `docs/source-application-brief.md`

Present an in-chat review packet with the detected app name, startup form, form/module/data/dependency counts, major risks, old-system diagram, and uncertainty list.

Ask whether the source understanding is accurate. If the user corrects it, update the source brief and inventory notes before proceeding.

### Gate 2: Migration Options Approval

Present a decision worksheet with recommendations, alternatives, rationale, risks, and output impact.

Include at minimum:

| Decision | Recommended default | Alternatives to offer |
|---|---|---|
| Backend | ASP.NET Core + EF Core | MVC, minimal API, service split |
| Frontend | React + TypeScript | Vue, Svelte, Razor Pages, Blazor |
| Database | SQLite for demo | SQL Server, Postgres, Access import path |
| Data strategy | Fresh seed | Migrate `.bak`, hybrid, defer data |
| Auth | Single admin | No auth, roles, preserve legacy login |
| UI strategy | Web-native workflows | Pixel-ish form clone, hybrid |
| Hosting | Local dev | Deployable web app, desktop wrapper |
| Packaging | None initially | Tauri desktop, Docker, installer |
| Backend tests | xUnit API/service tests | Smoke only, integration-heavy |
| Frontend tests | Playwright smoke flows | Vitest component tests, manual only |
| Parity tracking | Update per slice | User may request additional final audit depth, but per-slice ledgers remain required |
| Build gate | Explicit final approval | Auto-build after tests |

Write selected choices to `docs/migration-options.md` and `docs/decision-log.md`.

### Gate 3: Governance Plan Approval

Generate or update:

- `docs/migration-governance-brief.md`
- `docs/decision-log.md`
- `docs/migration-options.md`
- `docs/compatibility-ledger.md`
- `docs/semantic-ledger.md`
- `docs/remaining-work-ledger.md`
- `docs/test-plan.md`

Present the decision-critical sections in-chat: selected options, old/new diagrams, screen mapping, code mapping, data mapping, dependency mapping, test plan, parity plan, assumptions, and open questions.

Ask for explicit approval before implementation planning.

### Gate 4: Implementation Approval

Before scaffolding or writing implementation code, show:

- exact folders to create
- major files/projects to create
- commands to run
- first slice to implement
- tests expected after the slice
- ledgers that will be updated

Ask for approval to begin implementation.

### Gate 5: Slice Execution And Reporting

Execute in thin vertical slices. After every slice, update:

- `docs/compatibility-ledger.md`
- `docs/semantic-ledger.md`
- `docs/remaining-work-ledger.md`
- `docs/test-results.md`
- `docs/slice-reports.md`
- `docs/decision-log.md` when decisions or deferrals changed

Each slice report must include:

- legacy forms/procedures/workflows covered
- target files changed
- tests added or run
- pass/fail summary
- parity status changes
- open gaps, blockers, and deferrals
- user decisions needed before the next slice

### Gate 6: Full Test And Parity Audit

After implementation slices are complete, run the agreed test suite and record results:

- backend unit/integration/API tests
- frontend tests where selected
- frontend build/lint where applicable
- smoke tests
- data import/seed validation
- packaging preflight if selected

Write `docs/test-results.md` and `docs/parity-audit-report.md`.

Run `vb6-parity-auditor`. The final verdict must be one of:

- `Complete`
- `Complete with accepted deferrals`
- `Blocked`
- `Incomplete`

Do not continue to final build approval on `Incomplete`.

### Gate 7: Final Product Build Approval

After tests pass and parity is `Complete`, `Complete with accepted deferrals`, or `Blocked` with concrete external blockers, ask whether to build the final product artifact.

Build may mean:

- local web app production build
- deployable web bundle
- Docker image
- Tauri desktop app
- Windows installer
- macOS `.app` / `.dmg`

Record build commands, outputs, environment versions, artifact paths, and checksums when practical in `docs/final-build-report.md`.

### Gate 8: Closeout Documentation And Final Acceptance

After the final build succeeds, update:

- `docs/final-build-report.md`
- `docs/migration-closeout.md`
- `docs/decision-log.md`
- `docs/test-results.md`
- `docs/parity-audit-report.md`
- `docs/remaining-work-ledger.md`
- `README.md`

Present a final handoff packet:

- source repo and commit/hash used
- target repo and commit/hash built
- selected stack
- test verdict
- parity verdict
- accepted deferrals
- build artifacts
- run instructions
- rebuild instructions
- remaining work

Ask for final acceptance. If accepted, record final acceptance in `docs/decision-log.md`.
