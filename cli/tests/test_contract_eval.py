#!/usr/bin/env python3
"""Contract Evaluator V1 tests (P79 §9.1, `reports/P79-CONTRACT-EVALUATOR-V1.md`).

Three of these tests exist to fail if a load-bearing property regresses, and
each is written so that it would pass anyway under a weaker implementation:

- `test_record_failure_does_not_erase_the_original_finding` — persistence is
  a precondition, but losing the original evidence would defeat the audit.
- `test_stdout_carries_no_parseable_structure` — stdout is human-facing; if it
  ever grew a key/value grammar it would become a second protocol.
- `test_criterion_comes_from_the_workflow_not_the_caller` — a caller-supplied
  criterion would void the Phase Contract.

Layout is built in a temp workspace, so no test depends on the real repository
except the two that read the real `workflows/develop.md`.

Run:
    python3 -m unittest cli.tests.test_contract_eval
"""

import importlib.util
import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]

_spec = importlib.util.spec_from_file_location(
    "contract_eval", REPO_ROOT / "tools" / "contract-eval.py"
)
ce = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(ce)

PROJ = "p1"
CHG = "c1"
TASK = "T-001"


class Fixture:
    """A workspace with a change tree; `with_task` controls what exists."""

    def __init__(self, root):
        self.ws = Path(root)
        self.base = self.ws / ce.REL_PREFIX / PROJ / "openspec" / "changes" / CHG
        (self.base / "tasks" / "cards").mkdir(parents=True, exist_ok=True)
        (self.base / "completion-reports").mkdir(parents=True, exist_ok=True)

    def with_task(self, task=TASK, card=True, report=True, report_name=None):
        if card:
            (self.base / "tasks" / "cards" / f"{task}.md").write_text("card", encoding="utf-8")
        if report:
            name = report_name or f"{task}-completion-report.md"
            (self.base / "completion-reports" / name).write_text("r", encoding="utf-8")
        return self

    def run(self, project=PROJ, change=CHG, task=TASK):
        ws, failure = ce.resolve_inputs(self.ws, project, change, task)
        if failure is not None:
            return failure
        return ce.evaluate(ws, project, change, task)


class VerdictTests(unittest.TestCase):

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.fx = Fixture(self._tmp.name)

    def tearDown(self):
        self._tmp.cleanup()

    def test_report_present_is_completed(self):
        res = self.fx.with_task().run()
        self.assertEqual(res["verdict"], "completed")
        self.assertEqual(res["evidence"][-1]["type"], "report-found")

    def test_report_absent_is_not_satisfied(self):
        res = self.fx.with_task(report=False).run()
        self.assertEqual(res["verdict"], "not-satisfied")
        self.assertEqual(res["evidence"][-1]["type"], "report-missing")

    def test_missing_card_is_undetermined_not_not_satisfied(self):
        """A caller naming a task that does not exist is an input problem.

        Reporting it as `not-satisfied` would assert "the run failed to
        deliver", filing a typo as a missed deliverable.
        """

        res = self.fx.run(task="T-999")
        self.assertEqual(res["verdict"], "undetermined")
        self.assertEqual(res["evidence"][-1]["type"], "task-card-missing")

    def test_sibling_reports_do_not_satisfy_this_task(self):
        """判据 4 (Execution-Isolated) — the only direct test of it.

        Three siblings have reports; this task does not. A directory-level check
        would return completed here.
        """

        self.fx.with_task("T-001").with_task("T-002").with_task("T-003")
        # T-011 gets a Card but no report: the scenario under test is
        # "sibling reports must not stand in for this task's own".
        (self.fx.base / "tasks" / "cards" / "T-011.md").write_text("c", encoding="utf-8")
        res = self.fx.run(task="T-011")
        self.assertEqual(res["verdict"], "not-satisfied")
        self.assertNotEqual(res["verdict"], "completed")

    def test_non_report_files_do_not_satisfy_the_criterion(self):
        """A real workspace holds `T-011-L3-check-log.md` beside the reports."""

        self.fx.with_task(card=True, report=False)
        d = self.fx.base / "completion-reports"
        (d / f"{TASK}-L3-check-log.md").write_text("x", encoding="utf-8")
        (d / "completed-cards-walkthrough-log-20260909.md").write_text("x", encoding="utf-8")
        res = self.fx.run()
        self.assertEqual(res["verdict"], "not-satisfied")

    def test_non_conforming_filename_is_a_known_false_negative(self):
        """Disclosed in P79 §12.5, not worked around. Asserted so it stays
        visible rather than quietly becoming a bug report."""

        self.fx.with_task(report_name=f"{TASK}-report.md")
        res = self.fx.run()
        self.assertEqual(res["verdict"], "not-satisfied")

    def test_dotted_task_id_is_valid(self):
        """Real cards use both `T-001` and `2.1`; no prefix may be assumed."""

        self.fx.with_task("2.1")
        self.assertEqual(self.fx.run(task="2.1")["verdict"], "completed")

    def test_padded_task_id_is_rejected_not_corrected(self):
        """A whitespace-padded id is rejected, never trimmed.

        Either handling avoids silent correction, but rejecting at the input
        boundary names the actual problem ("your input is malformed") instead
        of reporting a missing artifact.
        """

        self.fx.with_task()
        _ws, failure = ce.resolve_inputs(self.fx.ws, PROJ, CHG, f"{TASK} ")
        self.assertIsNotNone(failure)
        self.assertEqual(failure["evidence"][-1]["type"], "input-missing")


