# Change Proposal: P35 — python 解释器鲁棒性（`python` shim 在 WSL 不可用，scripts/docs 用法不一）

| Field | Value |
|---|---|
| Status | **Proposed** |
| Type | Fix（环境/工具鲁棒性，多文件） |
| Author | AI Maintainer |
| Created | 2026-08-24 |
| Reference | logs recycle（P34 后知识生命周期 review 触发）：python-shim 在 4 份 log 重复出现未捕获——change-impact-20260818、maintain-20260820/20260823/20260824；maintain on-demand/prepare 2026-08-24 后续 |
| Process | OPERATIONS §12 Change Management |

---

## 1. Problem（现状问题 / 缺口）

`python`（pyenv-win shim）在 WSL 下不可执行（`cannot execute: required file not found`），每轮运行都重新发现「改用 `python3`」。证据：4 份 log 跨 08-18→08-24 重复记录同一摩擦，从未进 Coding Memory / env.yaml / 提案——正是「现成机制 dormant」的活样本。

根因双重：
- **环境层**：本机 `python` shim 坏（pyenv-win shim 在 WSL 不生效）。
- **系统层**：ai-system 的命令文档（`aic-maintain.md` 等）与部分调用处用 `python tools/...`，未对 `python`/`python3` 鲁棒化；`~/.config/ai-system/env.yaml`（P29）无 `runtime.python` 字段且无消费者，无法承载「本机解释器」事实。

后果：每轮重复踩坑、日志噪音、新机器/CI 可能复现。

## 2. Root-Cause（根因分析）

非「缺家」：env.yaml 已是机器层 config 家，但无 python 字段且无消费者——直接手记进去 = 死字段（Value-Burden）。真正缺的是「解释器事实有消费者」或「调用处对 python/python3 鲁棒」。属多文件改动（命令文档 + 可能的工具/脚本），非单点 doc drift，故走提案（Issue Capture triage：触及多文件 → 提案）。

## 3. Options（至少两方案对比）

| 选项 | 含义 | 评估 |
|---|---|---|
| **A. 命令文档统一 `python3` + 工具调用鲁棒化（Recommended）** | aic-*.md / OPERATIONS 的 `python tools/...` → `python3`（WSL/Linux 原生）；工具脚本 shebang 已是 `#!/usr/bin/env python3`（核对）；CI 文档注明 `python3` | 最小：文档级为主，运行时零改动；与 WSL/Linux 一致；CI 失误面下降 |
| B. env.yaml 增 `runtime.python` 字段 + setup.py 探测 + 调用处读取 | 配置驱动：env.yaml 记 `/usr/bin/python3`，工具/文档读它 | 更彻底但增消费者面（多个工具需改读 env），负担大；当前仅一台机器有问题，配置驱动收益未到触发点 |
| C. 修 pyenv shim / 软链 | 环境层修复 `python` 指向 | 否决：属本机环境治理，非 ai-system 职责；且不解决文档 `python`/`python3` 不一 |

## 4. Recommendation（推荐方案 + 理由）

**方案 A**。理由：
1. **最小**：以文档级统一为主（`python` → `python3`），运行时零改动；shebang 已是 python3（待实施时核对）。
2. **根因对齐**：摩擦出在「文档让 AI 跑 `python`」与「WSL 无 `python`」；统一 `python3` 直击。
3. **Evolution Principle**：仅一台机器、单一 shim 问题，配置驱动（B）收益未到触发点；若将来多机器/多解释器差异成真再升级 B（届时为真实新需求）。
4. B 的 env.yaml runtime 字段留作 B 升级时的落点，不预先引入。

## 5. Proposed Changes（具体改动清单，待批准实施）

> 仅记录提案，**不直接修改**；批准后按 OPERATIONS §12 Implement 阶段执行。

1. 全量核查 `python `（非 `python3`、非 `python3-`）调用点：`cli/commands/*.md`、`OPERATIONS.md`、`tools/README.md`、各 workflow/command 文档。
2. 命令文档统一 `python3 tools/...`（WSL/Linux 原生；Windows 端若有 py launcher 另注）。
3. 核对 `tools/*.py` shebang 均为 `#!/usr/bin/env python3`；若有用 `python` 的包装脚本，改 `python3`。
4. `quick-check.py` / `check.py` 内部若 `subprocess` 调 `python`，改 `python3` 或 `sys.executable`。
5. 不动 env.yaml（不引入死字段 runtime.python）；不动 pyenv shim（环境层）。
6. 不建 ADR（非 hard-to-reverse / 非 surprising / 无真实 trade-off）。

## 6. Validation Plan（如何验证）

- `grep -rn "\bpython\b" cli/commands/ OPERATIONS.md tools/README.md workflows/ | grep -v python3` → 命中清单即待改点；实施后应仅余历史 log/proposal 引用。
- `python3 tools/check.py` / `repo-lint.py` / `path-audit.py` / `quick-check.py` 全绿。
- `python3 -m unittest cli/tests/` 全 PASS。
- 行为回归：下一轮 maintain 在 WSL 直接跑 `python3 tools/quick-check.py` 不再触发 shim 报错；log 中不再出现「python shim 不可执行」。
- proposal-audit：P35 登记一致、无新增 ERROR/WARN。

## 7. Risks（风险与缓解）

- 风险低：以文档统一 + shebang 核对为主，无运行时/契约影响。
- 缓解：实施时区分 `python`（待改）与 `python3`/`python-*`/`pythonic`（保留）；Windows 端若依赖 py launcher，在相关文档注明跨平台调用约定。
- 遗留：本机 pyenv shim 坏仍存（环境层，非本提案范围），用户可自行修 shim 或接受用 python3。

---

## Review Log

| Reviewer | Decision | Date |
|---|---|---|
| User (AI Maintainer operator) | **Pending** | 2026-08-24 |

---

## Implementation Record

（批准并实施后追加：Applied per approval → 改动清单 → Validation 结果 → Status 置 Implemented + 同步 PROPOSALS.md/README）
