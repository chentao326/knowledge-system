---
id: concept-query-loop
title: Query Loop
type: concept
created_at: 2026-04-10
updated_at: 2026-04-10
aliases:
  - 查询循环
related:
  - "concept-knowledge-compound"
  - "concept-llm-knowledge-compiler"
sources:
  - 2026-04-10-karpathy-llm-knowledge-base-002
---

# Definition

Wiki 长到一定规模后，查询本身也在不断积累资产。模型先读索引和摘要，再追相关文章，把复杂问答写回知识库，形成自我增强的查询循环。

# Why It Matters

这是知识复利在查询环节的具体体现——每次提问不只是消费知识，还在生产新知识。

# Where It Appears

Karpathy 推文 Q&A 和 Output 部分。

# Notes

Karpathy 经常将输出"归档"回 wiki 以增强后续查询。
