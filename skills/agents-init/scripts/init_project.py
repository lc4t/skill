#!/usr/bin/env python3
"""Create the agents-init v5 project skeleton without overwriting files."""

from __future__ import annotations

import argparse
import json
import os
import re
import stat
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
        "initializer_version": "5.1.0",
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
            "native_mcp_sources": [],
            "credential_env_file": None,
            "mcp_client_policy": {},
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
        current = root
        for part in relative.parts[:-1]:
            current /= part
            try:
                metadata = current.lstat()
            except FileNotFoundError:
                break
            if stat.S_ISLNK(metadata.st_mode):
                raise InitError(f"refusing symlinked parent: {current.relative_to(root)}")
            if not stat.S_ISDIR(metadata.st_mode):
                raise InitError(f"parent is not a directory: {current.relative_to(root)}")
        destination = root / relative
        try:
            destination.lstat()
            exists = True
        except FileNotFoundError:
            exists = False
        (collisions if exists else create).append(relative)
    return create, collisions


def _open_parent(root_fd: int, relative: Path, created_dirs: list[Path]) -> int:
    descriptor = os.dup(root_fd)
    traversed = Path()
    flags = os.O_RDONLY | getattr(os, "O_DIRECTORY", 0) | getattr(os, "O_NOFOLLOW", 0)
    try:
        for part in relative.parts[:-1]:
            traversed /= part
            try:
                child = os.open(part, flags, dir_fd=descriptor)
            except FileNotFoundError:
                os.mkdir(part, mode=0o755, dir_fd=descriptor)
                created_dirs.append(traversed)
                child = os.open(part, flags, dir_fd=descriptor)
            except OSError as exc:
                raise InitError(f"unsafe parent path {traversed}: {exc}") from exc
            os.close(descriptor)
            descriptor = child
        return descriptor
    except Exception:
        os.close(descriptor)
        raise


def _write_exclusive(parent_fd: int, name: str, payload: bytes) -> None:
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0)
    descriptor = os.open(name, flags, 0o644, dir_fd=parent_fd)
    try:
        offset = 0
        while offset < len(payload):
            written = os.write(descriptor, payload[offset:])
            if written <= 0:
                raise OSError("short write")
            offset += written
        os.fsync(descriptor)
        os.fchmod(descriptor, 0o644)
    finally:
        os.close(descriptor)


def _open_existing_parent(root_fd: int, relative: Path) -> int:
    descriptor = os.dup(root_fd)
    flags = os.O_RDONLY | getattr(os, "O_DIRECTORY", 0) | getattr(os, "O_NOFOLLOW", 0)
    try:
        for part in relative.parts[:-1]:
            child = os.open(part, flags, dir_fd=descriptor)
            os.close(descriptor)
            descriptor = child
        return descriptor
    except Exception:
        os.close(descriptor)
        raise


def _unlink_relative(root_fd: int, relative: Path, *, directory: bool = False) -> None:
    parent_fd = _open_existing_parent(root_fd, relative)
    try:
        if directory:
            os.rmdir(relative.name, dir_fd=parent_fd)
        else:
            os.unlink(relative.name, dir_fd=parent_fd)
    finally:
        os.close(parent_fd)


def apply_writes(root: Path, files: dict[Path, str], create: Iterable[Path]) -> None:
    planned = list(create)
    rendered = {relative: files[relative].encode("utf-8") for relative in planned}
    created_files: list[Path] = []
    created_dirs: list[Path] = []
    root_fd = os.open(root, os.O_RDONLY | getattr(os, "O_DIRECTORY", 0) | getattr(os, "O_NOFOLLOW", 0))
    try:
        for relative in planned:
            parent_fd = _open_parent(root_fd, relative, created_dirs)
            try:
                _write_exclusive(parent_fd, relative.name, rendered[relative])
                created_files.append(relative)
            finally:
                os.close(parent_fd)
    except Exception as exc:
        cleanup_errors: list[str] = []
        for relative in reversed(created_files):
            try:
                _unlink_relative(root_fd, relative)
            except OSError as cleanup_exc:
                cleanup_errors.append(f"{relative}: {cleanup_exc}")
        for relative in reversed(created_dirs):
            try:
                _unlink_relative(root_fd, relative, directory=True)
            except OSError:
                # A concurrent writer may have added unknown content. Never remove it.
                pass
        detail = f"; rollback incomplete: {', '.join(cleanup_errors)}" if cleanup_errors else ""
        raise InitError(f"initialization rolled back after write failure: {exc}{detail}") from exc
    finally:
        os.close(root_fd)


