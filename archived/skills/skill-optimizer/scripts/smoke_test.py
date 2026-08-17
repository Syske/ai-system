#!/usr/bin/env python3
"""End-to-end smoke test for skill-optimizer with a stub LLM.

Runs the full pipeline without any network / API key:
  augment -> snapshot -> validate (all three benchmark shapes) -> tune-description

Exit code 0 = all steps OK. Run:
    python scripts/smoke_test.py
"""

import json
import pathlib
import sys
import tempfile

SCRIPTS_DIR = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPTS_DIR))


def main() -> int:
    from snapshot_manager import SnapshotManager
    from actions import run_augment, run_tune_description, run_validate
    from actions import _propose_candidate

    class StubLLM:
        def __call__(self, prompt, system=None):
            text = (system or "") + "\n" + prompt
            if "held-out validator" in text:
                return "T1: PASS\nT2: PASS\nPASS RATE: 2/2"
            if "tuning the frontmatter" in text:
                return "1) vague\n---\n`Optimize skills via static/dynamic`"
            return "## Examples\n\n- task: A\n  approach: B\n  result: C"

    import actions

    actions._load_llm = lambda: StubLLM()

    work = pathlib.Path(tempfile.mkdtemp())
    skill_dir = work / "demo-skill"
    skill_dir.mkdir()
    (skill_dir / "SKILL.md").write_text(
        "---\nname: demo-skill\n---\n\n# Demo\n\nSome body.\n", encoding="utf-8"
    )

    # 1. augment
    demos = work / "demos.json"
    demos.write_text(json.dumps([{"task": "t", "approach": "a", "result": "r"}]), encoding="utf-8")
    assert run_augment(skill_dir, demos) == 0
    sm = SnapshotManager(skill_dir)
    v1 = sm.get_latest_version()
    assert (sm.snapshots_dir / v1 / "SKILL.md").exists()

    # 2. validate (minimal + routing + outcome shapes)
    bench = work / "bench.json"
    bench.write_text(json.dumps([
        {"task": "t1", "expected_outcome": "o1"},
        {"query": "q1", "expectedSkills": ["demo-skill"]},
        {"standardAnswer": "sa", "rootCauses": ["rc"], "keyActions": ["ka"]},
    ]), encoding="utf-8")
    assert run_validate(skill_dir, bench) == 0

    # 3. tune-description
    assert run_tune_description(skill_dir, None) == 0

    # 4. diff core still importable & generates html
    from diff_core import generate_html, discover_snapshots
    versions = discover_snapshots(sm.snapshots_dir)
    html = generate_html(versions, "demo-skill")
    assert "const DIFF_DATA" in html

    print(f"✅ SMOKE OK — snapshots: {sorted(p.name for p in sm.snapshots_dir.iterdir() if p.is_dir())}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
