#!/usr/bin/env python3
"""knowledge-metric tests (P71 §5.9 observation-period reader).

This tool exists for one reason beyond reporting: it makes two disciplines
**mechanical instead of remembered**. A rate is never printed without its
denominator, and a sub-floor zero is reported as insufficient rather than as
failure. Both are output-format properties, so they are tested at the format
level — a test that only checked the arithmetic would pass while the
discipline quietly regressed.

Run:
    python3 -m unittest cli.tests.test_knowledge_metric
"""

import json
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]

# The tool is `knowledge-metric.py`, hyphenated like its siblings
# (`repo-metrics.py`, `maintain-delta.py`), so it loads by path rather than by
# module name. Renaming it to an underscore would diverge from the convention
# those two already set.
import importlib.util  # noqa: E402

_spec = importlib.util.spec_from_file_location(
    "knowledge_metric", REPO_ROOT / "tools" / "knowledge-metric.py"
)
km = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(km)


def write_store(workspace, machine, records):
    d = Path(workspace) / "metrics" / "by-machine" / machine
    d.mkdir(parents=True, exist_ok=True)
    lines = [json.dumps(r, ensure_ascii=False) for r in records]
    (d / "knowledge-runs.jsonl").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return d


def rec(ts, generated=0, triaged=0, runs=None, by_type=None):
    return {
        "ts": ts,
        "machine": "m1",
        "watermark": f"{ts}-wm",
        "counts": {
            "generated": generated, "triaged": triaged, "promoted": 0,
            "redirected": 0, "discarded": 0,
        },
        "runs": runs or {},
        "by_type": by_type or {},
        "files": [],
    }


class StoreTests(unittest.TestCase):

    def test_empty_workspace_reports_nothing_observed(self):
        """Absence of data must be stated, not rendered as zeros."""

        with tempfile.TemporaryDirectory() as ws:
            self.assertEqual(km.read_snapshots(ws), {})

    def test_missing_store_returns_zero_exit(self):
        """No snapshots is a normal state, not an error to fail on."""

        with tempfile.TemporaryDirectory() as ws:
            self.assertEqual(km.main(["--workspace", ws]), 0)

    def test_corrupt_line_is_skipped_not_fatal(self):
        """An interrupted append must not lose the whole history."""

        with tempfile.TemporaryDirectory() as ws:
            d = write_store(ws, "m1", [rec("2026-09-01")])
            with open(d / "knowledge-runs.jsonl", "a", encoding="utf-8") as fh:
                fh.write('{"ts": "2026-09-02", "counts": {gen\n')
            got = km.read_snapshots(ws)
            self.assertEqual(len(got["m1"]), 1)

    def test_accumulates_across_inspections(self):
        with tempfile.TemporaryDirectory() as ws:
            write_store(ws, "m1", [
                rec("2026-09-01", generated=2, triaged=2,
                    runs={"develop": 2}, by_type={"develop": 2}),
                rec("2026-09-02", generated=1, triaged=1,
                    runs={"develop": 3}, by_type={"develop": 1}),
            ])
            s = km.summarize(km.read_snapshots(ws)["m1"])
            self.assertEqual(s["inspections"], 2)
            self.assertEqual(s["counts"]["generated"], 3)
            self.assertEqual(s["runs"]["develop"], 5)
            self.assertEqual(s["by_type"]["develop"], 3)

    def test_machines_are_isolated(self):
        """Two machines must never sum into one series.

        The denominator store is per-machine precisely because
        `metrics/maintain-<date>.json` collides across machines.
        """

        with tempfile.TemporaryDirectory() as ws:
            write_store(ws, "m1", [rec("2026-09-01", generated=1,
                                       runs={"develop": 1})])
            write_store(ws, "m2", [rec("2026-09-01", generated=5,
                                       runs={"develop": 9})])
            got = km.read_snapshots(ws)
            self.assertEqual(sorted(got), ["m1", "m2"])
            self.assertEqual(km.summarize(got["m1"])["counts"]["generated"], 1)
            self.assertEqual(km.summarize(got["m2"])["counts"]["generated"], 5)


class RateCellTests(unittest.TestCase):

    def test_zero_always_carries_its_denominator(self):
        """`0/1` and `0/22` read identically without the n. That is the bug."""

        self.assertIn("(0/22)", km.rate_cell(0, 22))
        self.assertIn("(0/1)", km.rate_cell(0, 1))

    def test_no_runs_is_not_a_zero(self):
        cell = km.rate_cell(3, 0)
        self.assertNotIn("0/", cell)
        self.assertIn("n/a", cell)


