"""Main-chain branch parser (provider contract).

Contract (mirrors the bugfix branch.parser contract in
templates/runtime/runtime-bugfix.md Phase 4.6):

  method:    parse(branch_name: str) -> ParsedBranch | None
  fields:    ParsedBranch = {date, type, desc, service}  (all str, "" when absent)
  behavior:  blank / unparseable -> return None (never raise)

Main-chain branch format (暂定, 2026-08-20; 需求确认时确定公共部分，之后不变):

  cc{date}_ipd_{desc}_{service}
    e.g. cc20260820_ipd_italent-sync-plus_user-center-api
         date   = YYYYMMDD（需求确认日期）
         type   = ipd（固定，需求/特性分支）
         desc   = 需求简述（kebab-case）
         service= 服务名（每服务独立分支；除分支名外其余一致）

The naming RULE lives in the Task Card `branch` field (template with
{date} / {desc} / {service} placeholders) and is fixed at requirement-confirmation
time; a created branch must NOT be renamed afterwards (immutable, except new
projects with authorization). A provider under extensions/<name>/scripts/
branch_parser.py may override this default (config: branch.parser logic name);
this module is the ai-system default inline implementation.
"""

import re
from dataclasses import dataclass

# 主链默认模板：cc{date}_ipd_{desc}_{service}（暂定）。
_BRANCH_RE = re.compile(
    r"^cc(?P<date>\d{8})_ipd_(?P<desc>[a-z0-9_-]+)_(?P<service>[a-z0-9-]+)$"
)


@dataclass
class ParsedBranch:
    date: str = ""      # YYYYMMDD
    type: str = ""      # ipd
    desc: str = ""
    service: str = ""


def parse(branch_name: str) -> ParsedBranch | None:
    """Return None when the branch name cannot be parsed (never raises)."""

    if not isinstance(branch_name, str) or not branch_name.strip():
        return None

    m = _BRANCH_RE.match(branch_name.strip())

    if not m:
        return None

    g = m.groupdict()

    return ParsedBranch(
        date=g["date"],
        type="ipd",
        desc=g["desc"],
        service=g["service"],
    )


def render(template: str, date: str, desc: str, service: str = "") -> str:
    """Render a branch-name template ({date} / {desc} / {service} placeholders).

    The template is the Task Card `branch` field
    (default `cc{date}_ipd_{desc}_{service}`).
    """

    out = (template or "cc{date}_ipd_{desc}_{service}").replace(
        "{date}", date
    ).replace("{desc}", desc)

    return out.replace("{service}", service)
