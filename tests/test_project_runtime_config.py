from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock


RUNTIME = Path(__file__).resolve().parents[1] / "runtime"
sys.path.insert(0, str(RUNTIME))

from project_runtime_config import (  # noqa: E402
    AGENT_PLUGIN_MCP_SCHEMA,
    AGENT_PLUGIN_SCHEMA,
    PROJECT_RUNTIME_NAMESPACE,
    RuntimeConfigError,
    doctor,
    install_plugin,
    inventory_client,
    inventory_project,
    reconcile_project,
    sync_project,
    transfer_to_project,
)
from mcp_server import PROTOCOL_VERSION, handle_message  # noqa: E402
import project_runtime_config  # noqa: E402


def write_json(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def make_project(root: Path, name: str) -> Path:
    root.mkdir(parents=True)
    (root / "AGENTS.md").write_text("# Test\n", encoding="utf-8")
    profile = {
        "schema_version": "1.0",
        "project": {"name": name},
        "runtime": {"manager": "project-runtime"},
        "capabilities": {
            "plugin_roots": [".agents"],
            "skill_roots": [".agents/skills"],
            "mcp_sources": [".agents/mcp.json"],
            "destination_skill_root": ".agents/skills",
            "destination_mcp": ".agents/mcp.json",
        },
    }
    write_json(root / ".agents" / PROJECT_RUNTIME_NAMESPACE / "project.json", profile)
    write_json(root / ".agents" / "plugin.json", {
        "$schema": AGENT_PLUGIN_SCHEMA,
        "name": name,
        "version": "1.0.0",
    })
    write_json(root / ".agents" / "mcp.json", {
        "$schema": AGENT_PLUGIN_MCP_SCHEMA,
        "mcpServers": {
            "local-check": {
                "type": "stdio",
                "command": "python3",
                "args": ["-m", "checker"],
            }
        },
    })
    skill = root / ".agents" / "skills" / "sample-skill"
    skill.mkdir(parents=True)
    (skill / "SKILL.md").write_text(
        "---\nname: sample-skill\ndescription: Test skill used by project-runtime tests.\n---\n\n# Sample\n",
        encoding="utf-8",
    )
    return root


class ProjectRuntimeConfigTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)

    def tearDown(self) -> None:
        self.temp.cleanup()

    def test_inventory_standard_agent_plugin_project(self) -> None:
        project = make_project(self.root / "source", "source-project")
        inventory = inventory_project(project)
        self.assertEqual([item.name for item in inventory.skills], ["sample-skill"])
        self.assertEqual([item.name for item in inventory.mcps], ["local-check"])
        self.assertEqual(inventory.issues, [])
        self.assertTrue(doctor(project)["ok"])

    def test_transfer_dry_run_then_apply(self) -> None:
        source = make_project(self.root / "source", "source-project")
        destination = make_project(self.root / "destination", "destination-project")
        (destination / ".agents" / "skills" / "sample-skill").rename(
            destination / ".agents" / "skills" / "destination-skill"
        )
        destination_mcp = destination / ".agents" / "mcp.json"
        write_json(destination_mcp, {"$schema": AGENT_PLUGIN_MCP_SCHEMA, "mcpServers": {}})

        inventory = inventory_project(source)
        preview = transfer_to_project(
            inventory, destination, ["sample-skill"], ["local-check"], apply=False
        )
        self.assertFalse(preview["applied"])
        self.assertFalse((destination / ".agents" / "skills" / "sample-skill").exists())

        applied = transfer_to_project(
            inventory, destination, ["sample-skill"], ["local-check"], apply=True
        )
        self.assertTrue(applied["applied"])
        self.assertTrue((destination / ".agents" / "skills" / "sample-skill" / "SKILL.md").is_file())
        self.assertIn("local-check", json.loads(destination_mcp.read_text())["mcpServers"])

    def test_transfer_refuses_existing_destination(self) -> None:
        source = make_project(self.root / "source", "source-project")
        destination = make_project(self.root / "destination", "destination-project")
        with self.assertRaises(RuntimeConfigError):
            transfer_to_project(
                inventory_project(source), destination, ["sample-skill"], [], apply=False
            )

    def test_doctor_flags_secret_bearing_mcp(self) -> None:
        project = make_project(self.root / "source", "source-project")
        mcp = project / ".agents" / "mcp.json"
        write_json(mcp, {
            "$schema": AGENT_PLUGIN_MCP_SCHEMA,
            "mcpServers": {
                "unsafe": {
                    "type": "streamable-http",
                    "url": "https://example.test/mcp",
                    "headers": {"Authorization": "Bearer secret-value"},
                }
            },
        })
        result = doctor(project)
        self.assertFalse(result["ok"])
        self.assertTrue(any("possible secret" in issue for issue in result["issues"]))

    def test_inventory_codex_native_mcp(self) -> None:
        home = self.root / "home"
        skill = home / ".codex" / "skills" / "native-skill"
        skill.mkdir(parents=True)
        (skill / "SKILL.md").write_text("# Native\n", encoding="utf-8")
        config = home / ".codex" / "config.toml"
        config.write_text(
            '[mcp_servers.demo]\ncommand = "python3"\nargs = ["-m", "demo"]\n',
            encoding="utf-8",
        )
        inventory = inventory_client("codex", home)
        self.assertEqual([item.name for item in inventory.skills], ["native-skill"])
        self.assertEqual(inventory.mcps[0].config["type"], "stdio")

    def test_sync_cursor_builds_portable_package(self) -> None:
        project = make_project(self.root / "source", "source-project")
        home = self.root / "home"
        preview = sync_project(project, "cursor", home=home, apply=False)
        self.assertFalse(preview["applied"])
        sync_project(project, "cursor", home=home, apply=True)
        target = home / ".cursor" / "plugins" / "local" / "source"
        self.assertEqual(json.loads((target / "plugin.json").read_text())["$schema"], AGENT_PLUGIN_SCHEMA)
        self.assertTrue((target / "skills" / "sample-skill" / "SKILL.md").is_file())

    def test_sync_codex_builds_adapter_and_marketplace(self) -> None:
        project = make_project(self.root / "source", "source-project")
        home = self.root / "home"
        sync_project(project, "codex", home=home, apply=True)
        target = home / ".agents" / "plugins" / "plugins" / "source"
        codex_manifest = json.loads((target / ".codex-plugin" / "plugin.json").read_text())
        self.assertEqual(codex_manifest["mcpServers"], "./.mcp.json")
        self.assertTrue((target / ".mcp.json").is_file())
        marketplace = json.loads(
            (home / ".agents" / "plugins" / "marketplace.json").read_text()
        )
        self.assertEqual(marketplace["plugins"][0]["name"], "source")
        self.assertEqual(
            marketplace["plugins"][0]["source"]["path"],
            "./.agents/plugins/plugins/source",
        )

    def test_native_mcp_source_is_visible_without_failing_doctor(self) -> None:
        project = make_project(self.root / "source", "source-project")
        profile_path = project / ".agents" / PROJECT_RUNTIME_NAMESPACE / "project.json"
        profile = json.loads(profile_path.read_text())
        profile["capabilities"]["native_mcp_sources"] = ["native.jsonc"]
        profile["capabilities"]["credential_env_file"] = ".env"
        profile["capabilities"]["mcp_client_policy"] = {
            "portable": {"include": ["cursor"]}
        }
        write_json(profile_path, profile)
        (project / ".env").write_text("API_TOKEN=test-only\n", encoding="utf-8")
        (project / ".env").chmod(0o600)
        (project / "native.jsonc").write_text(
            '{"mcpServers":{"portable":{"command":"python3","args":["__PROJECT_DIR__/runner.py"]},'
            '"private":{"command":"python3","env":{"API_TOKEN":"${API_TOKEN}"}}}}',
            encoding="utf-8",
        )
        inventory = inventory_project(project)
        records = {item.name: item for item in inventory.mcps}
        self.assertTrue(records["portable"].portable)
        self.assertEqual(records["portable"].authority, "native")
        self.assertTrue(records["private"].portable)
        result = doctor(project)
        self.assertTrue(result["ok"])
        self.assertEqual(result["warnings"], [])
        home = self.root / "home"
        sync_project(project, "cursor", home=home, apply=True)
        package_mcp = json.loads(
            (home / ".cursor/plugins/local/source/mcp.json").read_text(encoding="utf-8")
        )
        self.assertEqual(
            package_mcp["mcpServers"]["portable"]["args"],
            [str((project / "runner.py").resolve())],
        )
        private_projection = package_mcp["mcpServers"]["private"]
        self.assertEqual(private_projection["command"], "python3")
        self.assertIn("mcp_env_launcher.py", private_projection["args"][0])
        package_text = "\n".join(
            path.read_text(encoding="utf-8")
            for path in (home / ".cursor/plugins/local/source").rglob("*.json")
        )
        self.assertNotIn("test-only", package_text)
        codex_home = self.root / "codex-home"
        sync_project(project, "codex", home=codex_home, apply=True)
        codex_mcp = json.loads(
            (codex_home / ".agents/plugins/plugins/source/mcp.json").read_text(encoding="utf-8")
        )
        self.assertNotIn("portable", codex_mcp["mcpServers"])
        self.assertIn("private", codex_mcp["mcpServers"])

    def test_bootstrap_installs_runtime_plugin(self) -> None:
        plugin = make_project(self.root / "plugin", "runtime-test") / ".agents"
        home = self.root / "home"
        preview = install_plugin(plugin, "cursor", home=home)
        self.assertFalse(preview["applied"])
        install_plugin(plugin, "cursor", home=home, apply=True)
        self.assertTrue((home / ".cursor/plugins/local/runtime-test/plugin.json").is_file())
        (plugin / "skills/sample-skill/SKILL.md").write_text("# Updated\n", encoding="utf-8")
        with self.assertRaises(RuntimeConfigError):
            install_plugin(plugin, "cursor", home=home, apply=True)
        install_plugin(plugin, "cursor", home=home, apply=True, replace=True)
        self.assertEqual(
            (home / ".cursor/plugins/local/runtime-test/skills/sample-skill/SKILL.md").read_text(),
            "# Updated\n",
        )

    def test_bootstrap_codex_accepts_skill_only_plugin(self) -> None:
        plugin = self.root / "skill-only"
        write_json(plugin / "plugin.json", {
            "$schema": AGENT_PLUGIN_SCHEMA,
            "name": "skill-only",
            "version": "1.0.0",
            "description": "Skill-only test plugin",
        })
        skill = plugin / "skills" / "sample-skill"
        skill.mkdir(parents=True)
        (skill / "SKILL.md").write_text(
            "---\nname: sample-skill\ndescription: Test skill.\n---\n",
            encoding="utf-8",
        )
        home = self.root / "home"
        install_plugin(plugin, "codex", home=home, apply=True)
        target = home / ".agents/plugins/plugins/skill-only"
        adapter = json.loads((target / ".codex-plugin/plugin.json").read_text())
        self.assertNotIn("mcpServers", adapter)
        self.assertFalse((target / ".mcp.json").exists())
        self.assertTrue((target / "skills/sample-skill/SKILL.md").is_file())

    def test_reconcile_classifies_and_archives_selected_legacy_skill(self) -> None:
        project = make_project(self.root / "source", "source-project")
        home = self.root / "home"
        legacy = home / ".cursor" / "skills" / "work-engine"
        legacy.mkdir(parents=True)
        (legacy / "SKILL.md").write_text("# Legacy\n", encoding="utf-8")
        preview = reconcile_project(
            project, "cursor", home=home, retire_skills=["work-engine"]
        )
        self.assertTrue(any(item["name"] == "work-engine" for item in preview["states"]["native_only"]))
        recovery = self.root / "recovery"
        applied = reconcile_project(
            project,
            "cursor",
            home=home,
            retire_skills=["work-engine"],
            recovery_root=recovery,
            apply=True,
        )
        self.assertTrue(applied["applied"])
        self.assertFalse(legacy.exists())
        self.assertTrue(any(recovery.glob("*/skills/work-engine/SKILL.md")))
        second = reconcile_project(project, "cursor", home=home)
        self.assertEqual(second["operations"][0]["action"], "keep-plugin")

    def test_reconcile_restores_previous_package_when_replacement_fails(self) -> None:
        project = make_project(self.root / "source", "source-project")
        home = self.root / "home"
        reconcile_project(project, "cursor", home=home, apply=True)
        destination = home / ".cursor/plugins/local/source"
        marker = destination / "local-marker.txt"
        marker.write_text("keep me\n", encoding="utf-8")
        original = project_runtime_config._build_package
        calls = 0

        def fail_apply(*args, **kwargs):
            nonlocal calls
            calls += 1
            if calls == 2:
                raise OSError("injected")
            return original(*args, **kwargs)

        with mock.patch.object(project_runtime_config, "_build_package", side_effect=fail_apply):
            with self.assertRaises(RuntimeConfigError):
                reconcile_project(project, "cursor", home=home, apply=True)
        self.assertEqual(marker.read_text(encoding="utf-8"), "keep me\n")


