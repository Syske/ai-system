"""C2 豁免清单治理 — `tools/jdt-format-gate/known-ignore.txt` 必须逐条附理由并定期复核。

P65 Option D（2026-09-21 采纳）：`known-ignore.txt` 是 C2 门禁的**逃生门**
（登记"无 fixpoint / 振荡"的边界文件，门禁对其跳过）。逃生门若无理由、无复核期限，
会静默长期化 —— 与 P60「声明 vs 实效必须对账」同族。故强制：

- 每个路径条目**紧邻上方**必须有一行 `# reason: <理由>（<YYYY-MM-DD> 复核基线）`
  → 缺理由、缺日期、理由与路径不紧邻 → **ERROR**
- 复核基线超过 `REVIEW_MAX_AGE_DAYS`（180 天 ≈ 两个季度）→ **WARN**（季度复核信号）
- `# reason:` 行后面没有路径条目（悬空理由）→ **ERROR**（防止条目被删而理由留存）

文件格式（Java wrapper 跳过 `#` 注释行，故可在不改 Java 的前提下携带元数据）：

    # reason: <理由>（2026-09-21 复核基线）
    main/java/.../EnterpriseProvider.java
"""

import datetime
import re
from pathlib import Path

from .base import ROOT

IGNORE_FILE = ROOT / "tools" / "jdt-format-gate" / "known-ignore.txt"

REASON_RE = re.compile(r"^#\s*reason\s*:\s*(?P<text>.+)$")
DATE_RE = re.compile(r"(\d{4})-(\d{2})-(\d{2})")

REVIEW_MAX_AGE_DAYS = 180


def parse_entries(text):
    """把清单拆成 [(path, reason, date_or_None, line_no)]，并回报悬空理由行号。"""
    entries = []
    dangling = []
    pending = None                      # (reason_text, line_no)

    for line_no, raw in enumerate(text.splitlines(), start=1):
        line = raw.strip()

        if not line:
            continue

        if line.startswith("#"):
            match = REASON_RE.match(line)
            if match:
                if pending is not None:
                    dangling.append(pending[1])
                pending = (match.group("text"), line_no)
            continue

        reason, reason_line = (pending if pending else (None, None))
        entries.append((line, reason, reason_line, line_no))
        pending = None

    if pending is not None:
        dangling.append(pending[1])

    return entries, dangling


def _age_days(date_text):
    """返回距今的天数；无法解析返回 None。"""
    match = DATE_RE.search(date_text or "")
    if not match:
        return None
    try:
        when = datetime.date(int(match.group(1)), int(match.group(2)), int(match.group(3)))
    except ValueError:
        return None
    return (datetime.date.today() - when).days


def check_jdt_ignore(c):
    """校验 C2 豁免清单的理由与复核期限。"""

    if not IGNORE_FILE.is_file():
        c.warn("tools/jdt-format-gate/known-ignore.txt 不存在 —— C2 豁免清单缺失")
        return

    text = IGNORE_FILE.read_text(encoding="utf-8")
    entries, dangling = parse_entries(text)

    for line_no in dangling:
        c.error(
            f"tools/jdt-format-gate/known-ignore.txt:{line_no}: `# reason:` 之后没有路径条目"
            "（悬空理由 → 条目被删但理由留存）"
        )

    for path, reason, reason_line, line_no in entries:
        if not reason:
            c.error(
                f"tools/jdt-format-gate/known-ignore.txt:{line_no}: 豁免条目缺少理由"
                "（紧邻上方需 `# reason: <理由>（<YYYY-MM-DD> 复核基线）`）"
            )
            continue

        age = _age_days(reason)
        if age is None:
            c.error(
                f"tools/jdt-format-gate/known-ignore.txt:{reason_line}: 理由缺少复核基线日期"
                "（格式 `<YYYY-MM-DD> 复核基线`）"
            )
        elif age > REVIEW_MAX_AGE_DAYS:
            c.warn(
                f"tools/jdt-format-gate/known-ignore.txt:{reason_line}: 豁免理由已 {age} 天未复核"
                f"（阈值 {REVIEW_MAX_AGE_DAYS} 天）—— 请确认 {path} 是否仍无 fixpoint"
            )