class SampleFloorTests(unittest.TestCase):
    """A zero below the floor is uninformative and must not read as failure."""

    def _row(self, n, attributed):
        import io
        from contextlib import redirect_stdout

        buf = io.StringIO()
        with redirect_stdout(buf):
            km.print_report(
                {"m1": {
                    "inspections": 1, "window": ["t0", "t0"],
                    "counts": {"generated": attributed, "triaged": 0,
                               "promoted": 0, "redirected": 0, "discarded": 0},
                    "runs": {k: n if k == "develop" else 0 for k in km.RUN_TYPES},
                    "run_total": n, "by_type": {"develop": attributed},
                }},
                {"develop": attributed},
            )
        for line in buf.getvalue().splitlines():
            if line.strip().startswith("develop"):
                return line
        self.fail("no develop row in output")

    def test_below_floor_zero_is_insufficient(self):
        self.assertIn("insufficient sample", self._row(2, 0))

    def test_at_or_above_floor_zero_is_a_finding(self):
        self.assertIn("ENTRY UNUSED", self._row(6, 0))

    def test_capture_above_floor_is_observed(self):
        self.assertIn("capture observed", self._row(6, 2))


class AttributionTests(unittest.TestCase):

    def test_missing_by_type_says_not_attributable(self):
        """Never divide a total by one type's n.

        Dividing the overall `generated` by a single type's run count produces
        rates above 1 — the numerator/denominator mismatch P71 warns about.
        """

        import io
        from contextlib import redirect_stdout

        buf = io.StringIO()
        with redirect_stdout(buf):
            km.print_report(
                {"m1": {
                    "inspections": 1, "window": ["t0", "t0"],
                    "counts": {"generated": 3, "triaged": 0, "promoted": 0,
                               "redirected": 0, "discarded": 0},
                    "runs": {"develop": 7, "review": 1, "bugfix": 0,
                             "change-impact": 0},
                    "run_total": 8, "by_type": {},
                }},
                {},
            )
        out = buf.getvalue()
        self.assertIn("not attributable", out)
        self.assertNotIn("3.00", out)

    def test_untriaged_candidates_are_flagged(self):
        """Captured but never triaged is a stalled loop, not a quiet success."""

        import io
        from contextlib import redirect_stdout

        buf = io.StringIO()
        with redirect_stdout(buf):
            km.print_report(
                {"m1": {
                    "inspections": 1, "window": ["t0", "t0"],
                    "counts": {"generated": 4, "triaged": 0, "promoted": 0,
                               "redirected": 0, "discarded": 0},
                    "runs": {"develop": 4}, "run_total": 4,
                    "by_type": {"develop": 4},
                }},
                {"develop": 4},
            )
        self.assertIn("never triaged", buf.getvalue())


class SchemaDocTests(unittest.TestCase):
    """The module docstring is the schema contract for whoever writes the JSONL."""

    def test_docstring_documents_every_field(self):
        doc = km.__doc__
        for field in ("ts", "machine", "watermark", "counts", "by_type", "files"):
            self.assertIn(f'"{field}"', doc)

    def test_every_run_type_is_covered(self):
        for t in ("develop", "review", "bugfix", "change-impact"):
            self.assertIn(t, km.RUN_TYPES)

    def test_runtimes_declare_the_attribution_field(self):
        """If the runtime does not ask for Origin Workflow, by_type stays empty.

        The per-type rate is only as good as the field that feeds it; a
        missing instruction upstream silently degrades every downstream read.
        """

        for name in km.RUN_TYPES:
            p = REPO_ROOT / "templates" / "runtime" / f"runtime-{name}.md"
            text = p.read_text(encoding="utf-8")
            self.assertIn("## Experience Candidates", text, name)
            self.assertIn("Origin Workflow", text, name)

    def test_guidelines_declare_six_mandatory_fields(self):
        text = (REPO_ROOT / "governance" / "memory" / "MEMORY_GUIDELINES.md").read_text(
            encoding="utf-8"
        )
        self.assertIn("Six fields are mandatory", text)
        for field in ("- What:", "- Why:", "- Source:",
                      "- Candidate Category:", "- Origin Workflow:"):
            self.assertIn(field, text)


if __name__ == "__main__":
    unittest.main()
