"""Pre-commit gate — Python body of .githooks/pre-commit.

Invoked by the thin bash shim (which only probes python3 / python and execs
this file). Performs three gates:

  1. Language check (LANGUAGE_CONVENTION Rule 4, tools/repo-lint.py --files)
     — staged files in the English-discipline zone
     (`templates/runtime/*.md` + `workflows/*.md`)
  2. workflow ↔ runtime contract consistency (tools/check-contract.py)
     — same staged zone files
  3. memory English discipline (governance/memory/**) — staged memory files;
     same rule/source as check.py item 8 (tools/checks/memory.py); blocks a
     commit that would land Chinese into AI-internal memory (recurred 3× before
     this gate existed: 2026-09-16 / 09-18 / 09-21)
  4. secret + injection scan (all staged files) — same source as check.py item
     18 (tools/checks/secret_scan.py). security-policy Principles 1 and 3 had
     no machine execution until P78. S1-S5 block the commit; I1 and S4 are
     surfaced for adjudication because the gate cannot judge them. Needed as a
     separate line from check.py: a secret that reaches a commit is already
     leaked, and CI only sees what was committed.

Exit 0 = pass, 1 = blocked. Escape hatch stays `git commit --no-verify`.
Python body keeps the hook logic unit-testable and platform-neutral (the only
bash left is the 3-line shim, which runs under Git-Bash on Windows).
"""

import re
import subprocess
import sys
from pathlib import Path

ZONE_RE = re.compile(r"^(templates/runtime/|workflows/)[^ ]*\.md$")

MEMORY_RE = re.compile(r"^governance/memory/[^ ]*\.md$")

NO_VERIFY_HINT = "  Fix the flagged issue, or force-commit with: git commit --no-verify"


def git_repo_root():
    """Repo root via git (works from worktrees/subdirs). None if not a repo."""

    r = subprocess.run(
        ["git", "rev-parse", "--show-toplevel"],
        capture_output=True, text=True,
    )

    if r.returncode != 0:
        return None

    return Path(r.stdout.strip())


def staged_files(repo_root, pattern):
    """Staged (added/copied/modified) files matching a path pattern."""

    r = subprocess.run(
        ["git", "-C", str(repo_root), "diff", "--cached", "--name-only",
         "--diff-filter=ACM"],
        capture_output=True, text=True,
    )

    if r.returncode != 0:
        return []

    if pattern is None:                     # 全部 staged（C4：check-contract 需全量列表）
        return [f for f in r.stdout.splitlines() if f]

    return [f for f in r.stdout.splitlines() if pattern.match(f)]


def staged_zone_files(repo_root):
    """Staged (added/copied/modified) files in the English-discipline zone."""

    return staged_files(repo_root, ZONE_RE)


def staged_memory_files(repo_root):
    """Staged memory files (governance/memory/**)."""

    return staged_files(repo_root, MEMORY_RE)


def _run(root, argv):
    """Run a gate tool from repo root; return (returncode, combined output)."""

    r = subprocess.run(argv, cwd=root, capture_output=True, text=True)

    out = r.stdout.rstrip()
    err = r.stderr.rstrip()

    return r.returncode, (out + ("\n" + err if err else ""))


def memory_language_check(files):
    """Return blocked lines for staged memory files carrying CJK."""

    from checks.memory import language_violations

    violations = language_violations(files)

    if not violations:
        return []

    lines = [
        "pre-commit: memory English-discipline check FAILED "
        "(LANGUAGE_CONVENTION: AI System memory must be English)."
    ]

    for rel, cjk in violations:
        lines.append(f"  - {rel}: {cjk} CJK chars")

    lines.append(NO_VERIFY_HINT)

    return lines


def secret_scan_check(files):
    """Return blocked lines for staged files carrying secrets.

    S1-S5 (critical) block the commit: Triage has no authority to release a
    hardcoded credential. I1 (high) and S4 (low) surface as advisories, since
    those require a judgement this gate cannot make.
    """

    from checks.base import Checker
    from checks.secret_scan import check_secret_scan

    c = Checker()
    check_secret_scan(c, files)

    if not c.errors and not c.warnings:
        return []

    lines = [
        "pre-commit: secret + injection scan FAILED "
        "(security-policy Principles 1 and 3)."
    ]

    for e in c.errors:
        lines.append(f"  [BLOCK] {e}")

    for w in c.warnings:
        lines.append(f"  [REVIEW] {w}")

    if c.errors:
        lines.append(NO_VERIFY_HINT)

    return lines


def run_checks(repo_root, files, memory_files=None, staged_all=None):
    """Run the language + contract + memory gates. Returns (blocked, lines)."""

    blocked = False
    lines = []

    if files:

        # 1. 英文纪律区语言检查（LANGUAGE_CONVENTION Rule 4）
        code, out = _run(
            repo_root,
            [sys.executable, "tools/repo-lint.py", "--repo-root", str(repo_root),
             "--files", ",".join(files)],
        )

        if code != 0:
            blocked = True
            lines.append("pre-commit: English-discipline zone language check FAILED (LANGUAGE_CONVENTION Rule 4).")
            if out:
                lines.append(out)
            lines.append(NO_VERIFY_HINT)

        # 2. workflow ↔ runtime 契约一致性
        staged = [p for p in staged_files(repo_root, None)
                  if p.endswith((".md", ".yaml"))]
        code, out = _run(
            repo_root,
            [sys.executable, "tools/check-contract.py",
             "--files", ",".join(staged)],
        )

        if code != 0:
            blocked = True
            lines.append("pre-commit: workflow ↔ runtime contract consistency FAILED.")
            if out:
                lines.append(out)
            lines.append(NO_VERIFY_HINT)

    # 3. memory 英文纪律（governance/memory/**；与 check.py 第 8 项同源）
    if memory_files:

        mem_lines = memory_language_check(memory_files)

        if mem_lines:
            blocked = True
            lines.extend(mem_lines)

    # 4. secret + injection 扫描（check.py 第 18 项同源）。
    #    覆盖全部 staged 文件而非仅 memory 区：secret 可能落在任何文件类型，
    #    而 pre-commit 是唯一一道"提交前"的闸（check.py 只在 CI 跑到）。
    if staged_all:
        sec_lines = secret_scan_check(staged_all)
        if sec_lines:
            blocked = True
            lines.extend(sec_lines)

    return blocked, lines


def main(argv=None):
    repo_root = git_repo_root()

    if repo_root is None:
        print("pre-commit: not inside a git repo", file=sys.stderr)
        return 1

    files = staged_zone_files(repo_root)
    memory_files = staged_memory_files(repo_root)

    staged_all = staged_files(repo_root, None)

    if not files and not memory_files and not staged_all:
        return 0

    blocked, lines = run_checks(repo_root, files, memory_files, staged_all)

    for line in lines:
        print(line)

    return 1 if blocked else 0


if __name__ == "__main__":
    sys.exit(main())
