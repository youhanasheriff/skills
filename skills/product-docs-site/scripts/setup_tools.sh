#!/usr/bin/env bash
# One-time setup of the docs build tools (about 400 MB: Mermaid, Puppeteer, Chrome for Testing).
# Usage: setup_tools.sh [tools-dir]   (default ~/.cache/product-docs-site/tools)
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
TOOLS="${1:-${DOCS_TOOLS:-$HOME/.cache/product-docs-site/tools}}"
mkdir -p "$TOOLS"
cd "$TOOLS"
if [ ! -x venv/bin/python ]; then python3 -m venv venv; fi
venv/bin/pip -q install markdown mdx_truly_sane_lists
[ -f package.json ] || npm init -y >/dev/null
[ -d node_modules/@mermaid-js/mermaid-cli ] || npm i -s @mermaid-js/mermaid-cli
npx --yes puppeteer browsers install chrome >/dev/null
cp "$HERE/render.mjs" "$HERE/shot.mjs" "$TOOLS/"
echo "Tools ready in $TOOLS"
echo "Build with: DOCS_TOOLS=$TOOLS $TOOLS/venv/bin/python $HERE/build_docs.py --src <docs-src-dir>"
