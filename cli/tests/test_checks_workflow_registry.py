#!/usr/bin/env python3
"""tools/checks/workflow.py 注册表校验的 fail-open 回归测试。

来源：2026-09-21 外部盲检 T4（交叉评委 glm-5.3 提出，已核实）。
缺陷：`ROOT / wf.get(key, "")` 在注册表条目缺 `workflow:`/`runtime:` 键时退化为
`ROOT / ""` == ROOT（目录，`.exists()` 恒真）→ 校验静默通过（fail-open），
且 `check_workflow_runtime_section` 随后 `read_text` 会抛 IsADirectoryError。

Run:
    python -m unittest cli/tests/test_checks_workflow_registry.py
"""

import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "tools"))

from checks import Checker                     # noqa: E402
from checks import workflow as wf_mod          # noqa: E402


class TestRegistryFailOpen(unittest.TestCase):

    def setUp(self):
        self._td = tempfile.TemporaryDirectory()
        self.root = Path(self._td.name)
        (self.root / "config" / "workflows").mkdir(parents=True)
        (self.root / "workflows").mkdir()
        (self.root / "config" / "workflow-registry.yaml").write_text(
            "workflows:\n  demo: config/workflows/demo.yaml\n", encoding="utf-8"
        )
        self._old_root = wf_mod.ROOT
        wf_mod.ROOT = self.root

    def tearDown(self):
        wf_mod.ROOT = self._old_root
        self._td.cleanup()

    def _wf(self, body: str):
        (self.root / "config" / "workflows" / "demo.yaml").write_text(
            body, encoding="utf-8"
        )

    def _errors(self) -> list:
        c = Checker()
        wf_mod.check_registry(c)
        return c.errors

    def test_missing_workflow_key_is_reported(self):
        # 缺 workflow: 键 → 修复前 ROOT / "" 恒存在 → 无任何错误（fail-open）
        self._wf("runtime: templates/runtime/demo.md\n")
        errors = self._errors()
        self.assertTrue(
            any("missing 'workflow' key" in e for e in errors),
            f"应当报缺键错误，实际 errors={errors}",
        )

    def test_missing_runtime_key_is_reported(self):
        self._wf("workflow: workflows/demo.md\n")
        errors = self._errors()
        self.assertTrue(
            any("missing 'runtime' key" in e for e in errors),
            f"应当报缺键错误，实际 errors={errors}",
        )

    def test_present_but_nonexistent_path_is_reported(self):
        self._wf("workflow: workflows/nope.md\nruntime: templates/runtime/nope.md\n")
        errors = self._errors()
        self.assertTrue(
            any("'workflows/nope.md' missing" in e for e in errors), errors
        )
        self.assertTrue(
            any("'templates/runtime/nope.md' missing" in e for e in errors), errors
        )

    def test_valid_entry_has_no_missing_errors(self):
        self._wf("workflow: workflows/demo.md\nruntime: templates/runtime/demo.md\n")
        (self.root / "workflows" / "demo.md").write_text(
            "# Demo\n\n## Runtime\n\n- templates/runtime/demo.md\n", encoding="utf-8"
        )
        rt = self.root / "templates" / "runtime"
        rt.mkdir(parents=True)
        (rt / "demo.md").write_text(
            "# Runtime: Demo\n\n# Outputs\n\n- reports/x.md\n", encoding="utf-8"
        )
        errors = self._errors()
        self.assertFalse(
            [e for e in errors if "missing" in e],
            f"注册完整条目不应报 missing，实际 errors={errors}",
        )