class McpServerTests(unittest.TestCase):
    def test_modern_discovery(self) -> None:
        response = handle_message({
            "jsonrpc": "2.0",
            "id": "discover",
            "method": "server/discover",
            "params": {
                "_meta": {
                    "io.modelcontextprotocol/protocolVersion": PROTOCOL_VERSION,
                    "io.modelcontextprotocol/clientCapabilities": {},
                }
            },
        })
        self.assertEqual(response["result"]["supportedVersions"], [PROTOCOL_VERSION])
        self.assertEqual(response["result"]["resultType"], "complete")

    def test_modern_tools_list_has_cache_contract(self) -> None:
        response = handle_message({
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/list",
            "params": {
                "_meta": {
                    "io.modelcontextprotocol/protocolVersion": PROTOCOL_VERSION,
                    "io.modelcontextprotocol/clientCapabilities": {},
                }
            },
        })
        self.assertEqual(response["result"]["resultType"], "complete")
        self.assertEqual(response["result"]["cacheScope"], "public")
        self.assertGreaterEqual(len(response["result"]["tools"]), 4)

    def test_legacy_initialize_compatibility(self) -> None:
        response = handle_message({
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {"protocolVersion": "2025-06-18"},
        })
        self.assertEqual(response["result"]["protocolVersion"], "2025-06-18")


if __name__ == "__main__":
    unittest.main()
