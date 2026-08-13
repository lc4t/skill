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
            "mcp.json",
            "skills",
            "runtime",
            "scripts",
            ".codex-plugin/plugin.json",
            ".mcp.json",
        ):
            self.assertIn(required, workflow)


if __name__ == "__main__":
    unittest.main()
