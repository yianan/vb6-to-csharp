---
name: vb6-migration-orchestrator
description: "Run the end-to-end VB6 to C# migration workflow in Codex: inventory a VB6 app, choose the migration architecture, scaffold backend/frontend, translate forms, verify flows, and feed project-specific gotchas back into the plugin. Use when the user asks to migrate, plan, inventory, or demo a VB6-to-C# migration."
---

# VB6 migration orchestrator

Use this skill as the Codex-visible equivalent of the plugin's Claude slash commands and architect agent.

## Workflow

Use `references/migration-decision-workflow.md` as the controlling process. This is a gated workflow, not a fire-and-forget scaffold.

0. **Gate 0: source and target approval.** Treat the VB6 checkout as read-only source input. Present the detected source repo, proposed target repo, proposed generated folders, and whether a git repo will be initialized. Offer the user choices to use the default, choose another path, use an existing empty target repo, or stop. Do not create the target repo or generated folders until the user approves.

1. **Gate 1: inventory approval.** After target location approval, run only inventory. Resolve the script path relative to this `SKILL.md` file:

   ```sh
   mkdir -p <target-repo>/docs
   python3 <skill-dir>/scripts/vb6_inventory.py <source-repo> --out <target-repo>/docs
   ```

   It writes `<target-repo>/docs/vb6-inventory.json`, `<target-repo>/docs/vb6-inventory.md`, and `<target-repo>/docs/source-application-brief.md`. Present an in-chat review packet for the source understanding and ask whether it is accurate. Revise the source brief/inventory notes if the user corrects anything.

2. **Gate 2: migration options approval.** Present a decision worksheet before writing the migration plan. Include recommendations, alternatives, rationale, risks, and output impact for backend, frontend, database, data strategy, auth, UI strategy, hosting, packaging, backend tests, frontend tests, parity tracking, and final build gate. Write selections to `<target-repo>/docs/migration-options.md` and `<target-repo>/docs/decision-log.md`.

3. **Gate 3: governance plan approval.** Read `references/governance-documentation.md`, `references/pre-migration-design-brief.md`, `references/testing-and-evidence.md`, and `references/parity-tracking.md`. Generate or update:
   - `<target-repo>/docs/migration-governance-brief.md`
   - `<target-repo>/docs/decision-log.md`
   - `<target-repo>/docs/migration-options.md`
   - `<target-repo>/docs/compatibility-ledger.md`
   - `<target-repo>/docs/semantic-ledger.md`
   - `<target-repo>/docs/remaining-work-ledger.md`
   - `<target-repo>/docs/test-plan.md`

   Present selected options, old/new diagrams, screen mapping, code mapping, data mapping, dependency mapping, test plan, parity plan, assumptions, and open questions in-chat or open the docs when asked. Ask for explicit approval before implementation planning.

4. **Gate 4: implementation approval.** Before scaffolding or writing implementation code, show exact folders/files/projects to create, commands to run, the first slice, expected tests, and ledgers to update. Ask for approval to begin implementation.

5. **Gate 5: slice execution and reporting.** Execute in thin vertical slices. After every slice update:
   - `<target-repo>/docs/compatibility-ledger.md`
   - `<target-repo>/docs/semantic-ledger.md`
   - `<target-repo>/docs/remaining-work-ledger.md`
   - `<target-repo>/docs/test-results.md`
   - `<target-repo>/docs/slice-reports.md`
   - `<target-repo>/docs/decision-log.md` when decisions or deferrals changed

   Each slice report must include source coverage, target files changed, tests added/run, pass/fail summary, parity status changes, open gaps, blockers, deferrals, and user decisions needed.

6. **Gate 6: full test and parity audit.** Run the agreed backend/frontend/build/smoke/data validation tests. Record commands and results in `<target-repo>/docs/test-results.md`. Run `vb6-parity-auditor` and write `<target-repo>/docs/parity-audit-report.md`. Do not continue to final build approval on `Incomplete`.

7. **Gate 7: final product build approval.** Only after tests pass and parity is `Complete`, `Complete with accepted deferrals`, or `Blocked` with concrete external blockers, ask whether to build the final product artifact. Record build commands, environment versions, artifact paths, checksums when practical, and unresolved accepted deferrals in `<target-repo>/docs/final-build-report.md`.

8. **Gate 8: closeout documentation and final acceptance.** After the final build succeeds, update `<target-repo>/docs/migration-closeout.md`, `<target-repo>/README.md`, final reports, ledgers, and decision log. Present a final handoff packet and ask for final acceptance. Record acceptance in `<target-repo>/docs/decision-log.md`.

9. **Skill upkeep.** Throughout execution, when you hit a VB6 quirk that's not yet documented, add a `[skill: <skill-name>]`-tagged note to `<target-repo>/docs/migration-notes.md` and update the skill's `SKILL.md` only when the pattern is general and backed by real source evidence.

## References

- For a proven form-to-route reduction pattern, read `references/seed-library-form-mapping.md`.
- For verification flow shape, read `references/seed-library-smoke-flow.md`.
- For the governing gate model, read `references/migration-decision-workflow.md`.
- For governed documentation requirements, read `references/governance-documentation.md`.
- For the required planning shape, read `references/pre-migration-design-brief.md`.
- For compatibility/semantic/remaining-work tracking, read `references/migration-ledgers.md`.
- For continuous parity tracking, read `references/parity-tracking.md`.
- For test/build/closeout evidence, read `references/testing-and-evidence.md`.
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
- Do not create a target repo, choose a stack, scaffold code, or build final artifacts before the relevant gate has explicit user approval.
- Treat user steering as change control: stop, record the change, update impacted docs/tests/ledgers, present the impact, and ask for renewed approval when scope, architecture, parity, tests, packaging, or build output changes.
- Do not move from one slice to the next without recording tests and parity ledger updates for the slice just completed.
- Do not call the migration complete while unmapped forms, helper dialogs, menu handlers, double-click handlers, or modal confirmations remain outside the compatibility ledger.
