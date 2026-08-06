#!/usr/bin/env python3
"""Tests for snapshot meta.json optimization_gradient persistence (R6/Q2)."""

import json
import pathlib
import tempfile
import unittest

from fixtures import make_skill_dir, SCRIPTS_DIR  # noqa: F401
from snapshot_manager import SnapshotManager


class TestOptimizationGradient(unittest.TestCase):
    def test_gradient_persisted_in_meta(self):
        skill_dir = make_skill_dir()
        sm = SnapshotManager(skill_dir)
        version = sm.create_snapshot(
            mode="static",
            reason="auto optimization",
            source="auto",
            optimization_gradient="[structure] body too short => expand body\n[risk] missing section => add risk",
        )
        meta_path = sm.snapshots_dir / version / "meta.json"
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
        self.assertIn("optimization_gradient", meta)
        self.assertIn("expand body", meta["optimization_gradient"])

    def test_gradient_absent_when_not_provided(self):
        skill_dir = make_skill_dir()
        sm = SnapshotManager(skill_dir)
        version = sm.create_snapshot(mode="feedback", reason="user", source="user")
        meta_path = sm.snapshots_dir / version / "meta.json"
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
        self.assertNotIn("optimization_gradient", meta)

    def test_backward_compatible_signature(self):
        # actions.py calls create_snapshot without the new kwarg; must still work
        skill_dir = make_skill_dir()
        sm = SnapshotManager(skill_dir)
        version = sm.create_snapshot(mode="augment", reason="r", source="auto")
        self.assertTrue(version.startswith("v"))


if __name__ == "__main__":
    unittest.main()
