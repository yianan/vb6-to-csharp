#!/usr/bin/env bash
# Install this plugin into Codex from a local clone.
#
# Codex local marketplaces expect:
#   marketplace-root/.agents/plugins/marketplace.json
#   marketplace-root/plugins/<plugin-name>/.codex-plugin/plugin.json
#
# This repo is the plugin root, so this script creates a small local marketplace
# wrapper that symlinks back to the clone.

set -euo pipefail

PLUGIN_NAME="vb6-to-csharp"
MARKETPLACE_NAME="vb6-to-csharp-local"
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
WRAPPER_ROOT="${VB6_TO_CSHARP_CODEX_MARKETPLACE:-$HOME/.local/share/vb6-to-csharp-codex-marketplace}"
CONFIG_PATH="${CODEX_CONFIG:-$HOME/.codex/config.toml}"

if ! command -v codex >/dev/null 2>&1; then
  echo "codex CLI was not found on PATH." >&2
  exit 1
fi

if [ ! -f "$ROOT/.codex-plugin/plugin.json" ]; then
  echo "Missing $ROOT/.codex-plugin/plugin.json" >&2
  exit 1
fi

mkdir -p "$WRAPPER_ROOT/.agents/plugins" "$WRAPPER_ROOT/plugins"
ln -sfn "$ROOT" "$WRAPPER_ROOT/plugins/$PLUGIN_NAME"

cat > "$WRAPPER_ROOT/.agents/plugins/marketplace.json" <<JSON
{
  "name": "$MARKETPLACE_NAME",
  "interface": {
    "displayName": "VB6 to C# Local"
  },
  "plugins": [
    {
      "name": "$PLUGIN_NAME",
      "source": {
        "source": "local",
        "path": "./plugins/$PLUGIN_NAME"
      },
      "policy": {
        "installation": "AVAILABLE",
        "authentication": "ON_INSTALL"
      },
      "category": "Coding"
    }
  ]
}
JSON

codex plugin marketplace remove "$PLUGIN_NAME" >/dev/null 2>&1 || true
codex plugin marketplace remove "$MARKETPLACE_NAME" >/dev/null 2>&1 || true
codex plugin marketplace add "$WRAPPER_ROOT"

mkdir -p "$(dirname "$CONFIG_PATH")"
touch "$CONFIG_PATH"
if ! grep -Fq "[plugins.\"$PLUGIN_NAME@$MARKETPLACE_NAME\"]" "$CONFIG_PATH"; then
  cp "$CONFIG_PATH" "$CONFIG_PATH.bak-vb6-plugin-$(date +%Y%m%d%H%M%S)"
  {
    printf '\n'
    printf '[plugins."%s@%s"]\n' "$PLUGIN_NAME" "$MARKETPLACE_NAME"
    printf 'enabled = true\n'
  } >> "$CONFIG_PATH"
fi

echo "Installed Codex marketplace wrapper:"
echo "  $WRAPPER_ROOT"
echo
echo "Enabled plugin:"
echo "  $PLUGIN_NAME@$MARKETPLACE_NAME"
echo
echo "Restart Codex Desktop to load it."
