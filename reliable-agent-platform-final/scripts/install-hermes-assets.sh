#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
HERMES_HOME="${HERMES_HOME:-$HOME/.hermes}"

SKILL_SOURCE="$PROJECT_ROOT/hermes/skills/reliable-platform-engineering"
SKILL_TARGET="$HERMES_HOME/skills/software-development/reliable-platform-engineering"
BUNDLE_SOURCE="$PROJECT_ROOT/hermes/bundles/reliable-platform-dev.yaml"
BUNDLE_TARGET="$HERMES_HOME/skill-bundles/reliable-platform-dev.yaml"

mkdir -p "$(dirname "$SKILL_TARGET")" "$(dirname "$BUNDLE_TARGET")"

if [[ -e "$SKILL_TARGET" ]]; then
  echo "Refusing to overwrite existing Hermes skill: $SKILL_TARGET"
  echo "Review and remove it manually before reinstalling."
  exit 1
fi

if [[ -e "$BUNDLE_TARGET" ]]; then
  echo "Refusing to overwrite existing Hermes bundle: $BUNDLE_TARGET"
  echo "Review and remove it manually before reinstalling."
  exit 1
fi

cp -R "$SKILL_SOURCE" "$SKILL_TARGET"
cp "$BUNDLE_SOURCE" "$BUNDLE_TARGET"

echo "Installed Hermes skill:"
echo "  $SKILL_TARGET"
echo "Installed Hermes bundle:"
echo "  $BUNDLE_TARGET"
echo
echo "Start Hermes in the repository root and run:"
echo "  /reliable-platform-dev"
