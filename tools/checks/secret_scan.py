"""Secret and instruction-injection structural detection.

ai-secret-scan: allow-file

This module carries every detector pattern as a literal, so it necessarily
matches its own rules. The marker is explicit and greppable; the gate never
infers an exemption.

Single source for two rules that `governance/policies/security-policy.md`
states but never had machine execution for (proposal P78):

- S1-S5  secret / credential forms      -> ERROR (not negotiable by Triage)
- I1    instruction-injection structure -> WARN  (Triage must adjudicate)

Two deliberate limits, both recorded in P78:

1. `Checker` has only `error` / `warn`, and `check.py` can only exit 0/1, so
   there is no QUARANTINE state to write into. Severity instead encodes *who
   may overrule the finding*: ERROR = Triage has no authority to release it,
   WARN = a human must adjudicate before the content is promoted.
2. I1 does not decide whether text is an injection. Deciding that requires
   intent judgement, and this gate layer carries no LLM dependency and no
   semantic precedent (ADR-0009 determinism, cf. P76 "Runtime must be
   deterministic"). I1 only flags shape that warrants adjudication.

Known gap: a fixed rule set cannot cover unknown vendor token formats. This
lowers risk; it does not guarantee safety.
"""

import re
from pathlib import Path

from .base import ROOT

MARKER_LINE = "ai-secret-scan: allow"
MARKER_FILE = "ai-secret-scan: allow-file"

# Machine layer. P29 made this the authoritative location for machine
# credentials, so scanning it would make the gate unusable rather than safer.
EXCLUDED_PREFIXES = (
    ".git/",
    "__pycache__/",
    "node_modules/",
    ".venv/",
    "build/",
    "dist/",
)

EXCLUDED_NAMES = (".env", "id_rsa", "id_dsa", "id_ecdsa", "id_ed25519")

SENSITIVE_SUFFIXES = (".pem", ".key", ".p12", ".pfx", ".jks")

SCAN_SUFFIXES = (
    ".md", ".py", ".yaml", ".yml", ".json", ".toml", ".cfg", ".ini",
    ".sh", ".bash", ".txt", ".java", ".ts", ".js", ".tsx", ".jsx",
    ".html", ".xml", ".sql", ".properties",
)

PLACEHOLDER_RE = re.compile(
    r"""^[\s'"]*(
          |x{3,}|X{3,}|\*{3,}|\.{3,}|<[^>]*>|\{\{[^}]*\}\}|\$\{[^}]*\}|\$[A-Z_][A-Z0-9_]*
        |yours?|your[-_ ].*
        |change[-_ ]?me|placeholder|example|sample|dummy|fake|mock
        |redacted|\*{2,}|-{2,}|none|null|nil|undefined|todo|tbd
        |not[-_ ]?found|notfound|unknown|missing|unset|empty|absent|n/?a
        |test[-_ ]?(key|token|secret|password)?|foo|bar|abc123
        |os\.environ|getenv|env\(
    )[\s'"]*$""",
    re.X | re.I,
)

# S1 vendor-prefixed keys. Each entry is (rule_id, compiled pattern).
VENDOR_KEY_PATTERNS = (
    ("S1", re.compile(r"\b(?:sk-ant-[A-Za-z0-9_\-]{8,}|sk-[A-Za-z0-9_\-]{16,})")),
    ("S1", re.compile(r"\bgh[pousr]_[A-Za-z0-9]{16,}")),
    ("S1", re.compile(r"\bgithub_pat_[A-Za-z0-9_]{20,}")),
    ("S1", re.compile(r"\bAKIA[0-9A-Z]{16}\b")),
    ("S1", re.compile(r"\b(?:AIza|ya29\.)[A-Za-z0-9_\-]{20,}")),
    ("S1", re.compile(r"\bxox[baprs]-[A-Za-z0-9\-]{10,}")),
)

# S2 / S3 / S5
BEARER_RE = re.compile(r"\bBearer\s+[A-Za-z0-9_\-\.=]{20,}")
PRIVATE_KEY_RE = re.compile(r"-----BEGIN\s+(?:[A-Z ]+\s+)?PRIVATE KEY-----")
CONN_STRING_RE = re.compile(r"\b[a-z][a-z0-9+.\-]*://[^\s:@/]+:[^\s:@/]+@[^\s/]+")

