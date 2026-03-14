<div align="center">

# code-template

### Starting a new project means manually running init commands, creating .gitignore files, and setting up git every single time. This fixes that.

</div>

---

> [!NOTE]
> **What this tool touches:**
> - Runs `git init`, `uv init`, `bun init`, or `go mod init` in your target directory
> - Creates files in the new project (`.gitignore`, `tsconfig.json`, `.claude/.gitignore`, etc.)
> - No network calls, no telemetry, nothing outside the project directory
>
> **To disable:** remove the shell alias. **To uninstall:** delete the repo.

```bash
alias new-project="uv run --project /path/to/code-template /path/to/code-template/scripts/new_project.py"
```

---

## The Problem

Every language ecosystem has its own scaffolder — `cargo new`, `bun init`, `uv init`. But none of them give you a consistent baseline: no `.gitignore`, no git history, no Claude-local file exclusions, no standard structure. You end up doing the same five manual steps every time you start something new.

If you've used `cookiecutter` or `create-react-app`, you know the idea. This is cross-language, opinionated for a personal workflow, and runs in a single interactive TUI.

---

## Install

**Prerequisites:**

- Python 3.12+ and [uv](https://docs.astral.sh/uv/)
- [bun](https://bun.sh) — for TypeScript projects
- [go](https://go.dev/dl) — for Go projects

**Setup:**

```bash
git clone https://github.com/you/code-template
cd code-template
uv sync
```

Add to `~/.zshrc` (or `~/.bashrc`):

```bash
alias new-project="uv run --project /path/to/code-template /path/to/code-template/scripts/new_project.py"
source ~/.zshrc
```

Then run `new-project` from any directory.

---

## See It Work

```
$ new-project

╭──────────────────╮
│   new-project    │
│  project initializer  │
╰──────────────────╯

? Select language  › python / typescript / go
? Where to initialize?  › New subdirectory / Current directory
? Project name  › my-app

  ✓ Template copied
  ✓ uv environment created (.venv)
  ✓ Git initialized

Done! Project ready at: /Users/you/my-app
```

Your new project has a `.gitignore`, a `.claude/.gitignore`, and an initial git commit — ready to code.

---

## How It Works

The TUI (built with [questionary](https://github.com/tmbo/questionary) + [rich](https://github.com/Textualize/rich)) asks three questions, copies the matching template, runs the language-specific init command, and commits everything.

<details>
<summary><b>Language setup details</b></summary>

| Language   | What runs                                        | What you get                          |
|------------|--------------------------------------------------|---------------------------------------|
| Python     | `uv init --no-readme` + `uv venv`               | `pyproject.toml`, `.venv`             |
| TypeScript | `bun init -y` + `bun add -d typescript @types/node` | `package.json`, `tsconfig.json`   |
| Go         | `go mod init <module-name>`                      | `go.mod` (module name prompted)       |

Every project also gets:
- `.gitignore` tailored to the language
- `.claude/.gitignore` (ignores all Claude local files — `*`)
- `git init` + initial commit: `chore: init <lang> project from template`

</details>

<details>
<summary><b>Project structure</b></summary>

```
code-template/
├── scripts/
│   └── new_project.py     # TUI entrypoint
├── templates/
│   ├── python/            # .gitignore, .claude/.gitignore
│   ├── typescript/        # .gitignore, .claude/.gitignore, tsconfig.json
│   └── go/                # .gitignore, .claude/.gitignore
└── pyproject.toml
```

</details>

---

## Adding a Language

1. Create `templates/<lang>/` with at least `.gitignore` and `.claude/.gitignore` (contents: `*`)
2. Add a `setup_<lang>(project_dir: Path) -> None` function in `scripts/new_project.py`
3. Register it in the `LANG_SETUP` dict

---

## FAQ

**Does it work with existing directories?**
Yes — choose "Current directory" in the TUI. It won't overwrite files that already exist.

**Can I customize the templates?**
Yes — edit anything under `templates/<lang>/`. Files are copied as-is.

**What if I don't have bun/go installed?**
The tool checks for the required binary before running setup and exits with an install hint if it's missing.
