---
id: summary-2026-04-10-karpathy-llm-knowledge-base
source_id: 2026-04-10-karpathy-llm-knowledge-base-002
title: 用 LLM 构建个人知识库 摘要
created_at: 2026-04-10
updated_at: 2026-04-10
type: summary
topics:
  - llm-knowledge-system
  - personal-wiki
  - obsidian-workflow
concepts:
  - llm-knowledge-compiler
  - file-over-app
  - query-loop
  - incremental-processing
---

# Core Idea

用 LLM 作为知识编译器维护个人 wiki，通过 raw/ → wiki/ → outputs/ 三层架构实现知识复利，Obsidian 做前端浏览，人类几乎不手动编辑 wiki。

# Key Points

1. **Token 消耗从"操作代码"转向"操作知识"**（Markdown 和图片）
2. **LLM 增量编译 wiki**：摘要、回链、概念分类、文章编写，人类很少直接编辑
3. **40 万词规模下不需要复杂 RAG**，LLM 能自动维护索引和摘要
4. **输出可归档回 wiki 形成复利**：Markdown 文件、Marp 幻灯片、matplotlib 图表
5. **健康检查确保数据完整性**：发现不一致、补齐缺失数据、建议新文章

# Evidence

Karpathy 以 ~100 篇文章 ~40 万词的研究 wiki 为实例验证了方法的可行性。

# Open Questions

- 合成数据 + 微调在什么规模下值得投入？
- 搜索引擎的准确性如何评估？

# Related

- concept-llm-knowledge-compiler
- concept-file-over-app
- concept-query-loop
- concept-incremental-processing
- 2026-04-10-karpathy-llm-knowledge-base-002
