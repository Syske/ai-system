#!/usr/bin/env python3
"""Shared core logic for the skill-optimizer CLI (S1 split).

Extracted from main.py / main_parallel.py: LLM client setup plus the
pure helper functions used by both entry points. Behavior is identical
to the original code — this is a move-only refactor.
"""

import argparse
import datetime
import logging
import os
import re
import sys
import datetime
from pathlib import Path
from typing import List, Optional

import httpx
from dotenv import load_dotenv
from openai import OpenAI

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from architecture.genome import SkillGenome
from constants import ENV_FILE
from engine.report_generator import OptimizationReportGenerator
from optimizer import SkillOptimizer
from skill_insight_api import get_skill_logs
from cli_args import CliArgsError, resolve_human_feedback_content

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# 缓存命中率监控（跨实例累计，模块级）：
#   DeepSeek usage 字段: prompt_cache_hit_tokens / prompt_cache_miss_tokens
#   命中率 = hit / (hit + miss)。每次调用成功后累计，退出时汇总输出。
CACHE_STATS = {
    "calls": 0,       # 计入统计的调用次数
    "hit": 0,         # prompt_cache_hit_tokens 累计
    "miss": 0,        # prompt_cache_miss_tokens 累计
}


def reset_cache_stats():
    """清零缓存统计（单次优化会话开始时调用）。"""
    CACHE_STATS["calls"] = 0
    CACHE_STATS["hit"] = 0
    CACHE_STATS["miss"] = 0


def record_cache_usage(usage):
    """从 OpenAI response.usage 累计缓存命中/未命中 token。"""
    if not usage:
        return
    hit = getattr(usage, "prompt_cache_hit_tokens", 0) or 0
    miss = getattr(usage, "prompt_cache_miss_tokens", 0) or 0
    CACHE_STATS["calls"] += 1
    CACHE_STATS["hit"] += int(hit)
    CACHE_STATS["miss"] += int(miss)


def cache_stats_report() -> str:
    """格式化缓存命中率报告（供退出时输出）。"""
    hit = CACHE_STATS["hit"]
    miss = CACHE_STATS["miss"]
    total = hit + miss
    rate = (hit / total * 100) if total else 0.0
    return (
        f"[CacheStats] calls={CACHE_STATS['calls']} "
        f"hit_tokens={hit} miss_tokens={miss} "
        f"hit_rate={rate:.1f}%"
    )



class RealLLMClient:
    def __init__(self):
        # Override: if LLM_* env vars are set, use them directly
        llm_key = os.getenv("LLM_API_KEY")
        if llm_key:
            api_key = llm_key
            base_url = os.getenv("LLM_BASE_URL", "https://api.deepseek.com/")
            model_name = os.getenv("LLM_MODEL", "deepseek-chat")
        elif os.getenv("DEEPSEEK_API_KEY"):
            api_key = os.getenv("DEEPSEEK_API_KEY")
            base_url = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com/")
            model_name = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")
        elif os.getenv("OPENAI_API_KEY"):
            api_key = os.getenv("OPENAI_API_KEY")
            base_url = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
            model_name = os.getenv("OPENAI_MODEL", "gpt-4")
        elif os.getenv("ANTHROPIC_API_KEY") or os.getenv("ANTHROPIC_AUTH_TOKEN"):
            api_key = os.getenv("ANTHROPIC_API_KEY") or os.getenv("ANTHROPIC_AUTH_TOKEN")
            base_url = os.getenv("ANTHROPIC_BASE_URL", "https://api.anthropic.com")
            model_name = os.getenv("ANTHROPIC_MODEL", "claude-3-5-sonnet-20241022")
        else:
            from constants import ENV_FILE

            raise ValueError(
                f"\n❌ Error: No API key found in environment.\n"
                f"Please configure your AI model API key in the environment file:\n"
                f"   -> {ENV_FILE.absolute()}\n"
                f"Alternatively, you can run './scripts/opt.sh --help' to use the interactive setup."
            )

        self.model_name = model_name
        self.llm = OpenAI(
            base_url=base_url,
            api_key=api_key,
            http_client=httpx.Client(verify=False, timeout=300.0),
            max_retries=2,
            timeout=300.0,
        )
        logger.info(f"[RealLLM] Using base_url={base_url}, model={model_name}")

    def __call__(self, prompt, system=None):
        """Simple text completion (no tools). Returns str.

        system: optional static system instruction. When provided, the
        request becomes [system] + [user] — the constant system part is
        prefix-stable across calls, enabling DeepSeek-style prefix cache
        hits (cache optimization). Default None keeps legacy single-user
        behavior.
        """
        logger.info(f"\n[RealLLM] Sending Prompt (truncated): {prompt[:100]}...")
        try:
            messages = []
            if system:
                messages.append({"role": "system", "content": system})
            messages.append({"role": "user", "content": prompt})
            response = self.llm.chat.completions.create(
                model=self.model_name,
                messages=messages,
                max_tokens=8192,
            )
            record_cache_usage(response.usage)
            return (response.choices[0].message.content or "").strip()
        except Exception as e:
            logger.error(f"[RealLLM] Error: {e}")
            return ""

    def chat(self, messages, tools=None, temperature=0.2):
        """Chat completion with optional native function-calling tools.

        messages: list of {"role": ..., "content": ...} (system/user/assistant/tool)
        tools: optional list of OpenAI tool JSON schemas.

        Returns the raw openai response object (caller reads
        .choices[0].message.content / .tool_calls).
        """
        kwargs = {
            "model": self.model_name,
            "messages": messages,
            "max_tokens": 8192,
            "temperature": temperature,
        }
        if tools:
            kwargs["tools"] = tools
        try:
            resp = self.llm.chat.completions.create(**kwargs)
            record_cache_usage(getattr(resp, "usage", None))
            return resp
        except Exception as e:
            logger.error(f"[RealLLM] chat error: {e}")
            return None


