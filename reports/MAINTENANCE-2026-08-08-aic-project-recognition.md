# Maintenance — aic 项目识别与状态记录修复(2026-08-08 晚)

- 日期 / Date: 2026-08-08(晚间)
- 模式 / Mode: on-demand(用户报告问题驱动)
- 范围 / Scope: aic CLI 项目识别、状态记录、workspace 映射、门禁流程
- 关联 / Related: P16-STATE-WRITE-GUARD(前置根因)、ADR-0008(架构决策)

---

## 1. 问题 1:aic 无法识别 workspaces 下项目

**现象**: `aic` 项目列表只显示 "system (no project)",workspaces 下的 4 个项目全消失。

**根因**: P16 实现的 `_project_exists` 守卫被错误应用于 `_select_project` 项目列表——
要求项目在 `projects/` 下必须有同名业务仓库,但 workspace 项目
(opencode-test 等)无对应仓库,全部被过滤。

**修复**: `_select_project` 去掉 `_project_exists` 过滤,恢复显示全部
workspace 项目(workspace 目录存在即可)。P16 守卫仅保留用于 `_save_state`。
(提交 d5bf78d)

## 2. 问题 2:项目状态无法记录

**现象**: 用户报告项目状态无法正确记录(last_project/last_workflow 写不进去)。

**根因**: `_save_state` 仍用 `_project_exists` 守卫——workspace 项目无业务仓库
→ 状态写入被跳过 → 状态记忆失效(与修复后的项目列表矛盾:项目可选但记不住)。

**修复**: `_save_state` 改为仅校验 workspace 目录存在(与项目列表语义一致);
`_project_exists`(仓库级校验)仅用于仓库级操作。更新 P16 测试断言。
(提交 d5bf78d,测试 52→52)

## 3. 架构决策:项目-仓库逻辑映射(ADR-0008)

**背景**: 用户询问是否将 projects/ 迁移到 workspaces/(软链接方式)便于维护。

**决策**: 不迁移、不软链。`workspaces/<id>/workspace.yaml` 的 `repository`
段记录 service → repo path/branch/remote 逻辑映射(复用 pywechat-live-2608
已有格式)。wizard 项目列表显示映射服务名。

**落地**:
- `providers.project_repos()` / `repo_path_for()` 读取映射
- wizard `_select_project` 显示 `pywechat-live-2608 — knowledge-api, training-manage-api`
- 补全 3 个项目(open-code-test/openspec-test/pi-agent-develop)的 workspace.yaml
- ADR-0008 登记(判定标准 + 初始化流程,执行者=AI)

## 4. 语言规范修正

- ADR-0008 初稿 179 处中文 → 重写英文(LANGUAGE_CONVENTION: Governance 层含 ADR 须英文)
- 语言检查盲区登记:repo-lint Rule 3 原不覆盖 rfc/(MAINTENANCE language-lint-debt #9)

## 5. 门禁流程完善

| 缺口 | 修复 |
|---|---|
| Rule 3 只查 governance/ | 扩展覆盖 rfc/(ADR/RFC 中文自动 warning) |
| LANGUAGE_CONVENTION 无 ADR 行 | 新增 RFC/ADR 行(English is less ambiguous) |
| 无提交前强制门禁 | 新增 `.githooks/pre-commit`(跑 repo-lint + check.py,FAIL 即拦截) |

## 6. 提交记录

```
d5bf78d 项目列表误过滤修复 + 状态记录修复
084a6d4 ADR-0008 架构决策(映射实现)
56a932f ADR-0008 补充(判定标准+初始化流程,中文稿)
cf38555 ADR-0008 重写英文
31eba02 语言盲区登记
8e4027b 门禁完善(Rule 3 扩展 + hook)
```

## 7. 遗留

- workspace.yaml 初始化尚未自动化(新项目需手动创建,可后续接入 wizard)
- 语言违规仍为 WARN 级(人工审),未升级为强制(存量豁免设计)
