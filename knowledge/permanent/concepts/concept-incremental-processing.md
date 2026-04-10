---
id: concept-incremental-processing
title: Incremental Processing
type: concept
created_at: 2026-04-10
updated_at: 2026-04-10
aliases:
  - 增量处理
  - 增量编译
related:
  - "[[concept-compound-engineering]]"
  - "[[concept-file-over-app]]"
sources:
  - 2026-04-10-samuel-compound-knowledge-system-001
  - 2026-04-10-karpathy-llm-knowledge-base-002
---

# Definition

只处理新增内容，不要每次重建全库。在摄取阶段只处理新输入，在消化阶段只编译新增 raw 文件，在巡检阶段按目录分批进行。

# Why It Matters

全量重建成本高且容易引入错误，增量处理是系统可持续运行的前提。

# Where It Appears

- Samuel 文档三大原则之一
- Karpathy 推文中"incrementally compile a wiki"

# Notes

增量处理要求良好的文件命名和索引机制来追踪哪些内容已处理。
