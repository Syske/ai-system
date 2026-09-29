"""knowledge-metric — read-only view of the P71 Experience Inbox observation period.

Reads the per-machine JSONL snapshots written by `aic-maintain` step 2.6 and
prints the capture-rate lower bound. It creates and modifies nothing: the JSONL
is the only structured source, so this tool never parses free text (P77 §14.4
path C rejected exactly that).

    python3 tools/knowledge-metric.py --workspace <ws>
    python3 tools/knowledge-metric.py --workspace <ws> --json

The JSONL schema is written in one pass per inspection:

    {"ts": "...", "machine": "...", "watermark": "...",
     "counts": {"generated": 3, "triaged": 3, "promoted": 1,
                "redirected": 1, "discarded": 1},
     "by_type": {"develop": 2, "review": 1},
     "runs":   {"develop": 7, "review": 6, "bugfix": 1, "change-impact": 2},
     "files":  ["develop-20260929-165225.md", ...]}

The JSONL is written by an agent following a schema, so a missing or malformed
key is an ordinary occurrence rather than a programming error. Missing run types
degrade to zero and missing `by_type` degrades to "not attributable"; neither
raises. A reader that crashes on a hand-written record becomes a reader nobody
runs.

`files` is kept verbatim so the run counts stay auditable — a number whose
inputs are not recorded cannot be questioned.

Two disciplines are enforced by the output format rather than by prose:

- **A rate is never printed without its n.** `0/1` and `0/22` are both "the
  capture rate is zero"; only the second is a finding. Printing them the same
  way is how an unexamined zero becomes an accepted conclusion.
- **A type below the sample floor is reported as insufficient, not as failure.**
  At n < 4 a zero cannot distinguish "the entry point is unused" from "those
  runs happened to contain no experience".
"""

import argparse
import json
import platform
import sys
from pathlib import Path

RUN_TYPES = ("develop", "review", "bugfix", "change-impact")

# Tied to P71 §5.8 condition 1 (four consecutive inspections make a metric
# collectable). Below this, a zero is not evidence — see module docstring.
SAMPLE_FLOOR = 4


def machine_id():
    return platform.node() or "unknown-host"


def store_dir(workspace):
    return Path(workspace) / "metrics" / "by-machine"


def read_snapshots(workspace):
    """Return {machine: [record, ...]} for every machine that has a store."""

    base = store_dir(workspace)
    out = {}
    if not base.is_dir():
        return out
    for d in sorted(base.iterdir()):
        f = d / "knowledge-runs.jsonl"
        if not f.is_file():
            continue
        records = []
        for lineno, line in enumerate(f.read_text(encoding="utf-8").splitlines(), 1):
            line = line.strip()
            if not line:
                continue
            try:
                records.append(json.loads(line))
            except json.JSONDecodeError as exc:
                print(
                    f"knowledge-metric: skipping {d.name}:{lineno} "
                    f"({exc}) — the line was not appended atomically",
                    file=sys.stderr,
                )
        if records:
            out[d.name] = records
    return out


def summarize(records):
    counts = {"generated": 0, "triaged": 0, "promoted": 0,
              "redirected": 0, "discarded": 0}
    runs = {t: 0 for t in RUN_TYPES}
    by_type = {}
    inspections = len(records)
    first = records[0].get("ts", "?")
    last = records[-1].get("ts", "?")

    for rec in records:
        for k, v in (rec.get("counts") or {}).items():
            if k in counts:
                counts[k] += int(v or 0)
        for k, v in (rec.get("runs") or {}).items():
            if k in runs:
                runs[k] += int(v or 0)
        for k, v in (rec.get("by_type") or {}).items():
            by_type[k] = by_type.get(k, 0) + int(v or 0)

    return {
        "inspections": inspections,
        "window": [first, last],
        "counts": counts,
        "runs": runs,
        "run_total": sum(runs.values()),
        "by_type": by_type,
    }


def rate_cell(generated, n):
    """A rate is only printed with its denominator attached."""

    if n <= 0:
        return "n/a (0 runs)"
    return f"{generated / n:.2f}  (0/{n})" if generated == 0 else f"{generated / n:.2f}  ({generated}/{n})"


def print_report(per_machine, per_type):
    for machine, s in sorted(per_machine.items()):
        print(f"\n=== {machine} — {s['inspections']} inspection(s), "
              f"{s['window'][0]} → {s['window'][1]}")
        c, runs = s["counts"], s["runs"]
        print("  counts : " + "  ".join(f"{k}={v}" for k, v in c.items()))
        print("  runs   : " + "  ".join(f"{k}={runs.get(k, 0)}" for k in RUN_TYPES))
        gen = c["generated"]
        total = s.get("run_total", sum(runs.get(k, 0) for k in RUN_TYPES))
        print(f"  capture rate (lower bound) = {rate_cell(gen, total)}")
        print("  per type — attributed, a zero below the floor is not evidence:")
        for k in RUN_TYPES:
            n = runs.get(k, 0)
            attributed = per_type.get(k)
            if attributed is None:
                cell = "not attributable"
                verdict = "record `by_type` (candidate needs its origin workflow)"
            else:
                cell = rate_cell(attributed, n)
                verdict = (
                    "insufficient sample" if n < SAMPLE_FLOOR
                    else ("ENTRY UNUSED" if attributed == 0 else "capture observed")
                )
            print(f"    {k:<15} {cell:<22} {verdict}")
        if c["triaged"] == 0 and gen > 0:
            print("  WARNING: candidates were captured but never triaged — "
                  "the loop stalled, not the entry point")

    total_gen = sum(s["counts"]["generated"] for s in per_machine.values())
    total_runs = sum(s["run_total"] for s in per_machine.values())
    if len(per_machine) > 1:
        print(f"\n=== all machines: capture rate (lower bound) = "
              f"{rate_cell(total_gen, total_runs)}")
        print("  Per-machine rows above are more informative than this total: "
              "a machine with no runs dilutes it without adding evidence.")


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--workspace", required=True,
                    help="workspace root containing metrics/by-machine/")
    ap.add_argument("--json", action="store_true", help="machine-readable output")
    args = ap.parse_args(argv)

    snapshots = read_snapshots(args.workspace)

    if not snapshots:
        print(
            f"knowledge-metric: no snapshots under "
            f"{store_dir(args.workspace)}.\n"
            "  The store is created by the first aic-maintain run that performs "
            "the P71 5.9 denominator snapshot. Nothing has been observed yet."
        )
        return 0

    per_machine = {m: summarize(r) for m, r in snapshots.items()}
    per_type = {}
    for s in per_machine.values():
        for k, v in s["by_type"].items():
            per_type[k] = per_type.get(k, 0) + v

    if args.json:
        print(json.dumps(
            {"sample_floor": SAMPLE_FLOOR, "machines": per_machine},
            indent=2, ensure_ascii=False,
        ))
        return 0

    print_report(per_machine, per_type)
    print("\nP71 §5.8 release conditions for P77 §6 are in "
          "reports/P77-HINDSIGHT-EVALUATION.md §13.5. Conditions 1-2 and 4 are "
          "readable from this table; condition 3 (a canonical entry actually "
          "reused) has no data source by design and must be recorded by hand.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
