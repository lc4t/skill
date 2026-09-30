from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class SiteReleaseTests(unittest.TestCase):
    def test_homepage_metadata_matches_plugin_authority(self) -> None:
        manifest = json.loads((ROOT / "plugin.json").read_text(encoding="utf-8"))
        index = json.loads((ROOT / "index.json").read_text(encoding="utf-8"))
        homepage = (ROOT / "index.html").read_text(encoding="utf-8")
        version = manifest["version"]
        updated_at = index["site"]["updated_at"]
        self.assertEqual(index["plugin"]["version"], version)
        self.assertIn(f"Plugin {version}", homepage)
        self.assertIn(f"更新日期 {updated_at}", homepage)
        self.assertNotIn("main 分支", homepage)
        self.assertNotIn("正式域名", homepage)

    def test_pages_workflow_publishes_complete_install_unit(self) -> None:
        workflow = (ROOT / ".github/workflows/pages.yml").read_text(encoding="utf-8")
        for required in (
            "INSTALL.md",
            "llms.txt",
            "plugin.json",
            "skills",
            "plugins",
            "scripts",
            ".codex-plugin/plugin.json",
        ):
            self.assertIn(required, workflow)
        self.assertNotIn("runtime", workflow)

    def test_bundled_plugins_match_manifests(self) -> None:
        for name in ("project-orchestrator", "agent-pack", "opinion-manager"):
            root = ROOT / "plugins" / name
            manifest = json.loads((root / "plugin.json").read_text(encoding="utf-8"))
            adapter = json.loads((root / ".codex-plugin/plugin.json").read_text(encoding="utf-8"))
            self.assertEqual(manifest["name"], name)
            self.assertEqual(adapter["version"], manifest["version"])
            self.assertEqual(manifest["repository"], "https://github.com/lc4t/skill")
            self.assertTrue((root / "skills" / name / "SKILL.md").is_file())

    def test_no_project_runtime_left_in_distribution(self) -> None:
        self.assertFalse((ROOT / "skills/project-runtime").exists())
        self.assertFalse((ROOT / "runtime").exists())
        for path in ("plugin.json", ".codex-plugin/plugin.json", "index.json", "llms.txt"):
            self.assertNotIn("project-runtime", (ROOT / path).read_text(encoding="utf-8"), path)

    def test_public_opinion_template_catalog_is_empty(self) -> None:
        template_root = ROOT / "plugins/opinion-manager/templates"
        self.assertEqual(
            [path.name for path in template_root.iterdir() if path.name != ".gitkeep"],
            [],
        )
        schema = json.loads(
            (ROOT / "plugins/opinion-manager/references/template.schema.json").read_text(
                encoding="utf-8"
            )
        )
        self.assertEqual(schema["title"], "Opinion template")
        versioned_root = ROOT / "plugins/opinion-manager/catalog"
        self.assertEqual(list(versioned_root.rglob("*.json")), [])
        for directory in ("rules", "templates"):
            self.assertTrue((versioned_root / directory / ".gitkeep").is_file())


if __name__ == "__main__":
    unittest.main()
