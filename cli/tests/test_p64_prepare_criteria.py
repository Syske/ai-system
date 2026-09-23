#!/usr/bin/env python3
"""P64 回归测试 —— spec 前置条件（"Prepare completed"）的 SSOT 不得再分叉。

P64 背景（2026-09-23 部分 Implemented）：同一前置条件曾有两处表述且指向不同产物，
runtime 侧更用 `proposal.md` 作替代 —— 而 `proposal.md` 是 OpenSpec 自有文件、**恒存在**，
于是该前置检查**永远不可能 FAIL**（未 prepare 的变更静默放行）。

本测试固化修复后的形状：
- `workflows/prepare.md` → `## Exit Criteria` → `### Completion Criteria (consumed by spec)` 是唯一定义；
- `workflows/spec.md` 的 Preconditions 只**引用**，不重述具体产物清单；
- `templates/runtime/runtime-spec.md` 的 Pre-flight 不再把 `proposal.md` 当作满足条件；
- `templates/runtime/runtime-prepare.md` 不复制契约条款，且禁止把报告写进 OpenSpec 的 `proposal.md`。

Run:
    python -m unittest cli.tests.test_p64_prepare_criteria
"""

import re
import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]

PREPARE = REPO_ROOT / "workflows" / "prepare.md"
SPEC = REPO_ROOT / "workflows" / "spec.md"
RUNTIME_SPEC = REPO_ROOT / "templates" / "runtime" / "runtime-spec.md"
RUNTIME_PREPARE = REPO_ROOT / "templates" / "runtime" / "runtime-prepare.md"

CRITERIA_HEADING = "### Completion Criteria (consumed by spec)"


def _text(p):
    return p.read_text(encoding="utf-8")


class TestSSOTShape(unittest.TestCase):

    def test_唯一定义在_prepare_的_Exit_Criteria_内(self):
        text = _text(PREPARE)
        self.assertIn(CRITERIA_HEADING, text)
        # 必须位于 ## Exit Criteria 与下一个 ## 之间（不得新增顶层小节：workflows/README.md 契约）
        exit_at = text.index("## Exit Criteria")
        criteria_at = text.index(CRITERIA_HEADING)
        self.assertLess(exit_at, criteria_at)
        next_top = text.find("\n## ", criteria_at)
        self.assertTrue(next_top == -1 or "## Next" in text[criteria_at:next_top + 8])

    def test_定义体含四条判定项(self):
        body = _text(PREPARE).split(CRITERIA_HEADING, 1)[1]
        for needle in ("prepare/preparation-report.md", "skipped", "Legacy", "Grandfathering"):
            self.assertIn(needle, body, needle)

    def test_spec_precondition_只引用不重述(self):
        pre = _text(SPEC).split("## Preconditions", 1)[1].split("##", 1)[0]
        self.assertIn("prepare.md", pre)
        # 不得再出现"独立判定"的旧措辞或产物清单
        self.assertNotIn("Preparation Report available", pre)
        self.assertNotIn("Requirement Summary", pre)

    def test_运行时不把_proposal_md_当满足条件(self):
        text = _text(RUNTIME_SPEC)
        preflight = text.split("## Pre-flight", 1)[1].split("\n## ", 1)[0]
        self.assertIn("Completion Criteria", preflight)
        # 旧写法：`proposal.md`（或 Preparation Report）存在即可 → 恒真
        self.assertNotIn("(or the current change's Preparation Report)", preflight)
        self.assertIn("always exists", preflight)

    def test_运行时不再复制契约条款(self):
        outs = _text(RUNTIME_PREPARE).split("## Outputs", 1)[1].split("\n## ", 1)[0]
        self.assertIn("Completion Criteria", outs)
        self.assertNotIn("Generate (required — consumed by spec):", outs)

    def test_禁止写进_openspec_的_proposal_md(self):
        self.assertIn("Never write the Preparation Report into the change's OpenSpec `proposal.md`",
                      _text(RUNTIME_PREPARE))


class TestDecisionTable(unittest.TestCase):
    """把新口径实现为判定器：构造场景断言判定结果（含决定性反例）。"""

    PREP_TITLE_RE = re.compile(r"^#\s*(Preparation Report|准备报告)", re.M)
    SKIP_RE = re.compile(r"^-\s*\*\*Prepare\*\*:\s*skipped\s*\(([^)]*)\)", re.I | re.M)

    def _decision(self, change: Path, effective_ts: float):
        rep = change / "prepare" / "preparation-report.md"
        if rep.is_file() and rep.read_text(encoding="utf-8").strip():
            return "PASS"
        prop = change / "proposal.md"
        if prop.is_file():
            text = prop.read_text(encoding="utf-8")
            m = self.SKIP_RE.search(text)
            if m:
                return "PASS(skip)" if m.group(1).strip() else "STOP"
            if self.PREP_TITLE_RE.search(text):
                return "WARN(legacy)"
            if prop.stat().st_mtime < effective_ts:
                return "WARN(grandfather)"
        return "STOP"

    def test_判定表(self):
        import os
        import tempfile
        import time

        effective = time.mktime(time.strptime("2026-09-23", "%Y-%m-%d"))
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)

            def mk(name, files, old=False):
                ch = base / name / "openspec" / "changes" / name
                ch.mkdir(parents=True)
                for rel, content in files.items():
                    p = ch / rel
                    p.parent.mkdir(parents=True, exist_ok=True)
                    p.write_text(content, encoding="utf-8")
                if old:
                    ts = effective - 86400
                    for p in ch.rglob("*"):
                        os.utime(p, (ts, ts))
                return ch

            done = mk("done", {"prepare/preparation-report.md": "# Report\nbody\n"})
            missing = mk("missing", {"proposal.md": "# 意图\n"})
            skipped = mk("skipped", {"proposal.md": "# 意图\n\n- **Prepare**: skipped (纯文档改动)\n"})
            empty = mk("empty", {"proposal.md": "# 意图\n\n- **Prepare**: skipped ()\n"})
            legacy = mk("legacy", {"proposal.md": "# 准备报告 / Preparation Report\n内容\n"})
            grand = mk("grand", {"proposal.md": "# 意图\n"}, old=True)

            self.assertEqual(self._decision(done, effective), "PASS")
            # 决定性反例：旧实现因 proposal.md 存在而放行；新口径必须 STOP
            self.assertEqual(self._decision(missing, effective), "STOP")
            self.assertEqual(self._decision(skipped, effective), "PASS(skip)")
            self.assertEqual(self._decision(empty, effective), "STOP")
            self.assertEqual(self._decision(legacy, effective), "WARN(legacy)")
            self.assertEqual(self._decision(grand, effective), "WARN(grandfather)")


if __name__ == "__main__":
    unittest.main()