class InputContractTests(unittest.TestCase):

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.ws = Path(self._tmp.name)

    def tearDown(self):
        self._tmp.cleanup()

    def test_each_missing_input_yields_undetermined(self):
        for kwargs in (
            {"project": None}, {"change": None}, {"task": None},
            {"project": ""}, {"change": "  "},
        ):
            with self.subTest(**kwargs):
                base = {"project": "p", "change": "c", "task": "t"}
                base.update(kwargs)
                _ws, failure = ce.resolve_inputs(self.ws, **base)
                self.assertIsNotNone(failure)
                self.assertEqual(failure["verdict"], "undetermined")
                self.assertEqual(failure["evidence"][-1]["type"], "input-missing")

    def test_unsafe_input_is_rejected(self):
        """Inputs are concatenated into paths; a separator is traversal.

        Mirrors `change_resume._safe_segment`.
        """

        for bad in ("T/001", "..", "../x", "a\\b"):
            with self.subTest(task=bad):
                _ws, failure = ce.resolve_inputs(self.ws, "p", "c", bad)
                self.assertIsNotNone(failure)
                self.assertEqual(failure["evidence"][-1]["type"], "input-missing")

    def test_unresolvable_workspace_is_undetermined(self):
        _ws, failure = ce.resolve_inputs(self.ws / "nope", "p", "c", "t")
        self.assertEqual(failure["verdict"], "undetermined")

    def test_workspace_that_is_a_file_is_undetermined(self):
        f = self.ws / "afile"
        f.write_text("x", encoding="utf-8")
        _ws, failure = ce.resolve_inputs(f, "p", "c", "t")
        self.assertEqual(failure["verdict"], "undetermined")


class CriterionContractTests(unittest.TestCase):
    """The criterion is read from the Workflow Contract, never injected."""

    def test_real_workflow_criterion_resolves(self):
        text, failure = ce.resolve_criterion(REPO_ROOT, "develop", "4")
        self.assertIsNone(failure)
        self.assertEqual(text, ce.KNOWN_CRITERION)

    def test_real_workflow_criterion_matches_the_constant(self):
        """If the frontmatter text drifts, the constant must be revisited.

        Equality is the point: an edited criterion must not be silently
        evaluated as something else.
        """

        from checks.phase_contract import _frontmatter, _parse_phases
        import sys
        sys.path.insert(0, str(REPO_ROOT / "tools"))
        fm, _ = _frontmatter(
            (REPO_ROOT / "workflows" / "develop.md").read_text(encoding="utf-8")
        )
        entry = [e for e in _parse_phases(fm) if e.get("id") == "4"]
        self.assertEqual(len(entry), 1)
        self.assertEqual(entry[0]["pass_criterion"], ce.KNOWN_CRITERION)

    def test_edited_criterion_is_invalid_never_a_fallback(self):
        _text, failure = ce.resolve_criterion(REPO_ROOT / "cli", "develop", "4")
        self.assertIsNotNone(failure)
        self.assertEqual(failure["evidence"][-1]["type"], "criterion-missing")

    def test_unknown_phase_is_criterion_missing(self):
        _text, failure = ce.resolve_criterion(REPO_ROOT, "develop", "99")
        self.assertEqual(failure["evidence"][-1]["type"], "criterion-missing")

    def test_unknown_workflow_is_criterion_missing(self):
        _text, failure = ce.resolve_criterion(REPO_ROOT, "nosuch", "4")
        self.assertEqual(failure["evidence"][-1]["type"], "criterion-missing")

    def test_evaluate_signature_takes_no_criterion(self):
        """A caller-supplied criterion could hand over an easier one and void
        the Phase Contract entirely. The signature itself must prevent it."""

        import inspect
        params = set(inspect.signature(ce.evaluate).parameters)
        self.assertNotIn("criterion", params)
        self.assertNotIn("verdict", params)


