# Change Proposal: P23 — 跨平台（Linux/WSL + Windows）混合维护治理约定

| Field | Value |
|---|---|
| Status | **Implemented** |
| Type | Governance（治理条款登记，非结构改动） |
| Author | AI Maintainer |
| Created | 2026-08-14 |
| Reference | MAINTENANCE-2026-08-14（357 个 CRLF 噪音 M 条目；pre-commit hook 假阳性） |
| Process | OPERATIONS §12 Change Management |

---

## 1. Problem

ai-system 由 Linux（WSL2）与 Windows 双平台混合维护，但仓库**未声明平台契约**，导致：

1. **行尾噪音**：无 `.gitattributes`、autocrlf/eol 均未设置。仓库内 md 209 CRLF / 87 LF、py 79/42、sh 全 CRLF 混排 → 每次维护产生 357 个"纯行尾变更"M 条目，污染 diff、误报门禁（本次 section 顺序抽查即被 CRLF 干扰）。
2. **命令解析错位**：WSL 下 `python` 命中不可执行的 Windows pyenv shim → pre-commit hook 报错被 `|| true` 吞掉后仍打印 "gates passed"（**门禁假阳性**）。
3. **无规可循**：环境配置已双份（local.yaml / wsl.yaml）、路径转换已落地（`_linux_path`/`_repo_path`），但均无治理条款约束，后续新增内容可能回退。

## 2. Root-Cause

- git 层：无 `text=auto` 归一化声明，各平台按本机默认行尾写入工作区，入库内容随首个提交者而定。
- 命令层：hook/脚本裸用 `python`，未约定 `python3`。
- 治理层：LANGUAGE_CONVENTION / OPERATIONS 无平台章节。

## 3. Options

| Option | 描述 | 优点 | 缺点 |
|---|---|---|---|
| A（推荐） | 分层约定：L1 git 归一化（.gitattributes 入库，LF 唯一规范）+ L2 环境双份显式化 + L3 命令层 python3 + L4 文件系统操作纪律 + L5 门禁化（repo-lint 行尾规则） | 一次性根治行尾噪音；门禁防回退；改动集中、可验证 | 需一次全仓归一提交（357 文件，纯行尾） |
| B | 仅加 .gitattributes，不做归一与门禁 | 改动最小 | 存量噪音仍在，无门禁防回退 |
| C | 约定"Windows 平台维护"（只在一侧维护） | 无需归一 | 与 WSL 集成方向（P22）矛盾，限制双平台协作 |

## 4. Recommendation

**Option A**，分四批落地：

- **批 1（本提案登记）**：`docs/governance` 或 OPERATIONS 增补"跨平台维护约定"章节（L1-L5 全文）。
- **批 2（git 归一化）**：新增 `.gitattributes`（`* text=auto` + 脚本类 `eol=lf` + bat/ps1 `eol=crlf`），全仓文本文件 CRLF→LF 归一提交。
- **批 3（命令层修复）**：`.githooks/pre-commit` 的 `python` → `python3`。
- **批 4（门禁化）**：`tools/repo-lint.py` 新增行尾规则（文本文件禁混排，WARN 级）；check.py 已串联 repo-lint，无需改动。

## 5. Proposed Changes

**L1 存储层 — git 归一化（根治行尾噪音）**

```gitattributes
# .gitattributes（入库）
* text=auto
*.sh  text eol=lf
*.py  text eol=lf
*.md  text eol=lf
*.yaml text eol=lf
*.yml text eol=lf
*.json text eol=lf
*.bat text eol=crlf
*.ps1 text eol=crlf
```

约定：**仓库统一 LF 为唯一入库规范**；`text=auto` 使 Windows checkout 自动转 CRLF、WSL 保持 LF——工作区行尾随平台自适应，入库永远 LF，杜绝"行尾噪音提交"。

**L2 环境层 — 平台身份显式化**

