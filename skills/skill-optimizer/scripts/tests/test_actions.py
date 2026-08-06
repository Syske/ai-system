#!/usr/bin/env python3
"""Tests for the P11 absorbed actions (augment / validate / tune-description).

Verifies candidate-first semantics (writes to snapshot, never touches the
live skill dir), and validate's format normalization across the three
supported benchmark shapes (routing / outcome / minimal).
"""

import json
import pathlib
import tempfile
import unittest

from fixtures import make_skill_dir, SCRIPTS_DIR  # noqa: F401

from snapshot_manager import SnapshotManager
from actions import run_augment, run_tune_description, run_validate


class FakeLLM:
    def __call__(self, prompt):
        if "held-out validator" in prompt:
            return "T1: PASS\nT2: PASS\nT3: FAIL\nPASS RATE: 2/3"
        if "tuning the frontmatter" in prompt:
            return "1) vague\n---\n`Optimize skills via static/dynamic`"
        return "## Examples\n\n- task: A\n  approach: B\n  result: C"


def _patch_llm():
    import actions

    actions._load_llm = lambda: FakeLLM()
    return actions


class TestAugment(unittest.TestCase):
    def test_writes_candidate_snapshot_not_live(self):
        actions = _patch_llm()
        skill_dir = make_skill_dir()
        demos = pathlib.Path(tempfile.mkdtemp()) / "demos.json"
        demos.write_text(
            json.dumps([{"task": "x", "approach": "y", "result": "z"}]),
            encoding="utf-8",
        )
        rc = run_augment(skill_dir, demos)
        self.assertEqual(rc, 0)

        sm = SnapshotManager(skill_dir)
        latest = sm.get_latest_version()
        snap = sm.snapshots_dir / latest / "SKILL.md"
        self.assertTrue(snap.exists())
        self.assertIn("## Examples", snap.read_text(encoding="utf-8"))
        # live skill dir untouched
        self.assertNotIn("## Examples", (skill_dir / "SKILL.md").read_text(encoding="utf-8"))

    def test_missing_demos_errors(self):
        actions = _patch_llm()
        skill_dir = make_skill_dir()
        rc = run_augment(skill_dir, None)
        self.assertEqual(rc, 1)


class TestValidateFormatNormalization(unittest.TestCase):
    def test_minimal_shape(self):
        actions = _patch_llm()
        skill_dir = make_skill_dir()
        # create a candidate snapshot first so validate has something to diff
        from actions import _propose_candidate

        _propose_candidate(skill_dir, skill_dir / "SKILL.md", "---\nname: test-skill\n---\n\n# T\n\nNew body.\n", mode="augment", reason="r")
        bench = pathlib.Path(tempfile.mkdtemp()) / "b.json"
        bench.write_text(
            json.dumps([{"task": "t1", "expected_outcome": "o1"}]),
            encoding="utf-8",
        )
        rc = run_validate(skill_dir, bench)
        self.assertEqual(rc, 0)

    def test_routing_shape(self):
        actions = _patch_llm()
        skill_dir = make_skill_dir()
        bench = pathlib.Path(tempfile.mkdtemp()) / "b.json"
        bench.write_text(
            json.dumps([
                {"query": "optimize my skill", "expectedSkills": ["skill-optimizer"],
                 "routingIntent": "optimize", "routingAnchors": ["optimize"]}
            ]),
            encoding="utf-8",
        )
        # normalize path: build candidate, then validate
        from actions import _propose_candidate
        _propose_candidate(skill_dir, skill_dir / "SKILL.md", "---\nname: test-skill\n---\n\n# T\n\nNew body.\n", mode="augment", reason="r")
        rc = run_validate(skill_dir, bench)
        self.assertEqual(rc, 0)

    def test_outcome_shape(self):
        actions = _patch_llm()
        skill_dir = make_skill_dir()
        bench = pathlib.Path(tempfile.mkdtemp()) / "b.json"
        bench.write_text(
            json.dumps([
                {"skill": "test-skill", "skillVersion": "v1",
                 "standardAnswer": "produces report", "rootCauses": ["c1"],
                 "keyActions": ["k1"]}
            ]),
            encoding="utf-8",
        )
        from actions import _propose_candidate
        _propose_candidate(skill_dir, skill_dir / "SKILL.md", "---\nname: test-skill\n---\n\n# T\n\nNew body.\n", mode="augment", reason="r")
        rc = run_validate(skill_dir, bench)
        self.assertEqual(rc, 0)

    def test_unrecognized_shape_errors(self):
        actions = _patch_llm()
        skill_dir = make_skill_dir()
        bench = pathlib.Path(tempfile.mkdtemp()) / "b.json"
        bench.write_text(json.dumps([{"foo": "bar"}]), encoding="utf-8")
        rc = run_validate(skill_dir, bench)
        self.assertEqual(rc, 1)


class TestTuneDescription(unittest.TestCase):
    def test_updates_description_in_snapshot(self):
        actions = _patch_llm()
        skill_dir = make_skill_dir(frontmatter=True)
        rc = run_tune_description(skill_dir, None)
        self.assertEqual(rc, 0)

        sm = SnapshotManager(skill_dir)
        snap = sm.snapshots_dir / sm.get_latest_version() / "SKILL.md"
        content = snap.read_text(encoding="utf-8")
        self.assertIn("description: Optimize skills via static/dynamic", content)
        # live untouched
        self.assertNotIn("Optimize skills via", (skill_dir / "SKILL.md").read_text(encoding="utf-8"))

    def test_missing_frontmatter_errors(self):
        actions = _patch_llm()
        skill_dir = make_skill_dir(frontmatter=False)
        rc = run_tune_description(skill_dir, None)
        self.assertEqual(rc, 1)  # no YAML frontmatter -> explicit error, no write


if __name__ == "__main__":
    unittest.main()
