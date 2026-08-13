#!/usr/bin/env python3
"""从可信源码目录确定性导出公开 project-runtime，默认只检查差异。"""

from __future__ import annotations

import argparse
import hashlib
import os
import re
import stat
import tempfile
from pathlib import Path


MAX_FILE_BYTES = 2 * 1024 * 1024
FILES = {
    Path("runtime/mcp_env_launcher.py"): Path("runtime/mcp_env_launcher.py"),
    Path("runtime/mcp_server.py"): Path("runtime/mcp_server.py"),
    Path("runtime/project_runtime_config.py"): Path("runtime/project_runtime_config.py"),
    Path("skills/project-runtime/SKILL.md"): Path("skills/project-runtime/SKILL.md"),
    Path("skills/project-runtime/references/capability-config.md"): Path("skills/project-runtime/references/capability-config.md"),
    Path("skills/project-runtime/agents/openai.yaml"): Path("skills/project-runtime/agents/openai.yaml"),
    Path("tests/test_project_runtime_config.py"): Path("tests/test_project_runtime_config.py"),
}
FORBIDDEN_TEXT = (
    "/Users/",
    "CloudDocs/",
    "global.yml",
    "BEGIN PRIVATE KEY",
)
FORBIDDEN_TOKEN_DIGESTS = {
    "cf16a9a09ccde020f1f1539b54ebcf918bd7b9668cd178f8a2bec15823953654",
    "e0132c30db86c621e78f0d5495730752ac55d692d3d069499306a0fab82416aa",
}


class ExportError(RuntimeError):
    pass


def read_source(path: Path) -> bytes:
    metadata = path.lstat()
    if stat.S_ISLNK(metadata.st_mode) or not stat.S_ISREG(metadata.st_mode):
        raise ExportError(f"拒绝非普通源码文件：{path}")
    if metadata.st_size > MAX_FILE_BYTES:
        raise ExportError(f"源码文件超过大小限制：{path}")
    payload = path.read_bytes()
    try:
        text = payload.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise ExportError(f"源码必须是 UTF-8：{path}") from exc
    hits = [marker for marker in FORBIDDEN_TEXT if marker in text]
    token_digests = {
        hashlib.sha256(token.encode("utf-8")).hexdigest()
        for token in re.findall(r"[A-Za-z0-9._-]+", text)
    }
    if token_digests & FORBIDDEN_TOKEN_DIGESTS:
        hits.append("private-project-identifier")
    if hits:
        raise ExportError(f"源码包含禁止公开的标记 {hits}：{path}")
    return payload


def atomic_write(path: Path, payload: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o755)
    descriptor, temporary_name = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
        os.chmod(temporary, 0o644)
        os.replace(temporary, path)
    finally:
        if temporary.exists():
            temporary.unlink()


def digest(payload: bytes | None) -> str | None:
    return hashlib.sha256(payload).hexdigest() if payload is not None else None


def export(source: Path, destination: Path, *, apply: bool) -> list[str]:
    source = source.expanduser().resolve()
    destination = destination.expanduser().resolve()
    changes: list[str] = []
    rendered: dict[Path, bytes] = {}
    for source_relative, destination_relative in FILES.items():
        payload = read_source(source / source_relative)
        rendered[destination_relative] = payload
        target = destination / destination_relative
        current = target.read_bytes() if target.is_file() and not target.is_symlink() else None
        if digest(current) != digest(payload):
            changes.append(str(destination_relative))
    if apply:
        for relative in changes:
            atomic_write(destination / relative, rendered[Path(relative)])
    return changes


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, required=True, help="project-runtime 源码根目录")
    parser.add_argument("--destination", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--apply", action="store_true", help="应用白名单内的差异；默认只检查")
    args = parser.parse_args()
    try:
        changes = export(args.source, args.destination, apply=args.apply)
    except (OSError, ExportError) as exc:
        print(f"错误：{exc}")
        return 2
    if changes:
        verb = "已导出" if args.apply else "待导出"
        for path in changes:
            print(f"{verb}：{path}")
        return 0 if args.apply else 1
    print("公开 project-runtime 与源码一致。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
