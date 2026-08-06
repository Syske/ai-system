# Change Proposal: P12 — 移除 langchain 依赖（openai SDK 直调）

| Field | Value |
|---|---|
| Status | **Implemented** |
| Type | Structural (dependency removal + core path rewrite) |
| Author | AI Maintainer |
| Created | 2026-08-06 |
| Reference | MAINTENANCE-2026-08-06.md; user decision "Option A — 移除 langchain 改 openai SDK 直调" |
| Process | OPERATIONS §12 Change Management |

---

## 1. Problem

skill-optimizer 依赖 langchain 4 处，但当前**实际不可运行**：

| 位置 | 用法 | 问题 |
|------|------|------|
| `core.py:21` | `langchain_openai.ChatOpenAI` | 薄包装，可替换 |
| `engine/mutator.py:7-9` | `create_agent` + `HumanMessage` + `@tool` | **核心路径**；`create_agent` 是 langchain 0.3+ API |
| `engine/report_generator.py:4` | `HumanMessage` | 仅构造消息 |
| `evaluation/evaluate_skill.py:8` | `ChatOpenAI` | 独立入口 |

三个根因事实：
1. `requirements.txt` 声明 `langchain>=0.1.0`，但代码用 0.3+ 的 `create_agent` —— 按声明安装必失败（实测全局 0.2.17 导入即崩）。
2. `mutator.py:90` `hasattr(self.model_client, "llm")` 恒真（RealLLMClient 必有 .llm）→ **永远走 create_agent 路径**，legacy 模式到不了，langchain 是硬依赖。
3. `.opt` 虚拟环境不存在 → 当前处于"装了也跑不起来"状态。

价值分解：真正有价值的是 agentic tool-calling 循环设计（分块写文件/完整性校验/多轮重试，均自实现），langchain 仅提供 ~10% 框架胶水（create_agent 循环 + @tool + HumanMessage），却引入版本陷阱与庞大依赖树。

## 2. 方案（Option A — 移除）

| 文件 | 改造 |
|------|------|
| `requirements.txt` | 移除 `langchain` / `langchain-openai` / `langchain-core`；新增 `openai>=1.0` |
| `core.py` | `RealLLMClient` 改用 `openai.OpenAI(base_url, api_key, http_client=httpx.Client(...))`；保留 `__call__(prompt)->str`；新增 `chat(messages, tools=None)` 原生 function-calling 接口 |
| `engine/mutator.py` | `_mutate_with_tools` 重写 agent 循环为原生 tools 循环（messages + tool_calls 执行 + 追加结果），复用全部 chunk 校验/retry/多轮逻辑；`@tool` 改为 JSON schema 定义 |
| `engine/report_generator.py` | `.llm.invoke([HumanMessage(...)])` → `self.model_client(prompt)` |
| `evaluation/evaluate_skill.py` | `ChatOpenAI` → openai SDK 直调；`SkillEvaluator` 改收 callable |
| `engine/evaluation_adapter.py` | `getattr(.llm)` → 直接传 model_client |

## 3. Validation

- 全部脚本 `py_compile` 通过
- `import main` / `import actions` 在全局环境可导入（不再依赖 langchain）
- agent 循环 stub 冒烟：tools 定义、chunk 组装、retry 逻辑保持
- repo-lint / check.py / path-audit / proposal-audit 全绿

## 4. Risks

- **中**：mutator agent 循环重写是核心路径，需保持 tool 语义（write_file_chunk/delete_file/record_fix）与消息流一致。
- **低**：openai SDK 的 tool_calls 响应结构与 create_agent 的 stream 事件不同，解析逻辑需对应改写。
- 不改变 CLI/工作流/快照语义。

---

## Review Log

| Reviewer | Decision | Date |
|---|---|---|
| User (AI Maintainer operator) | **Approved — Option A（移除 langchain，openai SDK 直调）** | 2026-08-06 |

---

## Implementation Record (2026-08-06)

Applied per approval (OPERATIONS §12 → Implement → Validate):

1. `scripts/core.py` — `RealLLMClient` 改用 `openai.OpenAI`（httpx client）；保留 `__call__(prompt)->str`，新增 `chat(messages, tools=None)` 原生 function-calling 接口；暴露 `self.model_name`。
2. `scripts/engine/mutator.py` — 移除 langchain imports（create_agent/HumanMessage/@tool）；`@tool` 函数改为普通函数；新增 `TOOL_SCHEMAS`（3 个 openai JSON schema：write_file_chunk/delete_file/record_fix）+ `TOOL_IMPL` 分发表；`run_agent_round` 重写为原生消息循环（system+user → tool_calls 执行 → tool 结果回传 → 直至无 tool_calls）；`create_agent` 块移除；模式判定改 `hasattr(model_client, "chat")`。chunk 完整性校验/retry/多轮逻辑全部保留。
3. `scripts/engine/report_generator.py` — 移除 HumanMessage；报告生成改 `self.model_client(prompt)` 直调。
4. `scripts/evaluation/evaluate_skill.py` — ChatOpenAI → openai SDK；`call_deepseek_api` 直调 chat.completions；`SkillEvaluator.evaluate_meta` 改 callable（`self.llm(prompt)`）；`_coerce_llm_response_text` 兼容 openai 响应。
5. `scripts/engine/evaluation_adapter.py` — `SkillEvaluator` 传 callable model_client（不再取 `.llm`）。
6. `requirements.txt` — 移除 langchain/langchain-openai/langchain-core；新增 `openai>=1.0.0`。
7. `model_config_detector.py:224` 注释提及 langchain-openai（纯注释，未动）。

**Validation（全绿）**：
- 全部 .py `py_compile` 通过；langchain 引用清零（仅 1 处历史注释）
- `import main` / `import actions` 在全局 Python 3.10 **可直接导入**（此前因 langchain 版本陷阱必失败）
- mutator agent 循环 stub 冒烟：write_file_chunk 保存 chunk、record_fix 写 changelog、组装 SKILL.md 正确、3 个 tool schemas 传递正确 ✅
- repo-lint 0/0/9、check.py PASS 0 warning、path-audit 0 broken、proposal-audit 0 遗留

**Deviations**: 无。
**Risks**: 原生 tool-calling 依赖模型端点支持 `tools` 参数（DeepSeek/OpenAI 兼容端点均支持）；`create_agent` 的 stream 事件模型替换为单次轮询循环（每次 tool 调用为一次 API 请求），行为等价但请求次数可能略增。
