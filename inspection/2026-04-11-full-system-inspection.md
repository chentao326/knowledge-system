---
id: inspection-2026-04-11-full-system
title: "知识系统全面巡检报告"
type: inspection
created_at: 2026-04-11
scope:
  - "knowledge/literature/"
  - "knowledge/permanent/concepts/"
  - "knowledge/permanent/topics/"
  - "knowledge/index/"
  - "raw/2026/04/"
---

## Summary

知识系统共 34 个知识条目，发现 22 个问题：其中断链 11 处（最严重）、frontmatter 不一致 8 处、MOC 覆盖缺失 2 处、孤岛文件 2 处。无定义冲突、无重复概念、无未注册文件、无命名规范违规。

## Findings

### High Priority

1. **topic-effective-decision.md 存在 4 处断链**
   - 证据：Related 部分使用了中文链接名 `[[选择ROI]]`、`[[机会成本]]`、`[[稀缺资源]]`、`[[时间窗口]]`，而非对应的概念卡 id
   - 建议动作：分别改为 `[[concept-choice-roi]]`、`[[concept-opportunity-cost]]`、`[[concept-scarce-resource]]`、`[[concept-time-window]]`

2. **xiaozheng-effective-choice-summary.md 存在 6 处断链**
   - 证据：Related 部分使用了 `[[选择ROI]]`、`[[机会成本]]`、`[[稀缺资源]]`、`[[时间窗口]]`、`[[有效决策]]`，以及格式错误的 `[[来源: 2026-04-11-xiaozheng-tool3-effective-choice-005]]`
   - 建议动作：分别改为 `[[concept-choice-roi]]`、`[[concept-opportunity-cost]]`、`[[concept-scarce-resource]]`、`[[concept-time-window]]`、`[[topic-effective-decision]]`、`[[2026-04-11-xiaozheng-tool3-effective-choice-005]]`

3. **断链导致 4 个概念卡成为事实孤岛**
   - 证据：concept-choice-roi、concept-opportunity-cost、concept-scarce-resource、concept-time-window 仅被 topic-effective-decision.md 的 frontmatter related 引用，但该文件的正文 Related 链接全部断链，导致这些概念卡在知识网络中实际不可达
   - 建议动作：修复上述断链后，孤岛问题自动解决

### Medium Priority

4. **摘要文件 frontmatter 的 topics/concepts 字段格式不统一**
   - 证据：karpathy/samuel 摘要使用纯文本格式（如 `topics: llm-knowledge-system`），而三篇小挣青年摘要使用 wiki-link 格式（如 `topics: "[[topic-earning-methodology]]"`）
   - 建议动作：统一为纯文本 id 格式

5. **xiaozheng-effective-choice-summary.md 的 concepts 字段包含无对应概念卡的条目**
   - 证据：concepts 列表中包含 `"盈亏平衡点"` 和 `"LTV/CAC"`，这两个只是工具/指标，并非独立概念卡
   - 建议动作：从 concepts 字段中移除，或在 Notes 中以文字说明

6. **概念卡正文标题层级不统一**
   - 证据：2026-04-10 的 10 个概念卡使用 `# Definition`（一级标题），2026-04-11 的 12 个概念卡使用 `## Definition`（二级标题）
   - 建议动作：统一为 `##`（二级标题），因为一级标题应留给文件标题

7. **概念卡 title 字段格式不统一**
   - 证据：2026-04-10 的概念卡 title 使用英文无引号（如 `title: Compound Engineering`），2026-04-11 的使用中文带引号（如 `title: "能力圈"`）
   - 建议动作：统一为中文带引号格式，与系统规则"中文内容为主，专有名词保留英文原文"保持一致

8. **MOC 未覆盖新增的两个主题**
   - 证据：moc-knowledge-system.md 未包含 topic-earning-methodology（赚钱方法论）和 topic-effective-decision（有效决策）
   - 建议动作：在 MOC 中新增"赚钱方法论"和"有效决策"两个分区

### Low Priority

9. **index.md 和 moc-knowledge-system.md 缺少 frontmatter**
   - 证据：这两个文件没有 id、type 等 frontmatter 字段
   - 建议动作：可选添加，作为导航文件不影响功能

10. **topic-earning-methodology 和 topic-effective-decision 缺少交叉引用**
    - 证据：两个主题页的 related 列表中未互相引用，且其他主题页也未引用它们
    - 建议动作：在相关主题页的 related 中补充交叉引用，增强知识网络连通性

## Statistics

- 概念总数：22
- 主题页总数：5
- 摘要总数：5
- 原始材料总数：5
- 发现问题数：22（High: 3, Medium: 5, Low: 2，其中断链 11 处、frontmatter 不一致 8 处、MOC 缺失 2 处、孤岛 2 处）
- 定义冲突：0
- 重复概念：0
- 未注册文件：0
- 命名规范违规：0

## Suggested Fixes

1. **[P0] 修复 topic-effective-decision.md 的 4 处断链**：将中文链接名改为概念卡 id
2. **[P0] 修复 xiaozheng-effective-choice-summary.md 的 6 处断链**：同上 + 修复来源链接格式
3. **[P1] 统一摘要文件 frontmatter 的 topics/concepts 字段格式**：全部使用纯文本 id
4. **[P1] 清理 xiaozheng-effective-choice-summary.md 中无对应概念卡的 concepts 条目**
5. **[P1] 统一概念卡正文标题层级为 `##`**
6. **[P1] 统一概念卡 title 字段为中文带引号格式**
7. **[P2] 更新 MOC，添加赚钱方法论和有效决策两个主题的覆盖**
8. **[P2] 在相关主题页之间补充交叉引用**
