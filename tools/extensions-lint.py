r"""Lint the extensions directory (company/platform skill extensions).

CONTRACT ENGINE — this tool contains NO company-specific conventions.
It loads them from the extensions-side rules file:

    <extensions-root>/extension-rules.yaml

(provider-side implementation, per ADR-0009 principle 6: contract in
ai-system, implementation in extensions). The extensions repo owns the
rules; ai-system only executes them. Change a convention -> edit the YAML,
not this tool.

Usage:
    python tools/extensions-lint.py [--ext-root <path>] [--json] [--verbose]
    python tools/extensions-lint.py --fix-missing-log   # scaffold missing logs
    python tools/extensions-lint.py --rules <path>      # override rules file

Checks (all driven by extension-rules.yaml):
1. Required files per extension: SKILL.md / OPTIMIZATION_LOG.md
   (parser_providers exempt).
2. No forbidden artifacts tracked (sensitive/debug patterns).
3. No compiled artifacts tracked (suffixes).
4. kebab-case directory names.

Exit code 0 = no errors (warnings allowed); 1 = errors found.

Registered in tools/README.md (check_tools_readme gate).
"""

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
DEFAULT_EXT_ROOT = ROOT.parent / "extensions"

DEFAULT_RULES_FILE = "extension-rules.yaml"

KUBE_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")

DEFAULT_RULES = {
    "require_skill_md": [],
    "require_opt_log": [],
    "parser_providers": [],
    "non_skill_domains": [],
    "forbidden_artifacts": [],
    "forbidden_suffixes": [],
    "kebab_case": False,
}


def _load_rules(ext_root: Path, rules_arg: str | None) -> dict:
    """Load the provider-side rules file (YAML).

    Falls back to empty rules when the file is missing — the engine stays
    generic; conventions live in extensions/extension-rules.yaml.
    """
    if rules_arg:
        path = Path(rules_arg)
    else:
        path = ext_root / DEFAULT_RULES_FILE

    if not path.exists():
        print(f"[INFO] rules file not found: {path} "
              "(no conventions applied; engine-only run)")
        return dict(DEFAULT_RULES)

    import yaml
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    except Exception as exc:
        print(f"[ERROR] cannot parse rules {path}: {exc}")
        return dict(DEFAULT_RULES)

    rules = dict(DEFAULT_RULES)
    for key in rules:
        if key in data:
            rules[key] = data[key]
    return rules


def _matches(name: str, patterns) -> bool:
    import fnmatch
    return any(fnmatch.fnmatch(name, p) for p in patterns)


def _matches_path(rel: str, pattern: str) -> bool:
    """Match a tracked file path against a forbidden-artifact pattern.

    Patterns may be a bare name (tmp_docs, credentials.json), a glob
    (*_debug_*), or a path fragment (scripts/x). Matching is exact per
    path segment to avoid fnmatch's over-broad '*' matching arbitrary
    files (e.g. '*_debug_*' must not match 'yapi.py').
    """
    import fnmatch
    pat = pattern.rstrip("/")
    # 精确段匹配（裸名如 credentials.json / tmp_docs）
    parts = rel.split("/")
    if pat in parts:
        return True
    # 路径片段匹配（scripts/x, dir/sub）
    if "/" in pat and pat in rel:
        return True
    # 段级通配（*_debug_* 等）与整路径通配
    for part in parts:
        if fnmatch.fnmatch(part, pat):
            return True
    if fnmatch.fnmatch(rel, pat):
        return True
    return False


def _matches_suffix(rel: str, suffix: str) -> bool:
    """Compiled-artifact suffix match (path segment or file suffix)."""
    if suffix.startswith("."):
        return rel.endswith(suffix)
    return suffix in rel.split("/")



def _tracked_files(ext_dir: Path) -> list[str]:
    """Git-tracked file paths relative to the extension dir.

    Falls back to disk scan when not inside a git repo."""
    repo_root = None
    cur = ext_dir
    while True:
        if (cur / ".git").exists():
            repo_root = cur
            break
        if cur.parent == cur:
            break
        cur = cur.parent

    if repo_root is None:
        return [
            f.relative_to(ext_dir).as_posix()
            for f in ext_dir.rglob("*")
            if f.is_file()
        ]

    out = subprocess.run(
        ["git", "-C", str(repo_root), "ls-files"],
        capture_output=True, text=True,
    ).stdout
    result = []
    for line in out.splitlines():
        p = (repo_root / line).resolve()
        if str(p).startswith(str(ext_dir.resolve())):
            result.append(p.relative_to(ext_dir.resolve()).as_posix())
    return result


