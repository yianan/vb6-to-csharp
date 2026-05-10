# Pre-Migration Design Brief

Create this brief after inventorying the whole VB6 project and before broad coding, unless the user has already approved an equivalent plan.

## Required Sections

1. Source summary
   - Startup object and first screen.
   - Forms, modules, classes, resources, data files, project groups, and COM/OCX references.
   - Major user roles and public/private workflows.

2. Target experience
   - What the user sees first in the web app.
   - Route/screen list.
   - Which VB6 forms become pages, tabs, panels, dialogs, prompts, or background services.
   - Which workflows intentionally change for web ergonomics.

3. Architecture
   - .NET projects, React project, database target, and runtime assumptions.
   - API endpoints grouped by workflow.
   - Domain/application services and where business rules live.

4. Data plan
   - Schema mapping from Access/DAO/ADO/SQL Server to EF Core.
   - Seed data.
   - Import/export plan for existing `.mdb`, `.accdb`, or `.bak` data, or why import is not applicable.

5. Semantic hazard plan
   - `On Error`, `Resume Next`, default properties, `Collection`, arrays/bounds, date/currency/null handling, global state, and UI index lookups.
   - Specific tests or characterization checks for risky behavior.

6. Slice plan
   - Ordered workflow slices from smallest runnable slice to full parity.
   - For each slice: source files/procedures, target components, tests, and smoke checks.

7. Completion criteria
   - All forms/procedures mapped to migrated, intentionally redesigned, user-deferred, blocked, or not applicable.
   - Backend build/test pass.
   - Frontend lint/build pass.
   - Live smoke checks pass in the target runtime.
   - `vb6-parity-auditor` has run and every blocking finding is fixed, user-deferred, blocked with a concrete reason, or not applicable.
   - Compatibility, semantic, and remaining-work ledgers are current.

## User Review

Show the design brief before implementation. Ask the user to confirm notable product choices, especially:

- Whether public workflows remain public.
- Whether login, confirmation, and helper forms should remain modal.
- Whether the target should preserve exact UI layout or use web-native task layouts.
- Whether plaintext password parity should be kept only for demo migration or replaced immediately.
- Whether SQLite is sufficient or a server database is preferred.
