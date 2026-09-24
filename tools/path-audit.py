import re
import sys
from pathlib import Path

AIS = Path(__file__).resolve().parents[1]
WS = AIS.parent

KNOWN_PLACEHOLDER_DEBT = {
    # 记忆索引中保留的目录引用（目标 not yet created)
    "governance/memory/integration/",
    "governance/memory/python/",
    # 记忆条目内的历史引用（描述迁移前chive state)
    "governance/standards/common/code-quality.md",
}

FALSE_POSITIVES = {
    "../ai-runtime/",
    # 运行时态（logs/ metrics/）已迁至工作区层（2026-09-24），仓库内不再存在；
    # 文档中的 logs/… metrics/… 引用属合法（与 metrics/baseline- 同类，均非仓库内路径）
    "metrics/baseline-",
    "metrics/maintain-",
    "metrics/prompt-",
    "metrics/quick-check-",
    # 命令/运行时文档引用的生成产物（运行时产生）uced at run time)
    "../ai-system-pack",
    "config/environments/local.yaml",
    "ai-system/config/environments/context.yaml",
    # metrics/ 被 gitignore（运行时快照）；CI checkout 中不存在ckouts
    "ai-system/metrics",
    # 运行时诊断日志已移到工作区层 <workspace>/logs/（仓库外，2026-09-24 事故后），
    # 仓库内不再存在；文档里残留的 logs/ 引用仍属合法（与 metrics/ 同类，均非仓库内路径）
    "ai-system/logs/",
    "ai-system/logs",
    "logs/",
    "logs",
    # governance/DIRECTORY-RESPONSIBILITY.md 中的故意反例BILITY.md
    "ai-system/skills/foo/report.md",
    "config/governance/",
    "reports/foo-skill/",
    # skills/idea-build 文档引用的本机 JDK/Maven 路径（外部绝对路径的
    # 目录尾匹配，非仓库内缺失文件；环境运行时引用）
    "tools/java/jdk-17",
    "tools/java/jdk8",
    # idea-build SKILL.md 文档化的本机绝对工具路径（环境配置引用，
    # 非仓库断链；与 local.yaml 的 java_home/maven_home 同类）
    r"D:\tools\java\jdk8",
    r"D:\tools\java\jdk-17",
    r"D:\tools\apache-maven-3.6.3",
    # 机器层环境配置 ~/.config/ai-system/env.yaml（P29：首启生成，运行时环境，
    # 非仓库内路径；~ 被剥离后呈 config/... 相对形，实为 home 引用）
    "config/ai-system/env.yaml",
    ".config/ai-system/env.yaml",
    # skill-author 约定示例/代码片段的 token（resolve_environment 的
    # paths 键、反例 "C:\Program Files\Java\..."）——非真实依赖
    "config/paths",
    r"C:\Program",
    # config/maintenance.yaml scope 行的 delta 域清单（斜杠分隔的多个
    # 顶层域，非单一路径）；PATH_RE 将其整体匹配为一个 token 误报断链
    "cli/config/governance/reports/skills/templates/workflows",
}

# 仅示例引用（T2/Batch 2）：出现在文档示例中的路径de doc examples,
# 模板或占位片段中——它们是说明性的， not real
# 非真实依赖。与 FALSE_POSITIVES 分开保持可区分性inction stays
# 可见。
EXAMPLE_ONLY = {
    # governance/standards/common/cross-project-sync.md：说明性的ive **/ wildcard
    "../AuditTypeEnum.java",
    # skills/skill-sync/SKILL.md（2026-09-23 已归档至 archived/skills/skill-sync/，
    # 该目录不在 path-audit 扫描范围内）："上传你构建的技能"示例目标
    "../skill-generator",
    # skills/open-cli/SKILL.md：~/.opencli 下的正确示例路径ncli/clis
    "cli/clis/aem/page-views.ts",
    "cli/clis/bilibili/favorites.ts",
    "cli/clis/twitter/lists.yaml",
    # skills/bugfix/feedback-loop.md："逐一切除 inputs/callers/ata" prose
    "config/data",
    "skills/my-skill",
    "skills/openeuler-docker-fault",
    # skills/index-project/SKILL.md：$HOME/.claude 工具路径（运行时环境）ime env)
    "tools/code-indexer/reindex_cli.py",
}

