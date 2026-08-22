#!/usr/bin/env bash
# publish.sh — build the Good Ancestor open lab site and deploy to Cloudflare Pages.
#
# Adapted from GoodAncestor/seagrass. Same toolchain, same build_site.py dialect.
#
#   Usage:
#     ./publish.sh build      # generate pages + render HTML into publish/  (no deploy)
#     ./publish.sh deploy     # build, then deploy to the pages.dev staging URL
#     ./publish.sh            # same as build
#
#   Requirements:
#     - python3 with pyyaml
#     - wrangler (npm i -g wrangler)                        — only for `deploy`
#     - env: CLOUDFLARE_API_TOKEN, CLOUDFLARE_ACCOUNT_ID    — only for `deploy`
#
#   Four of the five pages are generated from data/items.yaml on every build.
#   They are never committed; editing site/_generated/ by hand does nothing.
#
#   STAGING ONLY. This script deploys to the pages.dev URL. The custom domain is
#   production and is not configured here — binding it needs an explicit
#   go-ahead, per the house rule inherited from the seagrass project.

set -euo pipefail
cd "$(dirname "$0")"

MODE="${1:-build}"
SITE=site
GEN=site/_generated
PUB=publish
PROJECT=openlab           # Cloudflare Pages project name
BRANCH=main

# md source -> output html  (nav active-state key = output name)
declare -a PAGES=(
  "$SITE/overview.md:index.html"
  "$GEN/inventory.md:inventory.html"
  "$GEN/buy-list.md:buy-list.html"
  "$GEN/software.md:software.html"
  "$GEN/open-questions.md:open-questions.html"
  "$SITE/sequencing-protocol.md:protocol.html"
  "$SITE/colorimetry-protocol.md:colorimetry.html"
)

echo "==> validate register"
python3 software/validate_register.py

echo "==> leakage scan"
./scripts/leakage_scan.sh

echo "==> doc voice check"
./scripts/doc_voice_check.sh

echo "==> generate pages from data/items.yaml"
python3 scripts/gen_pages.py

echo "==> clean publish/"
rm -rf "$PUB"; mkdir -p "$PUB"

echo "==> build web pages (nav-enabled)"
for pair in "${PAGES[@]}"; do
  md="${pair%%:*}"; out="${pair##*:}"
  python3 "$SITE/build_site.py" "$md" "$PUB/$out" --figdir figures --nav "$out"
done

echo "==> copy hardware downloads"
mkdir -p "$PUB/downloads"
for f in hardware/*.scad hardware/*.stl; do
  [ -e "$f" ] && cp "$f" "$PUB/downloads/"
done
echo "   downloads/ has $(ls "$PUB/downloads" | wc -l | tr -d ' ') files"

if [ "$MODE" != "deploy" ]; then
  echo "==> build complete: $PUB/  (run './publish.sh deploy' to push to staging)"
  exit 0
fi

echo "==> deploy to Cloudflare Pages ($PROJECT) — STAGING"
: "${CLOUDFLARE_API_TOKEN:?set CLOUDFLARE_API_TOKEN}"
: "${CLOUDFLARE_ACCOUNT_ID:?set CLOUDFLARE_ACCOUNT_ID}"
wrangler pages deploy "$PUB" --project-name "$PROJECT" --branch "$BRANCH" --commit-dirty=true
echo "==> staging: https://${PROJECT}.pages.dev"
echo "    Custom domain is NOT bound. That needs an explicit go-ahead."
