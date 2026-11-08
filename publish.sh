#!/usr/bin/env bash
# publish.sh — build the Good Ancestor open lab site and deploy it to the staging Worker.
#
# Adapted from GoodAncestor/seagrass. Same toolchain, same build_site.py dialect.
#
#   Usage:
#     ./publish.sh build      # generate pages + render HTML into publish/  (no deploy)
#     ./publish.sh deploy     # build, then deploy to the staging Worker (openlab.ancestor.workers.dev)
#     ./publish.sh            # same as build
#
#   Requirements:
#     - python3 with pyyaml
#     - wrangler (npm i -g wrangler), logged in to the goodancestor account
#       (OAuth `wrangler login`, or CLOUDFLARE_API_TOKEN)   — only for `deploy`
#
#   Four of the five pages are generated from data/items.yaml on every build.
#   They are never committed; editing site/_generated/ by hand does nothing.
#
#   STAGING ONLY. This script deploys to the Workers static-assets Worker
#   `openlab` (https://openlab.ancestor.workers.dev). It used to name a Pages
#   project `openlab`, which no longer exists in the goodancestor account
#   (openlab.pages.dev is a third party's site). Production is a DIFFERENT
#   Worker, `open-dna-lab`, built by Workers Builds from `main` and bound to
#   openlab.goodancestor.com; this script refuses to deploy to it.

set -euo pipefail
cd "$(dirname "$0")"

MODE="${1:-build}"
SITE=site
GEN=site/_generated
PUB=publish
WORKER=openlab            # staging Worker (static assets). NOT open-dna-lab (production)
PROD_WORKER=open-dna-lab

# md source -> output html  (nav active-state key = output name)
declare -a PAGES=(
  "$SITE/overview.md:index.html"
  "$GEN/inventory.md:inventory.html"
  "$GEN/buy-list.md:buy-list.html"
  "$GEN/software.md:software.html"
  "$GEN/open-questions.md:open-questions.html"
  "$SITE/sequencing-protocol.md:protocol.html"
  "$SITE/adapted-methods.md:adaptations.html"
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
for f in hardware/*.scad hardware/*.stl templates/*.md templates/*.yaml templates/*.csv; do
  [ -e "$f" ] && cp "$f" "$PUB/downloads/"
done
echo "   downloads/ has $(ls "$PUB/downloads" | wc -l | tr -d ' ') files"

if [ "$MODE" != "deploy" ]; then
  echo "==> build complete: $PUB/  (run './publish.sh deploy' to push to staging)"
  exit 0
fi

if [ "$WORKER" = "$PROD_WORKER" ]; then
  echo "refusing: $PROD_WORKER is production (deploys only from main via Workers Builds)" >&2
  exit 1
fi
echo "==> deploy to Worker $WORKER — STAGING"
wrangler deploy --name "$WORKER" --assets "$PUB" --compatibility-date 2026-11-08
echo "==> staging: https://${WORKER}.ancestor.workers.dev"
echo "    openlab.goodancestor.com is production and only deploys from main."
