---
id: topic-compound-engineering
title: Compound Engineering 复利工程
type: topic
created_at: 2026-04-10
updated_at: 2026-04-10
related:
  - "concept-compound-engineering"
  - "concept-knowledge-compound"
  - "concept-output-as-reproduction"
  - "concept-incremental-processing"
  - "concept-inspection-over-repair"
  - "topic-llm-knowledge-system"
sources:
  - 2026-04-10-samuel-compound-knowledge-system-001
---

## Thesis

Compound Engineering 是一种通用方法论——不只适用于知识库，也适用于内容生产、研究、运营、支持等一切重复型知识工作。它的核心是让每次任务的经验沉淀成系统资产，使第 N 次任务自动携带前 N-1 次的判断沉淀。

## Main Structure

### 1. 核心循环：Plan → Work → Review → Compound

复利工程的关键不在任务做得更快，而在每次做完之后，都把判断回写成下一次默认可用的系统能力。

| 步骤 | 名称 | 人类/AI 分工 |
|:---:|------|-------------|
| ① | **Plan** | 人类+AI：先看旧材料、旧规则、旧案例，带着历史上下文开工 |
| ② | **Work** | AI 为主：生成初稿、分析、回复，把执行成本压低 |
| ③ | **Review** | 人类为主：判断哪些错误会重复、哪些标准值得固化 |
| ④ | **Compound** | 人类+AI：把教训回写进模板、清单、术语表 |

### 2. 四类系统资产

真正被复用的不是答案本身，而是这些系统资产：

| 资产 | 定义 | 示例 |
|------|------|------|
| **Standards** | 什么算合格，口径如何统一 | 品牌语气、禁用表达、验收标准 |
| **Memory** | 历史案例、反例、已踩的坑 | 术语表、失败样例 |
| **Routing** | 什么情况自动过，什么升级 | 问题分层、升级条件 |
| **Evaluation** | 用什么检查系统有没有更准 | 证据标准、引用规范 |

> 答案会过期，但判断依据、失败样例、升级条件和验收口径会持续复用。

### 3. Linear vs Compound 的本质差异

| 维度 | 线性模式 | 复利模式 |
|------|---------|---------|
| 性能 | 第 20 次仍像第 1 次 | 第 20 次调用前 19 次积累 |
| 知识位置 | 主要在人脑子里 | 主要在系统文档和规则里 |
| 错误处理 | 一次次补救 | 尽量变成永久预防 |
| 工作流 | 写完就发，答完就算 | 每次任务都回写系统 |

### 4. 高杠杆点

在 agent 速度足够快之后，瓶颈不再是"做"，而是"做什么"与"学到了什么"。高价值工作量会向 **Plan + Review** 偏移，因为那里决定系统是否会越来越准。

### 5. 适用领域

| 领域 | 具体应用 |
|------|---------|
| 内容 | 品牌语气、禁用表达、标题结构、内链规则 |
| 研究 | 证据标准、摘要格式、判断框架、引用规范 |
| 运营 | 异常处理、阈值判断、周报格式、交接规则 |
| 支持 | 问题分层、回复模板、升级条件、风险用语 |

## Tensions

- **即时产出 vs 系统沉淀**：短期内直接让 AI 生成结果更快，但长期看不沉淀经验会越来越累
- **标准化 vs 灵活性**：系统资产需要稳定的标准，但不同场景可能需要不同的处理方式
- **人工审查 vs 自动化**：Review 步骤需要人类判断，但随着系统成熟，越来越多判断可以固化

## Related

- concept-compound-engineering — 核心概念定义
- concept-knowledge-compound — 知识复利效应
- concept-output-as-reproduction — 输出即再生产
- topic-llm-knowledge-system — 复利工程在知识系统中的具体实践
- 2026-04-10-samuel-compound-knowledge-system-001 — 来源文档
