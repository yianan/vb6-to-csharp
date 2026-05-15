#!/usr/bin/env bash
# Build a .plugin file (zip with `application/zip` content type, .plugin extension)
# that can be opened by Claude Desktop to upload to your account's plugins marketplace.
#
# Usage:
#   ./scripts/build-plugin.sh
#   open -a Claude ./vb6-to-csharp.plugin   # or just double-click it in Finder

set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
OUT="$ROOT/vb6-to-csharp.plugin"

cd "$ROOT"
rm -f "$OUT"
zip -rq "$OUT" . -x \
  ".git/*" "*.DS_Store" \
  "vb6-to-csharp.plugin" \
  "scripts/*" \
  "*__pycache__*" "*.pyc" \
  "node_modules/*"

echo "✅ Built $OUT ($(du -h "$OUT" | cut -f1))"
echo "Open in Claude Desktop:"
echo "  open -a Claude \"$OUT\""
