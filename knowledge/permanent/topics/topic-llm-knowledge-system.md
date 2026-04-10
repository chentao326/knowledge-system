---
id: topic-llm-knowledge-system
title: LLM 知识系统设计
type: topic
created_at: 2026-04-10
updated_at: 2026-04-10
related:
  - "[[concept-llm-knowledge-compiler]]"
  - "[[concept-file-over-app]]"
  - "[[concept-incremental-processing]]"
  - "[[concept-zettelkasten]]"
  - "[[concept-query-loop]]"
  - "[[concept-inspection-over-repair]]"
  - "[[topic-compound-engineering]]"
sources:
  - 2026-04-10-samuel-compound-knowledge-system-001
  - 2026-04-10-karpathy-llm-knowledge-base-002
---

## Thesis

用 LLM 搭建个人知识系统的核心是让 AI 成为知识维护者而非一次性工具，通过 raw → knowledge → outputs 的流水线实现知识复利。Samuel 提供了系统化的四步方法论（摄取→消化→输出→巡检），Karpathy 提供了经过实战验证的架构模式（raw/ → wiki/ → outputs/），两者高度互补。

## Main Structure

### 1. 系统架构：三层目录 + 规则文件

```
知识系统/
├── raw/           # 原始材料池（摄取层）
├── knowledge/     # 知识层（消化层）
├── outputs/       # 输出层
├── inspection/    # 巡检报告
├── AGENTS.md      # 系统规则
├── prompts/       # 提示词模板
└── schemas/       # Schema 模板
```

**核心理念**：你不直接写 wiki，LLM 才是知识库的主要维护者。Obsidian 更像前台：看 raw、看 wiki、看输出，而不是手工逐页整理。

### 2. 四步流程

| 步骤 | 目标 | 关键原则 | 产物 |
|------|------|---------|------|
| **摄取** | 把异构输入统一为 Markdown | 保留原文、不做深度加工 | `raw/` |
| **消化** | 编译为可复用知识结构 | 增量处理、结论带来源 | `knowledge/` |
| **输出** | 基于知识系统生成内容 | 先检索再综合、落文件 | `outputs/` |
| **巡检** | 定期审计系统健康度 | 只出报告不自动修复 | `inspection/` |

### 3. Samuel vs Karpathy 对照

| 维度 | Samuel 的方法论 | Karpathy 的实践 |
|------|----------------|----------------|
| 摄取 | AI 驱动的标准化摄取 + 提示词 | Obsidian Web Clipper + 手动 |
| 消化 | 四步产物：摘要→概念→主题→索引 | LLM 增量编译 wiki |
| 输出 | 多 Skills 可组合 | Markdown / Marp / matplotlib |
| 巡检 | 结构化审计框架 | LLM 健康检查 |
| RAG 态度 | 规模不大时不要早上 RAG | ~40 万词不需要复杂 RAG |
| 前端 | Obsidian | Obsidian |
| 知识层命名 | `knowledge/` | `wiki/` |

### 4. 笔记方法选型

本系统采用 **Zettelkasten** 作为知识层结构：

| 目录 | 用途 |
|------|------|
| `fleeting/` | 临时想法 |
| `literature/` | 阅读笔记与摘要 |
| `permanent/concepts/` | 概念卡（原子化） |
| `permanent/topics/` | 主题页（综合深度） |
| `index/` | 索引、MOC 导航页 |

### 5. 最小闭环与扩展路径

**最小闭环**：
1. 摄取一篇文章和一条推文 → `raw/`
2. 对 raw 执行一次消化 → `knowledge/`
3. 回答一个具体问题 → `outputs/qa/`
4. 做一次巡检 → `inspection/`

**扩展方向**：
- 添加更多输出 Skills（article / infographic / PDF / PPT / memo / social）
- 引入自动化工具（Search CLI / Health Check）
- 规模增大后考虑合成数据 + 微调

## Tensions

- **Karpathy 的 wiki/ vs Samuel 的 knowledge/**：两者本质相同，都是"消化后的结构化知识层"。本系统采用 `knowledge/` 命名以与 `raw/` 形成更明确的语义对比
- **标准化 vs 场景化**：摄取和消化需要高度标准化，但输出天然是场景化的——不应强行统一输出 schema
- **手动 vs 自动**：Karpathy 用 Obsidian Web Clipper 手动摄取，Samuel 建议用 AI 自动摄取。初期手动更可控，后期可逐步自动化

## Related

- [[concept-llm-knowledge-compiler]] — LLM 作为知识编译器
- [[concept-file-over-app]] — 文件优先原则
- [[concept-zettelkasten]] — Zettelkasten 笔记法
- [[concept-query-loop]] — 查询循环
- [[topic-compound-engineering]] — 复利工程方法论
- [[2026-04-10-samuel-compound-knowledge-system-001]] — Samuel 来源
- [[2026-04-10-karpathy-llm-knowledge-base-002]] — Karpathy 来源
