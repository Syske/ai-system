# Maintenance Report — 2026-08-06 live-facade SNAPSHOT 依赖风险

**Mode**: on-demand
**Scope**: knowledge-api 依赖 live-facade 1.2.6-SNAPSHOT 的不可重复构建风险
**Date**: 2026-08-06
**Trigger**: 排查 "BizLiveInfo 未持久化 micNum/subscribeCount" 时发现字段齐全,但 SNAPSHOT 依赖存在真实风险

---

## 1. 核查结论 / Findings

**问题"BizLiveInfo 未持久化 micNum/subscribeCount"不成立**,字段链路完整:

| 层 | 字段 | 证据 |
|---|---|---|
| `BizLiveInfo`(live-dao) | micNum / subscribeCount | ✅ 存在(311/317 行) |
| `LiveInfoBO`(live-biz) | micNum / subscribeCount | ✅ 存在(217/222 行) |
| `LiveInfoResponse`(live-facade 1.2.6-SNAPSHOT jar) | micNum / subscribeCount | ✅ javap 证实(20260720 构建) |
| knowledge 消费链 | `BeanUtil.transform` 自动映射 | ✅ `LiveCourseResponseVO` 同名字段 + 测试断言 5/200 通过 |

## 2. 真实风险 / Real Risk

**SNAPSHOT 不可重复构建**:

- knowledge-api `pom.xml:47` 声明 `live-facade.version = 1.2.6-SNAPSHOT`
- 本地解析到 `live-facade-1.2.6-20260720.112049-11.jar`(时间戳构建,含 micNum)
- live-api 分支 `cc20260701_wecom_live_live-api` **仍活跃**(今日新增 7 commit,含 live-facade 相关改动)
- 风险链:
  1. live-api 重建 live-facade → nexus 发布新 SNAPSHOT 时间戳版本
  2. knowledge 下次构建拉取最新 SNAPSHOT → 字段行为可能变化
  3. 若 live-facade 源码回退(移除字段)→ knowledge 编译失败或运行时字段 null

## 3. 建议 / Proposal

1. **短期**:live-api 分支合并后发布正式版本(RELEASE),knowledge 切换 `live-facade.version` 到 RELEASE,消除 SNAPSHOT 漂移
2. **中期**:跨服务接口(如 live-facade)建立版本发布纪律——SNAPSHOT 仅用于同迭代联调,联调完成后立即发 RELEASE
3. **记录**:live-api 今日 7 个 commit 中涉及 live-facade 的改动,合并时需重新构建并验证 knowledge 兼容

**决策(2026-08-06)**:问题 1 将在**发灰度时统一修改为 RELEASE 版本**,不在当前迭代单独处理。

## 4. 状态 / Status

- [x] 决策:发灰度时统一改为 RELEASE 版本(2026-08-06 确认,不在当前迭代处理)
- [x] 跨服务 SNAPSHOT 治理纪律 —— **defer**（2026-08-06 巡检评估：短期已闭环，治理增补走变更流程，下月重新评估；见 MAINTENANCE-2026-08-06.md §4）