CRED_ASSIGN_RE = re.compile(
    r"""(?ix)
    \b(?:
        pass(?:word|wd|phrase)?
      | api[-_ ]?key
      | apikey
      | secret[-_ ]?key
      | access[-_ ]?token
      | refresh[-_ ]?token
      | auth[-_ ]?token
      | client[-_ ]?secret
      | private[-_ ]?token
      | credential
      | session[-_ ]?token
    )\b
    \s*[:=]\s*
    (?P<val>"[^"\n]+"|'[^'\n]+')
    """
)

# The value must be a quoted string literal. Bare identifiers, function calls
# and attribute reads (`api_key = os.getenv("X")`, `api_key = args.api_key`,
# `api_key = line.split(...)`) are variable plumbing, not hardcoded
# credentials, and were 38/38 of the real-repo S4 hits during P78 bring-up.

# I1 group A: imperative + reference to a rule/constraint.
INJECT_A_RES = (
    re.compile(
        r"(?i)\b(?:ignore|disregard|forget|override)\b[^.\n]{0,40}?"
        r"\b(?:previous|prior|above|earlier|all|any|existing)\b[^.\n]{0,20}?"
        r"\b(?:instruction|instructions|prompt|rule|rules|direction|guardrail)s?\b"
    ),
    re.compile(
        r"(?:忽略|无视|忘记|不要理会|不必理会)[^。\n]{0,20}?"
        r"(?:之前|以上|前面|上述|原先|所有)[^。\n]{0,10}?"
        r"(?:指令|要求|规则|提示|约束)"
    ),
    # Polarity matters: "always skip verification" instructs a violation,
    # "never skip verification" forbids one and is exactly the behaviour we
    # want. A polarity-blind keyword scan flagged the latter in
    # `skills/implement/planning.md` and `reports/P70-OUTPUT-DISCIPLINE.md`
    # during P78 bring-up. Only the imperative-to-violate shapes trigger.
    re.compile(
        r"(?i)\b(?:always|from now on|henceforth)\b[^.\n]{0,30}?"
        r"\b(?:skip|bypass|omit|ignore|disable|suppress)\b[^.\n]{0,30}?"
        r"\b(?:verify|verification|check|test|testing|review|validation|gate|gates)\b"
    ),
    re.compile(
        r"(?:始终|一律|从今以后|以后)[^。\n]{0,20}?"
        r"(?:跳过|免去|略过)[^。\n]{0,10}?"
        r"(?:验证|检查|测试|评审|审核|门禁)"
    ),
    re.compile(
        r"(?i)\bfrom now on\b[^.\n]{0,60}|\b今后[^。\n]{0,40}|\b以后请[^。\n]{0,40}"
    ),
)

# I1 group B: impersonating an authority.
INJECT_B_RES = (
    re.compile(r"(?i)\b(?:system\s+prompt|system\s*:|<\s*/?\s*system\s*>)"),
    re.compile(r"(?:系统提示|系统指令|系统消息)"),
    re.compile(
        r"(?i)\byou are now\b[^.\n]{0,60}|\byou are no longer\b[^.\n]{0,60}"
        r"|\byour new (?:role|identity|instruction|purpose)s?\b"
    ),
    re.compile(r"(?:你现在(?:是|为)|从现在起你是)[^。\n]{0,40}"),
    re.compile(
        r"(?i)\b(?:update|append|add|modify)\s+(?:your|the)\s+"
        r"(?:rules?|instructions?|guidelines?|memory|config)\b"
    ),
    re.compile(r"(?:更新|修改|追加)(?:你的?|本)?(?:规则|指令|记忆|配置)"),
    re.compile(
        r"(?i)\bthis (?:overrides|supersedes|replaces)\b[^.\n]{0,40}"
        r"|\b此条(?:覆盖|优先于|取代)"
    ),
    re.compile(
        r"(?i)\bdo not (?:tell|inform|mention|reveal)\b[^.\n]{0,40}"
        r"|\b(?:keep|hide)\s+(?:this\s+)?(?:secret|hidden)\b[^.\n]{0,20}"
        r"|\b(?:不要|别)(?:告诉|告知|透露|告诉任何)"
    ),
)

