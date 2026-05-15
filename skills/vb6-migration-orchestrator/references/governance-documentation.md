# Governance Documentation Standard

Use this reference when producing migration documentation. The documents are evidence that the migration is controlled, reviewable, and repeatable.

## Required Artifacts

1. `docs/vb6-inventory.json`
   - Machine-readable inventory of projects, forms, modules, controls, SQL references, data files, resources, binary dependencies, risks, and smells.

2. `docs/vb6-inventory.md`
   - Human-readable summary of counts, forms, modules, data files, dependencies, risk hits, and smells.

3. `docs/source-application-brief.md`
   - Existing application documentation.
   - Must include old-system diagrams and maps of source screens, code modules, data assets, dependencies, and risks.

4. `docs/migration-governance-brief.md`
   - Reviewed plan for the target system.
   - Must include old-to-new mapping tables, target diagrams, data plan, semantic hazard plan, slice plan, verification plan, and review gates.

5. Ledgers:
   - `docs/compatibility-ledger.md`
   - `docs/semantic-ledger.md`
   - `docs/remaining-work-ledger.md`

6. Verification evidence:
   - build/test commands and results
   - smoke script
   - data import logs/counts when applicable
   - parity audit report

## Source-To-Target Mapping Requirements

Every migration plan must include these tables:

### Screen Mapping

| Legacy screen/form | Legacy purpose | Target route/page/dialog | Target API/service | Verification | Status |
|---|---|---|---|---|---|

### Code Mapping

| Legacy file | Procedure/event/class | Legacy behavior | Target file/member | Verification | Status |
|---|---|---|---|---|---|

### Database Mapping

| Legacy table/query/file | Legacy columns/meaning | Target entity/table | Transform/import rule | Verification | Status |
|---|---|---|---|---|---|

### Dependency Mapping

| Legacy dependency | Usage | Target replacement | Risk | Verification/deferral |
|---|---|---|---|---|

## Review Gate Wording

Before implementation, first present the review packet in-chat or open the generated Markdown files for the user. The review packet must include the decision-critical contents, not just links:

- absolute paths to the source brief and governance brief
- source application summary
- old-system Mermaid diagram(s)
- new-system Mermaid diagram(s)
- screen/form mapping table
- code module/procedure mapping table
- database/file/query mapping table
- dependency/risk mapping table
- open questions and assumptions

Then ask:

> Have you reviewed the source application brief and migration governance brief? What questions or corrections do you have, and do you approve proceeding with implementation?

If the answer is not an explicit yes, do not begin broad implementation. Clarify questions, revise the documents, present the changed sections, and ask again.

Record the approval in the governance brief:

| Review item | Reviewer | Decision | Date | Notes |
|---|---|---|---|---|

## Evidence Standards

- A passing build is not evidence of parity.
- A CRUD route is not evidence that every form touching that table was migrated.
- A target screen is not complete until it maps to legacy behavior and has verification.
- A deferral is acceptable only when explicitly recorded with owner/next action or user acceptance.
- Dynamic or unclear VB6 behavior must be characterized by a test, smoke step, manual note, or accepted risk.
