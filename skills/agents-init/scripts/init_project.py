#!/usr/bin/env python3
"""Create the agents-init v5 project skeleton without overwriting files."""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


class InitError(Exception):
    """Expected initialization failure."""


@dataclass(frozen=True)
class Inputs:
    project: Path
    name: str
    slug: str
    project_type: tuple[str, ...]
    vcs: str
    stack: tuple[str, ...]
    runtime: str
    agent_cli: tuple[str, ...]


def split_csv(value: str) -> tuple[str, ...]:
    items = tuple(part.strip() for part in value.split(",") if part.strip())
    if not items:
        raise argparse.ArgumentTypeError("expected at least one non-empty value")
    return items


def slugify(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    if not slug:
        raise InitError("--name needs an ASCII --slug override")
    return slug


def json_text(value: object) -> str:
    return json.dumps(value, ensure_ascii=False, indent=2) + "\n"


def files_for(inputs: Inputs) -> dict[Path, str]:
    profile = {
        "$schema": "https://skill.sakanano.moe/skills/agents-init/project.schema.json",
        "schema_version": "1.0",
        "initializer_version": "5.0.0",
        "name": inputs.name,
        "profile": {
            "project_type": list(inputs.project_type),
            "vcs": inputs.vcs,
            "stack": list(inputs.stack),
            "runtime": inputs.runtime,
            "agent_cli": list(inputs.agent_cli),
        },
        "runtime": {
            "skill": "project-runtime",
            "required": True,
            "commit_policy": "explicit",
            "push_policy": "explicit",
        },
        "opinion": {
            "provider": None,
            "project_overlay": "OPINION.md",
            "strict_mode": "smart",
        },
        "capabilities": {
            "plugin_roots": [".agents"],
            "plugin_dirs": [],
            "skill_roots": [".agents/skills"],
            "mcp_sources": [".agents/mcp.json"],
            "destination_skill_root": ".agents/skills",
            "destination_mcp": ".agents/mcp.json",
        },
        "work": {"task": None, "case": None},
        "privacy": {"forbidden_default_reads": [], "generated_outputs": []},
    }
    agents = f"""# {inputs.name} — Agent execution entry

## Project Profile

- Type: {', '.join(inputs.project_type)}
- VCS: {inputs.vcs}
- Stack: {', '.join(inputs.stack)}
- Runtime: {inputs.runtime}
- Agent clients: {', '.join(inputs.agent_cli)}

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
"""
    route = """# Agent route

Read `AGENTS.md` and follow its Project Profile. Load `project-runtime` for project management. Load the configured Opinion provider independently for guidance and review.
"""
    return {
        Path("AGENTS.md"): agents,
        Path("AGENT.RULES.md"): """# Project-specific rules

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
""",
        Path("OPINION.md"): """# Project Opinion overlay

No project-specific Opinion rules have been confirmed.

Personal global and scenario rules belong to the user's private Opinion authority. Configure its provider in `.agents/moe.sakanano.project-runtime/project.json`; do not copy those rules into a public project template.
""",
        Path("CLAUDE.md"): route,
        Path("AGENT.md"): route,
        Path(".agents/plugin.json"): json_text({
            "$schema": "https://agent-plugins.org/schemas/1.0.0/plugin.schema.json",
            "name": inputs.slug,
            "version": "0.1.0",
            "description": "Project-local portable Agent capabilities.",
        }),
        Path(".agents/mcp.json"): json_text({
            "$schema": "https://agent-plugins.org/schemas/1.0.0/mcp.schema.json",
            "mcpServers": {},
        }),
        Path(".agents/moe.sakanano.project-runtime/project.json"): json_text(profile),
        Path(".agents/skills/.gitkeep"): "",
        Path(".agent-doc/plan.md"): "# Plan\n\nNo active multi-step plan.\n",
        Path(".agent-doc/progress.md"): "# Progress\n\nNo active Task or Case. Project work state is managed by `project-runtime` using the configured project subsystem.\n",
        Path(".agent-doc/chat-summary.md"): """# Chat summary

## Pending assumptions

None.

## Unresolved conflicts

None.

## Opinion evolution candidates

None. Submit candidates through the configured Opinion provider; do not promote them here.
""",
        Path("docs/refs/README.md"): "# References\n\nPlace durable task references here when the project contract requires them.\n",
        Path("docs/drafts/.gitkeep"): "",
    }


def validate_root(path: Path) -> Path:
    root = path.expanduser().resolve()
    if not root.exists() or not root.is_dir():
        raise InitError(f"project directory does not exist: {root}")
    return root


def plan_writes(root: Path, files: dict[Path, str]) -> tuple[list[Path], list[Path]]:
    create: list[Path] = []
    collisions: list[Path] = []
    for relative in sorted(files, key=str):
        destination = root / relative
        (collisions if destination.exists() else create).append(relative)
    return create, collisions


def apply_writes(root: Path, files: dict[Path, str], create: Iterable[Path]) -> None:
    for relative in create:
        destination = root / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(files[relative], encoding="utf-8", newline="\n")


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description=__doc__)
    result.add_argument("--project", type=Path, required=True)
    result.add_argument("--name", required=True)
    result.add_argument("--slug")
    result.add_argument("--project-type", type=split_csv, required=True)
    result.add_argument("--vcs", required=True)
    result.add_argument("--stack", type=split_csv, required=True)
    result.add_argument("--runtime", required=True)
    result.add_argument("--agent-cli", type=split_csv, required=True)
    result.add_argument("--apply", action="store_true", help="write non-colliding files")
    result.add_argument("--output", choices=("text", "json"), default="text")
    return result


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    try:
        root = validate_root(args.project)
        slug = args.slug or slugify(args.name)
        if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", slug):
            raise InitError("--slug must be lowercase ASCII kebab-case")
        inputs = Inputs(root, args.name.strip(), slug, args.project_type, args.vcs, args.stack, args.runtime, args.agent_cli)
        if not inputs.name:
            raise InitError("--name must not be empty")
        files = files_for(inputs)
        create, collisions = plan_writes(root, files)
        if args.apply:
            apply_writes(root, files, create)
        result = {
            "ok": not collisions,
            "applied": args.apply,
            "create": [str(path) for path in create],
            "preserved_collisions": [str(path) for path in collisions],
        }
        if args.output == "json":
            print(json_text(result), end="")
        else:
            print(("Applied" if args.apply else "Dry-run") + f": {len(create)} create, {len(collisions)} preserved collision(s)")
            for path in create:
                print(f"  create {path}")
            for path in collisions:
                print(f"  preserve {path}")
        return 1 if collisions else 0
    except InitError as error:
        if args.output == "json":
            print(json_text({"ok": False, "error": str(error)}), end="")
        else:
            print(f"error: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
