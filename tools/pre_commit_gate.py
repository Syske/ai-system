"""Pre-commit gate — Python body of .githooks/pre-commit.

Invoked by the thin bash shim (which only probes python3 / python and execs
this file). Performs two gates on staged files in the English-discipline zone
(`templates/runtime/*.md` + `workflows/*.md`):

  1. Language check (LANGUAGE_CONVENTION Rule 4, tools/repo-lint.py --files)
  2. workflow ↔ runtime contract consistency (tools/check-contract.py)

Exit 0 = pass, 1 = blocked. Escape hatch stays `git commit --no-verify`.
Python body keeps the hook logic unit-testable and platform-neutral (the only
bash left is the 3-line shim, which runs under Git-Bash on Windows).
"""

import re
import subprocess
import sys
from pathlib import Path

ZONE_RE = re.compile(r"^(templates/runtime/|workflows/)[^ ]*\.md$")

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


def staged_zone_files(repo_root):
    """Staged (added/copied/modified) files in the English-discipline zone."""

    r = subprocess.run(
        ["git", "-C", str(repo_root), "diff", "--cached", "--name-only",
         "--diff-filter=ACM"],
        capture_output=True, text=True,
    )

    if r.returncode != 0:
        return []

    return [f for f in r.stdout.splitlines() if ZONE_RE.match(f)]


def _run(root, argv):
    """Run a gate tool from repo root; return (returncode, combined output)."""

    r = subprocess.run(argv, cwd=root, capture_output=True, text=True)

    out = r.stdout.rstrip()
    err = r.stderr.rstrip()

    return r.returncode, (out + ("\n" + err if err else ""))


def run_checks(repo_root, files):
    """Run language + contract gates. Returns (blocked: bool, lines: list[str])."""

    if not files:
        return False, []

    blocked = False
    lines = []

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
    code, out = _run(
        repo_root,
        [sys.executable, "tools/check-contract.py"],
    )

    if code != 0:
        blocked = True
        lines.append("pre-commit: workflow ↔ runtime contract consistency FAILED.")
        if out:
            lines.append(out)
        lines.append(NO_VERIFY_HINT)

    return blocked, lines


def main(argv=None):
    repo_root = git_repo_root()

    if repo_root is None:
        print("pre-commit: not inside a git repo", file=sys.stderr)
        return 1

    files = staged_zone_files(repo_root)

    if not files:
        return 0

    blocked, lines = run_checks(repo_root, files)

    for line in lines:
        print(line)

    return 1 if blocked else 0


if __name__ == "__main__":
    sys.exit(main())
