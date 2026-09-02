# Spotless 格式门禁建议（业务仓侧，待业务评审）

> 类型：业务仓改进建议（非 ai-system 变更提案，不进 PROPOSALS.md）
> 日期：2026-09-02
> 关联：env-google-java-format-20260902（卸载 gjf/停用 pi-lens 决策）；A 层 format-check.py 已交付（ai-system）；本文档为 B 层（机械强校验）设计

---

## 1. 背景与决策链

- 2026-09-02 环境治理决策：google-java-format 固定 GOOGLE/AOSP 两档风格，与项目 Java 4 空格约定不可调和 → 卸载 + 停用 pi-lens Java 自动格式化 → 格式化改 develop 工作流校验。
- 补充（本建议）：人工/脚本自检（A 层 `ai-system/tools/format-check.py`）为软约束；格式的**最终机械闸门**建议由 **Spotless** 补位（可配置、不重蹈 gjf 覆辙）。

## 2. 方案对比

| 方案 | 可配置性 | 强校验 | 依赖 | 结论 |
|---|---|---|---|---|
| **Spotless + eclipse formatter**（推荐） | ✅ 完全可配（xml：indent=4 与 IDEA/存量一致） | ✅ `mvn spotless:check` 做 CI/发布闸门 | JDK+Maven（CI 正常；本机 Windows JDK8 可跑） | 采纳建议 |
| google-java-format | ❌ 固定两档（与项目 4 空格冲突，已证伪卸载） | — | — | 否决（历史） |
| 仅 A 层脚本 | ✅ 检查规范泄漏 | ❌ 软约束 | python3 | 保留为提交前快检，不足以为最终闸门 |

## 3. 配置草稿

### 3.1 pom.xml（每服务仓：platform-api / user-center-api / bs-integration / cmdb-api）

```xml
<plugin>
  <groupId>com.diffplug.spotless</groupId>
  <artifactId>spotless-maven-plugin</artifactId>
  <version>2.43.0</version>
  <configuration>
    <java>
      <eclipse>
        <!-- eclipse formatter 完全可配置：indent=4 与 IDEA 默认/存量一致 -->
        <file>${project.basedir}/eclipse-format.xml</file>
      </eclipse>
      <removeUnusedImports/>
      <endWithNewline/>
    </java>
  </configuration>
  <executions>
    <execution>
      <goals>
        <goal>check</goal>   <!-- 绑定生命周期：构建/CI 即校验 -->
      </goals>
    </execution>
  </executions>
</plugin>
```

### 3.2 eclipse-format.xml（关键项）

```xml
<?xml version="1.0" encoding="UTF-8"?>
<profiles version="13">
  <profile kind="CodeFormatterProfile" name="Cool4Space" version="13">
    <setting id="org.eclipse.jdt.core.formatter.tabulation.char" value="space"/>
    <setting id="org.eclipse.jdt.core.formatter.tabulation.size" value="4"/>
    <setting id="org.eclipse.jdt.core.formatter.indentation.size" value="4"/>
    <!-- 其余条目由 IDE 导出"当前项目风格"补充（一次性生成） -->
  </profile>
</profiles>
```

> 生成方式：IDEA → Settings → Editor → Code Style → Java → Scheme Export 为 Eclipse XML Profile，
> 再核对 tabulation.size=4 后入库；避免手写全部条目。

## 4. 迁移步骤（一次性）

1. 每仓加 spotless 插件 + eclipse-format.xml（含实时风格导出）
2. `mvn spotless:apply` 全仓格式化 → 生成一次性「format baseline」提交（单独 commit，附格式化说明）
3. `mvn spotless:check` 本机验证 0 差异
4. CI 流水线加入 `mvn spotless:check` 步骤（Linux 环境）
5. 开发约定：IDEA 已按 4 空格格式化，日常开发无感知；历史命令机器校验兜底
6. 发布闸门：release 阶段 check 前置（复用现有验证链）

## 5. 验证计划

- `mvn spotless:check` → BUILD SUCCESS（0 差异）为完成标准
- 改造后对新 change 跑 A 层 format-check 仍 PASS（两层互补不互斥）
- 回归：既有测试全绿（格式化不改变语义）

## 6. 风险与缓解

| 风险 | 缓解 |
|---|---|
| 全仓 apply 产生超大 diff（一次性） | 独立 baseline 提交 + 与业务提交隔离；IDE 导出格式先本地试点 1 仓（建议 user-center-api） |
| eclipse formatter 与 IDEA 存在细节差异（换行/注解换行） | 生成后 diff 人工审查一次；差异条目在该仓 eclipse-format.xml 调整 |
| spotless 版本/插件拉取依赖外网 | 已有 Maven 镜像（.m2/settings.xml）惯例，插件走同源 |
| 团队未约定 → check 误红 | 文档登记 + CI 步骤随发布链评审；回滚 = 移除 executions 段 |

## 7. 结论

业务侧评审通过后，建议以 **user-center-api 为试点仓**（1 周内无回归再铺 4 仓）。评审期间 A 层 format-check 持续兜底（已接入 develop gate）。

## 8. 登记

- 本建议入 `reports/README.md`（评估与评审报告表，类型=Business-side recommendation / Pending）
- 不立 P 提案（非 ai-system 变更）；若业务侧确认进入实施，由业务链（dev-setup 或各仓 CI 任务）承接