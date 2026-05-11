---
name: tauri-dotnet-sidecar-packaging
description: Package a migrated ASP.NET Core + React/Vite VB6 rewrite as a Tauri desktop app with an ASP.NET Core sidecar, including macOS .app/.dmg builds and pure WSL2/Linux Windows NSIS builds using cargo-xwin. Use when the user chooses a desktop wrapper, asks to build/package/distribute a migrated app, or needs Windows builds from WSL2 without PowerShell.
---

# Tauri + ASP.NET Core sidecar packaging

Use this after the migrated web app has a working ASP.NET Core API, Vite/React frontend, smoke test, and parity audit. This skill turns the app into a desktop package without changing the same-origin auth model.

## Architecture

- ASP.NET Core sidecar serves both `/api/*` and the built React SPA from `wwwroot/`.
- Tauri release window loads `http://127.0.0.1:5174/`, not a `tauri://` bundled frontend.
- The Rust shell starts the sidecar, waits for `127.0.0.1:5174`, then shows the window.
- Cookie auth remains same-origin because the SPA and API are served by the sidecar.
- Bundle resources with array-form glob: `["resources/library-api/**/*"]`. Tauri preserves the source tree under the app resource directory.

## Files to create

Add these files to the migrated app when desktop packaging is in scope:

```text
frontend/src-tauri/
frontend/src-tauri/src/lib.rs
frontend/src-tauri/src/main.rs
frontend/src-tauri/tauri.conf.json
scripts/build-sidecar.sh
scripts/build-windows-wsl.sh
```

Use the template scripts bundled with this skill:

```sh
cp <skill-dir>/scripts/build-sidecar.sh scripts/build-sidecar.sh
cp <skill-dir>/scripts/build-windows-wsl.sh scripts/build-windows-wsl.sh
chmod +x scripts/build-sidecar.sh scripts/build-windows-wsl.sh
```

Then adapt project names, ports, app identifiers, and output paths.

## .gitignore

Do not commit generated build outputs:

```gitignore
backend/**/bin/
backend/**/obj/
backend/**/*.db
backend/**/*.db-shm
backend/**/*.db-wal
backend/Library.Api/wwwroot/
frontend/node_modules/
frontend/dist/
frontend/src-tauri/target/
frontend/src-tauri/resources/
frontend/src-tauri/gen/
```

Commit lockfiles (`package-lock.json`, `Cargo.lock`) and source icons. Do not commit the self-contained sidecar binary; it can exceed GitHub's normal file limit and is platform-specific.

## macOS build

```sh
npm ci --prefix frontend
dotnet test backend/Library.Api.Tests/Library.Api.Tests.csproj
./scripts/build-sidecar.sh
cd frontend
npx tauri build
```

Override RID when needed:

```sh
RID=osx-arm64 ./scripts/build-sidecar.sh
RID=osx-x64 ./scripts/build-sidecar.sh
```

Expected output:

```text
frontend/src-tauri/target/release/bundle/macos/
frontend/src-tauri/target/release/bundle/dmg/
```

## Windows build from WSL2

Use NSIS, not MSI. The WSL2 path should not use PowerShell or Windows Visual Studio Build Tools.

Ubuntu/WSL2 prerequisites:

```sh
sudo apt update
sudo apt install -y build-essential curl clang llvm lld nsis
```

Install .NET SDK, Node/npm, and Rust/rustup in WSL2. Then:

```sh
./scripts/build-windows-wsl.sh
```

The script should:

```sh
npm ci --prefix frontend
dotnet test backend/Library.Api.Tests/Library.Api.Tests.csproj
RID=win-x64 ./scripts/build-sidecar.sh
cd frontend
npx tauri build --runner cargo-xwin --target x86_64-pc-windows-msvc --bundles nsis
```

Expected output:

```text
frontend/src-tauri/target/x86_64-pc-windows-msvc/release/bundle/nsis/
```

## Verification

Before calling packaging complete:

1. Run backend tests.
2. Run frontend build and lint.
3. Run the app smoke script.
4. Run `RID=win-x64 ./scripts/build-sidecar.sh` and confirm `frontend/src-tauri/resources/library-api/Library.Api.exe` exists.
5. Run `./scripts/build-sidecar.sh` on macOS and confirm `frontend/src-tauri/resources/library-api/Library.Api` exists.
6. On WSL2, run `./scripts/build-windows-wsl.sh` and test the generated installer on Windows.

## Gotchas

- `tauri.conf.json` with `"targets": "all"` is fine on macOS, but WSL2 Windows cross-builds should pass `--bundles nsis`.
- The .NET sidecar binary name is `Library.Api.exe` on Windows and `Library.Api` on macOS/Linux. The Rust launcher must branch on `cfg!(windows)`.
- Avoid hard-coded macOS `DOTNET_ROOT`; only set it if the Homebrew path exists and `DOTNET_ROOT` is not already set.
- Do not use WebView cross-origin cookies. Serve the SPA from ASP.NET Core instead.
- WSL2 builds can create Windows binaries, but they cannot honestly validate Windows runtime behavior. Test the installer on Windows.
