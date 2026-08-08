#!/usr/bin/env python3
r"""context-audit.py — Session context consumption auditor.

Analyzes a pi session file (or the most recent session for a project) and
reports token usage, largest messages, and the session health level defined
in governance/CONTEXT_LOADING.md (Session Health Levels: 40/60/80).

Usage:

    python tools/context-audit.py --session <path-to-session.jsonl>
    python tools/context-audit.py --recent            # most recent session
    python tools/context-audit.py --recent --json     # machine-readable

The audit answers the CONTEXT_LOADING "audit after changes" discipline and
the Session Health Levels thresholds:

    < 40%   normal; deep reasoning OK
    40-60%  summarize big outputs; delegate exploration
    > 60%   actively compact with focus; consider session boundary
    > 80%   split session now; keep only essential conclusions

Token estimation is heuristic (chars / 3 for mixed CJK/Latin, code-heavy
content chars / 4). It is a budget signal, not an exact meter.
"""

import argparse
import json
import sys
from pathlib import Path

# CJK characters weigh more than Latin chars per token
CJK_RE = None


def _import_re():
    global CJK_RE
    import re

    CJK_RE = re.compile(r"[\u4e00-\u9fff]")


def estimate_tokens(text):
    """Heuristic token estimate: CJK-heavy -> chars/2, code-heavy -> chars/4."""
    if not text:
        return 0
    cjk = sum(1 for ch in text if "\u4e00" <= ch <= "\u9fff")
    ratio = cjk / max(len(text), 1)
    if ratio > 0.3:
        return int(len(text) / 2)
    if ratio > 0.1:
        return int(len(text) / 3)
    return int(len(text) / 4)


def find_recent_session(project_dir):
    """Find the most recently modified session for a project."""
    sessions_root = Path.home() / ".pi" / "agent" / "sessions"
    norm = project_dir.replace("/", "-").replace("\\", "-")
    key = "--D--" + norm + "--"
    session_dir = sessions_root / key
    if not session_dir.exists():
        # fallback: scan all session dirs for newest .jsonl
        candidates = sorted(sessions_root.rglob("*.jsonl"), key=lambda p: p.stat().st_mtime, reverse=True)
        if not candidates:
            return None
        return candidates[0]
    candidates = sorted(session_dir.glob("*.jsonl"), key=lambda p: p.stat().st_mtime, reverse=True)
    return candidates[0] if candidates else None


def audit_session(path):
    """Parse a session jsonl and compute token stats."""
    stats = {
        "messages": 0,
        "total_chars": 0,
        "estimated_tokens": 0,
        "by_type": {},
        "largest": [],
        "compactions": [],
        "post_compact_chars": 0,
        "post_compact_tokens": 0,
    }
    entries = []
    seen_compaction = False
    with open(path, encoding="utf-8", errors="replace") as fh:
        for line in fh:
            try:
                d = json.loads(line)
            except Exception:
                continue
            t = d.get("type", "?")
            stats["messages"] += 1
            stats["by_type"][t] = stats["by_type"].get(t, 0) + 1
            if t == "compaction":
                seen_compaction = True
                summ = str(d.get("summary") or "")
                stats["compactions"].append(
                    {
                        "tokens_before": d.get("tokensBefore"),
                        "summary_chars": len(summ),
                        "summary_tokens": estimate_tokens(summ),
                    }
                )
                continue
            # pi messages: content may be None with the payload under "message"
            content = d.get("content") or ""
            if not content and isinstance(d.get("message"), dict):
                msg = d["message"]
                content = msg.get("content") or ""
            if isinstance(content, list):
                content = " ".join(
                    str(x.get("text", "")) for x in content if isinstance(x, dict)
                )
            content = str(content)
            # Prefer recorded usage tokens when available
            usage = d.get("usage") or (d.get("message") or {}).get("usage")
            entry_tokens = None
            if isinstance(usage, dict):
                entry_tokens = (
                    usage.get("input") or usage.get("totalTokens") or usage.get("output")
                )
            n = len(content)
            stats["total_chars"] += n
            if entry_tokens:
                stats["estimated_tokens"] += int(entry_tokens)
            else:
                stats["estimated_tokens"] += estimate_tokens(content)
            if seen_compaction:
                stats["post_compact_chars"] += n
                stats["post_compact_tokens"] += int(entry_tokens) if entry_tokens else estimate_tokens(content)
            if t in ("message", "tool") and n > 0:
                entries.append((n, t, content))
            if t == "session":
                stats["model_ctx_window"] = None  # not stored in session file
    entries.sort(reverse=True)
    stats["largest"] = [(n, t) for n, t, _ in entries[:8]]
    return stats


