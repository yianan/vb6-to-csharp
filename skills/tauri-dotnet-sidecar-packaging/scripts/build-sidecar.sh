#!/usr/bin/env bash
# Build the self-contained .NET sidecar with the React SPA inside its wwwroot.
# Output is dropped at frontend/src-tauri/resources/library-api/ ready for
# `tauri build` to bundle.

set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
API_DIR="$ROOT/backend/Library.Api"
FRONTEND_DIR="$ROOT/frontend"

default_rid() {
  local os arch
  os="$(uname -s)"
  arch="$(uname -m)"

  case "$os:$arch" in
    Darwin:arm64) echo "osx-arm64" ;;
    Darwin:x86_64) echo "osx-x64" ;;
    Linux:x86_64) echo "linux-x64" ;;
    Linux:aarch64|Linux:arm64) echo "linux-arm64" ;;
    *)
      echo "Unable to infer RID for $os/$arch. Set RID explicitly, for example RID=win-x64." >&2
      exit 2
      ;;
  esac
}

RID="${RID:-$(default_rid)}"

if [[ -z "${DOTNET_ROOT:-}" && -d /opt/homebrew/opt/dotnet/libexec ]]; then
  export DOTNET_ROOT=/opt/homebrew/opt/dotnet/libexec
fi

echo "Building React SPA"
( cd "$FRONTEND_DIR" && npm run build )

echo "Copying dist to Library.Api/wwwroot"
rm -rf "$API_DIR/wwwroot"
mkdir -p "$API_DIR/wwwroot"
cp -R "$FRONTEND_DIR/dist/." "$API_DIR/wwwroot/"

echo "Publishing self-contained .NET binary (rid=$RID)"
rm -rf "$FRONTEND_DIR/src-tauri/resources/library-api"
( cd "$API_DIR" && dotnet publish -c Release -r "$RID" --self-contained true \
    -p:PublishSingleFile=true -p:IncludeNativeLibrariesForSelfExtract=true \
    -o "$FRONTEND_DIR/src-tauri/resources/library-api" )

echo "Removing pdb files to shrink bundle"
rm -f "$FRONTEND_DIR/src-tauri/resources/library-api"/*.pdb

echo "Sidecar ready at $FRONTEND_DIR/src-tauri/resources/library-api"
