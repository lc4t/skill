#!/usr/bin/env python3
"""使用 agents-init v5.2 中文模板安全创建项目骨架。"""

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


INITIALIZER_VERSION = "5.2.0"
PLUGIN_ROOT = Path(__file__).resolve().parents[3]
TEMPLATE_PATH = Path(__file__).resolve().parents[1] / "AGENT.template.md"
TEMPLATE_PATTERN = re.compile(
    r"<!-- agents-init:template (?P<name>[^ ]+) -->\n"
    r"```markdown\n(?P<body>.*?)```\n"
    r"<!-- /agents-init:template -->",
    re.DOTALL,
)
REQUIRED_TEMPLATES = {
    "AGENTS.md",
    "AGENT.RULES.md",
    "OPINION.md",
    "ROUTE.md",
    ".agent-doc/plan.md",
    ".agent-doc/progress.md",
    ".agent-doc/chat-summary.md",
    "docs/refs/README.md",
}


class InitError(Exception):
    """Expected initialization failure."""

    def __init__(self, message: str, *, code: str = "invalid-request") -> None:
        super().__init__(message)
        self.code = code


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


def load_templates(path: Path = TEMPLATE_PATH) -> dict[str, str]:
    try:
        source = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        raise InitError(f"无法读取中文模板：{path}", code="template-invalid") from exc
    templates = {match.group("name"): match.group("body") for match in TEMPLATE_PATTERN.finditer(source)}
    missing = sorted(REQUIRED_TEMPLATES - set(templates))
    if missing:
        raise InitError("中文模板缺少生成区块：" + ", ".join(missing), code="template-invalid")
    return templates


def render_template(template: str, replacements: dict[str, str]) -> str:
    rendered = template
    for token, value in replacements.items():
        rendered = rendered.replace(token, value)
    return rendered


def validate_runtime(plugin_root: Path) -> dict[str, str | bool]:
    root = plugin_root.expanduser().resolve()
    required = (
        Path("plugin.json"),
        Path("runtime/project_runtime_config.py"),
        Path("runtime/mcp_server.py"),
        Path("skills/project-runtime/SKILL.md"),
    )
    missing: list[str] = []
    for relative in required:
        candidate = root / relative
        try:
            metadata = candidate.lstat()
        except FileNotFoundError:
            missing.append(str(relative))
            continue
        if stat.S_ISLNK(metadata.st_mode) or not stat.S_ISREG(metadata.st_mode):
            missing.append(str(relative))
    if missing:
        raise InitError(
            "缺少必需的同包 project-runtime 文件：" + ", ".join(missing),
            code="runtime-required",
        )
    try:
        manifest = json.loads((root / "plugin.json").read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise InitError("Plugin manifest 无法解析", code="runtime-required") from exc
    if manifest.get("name") != "agents-init":
        raise InitError("Plugin manifest 必须声明 name=agents-init", code="runtime-required")
    return {
        "available": True,
        "source": "bundled" if root == PLUGIN_ROOT.resolve() else "external",
        "plugin": "agents-init",
    }


def validate_inline(label: str, value: str) -> str:
    if not value.strip():
        raise InitError(f"{label} 不能为空")
    if len(value) > 512 or any(ord(character) < 32 for character in value):
        raise InitError(f"{label} 只能包含单行可打印文本")
    return value.strip()


def files_for(inputs: Inputs, templates: dict[str, str] | None = None) -> dict[Path, str]:
    templates = templates or load_templates()
    profile = {
        "$schema": "https://skill.sakanano.moe/skills/agents-init/project.schema.json",
        "schema_version": "1.0",
        "initializer_version": INITIALIZER_VERSION,
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
            "plugin": "agents-init",
            "distribution": "bundled",
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
    replacements = {
        "PROJECT_NAME": inputs.name,
        "PROJECT_SLUG": inputs.slug,
        "PROJECT_TYPE": ", ".join(inputs.project_type),
        "VCS": inputs.vcs,
        "STACK": ", ".join(inputs.stack),
        "RUNTIME": inputs.runtime,
        "AGENT_CLI": ", ".join(inputs.agent_cli),
    }
    agents = render_template(templates["AGENTS.md"], replacements)
    route = render_template(templates["ROUTE.md"], replacements)
    return {
        Path("AGENTS.md"): agents,
        Path("AGENT.RULES.md"): render_template(templates["AGENT.RULES.md"], replacements),
        Path("OPINION.md"): render_template(templates["OPINION.md"], replacements),
        Path("CLAUDE.md"): route,
        Path("AGENT.md"): route,
        Path(".agents/plugin.json"): json_text({
            "$schema": "https://agent-plugins.org/schemas/1.0.0/plugin.schema.json",
            "name": inputs.slug,
            "version": "0.1.0",
            "description": "项目本地的可移植 Agent 能力包。",
        }),
        Path(".agents/mcp.json"): json_text({
            "$schema": "https://agent-plugins.org/schemas/1.0.0/mcp.schema.json",
            "mcpServers": {},
        }),
        Path(".agents/moe.sakanano.project-runtime/project.json"): json_text(profile),
        Path(".agents/skills/.gitkeep"): "",
        Path(".agent-doc/plan.md"): render_template(templates[".agent-doc/plan.md"], replacements),
        Path(".agent-doc/progress.md"): render_template(templates[".agent-doc/progress.md"], replacements),
        Path(".agent-doc/chat-summary.md"): render_template(templates[".agent-doc/chat-summary.md"], replacements),
        Path("docs/refs/README.md"): render_template(templates["docs/refs/README.md"], replacements),
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
    result.add_argument(
        "--runtime-plugin-root",
        type=Path,
        default=PLUGIN_ROOT,
        help="包含 agents-init 与 project-runtime 的完整 Plugin 根目录",
    )
    result.add_argument("--apply", action="store_true", help="create the complete skeleton only when no collision exists")
    result.add_argument("--output", choices=("text", "json"), default="text")
    return result


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    try:
        root = validate_root(args.project)
        runtime_status = validate_runtime(args.runtime_plugin_root)
        slug = args.slug or slugify(args.name)
        if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", slug):
            raise InitError("--slug must be lowercase ASCII kebab-case")
        inputs = Inputs(
            root,
            validate_inline("--name", args.name),
            slug,
            tuple(validate_inline("--project-type", value) for value in args.project_type),
            validate_inline("--vcs", args.vcs),
            tuple(validate_inline("--stack", value) for value in args.stack),
            validate_inline("--runtime", args.runtime),
            tuple(validate_inline("--agent-cli", value) for value in args.agent_cli),
        )
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
            "runtime": runtime_status,
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
            print(json_text({"ok": False, "code": error.code, "error": str(error)}), end="")
        else:
            print(f"error: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
