r"""Scaffold a branch-name parser provider for the bugfix hotfix mode.

Contract owner: templates/runtime/runtime-bugfix.md Phase 4.6.
Gate owner: tools/checks/bugfix_modes.py (check.py item 15).

Usage:
    python tools/branch-parser-scaffold.py init <provider> [--ext-root <path>]
    python tools/branch-parser-scaffold.py --list

Generates (non-destructive, never overwrites existing files):
    extensions/<provider>/scripts/branch_parser.py        contract skeleton
    extensions/<provider>/scripts/branch_parser_test.py   contract tests

The provider then fills the company-specific pattern (e.g. cc{date}) into
branch_parser.py. Do NOT change the script name, method name, or return
fields — the gate and runtime depend on them.

After scaffolding, register the parser in config/workflows/bugfix-modes.yaml
(branch.parser = <provider>) and run:
    python tools/check.py
"""

import argparse
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent

DEFAULT_EXT_ROOT = ROOT.parent / "extensions"

PARSER_TEMPLATE = '''"""Branch name parser — implements the ai-system branch.parser contract.

Contract (templates/runtime/runtime-bugfix.md Phase 4.6):
  method:    parse(branch_name: str) -> ParsedBranch | None
  fields:    ParsedBranch = {date, type, desc, service}  (all str, "" when absent)
  behavior:  unparseable / blank input -> return None (never raise)

Stability: do NOT change the script name, method name, or return fields.
Provider-specific rules (e.g. the cc{date} pattern) live in this file only.
"""

import re
from dataclasses import dataclass


@dataclass
class ParsedBranch:
    date: str = ""      # YYYYMMDD
    type: str = ""      # fix / feat / ...
    desc: str = ""
    service: str = ""


# TODO(provider): 实现公司分支规范，例如 cc20260813_fix_thread_leak_housekeeping-service-api
_BRANCH_RE = re.compile(r"^(.+)$")


def parse(branch_name: str) -> ParsedBranch | None:
    """返回 None 表示无法解析的分支名。"""
    if not branch_name or not branch_name.strip():
        return None
    m = _BRANCH_RE.match(branch_name.strip())
    if not m:
        return None
    # TODO(provider): 将分组映射为 ParsedBranch(date=..., type=..., desc=..., service=...)
    return None
'''

TEST_TEMPLATE = '''"""Contract tests for the branch-name parser (ai-system bugfix hotfix mode).

Contract (templates/runtime/runtime-bugfix.md Phase 4.6):
  parse(branch_name: str) -> ParsedBranch | None
  return fields {date, type, desc, service}
"""

import inspect
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from branch_parser import ParsedBranch, parse  # noqa: E402


def test_contract_signature():
    sig = inspect.signature(parse)
    assert list(sig.parameters) == ["branch_name"], sig


def test_return_fields_match_contract():
    r = parse("__contract_probe__")
    if r is None:
        return  # unparseable -> None is legal
    assert isinstance(r, ParsedBranch)
    fields = set(r.__dataclass_fields__)
    assert fields == {"date", "type", "desc", "service"}, fields


def test_blank_returns_none():
    assert parse("") is None
    assert parse("   ") is None


# TODO(provider): 添加公司规范实例，例如
# def test_cc_pattern():
#     r = parse("cc20260813_fix_thread_leak_housekeeping-service-api")
#     assert r is not None
#     assert r.date == "20260813" and r.type == "fix"
#     assert r.desc == "thread_leak" and r.service == "housekeeping-service-api"
'''


def init_provider(provider: str, ext_root: Path) -> int:
    if not re.match(r"^[a-z0-9]+(-[a-z0-9]+)*$", provider):
        print(f"error: provider '{provider}' must be kebab-case")
        return 2

    ext_dir = ext_root / provider
    scripts_dir = ext_dir / "scripts"
    scripts_dir.mkdir(parents=True, exist_ok=True)

    parser_path = scripts_dir / "branch_parser.py"
    test_path = scripts_dir / "branch_parser_test.py"

    if parser_path.exists() or test_path.exists():
        print(f"error: {parser_path.name} or {test_path.name} already exists; "
              "refusing to overwrite (non-destructive)")
        return 1

    parser_path.write_text(PARSER_TEMPLATE, encoding="utf-8")
    test_path.write_text(TEST_TEMPLATE, encoding="utf-8")

    print(f"scaffolded branch-name parser provider '{provider}':")
    print(f"  {parser_path.relative_to(ROOT.parent)}")
    print(f"  {test_path.relative_to(ROOT.parent)}")
    print()
    print("next steps:")
    print(f"  1. Fill the company-specific pattern into {parser_path.name} "
          "(e.g. cc{{date}}_fix_{{desc}}_{{service}})")
    print(f"  2. Add concrete examples to {test_path.name}")
    print("  3. Register in config/workflows/bugfix-modes.yaml: "
          f"branch.parser = {provider}")
    print("  4. Run: python tools/check.py")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="cmd", required=True)

    init = sub.add_parser("init", help="scaffold a parser provider")
    init.add_argument("provider", help="provider extension name (kebab-case)")
    init.add_argument("--ext-root", type=Path, default=DEFAULT_EXT_ROOT,
                      help=f"extensions root (default: {DEFAULT_EXT_ROOT})")

    sub.add_parser("--list", help="reserved", add_help=False)

    args = parser.parse_args()

    if args.cmd == "init":
        return init_provider(args.provider, args.ext_root)

    print("available providers:")
    for ext_dir in sorted(DEFAULT_EXT_ROOT.glob("*")):
        script = ext_dir / "scripts" / "branch_parser.py"
        if script.is_file():
            print(f"  {ext_dir.name}  ->  {script}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
