"""受保护路径检测（P72）。

判据（清单唯一来源：config/protected-paths.yaml）：
1. 受保护路径**缺失**（被删/被改名）→ 按清单 missing 强度（error / warn）
2. 受保护路径在 git 工作树/暂存区显示为**删除或重命名** → error
3. 历史位置（仓库内 logs/、metrics/）**出现** → warn（回归信号）
4. 非 git 仓库 / git 不可用 → warn（不阻断）

诚实边界：本检测只能**事后发现**，无法阻止命令本身（git 无 pre-clean 钩子）。
预防靠三层：位置（运行时态在仓库外）+ Always-Load 规则（默认拒绝）+ 本检测。
事故依据：reports/INCIDENT-2026-09-24-ignored-state-wipe.md
"""

import subprocess
from pathlib import Path

from .base import ROOT, load_yaml

CONFIG_REL = Path("config") / "protected-paths.yaml"

SPEC = ROOT / CONFIG_REL


def resolve(entry, root):
    """把清单条目解析为绝对路径（<repo> / <workspace> / ~ 三种占位符）。"""
    text = str(entry).strip()
    if text.startswith("<repo>/"):
        return Path(root) / text[len("<repo>/"):]
    if text.startswith("<workspace>/"):
        return Path(root).parent / text[len("<workspace>/"):]
    if text.startswith("~/"):
        return Path.home() / text[2:]
    return Path(text)


def load_spec(root):
    """读取清单；返回 dict；文件缺失/不可解析 → {__error__: ...}。"""
    path = Path(root) / CONFIG_REL
    if not path.exists():
        return {"__error__": f"missing {CONFIG_REL}"}
    data = load_yaml(path)
    if not isinstance(data, dict) or "__error__" in data:
        return {"__error__": f"unreadable {CONFIG_REL}"}
    return data


def _git_deleted_paths(root):
    """git status --porcelain 中处于删除/重命名状态的仓库相对路径集合；非 git → None。"""
    try:
        out = subprocess.run(
            ["git", "-C", str(root), "status", "--porcelain"],
            capture_output=True, text=True, timeout=60,
        )
    except (OSError, subprocess.SubprocessError):
        return None
    if out.returncode != 0:
        return None
    deleted = set()
    for line in out.stdout.splitlines():
        if len(line) < 4:
            continue
        code, entry = line[:2], line[3:].strip()
        if "D" not in code and "R" not in code:
            continue
        if " -> " in entry:                      # 重命名：记录旧路径与新路径
            old, new = (part.strip() for part in entry.split(" -> ", 1))
            deleted.add(old)
            deleted.add(new)
        else:
            deleted.add(entry.strip('"'))
    return deleted


def check_protected_paths(c, root=None):
    """P72 检测主体（root 可注入，便于单测）。"""
    root = Path(root or ROOT)
    spec = load_spec(root)
    if "__error__" in spec:
        c.warn(f"protected-paths: {spec['__error__']} (P72 check skipped)")
        return

    git_deleted = _git_deleted_paths(root)

    for klass in spec.get("classes") or []:
        strength = str(klass.get("missing", "error")).lower()
        why = klass.get("why", "")
        for entry in klass.get("paths") or []:
            target = resolve(entry, root)
            if not target.exists():
                msg = (f"protected path missing: {entry} [{klass.get('id')}] — {why}"
                       f" (see {CONFIG_REL})")
                c.error(msg) if strength == "error" else c.warn(msg)
                continue
            try:
                rel = target.relative_to(root).as_posix()
            except ValueError:
                continue                          # 工作区/家目录项不参与仓库内 git 判据
            if git_deleted is None:
                continue
            if rel in git_deleted or any(d == rel or d.startswith(rel + "/") for d in git_deleted):
                c.error(
                    f"protected path deleted/renamed in git: {rel} [{klass.get('id')}]"
                    f" — restore it or get explicit user confirmation (see {CONFIG_REL})"
                )

    if git_deleted is None:
        c.warn("protected-paths: not a git work tree — deletion detection limited (P72)")

    for entry in spec.get("regression") or []:
        target = resolve(entry, root)
        if target.exists():
            c.warn(
                f"runtime state found inside the repo: {entry} — "
                "runtime state lives at workspace level (<workspace>/logs|metrics); "
                "presence signals a regression (see tools/runtime_state.py)"
            )