from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).with_name("init_project.py")


class InitProjectTests(unittest.TestCase):
    def run_script(self, root: Path, *extra: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [
                sys.executable,
                str(SCRIPT),
                "--project", str(root),
                "--name", "Example Project",
                "--project-type", "code,docs",
                "--vcs", "github",
                "--stack", "python,markdown",
                "--runtime", "local",
                "--agent-cli", "codex,cursor",
                "--output", "json",
                *extra,
            ],
            check=False,
            capture_output=True,
            text=True,
        )

    def test_dry_run_does_not_write(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            result = self.run_script(root)
            self.assertEqual(result.returncode, 0)
            payload = json.loads(result.stdout)
            self.assertFalse(payload["applied"])
            self.assertFalse((root / "AGENTS.md").exists())

    def test_apply_creates_v5_skeleton(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            result = self.run_script(root, "--apply")
            self.assertEqual(result.returncode, 0, result.stderr)
            profile = json.loads((root / ".agents/moe.sakanano.project-runtime/project.json").read_text())
            self.assertEqual(profile["schema_version"], "1.0")
            self.assertEqual(profile["initializer_version"], "5.0.0")
            self.assertEqual(profile["$schema"], "https://skill.sakanano.moe/skills/agents-init/project.schema.json")
            self.assertEqual(profile["runtime"]["skill"], "project-runtime")
            self.assertIsNone(profile["opinion"]["provider"])
            self.assertTrue((root / "docs/drafts/.gitkeep").exists())

    def test_apply_preserves_collision(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "AGENTS.md").write_text("existing\n")
            result = self.run_script(root, "--apply")
            self.assertEqual(result.returncode, 1)
            self.assertEqual((root / "AGENTS.md").read_text(), "existing\n")
            payload = json.loads(result.stdout)
            self.assertIn("AGENTS.md", payload["preserved_collisions"])
            self.assertTrue((root / ".agents/plugin.json").exists())

    def test_rejects_invalid_slug(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            result = self.run_script(Path(temporary), "--slug", "Bad Slug")
            self.assertEqual(result.returncode, 2)
            self.assertFalse(json.loads(result.stdout)["ok"])


if __name__ == "__main__":
    unittest.main()