def health_level(percent):
    if percent < 40:
        return "GREEN (<40%) — normal; deep reasoning OK"
    if percent < 60:
        return "YELLOW (40-60%) — summarize big outputs; delegate exploration"
    if percent < 80:
        return "ORANGE (60-80%) — actively compact with focus; consider session boundary"
    return "RED (>=80%) — split session now; keep only essential conclusions"


def main():
    parser = argparse.ArgumentParser(description="Session context consumption auditor")
    parser.add_argument("--session", help="Path to a session .jsonl file")
    parser.add_argument("--recent", action="store_true", help="Audit the most recent session")
    parser.add_argument("--project", default="ai-workspace", help="Project dir name for --recent")
    parser.add_argument("--json", action="store_true", help="Machine-readable output")
    args = parser.parse_args()

    _import_re()

    path = None
    if args.session:
        path = Path(args.session)
    elif args.recent:
        path = find_recent_session(args.project)
        if path is None:
            print("No session found.", file=sys.stderr)
            sys.exit(2)
    else:
        parser.print_help()
        sys.exit(2)

    if not path.exists():
        print(f"Session not found: {path}", file=sys.stderr)
        sys.exit(2)

    s = audit_session(path)

    # Compute active context: compaction summaries + messages after the last
    # compaction (pi keeps only summaries + recent window in the live model
    # context). Full history is reported separately.
    active_chars = 0
    active_tokens = 0
    for c in s["compactions"]:
        active_chars += c.get("summary_chars", 0)
        active_tokens += c.get("summary_tokens", 0)
    active_chars += s.get("post_compact_chars", 0)
    active_tokens += s.get("post_compact_tokens", 0)

    if args.json:
        out = {
            "path": str(path),
            "full_history": {
                "chars": s["total_chars"],
                "estimated_tokens": s["estimated_tokens"],
            },
            "active_context": {
                "chars": active_chars,
                "estimated_tokens": active_tokens,
            },
            "messages": s["messages"],
            "by_type": s["by_type"],
            "largest": s["largest"],
            "compactions": s["compactions"],
        }
        print(json.dumps(out, indent=2, ensure_ascii=False))
        return

    print(f"Session: {path}")
    print(f"Messages: {s['messages']} | full-history chars: {s['total_chars']:,}")
    print(f"Full-history estimated tokens: ~{s['estimated_tokens']:,} (heuristic)")
    print(f"By type: {json.dumps(s['by_type'], ensure_ascii=False)}")
    print("")
    print("Largest messages (chars):")
    for n, t in s["largest"]:
        print(f"  [{t}] {n:,}")
    print("")
    print("Compactions:")
    if s["compactions"]:
        for c in s["compactions"]:
            print(f"  tokensBefore={c.get('tokens_before', 0):,} summary={c.get('summary_chars', 0):,} chars")
    else:
        print("  none")
    print("")
    # Active context (what the model currently holds after compaction)
    window = 1_000_000
    pct = active_tokens / window * 100
    print(f"ACTIVE context (compaction summaries + recent window):")
    print(f"  ~{active_tokens:,} tokens / {window:,} window = {pct:.1f}%")
    print(f"  {health_level(pct)}")
    print("")
    hist_pct = s["estimated_tokens"] / window * 100
    print(f"FULL history (all messages ever): {s['estimated_tokens']:,} tokens ≈ {hist_pct:.0f}% of window")


if __name__ == "__main__":
    main()