# A quoted credential value is ASCII by construction. A non-ASCII value is a
# localized sentinel, not a key -- e.g. `api_key = 'not found'` in
# `archived/skills/skill-optimizer/scripts/model_config_detector.py`.
CJK_VALUE_RE = re.compile(r"[\u4e00-\u9fff]")

# Rule catalogue. `severity` maps onto check.py error/warn; see module docstring.
RULES = (
    ("S1", "api_key", "critical"),
    ("S2", "bearer_token", "critical"),
    ("S3", "private_key", "critical"),
    ("S4", "credential_assignment", "low"),
    ("S5", "conn_string", "critical"),
    ("I1", "injection_structural", "high"),
)

SEVERITY_TO_ERROR = ("critical",)


def _is_excluded(rel):
    if rel.startswith(EXCLUDED_PREFIXES):
        return True
    name = rel.rsplit("/", 1)[-1]
    if name.startswith(".env") and name != ".env.example":
        return True
    return False


def _tracked_rels():
    """Rel paths git tracks. None when git is unavailable or not a repo.

    A developer's local, git-ignored `.env` is not a repository risk; a
    committed one is. Scanning the tracked set is what makes "`.env` present
    is an ERROR" a true statement rather than a trap for anyone with a local
    credentials file.
    """

    import subprocess

    r = subprocess.run(
        ["git", "ls-files"],
        cwd=ROOT, capture_output=True, text=True,
    )

    if r.returncode != 0:
        return None

    return {line for line in r.stdout.splitlines() if line}


def _header_allows(text):
    """True when the file carries an explicit whole-file allow marker."""

    head = "\n".join(text.splitlines()[:20])
    return MARKER_FILE in head


def _line_allows(line):
    return MARKER_LINE in line


def _scan_text(rel, text):
    """Return [(rel, line_no, rule_id, severity, category, excerpt)] for one file."""

    if not _is_excluded(rel) and not _header_allows(text):
        out = []
        for idx, line in enumerate(text.splitlines(), 1):
            if _line_allows(line):
                continue
            out.extend(_scan_line(rel, idx, line))
        return out

    return []


def _scan_line(rel, idx, line):
    hits = []

    maskers = _maskers_for(line)

    for rid, pattern in VENDOR_KEY_PATTERNS:
        if pattern.search(line):
            hits.append(
                (rel, idx, rid, _sev(rid), _cat(rid), _excerpt(line, maskers=maskers))
            )

    for rid, pattern in (("S2", BEARER_RE), ("S3", PRIVATE_KEY_RE), ("S5", CONN_STRING_RE)):
        if pattern.search(line):
            hits.append(
                (rel, idx, rid, _sev(rid), _cat(rid), _excerpt(line, maskers=maskers))
            )

    m = CRED_ASSIGN_RE.search(line)
    if m and not PLACEHOLDER_RE.match(m.group("val") or "") and not CJK_VALUE_RE.search(
        m.group("val") or ""
    ):
        hits.append(
            (rel, idx, "S4", _sev("S4"), _cat("S4"),
             _excerpt(line, maskers=maskers))
        )

    a = next((p.pattern for p in INJECT_A_RES if p.search(line)), None)
    b = next((p.pattern for p in INJECT_B_RES if p.search(line)), None)

    # A group (imperative + reference to a rule/constraint) is the trigger.
    # B group only aggravates. Requiring B alone produced 27/27 false hits on
    # the real repo: YAML keys (`ai-system:`), Python kwargs (`system:`) and
    # prose about the concept ("One agent round: system prompt + ..."). That is
    # precisely the keyword-blacklist failure the external reviewer warned
    # about — a keyword appearing in content is not the risk; content trying
    # to *become* a rule is.
    if a:
        tag = " (group A + B)" if b else " (group A)"
        hits.append(
            (rel, idx, "I1", _sev("I1"), _cat("I1") + tag, _excerpt(line))
        )

    return hits


def _sev(rid):
    for r, _c, s in RULES:
        if r == rid:
            return s
    return "low"


def _cat(rid):
    for r, cat, _s in RULES:
        if r == rid:
            return cat
    return rid