class Results:
    def __init__(self):
        self.errors = []
        self.warnings = []

    def error(self, msg):
        self.errors.append(msg)

    def warn(self, msg):
        self.warnings.append(msg)


def check_extension(ext_dir: Path, rules: dict, res: Results, verbose: bool):
    name = ext_dir.name

    is_parser = _matches(name, rules["parser_providers"])

    is_non_skill = _matches(name, rules["non_skill_domains"])

    if rules.get("kebab_case") and not KUBE_RE.match(name):
        res.error(f"{name}: directory name must be kebab-case (got '{name}')")

    has_skill = (ext_dir / "SKILL.md").exists()

    # 1. required files (parser providers + non-skill domains exempt)
    if not is_parser and not is_non_skill:
        if _matches(name, rules["require_skill_md"]) and not has_skill:
            res.warn(
                f"{name}: missing SKILL.md (required by "
                f"{DEFAULT_RULES_FILE})"
            )
        if _matches(name, rules["require_opt_log"]) and \
                not (ext_dir / "OPTIMIZATION_LOG.md").exists():
            res.warn(
                f"{name}: missing OPTIMIZATION_LOG.md "
                f"(required by {DEFAULT_RULES_FILE}) — run "
                "extensions-lint.py --fix-missing-log to scaffold"
            )
    elif verbose:
        res.warn(f"{name}: parser provider (scripts only), files not required")

    # 2+3. forbidden tracked artifacts
    forbidden = rules["forbidden_artifacts"]
    suffixes = rules["forbidden_suffixes"]
    for rel in _tracked_files(ext_dir):
        for pat in forbidden:
            if _matches_path(rel, pat):
                res.error(f"{name}: forbidden artifact tracked: {rel}")
                break
        if any(_matches_suffix(rel, s) for s in suffixes):
            res.error(f"{name}: compiled artifact tracked: {rel}")


def scaffold_missing_logs(ext_root: Path, rules: dict) -> int:
    created = 0
    for ext_dir in sorted(ext_root.iterdir()):
        if not ext_dir.is_dir():
            continue
        name = ext_dir.name
        if _matches(name, rules["parser_providers"]):
            continue
        if _matches(name, rules.get("non_skill_domains", [])):
            continue
        if _matches(name, rules["require_opt_log"]) and \
                not (ext_dir / "OPTIMIZATION_LOG.md").exists():
            log = ext_dir / "OPTIMIZATION_LOG.md"
            log.write_text(
                "# OPTIMIZATION_LOG\n\n"
                "<!-- 每次实战优化后在顶部追加一条记录。"
                "字段: 触发场景/问题清单与根因/改动内容/验证结果/影响评估/"
                "复现与回归建议 (extensions/README.md) -->\n",
                encoding="utf-8",
            )
            print(f"scaffolded {log.relative_to(ext_root)}")
            created += 1
    print(f"created {created} OPTIMIZATION_LOG.md (empty templates)")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ext-root", type=Path, default=DEFAULT_EXT_ROOT,
                        help=f"extensions root (default: {DEFAULT_EXT_ROOT})")
    parser.add_argument("--rules", default=None,
                        help="override rules file path")
    parser.add_argument("--json", action="store_true", help="JSON output")
    parser.add_argument("--verbose", action="store_true", help="verbose")
    parser.add_argument("--fix-missing-log", action="store_true",
                        help="scaffold missing OPTIMIZATION_LOG.md templates")
    args = parser.parse_args()

    rules = _load_rules(args.ext_root, args.rules)

    if args.fix_missing_log:
        return scaffold_missing_logs(args.ext_root, rules)

    res = Results()

    if not args.ext_root.is_dir():
        res.error(f"extensions root not found: {args.ext_root}")
        _report(res, args.json)
        return 1

    for d in sorted(
        d for d in args.ext_root.iterdir()
        if d.is_dir() and not d.name.startswith(".")
    ):
        check_extension(d, rules, res, args.verbose)

    _report(res, args.json)
    return 1 if res.errors else 0


def _report(res: Results, as_json: bool):
    if as_json:
        print(json.dumps({
            "errors": res.errors,
            "warnings": res.warnings,
            "error_count": len(res.errors),
            "warning_count": len(res.warnings),
        }, ensure_ascii=False, indent=2))
        return

    for w in res.warnings:
        print(f"  [WARN] {w}")
    for e in res.errors:
        print(f"  [ERROR] {e}")
    print(
        f"Summary: {len(res.errors)} errors, "
        f"{len(res.warnings)} warnings"
    )


if __name__ == "__main__":
    sys.exit(main())
