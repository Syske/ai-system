#!/usr/bin/env python3
"""MenuConfig tests: project_required target gating (2026-08-18).

Covers the 开发主链 gating config: targets that require a project container
are hidden when the user selects "system (no project)"; only prepare remains
as the project-lifecycle entry. bugfix/hotfix-test-doc are hidden workflows
(AI/Next-triggered), not menu items.

Run:
    python -m unittest cli/tests/test_menu_config.py
"""

import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

from cli.services.menu_config import MenuConfig  # noqa: E402


def _root_with_menu(tmp, menu_text):
    root = Path(tmp)
    cfg = root / "config"
    (cfg / "i18n").mkdir(parents=True)
    (cfg / "menu.yaml").write_text(menu_text, encoding="utf-8")
    (cfg / "i18n" / "zh.yaml").write_text(
        "sections: {}\nfield_notes: {}\n",
        encoding="utf-8",
    )
    (cfg / "providers.yaml").write_text("version: 1\n", encoding="utf-8")
    (cfg / "skill-groups.yaml").write_text("version: 1\n", encoding="utf-8")
    return root


MENU = """\
version: 1
locale: zh
hidden_workflows:
  - bugfix
  - hotfix-test-doc
project_required:
  workflows:
    - spec
    - develop
    - review
    - verify
    - release
    - dev-setup
  commands:
    - trace
sections:
  - title: flow_main
    items:
      - name: prepare
        kind: workflow
  - title: flow_analysis
    items:
      - name: code-review
        kind: workflow
      - name: change-impact
        kind: workflow
"""


class TestProjectRequired(unittest.TestCase):

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = _root_with_menu(self.tmp.name, MENU)

    def tearDown(self):
        self.tmp.cleanup()

    def test_reads_project_required_sets(self):
        cfg = MenuConfig(self.root)
        wf, cmd = cfg.project_required()
        self.assertIn("spec", wf)
        self.assertIn("develop", wf)
        self.assertNotIn("prepare", wf)
        self.assertIn("trace", cmd)

    def test_bugfix_and_hotfix_hidden(self):
        cfg = MenuConfig(self.root)
        self.assertIn("bugfix", cfg.hidden_workflows())
        self.assertIn("hotfix-test-doc", cfg.hidden_workflows())

    def test_missing_project_required_returns_empty(self):
        root = _root_with_menu(
            str(Path(self.tmp.name) / "no-req"),
            MENU.replace("project_required:", "# project_required:").replace(
                "  workflows:", "#   workflows:"
            ).replace("    - spec", "#     - spec"),
        )
        cfg = MenuConfig(root)
        wf, cmd = cfg.project_required()
        self.assertEqual(wf, set())
        self.assertEqual(cmd, set())


if __name__ == "__main__":
    unittest.main()