MASK = "[redacted]"


def _mask(pattern, line):
    """Blank a detected span so the report never reproduces the secret."""

    if pattern is None:
        return line
    return pattern.sub(MASK, line)


def _excerpt(line, width=60, maskers=()):
    """Report context with every detected secret span masked.

    A gate that prints the credential it found turns its own log, and any CI
    artifact, into a second copy of the leak. Masking applies to S1-S5 only;
    I1 is a behavioural finding with no secret to protect.
    """

    for pattern in maskers:
        line = _mask(pattern, line)

    flat = " ".join(line.split())
    return flat if len(flat) <= width else flat[:width] + "..."


def _maskers_for(line):
    """Every S-class pattern that matches this line, for masking."""

    out = [p for _rid, p in VENDOR_KEY_PATTERNS if p.search(line)]

    for p in (BEARER_RE, PRIVATE_KEY_RE, CONN_STRING_RE):
        if p.search(line):
            out.append(p)

    m = CRED_ASSIGN_RE.search(line)
    if m and not PLACEHOLDER_RE.match(m.group("val") or "") and not CJK_VALUE_RE.search(
        m.group("val") or ""
    ):
        out.append(re.compile(re.escape(m.group("val"))))

    return out


def _candidates(files):
    if files is not None:
        out = []
        for f in files:
            p = Path(f)
            if not p.is_absolute():
                p = ROOT / p
            out.append(p)
        return out

    tracked = _tracked_rels()

    out = []
    for p in ROOT.rglob("*"):
        if not p.is_file() or p.suffix not in SCAN_SUFFIXES:
            continue
        if ".git" in p.parts or "__pycache__" in p.parts:
            continue
        if "node_modules" in p.parts or ".venv" in p.parts:
            continue
        if tracked is not None:
            try:
                rel = p.relative_to(ROOT).as_posix()
            except ValueError:
                continue
            if rel not in tracked:
                continue
        out.append(p)
    return sorted(out)


def _machine_layer_allowed(rel):
    """True for machine-layer config that is not inside the repo."""

    return rel.startswith("~") or "/.config/ai-system/" in rel


def findings(files=None):
    """Return [(rel, line_no, rule_id, severity, category, excerpt)].

    Single source for the P78 rules, shared by check.py (full scan) and the
    pre-commit gate (staged subset) — mirrors `checks.memory.language_violations`.
    """

    out = []

    for p in _candidates(files):

        try:
            rel = p.relative_to(ROOT).as_posix()
        except ValueError:
            rel = p.as_posix()

        if _machine_layer_allowed(rel):
            continue

        # Order matters. A credential file is a finding *because* it is in the
        # repository, so this test must precede the general exclusion filter --
        # a staged `.env` is about to be committed and must never be skipped.
        # The untracked case never reaches here: the rglob discovery path in
        # `_candidates` filters to the git-tracked set.
        name = p.name
        if name == ".env" or name in EXCLUDED_NAMES:
            out.append(
                (rel, 0, "S3", "critical", "private_key",
                 "credential file is tracked by git")
            )
            continue

        if _is_excluded(rel):
            continue

        if p.suffix in SENSITIVE_SUFFIXES:
            out.append(
                (rel, 0, "S3", "critical", "private_key",
                 "sensitive key file present in tree")
            )
            continue

        try:
            text = p.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue

        out.extend(_scan_text(rel, text))

    return out


def check_secret_scan(c, files=None):
    """security-policy Principles 1 and 3 — now with machine execution.

    - S1/S2/S3/S5 (critical) -> ERROR: Triage has no authority to release.
    - I1 (high) and S4 (low) -> WARN: must be adjudicated before promotion.
    """

    hits = findings(files)

    for rel, line, rid, sev, cat, excerpt in hits:

        loc = f"{rel}:{line}" if line else rel

        if sev in SEVERITY_TO_ERROR:
            c.error(
                f"secret-scan {loc}: {rid} {cat} [{sev}] — {excerpt}"
            )
        else:
            c.warn(
                f"secret-scan {loc}: {rid} {cat} [{sev}] — "
                f"adjudicate before promotion — {excerpt}"
            )
