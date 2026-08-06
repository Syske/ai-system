#!/usr/bin/env python3
"""Tests for core.py pure helpers (no LLM / no network)."""

import pathlib
import tempfile
import unittest

from fixtures import make_skill_dir, SCRIPTS_DIR  # noqa: F401 (path setup)

from core import (
    extract_referenced_skill_paths,
    sanitize_reference_content,
    update_skill_name_in_md,
    validate_auxiliary_file,
    validate_skill_file,
)


class TestValidateSkillFile(unittest.TestCase):
    def test_valid_frontmatter(self):
        d = pathlib.Path(tempfile.mkdtemp())
        p = d / "SKILL.md"
        p.write_text("---\nname: demo\n---\n\n# Demo\n\nbody" * 10, encoding="utf-8")
        ok, err = validate_skill_file(p)
        self.assertTrue(ok, err)
        self.assertEqual(err, "")

    def test_missing_frontmatter(self):
        d = pathlib.Path(tempfile.mkdtemp())
        p = d / "SKILL.md"
        p.write_text("# Demo\n\n" + "no frontmatter here at all, just body text " * 5,
                      encoding="utf-8")
        ok, err = validate_skill_file(p)
        self.assertFalse(ok)
        self.assertIn("frontmatter", err)

    def test_missing_name(self):
        d = pathlib.Path(tempfile.mkdtemp())
        p = d / "SKILL.md"
        p.write_text("---\nfoo: bar\n---\n\n# Demo\n" + "x" * 120, encoding="utf-8")
        ok, err = validate_skill_file(p)
        self.assertFalse(ok)
        self.assertIn("name", err)

    def test_empty_auxiliary(self):
        d = pathlib.Path(tempfile.mkdtemp())
        p = d / "ref.md"
        p.write_text("", encoding="utf-8")
        ok, err = validate_auxiliary_file(p)
        self.assertFalse(ok)
        self.assertIn("空", err)


class TestSkillNameUpdate(unittest.TestCase):
    def test_frontmatter_rename(self):
        content = "---\nname: old\n---\n\n# Old\n"
        out = update_skill_name_in_md(content, "new")
        self.assertIn("name: new", out)
        self.assertNotIn("name: old", out)


class TestReferenceSanitize(unittest.TestCase):
    def test_md_link_to_backtick(self):
        content = "see [guide](references/REFERENCE.md) for details"
        out = sanitize_reference_content(content)
        self.assertIn("(`references/REFERENCE.md`)", out)


class TestExtractReferencedPaths(unittest.TestCase):
    def test_extracts_scripts_and_refs(self):
        content = "Run `scripts/build.sh` and see references/REFERENCE.md"
        out = extract_referenced_skill_paths(content)
        self.assertIn("scripts/build.sh", out)
        self.assertIn("references/REFERENCE.md", out)


if __name__ == "__main__":
    unittest.main()
