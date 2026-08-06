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
    "metrics/baseline-",
    # 命令/运行时文档引用的生成产物（运行时产生）uced at run time)
    "../ai-system-pack",
    "config/environments/local.yaml",
    "ai-system/config/environments/context.yaml",
    # metrics/ 被 gitignore（运行时快照）；CI checkout 中不存在ckouts
    "ai-system/metrics",
    # governance/DIRECTORY-RESPONSIBILITY.md 中的故意反例BILITY.md
    "ai-system/skills/foo/report.md",
    "config/governance/",
    "reports/foo-skill/",
}

# 仅示例引用（T2/Batch 2）：出现在文档示例中的路径de doc examples,
# 模板或占位片段中——它们是说明性的， not real
# 非真实依赖。与 FALSE_POSITIVES 分开保持可区分性inction stays
# 可见。
EXAMPLE_ONLY = {
    # governance/standards/common/cross-project-sync.md：说明性的ive **/ wildcard
    "../AuditTypeEnum.java",
    # skills/skill-sync/SKILL.md："上传你构建的技能"示例le target
    "../skill-generator",
    # skills/open-cli/SKILL.md：~/.opencli 下的正确示例路径ncli/clis
    "cli/clis/aem/page-views.ts",
    "cli/clis/bilibili/favorites.ts",
    "cli/clis/twitter/lists.yaml",
    # skills/bugfix/feedback-loop.md："逐一切除 inputs/callers/ata" prose
    "config/data",
    # skills/iterative-optimizer/examples/*：模板占位符
    "skills/my-skill",
    # skills/skill-optimizer/workflow.md：/Users/xxx 示例命令d
    "skills/offline-disk-fault-diagnosis",
    # skills/iterative-optimizer/workflow.md：用户提示示例 skill
    "skills/openeuler-docker-fault",
    # skills/index-project/SKILL.md：$HOME/.claude 工具路径（运行时环境）ime env)
    "tools/code-indexer/reindex_cli.py",
}

# 运行时数据根：workspace 级目录，保存运行时创建的内容oject/workspace
# 对这些的引用不是源码依赖，ource-code
# 审计跳过它们（除非目标也存在于o exists inside
# AI System 仓库内）。
RUNTIME_ROOTS = (
    "methodologies/",
    "workspaces/",
    "projects/",
    "repositories/",
)

PATH_RE = re.compile(
    r"(?:[A-Za-z]:[\\/][^\s`'\")\]，。；;|]+"
    r"|(?:\.\./)+[\w./\-]+"
    r"|(?:ai-system|governance|workflows|templates|skills|loaders|cli|config|tools|"
    r"metrics|reports|methodologies|workspaces|projects|repositories)"
    r"/[\w{}$./*\-]+)"
)


def is_runtime_reference(tok):
    """True if tok points into a runtime data root outside the repo.

    Runtime roots (methodologies/workspaces/projects/repositories) hold
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
                candidates = [WS / tok]

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
