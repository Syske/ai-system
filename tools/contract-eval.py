"""AIC Contract Evaluator V1 — develop Phase 4 (P79).

Evaluates one Phase's `pass_criterion` and emits a three-state verdict with a
durable audit record. Scope is deliberately one Phase: the experiment is
whether AIC can read a deterministic criterion from the Workflow Contract and
execute it independently — not whether it understands the develop workflow.

    python3 tools/contract-eval.py --project P --change C --task T
    python3 tools/contract-eval.py --help

Verdicts: completed (exit 0) / not-satisfied / undetermined (exit 1).

Three properties are load-bearing and each has a test that would fail if it
broke:

- **Persistence is a precondition for the verdict.** A verdict that cannot be
  recorded was never issued. Writing a record and reporting the verdict are one
  operation, not two; if the write fails the result is `undetermined` with
  `record-unwritable` appended to the original evidence.
- **Evidence is ordered and the LAST entry is decisive.** Normally there is
  exactly one. The two-entry form exists only for a failed record write, where
  dropping the original finding would lose why the criterion came out as it
  did. Consumers classify on `evidence[-1].type`.
- **The criterion is read from the Workflow Contract, never supplied by the
  caller.** This evaluator implements exactly one criterion and compares the
  frontmatter text verbatim. A caller that passed the criterion in could hand
  over an easier one, which would void the Phase Contract entirely. A text
  mismatch is `criterion-invalid`, never a fallback to some other check.

The Phase frontmatter is parsed by `checks/phase_contract.py` rather than a
second reader, so "what Phase 4 is" has exactly one definition.
"""

import argparse
import hashlib
import json
import os
import platform
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

TOOLS_DIR = Path(__file__).resolve().parent
REPO_ROOT = TOOLS_DIR.parent
sys.path.insert(0, str(TOOLS_DIR))

from checks.phase_contract import _frontmatter, _parse_phases  # noqa: E402

DEFAULT_WORKFLOW = "develop"
DEFAULT_PHASE = "4"
RECORD_NAME = "contract-eval.jsonl"

# The one criterion this evaluator implements. Verbatim comparison against the
# workflow frontmatter; see the module docstring for why it is not parsed.
KNOWN_CRITERION = (
    "Completion Report for <task> exists "
    "(workspaces/<project>/openspec/changes/<change>/completion-reports/"
    "<task>-completion-report.md)"
)

# Closed set. Consumers may aggregate on these; nothing outside this tuple is
# ever emitted as an evidence type.
EVIDENCE_TYPES = (
    "criterion-missing",
    "criterion-invalid",
    "input-missing",
    "task-card-missing",
    "report-missing",
    "report-found",
    "record-unwritable",
    "evaluator-error",
)

UNSAFE = ("/", "\\", "..")

# Paths are recorded relative to the workspace root: an absolute path would
# embed a machine-local prefix, and this repo forbids treating those as the
# sole evidence for a claim.
REL_PREFIX = "workspaces"


def _ev(kind, **fields):
    if kind not in EVIDENCE_TYPES:
        raise ValueError(f"undeclared evidence type: {kind}")
    out = {"type": kind}
    out.update({k: v for k, v in fields.items() if v is not None})
    return out


def _result(verdict, evidence, **meta):
    if not evidence:
        raise ValueError("a result must carry at least one evidence entry")
    res = {"verdict": verdict, "evidence": evidence}
    res.update({k: v for k, v in meta.items() if v is not None})
    return res


def _bad_input(field, value=None):
    return _result(
        "undetermined", [_ev("input-missing", field=field, value=value)]
    )


def resolve_inputs(workspace, project, change, task):
    """Validate the Input Contract.

    No derivation: project/change/task are explicit or the verdict is
    undetermined. Values are also passed through unnormalised — trimming a
    trailing space here would make "caller typo" and "artifact absent" produce
    the same verdict, which loses the diagnosis.
    """

    for field, value in (("project", project), ("change", change), ("task", task)):
        if not value or not value.strip():
            return None, _bad_input(field)
        if any(part in value for part in UNSAFE) or value.strip() != value:
            return None, _bad_input(field, value)

    ws = Path(workspace)
    if not ws.is_dir():
        return None, _result(
            "undetermined", [_ev("input-missing", field="workspace", value=str(ws))]
        )
    return ws, None


def resolve_criterion(root, workflow, phase):
    """Read the Phase's pass_criterion from the Workflow Contract (SSOT).

    Returns (criterion_text, None) or (None, result-with-criterion-evidence).
    """

    wf = root / "workflows" / f"{workflow}.md"
    if not wf.is_file():
        return None, _result(
            "undetermined", [_ev("criterion-missing", workflow=workflow)]
        )

    fm, _body = _frontmatter(wf.read_text(encoding="utf-8", errors="replace"))

    for entry in _parse_phases(fm):
        if entry.get("id") != phase:
            continue
        text = (entry.get("pass_criterion") or "").strip()
        if not text:
            return None, _result(
                "undetermined",
                [_ev("criterion-missing", workflow=workflow, phase=phase)],
            )
        if text != KNOWN_CRITERION:
            return None, _result(
                "undetermined",
                [_ev("criterion-invalid", workflow=workflow, phase=phase)],
            )
        return text, None

    return None, _result(
        "undetermined",
        [_ev("criterion-missing", workflow=workflow, phase=phase)],
    )


