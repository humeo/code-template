#!/usr/bin/env python3
"""Interactive project initializer."""

import shutil
import subprocess
import sys
from pathlib import Path

import questionary
from questionary import Style
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

TEMPLATES_DIR = Path(__file__).parent.parent / "templates"

console = Console()

STYLE = Style([
    ("qmark", "fg:#00d7ff bold"),
    ("question", "bold"),
    ("answer", "fg:#00d7ff bold"),
    ("pointer", "fg:#00d7ff bold"),
    ("highlighted", "fg:#00d7ff bold"),
    ("selected", "fg:#00d7ff"),
    ("separator", "fg:#555555"),
    ("instruction", "fg:#555555"),
])


def run(cmd: list[str], cwd: Path | None = None) -> None:
    subprocess.run(cmd, cwd=cwd, check=True, capture_output=True)


def copy_template(template_dir: Path, dest: Path) -> None:
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
        pass


def setup_python(project_dir: Path) -> None:
    if not questionary.confirm("Initialize uv environment?", default=True, style=STYLE).ask():
        return
    if not shutil.which("uv"):
        console.print("[red]Error:[/red] uv not found. Install: curl -LsSf https://astral.sh/uv/install.sh | sh")
        sys.exit(1)
    with console.status("[cyan]Setting up uv environment...[/cyan]"):
        if not (project_dir / "pyproject.toml").exists():
            run(["uv", "init", "--no-readme", "-q"], cwd=project_dir)
        run(["uv", "venv", "-q"], cwd=project_dir)
    console.print("  [green]✓[/green] uv environment created [dim](.venv)[/dim]")


LANG_SETUP = {
    "python": setup_python,
}


def main() -> None:
    console.print(Panel(
        Text("new-project", style="bold cyan", justify="center"),
        subtitle="[dim]project initializer[/dim]",
        border_style="cyan",
        padding=(0, 4),
    ))

    langs = sorted(p.name for p in TEMPLATES_DIR.iterdir() if p.is_dir())
    if not langs:
        console.print("[red]No templates found.[/red]")
        sys.exit(1)

    lang = questionary.select("Select language", choices=langs, style=STYLE).ask()
    if not lang:
        sys.exit(0)

    mode = questionary.select(
        "Where to initialize?",
        choices=["New subdirectory", "Current directory"],
        style=STYLE,
    ).ask()
    if not mode:
        sys.exit(0)

    cwd = Path.cwd()

    if mode == "New subdirectory":
        name = questionary.text("Project name", style=STYLE).ask()
        if not name:
            sys.exit(0)
        project_dir = cwd / name
        if project_dir.exists():
            console.print(f"[red]Error:[/red] '{project_dir}' already exists")
            sys.exit(1)
        project_dir.mkdir()
    else:
        project_dir = cwd

    with console.status("[cyan]Copying template...[/cyan]"):
        copy_template(TEMPLATES_DIR / lang, project_dir)
    console.print("  [green]✓[/green] Template copied")

    if lang in LANG_SETUP:
        LANG_SETUP[lang](project_dir)

    with console.status("[cyan]Initializing git...[/cyan]"):
        git_init_commit(project_dir, lang)
    console.print("  [green]✓[/green] Git initialized")

    console.print(f"\n[bold green]Done![/bold green] Project ready at: [cyan]{project_dir}[/cyan]")


if __name__ == "__main__":
    main()
