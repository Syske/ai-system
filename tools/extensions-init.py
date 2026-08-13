r"""Initialize the extensions directory as a standalone git repository.

Purpose: quickly bootstrap a fresh company/platform extension directory when
onboarding a new environment or company. Generic scaffolding only — no
company-specific content (branch conventions, remote URLs, credentials)
is embedded; providers supply those per environment.

Usage:
    python tools/extensions-init.py                       # dir + git + templates
    python tools/extensions-init.py --remote <git-url>    # + remote add + first push
    python tools/extensions-init.py --email <e> --name <n>  # + committer identity
    python tools/extensions-init.py --force               # (no-op today; reserved)
    python tools/extensions-init.py --check               # verify an existing init

Non-destructive and idempotent: never deletes or overwrites existing
directories, files, or git config. Re-running is safe.

Steps:
1. Ensure extensions/ exists (setup.py already scaffolds it; this is a guard).
2. Write extensions/.gitignore from the generic template (only if missing).
3. Write extensions/README.md from the generic template (only if missing).
4. git init with branch main (only if no .git yet).
5. Set committer identity from --name/--email (repo-local, only when provided
   and only when not already set to the same value).
6. With --remote: git remote add origin + first push -u origin main.
7. Scaffold one example extension skeleton (example-hello/ with SKILL.md +
   OPTIMIZATION_LOG.md templates) — a starting point, never a company asset.
8. Print the post-init checklist (sensitive ignore list, company remote, etc.).

Every tools/*.py must be registered in tools/README.md (check_tools_readme).
"""

import argparse
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
DEFAULT_WORKSPACE = ROOT.parent

GITIGNORE_TEMPLATE = """# Secrets / credentials
*.env
**/.env
credentials.json
!credentials.json.example

# Debug / runtime artifacts
tmp_docs/
**/tmp_docs/
*_debug_*.json

# Python
__pycache__/
*.py[cod]
.pytest_cache/
.mypy_cache/

# OS
.DS_Store
Thumbs.db

# AI workspace root is NOT part of this repo
# (extensions/ 独立仓库；ai-system/ 由其自身仓库管理)
/ai-system/
/workspaces/
/projects/
/docs/
/outputs/
/temp/
/worktrees/
/launch/
/methodologies/
/repositories/
/.pi/
/.codescope/
/.obsidian/
"""

README_TEMPLATE = """# Extensions — 公司/平台技能扩展目录

本目录存放**公司特有 / 平台特有**的技能（extension skills），与 ai-system 内置
通用技能（`ai-system/skills/`）分离。

## 定位与边界

- **不被 agent 自动扫描**：目录名 `extensions` 避开 opencode/pi 的自动发现路径
  （`skills` / `.claude/skills` / `.agents/skills`），技能不会污染 agent 上下文。
- **显式加载**：通过 `aic skill-launch`（选 skill + agent + 任务）显式触发。
- **配置驱动**：分组/组合/任务模板见 `ai-system/config/skill-groups.yaml`；
  位置经 `config/environments/{env}.yaml → layers.skills` 配置（默认本目录）。

## 目录约定

每个技能一个子目录，含 `SKILL.md`（平台大写约定）+ 辅助文件（scripts/、
references/、模板等）。

## OPTIMIZATION_LOG 约定

每次**实战优化**后，在技能目录内维护 `OPTIMIZATION_LOG.md`，追加一条记录
（顶部为最新）。统一字段：

| 字段 | 说明 |
|---|---|
| 触发场景 | 为什么优化（真实执行暴露的问题） |
| 问题清单与根因 | 问题列表 + 根因分析 |
| 改动内容 | 新增/修改文件 + 说明 |
| 验证结果 | 如何验证（测试/实测/审查） |
| 影响评估 | 正确性/可维护性/可移植性/遗留风险 |
| 复现与回归建议 | 新环境如何复现 + 回归检查点 |

> 与 `skill-optimizer` 的 `opt.sh` 快照（`~/.agent-insight/skill-history/`）定位
> 不同：前者记录实战优化决策，后者为自动化工具的版本产物，两者可并存。

## 版本管理

本目录是**独立 git 仓库**（与 ai-system 分离），由
`python tools/extensions-init.py` 初始化。远程仓库地址与提交者身份按环境
配置（`--remote` / `--email` / `--name`）；公司特定排除项请在 `.gitignore`
中按需补充。
"""

EXAMPLE_SKILL_MD = """---
name: example-hello
description: >
  示例扩展技能骨架。复制本目录为 <your-skill-name>/ 后按需修改：
  说明该技能做什么、何时触发、何时不触发（反触发），100-1024 字符，
  含 ≥3 触发短语与 "Does NOT" / "not responsible for" 反触发。
  Trigger when: ... / Does NOT: ...
---

# <Skill Name>

## Overview

一句话说明职责。

## Activation

- 何时激活
- 何时不激活

## Workflow

1. 步骤一
2. 步骤二

## Output

返回什么。
"""

EXAMPLE_OPTIMIZATION_LOG = """# OPTIMIZATION_LOG

<!-- 每次实战优化后在顶部追加一条记录 -->

## YYYY-MM-DD 标题

- 触发场景: 为什么优化
- 问题清单与根因: 问题列表 + 根因分析
- 改动内容: 新增/修改文件 + 说明
- 验证结果: 如何验证（测试/实测/审查）
- 影响评估: 正确性/可维护性/可移植性/遗留风险
- 复现与回归建议: 新环境如何复现 + 回归检查点
"""