def expected_paths(ws, project, change, task):
    base = ws / REL_PREFIX / project / "openspec" / "changes" / change
    return (
        base / "tasks" / "cards" / f"{task}.md",
        base / "completion-reports" / f"{task}-completion-report.md",
    )


def _rel(ws, path):
    try:
        return path.relative_to(ws).as_posix()
    except ValueError:
        return path.as_posix()


def evaluate(ws, project, change, task):
    """The whole judgment: Task Card present AND its report present.

    Card absence is `task-card-missing` / undetermined, not
    `report-missing` / not-satisfied. The difference is what the verdict
    asserts: "this run did not produce the report" versus "the task you named
    does not exist". The latter is a caller-side input problem, and reporting
    it as an execution failure would file a typo as a missed deliverable.
    """

    card, report = expected_paths(ws, project, change, task)
    card_rel, report_rel = _rel(ws, card), _rel(ws, report)

    if not card.is_file():
        return _result("undetermined", [_ev("task-card-missing", path=card_rel)])

    if not report.is_file():
        return _result("not-satisfied", [_ev("report-missing", path=report_rel)])

    return _result("completed", [_ev("report-found", path=report_rel)])


def execution_id(project, change, task, phase):
    """Derived, not an entity.

    Deterministic for the same input, which is what makes repeated evaluation
    comparable (P79 §9.1 scenario 5). It carries no timestamp by design: a
    second evaluation of the same task yields the same id and appends another
    line, ordered by `ts`. A real Execution entity with state and migration is
    explicitly out of V1.
    """

    raw = f"{project}|{change}|{task}|{phase}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]


def machine_id():
    return platform.node() or "unknown-host"


def record_path(ws, machine):
    return ws / "metrics" / "by-machine" / machine / RECORD_NAME


def append_record(ws, payload):
    """Single write, one trailing newline.

    POSIX appends below PIPE_BUF are atomic, but this repo has no prior
    JSONL-append code to cite, so the guarantee claimed here is the
    implementation fact "one write() call" — not a cross-process locking
    contract. Concurrency is out of V1.
    """

    target = record_path(ws, machine_id())
    try:
        target.parent.mkdir(parents=True, exist_ok=True)
        with open(target, "a", encoding="utf-8") as fh:
            fh.write(json.dumps(payload, ensure_ascii=False) + "\n")
    except OSError:
        return False
    return True


def finalize(result, ws, **meta):
    """Attach audit metadata, persist, then return the effective verdict.

    Persistence precedes reporting: an unrecorded verdict was never issued.
    The original evidence is kept and the write failure is appended after it,
    so a `not-satisfied` that could not be recorded still shows why.
    """

    payload = dict(result)
    payload.update(meta)
    payload["ts"] = datetime.now(timezone.utc).isoformat(timespec="seconds")

    if not append_record(ws, payload):
        # Carry the audit metadata across, but NOT the verdict: `payload` was
        # seeded from `result`, so copying it wholesale would restore
        # "completed" and the write failure would return exit 0 — a false pass
        # through the exact door this function exists to close.
        carried = {k: v for k, v in payload.items()
                   if k not in ("verdict", "evidence")}
        failed = _result(
            "undetermined",
            list(result["evidence"])
            + [_ev("record-unwritable", path=_rel(ws, record_path(ws, machine_id())))],
        )
        failed.update(carried)
        return failed

    return result


PREFIX = {
    "completed": "[PASSED]",
    "not-satisfied": "[NOT-SATISFIED]",
    "undetermined": "[UNDETERMINED]",
}


def report(result, workflow, phase):
    """Human-facing line. Not a machine protocol: the prose carries no
    key/value grammar, and a test asserts the output stays unparseable."""

    last = result["evidence"][-1]
    detail = last.get("path") or last.get("field") or ""
    suffix = f" {detail}" if detail else ""
    print(
        f"{PREFIX[result['verdict']]} {workflow} Phase {phase}: "
        f"{last['type']}{suffix}"
    )


def run(ws, project, change, task, workflow, phase):
    _criterion, failure = resolve_criterion(REPO_ROOT, workflow, phase)
    if failure is not None:
        return finalize(failure, ws)
    result = evaluate(ws, project, change, task)
    return finalize(
        result, ws,
        project=project, change=change, task=task, phase=phase,
        workflow=workflow, execution_id=execution_id(project, change, task, phase),
    )


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--project", help="explicit project id (never derived)")
    ap.add_argument("--change", help="explicit change id (never derived)")
    ap.add_argument("--task", help="explicit task id (never derived)")
    ap.add_argument("--workflow", default=DEFAULT_WORKFLOW)
    ap.add_argument("--phase", default=DEFAULT_PHASE)
    ap.add_argument("--workspace", help="defaults to the machine's workspace root")
    args = ap.parse_args(argv)

    ws_root = None
    if args.workspace:
        ws_root = Path(args.workspace)
    else:
        from runtime_state import workspace_root
        ws_root = workspace_root()

    ws, failure = resolve_inputs(ws_root, args.project, args.change, args.task)
    if failure is not None:
        ws = ws_root
    else:
        try:
            result = run(ws, args.project, args.change, args.task, args.workflow, args.phase)
        except Exception as exc:  # noqa: BLE001 - fail-closed, see below
            result = _result("undetermined", [_ev("evaluator-error", problem=type(exc).__name__)])
            result = finalize(result, ws_root)
        report(result, args.workflow, args.phase)
        return 0 if result["verdict"] == "completed" else 1

    report(failure, args.workflow, args.phase)
    return 1


if __name__ == "__main__":
    sys.exit(main())
