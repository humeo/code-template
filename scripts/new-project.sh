#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TEMPLATES_DIR="$SCRIPT_DIR/../templates"

SUPPORTED_LANGS=$(ls "$TEMPLATES_DIR")

usage() {
  echo "Usage:"
  echo "  new-project <language> <project-name> [destination]  # create new dir"
  echo "  new-project <language> init                          # init in current dir"
  echo ""
  echo "Supported languages:"
  for lang in $SUPPORTED_LANGS; do
    echo "  - $lang"
  done
  echo ""
  echo "Examples:"
  echo "  new-project python my-app"
  echo "  new-project python my-app ~/projects"
  echo "  new-project python init          # init current directory"
  exit 1
}

# Args
LANG="${1:-}"
PROJECT_NAME="${2:-}"

[[ -z "$LANG" || -z "$PROJECT_NAME" ]] && usage

TEMPLATE_DIR="$TEMPLATES_DIR/$LANG"
if [[ ! -d "$TEMPLATE_DIR" ]]; then
  echo "Error: no template found for language '$LANG'"
  echo "Supported: $SUPPORTED_LANGS"
  exit 1
fi

# "init" means initialize current directory in-place
if [[ "$PROJECT_NAME" == "init" ]]; then
  PROJECT_DIR="$(pwd)"
  echo "Initializing $LANG template in current directory: $PROJECT_DIR"

  # Copy template files, skip if already exists
  cp -rn "$TEMPLATE_DIR/." "$PROJECT_DIR/"

  # Init git if not already a repo
  if [[ ! -d "$PROJECT_DIR/.git" ]]; then
    git init -q
  fi
  git add .
  git commit -q -m "chore: init project from $LANG template" 2>/dev/null || true

  echo "Done."
  exit 0
fi

DEST="${3:-$(pwd)}"
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
