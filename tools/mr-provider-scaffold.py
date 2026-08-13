r"""Scaffold an MR-submit provider for the bugfix hotfix mode.

Contract owner: templates/runtime/runtime-bugfix.md Phase 6.6.
Gate owner: tools/checks/bugfix_modes.py (check.py item 15).

Usage:
    python tools/mr-provider-scaffold.py init <provider> [--ext-root <path>]
    python tools/mr-provider-scaffold.py --list

Generates (non-destructive, never overwrites existing files):
    extensions/<provider>/scripts/submit_mr.py        contract skeleton
    extensions/<provider>/scripts/submit_mr_test.py   contract tests

The provider then fills the platform-specific logic (e.g. Codeup OpenAPI).
Do NOT change the script name, method name, or return fields — the gate
and runtime depend on them.

After scaffolding, register the provider in config/workflows/bugfix-modes.yaml
(mr.provider = <provider>) and run:
    python tools/check.py
"""

import argparse
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent

DEFAULT_EXT_ROOT = ROOT.parent / "extensions"

SUBMIT_TEMPLATE = '''"""MR submit provider — implements the ai-system mr.provider contract.

Contract (templates/runtime/runtime-bugfix.md Phase 6.6):
  method:    submit(source_branch, target_branch, title, description)
             -> MrResult | None
  fields:    MrResult = {url, id}
  behavior:  idempotent (existing open MR for source+target -> return it,
             do NOT create a duplicate); failure -> None (never raise)

Stability: do NOT change the script name, method name, or return fields.
Provider-specific logic (API host, credentials, org id) lives here only.
"""

from dataclasses import dataclass


@dataclass
class MrResult:
    url: str = ""
    id: str = ""


def submit(source_branch: str, target_branch: str,
           title: str, description: str) -> MrResult | None:
    """Return the MR (created or reused) or None on failure.

    TODO(provider): implement platform-specific MR creation, e.g.:
      1. resolve repository id by source_branch's remote
      2. list open MRs for source+target; if found, return it
      3. create the MR with title/description; return MrResult(url, id)
    """
    # 探测调用（门禁 importlib 校验契约）——不得创建任何内容。
    if source_branch.startswith("__probe"):
        return None
    return None
'''

TEST_TEMPLATE = '''"""Contract tests for the MR submit provider (bugfix hotfix mode).

Contract (templates/runtime/runtime-bugfix.md Phase 6.6):
  submit(source_branch, target_branch, title, description) -> MrResult | None
  return fields {url, id}
"""

import inspect
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from submit_mr import MrResult, submit  # noqa: E402


def test_contract_signature():
    sig = inspect.signature(submit)
    assert list(sig.parameters) == [
        "source_branch", "target_branch", "title", "description",
    ], sig


def test_probe_returns_none():
    # 探测/失败路径必须返回 None（不抛异常、不创建）
    assert submit("__probe_src__", "__probe_tgt__", "t", "d") is None


def test_return_fields_match_contract():
    r = submit("__probe_src__", "__probe_tgt__", "t", "d")
    if r is None:
        return
    assert isinstance(r, MrResult)
    fields = set(r.__dataclass_fields__)
    assert fields == {"url", "id"}, fields


# TODO(provider): 添加平台实例，例如
# def test_codeup_reuse_existing():
#     r = submit("cc20260813_fix_x_service-api", "master", "t", "d")
#     assert r is not None and r.url
'''


def init_provider(provider: str, ext_root: Path) -> int:
    if not re.match(r"^[a-z0-9]+(-[a-z0-9]+)*$", provider):
        print(f"error: provider '{provider}' must be kebab-case")
        return 2

    ext_dir = ext_root / provider
    scripts_dir = ext_dir / "scripts"
    scripts_dir.mkdir(parents=True, exist_ok=True)

    submit_path = scripts_dir / "submit_mr.py"
    test_path = scripts_dir / "submit_mr_test.py"

    if submit_path.exists() or test_path.exists():
        print(f"error: {submit_path.name} or {test_path.name} already "
              "exists; refusing to overwrite (non-destructive)")
        return 1

    submit_path.write_text(SUBMIT_TEMPLATE, encoding="utf-8")
    test_path.write_text(TEST_TEMPLATE, encoding="utf-8")

    print(f"scaffolded MR provider '{provider}':")
    print(f"  {submit_path.relative_to(ROOT.parent)}")
    print(f"  {test_path.relative_to(ROOT.parent)}")
    print()
    print("next steps:")
    print(f"  1. Fill the platform-specific logic into {submit_path.name}")
    print(f"  2. Add concrete examples to {test_path.name}")
    print("  3. Register in config/workflows/bugfix-modes.yaml: "
          f"mr.provider = {provider}")
    print("  4. Run: python tools/check.py")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="cmd", required=True)

    init = sub.add_parser("init", help="scaffold an MR provider")
    init.add_argument("provider", help="provider extension name (kebab-case)")
    init.add_argument("--ext-root", type=Path, default=DEFAULT_EXT_ROOT,
                      help=f"extensions root (default: {DEFAULT_EXT_ROOT})")

    args = parser.parse_args()

    if args.cmd == "init":
        return init_provider(args.provider, args.ext_root)

    print("available providers:")
    for ext_dir in sorted(DEFAULT_EXT_ROOT.glob("*")):
        script = ext_dir / "scripts" / "submit_mr.py"
        if script.is_file():
            print(f"  {ext_dir.name}  ->  {script}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
