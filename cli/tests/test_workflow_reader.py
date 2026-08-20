"""Tests for the shared frontmatter reader + workflow_reader frontmatter-first parsing."""

import tempfile
import unittest
from pathlib import Path

from cli.services import frontmatter, workflow_reader

ROOT = Path(__file__).resolve().parents[2]

SAMPLE = """---
name: demo
workflow:
  inputs:
    required: [A, B]
    optional:
      - name: C
        default: x
      - name: D
next:
  - zz
---
Demo body heading
Purpose body text
"""


class TestFrontmatter(unittest.TestCase):

    def test_extract(self):
        data, body = frontmatter.read_frontmatter(SAMPLE)
        self.assertEqual(data["name"], "demo")
        self.assertEqual(data["workflow"]["inputs"]["required"], ["A", "B"])
        self.assertTrue(body.lstrip().startswith("Demo"))

    def test_none(self):
        text = "# No frontmatter\n## Purpose\nx"
        data, body = frontmatter.read_frontmatter(text)
        self.assertEqual(data, {})
        self.assertEqual(body, text)

    def test_bad_yaml(self):
        data, _ = frontmatter.read_frontmatter("---\n: not: : yaml\n---\nbody")
        self.assertEqual(data, {})


class TestWorkflowReaderInputs(unittest.TestCase):

    def test_frontmatter_authoritative(self):
        required, optional = workflow_reader.parse_inputs(SAMPLE)
        self.assertEqual(required, ["A", "B"])
        self.assertEqual(optional, ["C", "D"])

    def test_frontmatter_defaults(self):
        self.assertEqual(workflow_reader.field_defaults(SAMPLE), {"C": "x"})

    def test_real_bugfix_frontmatter(self):
        text = (ROOT / "workflows" / "bugfix.md").read_text(encoding="utf-8")
        required, optional = workflow_reader.parse_inputs(text)
        self.assertEqual(required, ["Project ID", "Bug Description"])
        self.assertTrue({"Issue ID", "Logs", "Stack Trace", "Mode"} <= set(optional))
        self.assertEqual(workflow_reader.field_defaults(text), {"Mode": "standard"})

    def test_bugfix_frontmatter_equals_legacy(self):
        # 剥离 frontmatter 后回退旧解析，应与 frontmatter 解析一致（等价/无回归）
        text = (ROOT / "workflows" / "bugfix.md").read_text(encoding="utf-8")
        _, body = frontmatter.read_frontmatter(text)
        req_fm, opt_fm = workflow_reader.parse_inputs(text)
        req_leg, opt_leg = workflow_reader.parse_inputs(body)  # no frontmatter → legacy
        self.assertEqual((req_fm, opt_fm), (req_leg, opt_leg))

    def test_legacy_fallback_without_frontmatter(self):
        # 未迁移的 workflow（spec.md 无 frontmatter）仍走旧解析
        text = (ROOT / "workflows" / "spec.md").read_text(encoding="utf-8")
        required, optional = workflow_reader.parse_inputs(text)
        self.assertIsInstance(required, list)
        self.assertIsInstance(optional, list)
        self.assertTrue(required or optional)

    def test_output_base(self):
        self.assertEqual(
            workflow_reader.output_base(ROOT, "bugfix"),
            "outputs/bugfix/{yyMMdd}-{descriptor}/",
        )
        self.assertEqual(
            workflow_reader.output_base(ROOT, "prepare"),
            "workspaces/<change-id>/",
        )
        # 无 outputs 字段 → 空
        self.assertEqual(workflow_reader.output_base(ROOT, "proposal"), "")


if __name__ == "__main__":
    unittest.main()
