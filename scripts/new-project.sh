#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TEMPLATES_DIR="$SCRIPT_DIR/../templates"

SUPPORTED_LANGS=$(ls "$TEMPLATES_DIR")

usage() {
  echo "Usage: new-project <language> <project-name> [destination]"
  echo ""
  echo "Supported languages:"
  for lang in $SUPPORTED_LANGS; do
    echo "  - $lang"
  done
  echo ""
  echo "Examples:"
  echo "  new-project python my-app"
  echo "  new-project python my-app ~/projects"
  exit 1
}

# Args
LANG="${1:-}"
PROJECT_NAME="${2:-}"
DEST="${3:-$(pwd)}"

[[ -z "$LANG" || -z "$PROJECT_NAME" ]] && usage

TEMPLATE_DIR="$TEMPLATES_DIR/$LANG"
if [[ ! -d "$TEMPLATE_DIR" ]]; then
  echo "Error: no template found for language '$LANG'"
  echo "Supported: $SUPPORTED_LANGS"
  exit 1
fi

PROJECT_DIR="$DEST/$PROJECT_NAME"
if [[ -e "$PROJECT_DIR" ]]; then
  echo "Error: '$PROJECT_DIR' already exists"
  exit 1
fi

echo "Creating $LANG project: $PROJECT_NAME"
echo "Location: $PROJECT_DIR"

# Copy template (including hidden files)
cp -r "$TEMPLATE_DIR" "$PROJECT_DIR"

# Init git
cd "$PROJECT_DIR"
git init -q
git add .
git commit -q -m "chore: init project from $LANG template"

echo ""
echo "Done. Project ready at: $PROJECT_DIR"
