#!/usr/bin/env node
import * as p from "@clack/prompts";
import chalk from "chalk";
import { execa } from "execa";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const TEMPLATES_DIR = path.resolve(__dirname, "../templates");
const AI_TOOLS = ["claude", "codex"] as const;

function which(cmd: string): boolean {
  try {
    const result = fs.existsSync(
      (process.env["PATH"] ?? "")
        .split(":")
        .map((p) => path.join(p, cmd))
        .find((p) => {
          try {
            fs.accessSync(p, fs.constants.X_OK);
            return true;
          } catch {
            return false;
          }
        }) ?? ""
    );
    return result;
  } catch {
    return false;
  }
}

function copyTemplate(src: string, dest: string): void {
  for (const entry of fs.readdirSync(src, { withFileTypes: true })) {
    const srcPath = path.join(src, entry.name);
    const destPath = path.join(dest, entry.name);
    if (entry.isDirectory()) {
      fs.mkdirSync(destPath, { recursive: true });
      copyTemplate(srcPath, destPath);
    } else if (!fs.existsSync(destPath)) {
      fs.mkdirSync(path.dirname(destPath), { recursive: true });
      fs.copyFileSync(srcPath, destPath);
    }
  }
}

async function setupPython(projectDir: string): Promise<void> {
  const init = await p.confirm({
    message: "Initialize uv environment?",
    initialValue: true,
  });
  if (p.isCancel(init) || !init) return;
  if (!which("uv")) {
    p.log.error("uv not found. Install: curl -LsSf https://astral.sh/uv/install.sh | sh");
    process.exit(1);
  }
  const s = p.spinner();
  s.start("Setting up uv environment");
  if (!fs.existsSync(path.join(projectDir, "pyproject.toml"))) {
    await execa("uv", ["init", "--no-readme", "-q"], { cwd: projectDir });
  }
  await execa("uv", ["venv", "-q"], { cwd: projectDir });
  s.stop(chalk.green("✓") + " uv environment created " + chalk.dim("(.venv)"));
}

async function setupTypescript(projectDir: string): Promise<void> {
  if (!which("bun")) {
    p.log.error("bun not found. Install: curl -fsSL https://bun.sh/install | bash");
    process.exit(1);
  }
  const s = p.spinner();
  s.start("Initializing bun project");
  await execa("bun", ["init", "-y"], { cwd: projectDir });
  await execa("bun", ["add", "-d", "typescript", "@types/node"], { cwd: projectDir });
  s.stop(chalk.green("✓") + " bun project initialized with typescript + @types/node");
}

async function setupGo(projectDir: string): Promise<void> {
  if (!which("go")) {
    p.log.error("go not found. Install: https://go.dev/dl");
    process.exit(1);
  }
  const dirName = path.basename(projectDir);
  const module = await p.text({
    message: "Go module name",
    initialValue: `github.com/user/${dirName}`,
  });
  if (p.isCancel(module) || !module) return;
  const s = p.spinner();
  s.start("Initializing go module");
  await execa("go", ["mod", "init", module], { cwd: projectDir });
  s.stop(chalk.green("✓") + " go module initialized " + chalk.dim(`(${module})`));
}

async function setupAiDirs(projectDir: string): Promise<void> {
  const tools = await p.multiselect<typeof AI_TOOLS[number]>({
    message: "AI tool directories to create",
    options: AI_TOOLS.map((t) => ({ value: t, label: `.${t}/` })),
    initialValues: [...AI_TOOLS],
    required: false,
  });
  if (p.isCancel(tools)) process.exit(0);
  for (const tool of tools) {
    const toolDir = path.join(projectDir, `.${tool}`);
    fs.mkdirSync(toolDir, { recursive: true });
    const ignore = await p.confirm({
      message: `Add .gitignore to .${tool}/ (ignore its contents)?`,
      initialValue: true,
    });
    if (p.isCancel(ignore)) process.exit(0);
    if (ignore) fs.writeFileSync(path.join(toolDir, ".gitignore"), "*\n");
    p.log.success(`.${tool}/ created` + (ignore ? chalk.dim(" (ignored)") : ""));
  }
}

const LANG_SETUP: Record<string, (dir: string) => Promise<void>> = {
  python: setupPython,
  typescript: setupTypescript,
  go: setupGo,
};

async function main(): Promise<void> {
  console.log();
  p.intro(chalk.cyan("code-template") + chalk.dim(" — project initializer"));

  const langs = fs
    .readdirSync(TEMPLATES_DIR, { withFileTypes: true })
    .filter((e) => e.isDirectory())
    .map((e) => e.name)
    .sort();

  if (langs.length === 0) {
    p.log.error("No templates found.");
    process.exit(1);
  }

  const lang = await p.select({
    message: "Select language",
    options: langs.map((l) => ({ value: l, label: l })),
  });
  if (p.isCancel(lang)) { p.cancel("Cancelled."); process.exit(0); }

  const mode = await p.select({
    message: "Where to initialize?",
    options: [
      { value: "new", label: "New subdirectory" },
      { value: "current", label: "Current directory" },
    ],
  });
  if (p.isCancel(mode)) { p.cancel("Cancelled."); process.exit(0); }

  let projectDir: string;
  if (mode === "new") {
    const name = await p.text({ message: "Project name" });
    if (p.isCancel(name) || !name) { p.cancel("Cancelled."); process.exit(0); }
    projectDir = path.join(process.cwd(), name);
    if (fs.existsSync(projectDir)) {
      p.log.error(`'${projectDir}' already exists`);
      process.exit(1);
    }
    fs.mkdirSync(projectDir);
  } else {
    projectDir = process.cwd();
  }

  const s = p.spinner();
  s.start("Copying template");
  copyTemplate(path.join(TEMPLATES_DIR, lang), projectDir);
  s.stop(chalk.green("✓") + " Template copied");

  if (LANG_SETUP[lang]) await LANG_SETUP[lang]!(projectDir);

  await setupAiDirs(projectDir);

  const gs = p.spinner();
  gs.start("Initializing git");
  if (!fs.existsSync(path.join(projectDir, ".git"))) {
    await execa("git", ["init", "-q"], { cwd: projectDir });
  }
  await execa("git", ["add", "."], { cwd: projectDir });
  try {
    await execa("git", ["commit", "-q", "-m", `chore: init ${lang} project from template`], { cwd: projectDir });
  } catch { /* already committed */ }
  gs.stop(chalk.green("✓") + " Git initialized");

  p.outro(chalk.bold.green("Done!") + " Project ready at: " + chalk.cyan(projectDir));
}

main().catch((e) => {
  p.log.error(String(e));
  process.exit(1);
});
