"""Shared YAML frontmatter reader for skill / workflow assets.

Both skills (SKILL.md) and workflows (workflows/*.md) use the same
asset syntax: a leading `---` YAML frontmatter block (machine contract)
followed by a Markdown body (readable narrative). This module provides the
single parser for that block so skill and workflow consumers stay uniform.

Returns ({}, original_text) when there is no frontmatter, so callers can
fall back to legacy inline parsing.
"""

import re

import yaml

# 匹配开头的 `---` 分隔的 YAML 块（非贪婪到闭合 ---）
FRONTMATTER_RE = re.compile(
    r"\A---[ \t]*\n(.*?)\n---[ \t]*\n",
    re.DOTALL,
)


def read_frontmatter(text):
    """Return (frontmatter_dict, remaining_body_text).

    - Dict is empty when there is no frontmatter or it fails to parse.
    - remaining_body_text is the markdown after the closing `---`.
    """

    if not text:
        return {}, text

    m = FRONTMATTER_RE.match(text)

    if not m:
        return {}, text

    try:

        data = yaml.safe_load(m.group(1))

    except Exception:

        data = {}

    if not isinstance(data, dict):
        data = {}

    return data, text[m.end():]