def _git(ext_dir: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["git", "-C", str(ext_dir), *args],
        capture_output=True,
        text=True,
    )


def init_extensions(
    *,
    remote: str | None,
    email: str | None,
    name: str | None,
    workspace: Path,
    check: bool,
) -> int:
    ext_dir = workspace / "extensions"

    if check:
        return _check(ext_dir)

    ext_dir.mkdir(parents=True, exist_ok=True)

    # 1. .gitignore（仅缺失时写入）
    gi = ext_dir / ".gitignore"
    if not gi.exists():
        gi.write_text(GITIGNORE_TEMPLATE, encoding="utf-8")
        print(f"wrote {gi.relative_to(workspace)}")
    else:
        print(f"keep existing {gi.relative_to(workspace)}")

    # 2. README.md（仅缺失时写入）
    readme = ext_dir / "README.md"
    if not readme.exists():
        readme.write_text(README_TEMPLATE, encoding="utf-8")
        print(f"wrote {readme.relative_to(workspace)}")
    else:
        print(f"keep existing {readme.relative_to(workspace)}")

    # 3. git init（仅缺失时）
    if not (ext_dir / ".git").exists():
        _git(ext_dir, "init", "-b", "main")
        print("git init -b main")
    else:
        print("git already initialized")

    # 4. 提交者身份（仅当提供且不同时设置；仓库级，不动全局）
    if email:
        cur = _git(ext_dir, "config", "user.email").stdout.strip()
        if cur != email:
            _git(ext_dir, "config", "user.email", email)
            print(f"set user.email={email}")
    if name:
        cur = _git(ext_dir, "config", "user.name").stdout.strip()
        if cur != name:
            _git(ext_dir, "config", "user.name", name)
            print(f"set user.name={name}")

    # 5. 示例扩展骨架（仅缺失时）
    example = ext_dir / "example-hello"
    if not example.exists():
        example.mkdir(parents=True, exist_ok=True)
        (example / "SKILL.md").write_text(EXAMPLE_SKILL_MD, encoding="utf-8")
        (example / "OPTIMIZATION_LOG.md").write_text(
            EXAMPLE_OPTIMIZATION_LOG, encoding="utf-8"
        )
        print(f"scaffolded example extension: {example.relative_to(workspace)}")
    else:
        print("example-hello already exists, skipped")

    # 6. 远程绑定（仅 --remote 提供且未配置时）
    if remote:
        existing = _git(ext_dir, "remote", "get-url", "origin").stdout.strip()
        if not existing:
            _git(ext_dir, "remote", "add", "origin", remote)
            print(f"remote origin -> {remote}")
            # 首次提交（若工作区有未提交内容）并推送
            status = _git(ext_dir, "status", "--porcelain").stdout.strip()
            if status:
                _git(ext_dir, "add", "-A")
                _git(
                    ext_dir, "commit", "-m",
                    "chore: 初始化 extensions 目录（.gitignore/README/示例扩展）",
                )
                print("initial commit created")
            push = _git(ext_dir, "push", "-u", "origin", "main")
            print(push.stdout.strip() or push.stderr.strip())
            if push.returncode != 0:
                print("push failed (check remote url / auth / commit identity)")
        else:
            print(f"remote origin already set: {existing}")

    print()
    print("post-init checklist:")
    print("  1. 按公司调整 .gitignore 排除项（敏感文件/调试产物）")
    print("  2. 提交者身份合规（Codeup 等平台要求 author==push user）")
    print("  3. 删除示例扩展 example-hello/ 或复制为真实技能")
    print("  4. 公司分支规范等由扩展提供者实现（契约见 ai-system）")
    return 0


def _check(ext_dir: Path) -> int:
    problems = []
    if not ext_dir.exists():
        problems.append("extensions/ 不存在（先运行 setup.py 或本工具）")
    if not (ext_dir / ".gitignore").exists():
        problems.append("缺少 .gitignore")
    if not (ext_dir / "README.md").exists():
        problems.append("缺少 README.md")
    if not (ext_dir / ".git").exists():
        problems.append("不是 git 仓库")
    if problems:
        for p in problems:
            print(f"[FAIL] {p}")
        return 1
    print("extensions init OK: .gitignore / README.md / git 仓库均存在")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--remote", help="extensions 远程仓库 git url（如 Codeup）")
    parser.add_argument("--email", help="提交者邮箱（仓库级，如 lei.cao@coolcollege.cn）")
    parser.add_argument("--name", help="提交者姓名（仓库级）")
    parser.add_argument("--workspace", type=Path, default=DEFAULT_WORKSPACE,
                        help=f"workspace 根目录（默认 {DEFAULT_WORKSPACE}）")
    parser.add_argument("--check", action="store_true",
                        help="校验现有初始化状态（幂等检查）")
    args = parser.parse_args()

    return init_extensions(
        remote=args.remote,
        email=args.email,
        name=args.name,
        workspace=args.workspace,
        check=args.check,
    )


if __name__ == "__main__":
    sys.exit(main())
