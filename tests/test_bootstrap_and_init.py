from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


PLUGIN_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = PLUGIN_ROOT / "scripts" / "bootstrap_and_init.py"


class BootstrapAndInitTests(unittest.TestCase):
    def run_script(self, project: Path, home: Path, *extra: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [
                sys.executable,
                str(SCRIPT),
                "--client", "codex",
                "--project", str(project),
                "--name", "示例项目",
                "--slug", "example-project",
                "--project-type", "code,docs",
                "--vcs", "github",
                "--stack", "python,markdown",
                "--runtime", "local",
                "--agent-cli", "codex",
                "--home", str(home),
                *extra,
            ],
            check=False,
            capture_output=True,
            text=True,
        )

    def test_dry_run_keeps_client_and_project_unchanged(self) -> None:
        with tempfile.TemporaryDirectory() as project_dir, tempfile.TemporaryDirectory() as home_dir:
            project, home = Path(project_dir), Path(home_dir)
            result = self.run_script(project, home)
            self.assertEqual(result.returncode, 0, result.stderr or result.stdout)
            payload = json.loads(result.stdout)
            self.assertEqual(payload["stage"], "preview")
            self.assertFalse(payload["applied"])
            self.assertEqual(list(project.iterdir()), [])
            self.assertEqual(list(home.iterdir()), [])

    def test_apply_installs_initializes_and_runs_doctor(self) -> None:
        with tempfile.TemporaryDirectory() as project_dir, tempfile.TemporaryDirectory() as home_dir:
            project, home = Path(project_dir), Path(home_dir)
            result = self.run_script(project, home, "--apply")
            self.assertEqual(result.returncode, 0, result.stderr or result.stdout)
            payload = json.loads(result.stdout)
            self.assertEqual(payload["stage"], "complete")
            self.assertTrue(payload["applied"])
            self.assertTrue(payload["initializer"]["applied"])
            self.assertTrue(payload["doctor"]["ok"])
            self.assertTrue((project / "AGENTS.md").is_file())
            self.assertTrue(
                (home / ".agents/plugins/plugins/agents-init/skills/project-runtime/SKILL.md").is_file()
            )

    def test_project_collision_blocks_before_plugin_install(self) -> None:
        with tempfile.TemporaryDirectory() as project_dir, tempfile.TemporaryDirectory() as home_dir:
            project, home = Path(project_dir), Path(home_dir)
            (project / "AGENTS.md").write_text("existing\n", encoding="utf-8")
            result = self.run_script(project, home, "--apply")
            self.assertEqual(result.returncode, 1)
            payload = json.loads(result.stdout)
            self.assertEqual(payload["stage"], "initializer-preview")
            self.assertEqual((project / "AGENTS.md").read_text(encoding="utf-8"), "existing\n")
            self.assertEqual(list(home.iterdir()), [])


if __name__ == "__main__":
    unittest.main()
