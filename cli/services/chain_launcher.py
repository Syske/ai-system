"""Chain (积木组合) launcher — a lightweight 链路口.

Entry flow:
1. Pick a named chain, or describe the scenario (keyword-matched to a chain).
2. Create a run context (outputs/chain/{yyMMdd}-{desc}/chain-manifest.yaml)
   that records the ordered blocks and their artifact handoff slots.
3. Assemble a per-block launch prompt (command/workflow via PromptBuilder,
   skill via the skill-launch template) so the user/agent runs each block in
   order, and each block's produced artifact is registered in the manifest.

Loose coupling + explicit handoff: block N reads block N-1's artifact from the
manifest instead of guessing paths.
"""

from pathlib import Path

from cli.services import chain as chain_util
from cli.services.prompt_builder import PromptBuilder
from cli.utils.menu import BACK, ask_text, choose, e

_SKILL_TEMPLATE = Path("templates") / "prompts" / "skill-launch.md"


def _render_skill_prompt(root, skill_name, task):
    """Render the skill-launch template for one skill (light reuse)."""

    from cli.utils.file import read_text

    template = read_text(root / _SKILL_TEMPLATE)

    for k, v in {
        "skill_list": f"- {skill_name} (skill) [core/extensions]",
        "task": task or "",
        "agent": "opencode",
    }.items():

        template = template.replace("{{" + k + "}}", str(v))

    return template


def run(wizard, agent=None, project=None):
    """Pick/describe a chain, create the run context, assemble the prompt.

    `project` is the wizard-selected Project ID (forwarded from the wizard
    flow); falls back to wizard.project, then asks when the chain requires
    one. Returns (prompt, agent) or None (cancelled).
    """

    root = wizard.root

    chains = chain_util.load_chains(root)

    if not chains:

        print("config/chains.yaml 未定义任何链路。")

        return None

    options = [
        f"{c.get('icon', '✨')} {c.get('label', c.get('name'))}"
        for c in chains
    ]
    options.append("💬  描述你的场景（AI 匹配链路）")
    options.append("❌  取消")

    idx = choose(
        f"{e('🧬 ')}选择链路（积木组合）——你想做什么？",
        options,
        0,
    )

    if idx is BACK or idx == len(options) - 1:
        return None

    if idx == len(options) - 2:

        # 自由文本场景：AI 匹配链路，文本即任务内容（不再二次询问）
        text = ask_text(
            "描述你的场景: ",
            note="如：分析代码并把结果发到 wiki / 改 bug 并出转测文档",
        )

        if text is BACK or not text:
            return None

        chain = chain_util.resolve_chain(text, chains)

        if chain is None:

            print(
                "未匹配到已知链路。可使用列表中的命名链路，或在 "
                "config/chains.yaml 登记后重试。"
            )

            return None

        task_text = text.strip()

    else:

        chain = chains[idx]

        # 先选链路，再输入内容（2026-09-11 用户反馈：先选链，避免不知道输入什么）
        task_text = ask_text(
            "任务内容 — 该链路具体要做什么？",
            note=f"如：{chain.get('scenario') or ''}",
        )

        if task_text is BACK:
            return None

        task_text = (task_text or "").strip()

    # 按链解析项目需求（required 才要求项目，none/optional 跳过 —— 不再一刀切）。
    # 项目优先取 wizard 菜单透传值；required 且无项目时必须提供（留空 = 取消），
    # 避免无项目上下文跑出无用链路（2026-09-11 用户实测）。
    project_req = chain_util.project_requirement(chain)

    project = project or getattr(wizard, "project", None) or None

    if project_req == "required" and not project:

        project = ask_text(
            "该链路需要项目上下文，请输入 Project ID / 仓库路径（留空 = 取消）: ",
        )

        if project is not None:
            project = project.strip()

        if not project:

            print("该链路需要项目上下文；未提供项目，链路不运行。")

            return None

    if project_req in ("required", "optional") and project:

        print(
            f"  · {e('📦 ')}project 上下文: {project}"
        )

    elif project_req == "none":

        print(
            f"  · {e('🧬 ')}该链路无需项目上下文（project=none）"
        )

    # 建运行上下文 + 交接清单
    run_dir, manifest_path = chain_util.create_chain_run(
        root,
        chain,
        outputs_root=getattr(wizard, "outputs_root", None),
    )

    # 组装各块启动 prompt
    builder = PromptBuilder()

    parts = [
        f"# 链路: {chain.get('label', chain.get('name'))}",
        f"运行上下文: {run_dir}",
        f"交接清单: {manifest_path}",
        "",
        "按序执行以下块；每完成一块，将其『产物路径』登记到交接清单，供下游块读取。",
        "",
    ]

    if task_text:
        parts.append(f"任务内容: {task_text}")
        parts.append("")

    # 可选块（optional: true）逐块询问，跳过则不入链（2026-09-11 用户需求：
    # 合并重复链路，发布 wiki 作为可选块）。
    included = []

    for b in chain.get("blocks", []):

        if not b.get("optional"):

            included.append(b)

            continue

        include = ask_text(
            f"可选块 {b.get('name')}（{b.get('type')}）——是否执行？（Enter=是，no=跳过）: ",
        )

        if include is BACK:
            return None

        if include and include.strip().lower() in ("no", "n", "cancel", "取消"):

            print(f"  ⏭️  跳过可选块: {b.get('name')}")

            continue

        included.append(b)

    total = len(included)

    for i, b in enumerate(included):

        btype = b.get("type")
        bname = b.get("name")
        bargs = {
            **(b.get("args") or {})
        }

        # 项目上下文注入（仅被块声明的字段过滤后可见）
        if project and btype in ("workflow", "command"):

            for key in ("Project ID", "Project", "Projects", "Workspace"):

                if key not in bargs:
                    bargs[key] = project

        parts.append(f"===== 块 {i + 1}/{total} [{btype}] {bname} =====")

        if btype in ("workflow", "command"):

            try:

                parts.append(
                    builder.build(bname, bargs)
                )

            except Exception as exc:

                parts.append(f"（该块 prompt 构建失败: {exc}）")

        elif btype == "skill":

            parts.append(
                _render_skill_prompt(
                    root,
                    bname,
                    bargs.get("task", "")
                )
            )

        parts.append("")
        parts.append(
            f"→ 完成本块后，请将产物路径登记到: {manifest_path}（块名 {bname}）"
        )
        parts.append("")

    prompt = "\n".join(parts)

    if agent is None:

        agent = (
            wizard.config.default_provider()
            if hasattr(wizard, "config")
            else "opencode"
        )

    print()
    print(
        f"{e('✅ ')}链路上下文已创建: {manifest_path}"
    )
    print(
        f"{e('🧬 ')}链路: {' → '.join(chain_util.block_names(chain))}"
    )

    return prompt, agent or "opencode"


def run_chain(wizard, agent=None, mode=None):
    """Unified /aic-chain entry (mode ignored for now)."""

    return run(wizard, agent)
