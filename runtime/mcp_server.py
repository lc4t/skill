#!/usr/bin/env python3
"""MCP stdio adapter for project-runtime configuration operations.

Primary protocol: MCP 2026-07-28 (stateless, per-request metadata).
Compatibility: legacy initialize/notifications/initialized clients.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

from project_runtime_config import (
    RuntimeConfigError,
    doctor,
    install_plugin,
    inventory_source,
    reconcile_project,
    sync_project,
    transfer_to_project,
)


PROTOCOL_VERSION = "2026-07-28"
LEGACY_VERSION = "2025-06-18"
SERVER_INFO = {"name": "project-runtime", "version": "1.3.3"}
SERVER_META = {"io.modelcontextprotocol/serverInfo": SERVER_INFO}


TOOLS = [
    {
        "name": "project_runtime_bootstrap",
        "title": "Install Project Runtime Plugin",
        "description": "Dry-run or install a portable plugin, including project-runtime itself, into Codex or Cursor without overwriting an existing package.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "plugin": {"type": "string"},
                "client": {"type": "string", "enum": ["codex", "cursor"]},
                "home": {"type": "string"},
                "apply": {"type": "boolean", "default": False},
                "replace": {"type": "boolean", "default": False},
                "recoveryRoot": {"type": "string"},
            },
            "required": ["plugin", "client"],
            "additionalProperties": False,
        },
        "annotations": {"destructiveHint": False, "idempotentHint": False},
    },
    {
        "name": "project_runtime_reconcile",
        "title": "Reconcile Project and Client Capabilities",
        "description": "Classify capability drift, safely replace the managed project package, and archive explicitly selected legacy Skills or plugins with rollback. apply defaults to false.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "project": {"type": "string"},
                "client": {"type": "string", "enum": ["codex", "cursor"]},
                "home": {"type": "string"},
                "retireSkills": {"type": "array", "items": {"type": "string"}, "default": []},
                "retirePlugins": {"type": "array", "items": {"type": "string"}, "default": []},
                "recoveryRoot": {"type": "string"},
                "apply": {"type": "boolean", "default": False},
            },
            "required": ["project", "client"],
            "additionalProperties": False,
        },
        "annotations": {"destructiveHint": True, "idempotentHint": False},
    },
    {
        "name": "project_runtime_inventory",
        "title": "Inventory Agent Capabilities",
        "description": "Discover portable Agent Plugins, Skills, and MCP servers from a project, plugin directory, or supported client.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "source": {"type": "string", "description": "project:/path, plugin:/path, client:codex, client:cursor, or client:claude"},
                "home": {"type": "string"},
            },
            "required": ["source"],
            "additionalProperties": False,
        },
    },
    {
        "name": "project_runtime_doctor",
        "title": "Validate Project Capabilities",
        "description": "Validate an initialized project's Agent Plugin, Skill, MCP, duplicate-name, portability, and secret boundaries.",
        "inputSchema": {
            "type": "object",
            "properties": {"project": {"type": "string"}},
            "required": ["project"],
            "additionalProperties": False,
        },
    },
    {
        "name": "project_runtime_transfer",
        "title": "Transfer Skills and MCP Servers",
        "description": "Dry-run or copy explicitly selected portable Skills and MCP definitions into another initialized project. apply defaults to false.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "source": {"type": "string"},
                "toProject": {"type": "string"},
                "skills": {"type": "array", "items": {"type": "string"}, "default": []},
                "mcps": {"type": "array", "items": {"type": "string"}, "default": []},
                "home": {"type": "string"},
                "apply": {"type": "boolean", "default": False},
            },
            "required": ["source", "toProject"],
            "additionalProperties": False,
        },
        "annotations": {"destructiveHint": False, "idempotentHint": False},
    },
    {
        "name": "project_runtime_sync",
        "title": "Sync Project Capabilities to an Agent Client",
        "description": "Dry-run or install a project's portable capability package into Codex or Cursor. apply defaults to false and existing targets are never overwritten.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "project": {"type": "string"},
                "client": {"type": "string", "enum": ["codex", "cursor"]},
                "home": {"type": "string"},
                "apply": {"type": "boolean", "default": False},
            },
            "required": ["project", "client"],
            "additionalProperties": False,
        },
        "annotations": {"destructiveHint": False, "idempotentHint": False},
    },
]


def _modern(params: dict[str, Any]) -> bool:
    meta = params.get("_meta", {})
    return isinstance(meta, dict) and meta.get("io.modelcontextprotocol/protocolVersion") == PROTOCOL_VERSION


def _result(payload: dict[str, Any], modern: bool) -> dict[str, Any]:
    result: dict[str, Any] = {
        "content": [{"type": "text", "text": json.dumps(payload, ensure_ascii=False, indent=2)}],
        "structuredContent": payload,
        "isError": not payload.get("ok", True),
    }
    if modern:
        result["resultType"] = "complete"
        result["_meta"] = SERVER_META
    return result


def _call(name: str, arguments: dict[str, Any]) -> dict[str, Any]:
    home_value = arguments.get("home")
    home = Path(home_value) if isinstance(home_value, str) else None
    if name == "project_runtime_bootstrap":
        recovery_value = arguments.get("recoveryRoot")
        recovery = Path(recovery_value) if isinstance(recovery_value, str) else None
        return install_plugin(
            Path(arguments["plugin"]),
            arguments["client"],
            home=home,
            apply=bool(arguments.get("apply", False)),
            replace=bool(arguments.get("replace", False)),
            recovery_root=recovery,
        )
    if name == "project_runtime_reconcile":
        recovery_value = arguments.get("recoveryRoot")
        recovery = Path(recovery_value) if isinstance(recovery_value, str) else None
        return reconcile_project(
            Path(arguments["project"]),
            arguments["client"],
            home=home,
            retire_skills=arguments.get("retireSkills", []),
            retire_plugins=arguments.get("retirePlugins", []),
            recovery_root=recovery,
            apply=bool(arguments.get("apply", False)),
        )
    if name == "project_runtime_inventory":
        inventory = inventory_source(arguments["source"], home)
        payload = inventory.to_dict()
        payload["ok"] = not payload["issues"]
        return payload
    if name == "project_runtime_doctor":
        return doctor(Path(arguments["project"]))
    if name == "project_runtime_transfer":
        source = inventory_source(arguments["source"], home)
        return transfer_to_project(
            source,
            Path(arguments["toProject"]),
            arguments.get("skills", []),
            arguments.get("mcps", []),
            apply=bool(arguments.get("apply", False)),
        )
    if name == "project_runtime_sync":
        return sync_project(
            Path(arguments["project"]),
            arguments["client"],
            home=home,
            apply=bool(arguments.get("apply", False)),
        )
    raise RuntimeConfigError(f"unknown tool: {name}")


def handle_message(message: dict[str, Any]) -> dict[str, Any] | None:
    if message.get("jsonrpc") != "2.0":
        return {"jsonrpc": "2.0", "id": message.get("id"), "error": {"code": -32600, "message": "Invalid Request"}}
    if "id" not in message:
        return None
    request_id = message["id"]
    method = message.get("method")
    params = message.get("params") if isinstance(message.get("params"), dict) else {}
    modern = _modern(params)
    try:
        if method == "server/discover":
            result = {
                "resultType": "complete",
                "supportedVersions": [PROTOCOL_VERSION],
                "capabilities": {"tools": {}},
                "_meta": SERVER_META,
                "instructions": "Inventory first. Transfer and sync default to dry-run; set apply=true only after user approval.",
                "ttlMs": 3600000,
                "cacheScope": "public",
            }
        elif method == "initialize":
            result = {
                "protocolVersion": LEGACY_VERSION,
                "capabilities": {"tools": {}},
                "serverInfo": SERVER_INFO,
                "instructions": "Inventory first; write operations require apply=true.",
            }
        elif method == "tools/list":
            result = {"tools": TOOLS}
            if modern:
                result.update({
                    "resultType": "complete",
                    "ttlMs": 300000,
                    "cacheScope": "public",
                    "_meta": SERVER_META,
                })
        elif method == "tools/call":
            name = params.get("name")
            arguments = params.get("arguments", {})
            if not isinstance(name, str) or not isinstance(arguments, dict):
                raise RuntimeConfigError("tools/call requires string name and object arguments")
            result = _result(_call(name, arguments), modern)
        else:
            return {"jsonrpc": "2.0", "id": request_id, "error": {"code": -32601, "message": "Method not found"}}
        return {"jsonrpc": "2.0", "id": request_id, "result": result}
    except (RuntimeConfigError, KeyError, TypeError, ValueError) as exc:
        payload = {"ok": False, "error": str(exc)}
        if method == "tools/call":
            return {"jsonrpc": "2.0", "id": request_id, "result": _result(payload, modern)}
        return {"jsonrpc": "2.0", "id": request_id, "error": {"code": -32602, "message": str(exc)}}


def main() -> int:
    for line in sys.stdin:
        try:
            message = json.loads(line)
            if not isinstance(message, dict):
                raise ValueError("message must be an object")
            response = handle_message(message)
        except (json.JSONDecodeError, ValueError) as exc:
            response = {"jsonrpc": "2.0", "id": None, "error": {"code": -32700, "message": str(exc)}}
        if response is not None:
            sys.stdout.write(json.dumps(response, ensure_ascii=False, separators=(",", ":")) + "\n")
            sys.stdout.flush()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
