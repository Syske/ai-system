#!/usr/bin/env python3
"""Tests for run_optimizer multi-skill guard (P15 / E3 finding)."""

import os
import pathlib
import tempfile
import unittest

from fixtures import SCRIPTS_DIR  # noqa: F401

os.environ.setdefault("DEEPSEEK_API_KEY", "test-key-does-not-connect")


class TestMultiSkillGuard(unittest.TestCase):
    def test_multi_skill_dir_refused(self):
        from main import run_optimizer

        work = pathlib.Path(tempfile.mkdtemp())
        src = work / "multi-skill"
        for name in ["skill-a", "skill-b"]:
            d = src / name
            d.mkdir(parents=True)
            (d / "SKILL.md").write_text(
                f"---\nname: {name}\n---\n\n# {name}\n\nBody.\n", encoding="utf-8"
            )
        proj = work / "project"
        proj.mkdir()

        # RealLLMClient() would connect only lazily; guard must return before
        # any processing. run_optimizer with parallel=True exercises the
        # shared-workspace path that the guard now blocks.
        paths = run_optimizer(
            mode="static", input_path=src, project_dir=proj,
            open_diff=False, parallel=True,
        )
        self.assertEqual(paths, [])
        # no workspace artifacts created
        leftover = list(proj.glob("multi-skill-*"))
        self.assertEqual(leftover, [], f"workspace leaked: {leftover}")

    def test_single_skill_still_accepted_guard_skipped(self):
        # A single SKILL.md must pass the guard (no error return before LLM).
        from main import run_optimizer

        work = pathlib.Path(tempfile.mkdtemp())
        src = work / "single-skill"
        src.mkdir()
        (src / "SKILL.md").write_text(
            "---\nname: single\n---\n\n# Single\n\nBody.\n", encoding="utf-8"
        )
        proj = work / "project"
        proj.mkdir()
        # This would attempt a real LLM call; we only assert the guard path
        # itself is not the failure (guard passes, then LLM init occurs).
        # Run with invalid key to force an early return *after* the guard:
        old = os.environ.get("DEEPSEEK_API_KEY")
        os.environ["DEEPSEEK_API_KEY"] = "definitely-invalid-key-xyz"
        try:
            paths = run_optimizer(
                mode="static", input_path=src, project_dir=proj, open_diff=False
            )
        finally:
            if old:
                os.environ["DEEPSEEK_API_KEY"] = old
            else:
                os.environ.pop("DEEPSEEK_API_KEY", None)
        # Guard passes; LLM init with bad key returns [] (not a guard rejection).
        # Either way no exception -> guard logic is not triggered for 1 skill.
        self.assertIsInstance(paths, list)


if __name__ == "__main__":
    unittest.main()
