from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock


SCRIPT = Path(__file__).with_name("init_project.py")
sys.path.insert(0, str(SCRIPT.parent))
import init_project  # noqa: E402


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
            self.assertEqual(profile["initializer_version"], "5.1.0")
            self.assertEqual(profile["$schema"], "https://skill.sakanano.moe/skills/agents-init/project.schema.json")
            self.assertEqual(profile["runtime"]["skill"], "project-runtime")
            self.assertIsNone(profile["opinion"]["provider"])
            self.assertTrue((root / "docs/drafts/.gitkeep").exists())

    def test_apply_collision_writes_nothing(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "AGENTS.md").write_text("existing\n")
            result = self.run_script(root, "--apply")
            self.assertEqual(result.returncode, 1)
            self.assertEqual((root / "AGENTS.md").read_text(), "existing\n")
            payload = json.loads(result.stdout)
            self.assertIn("AGENTS.md", payload["preserved_collisions"])
            self.assertFalse(payload["applied"])
            self.assertFalse((root / ".agents/plugin.json").exists())

    def test_rejects_symlinked_parent(self) -> None:
        with tempfile.TemporaryDirectory() as temporary, tempfile.TemporaryDirectory() as outside:
            root = Path(temporary)
            (root / ".agents").symlink_to(Path(outside), target_is_directory=True)
            result = self.run_script(root, "--apply")
            self.assertEqual(result.returncode, 2)
            self.assertIn("symlinked parent", json.loads(result.stdout)["error"])
            self.assertEqual(list(Path(outside).iterdir()), [])

    def test_midway_failure_rolls_back_known_files(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            files = {Path("one/file.txt"): "one\n", Path("two/file.txt"): "two\n"}
            original = init_project._write_exclusive
            calls = 0

            def fail_second(parent_fd: int, name: str, payload: bytes) -> None:
                nonlocal calls
                calls += 1
                if calls == 2:
                    raise OSError("injected failure")
                original(parent_fd, name, payload)

            with mock.patch.object(init_project, "_write_exclusive", side_effect=fail_second):
                with self.assertRaises(init_project.InitError):
                    init_project.apply_writes(root, files, files)
            self.assertFalse((root / "one/file.txt").exists())
            self.assertFalse((root / "two/file.txt").exists())
            self.assertEqual(list(root.iterdir()), [])

    def test_rejects_invalid_slug(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            result = self.run_script(Path(temporary), "--slug", "Bad Slug")
            self.assertEqual(result.returncode, 2)
            self.assertFalse(json.loads(result.stdout)["ok"])

    def test_migrate_creates_missing_and_preserves_unselected_collision(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "AGENTS.md").write_text("legacy\n", encoding="utf-8")
            result = self.run_script(root, "--mode", "migrate", "--apply")
            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(result.stdout)
            self.assertTrue(payload["applied"])
            self.assertEqual((root / "AGENTS.md").read_text(), "legacy\n")
            self.assertTrue((root / ".agents/plugin.json").is_file())

    def test_migrate_replaces_only_selected_path_with_external_recovery(self) -> None:
        with tempfile.TemporaryDirectory() as temporary, tempfile.TemporaryDirectory() as backup:
            root = Path(temporary)
            (root / "AGENTS.md").write_text("legacy\n", encoding="utf-8")
            recovery = Path(backup) / "migration"
            result = self.run_script(
                root,
                "--mode", "migrate",
                "--replace", "AGENTS.md",
                "--recovery-dir", str(recovery),
                "--apply",
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertNotEqual((root / "AGENTS.md").read_text(), "legacy\n")
            self.assertEqual((recovery / "AGENTS.md").read_text(), "legacy\n")

    def test_migrate_replacement_requires_recovery(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "AGENTS.md").write_text("legacy\n", encoding="utf-8")
            result = self.run_script(
                root, "--mode", "migrate", "--replace", "AGENTS.md", "--apply"
            )
            self.assertEqual(result.returncode, 2)
            self.assertEqual((root / "AGENTS.md").read_text(), "legacy\n")


if __name__ == "__main__":
    unittest.main()
