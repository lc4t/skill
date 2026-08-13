---
name: agents-init
description: Initialize or migrate a repository to the agents-init v5 project skeleton. Use when the user asks to initialize Agent collaboration, create AGENTS.md, add the Project Profile, or migrate an older agents-init layout. This skill creates structure only; project-runtime owns ongoing project management and Opinion owns guidance/review.
metadata:
  author: lc4t
  version: "5.0.1"
---

# Agents Init

## Purpose

Create a small, portable project contract that any compatible Agent can discover. This skill owns **initialization and versioned skeleton migration only**.

Keep these boundaries strict:

- `agents-init`: creates the project skeleton and Project Profile;
- `project-runtime`: manages ongoing work, Task/Case state, capabilities, validation, progress, and Git handoff;
- Opinion provider: supplies independent guidance and review rules;
- domain skills: create or inspect concrete deliverables.

Never embed a user's personal rules, credentials, private paths, MCP secrets, or private Skill contents in this public template.

## Required reference

Read [AGENT.template.md](AGENT.template.md) completely before initializing or migrating a project. It is the v5 skeleton contract and migration guide.

## Workflow

1. Inspect the repository root, existing Agent entry files, Git state, project manifests, and likely build/test commands.
2. Infer fields that have direct evidence. Mark uncertain values; ask once only when a missing choice materially changes the generated contract.
3. Show the proposed file plan and collisions.
4. After user approval, run the bundled initializer with `--apply`, or create the same files manually when the script cannot run.
5. Any collision blocks the whole apply operation. Preserve every existing file; migrations edit only files the user selected after reviewing a diff.
6. Parse generated JSON, check entry-file routing, and report remaining placeholders.

Example dry-run:

```bash
python3 scripts/init_project.py --project /path/to/project \
  --name example --project-type code --vcs github \
  --stack python --runtime local --agent-cli codex
```

Apply only after reviewing the plan:

```bash
python3 scripts/init_project.py --project /path/to/project \
  --name example --project-type code --vcs github \
  --stack python --runtime local --agent-cli codex --apply
```

## Output contract

The v5 baseline is:

```text
AGENTS.md
AGENT.RULES.md
OPINION.md
CLAUDE.md
AGENT.md
.agents/
├── plugin.json
├── mcp.json
├── skills/
└── moe.sakanano.project-runtime/project.json
.agent-doc/
├── plan.md
├── progress.md
└── chat-summary.md
docs/
├── refs/README.md
└── drafts/.gitkeep
```

`AGENTS.md` is the project execution entry. `CLAUDE.md` and `AGENT.md` are short routers. `OPINION.md` is intentionally an empty project overlay with instructions; personal global rules remain in the user's private Opinion authority and are never copied into this template.

## Migration rules

- Detect the old version from explicit markers; do not infer that an unfamiliar layout is v4.
- Preserve project facts and local constraints.
- Remove duplicated lifecycle prose from Agent entry files only after `project-runtime` is available.
- Move personal/global rule content to the user's private authority only with explicit approval; never commit it to this public template.
- Do not delete old Skills, MCP entries, Task data, or progress records. Let `project-runtime` inventory and migrate capabilities after initialization.
- Do not run project work, create Tasks/Cases, evolve Opinion, or commit/push from this skill.

## Completion report

Report generated files, inferred Profile values and evidence, preserved collisions, validation results, and the next required runtime installation step. Stop after initialization or migration is complete.
