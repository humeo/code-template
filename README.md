# code-template

A personal project scaffolding tool. Run one command to get a new project with git, `.gitignore`, and language-specific tooling set up.

## Usage

```bash
uv run --project /path/to/code-template /path/to/code-template/scripts/new_project.py
```

Or add an alias to `~/.zshrc`:

```bash
alias new-project="uv run --project /Users/koltenluca/code/code-template /Users/koltenluca/code/code-template/scripts/new_project.py"
```

Then just run:

```bash
new-project
```

## What it does

Interactive TUI that asks:

1. **Language** — python, typescript, or go
2. **Where** — new subdirectory or current directory
3. **Language-specific setup**:
   - Python: `uv init` + `uv venv`
   - TypeScript: `bun init` + installs `typescript` and `@types/node`
   - Go: `go mod init` with your module name

Every project gets:
- `.gitignore` tailored to the language
- `.claude/.gitignore` (ignores all Claude local files)
- Git initialized with an initial commit

## Adding a new language

1. Create `templates/<lang>/` with at least a `.gitignore` and `.claude/.gitignore` (contents: `*`)
2. Optionally add a `setup_<lang>` function in `scripts/new_project.py` and register it in `LANG_SETUP`

## Requirements

- Python 3.12+
- [uv](https://docs.astral.sh/uv/)
- [bun](https://bun.sh) (for TypeScript projects)
- [go](https://go.dev/dl) (for Go projects)
