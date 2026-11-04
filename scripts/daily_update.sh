#!/usr/bin/env bash
# Rebuild the edition and publish only when the generated data actually changed.
# Safe to run from cron. Never touches the git remote configuration.
set -euo pipefail

cd "$(dirname "$0")/.."
REPO="$(pwd)"

echo "[daily_update] $(date -u +%Y-%m-%dT%H:%M:%SZ) rebuilding in ${REPO}"

# A failed build exits non-zero and leaves data/diario.json untouched (see build_diario.py).
git pull -q --ff-only origin "$(git rev-parse --abbrev-ref HEAD)"
python3 scripts/build_diario.py

# Stage only the generated data; source and template changes are published by hand.
git add -A data

if git diff --cached --quiet; then
  echo "[daily_update] sin cambios en data/: no se crea commit."
  exit 0
fi

git commit -m "Actualización automática del Diario Celeste ($(date -u +%Y-%m-%d))"

# Push to the already-configured upstream of the current branch. If none is set,
# this fails (non-zero) rather than inventing or editing any remote.
BRANCH="$(git rev-parse --abbrev-ref HEAD)"
git push origin "HEAD:${BRANCH}"

echo "[daily_update] publicado."
