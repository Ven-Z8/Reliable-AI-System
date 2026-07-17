# Hermes Agent Setup

## Project context

Hermes automatically loads `.hermes.md` from this repository. It is the primary project-specific system instruction.

`AGENTS.md` is included for portability with other coding agents.

## Install project skill and bundle

```bash
bash scripts/install-hermes-assets.sh
```

This installs:

```text
~/.hermes/skills/software-development/reliable-platform-engineering/
~/.hermes/skill-bundles/reliable-platform-dev.yaml
```

The installer refuses to overwrite an existing skill or bundle.

## Start safely

From the Git repository root:

```bash
hermes --worktree --checkpoints
```

Do not use `--yolo`.

Inside Hermes:

```text
/reliable-platform-dev
```

Then:

```text
Read prompts/001-foundation-contracts-and-mock-worker.md and execute it exactly.
```

## Optional SOUL template

`hermes/SOUL.portfolio-engineer.md` is a global personality template, not a project rule file.

Review it before copying:

```bash
cp hermes/SOUL.portfolio-engineer.md ~/.hermes/SOUL.md
```

Do not overwrite an existing `SOUL.md` without reviewing both files.
