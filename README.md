# vb6-to-csharp

A Claude Code plugin that migrates VB6 codebases to a modern stack: **ASP.NET Core + EF Core + SQLite** on the backend, **Vite + React + TypeScript** on the frontend.

## What's inside

- **Slash commands**
  - `/vb6-migrate` — orchestrate a full migration: inventory, architecture interview, plan, execute
  - `/vb6-inventory` — just the inventory step (forms, controls, SQL, schema inference)
  - `/vb6-translate-form <path>` — translate a single `.frm` to a React page + needed API endpoints
  - `/vb6-migrate-data <path-to-backup.bak>` — run the SQL Server backup to SQLite data-migration workflow
  - `/vb6-package-desktop [mac|wsl2-windows|both]` — package a migrated ASP.NET Core + React app as a Tauri desktop app
- **Subagent**: `vb6-migration-architect` — reads an inventory, asks 3-5 design questions, writes a phased plan
- **Skills** (auto-loaded by trigger):
  - `vb6-migration-orchestrator` — Codex-visible end-to-end workflow, inventory helper, and seed migration references
  - `vb6-parity-auditor` — final parity audit comparing VB6 inventory/source against migrated routes, endpoints, tests, smoke flows, and ledgers
  - `vb6-language-mapping` — VB6 ↔ C# syntax/semantics
  - `vb6-error-handling` — `On Error Goto` / `Resume Next` / `Err` → `try`/`catch`
  - `vb6-data-types` — `Variant`, `Currency`, 1-based arrays, `Option Base`
  - `vb6-form-controls` — TextBox / MSFlexGrid / MSADODC → React equivalents
  - `vb6-ado-patterns` — global `ADODB.Connection` → DI'd `DbContext` + parameterized LINQ
  - `vb6-frm-parser` — `.frm` file format reference
  - `dotnet-sqlite-scaffold` — exact ASP.NET Core 10 + EF Core + SQLite recipe
  - `vite-react-crud-scaffold` — exact Vite + React + TanStack Query CRUD recipe
  - `mssql-bak-to-sqlite` — restore a SQL Server `.bak` and migrate data into SQLite
  - `tauri-dotnet-sidecar-packaging` — package the migrated app as a Tauri desktop app, including macOS and pure WSL2 Windows NSIS builds

## Codex workflow note

Claude sees the plugin's slash commands and architect agent. Codex primarily sees `skills/`, so the `vb6-migration-orchestrator` skill carries the full workflow in a Codex-loadable form and points to bundled scripts/references.

## Install

Clone the repo first:

```sh
git clone https://github.com/yianan/vb6-to-csharp.git
cd vb6-to-csharp
```

### Codex Desktop / Codex CLI

Install from a local clone:

```sh
./scripts/install-codex-local.sh
```

The script creates a local Codex marketplace wrapper at:

```text
~/.local/share/vb6-to-csharp-codex-marketplace
```

and enables:

```text
vb6-to-csharp@vb6-to-csharp-local
```

Restart Codex Desktop after running the script.

### Claude Code CLI

From a local clone:

```sh
claude plugin marketplace add "$(pwd)" --scope user
claude plugin install vb6-to-csharp@vb6-to-csharp
```

Or from GitHub:

```
/plugin marketplace add yianan/vb6-to-csharp
/plugin install vb6-to-csharp@vb6-to-csharp
```

### Claude Desktop (macOS)

`/plugin` is gated in Desktop sessions, so use Desktop's account-upload flow instead:

```sh
./scripts/build-plugin.sh             # produces vb6-to-csharp.plugin (a zip)
open -a Claude ./vb6-to-csharp.plugin # or drag the .plugin file onto Claude.app
```

Desktop uploads it to your account's plugins marketplace and syncs it back into the local cache. After that, `/vb6-migrate` is available in Desktop sessions. Re-run `build-plugin.sh` and re-open the file to push updates.

## Usage

In any directory containing a VB6 project (`.vbp`, `.frm`, `.bas`):

```
/vb6-migrate
```

The plugin inventories the source, asks architecture questions, writes a plan, and executes it phase by phase.

## Provenance

Built alongside a real VB6 → modern-stack migration of a library-management app. Every skill contains examples from that migration; the seed app is the smoke-test bed. As you exercise the plugin on new codebases, please update the relevant skill's "examples" section with what you learned and any new gotchas.

## Status

- ✅ Slash commands and architect agent in place
- ✅ Core skills (language, error handling, data types, controls, ADO, frm parser)
- ✅ Scaffold skills (dotnet-sqlite, vite-react)
- ✅ Codex-visible orchestration skill with a deterministic VB6 inventory helper
- ✅ Final parity-audit skill for missed forms, helper workflows, semantic hazards, and weak verification
- ✅ Tauri + ASP.NET Core sidecar packaging skill with macOS and WSL2 Windows build paths
- ⚠️ `mssql-bak-to-sqlite` is documentation-only — pattern is correct but not yet exercised end-to-end
- ⚠️ No automated tests yet; verify by running `/vb6-migrate` against a fresh VB6 codebase
