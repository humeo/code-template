<div align="center">

# code-template

### Starting a new project means manually running init commands, creating .gitignore files, and setting up git every single time. This fixes that.

</div>

---

> [!NOTE]
> **What this tool touches:**
> - Runs `git init`, `uv init`, `bun init`, or `go mod init` in your target directory
> - Creates files in the new project (`.gitignore`, `tsconfig.json`, `.claude/`, `.codex/`, etc.)
> - No network calls, no telemetry, nothing outside the project directory
>
> **To uninstall:** `npm uninstall -g code-template`

---

## The Problem

Every language ecosystem has its own scaffolder — `cargo new`, `bun init`, `uv init`. But none of them give you a consistent baseline: no `.gitignore`, no git history, no AI tool directories, no standard structure. You end up doing the same five manual steps every time you start something new.

If you've used `cookiecutter` or `create-react-app`, you know the idea. This is cross-language, opinionated for a personal workflow, and runs in a single interactive TUI.

---

## Install

**Run without installing:**

```bash
npx code-template
```

**Install globally:**

```bash
npm install -g code-template
code-template
```

**Install from source:**

```bash
git clone https://github.com/humeo/code-template
cd code-template
npm install -g .
```

**Prerequisites for generated projects:**

- [bun](https://bun.sh) — for TypeScript projects
- [uv](https://docs.astral.sh/uv/) — for Python projects
- [go](https://go.dev/dl) — for Go projects

---

## See It Work

```
$ code-template

  code-template — project initializer

◆ Select language
│  ● python
│  ○ typescript
│  ○ go

◆ Where to initialize?
│  ● New subdirectory
│  ○ Current directory

◆ Project name
│  my-app

✓ Template copied
✓ uv environment created (.venv)

◆ AI tool directories to create
│  ◼ .claude/
│  ◼ .codex/

◆ Add .gitignore to .claude/ (ignore its contents)?
│  ● Yes  ○ No

✓ .claude/ created (ignored)
✓ .codex/ created (ignored)
✓ Git initialized

◇ Done! Project ready at: /Users/you/my-app
```

---

## How It Works

Built with [@clack/prompts](https://github.com/bombshell-dev/clack) + [execa](https://github.com/sindresorhus/execa). Asks a few questions, copies the matching template, runs the language-specific init command, creates AI tool directories, and commits everything.

<details>
<summary><b>Language setup details</b></summary>

| Language   | What runs                                           | What you get                        |
|------------|-----------------------------------------------------|-------------------------------------|
| Python     | `uv init --no-readme` + `uv venv`                  | `pyproject.toml`, `.venv`           |
| TypeScript | `bun init -y` + `bun add -d typescript @types/node` | `package.json`, `tsconfig.json`     |
| Go         | `go mod init <module-name>`                         | `go.mod` (module name prompted)     |

Every project also gets:
- `.gitignore` tailored to the language
- Optional `.claude/` and/or `.codex/` directories, each with an optional `*` gitignore
- `git init` + initial commit: `chore: init <lang> project from template`

</details>

<details>
<summary><b>Project structure</b></summary>

```
code-template/
├── src/
│   └── index.ts        # CLI entrypoint
├── templates/
│   ├── python/         # .gitignore
│   ├── typescript/     # .gitignore, tsconfig.json
│   └── go/             # .gitignore
├── package.json
└── tsconfig.json
```

</details>

---

## Adding a Language

1. Create `templates/<lang>/` with at least a `.gitignore`
2. Add a `setup<Lang>(projectDir: string): Promise<void>` function in `src/index.ts`
3. Register it in the `LANG_SETUP` map

---

## FAQ

**Does it work with existing directories?**
Yes — choose "Current directory" in the TUI. It won't overwrite files that already exist.

**Can I customize the templates?**
Yes — edit anything under `templates/<lang>/`. Files are copied as-is.

**What if I don't have bun/go/uv installed?**
The tool checks for the required binary before running setup and exits with an install hint if it's missing.