# --- Core Logic Functions ---


def validate_skill_file(file_path: Path) -> tuple[bool, str]:
    """
    验证 SKILL.md 文件的完整性
    
    Returns:
        (is_valid, error_message)
    """
    if not file_path.exists():
        return False, f"文件不存在: {file_path}"
    
    content = file_path.read_text(encoding='utf-8')
    if not content or len(content) < 100:
        return False, f"文件内容过短: {len(content)} 字符"
    
    if not content.startswith('---'):
        return False, "缺少 YAML frontmatter"
    
    frontmatter_match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
    if not frontmatter_match:
        return False, "frontmatter 格式错误"
    
    frontmatter = frontmatter_match.group(1)
    if 'name:' not in frontmatter:
        return False, "frontmatter 缺少 name 字段"
    
    return True, ""


def validate_auxiliary_file(file_path: Path) -> tuple[bool, str]:
    """
    验证辅助文件的完整性
    
    Returns:
        (is_valid, error_message)
    """
    if not file_path.exists():
        return False, f"文件不存在: {file_path}"
    
    content = file_path.read_text(encoding='utf-8')
    if not content or len(content.strip()) == 0:
        return False, f"文件内容为空: {file_path}"
    
    return True, ""


def sanitize_reference_content(content: str) -> str:
    content = content or ""
    content = re.sub(
        r"\[([^\]]+)\]\(((?:scripts|references)/[^)]+)\)",
        r"\1 (`\2`)",
        content,
        flags=re.IGNORECASE,
    )
    return content


def update_skill_name_in_md(content: str, new_name: str) -> str:
    """Update skill name in SKILL.md content."""
    # Try YAML frontmatter first
    pattern = r"^name:\s+(.+)$"
    match = re.search(pattern, content, re.MULTILINE)
    if match:
        return re.sub(
            pattern, f"name: {new_name}", content, count=1, flags=re.MULTILINE
        )

    # Fallback to header (only if name is in header)
    pattern = r"^#\s+(.+)$"
    match = re.search(pattern, content, re.MULTILINE)
    if match:
        return re.sub(pattern, f"# {new_name}", content, count=1, flags=re.MULTILINE)

    return content


