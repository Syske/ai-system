"""Skill 枚举的单一来源（R1：容器目录口径统一）。

**背景**（2026-09-21 盲检 R1 项）：`skills/architecture/` 这类**容器目录**
（自身无 `SKILL.md`，其下才是技能）曾同时被三个工具用三种口径处理：

| 工具 | 原口径 | 后果 |
|---|---|---|
| `repo-lint.py` | 无入口且有子目录 → **整棵跳过** | `architecture/` 下 **7 个技能永不进入 lint 视野** |
| `repo-metrics.py` | 顶层目录计数 | 把容器**多计为 1 个技能**（33 vs 32，口径分裂） |
| `dependency-graph.py` | 顶层目录计数 | 容器被记为"无入口的技能" |

本模块给出**唯一定义**：**技能 = 含 `SKILL.md`（或 `skill.md`）的目录，递归展开容器目录**；
容器目录本身**不是**技能。三个工具一律在此取值，避免口径漂移再现。
"""

from pathlib import Path

SKILLS_SUBDIR = "skills"


def resolve_root(root):
    """返回 ai-system 根目录（`--repo-root` 可能指向工作区或其下的 ai-system）。"""

    root = Path(root)

    if (root / "ai-system").is_dir():
        return root / "ai-system"

    return root


def find_entrypoint(skill_dir):
    """技能入口文件（大写优先，兼容历史小写）。"""

    for name in ("SKILL.md", "skill.md"):
        path = Path(skill_dir) / name
        if path.exists():
            return path

    return None


def _is_container(skill_dir):
    return find_entrypoint(skill_dir) is None and any(
        p.is_dir() for p in skill_dir.iterdir()
    )


def skill_dirs(root):
    """返回 `(skills, containers)`，均按路径排序。

    - `skills`：**叶子技能**目录（含容器目录下的嵌套技能）
    - `containers`：容器目录（自身无入口，仅承载子技能）

    隐藏目录（`.` 开头）一律忽略。
    """

    skills_dir = resolve_root(root) / SKILLS_SUBDIR

    if not skills_dir.exists():
        return [], []

    skills = []
    containers = []

    def walk(directory):
        for path in sorted(directory.iterdir()):
            if not path.is_dir() or path.name.startswith("."):
                continue
            if find_entrypoint(path) is not None:
                skills.append(path)
            elif any(p.is_dir() for p in path.iterdir()):
                containers.append(path)
                walk(path)

    walk(skills_dir)

    return sorted(skills), sorted(containers)