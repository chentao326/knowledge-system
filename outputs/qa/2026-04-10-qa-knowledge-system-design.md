---
id: 2026-04-10-qa-knowledge-system-design
title: Samuel 四步流程 vs Karpathy 三层架构对比分析
type: qa
created_at: 2026-04-10
updated_at: 2026-04-10
question: "Samuel 的四步流程和 Karpathy 的三层架构有什么异同？搭建个人知识系统时应该如何取舍？"
sources:
  - "2026-04-10-samuel-compound-knowledge-system-001"
  - "2026-04-10-karpathy-llm-knowledge-base-002"
  - "topic-llm-knowledge-system"
  - "topic-compound-engineering"
---

## 问题

Samuel 的四步流程和 Karpathy 的三层架构有什么异同？搭建个人知识系统时应该如何取舍？

---

## 已知结论

### 1. 核心相似点

两者本质上是**同一套理念的不同表达**：

| 维度 | 共识 |
|------|------|
| **核心理念** | LLM 是知识库的主要维护者，人类几乎不手动编辑 |
| **文件格式** | 全部使用 Markdown，文件优先于应用 |
| **摄取层** | 外部输入先统一存入 raw/ 目录 |
| **增量处理** | 不全量重建，只处理新增内容 |
| **输出回写** | 查询和输出结果应归档回知识库，形成复利 |
| **前端工具** | 都推荐 Obsidian 作为浏览前端 |
| **RAG 态度** | 在中小规模（~40 万词以内）不需要复杂 RAG |

### 2. 关键差异

| 维度 | Samuel（方法论） | Karpathy（实践） |
|------|----------------|-----------------|
| **定位** | 系统化的方法论框架 | 经过验证的个人实践 |
| **流程粒度** | 四步（摄取→消化→输出→巡检） | 三层（raw/ → wiki/ → outputs/） |
| **消化产物** | 四类（摘要、概念卡、主题页、索引） | 三类（摘要、概念+文章、索引+回链） |
| **巡检** | 有完整的巡检框架（检查项+提示词+schema） | 简单的"健康检查"（linting） |
| **提示词工程** | 每步都有详细提示词模板 | 未提供提示词 |
| **Schema 规范** | 每种产物都有标准化 schema | 未定义 schema |
| **笔记方法** | 推荐 PARA/MOC/Zettelkasten | 未明确使用特定笔记方法 |
| **输出形式** | 多 Skills 可组合（6 种输出类型） | Markdown / Marp 幻灯片 / matplotlib |
| **摄取方式** | AI 驱动的标准化摄取 | Obsidian Web Clipper 手动摄取 |
| **未来方向** | 未深入讨论 | 合成数据 + 微调 |

### 3. 互补关系

- **Karpathy 验证了 Samuel 的理论**：~100 篇文章 ~40 万词的实战证明四步流程可行
- **Samuel 补充了 Karpathy 缺失的方法论**：提示词、schema、巡检框架、笔记方法选型
- **Samuel 的"消化"步骤比 Karpathy 的"编译"更精细**：区分了摘要、概念、主题、索引四类产物

---

## 推断

### 搭建建议：取两者之长

1. **采用 Samuel 的四步流程作为操作框架**——它更完整、更有条理，每步都有明确的提示词和 schema
2. **借鉴 Karpathy 的实战经验**——在摄取阶段初期可以用 Obsidian Web Clipper 手动操作，逐步过渡到 AI 自动摄取
3. **用 Zettelkasten 组织知识层**——原子化笔记与 Samuel 的"编译而非总结"理念高度契合
4. **保留 Karpathy 的输出回写习惯**——每次查询和输出都归档回知识库
5. **引入 Samuel 的巡检机制**——这是 Karpathy 实践中相对薄弱的环节

### 不建议做的事

- 不建议一上来就追求完全自动化摄取（Karpathy 也是手动开始的）
- 不建议过早上 RAG（两人都认为中小规模不需要）
- 不建议忽略巡检（这是系统长期可信的关键）

---

## 待确认问题

- 在什么规模下应该考虑引入 RAG？（Karpathy 提到 ~40 万词仍不需要）
- 合成数据 + 微调在什么规模下值得投入？
- 如何衡量知识系统的"健康度"？

---

## 来源

- 2026-04-10-samuel-compound-knowledge-system-001 — Samuel「用 AI 搭一套会复利的知识系统」
- 2026-04-10-karpathy-llm-knowledge-base-002 — Karpathy「LLM Knowledge Bases」
- topic-llm-knowledge-system — LLM 知识系统设计主题页
- topic-compound-engineering — Compound Engineering 主题页
