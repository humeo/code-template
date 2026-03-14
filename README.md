# code-template

A personal project scaffolding tool. Run one command to spin up a new project with git, `.gitignore`, and language-specific tooling already configured.

## Requirements

- Python 3.12+
- [uv](https://docs.astral.sh/uv/) — Python environment manager
- [bun](https://bun.sh) — for TypeScript projects
- [go](https://go.dev/dl) — for Go projects

## Installation

Add an alias to `~/.zshrc` (or `~/.bashrc`):

```bash
alias new-project="uv run --project /path/to/code-template /path/to/code-template/scripts/new_project.py"
```

Then reload your shell:

```bash
source ~/.zshrc
```

## Usage

```bash
new-project
```

Or run directly without an alias:

```bash
uv run --project /path/to/code-template /path/to/code-template/scripts/new_project.py
```

The interactive TUI will prompt you for:

1. **Language** — `python`, `typescript`, or `go`
2. **Location** — new subdirectory or current directory
3. **Language-specific options** (module name for Go, uv env confirmation for Python)

## What gets created

Every project includes:

- `.gitignore` tailored to the language
- `.claude/.gitignore` (ignores all Claude local files)
- Git repository initialized with an initial commit

Language-specific setup:

| Language   | Tooling                                          |
|------------|--------------------------------------------------|
| Python     | `uv init` + `uv venv` → `.venv`                 |
| TypeScript | `bun init` + `typescript` + `@types/node`        |
| Go         | `go mod init <module-name>`                      |

TypeScript projects also include a `tsconfig.json` targeting ES2022 with strict mode, NodeNext module resolution, and source maps.

## Project Structure

```
code-template/
├── scripts/
│   └── new_project.py     # Main TUI script
├── templates/
│   ├── python/            # Python template files
│   ├── typescript/        # TypeScript template + tsconfig.json
│   └── go/                # Go template files
└── README.md
```

## Adding a New Language

1. Create `templates/<lang>/` with at least a `.gitignore` and `.claude/.gitignore` (contents: `*`)
2. Optionally add a `setup_<lang>(project_dir: Path)` function in `scripts/new_project.py`
3. Register it in the `LANG_SETUP` dict
