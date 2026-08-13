#!/usr/bin/env python3
"""先预演完整 Plugin 安装与项目初始化，再按授权应用并运行 doctor。"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any


PLUGIN_ROOT = Path(__file__).resolve().parents[1]
RUNTIME = PLUGIN_ROOT / "runtime" / "project_runtime_config.py"
INITIALIZER = PLUGIN_ROOT / "skills" / "agents-init" / "scripts" / "init_project.py"


class BootstrapInitError(RuntimeError):
    pass


def run_json(command: list[str]) -> tuple[int, dict[str, Any]]:
    completed = subprocess.run(command, check=False, capture_output=True, text=True)
    try:
        payload = json.loads(completed.stdout)
    except json.JSONDecodeError as exc:
        detail = completed.stderr.strip() or completed.stdout.strip() or "无输出"
        raise BootstrapInitError(f"子命令没有返回合法 JSON：{detail}") from exc
    if not isinstance(payload, dict):
        raise BootstrapInitError("子命令 JSON 根节点必须是对象")
    return completed.returncode, payload


def initializer_command(args: argparse.Namespace, *, apply: bool) -> list[str]:
    command = [
        sys.executable,
        str(INITIALIZER),
        "--project", str(args.project),
        "--name", args.name,
        "--project-type", args.project_type,
        "--vcs", args.vcs,
        "--stack", args.stack,
        "--runtime", args.runtime,
        "--agent-cli", args.agent_cli,
        "--runtime-plugin-root", str(PLUGIN_ROOT),
        "--output", "json",
    ]
    if args.slug:
        command.extend(("--slug", args.slug))
    if apply:
        command.append("--apply")
    return command


def install_command(args: argparse.Namespace, *, apply: bool) -> list[str]:
    command = [
        sys.executable,
        str(RUNTIME),
        "--output", "json",
        "bootstrap",
        "--plugin", str(PLUGIN_ROOT),
        "--client", args.client,
    ]
    if args.home:
        command.extend(("--home", str(args.home)))
    if apply:
        command.append("--apply")
    return command


def doctor_command(project: Path) -> list[str]:
    return [
        sys.executable,
        str(RUNTIME),
        "--output", "json",
        "doctor",
        "--project", str(project),
    ]


def execute(args: argparse.Namespace) -> tuple[int, dict[str, Any]]:
    project = args.project.expanduser().resolve()
    args.project = project

    init_code, init_preview = run_json(initializer_command(args, apply=False))
    if init_code != 0 or not init_preview.get("ok"):
        return 1, {
            "ok": False,
            "applied": False,
            "stage": "initializer-preview",
            "initializer": init_preview,
        }

    install_code, install_preview = run_json(install_command(args, apply=False))
    if install_code != 0 or not install_preview.get("ok"):
        return 1, {
            "ok": False,
            "applied": False,
            "stage": "plugin-preview",
            "plugin": install_preview,
            "initializer": init_preview,
        }

    result: dict[str, Any] = {
        "ok": True,
        "applied": False,
        "stage": "preview",
        "plugin": install_preview,
        "initializer": init_preview,
        "doctor": None,
    }
    if not args.apply:
        return 0, result

    install_code, installed = run_json(install_command(args, apply=True))
    result["plugin"] = installed
    if install_code != 0 or not installed.get("ok"):
        result.update(ok=False, stage="plugin-apply")
        return 1, result

    init_code, initialized = run_json(initializer_command(args, apply=True))
    result["initializer"] = initialized
    if init_code != 0 or not initialized.get("ok") or not initialized.get("applied"):
        result.update(ok=False, stage="initializer-apply")
        return 1, result

    doctor_code, checked = run_json(doctor_command(project))
    result["doctor"] = checked
    result["applied"] = True
    result["stage"] = "complete" if doctor_code == 0 and checked.get("ok") else "doctor"
    result["ok"] = result["stage"] == "complete"
    return (0 if result["ok"] else 1), result


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description=__doc__)
    result.add_argument("--client", choices=("codex", "cursor"), required=True)
    result.add_argument("--project", type=Path, required=True)
    result.add_argument("--name", required=True)
    result.add_argument("--slug")
    result.add_argument("--project-type", required=True)
    result.add_argument("--vcs", required=True)
    result.add_argument("--stack", required=True)
    result.add_argument("--runtime", required=True)
    result.add_argument("--agent-cli", required=True)
    result.add_argument("--home", type=Path, help="测试或显式客户端 home；默认使用当前用户 home")
    result.add_argument("--apply", action="store_true")
    return result


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    try:
        code, payload = execute(args)
    except (BootstrapInitError, OSError) as exc:
        code, payload = 2, {"ok": False, "applied": False, "stage": "error", "error": str(exc)}
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return code


if __name__ == "__main__":
    raise SystemExit(main())
