#!/usr/bin/env python3
"""C1 test base — StateStore tests (no LLM / no network / no TTY).

Covers read/write, nested keys, defaults, corrupted-file recovery, and
save round-trip. Part of the CLI test foundation (CLI-STANDARDIZATION C1).

Run:
    python -m unittest discover -s cli/tests
"""

import os
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

from cli.services.state_store import StateStore  # noqa: E402


class TestStateStore(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.path = Path(self.tmp.name) / "state.yaml"

    def tearDown(self):
        self.tmp.cleanup()

    def test_missing_file_returns_empty(self):
        store = StateStore(self.path)
        self.assertEqual(store.data, {})
        self.assertIsNone(store.get("anything"))

    def test_set_get_roundtrip(self):
        store = StateStore(self.path)
        store.set("a", value=1)
        self.assertEqual(store.get("a"), 1)

    def test_nested_keys(self):
        store = StateStore(self.path)
        store.set("outer", "inner", value="v")
        self.assertEqual(store.get("outer", "inner"), "v")
        # intermediate path is a dict
        self.assertEqual(store.get("outer"), {"inner": "v"})

    def test_default_when_missing(self):
        store = StateStore(self.path)
        self.assertEqual(store.get("nope", default="D"), "D")
        self.assertEqual(store.get("a", "b", default="D"), "D")

    def test_save_persists_to_file(self):
        store = StateStore(self.path)
        store.set("k", value="persisted")
        store.save()
        self.assertTrue(self.path.exists())
        # reload from disk
        store2 = StateStore(self.path)
        self.assertEqual(store2.get("k"), "persisted")

    def test_corrupted_file_recovers_to_empty(self):
        self.path.write_text("{ not valid yaml !!!", encoding="utf-8")
        store = StateStore(self.path)
        self.assertEqual(store.data, {})

    def test_save_never_raises_on_bad_path(self):
        store = StateStore(Path(self.tmp.name) / "no" / "such" / "dir" / "s.yaml")
        store.set("k", value=1)
        store.save()  # must not raise


if __name__ == "__main__":
    unittest.main()
