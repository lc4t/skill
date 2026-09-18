#!/usr/bin/env python3
"""从可信源码目录确定性导出公开的 project-orchestrator 与 agent-pack Plugin，默认只检查差异。"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import stat
import tempfile
from pathlib import Path


MAX_FILE_BYTES = 2 * 1024 * 1024
PUBLIC_REPOSITORY = "https://github.com/lc4t/skill"
PLUGINS: dict[str, tuple[str, ...]] = {
    "project-orchestrator": (
        "plugin.json",
        ".codex-plugin/plugin.json",
        "skills/project-orchestrator/SKILL.md",
        "skills/project-orchestrator/agents/openai.yaml",
    ),
    "agent-pack": (
        "plugin.json",
        ".codex-plugin/plugin.json",
        "mcp.json",
        ".mcp.json",
        "references/capability-config.md",
        "runtime/agent_pack_config.py",
        "runtime/mcp_env_launcher.py",
        "runtime/mcp_server.py",
        "skills/agent-pack/SKILL.md",
        "tests/test_agent_pack_config.py",
    ),
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


def read_source(path: Path, relative: Path) -> bytes:
    metadata = path.lstat()
    if stat.S_ISLNK(metadata.st_mode) or not stat.S_ISREG(metadata.st_mode):
        raise ExportError(f"拒绝非普通源码文件：{path}")
    if metadata.st_size > MAX_FILE_BYTES:
        raise ExportError(f"源码文件超过大小限制：{path}")
    try:
        text = path.read_bytes().decode("utf-8")
    except UnicodeDecodeError as exc:
        raise ExportError(f"源码必须是 UTF-8：{path}") from exc
    if relative == Path("plugin.json"):
        # 私有源仓库地址不能进入公开分发；改写后仍做完整隐私扫描。
        manifest = json.loads(text)
        manifest["repository"] = PUBLIC_REPOSITORY
        text = json.dumps(manifest, ensure_ascii=False, indent=2) + "\n"
    hits = [marker for marker in FORBIDDEN_TEXT if marker in text]
    token_digests = {
        hashlib.sha256(token.encode("utf-8")).hexdigest()
        for token in re.findall(r"[A-Za-z0-9._-]+", text)
    }
    if token_digests & FORBIDDEN_TOKEN_DIGESTS:
        hits.append("private-project-identifier")
    if hits:
        raise ExportError(f"源码包含禁止公开的标记 {hits}：{path}")
    return text.encode("utf-8")


def check_manifests(name: str, rendered: dict[Path, bytes]) -> None:
    manifest = json.loads(rendered[Path("plugin.json")])
    adapter = json.loads(rendered[Path(".codex-plugin/plugin.json")])
    if manifest.get("name") != name or adapter.get("name") != name:
        raise ExportError(f"{name} 的 plugin.json 与 Codex adapter 名称必须都为 {name}")
    if manifest.get("version") != adapter.get("version"):
        raise ExportError(
            f"{name} 的 Codex adapter 版本 {adapter.get('version')} 与 plugin.json {manifest.get('version')} 不一致"
        )


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


def export(source_root: Path, destination_root: Path, *, apply: bool) -> list[str]:
    source_root = source_root.expanduser().resolve()
    destination_root = destination_root.expanduser().resolve()
    changes: list[str] = []
    rendered: dict[Path, bytes] = {}
    for name, files in PLUGINS.items():
        plugin_payloads: dict[Path, bytes] = {}
        for relative in map(Path, files):
            plugin_payloads[relative] = read_source(source_root / name / relative, relative)
        check_manifests(name, plugin_payloads)
        for relative, payload in plugin_payloads.items():
            target_relative = Path(name) / relative
            rendered[target_relative] = payload
            target = destination_root / target_relative
            current = target.read_bytes() if target.is_file() and not target.is_symlink() else None
            if digest(current) != digest(payload):
                changes.append(str(Path("plugins") / target_relative))
    if apply:
        for relative, payload in rendered.items():
            if str(Path("plugins") / relative) in changes:
                atomic_write(destination_root / relative, payload)
    return changes


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--source",
        type=Path,
        required=True,
        help="包含 project-orchestrator/ 与 agent-pack/ 两个 Plugin 源码目录的父目录",
    )
    parser.add_argument("--destination", type=Path, default=Path(__file__).resolve().parents[1] / "plugins")
    parser.add_argument("--apply", action="store_true", help="应用白名单内的差异；默认只检查")
    args = parser.parse_args()
    try:
        changes = export(args.source, args.destination, apply=args.apply)
    except (OSError, ValueError, ExportError) as exc:
        print(f"错误：{exc}")
        return 2
    if changes:
        verb = "已导出" if args.apply else "待导出"
        for path in changes:
            print(f"{verb}：{path}")
        return 0 if args.apply else 1
    print("公开 Plugin 与源码一致。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
