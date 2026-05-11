#!/usr/bin/env bash
# Build a Windows-native Tauri NSIS installer from Linux/WSL2 without PowerShell.

set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
FRONTEND_DIR="$ROOT/frontend"
TARGET="${TARGET:-x86_64-pc-windows-msvc}"
RID="${RID:-win-x64}"
BUNDLES="${BUNDLES:-nsis}"

need() {
  if ! command -v "$1" >/dev/null 2>&1; then
    echo "Missing required command: $1" >&2
    return 1
  fi
}

if [[ "$(uname -s)" != "Linux" ]]; then
  echo "This script is intended for Linux/WSL2. Use scripts/build-sidecar.sh + npx tauri build on macOS." >&2
  exit 2
fi

missing=0
for cmd in dotnet npm rustup cargo clang makensis; do
  need "$cmd" || missing=1
done

if ! command -v ld.lld >/dev/null 2>&1 && ! command -v lld-link >/dev/null 2>&1; then
  echo "Missing required linker: ld.lld or lld-link" >&2
  missing=1
fi

if [[ "$missing" -ne 0 ]]; then
  cat >&2 <<'EOF'

Install the Linux/WSL2 prerequisites, for example on Ubuntu:
  sudo apt update
  sudo apt install -y build-essential curl clang llvm lld nsis

Also install .NET SDK, Node/npm, and Rust/rustup if they are not already present.
EOF
  exit 2
fi

echo "Installing Rust target $TARGET if needed"
rustup target add "$TARGET"

if ! command -v cargo-xwin >/dev/null 2>&1; then
  echo "Installing cargo-xwin"
  cargo install --locked cargo-xwin
fi

echo "Installing frontend dependencies"
( cd "$FRONTEND_DIR" && npm ci )

if [[ "${SKIP_TESTS:-0}" != "1" ]]; then
  echo "Running .NET tests"
  dotnet test "$ROOT/backend/Library.Api.Tests/Library.Api.Tests.csproj"
fi

echo "Building Windows .NET sidecar (rid=$RID)"
( cd "$ROOT" && RID="$RID" ./scripts/build-sidecar.sh )

echo "Building Windows Tauri bundle (target=$TARGET, bundles=$BUNDLES)"
( cd "$FRONTEND_DIR" && npx tauri build --runner cargo-xwin --target "$TARGET" --bundles "$BUNDLES" )

echo "Windows bundle ready under:"
echo "  $FRONTEND_DIR/src-tauri/target/$TARGET/release/bundle/$BUNDLES"
