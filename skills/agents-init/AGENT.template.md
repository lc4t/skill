# AGENT.template.md v5

> Scope: portable project initialization and migration. Runtime project management and Opinion rules are external capabilities.

## 1. Design contract

The generated project separates four concerns:

1. **Project contract** — `AGENTS.md` and the machine-readable Project Profile describe the repository.
2. **Project runtime** — one external `project-runtime` Skill manages work containers, capability routing, validation, progress, and Git.
3. **Guidance/review** — an independent Opinion provider resolves global, scenario, and project rules.
4. **Delivery capabilities** — domain Skills and deterministic Tools create or inspect artifacts.

The template must stay generic. Never publish personal preferences, organization data, credentials, private filesystem paths, or copied private Skills.

## 2. Standard layout

```text
<project>/
├── AGENTS.md
├── AGENT.RULES.md
├── OPINION.md
├── CLAUDE.md
├── AGENT.md
├── .agents/
│   ├── plugin.json
│   ├── mcp.json
│   ├── skills/
│   └── moe.sakanano.project-runtime/
│       └── project.json
├── .agent-doc/
│   ├── plan.md
│   ├── progress.md
│   └── chat-summary.md
└── docs/
    ├── refs/README.md
    └── drafts/.gitkeep
```

Agent Plugins 1.0 portable files live directly under `.agents/`: `plugin.json`, `skills/`, and `mcp.json`. The reverse-domain directory contains the client extension Project Profile so it cannot collide with future standard components.

## 3. Project Profile

Generate `.agents/moe.sakanano.project-runtime/project.json`:

```json
{
  "$schema": "https://skill.sakanano.moe/skills/agents-init/project.schema.json",
  "schema_version": "1.0",
  "initializer_version": "5.1.0",
  "name": "PROJECT_NAME",
  "profile": {
    "project_type": ["PROJECT_TYPE"],
    "vcs": "VCS",
    "stack": ["STACK"],
    "runtime": "RUNTIME",
    "agent_cli": ["AGENT_CLI"]
  },
  "runtime": {
    "skill": "project-runtime",
    "required": true,
    "commit_policy": "explicit",
    "push_policy": "explicit"
  },
  "opinion": {
    "provider": null,
    "project_overlay": "OPINION.md",
    "strict_mode": "smart"
  },
  "capabilities": {
    "plugin_roots": [".agents"],
    "plugin_dirs": [],
    "skill_roots": [".agents/skills"],
    "mcp_sources": [".agents/mcp.json"],
    "native_mcp_sources": [],
    "credential_env_file": null,
    "mcp_client_policy": {},
    "destination_skill_root": ".agents/skills",
    "destination_mcp": ".agents/mcp.json"
  },
  "work": {
    "task": null,
    "case": null
  },
  "privacy": {
    "forbidden_default_reads": [],
    "generated_outputs": []
  }
}
```

`$schema` is the public Project Profile contract. Tools must validate `schema_version` independently from `initializer_version`. Use JSON arrays for multi-valued fields. Missing integrations are `null` or empty arrays; do not invent commands.

## 4. AGENTS.md template

```markdown
# PROJECT_NAME — Agent execution entry

## Project Profile

- Type: PROJECT_TYPE
- VCS: VCS
- Stack: STACK
- Runtime: RUNTIME
- Agent clients: AGENT_CLI

Machine-readable authority: `.agents/moe.sakanano.project-runtime/project.json`.

## Session entry

1. Load `project-runtime` as the only project-management Skill.
2. Let it read the Project Profile, current Git state, and only the entry files required by the current task.
3. Use domain Skills for concrete artifacts and deterministic Tools for state changes.
4. If an Opinion provider is configured, request guidance before implementation and a check before delivery.

## Boundaries

- `agents-init` only creates or migrates this skeleton.
- `project-runtime` owns Task/Case selection, file placement, progress, validation orchestration, capability management, and Git handoff.
- Opinion guides and reviews deliverables; it does not manage project lifecycle.
- Domain Skills do not create unrelated Tasks, edit root progress, self-modify, or commit autonomously.
- Preserve unrelated changes. Push, publish, merge, delete, and destructive migration require explicit approval.

## Project-specific entry points

- Commands: TODO
- Tests: TODO
- Build: TODO
- Architecture/docs: TODO
- Privacy or forbidden paths: none declared
```

Keep this entry short. Put durable project-specific constraints in `AGENT.RULES.md`; do not copy the full runtime workflow into either file.

## 5. Other generated files

### AGENT.RULES.md

```markdown
# Project-specific rules

This file contains only durable constraints unique to this repository. The `project-runtime` Skill owns the generic lifecycle.

## Commands and validation

- Setup: TODO
- Test: TODO
- Build: TODO

## File placement and generated outputs

- Source authority: TODO
- Generated outputs: TODO

## Privacy and external systems

- Forbidden default reads: none declared
- External writes requiring approval: all, unless explicitly configured
```

### OPINION.md

```markdown
# Project Opinion overlay

No project-specific Opinion rules have been confirmed.

Personal global and scenario rules belong to the user's private Opinion authority. Configure its provider in `.agents/moe.sakanano.project-runtime/project.json`; do not copy those rules into a public project template.
```

### CLAUDE.md and AGENT.md

```markdown
# Agent route

Read `AGENTS.md` and follow its Project Profile. Load `project-runtime` for project management. Load the configured Opinion provider independently for guidance and review.
```

### Process placeholders

`.agent-doc/plan.md`:

```markdown
# Plan

No active multi-step plan.
```

`.agent-doc/progress.md`:

```markdown
# Progress

No active Task or Case. Project work state is managed by `project-runtime` using the configured project subsystem.
```

`.agent-doc/chat-summary.md`:

```markdown
# Chat summary

## Pending assumptions

None.

## Unresolved conflicts

None.

## Opinion evolution candidates

None. Submit candidates through the configured Opinion provider; do not promote them here.
```

## 6. Agent Plugin placeholders

`.agents/plugin.json`:

```json
{
  "$schema": "https://agent-plugins.org/schemas/1.0.0/plugin.schema.json",
  "name": "PROJECT_SLUG",
  "version": "0.1.0",
  "description": "Project-local portable Agent capabilities."
}
```

`.agents/mcp.json`:

```json
{
  "$schema": "https://agent-plugins.org/schemas/1.0.0/mcp.schema.json",
  "mcpServers": {}
}
```

Leave `.agents/skills/` empty until `project-runtime` imports a selected Skill. Never initialize secret-bearing MCP configuration from a public template.

## 7. Initialization and migration

### New project

1. Inspect facts with read-only commands.
2. Fill evidenced Profile values and leave unresolved commands as `TODO`.
3. Dry-run the initializer and show collisions.
4. Apply after approval.
5. Parse JSON and verify routers.

### Existing project

1. Preserve existing files and identify their authority.
2. Compare responsibilities, not filenames, with v5.
3. Create the machine Profile first.
4. Reduce duplicate Agent entry prose only after `project-runtime` is available.
5. Keep historical Tasks/Cases and capability sources intact; inventory them later with `project-runtime`.
6. Move personal Opinion content only to a private authority with explicit approval.

## 8. Acceptance criteria

- Every generated JSON document parses.
- `AGENTS.md` and router files point to the same Project Profile and runtime.
- Exactly one Skill owns project management: `project-runtime`.
- Opinion is configured as an independent provider or explicitly absent.
- No personal rule content, credentials, tokens, private paths, or private Skill contents enter the public template.
- Existing files are preserved unless the user approved each replacement.