def apply_migration(
    root: Path,
    files: dict[Path, str],
    create: Iterable[Path],
    replace: Iterable[Path],
    recovery_dir: Path | None,
) -> None:
    create_paths = list(create)
    replace_paths = list(replace)
    if replace_paths and recovery_dir is None:
        raise InitError("--recovery-dir is required when --replace is used")
    recovery = recovery_dir.expanduser().resolve() if recovery_dir is not None else None
    if recovery is not None:
        if recovery == root or root in recovery.parents:
            raise InitError("--recovery-dir must be outside the project root")
        recovery.mkdir(parents=True, exist_ok=True, mode=0o700)
        if recovery.is_symlink() or not recovery.is_dir():
            raise InitError("--recovery-dir must be a real directory")
        conflicts = [path for path in replace_paths if (recovery / path).exists()]
        if conflicts:
            raise InitError("recovery collision: " + ", ".join(str(path) for path in conflicts))

    root_fd = os.open(root, os.O_RDONLY | getattr(os, "O_DIRECTORY", 0) | getattr(os, "O_NOFOLLOW", 0))
    created_files: list[Path] = []
    created_dirs: list[Path] = []
    moved: list[tuple[Path, Path]] = []
    try:
        for relative in replace_paths:
            assert recovery is not None
            original = root / relative
            archived = recovery / relative
            archived.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
            os.replace(original, archived)
            moved.append((archived, original))
        for relative in [*create_paths, *replace_paths]:
            parent_fd = _open_parent(root_fd, relative, created_dirs)
            try:
                _write_exclusive(parent_fd, relative.name, files[relative].encode("utf-8"))
                created_files.append(relative)
            finally:
                os.close(parent_fd)
    except Exception as exc:
        for relative in reversed(created_files):
            try:
                _unlink_relative(root_fd, relative)
            except OSError:
                pass
        for archived, original in reversed(moved):
            if archived.exists() and not original.exists():
                original.parent.mkdir(parents=True, exist_ok=True)
                os.replace(archived, original)
        for relative in reversed(created_dirs):
            try:
                _unlink_relative(root_fd, relative, directory=True)
            except OSError:
                pass
        raise InitError(f"migration rolled back after write failure: {exc}") from exc
    finally:
        os.close(root_fd)


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
    result.add_argument("--mode", choices=("init", "migrate"), default="init")
    result.add_argument("--replace", action="append", default=[], help="known skeleton path to replace in migrate mode")
    result.add_argument("--recovery-dir", type=Path, help="outside-project backup directory required for replacements")
    result.add_argument("--apply", action="store_true", help="create the complete skeleton only when no collision exists")
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
        requested_replace = {Path(value) for value in args.replace}
        if args.mode == "init" and requested_replace:
            raise InitError("--replace is available only in migrate mode")
        unknown_replace = requested_replace - set(files)
        if unknown_replace:
            raise InitError("unknown skeleton path: " + ", ".join(str(path) for path in sorted(unknown_replace, key=str)))
        missing_replace = requested_replace - set(collisions)
        if missing_replace:
            raise InitError("--replace path does not exist: " + ", ".join(str(path) for path in sorted(missing_replace, key=str)))
        replace = [path for path in collisions if path in requested_replace]
        preserved = [path for path in collisions if path not in requested_replace]
        if args.mode == "init":
            applied = bool(args.apply and not collisions)
            if applied:
                apply_writes(root, files, create)
            ok = not collisions
        else:
            applied = bool(args.apply)
            if applied:
                apply_migration(root, files, create, replace, args.recovery_dir)
            ok = True
        result = {
            "ok": ok,
            "mode": args.mode,
            "applied": applied,
            "create": [str(path) for path in create],
            "replace": [str(path) for path in replace],
            "preserved_collisions": [str(path) for path in preserved],
        }
        if args.output == "json":
            print(json_text(result), end="")
        else:
            label = "Applied" if applied else ("Blocked" if args.mode == "init" and args.apply and collisions else "Dry-run")
            print(label + f": {len(create)} create, {len(replace)} replace, {len(preserved)} preserved collision(s)")
            for path in create:
                print(f"  create {path}")
            for path in replace:
                print(f"  replace {path}")
            for path in preserved:
                print(f"  preserve {path}")
        return 0 if ok else 1
    except InitError as error:
        if args.output == "json":
            print(json_text({"ok": False, "error": str(error)}), end="")
        else:
            print(f"error: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
