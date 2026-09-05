"""prepare 重入检测：加载已有 change 产物并按未决澄清驱动。

Change ID 字段收集后调用：若 workspaces/<project>/openspec/changes/<change-id>/
下已有 proposal.md（prepare 主链产物），读取 Readiness、Change Request 与
§8 澄清登记的未决项，供向导预填与提示。

重入语义：选择已有 change 时应承接已有分析（预填 Change Request、列出未决
澄清），而非重新收集必填项。首次运行（无产物）返回 None，走正常收集。
"""

import re
from datetime import datetime
from pathlib import Path

_HEADER_CR = re.compile(r"Change Request:\s*([^\n]+)")
_HEADER_READINESS = re.compile(r"Readiness:\s*\*\*([^*]+)\*\*")
_SECTION_8 = re.compile(
    r"^## 8\.\s*Clarification Questions.*?(?=^## 9\.)",
    re.M | re.S,
)
_ITEM = re.compile(r"^\d+\.\s*(.+)$", re.M)


def suggest_change_id():
    """新建 change 的建议默认：{YYYYMM}-（期间前缀，用户补描述）。

    首次输入 Change ID 时作为可编辑默认值，减少手输。完整自动生成
    （从 Change Request 派生 / AI 生成）另评估（见 P 提案，不在此实现）。
    """
    return datetime.now().strftime("%Y%m") + "-"


def change_artifact_path(workspaces_root, project, change_id):
    """prepare 主链产物路径：<workspaces_root>/<project>/openspec/changes/<change-id>/proposal.md。

    workspaces_root 为环境解析后的 workspaces 根（环境路径，如
    root.parent/workspaces 或 local.yaml 覆盖值），由调用方传入。
    """
    return (
        Path(workspaces_root)
        / project
        / "openspec"
        / "changes"
        / change_id
        / "proposal.md"
    )


def read_change_artifact(workspaces_root, project, change_id):
    """读取已有 prepare 产物；无产物或不可解析返回 None。

    返回: {path, change_request, readiness, open_questions}
    - change_request: 头部 "Change Request: ..."（重入预填用）
    - readiness: 头部 "Readiness: **...**"（状态提示用）
    - open_questions: §8 澄清登记中未决项摘要列表（未决 = 无 ~~ 删除线）
    """
    path = change_artifact_path(workspaces_root, project, change_id)
    if not path.exists():
        return None

    text = path.read_text(encoding="utf-8")
    header = text.split("## ", 1)[0]
    cr = _HEADER_CR.search(header)
    readiness = _HEADER_READINESS.search(header)

    return {
        "path": str(path),
        "change_request": (
            _strip_backticks(cr.group(1))
            if cr
            else ""
        ),
        "readiness": readiness.group(1).strip() if readiness else "",
        "open_questions": _open_questions(text),
    }


def _strip_backticks(value):
    """去掉 header 值外围的反引号（如 `init + supplement`）。"""
    return value.strip().strip("`").strip()


def _open_questions(text):
    """§8 Clarification Questions 中未决项（无删除线）的短摘要。"""
    section = _SECTION_8.search(text)
    if not section:
        return []

    open_qs = []
    for m in _ITEM.finditer(section.group(0)):
        item = m.group(1).strip()
        if "~~" in item:
            # 删除线 = 已解决/已关闭（proposal.md §8 约定）
            continue
        summary = re.split(r"[——。；;]", item)[0][:80]
        open_qs.append(summary.strip())
    return open_qs


def _slugify(text: str) -> str:
    """Change Request → kebab-case slug（P37 批次 1：Change ID 自动生成）。

    确定性规则，零 LLM（P28 评估结论）：取 Change Request 首段有意义词 →
    小写 kebab。保留中文词（不翻译，作为描述主体）；拼音/英文词原样小写。
    """

    if not text:
        return ""

    # 首段（按句号/换行切），去掉命令式与噪音词
    head = re.split(r"[。！？!?\n]", text)[0].strip()

    # 提取中文词块与字母数字词块（英文词块再按空格拆词，便于停用词过滤）
    tokens = []

    for m in re.finditer(
        r"[\u4e00-\u9fff]+|[a-zA-Z0-9]+(?:[ -][a-zA-Z0-9]+)*",
        head
    ):

        tok = m.group(0)

        if re.fullmatch(r"[\u4e00-\u9fff]+", tok):

            # 中文块：剔除前导停用词（整块无法匹配 stop 集合 → 前缀剔除，
            # P37 收尾：中文分词增强，避免 slug 以「实现/支持…」开头）
            for w in ("请", "实现", "完成", "支持", "新增", "添加", "修复", "优化", "重构"):
                if tok.startswith(w):
                    tok = tok[len(w):]
                    break

            if tok:
                tokens.append(tok)

        else:

            # 英文/数字块按空格拆词逐个过滤
            for w in re.split(r"[ -]+", tok):

                if w and re.match(r"^[a-z0-9]+$", w, re.I):
                    tokens.append(w)

    # 停用词（描述性前缀，不进入 slug）
    stop = {
        "请", "实现", "完成", "支持", "新增", "添加", "修复", "优化",
        "重构", "a", "an", "the", "to", "for", "of", "and", "with",
        "add", "implement", "support", "fix", "optimize",
    }

    kept = [p for p in tokens if p.lower() not in stop]

    slug = "-".join(kept)[:48].lower()

    return slug.strip("-")


def suggest_change_id(change_request: str = "") -> str:
    """新建 change 的建议默认：`{YYYYMM}-{slug}`（P37 批次 1）。

    有 Change Request 时自动派生 slug（`{YYYYMM}-{slug}`，用户可编辑）；
    无则仅 `{YYYYMM}-` 前缀（P28 既有行为，用户补描述）。
    """

    prefix = datetime.now().strftime("%Y%m") + "-"

    slug = _slugify(change_request)

    if not slug:
        return prefix

    return prefix + slug


def spec_reference_path(
    workspaces_root,
    project: str,
    change_id: str
):
    """verify 的 Specification Reference 自动推导（P37 批次 1）。

    从主链产物路径推导：`<workspaces_root>/<project>/openspec/changes/<change_id>/`
    （spec 工作流产物即该 change 目录下的 specs/）。返回目录绝对路径，
    供 verify 定位 spec 产物；目录不存在时仍返回路径（由运行期判断）。
    """

    return (
        Path(workspaces_root)
        / project
        / "openspec"
        / "changes"
        / change_id
    )