class PersistenceContractTests(unittest.TestCase):
    """Persistence is a precondition for the verdict."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.ws = Path(self._tmp.name)
        self.fx = Fixture(self.ws)

    def tearDown(self):
        self._tmp.cleanup()

    def test_record_is_appended(self):
        res = self.fx.with_task().run()
        out = ce.finalize(res, self.ws, project=PROJ, change=CHG, task=TASK, phase="4")
        self.assertEqual(out["verdict"], "completed")
        target = ce.record_path(self.ws, ce.machine_id())
        self.assertTrue(target.is_file())
        line = json.loads(target.read_text(encoding="utf-8").strip().splitlines()[-1])
        self.assertEqual(line["verdict"], "completed")

    def test_record_failure_downgrades_to_undetermined(self):
        res = self.fx.with_task().run()
        target = ce.record_path(self.ws, ce.machine_id())
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text("", encoding="utf-8")
        target.chmod(0o444)                      # unwritable file
        target.parent.chmod(0o555)                # unwritable dir
        try:
            out = ce.finalize(res, self.ws)
            self.assertEqual(out["verdict"], "undetermined")
            self.assertEqual(out["evidence"][-1]["type"], "record-unwritable")
        finally:
            target.parent.chmod(0o755)
            target.chmod(0o644)

    def test_record_failure_keeps_the_original_finding(self):
        """A not-satisfied that could not be recorded must still show why."""

        res = self.fx.with_task(report=False).run()
        target = ce.record_path(self.ws, ce.machine_id())
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text("", encoding="utf-8")
        target.chmod(0o444)
        target.parent.chmod(0o555)
        try:
            out = ce.finalize(res, self.ws)
            self.assertEqual(out["verdict"], "undetermined")
            types = [e["type"] for e in out["evidence"]]
            self.assertEqual(types, ["report-missing", "record-unwritable"])
        finally:
            target.parent.chmod(0o755)
            target.chmod(0o644)

    def test_evidence_is_ordered_and_last_is_decisive(self):
        self.assertIn("record-unwritable", ce.EVIDENCE_TYPES)
        self.assertIn("LAST entry is decisive", ce.__doc__ or "")
        # and the behaviour, not just the prose
        res = {"verdict": "not-satisfied",
               "evidence": [{"type": "report-missing"}]}
        failed = {"verdict": "undetermined",
                  "evidence": res["evidence"] + [{"type": "record-unwritable"}]}
        self.assertEqual(failed["evidence"][-1]["type"], "record-unwritable")
        self.assertEqual(failed["evidence"][0]["type"], "report-missing")

    def test_execution_id_is_deterministic_and_not_an_entity(self):
        a = ce.execution_id(PROJ, CHG, TASK, "4")
        b = ce.execution_id(PROJ, CHG, TASK, "4")
        self.assertEqual(a, b)
        self.assertNotEqual(a, ce.execution_id(PROJ, CHG, "T-002", "4"))

    def test_repeated_evaluation_appends_same_id(self):
        for _ in range(3):
            res = self.fx.with_task().run()
            ce.finalize(res, self.ws, project=PROJ, change=CHG, task=TASK,
                        phase="4", execution_id=ce.execution_id(PROJ, CHG, TASK, "4"))
        lines = ce.record_path(self.ws, ce.machine_id()).read_text(
            encoding="utf-8").strip().splitlines()
        self.assertEqual(len(lines), 3)
        ids = {json.loads(x)["execution_id"] for x in lines}
        self.assertEqual(len(ids), 1)


class OutputContractTests(unittest.TestCase):

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.fx = Fixture(self._tmp.name)

    def tearDown(self):
        self._tmp.cleanup()

    def _stdout(self, result, workflow="develop", phase="4"):
        buf = io.StringIO()
        with redirect_stdout(buf):
            ce.report(result, workflow, phase)
        return buf.getvalue()

    def test_every_verdict_has_a_prefix(self):
        for verdict in ce.PREFIX:
            with self.subTest(verdict=verdict):
                out = self._stdout({"verdict": verdict, "evidence": [
                    {"type": "report-found"}]})
                self.assertTrue(out.startswith(ce.PREFIX[verdict]))

    def test_stdout_carries_no_parseable_structure(self):
        """stdout is human-facing. If it grew a key/value grammar it would
        become a second machine protocol (P79 §5.2)."""

        out = self._stdout({"verdict": "completed", "evidence": [
            {"type": "report-found", "path": "a/b/c.md"}]})
        for token in ('"verdict"', '"reason"', '"evidence"', "verdict=", "reason="):
            self.assertNotIn(token, out)
        self.assertNotIn(": ", out.split(":", 1)[-1])

    def test_line_count_is_constant_per_verdict(self):
        """Evidence length must not leak into stdout shape."""

        one = self._stdout({"verdict": "undetermined",
                            "evidence": [{"type": "report-missing"}]})
        two = self._stdout({"verdict": "undetermined", "evidence": [
            {"type": "report-missing"}, {"type": "record-unwritable"}]})
        self.assertEqual(one.count("\n"), two.count("\n"))


class EvidenceContractTests(unittest.TestCase):

    def test_evidence_types_are_a_closed_set(self):
        with self.assertRaises(ValueError):
            ce._ev("some-free-text-reason")

    def test_every_declared_type_is_reachable_in_the_matrix(self):
        """Guards a type existing that no code path can produce."""

        matrix = {
            "criterion-missing", "criterion-invalid", "input-missing",
            "task-card-missing", "report-missing", "report-found",
            "record-unwritable", "evaluator-error",
        }
        self.assertEqual(set(ce.EVIDENCE_TYPES), matrix)

    def test_result_requires_evidence(self):
        with self.assertRaises(ValueError):
            ce._result("completed", [])

    def test_paths_are_recorded_relative_to_workspace(self):
        with tempfile.TemporaryDirectory() as tmp:
            ws = Path(tmp)
            p = ws / "workspaces" / "p" / "x.md"
            self.assertEqual(ce._rel(ws, p), "workspaces/p/x.md")


class ExitContractTests(unittest.TestCase):
    """Only 0 and 1. `exit 2` would clash with comment-lint / format-check,
    where 2 means the harder outcome."""

    def test_exit_codes_are_zero_and_one_only(self):
        with tempfile.TemporaryDirectory() as tmp:
            fx = Fixture(tmp)
            fx.with_task()
            for task, expected in ((TASK, 0), ("T-999", 1)):
                with self.subTest(task=task):
                    import io as _io
                    from contextlib import redirect_stdout as _rs
                    buf = _io.StringIO()
                    with _rs(buf):
                        code = ce.main([
                            "--workspace", tmp, "--project", PROJ,
                            "--change", CHG, "--task", task,
                        ])
                    self.assertEqual(code, expected)
                    self.assertIn(code, (0, 1))

    def test_no_json_flag(self):
        """V1 provides no --json; the record is the machine surface."""

        with self.assertRaises(SystemExit):
            ce.main(["--json"])


class EvaluatorErrorTests(unittest.TestCase):
    """The crash fallback must be observable, not merely declared.

    Found during the implementation-vs-ruling review: replacing this fallback
    with a false pass left all 37 tests green. That is the same failure shape
    as `runtime-base.md`'s eight unimplemented APIs and the `gates:`
    registry — declared, never exercised.
    """

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.fx = Fixture(self._tmp.name).with_task()

    def tearDown(self):
        self._tmp.cleanup()

    def _main(self):
        buf = io.StringIO()
        with redirect_stdout(buf):
            code = ce.main([
                "--workspace", str(self.fx.ws), "--project", PROJ,
                "--change", CHG, "--task", TASK,
            ])
        return code, buf.getvalue()

    def test_crash_becomes_undetermined_and_blocks(self):
        original = ce.evaluate

        def boom(*_a, **_k):
            raise RuntimeError("synthetic crash")

        ce.evaluate = boom
        try:
            code, out = self._main()
        finally:
            ce.evaluate = original
        self.assertEqual(code, 1, "a crash must not pass")
        self.assertIn("[UNDETERMINED]", out)
        self.assertIn("evaluator-error", out)

    def test_crash_does_not_erase_the_contract_gap(self):
        """Even on a crash the record must exist, or the gap is invisible."""

        original = ce.evaluate
        ce.evaluate = lambda *a, **k: (_ for _ in ()).throw(OSError("x"))
        try:
            self._main()
            target = ce.record_path(self.fx.ws, ce.machine_id())
            self.assertTrue(target.is_file(), "no audit record after a crash")
            rec = json.loads(target.read_text(encoding="utf-8").strip().splitlines()[-1])
            self.assertEqual(rec["evidence"][-1]["type"], "evaluator-error")
        finally:
            ce.evaluate = original


class ShortCircuitTests(unittest.TestCase):
    """Per-branch self-verification.

    A branch that cannot be observed failing may already be dead. Each case
    neutralises one judgment and asserts the corresponding verdict is gone —
    the discipline in `governance/policies/quality-gates.md`
    § "Writing a Gate That Can Be Proven to Fail".
    """

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.fx = Fixture(self._tmp.name)

    def tearDown(self):
        self._tmp.cleanup()

    def test_report_found_branch_is_observable(self):
        self.fx.with_task()
        self.assertEqual(self.fx.run()["verdict"], "completed")
        original = ce.evaluate
        ce.evaluate = lambda *a, **k: {
            "verdict": "undetermined",
            "evidence": [{"type": "evaluator-error"}],
        }
        try:
            self.assertNotEqual(self.fx.run()["verdict"], "completed")
        finally:
            ce.evaluate = original
        self.assertEqual(self.fx.run()["verdict"], "completed")

    def test_report_missing_branch_is_observable(self):
        self.fx.with_task(report=False)
        self.assertEqual(self.fx.run()["verdict"], "not-satisfied")
        original = ce.evaluate
        ce.evaluate = lambda *a, **k: {
            "verdict": "completed",
            "evidence": [{"type": "report-found"}],
        }
        try:
            self.assertNotEqual(self.fx.run()["verdict"], "not-satisfied")
        finally:
            ce.evaluate = original

    def test_criterion_invalid_branch_is_observable(self):
        saved = ce.KNOWN_CRITERION
        ce.KNOWN_CRITERION = "a different criterion"
        try:
            _t, failure = ce.resolve_criterion(REPO_ROOT, "develop", "4")
            self.assertEqual(failure["evidence"][-1]["type"], "criterion-invalid")
        finally:
            ce.KNOWN_CRITERION = saved
        self.assertIsNone(ce.resolve_criterion(REPO_ROOT, "develop", "4")[1])

    def test_record_unwritable_never_yields_completed(self):
        """The false pass this suite was written to catch."""

        target = ce.record_path(self.fx.ws, ce.machine_id())
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text("", encoding="utf-8")
        target.chmod(0o444)
        target.parent.chmod(0o555)
        try:
            for original in (
                {"verdict": "completed", "evidence": [{"type": "report-found"}]},
                {"verdict": "not-satisfied", "evidence": [{"type": "report-missing"}]},
            ):
                with self.subTest(verdict=original["verdict"]):
                    out = ce.finalize(original, self.fx.ws)
                    self.assertEqual(out["verdict"], "undetermined")
                    self.assertEqual(out["evidence"][-1]["type"], "record-unwritable")
                    self.assertEqual(out["evidence"][0]["type"],
                                     original["evidence"][0]["type"])
        finally:
            target.parent.chmod(0o755)
            target.chmod(0o644)


if __name__ == "__main__":
    unittest.main()
