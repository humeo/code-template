#!/usr/bin/env python3
"""Interactive project initializer."""

import shutil
import subprocess
import sys
from pathlib import Path

import questionary

TEMPLATES_DIR = Path(__file__).parent.parent / "templates"


def run(cmd: list[str], cwd: Path | None = None) -> None:
    subprocess.run(cmd, cwd=cwd, check=True, capture_output=True)


def copy_template(template_dir: Path, dest: Path) -> None:
    """Copy template into dest, skipping existing files."""
    for src in template_dir.rglob("*"):
        rel = src.relative_to(template_dir)
        dst = dest / rel
        if src.is_dir():
            dst.mkdir(parents=True, exist_ok=True)
        elif not dst.exists():
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)


def git_init_commit(project_dir: Path, lang: str) -> None:
    if not (project_dir / ".git").exists():
        run(["git", "init", "-q"], cwd=project_dir)
    run(["git", "add", "."], cwd=project_dir)
    try:
        run(["git", "commit", "-q", "-m", f"chore: init {lang} project from template"], cwd=project_dir)
    except subprocess.CalledProcessError:
        pass  # nothing to commit


def setup_python(project_dir: Path) -> None:
    if not questionary.confirm("Initialize uv environment?", default=True).ask():
        return
    if not shutil.which("uv"):
        print("Error: uv not found. Install: curl -LsSf https://astral.sh/uv/install.sh | sh")
        sys.exit(1)
    run(["uv", "init", "--no-readme", "-q"], cwd=project_dir)
    run(["uv", "venv", "-q"], cwd=project_dir)
    print("  uv environment created (.venv)")


LANG_SETUP = {
    "python": setup_python,
}


def main() -> None:
    langs = sorted(p.name for p in TEMPLATES_DIR.iterdir() if p.is_dir())
    if not langs:
        print("No templates found.")
        sys.exit(1)

    lang = questionary.select("Select language", choices=langs).ask()
    if not lang:
        sys.exit(0)

    mode = questionary.select(
        "Where to initialize?",
        choices=["New subdirectory", "Current directory"],
    ).ask()
    if not mode:
        sys.exit(0)

    cwd = Path.cwd()

    if mode == "New subdirectory":
        name = questionary.text("Project name").ask()
        if not name:
            sys.exit(0)
        project_dir = cwd / name
        if project_dir.exists():
            print(f"Error: '{project_dir}' already exists")
            sys.exit(1)
        project_dir.mkdir()
    else:
        project_dir = cwd

    copy_template(TEMPLATES_DIR / lang, project_dir)

    if lang in LANG_SETUP:
        LANG_SETUP[lang](project_dir)

    git_init_commit(project_dir, lang)
    print(f"\nDone. Project ready at: {project_dir}")


if __name__ == "__main__":
    main()
