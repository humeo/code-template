#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TEMPLATES_DIR="$SCRIPT_DIR/../templates"

# Check gum
if ! command -v gum &>/dev/null; then
  echo "Error: gum is required. Install with: brew install gum"
  exit 1
fi

# --- Select language ---
SUPPORTED_LANGS=$(ls "$TEMPLATES_DIR")
LANG=$(printf "%s\n" $SUPPORTED_LANGS | gum choose --header "Select language")
[[ -z "$LANG" ]] && exit 0

TEMPLATE_DIR="$TEMPLATES_DIR/$LANG"

# --- Select mode: new dir or current dir ---
MODE=$(gum choose --header "Where to initialize?" "New subdirectory" "Current directory")
[[ -z "$MODE" ]] && exit 0

if [[ "$MODE" == "New subdirectory" ]]; then
  PROJECT_NAME=$(gum input --placeholder "project name" --header "Project name")
  [[ -z "$PROJECT_NAME" ]] && exit 0
  PROJECT_DIR="$(pwd)/$PROJECT_NAME"
  if [[ -e "$PROJECT_DIR" ]]; then
    gum log --level error "'$PROJECT_DIR' already exists"
    exit 1
  fi
  cp -r "$TEMPLATE_DIR" "$PROJECT_DIR"
  cd "$PROJECT_DIR"
else
  PROJECT_DIR="$(pwd)"
  cp -rn "$TEMPLATE_DIR/." "$PROJECT_DIR/"
fi

# --- Language-specific options ---
if [[ "$LANG" == "python" ]]; then
  if gum confirm "Initialize uv environment?"; then
    if ! command -v uv &>/dev/null; then
      gum log --level error "uv not found. Install: curl -LsSf https://astral.sh/uv/install.sh | sh"
      exit 1
    fi
    uv init --no-readme -q 2>/dev/null || true
    uv venv -q
    gum log --level info "uv environment created (.venv)"
  fi
fi

# --- Git init ---
if [[ ! -d ".git" ]]; then
  git init -q
fi
git add .
git commit -q -m "chore: init $LANG project from template" 2>/dev/null || true

gum log --level info "Done. Project ready at: $PROJECT_DIR"
