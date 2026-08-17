#!/usr/bin/env python3
"""Tests for tools/dependency-graph.py cycle semantics (P13).

Verifies: real cycles (delegates_to / invokes / orchestrates) are still
detected, while doc-only backtick mentions are excluded from real cycles.
"""

import importlib.util
import pathlib
import tempfile
import unittest


def load_dg():
    tools_path = (
        pathlib.Path(__file__).resolve().parent.parent.parent.parent.parent
        / "tools" / "dependency-graph.py"
    )
    if not tools_path.exists():
        raise FileNotFoundError(f"dependency-graph.py not found at {tools_path}")
    spec = importlib.util.spec_from_file_location("dg", tools_path)
    dg = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(dg)
    return dg


def make_repo(files):
    """files: {skill_name: SKILL.md_body}"""
    tmp = pathlib.Path(tempfile.mkdtemp())
    sk = tmp / "skills"
    sk.mkdir()
    for name, body in files.items():
        d = sk / name
        d.mkdir()
        (d / "SKILL.md").write_text(body, encoding="utf-8")
    return tmp


class TestCycleDetection(unittest.TestCase):
    def test_real_cycle_detected(self):
        dg = load_dg()
        tmp = make_repo({
            "alpha": "---\nname: alpha\n---\n\nInvoke `beta` to do work.\n",
            "beta": "---\nname: beta\n---\n\ndelegates to: alpha\n",
        })
        skills = dg.find_skills(tmp)
        edges = {n: dg.extract_references(n, tmp) for n in skills}
        real = dg.detect_cycles(list(skills.keys()), edges, dg.REAL_EDGE_KINDS)
        self.assertTrue(real)
        self.assertIn("alpha → beta → alpha", real)

    def test_doc_only_mention_not_real_cycle(self):
        dg = load_dg()
        # benchmark-style: orchestrator -> worker (real), worker mentions
        # orchestrator as "internal component" (doc-only backtick)
        tmp = make_repo({
            "orchestrator": "---\nname: orchestrator\n---\n\nOrchestrates `worker`.\n",
            "worker": "---\nname: worker\n---\n\n通常作为 `orchestrator` 的内部组成部分出现。\n",
        })
        skills = dg.find_skills(tmp)
        edges = {n: dg.extract_references(n, tmp) for n in skills}
        real = dg.detect_cycles(list(skills.keys()), edges, dg.REAL_EDGE_KINDS)
        all_c = dg.detect_cycles(list(skills.keys()), edges, None)
        self.assertFalse(real)
        self.assertTrue(all_c)  # doc-only cycle still visible in ALL view

    def test_review_style_mentions_not_cycles(self):
        dg = load_dg()
        tmp = make_repo({
            "review": "---\nname: review\n---\n\nReplace `review-changes` (lightweight).\n",
            "review-changes": "---\nname: review-changes\n---\n\nUse `review` (workflow) instead.\n",
        })
        skills = dg.find_skills(tmp)
        edges = {n: dg.extract_references(n, tmp) for n in skills}
        real = dg.detect_cycles(list(skills.keys()), edges, dg.REAL_EDGE_KINDS)
        self.assertFalse(real)

    def test_orchestrate_extraction(self):
        dg = load_dg()
        tmp = make_repo({
            "skill-benchmark-generator": "---\nname: skill-benchmark-generator\n---\n\nOrchestrates `routing-benchmark-generator`.\n",
            "routing-benchmark-generator": "---\nname: routing-benchmark-generator\n---\n\nstandalone\n",
        })
        edges = dg.extract_references("skill-benchmark-generator", tmp)
        self.assertIn(("routing-benchmark-generator", "orchestrates"), edges)


if __name__ == "__main__":
    unittest.main()
