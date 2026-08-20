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


def run(wizard, agent=None):
    """Pick/describe a chain, create the run context, assemble the prompt.

    Returns (prompt, agent) or None (cancelled).
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

    else:

        chain = chains[idx]

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

    for i, b in enumerate(chain.get("blocks", [])):

        btype = b.get("type")
        bname = b.get("name")
        bargs = b.get("args") or {}

        parts.append(f"===== 块 {i + 1}/{len(chain.get('blocks', []))} [{btype}] {bname} =====")

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
