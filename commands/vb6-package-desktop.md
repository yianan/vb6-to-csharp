---
description: Package a migrated ASP.NET Core + React app as a Tauri desktop app, including macOS builds and WSL2 Windows NSIS builds.
argument-hint: "[mac|wsl2-windows|both] [optional notes]"
---

Use this command after the VB6 migration has a working backend, frontend, smoke script, and parity audit.

Load the `tauri-dotnet-sidecar-packaging` skill, then:

1. Inspect the repo layout and confirm it has `backend/Library.Api`, `frontend`, and `scripts/smoke.sh` or equivalent.
2. Add or update the Tauri sidecar packaging files:
   - `frontend/src-tauri/`
   - `scripts/build-sidecar.sh`
   - `scripts/build-windows-wsl.sh`
   - `.gitignore` rules for generated sidecar and Tauri outputs.
3. Make the ASP.NET Core app serve the React build from `wwwroot` in release packaging.
4. Configure Tauri to load `http://127.0.0.1:5174/` and bundle `resources/library-api/**/*`.
5. Verify macOS sidecar packaging with `./scripts/build-sidecar.sh`.
6. If `$ARGUMENTS` include `wsl2-windows` or `both`, document and wire the WSL2 path:
   - `RID=win-x64 ./scripts/build-sidecar.sh`
   - `npx tauri build --runner cargo-xwin --target x86_64-pc-windows-msvc --bundles nsis`
7. Run available tests and smoke checks. If WSL2 is not available in the current environment, state that the final NSIS build must be run inside WSL2.

Do not commit generated `dist`, `target`, `resources`, `bin/obj`, database files, or self-contained sidecar binaries.
