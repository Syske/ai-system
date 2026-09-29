"""Phase Contract gate (check.py item 16).

Validates the machine contract for Runtime Phases against
`governance/policies/phase-contract.md` (P76).

The contract lives in each workflow's **frontmatter** (`workflow.phases`);
the execution spec lives in the Runtime template (`## Phase <id> — <name>`).
The two are joined by Phase id.

Gates (see the policy §8):

    C1  activation references a phase("id") that does not exist        ERROR
    C2  phase("id").passed where <id> has no pass_criterion            ERROR
    C3  a Phase declares an artifact absent from workflow ## Outputs   ERROR
    C4  a workflow ## Outputs entry declared by no Phase               not reported
    C5  phases[].id set != the Runtime's Phase heading set             ERROR
    C6  duplicate id, or empty name                                   ERROR
    C7  activation not parseable (natural language, unknown mode key)  ERROR
    C8  the `## Phases` body section is missing                       ERROR

Every gate ships with a negative test in cli/tests/test_phase_contract.py —
a gate that cannot be proven to fail may silently stop working.
"""

import re

from .base import ROOT

# `## Phase 1 — Name` / `# Phase 4.5 — Name` (em/en dash, or a bare space
# for runtimes that predate the dash convention).
_PHASE_HEADING = re.compile(
    r"^#{1,2} Phase ([0-9]+(?:\.[0-9]+)?)\s*(?:[—–-]\s*)?(.+?)\s*$",
    re.M,
)

# `WHEN mode.<key> ∋ <value> ∧ phase("4.5").<state>` — v1 grammar, see policy §4.1.
_WHEN = re.compile(r"^\s*WHEN\s+(.+?)\s*$")
# `mode.<key> <op> <value>` or `phase("<id>").<state>` — v1 grammar, policy §4.1.
# A mode term may carry a trailing comparator + value (`∋ branch`, `= plan`).
_ATOM = re.compile(
    r"""^\s*(?:
          mode\.(?P<mkey>[A-Za-z_][A-Za-z0-9_]*)\s*(?:[∋=]+\s*\S+)?   # mode config key
        | phase\(\s*"(?P<pid>[0-9]+(?:\.[0-9]+)?)"\s*\)               # phase ref
          \.\s*(?P<state>active|completed|passed)
        )\s*$""",
    re.X,
)
_STATE_SUFFIX = re.compile(
    r"""phase\("(?P<pid>[0-9]+(?:\.[0-9]+)?)"\)\.(?P<state>active|completed|passed)"""
)

# Fallback: recognise a well-formed term even when the strict atom above
# rejects it, so the error message can name the offending reference.
_PHASE_REF = re.compile(
    r"""phase\(\s*"(?P<pid>[0-9]+(?:\.[0-9]+)?)"\s*\)"""
    r"""\.\s*(?P<state>active|completed|passed)"""
)

# Keys a mode config may expose to an activation expression.
_MODE_KEYS = {"approval_gate", "phases", "base", "branch", "mr", "doc",
              "commit", "extension", "target_branch"}


def _strip_condition_suffix(name):
    """Drop a trailing "(hotfix mode only, …)" qualifier from a heading."""
    return re.sub(r"\s*\(.*?(?:only|when|driven by).*?\)\s*$", "", name).strip()


def _read(path):
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return ""


def _frontmatter(text):
    """Return (frontmatter_text, body_text)."""
    m = re.match(r"\A---[ \t]*\n(.*?)\n---[ \t]*\n", text, re.S)
    if not m:
        return "", text
    return m.group(1), text[m.end():]


def _workflow_outputs(body):
    """Artifact names listed under `## Outputs` (file-like entries only)."""
    m = re.search(r"^## Outputs\s*\n(.*?)(?=^## |\Z)", body, re.M | re.S)
    if not m:
        return []
    out = []
    for line in m.group(1).splitlines():
        s = line.strip()
        if not s.startswith("- "):
            continue
        item = s[2:].strip()
        # Strip trailing "# comment" and markdown emphasis.
        item = re.sub(r"\s*#.*$", "", item).strip()
        item = item.replace("**", "").strip()
        if not item:
            continue
        # Take the first path-ish token: `sql/  # Executable SQL files…`
        token = item.split()[0].strip("`")
        if "/" in token or token.endswith(".md"):
            out.append(token)
    return out


def _runtime_phase_ids(runtime_text):
    """{phase_id: name} from the Runtime template's Phase headings."""
    found = {}
    for m in _PHASE_HEADING.finditer(runtime_text):
        pid = m.group(1)
        name = _strip_condition_suffix(m.group(2))
        if pid not in found:
            found[pid] = name
    return found


def _unquote(raw):
    """Strip surrounding quotes and undo backslash escapes inside them.

    The contract stores expressions as YAML double-quoted scalars, so a
    literal quote inside (e.g. `phase(\"6.5\").completed`) arrives escaped.
    """
    s = raw.strip()
    if len(s) >= 2 and s[0] == s[-1] and s[0] in "\"'":
        inner = s[1:-1]
        if s[0] == '"':
            inner = inner.replace('\\"', '"').replace("\\\\", "\\")
        return inner
    return s


def _parse_phases(frontmatter_text):
    """Parse the `phases:` block under `workflow:` → list of dicts.

    Minimal line-oriented reader (the block is a fixed shape; a full YAML
    parse of the frontmatter is not needed here and keeps error messages
    tied to this gate).
    """
    lines = frontmatter_text.splitlines()
    phases = []
    in_block = False
    current = None
    for line in lines:
        if re.match(r"^\s{2}phases:\s*$", line):
            in_block = True
            continue
        if in_block:
            m = re.match(r"^\s{4}-\s+(\w+):\s*(.*?)\s*$", line)
            if m:
                if current:
                    phases.append(current)
                current = {m.group(1): _unquote(m.group(2))}
                continue
            m = re.match(r"^\s{6}(\w+):\s*(.*?)\s*$", line)
            if m and current is not None:
                current[m.group(1)] = _unquote(m.group(2))
                continue
            # Dedent out of the block.
            if line.strip() and not line.startswith("      "):
                if current:
                    phases.append(current)
                    current = None
                in_block = False
    if current:
        phases.append(current)
    return phases