# 运行时数据根：workspace 级目录，保存运行时创建的内容oject/workspace
# 对这些的引用不是源码依赖，ource-code
# 审计跳过它们（除非目标也存在于o exists inside
# AI System 仓库内）。
RUNTIME_ROOTS = (
    "workspaces/",
    "projects/",
    "repositories/",
)

# 匹配必须从**记号边界**开始：不得把长路径/长单词的**中间段**当作引用。
# 实测误报（2026-09-23，一轮内 3 次）：`archived/skills/skill-sync/…` 命中 `skills/skill-sync/…`、
# `kubeconfig/连接错误时` 命中 `config/连接错误时`。与 DOT_REL_RE 的既有负向后顾同源
# （另一侧的历史误报：省略号路径 `.../x.java` 的尾部）。
# 注：本修复只治「中间段」类；「散文里的 word/word」（如 governance/infra commits）仍会被匹配，
# 那类需改措辞（不是路径引用的语义无法从形态区分）。
PATH_RE = re.compile(
    r"(?<![\w./\\-])"
    r"(?:[A-Za-z]:[\\/][^\s`'\")\]，。；;|]+"
    r"|(?:\.\./)+[\w./\-]+"
    r"|(?:ai-system|governance|workflows|templates|skills|loaders|cli|config|tools|"
    r"metrics|reports|workspaces|projects|repositories)"
    r"/[\w{}$./*\-]+)"
)

# 显式相对引用（`./x.md`）：以文件自身目录为基准解析。
# 原实现只解析 `../` 与「仓库顶层目录名开头」两种形态，技能内相对引用（如
# skills/open-cli/SKILL.md 的 `./references/CLI-ONESHOT.md`）完全是审计盲区
# （2026-09-21 外部盲检 V6 + P60 §5.3）。只收 `./` 前缀：语义无歧义。
# 负向后顾：避免命中省略号路径 `.../x.java` 的尾部（实测误报）。
DOT_REL_RE = re.compile(
    r"(?<![\w./])\./[\w{}$./*\-]+\.(?:md|yaml|yml|py|sh|json|txt|xml|java|js|template)"
)


def is_runtime_reference(tok):
    """True if tok points into a runtime data root outside the repo.

    Runtime roots (workspaces/projects/repositories) hold
    content created at run time under the workspace root. They are not
    source-code dependencies, so references into them are not audited.
    """

    return tok.startswith(RUNTIME_ROOTS)


def collect_files():

    scan = []

    for d in [
        AIS / "workflows",
        AIS / "templates" / "runtime",
        AIS / "templates" / "prompts",
        AIS / "loaders",
        AIS / "cli" / "commands",
        AIS / "config",
        AIS / "governance",
        AIS / "rfc",
    ]:
        scan += [
            p for p in d.rglob("*")
            if p.is_file() and p.suffix in (".md", ".yaml")
        ]

    scan += [
        AIS / "OPERATIONS.md",
    ]

    # 全部技能文件（T1/Batch 2：此前仅扫描 skills/implement，t was
    # 导致 repository-governor 等成为审计盲区）。nd spot).
    scan += [
        p for p in (AIS / "skills").rglob("*")
        if p.is_file()
        and p.suffix in (".md", ".yaml", ".yml")
        and "archived" not in p.parts
    ]

    return [
        p for p in scan
        if p.exists() and "archived" not in p.parts
    ]


