#!/usr/bin/env bash
# Scan doc sources for things that must not be published: IP addresses, long hex
# secrets, key-like strings, personal paths and e-mail addresses.
# Usage: check_docs.sh <docs-src-dir> [extra-regex]
set -uo pipefail
D="$1/docs"; EXTRA="${2:-}"
echo "== IPv4 addresses (except loopback / 0.0.0.0)"
grep -nE '\b([0-9]{1,3}\.){3}[0-9]{1,3}\b' "$D"/*.md | grep -vE '127\.0\.0\.1|0\.0\.0\.0' || true
echo "== long hex / key-like strings"
grep -nE '[0-9a-f]{32,}|sk-[A-Za-z0-9]{16,}|AKIA[0-9A-Z]{16}|-----BEGIN' "$D"/*.md || true
echo "== personal paths and addresses"
grep -nE '/Users/[a-z]|/home/[a-z]|[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[a-z]{2,}' "$D"/*.md || true
if [ -n "$EXTRA" ]; then echo "== extra: $EXTRA"; grep -niE "$EXTRA" "$D"/*.md || true; fi