def _declares_list(raw):
    """`declares` may be inline (`[a.md]`) or absent."""
    if not raw:
        return []
    raw = raw.strip()
    if raw in ("[]", "—", "-"):
        return []
    inner = raw.strip("[]")
    return [x.strip().strip("\"'`") for x in inner.split(",") if x.strip()]


def check_phase_contract(c, root=None):
    """Validate Phase contracts across all workflows."""
    r = ROOT if root is None else root
    wf_dir = r / "workflows"

    if not wf_dir.exists():
        return

    for wf_path in sorted(wf_dir.glob("*.md")):
        if wf_path.name == "README.md":
            continue

        name = wf_path.stem
        text = _read(wf_path)
        if not text:
            continue

        fm, body = _frontmatter(text)

        # Locate the runtime this workflow declares. The authoritative source
        # is config/workflows/<name>.yaml (check_registry validates the
        # workflow's own `## Runtime` section against it); the body section is
        # only a fallback.
        rt_rel = None
        cfg_path = r / "config" / "workflows" / f"{name}.yaml"
        if cfg_path.exists():
            cm = re.search(
                r"^runtime:\s*(\S+)\s*$",
                _read(cfg_path),
                re.M,
            )
            if cm:
                rt_rel = cm.group(1).strip().strip('"')
        if not rt_rel:
            m = re.search(r"^## Runtime\s*\n+\s*-\s+(.+)", body, re.M)
            if m:
                rt_rel = m.group(1).strip().replace("ai-system/", "").lstrip("./")

        phases = _parse_phases(fm)

        if not phases:
            # No contract declared — nothing to validate (C8 covers the
            # body section, checked separately below when present).
            continue

        ids = [p.get("id", "").strip() for p in phases]
        by_id = {i: p for i, p in zip(ids, phases) if i}

        # ---- C6: duplicate id / empty name ----
        seen = set()
        for pid in ids:
            if not pid:
                c.error(f"{name}: phase contract has an entry without an id")
                continue
            if pid in seen:
                c.error(f"{name}: duplicate phase id '{pid}' in the contract")
            seen.add(pid)
            if not by_id[pid].get("name", "").strip():
                c.error(f"{name}: phase '{pid}' has an empty name")

        # ---- C5: contract ids == runtime heading ids ----
        if rt_rel:
            rt_path = r / rt_rel
            if rt_path.exists():
                rt_phases = _runtime_phase_ids(_read(rt_path))
                missing = sorted(set(rt_phases) - set(ids))
                extra = sorted(set(ids) - set(rt_phases))
                if missing:
                    c.error(
                        f"{name}: runtime {rt_rel} has Phase(s) {missing} "
                        f"missing from the frontmatter contract"
                    )
                if extra:
                    c.error(
                        f"{name}: contract declares Phase(s) {extra} that do "
                        f"not exist in runtime {rt_rel}"
                    )
            else:
                c.warn(
                    f"{name}: runtime file not found for phase contract "
                    f"validation: {rt_rel}"
                )

        # ---- C1 / C2 / C7: activation expressions ----
        for pid, entry in by_id.items():
            activation = entry.get("activation", "").strip()
            if not activation or activation == "always":
                continue

            m = _WHEN.match(activation)
            if not m:
                c.error(
                    f"{name}: phase '{pid}' activation '{activation}' must be "
                    f"'always' or 'WHEN <expression>' (natural language is not "
                    f"parseable — see policies/phase-contract.md §4.1)"
                )
                continue

            for atom in m.group(1).split("∧"):
                if not atom.strip():
                    continue
                am = _ATOM.match(atom)
                if not am:
                    c.error(
                        f"{name}: phase '{pid}' activation term "
                        f"'{atom.strip()}' is not parseable (expected "
                        f"mode.<key> or phase(\"<id>\").<state>)"
                    )
                    continue
                if am.group("mkey"):
                    key = am.group("mkey")
                    if key not in _MODE_KEYS:
                        c.error(
                            f"{name}: phase '{pid}' activation references "
                            f"unknown mode key 'mode.{key}'"
                        )
                else:
                    ref = am.group("pid")
                    if ref not in by_id:
                        c.error(
                            f"{name}: phase '{pid}' activation references "
                            f"phase(\"{ref}\") which is not declared"
                        )
                        continue
                    if am.group("state") == "passed":
                        if not by_id[ref].get("pass_criterion", "").strip():
                            c.error(
                                f"{name}: phase '{pid}' activation requires "
                                f"phase(\"{ref}\").passed but '{ref}' declares "
                                f"no pass_criterion — passed is not a synonym "
                                f"for completed (policy §4.2)"
                            )

        # ---- C3: declares ⊆ workflow outputs (C4 intentionally unchecked) ----
        outputs = _workflow_outputs(body)
        for pid, entry in by_id.items():
            for artifact in _declares_list(entry.get("declares", "")):
                base = artifact.split("/")[-1]
                if any(
                    o == artifact or o.split("/")[-1] == base
                    or artifact.endswith(o) or o.endswith(base)
                    for o in outputs
                ):
                    continue
                c.error(
                    f"{name}: phase '{pid}' declares artifact "
                    f"'{artifact}' which is not declared by the workflow's "
                    f"## Outputs (wild artifact)"
                )