def main():

    missing = {}
    absolute = {}
    checked = 0
    placeholders = 0

    files = collect_files()

    for f in files:

        text = f.read_text(encoding="utf-8", errors="replace")
        rel = str(f.relative_to(WS))

        # 显式相对引用（./x）以文件目录为基准解析（P60 §5.3）
        for m in DOT_REL_RE.finditer(text):

            tok = m.group(0).rstrip(".,;:)`'\"*")

            if "{" in tok or "*" in tok or "$" in tok or "<" in tok:
                placeholders += 1
                continue

            if tok in FALSE_POSITIVES or tok in EXAMPLE_ONLY:
                continue

            checked += 1

            if not (f.parent / tok).resolve().exists():
                missing.setdefault(tok, set()).add(rel)

        for m in PATH_RE.finditer(text):

            raw_tok = m.group(0)
            tok = raw_tok.rstrip(".,;:)`'\"*")

            after = text[m.end():m.end() + 1]

            if "<" in after or after == "{":
                placeholders += 1
                continue

            # 被 rstrip 剥掉的尾部 '*' 仍是通配符占位符older
            # （如 `rfc\RFC-*`）。检查剥离前的原始 token。
            if (
                "{" in tok or "*" in raw_tok or "$" in tok or "<" in tok
            ):
                placeholders += 1
                continue

            if tok in FALSE_POSITIVES:
                continue

            if tok in EXAMPLE_ONLY:
                continue

            if re.match(r"[A-Za-z]:", tok):

                if "://" in tok:
                    continue

                # 自引用绝对路径：描述 ai-system 自身结构的文档
                # （如统计 D:/workspace/ai-workspace/ai-system/rfc 下的
                # RFC 数量）。这些指向仓库根自身，不是外部环境——
                # 按前缀匹配跳过，不用 target.exists()：Windows 风格
                # 绝对路径在 Linux CI checkout 上永不存在，但前缀本身
                # 已证明它引用仓库自身树（非外部环境）。
                ais_norm = str(AIS).replace("\\", "/").rstrip("/")
                tok_norm = tok.replace("\\", "/").rstrip("/")
                if tok_norm == ais_norm or tok_norm.startswith(ais_norm + "/"):
                    continue

                if "config/environments" not in rel.replace("\\", "/"):
                    absolute.setdefault(tok, set()).add(rel)

                continue

            if tok.startswith("../"):

                checked += 1

                if not (f.parent / tok).resolve().exists():
                    missing.setdefault(tok, set()).add(rel)

                continue

            checked += 1

            candidates = [AIS / tok, WS / tok]

            if tok.startswith("ai-system/"):
                # `ai-system/X` 双形态解析：workspace 部署（WS/ai-system/X）与
                # CI checkout（仓库根即 ai-system → AIS/X）都可达；
                # 裸 `ai-system/`（目录引用）→ AIS 自身。
                candidates = [
                    AIS / tok[len("ai-system/"):],
                    WS / tok,
                ]

            if not any(c.exists() for c in candidates):
                if is_runtime_reference(tok):
                    continue
                missing.setdefault(tok, set()).add(rel)

    debt = {t: s for t, s in missing.items() if t in KNOWN_PLACEHOLDER_DEBT}
    broken = {t: s for t, s in missing.items() if t not in KNOWN_PLACEHOLDER_DEBT}

    print(
        f"files={len(files)} refs_checked={checked} "
        f"placeholders={placeholders} known_debt={len(debt)}"
    )

    print()
    print(f"BROKEN ({len(broken)}):")

    for tok in sorted(broken):

        print(f"  {tok}")

        for src in sorted(broken[tok]):
            print(f"      <- {src}")

    print()
    print(f"ABSOLUTE OUTSIDE environments ({len(absolute)}):")

    for tok in sorted(absolute):

        print(f"  {tok}")

        for src in sorted(absolute[tok]):
            print(f"      <- {src}")

    if broken or absolute:
        sys.exit(1)

    print()
    print("OK: no broken path dependencies")


if __name__ == "__main__":
    main()