def integrate_auxiliary_references(
    skill_content: str,
    auxiliary_files: dict[str, str],
    auxiliary_meta: Optional[dict[str, str]] = None,
) -> str:
    """
    在 SKILL.md 中自动添加对辅助文件的引用
    
    Args:
        skill_content: SKILL.md 的内容
        auxiliary_files: 辅助文件字典 {相对路径: 内容}
        auxiliary_meta: 辅助文件元数据 {相对路径: summary}
    
    Returns:
        更新后的 SKILL.md 内容
    """
    if not auxiliary_files:
        return skill_content
    
    auxiliary_meta = auxiliary_meta or {}
    section_heading_re = re.compile(
        r"(?im)^\s*##\s*(辅助文件|相关文件|auxiliary files|related files)\s*$"
    )
    has_section = bool(section_heading_re.search(skill_content))
    should_replace = has_section and ("由优化器自动创建" in skill_content)

    base_content = skill_content
    if should_replace:
        matches = list(section_heading_re.finditer(skill_content))
        if matches:
            base_content = skill_content[: matches[-1].start()].rstrip()

    excluded_prefixes = ("snapshots/", ".opt/")
    excluded_exact = {
        "AUXILIARY_META.json",
        "diagnoses.json",
        "OPTIMIZATION_REPORT.md",
        "meta.json",
    }

    def is_excluded(rel_path: str) -> bool:
        if not rel_path:
            return True
        if rel_path.startswith(excluded_prefixes):
            return True
        if rel_path in excluded_exact:
            return True
        if "/__pycache__/" in f"/{rel_path}/":
            return True
        return False

    def normalize_summary(text: str) -> str:
        text = (text or "").strip()
        text = re.sub(r"\s+", " ", text)
        if len(text) > 160:
            text = text[:157].rstrip() + "..."
        return text

    def auto_summary(rel_path: str, content: str) -> str:
        content = content or ""
        lines = content.splitlines()

        def meaningful(line: str) -> bool:
            s = (line or "").strip()
            if not s:
                return False
            low = s.lower()
            if low.startswith("#!/"):
                return False
            if low in {"set -e", "set -eu", "set -euo pipefail"}:
                return False
            if low.startswith(("import ", "from ")):
                return False
            return True

        def pick_first_meaningful() -> str:
            for ln in lines[:200]:
                s = (ln or "").strip()
                if not s:
                    continue
                if s.startswith("#") and not s.startswith("# "):
                    continue
                if meaningful(s):
                    return s.lstrip("#").strip()
            for ln in lines:
                s = (ln or "").strip()
                if meaningful(s):
                    return s.lstrip("#").strip()
            return ""

        if rel_path.endswith(".md"):
            for ln in lines[:80]:
                s = (ln or "").strip()
                if s.startswith("#"):
                    s = s.lstrip("#").strip()
                    if s:
                        return s
            return pick_first_meaningful()

        if rel_path.endswith((".sh", ".bash")):
            for ln in lines[:200]:
                s = (ln or "").strip()
                if not s:
                    continue
                if "用法:" in s or "usage:" in s.lower() or "作用:" in s or "功能:" in s:
                    return s.lstrip("#").strip()
            return pick_first_meaningful()

        if rel_path.endswith(".py"):
            m = re.search(r'(?s)^\s*(?:"""|\'\'\')\s*(.*?)\s*(?:"""|\'\'\')', content)
            if m:
                doc = (m.group(1) or "").strip().splitlines()
                for ln in doc:
                    s = (ln or "").strip()
                    if s:
                        return s
            return pick_first_meaningful()

        return pick_first_meaningful()

    def ensure_summary(rel_path: str) -> str:
        summary = (auxiliary_meta.get(rel_path) or "").strip()
        if summary:
            return normalize_summary(summary)
        generated = normalize_summary(auto_summary(rel_path, auxiliary_files.get(rel_path, "")))
        if generated:
            auxiliary_meta[rel_path] = generated
            return generated
        generated = normalize_summary(rel_path)
        auxiliary_meta[rel_path] = generated
        return generated

    entrypoints: list[str] = []
    references: list[str] = []
    others: list[str] = []
    content_lower = skill_content.lower()

    def is_entrypoint_script(rel_path: str, summary: str) -> bool:
        if not rel_path.startswith("scripts/"):
            return False
        s = (summary or "").strip().lower()
        if not s:
            return False
        if "用法:" in s and ("作用:" in s or "功能:" in s):
            return True
        if rel_path.lower() in s:
            return True
        if re.search(r"\b(python|bash|sh|node|uv)\b", s) and "scripts/" in s:
            return True
        return False

    for rel_path in sorted(auxiliary_files.keys()):
        if is_excluded(rel_path):
            continue
        if not (rel_path.startswith("scripts/") or rel_path.startswith("references/")):
            continue
        if not should_replace:
            if rel_path.lower() in content_lower:
                continue
            base = Path(rel_path).name
            if base and base != rel_path:
                if re.search(
                    rf"(?i)(?<![A-Za-z0-9._-]){re.escape(base)}(?![A-Za-z0-9._-])",
                    skill_content,
                ):
                    continue
        summary = ensure_summary(rel_path)
        is_ref = rel_path.startswith("references/")
        is_entry = is_entrypoint_script(rel_path, summary)
        if is_ref:
            references.append(rel_path)
        elif is_entry:
            entrypoints.append(rel_path)
        else:
            others.append(rel_path)

    def line_for(rel_path: str) -> str:
        desc = ensure_summary(rel_path)
        return f"- **{rel_path}** - {desc}\n"

    def inject_progressive_references(content: str) -> str:
        if not references and not entrypoints:
            return content
        if re.search(r"(?im)^##\s+file references\s*$", content):
            return content

        def choose_reference() -> Optional[str]:
            preferred = ["references/REFERENCE.md", "references/README.md"]
            for p in preferred:
                if p in auxiliary_files:
                    return p
            return references[0] if references else None

        ref_path = choose_reference()
        parts: list[str] = []
        parts.append("## File references\n")
        added_any = False
        if ref_path and f"({ref_path})" not in content and ref_path not in content:
            parts.append(f"See [the reference guide]({ref_path}) for details.\n")
            added_any = True
        if entrypoints:
            new_entrypoints = [p for p in entrypoints if p not in content]
            if new_entrypoints:
                parts.append("\nRun the extraction script:\n")
                for p in new_entrypoints:
                    parts.append(f"\n{p}\n")
                added_any = True
        if added_any:
            parts.append(
                "\nKeep file references one level deep from SKILL.md. Avoid deeply nested reference chains.\n"
            )
        block = "\n".join(parts).strip() + "\n"
        if not added_any:
            return content

        insert_match = re.search(r"(?im)^#\s+(instruction|workflow)\b.*$", content)
        if insert_match:
            insert_at = insert_match.end()
            return content[:insert_at] + "\n\n" + block + "\n" + content[insert_at:].lstrip("\n")

        fm_match = re.match(r"^---\n.*?\n---\n?", content, re.DOTALL)
        if fm_match:
            insert_at = fm_match.end()
            return content[:insert_at].rstrip() + "\n\n" + block + "\n" + content[insert_at:].lstrip("\n")

        return block + "\n" + content.lstrip("\n")

    section = ""
    if entrypoints or references or others:
        section = "\n\n## 辅助文件\n\n"
        if entrypoints:
            section += "### 执行入口\n\n"
            for p in entrypoints:
                section += line_for(p)
            section += "\n"
        if references:
            section += "### 参考资料\n\n"
            for p in references:
                section += line_for(p)
            section += "\n"
        if others:
            section += "### 其他\n\n"
            for p in others:
                section += line_for(p)
            section += "\n"

    if has_section and not should_replace:
        injected = inject_progressive_references(skill_content)
        return injected

    injected = inject_progressive_references(base_content)
    if not section:
        return injected.rstrip() + "\n"
    return injected.rstrip() + section.rstrip() + "\n"


