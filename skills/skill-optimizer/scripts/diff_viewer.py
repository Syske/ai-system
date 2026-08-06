#!/usr/bin/env python3
"""Generate a self-contained HTML diff viewer for skill optimization iterations.

Thin CLI entry point (S1 split): computation lives in diff_core.py,
the HTML template in html_report.py.

Usage:
    python diff_viewer.py --snapshots ./snapshots -o diff.html
    python diff_viewer.py --base ./v0 --current ./v1 -o diff.html

No dependencies beyond the Python stdlib.
"""

import argparse
import os
import sys
from pathlib import Path

from diff_core import collect_files, discover_snapshots, generate_html


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate an interactive skill diff viewer")
    parser.add_argument("old_path", type=Path, nargs="?", help="Base path (file or dir)")
    parser.add_argument("new_path", type=Path, nargs="?", help="Current path (file or dir)")
    parser.add_argument("--snapshots", type=Path, default=None)
    parser.add_argument("--base", type=Path, default=None)
    parser.add_argument("--current", type=Path, default=None)
    parser.add_argument("--base-label", type=str, default="v0", help="Label for base version")
    parser.add_argument("--current-label", type=str, default="v1", help="Label for current version")
    parser.add_argument("--title", "-t", type=str, default="Skill", help="Skill name for UI")
    parser.add_argument("--default-base", type=str, default=None, help="Label of the default base version to select in snapshots mode")
    parser.add_argument("--default-current", type=str, default=None, help="Default current version label (e.g. v1.1)")
    parser.add_argument("--output", "-o", "--static", type=Path, default=None, help="Output HTML file (if not set, opens in browser)")
    parser.add_argument("--no-open", action="store_true", help="Do not open browser even if --output is not set")

    args = parser.parse_args()

    old_p = args.old_path or args.base
    new_p = args.new_path or args.current
    skill_name = args.title or "Skill"

    if args.snapshots:
        snap = args.snapshots.resolve()
        if not snap.is_dir():
            print(f"Error: {snap} not a directory", file=sys.stderr); sys.exit(1)
        versions = discover_snapshots(snap)
        if len(versions) < 2:
            print(f"Error: need >= 2 versions, found {len(versions)}", file=sys.stderr); sys.exit(1)
        default_base = 0
        default_current = len(versions) - 1
        if args.default_base:
            for i, v in enumerate(versions):
                if v["label"] == args.default_base:
                    default_base = i
                    break
        if args.default_current:
            for i, v in enumerate(versions):
                if v["label"] == args.default_current:
                    default_current = i
                    break
        html = generate_html(versions, skill_name, default_base=default_base, default_current=default_current)
    elif old_p and new_p:
        bd, cd = old_p.resolve(), new_p.resolve()

        if bd.is_file() and cd.is_file():
            b_files = {bd.name: bd.read_text(encoding="utf-8", errors="replace")}
            c_files = {cd.name: cd.read_text(encoding="utf-8", errors="replace")}
        else:
            if not bd.is_dir() or not cd.is_dir():
                print(f"Error: both arguments must be directories, or both must be files", file=sys.stderr); sys.exit(1)
            b_files = collect_files(bd)
            c_files = collect_files(cd)

        versions = [
            {"label": args.base_label, "files": b_files},
            {"label": args.current_label, "files": c_files},
        ]
        html = generate_html(versions, skill_name, default_base=0, default_current=1)
    else:
        parser.print_help()
        sys.exit(1)

    if args.output:
        out = args.output.resolve()
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(html, encoding="utf-8")
        print(f"Static diff written to: {out}")
    else:
        import tempfile, webbrowser
        fd, path = tempfile.mkstemp(suffix=".html", prefix="skill-diff-")
        with os.fdopen(fd, 'w', encoding='utf-8') as f:
            f.write(html)
        print(f"Opening diff in browser: file://{path}")
        if not args.no_open:
            webbrowser.open(f"file://{path}")


if __name__ == "__main__":
    main()
