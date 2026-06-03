---
id: concept-llm-knowledge-compiler
title: LLM Knowledge Compiler
type: concept
created_at: 2026-04-10
updated_at: 2026-04-10
aliases:
  - LLM 知识编译器
related:
  - "concept-file-over-app"
  - "concept-incremental-processing"
  - "concept-query-loop"
sources:
  - 2026-04-10-karpathy-llm-knowledge-base-002
---

# Definition

LLM 作为知识编译器而非一次性工具——它负责将原始材料（raw/）编译为结构化知识库（wiki/），包括生成摘要、创建回链、分类概念、编写文章。

# Why It Matters

改变了人在知识管理中的角色——从"手动整理者"变为"策展人和消费者"，LLM 承担了大部分维护工作。

# Where It Appears

Karpathy 推文核心架构，"Important to note that the LLM writes and maintains all of the data of the wiki, I rarely touch it directly"。

# Notes

Karpathy 发现在 ~40 万词规模下 LLM 不需要 RAG 就能很好地维护知识库。