def extract_referenced_skill_paths(skill_content: str) -> set[str]:
    if not skill_content:
        return set()
    matches = re.findall(r"\b(?:scripts|references)/[A-Za-z0-9._/\-]+\.[A-Za-z0-9]+\b", skill_content)
    return set(matches)


def build_auto_snapshot_reason(mode: str, diagnoses: list) -> str:
    base = f"自动优化: {mode} mode"
    if not diagnoses:
        return f"{base}（无诊断）"

    def clean_line(text: str) -> str:
        text = (text or "").strip()
        text = re.sub(r"\s+", " ", text)
        return text

    def format_item(d) -> str:
        dim = clean_line(str(getattr(d, "dimension", "") or "")) or "Unknown"
        severity = clean_line(str(getattr(d, "severity", "") or ""))
        desc = str(getattr(d, "description", "") or "").strip() or "（无描述）"
        header = f"[{dim}]"
        if severity:
            header = f"[{dim}/{severity}]"
        return f"{header} {desc}"

    lines = [base, "问题列表:"]
    for i, d in enumerate(diagnoses, start=1):
        lines.append(f"- {i}. {format_item(d)}")
    return "\n".join(lines)


def print_completion_summary(
    success: bool,
    output_dir: Path,
    skill_name: str,
    diagnoses_count: int,
    auxiliary_files: list[str],
    mode: str
):
    """
    输出清晰明确的完成状态摘要
    """
    print("\n" + "=" * 60)
    
    if success:
        print("✅ 优化完成！")
    else:
        print("⚠️ 优化部分完成")
    
    print("-" * 60)
    print(f"Skill 名称: {skill_name}")
    print(f"优化模式: {mode}")
    print(f"诊断数量: {diagnoses_count}")
    print(f"输出目录: {output_dir}")
    
    if auxiliary_files:
        print(f"\n生成的文件:")
        print(f"  - SKILL.md")
        for f in auxiliary_files:
            print(f"  - {f}")
    
    if diagnoses_count > 0:
        print(f"\n诊断报告:")
        print(f"  - diagnoses.json")
        print(f"  - OPTIMIZATION_REPORT.md")
    
    print("=" * 60)