- `config/environments/local.yaml`（Windows）、`wsl.yaml`（WSL）双份维持，机器级配置不入库（已 gitignore），模板入库。
- 默认环境按运行平台自动选择（P22 阶段二 Open Item 2），显式 `--environment` 优先。
- 跨平台路径以环境文件为唯一来源；代码内不再新增平台判断（`_linux_path`/`_repo_path` 为过渡兼容层，`env-init` 落地后收敛）。

**L3 命令层 — 可执行文件解析规则**

- WSL 侧 PATH 收敛后，`python3`/`aic`/`opencode`/`pi` 必须命中原生版（P22 已落地）。
- **hook/脚本一律用 `python3`，禁止裸 `python`**（shim 陷阱）。
- 新增脚本必须使用平台无关入口（`aic`）或显式平台探测。

**L4 文件系统层 — 操作纪律**

- 代码操作统一从 WSL 侧进行（P22 §8）：同一文件禁止两平台交替编辑。
- Windows 专属产物（`.bat`/`.ps1`/IDEA 配置）在 Windows 侧维护，行尾遵守 L1 声明。
- `/mnt/d` 为唯一挂载映射，路径以 `wsl.yaml` 为准。

**L5 验证层 — 门禁化**

- `tools/repo-lint.py` 新增行尾规则：**文本文件不允许混排 CRLF/LF**（WARN 级，heuristic）。
- pre-commit hook 改 `python3` 后恢复真实门禁效力。
- 归一完成基准：`git status --short` 中纯行尾 M 条目归零（本次 357 → 0）。

## 6. Validation Plan

- 批 2：`git add --renormalize .` 后 `git diff --cached --stat` 应仅剩真实内容变更；行尾统计 CRLF 归零（bat/ps1 除外）。
- 批 3：`bash .githooks/pre-commit` 实跑，确认输出含真实 lint 摘要（非 shim 报错）。
- 批 4：`python3 tools/repo-lint.py --repo-root .` 显示行尾规则 0 违规；故意构造 CRLF 文件验证 WARN 触发。
- 全量：`python3 tools/check.py` PASS；`python3 tools/proposal-audit.py` 0 gate errors。

## 7. Risks

- **全仓归一提交噪音大**：一次性 357 文件行尾变更，review 时用 `git diff -w` 可忽略行尾；此后不再产生。
- **`text=auto` 依赖 git 版本**：需 git ≥ 2.10（当前环境满足）；老 clone 未触发 renormalize 时需手动 `git add --renormalize`。
- **bat/ps1 当前仓库为 0**：`eol=crlf` 为防御性声明，未来新增时生效。
- **Windows 工具链**（IDEA/VS Code）若以 CRLF 保存：`text=auto` 会在入库时归一为 LF，工作区显示 CRLF，无冲突。

---

## Review Log

| Reviewer | Decision | Date |
|---|---|---|
| User (AI Maintainer operator) | **Approved** | 2026-08-14 |

---

## Implementation Record (2026-08-14)

四批全部落地（见下）：

1. **批 1**：本提案登记跨平台维护约定（§5 L1-L5）。
2. **批 2**：`.gitattributes` 已入库；全仓文本文件 CRLF→LF 归一（357 → 0 噪音 M）。
3. **批 3**：`.githooks/pre-commit` 的 `python` → `python3`（2 处调用）。
4. **批 4**：`tools/repo-lint.py` 新增 `check_line_endings` 规则（WARN 级，文本文件禁混排）。

**Validation**：
- `git add --renormalize .` 后纯行尾 M 归零 ✅
- `bash .githooks/pre-commit` 实跑输出真实 lint 摘要（无 shim 报错）✅
- `python3 tools/repo-lint.py --repo-root .`：行尾规则 0 违规 ✅
- 构造 CRLF 测试文件验证 WARN 触发 ✅
- `python3 tools/check.py` PASS ✅

**Deviations**: 无。
**Open Items**:
1. P22 阶段二 `env-init` 落地后，收敛 `_linux_path`/`_repo_path` 过渡层。
2. 其他仓库（extensions/、projects/）如需跨平台维护，复制 L1-L5 约定。
