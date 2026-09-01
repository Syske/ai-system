#!/usr/bin/env python3
r"""运行时语言门禁（P45）——校验面向用户文本是否按系统语言输出。

启发式判定文本语言是否匹配 config/menu.yaml → locale（当前 zh → 简体中文）。
用于 Runtime Complete 阶段（见 templates/runtime/runtime-base.md「语言自检」步骤）：
AI 生成 Completion Report 后、呈现给用户前运行本工具。

三态判定（exit code）：PASS=0 / WARN=1 / FAIL=2。
- locale=zh：去掉代码块与双语标题白名单后，面向用户正文 CJK 占比
  ≥ 20% → PASS；< 10% → FAIL；之间 → WARN。
- 双语标题（`## 实现总结 / Implementation Summary`）与技术标识符不计分。

用法：
    python3 tools/language-gate.py <report-file> [--locale zh] [--list-suspicious]
    cat report.md | python3 tools/language-gate.py --stdin
"""
import argparse
import re
import sys
from pathlib import Path

CJK_RE = re.compile(r"[\u4e00-\u9fff\u3400-\u4dbf]")
ASCII_LETTER_RE = re.compile(r"[A-Za-z]")
# 双语标题白名单：`## 中文 / English` 这类行（中文斜杠英文），是约定的混合标题模式
BILINGUAL_HEADING_RE = re.compile(r"^\s*#{1,6}\s*\S.{0,80}?\s*/\s*\S.{0,80}\s*$")
# 表格分隔线 / 纯符号行
SEPARATOR_RE = re.compile(r"^\s*[|\-:+\s]+$")
# 行内技术标识符（路径 / 命令 / 配置键）——不计入英文正文
TOKEN_RE = re.compile(r"[A-Za-z0-9_\-./\\:{}()\[\]<>+=*#@%^&|~`'\"]")

ROOT = Path(__file__).resolve().parent.parent
THRESHOLD_PASS = 0.20  # CJK 占比 ≥ 20% → PASS
THRESHOLD_FAIL = 0.10  # CJK 占比 < 10% → FAIL；之间 → WARN


def resolve_locale(override):
    """取系统语言唯一事实源：config/menu.yaml → locale（解析失败兜底 zh）。"""
    if override:
        return override
    try:
        import yaml
        menu = yaml.safe_load((ROOT / "config/menu.yaml").read_text(encoding="utf-8"))
        return (menu or {}).get("locale", "zh")
    except Exception:
        return "zh"


def strip_code_blocks(text):
    """移除 ``` 围栏代码块与行内代码段，避免技术内容拉低 CJK 占比。"""
    text = re.sub(r"```.*?```", " ", text, flags=re.S)
    text = re.sub(r"`[^`]*`", " ", text)
    return text


def analyze(text, locale):
    """返回 (verdict, cjk_ratio, suspicious_lines)。"""
    text = strip_code_blocks(text)
    cjk = 0
    letters = 0
    suspicious = []
    for raw in text.splitlines():
        line = raw.strip()
        if not line or SEPARATOR_RE.match(line) or BILINGUAL_HEADING_RE.match(line):
            continue
        cjk_cnt = len(CJK_RE.findall(line))
        letter_cnt = len(ASCII_LETTER_RE.findall(line))
        cjk += cjk_cnt
        letters += letter_cnt
        # 可疑行：面向用户正文里英文为主的句子（无中文、足够长、非标识符形态）
        if locale == "zh" and cjk_cnt == 0 and letter_cnt > 24:
            stripped = TOKEN_RE.sub("", line).strip()
            if len(stripped) > 12:  # 去掉标识符后仍剩较长英文 → 疑似英文正文
                suspicious.append(line)
    total = cjk + letters
    ratio = (cjk / total) if total else 1.0
    if locale == "zh":
        if ratio >= THRESHOLD_PASS:
            return "PASS", ratio, suspicious
        if ratio < THRESHOLD_FAIL:
            return "FAIL", ratio, suspicious
        return "WARN", ratio, suspicious
    # 非 zh locale 暂不判 FAIL（其他语言无约定），保守 PASS
    return "PASS", ratio, suspicious


def main(argv=None):
    ap = argparse.ArgumentParser(description="运行时语言门禁（P45）：校验面向用户文本语言")
    ap.add_argument("file", nargs="?", help="报告文件路径；缺省读 stdin")
    ap.add_argument("--stdin", action="store_true", help="从 stdin 读取文本")
    ap.add_argument("--locale", default=None, help="覆盖系统语言（默认读 config/menu.yaml）")
    ap.add_argument("--list-suspicious", action="store_true", help="列出疑似非系统语言的行")
    args = ap.parse_args(argv)

    locale = resolve_locale(args.locale)
    if args.file:
        text = Path(args.file).read_text(encoding="utf-8")
    else:
        text = sys.stdin.read()

    verdict, ratio, suspicious = analyze(text, locale)
    print(f"language-gate: locale={locale} verdict={verdict} cjk_ratio={ratio:.2f}")
    if verdict == "FAIL":
        print("  → 面向用户文本未按系统语言输出：请重写后再呈现（runtime-base 语言自检步骤）")
    elif verdict == "WARN":
        print("  → 语言混合，建议人工复核可疑行")
    if args.list_suspicious:
        for ln in suspicious[:10]:
            print(f"  [suspicious] {ln[:100]}")
        if not suspicious:
            print("  [suspicious] (无)")
    return 0 if verdict == "PASS" else (1 if verdict == "WARN" else 2)


if __name__ == "__main__":
    sys.exit(main())