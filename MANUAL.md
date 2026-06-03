# 知识系统操作手册

> 本手册是「可复利知识系统」的完整使用指南。无论你是第一次使用，还是日常操作，都可以在这里找到参考。

---

## 目录

1. [快速开始](#1-快速开始)
2. [系统概览](#2-系统概览)
3. [第一步：摄取](#3-第一步摄取)
4. [第二步：消化](#4-第二步消化)
5. [第三步：输出](#5-第三步输出)
6. [第四步：巡检](#6-第四步巡检)
7. [用 Obsidian 浏览知识系统](#7-用-obsidian-浏览知识系统)
8. [用 AI Agent 操作知识系统](#8-用-ai-agent-操作知识系统)
9. [日常使用流程](#9-日常使用流程)
10. [常见问题](#10-常见问题)
11. [扩展指南](#11-扩展指南)

---

## 1. 快速开始

### 1 分钟跑通最小闭环

如果你是第一次使用，按以下 4 步操作即可跑通系统：

```
① 摄取一篇资料 → 存入 raw/
② 让 AI 消化这篇资料 → 生成摘要、概念卡、主题页
③ 让 AI 回答一个问题 → 存入 outputs/qa/
④ 让 AI 做一次巡检 → 生成巡检报告
```

### 你需要准备的工具

| 工具 | 用途 | 必需？ |
|------|------|:------:|
| Obsidian | 浏览知识系统、查看双向链接 | 推荐 |
| AI Agent（Claude / ChatGPT 等） | 执行摄取、消化、输出、巡检 | 必需 |
| Obsidian Web Clipper | 快速摄取网页文章 | 推荐 |

---

## 2. 系统概览

### 2.1 目录结构

```
knowledge-system/
├── AGENTS.md              ← AI Agent 的行为规范（每次操作前先读这个）
├── README.md              ← 项目说明
├── MANUAL.md              ← 本文件（操作手册）
│
├── raw/                   ← 摄取层：原始材料池
│   └── YYYY/MM/           ← 按年月组织
│
├── knowledge/             ← 知识层（Zettelkasten 结构）
│   ├── fleeting/          ← 临时想法（未整理）
│   ├── literature/        ← 阅读笔记与摘要
│   ├── permanent/
│   │   ├── concepts/      ← 概念卡（每条一个概念）
│   │   └── topics/        ← 主题页（综合深度）
│   └── index/             ← 索引、导航页、MOC
│
├── outputs/               ← 输出层
│   ├── qa/                ← 问答归档
│   ├── article/           ← 图文长文
│   ├── memo/              ← 研究备忘录
│   └── social/            ← 海报与 thread
│
├── inspection/            ← 巡检报告
├── prompts/               ← 提示词模板（给 AI 用）
└── schemas/               ← Schema 模板（给 AI 用）
```

### 2.2 四步流程

```
摄取 (Ingest)     消化 (Digest)      输出 (Output)       巡检 (Inspect)
   │                 │                  │                  │
   ▼                 ▼                  ▼                  ▼
 外部资料 ──→  raw/ ──→  knowledge/ ──→  outputs/ ──→  inspection/
 (网页/论文/     (标准化        (摘要/概念/      (问答/文章/      (结构审计
  推文/播客)      Markdown)      主题/索引)       报告/图表)       修复建议)
```

### 2.3 核心原则

| 原则 | 含义 |
|------|------|
| **文件优先** | 所有东西落成 Markdown 文件，避免锁在单一应用里 |
| **增量更新** | 只处理新增内容，不全量重建 |
| **可追溯** | 任何结论都能追溯到原始来源 |
| **复利思维** | 每次处理都不是结束，而是下一次处理的输入 |

---

## 3. 第一步：摄取

### 3.1 这一步做什么

把外部输入（网页、推文、论文、播客、视频、对话等）统一转换为标准化的 Markdown 文件，存入 `raw/` 目录。

### 3.2 操作方式

#### 方式 A：用 AI Agent 自动摄取（推荐）

1. 把资料内容（URL 或文本）发给 AI Agent
2. 附上提示词：`请按照 prompts/ingest.md 的要求，将以下内容摄取为标准化 raw 文件`
3. AI 会按照 `schemas/raw-schema.md` 的格式输出文件
4. 将文件保存到 `raw/YYYY/MM/` 目录

#### 方式 B：用 Obsidian Web Clipper 手动摄取

1. 在浏览器中安装 Obsidian Web Clipper 扩展
2. 打开目标网页，点击 Clipper
3. 选择 "Markdown" 格式，保存到 `raw/YYYY/MM/`
4. 手动补充 frontmatter（或让 AI 补充）

#### 方式 C：手动创建

1. 复制 `schemas/raw-schema.md` 的模板
2. 填写 frontmatter 中的元信息
3. 将正文粘贴到 `## Raw Content` 部分
4. 保存到 `raw/YYYY/MM/`

### 3.3 摄取时的注意事项

| ✅ 应该做 | ❌ 不应该做 |
|----------|-----------|
| 保留原文，不做深度总结 | 不要让 AI "顺手"写观点或结论 |
| 保留来源、时间、作者等元信息 | 不要改写事实或补充外部知识 |
| 如果抓取不完整，标记为 `partial` | 不要在摄取阶段做概念抽取 |
| 专有名词保留英文原文 | 不要过早压缩信息 |

### 3.4 文件命名规则

```
raw/YYYY/MM/YYYY-MM-DD-slug-NNN.md
```

示例：
```
raw/2026/04/2026-04-10-karpathy-llm-knowledge-base-002.md
```

- 日期放前面，方便排序
- slug 用简短英文描述内容
- NNN 是当天的序号（001, 002, ...）

### 3.5 Raw 文件 Schema

```yaml
---
id: 2026-04-10-karpathy-llm-knowledge-base-002
title: "用 LLM 构建个人知识库"
source_type: x | article | pdf | podcast | note | conversation
source_url: "https://..."
author: "Andrej Karpathy"
published_at: 2026-04-10
captured_at: 2026-04-10
content_type: post | thread | article | transcript | note | pdf
status: complete | partial | shell_only
tags:
  - knowledge-system
  - llm
attachments: []
---

## Raw Content

[清洗后的正文]

## Capture Notes

- 完整性说明：完整
- 来源类型：正文
- 缺失说明：无
```

---

## 4. 第二步：消化

### 4.1 这一步做什么

把 `raw/` 中的原始材料"编译"为结构化的知识，存入 `knowledge/` 目录。这不是写摘要，而是更新一个知识系统。

### 4.2 操作方式

1. 确定要消化的 raw 文件（可以是新增的一个或多个）
2. 把 raw 文件内容发给 AI Agent
3. 附上提示词：`请按照 prompts/digest.md 的要求，对以下 raw 文件执行消化`
4. 同时附上 `knowledge/index/index.md`（让 AI 了解已有知识）
5. AI 会生成以下产物：

| 产物 | 存放位置 | 说明 |
|------|---------|------|
| **摘要** | `knowledge/literature/` | 每份 raw 对应一个摘要 |
| **概念卡** | `knowledge/permanent/concepts/` | 抽取的关键概念（原子化） |
| **主题页** | `knowledge/permanent/topics/` | 综合多个概念的深度页面 |
| **索引更新** | `knowledge/index/` | 更新总索引和 MOC |

### 4.3 消化时的注意事项

| ✅ 应该做 | ❌ 不应该做 |
|----------|-----------|
| 先读已有知识，再判断更新哪些文件 | 不要凭空生成，不参考已有内容 |
| 优先复用已有概念和主题页 | 不要每次都新建概念 |
| 所有结论带来源引用 | 不要静默覆盖旧结论 |
| 发现冲突时显式标记 | 不要偷偷覆盖冲突内容 |
| 每条笔记只表达一个概念 | 不要把多个概念混在一条笔记里 |
| 按主题组织，不按时间流水账 | 不要写成"第一天读了XX，第二天读了YY" |

### 4.4 消化产物的 Schema

#### 摘要（`knowledge/literature/`）

```yaml
---
id: summary-2026-04-10-slug
source_id: "对应的 raw 文件 id"
title: "摘要标题"
created_at: 2026-04-10
updated_at: 2026-04-10
type: summary
topics: [主题1, 主题2]
concepts: [概念1, 概念2]
---

## Core Idea
[一句话概括]

## Key Points
1. [要点]
2. [要点]

## Evidence
- [事实依据]

## Open Questions
- [待解决问题]

## Related
- 相关概念
- 来源 raw 文件
```

#### 概念卡（`knowledge/permanent/concepts/`）

```yaml
---
id: concept-slug
title: "概念名称"
type: concept
created_at: 2026-04-10
updated_at: 2026-04-10
aliases: [别名]
related:
  - "concept-related-1"
sources: [来源 raw 文件 id]
---

## Definition
[在当前系统中的定义]

## Why It Matters
[为什么重要]

## Where It Appears
[在哪些材料中出现过]

## Notes
[补充说明]
```

#### 主题页（`knowledge/permanent/topics/`）

```yaml
---
id: topic-slug
title: "主题名称"
type: topic
created_at: 2026-04-10
updated_at: 2026-04-10
related:
  - "concept-1"
  - "topic-related"
sources: [来源 raw 文件 id]
---

## Thesis
[核心判断]

## Main Structure
### 1. [子主题]
[内容]

## Tensions
- [冲突和未决问题]

## Related
- 相关概念
```

### 4.5 文件命名规则

| 产物类型 | 命名格式 | 示例 |
|---------|---------|------|
| 摘要 | `YYYY-MM-DD-slug-summary.md` | `2026-04-10-karpathy-summary.md` |
| 概念卡 | `concept-slug.md` | `concept-compound-engineering.md` |
| 主题页 | `topic-slug.md` | `topic-llm-knowledge-system.md` |

---

## 5. 第三步：输出

### 5.1 这一步做什么

基于知识系统回答问题或生成内容。输出既是消费，也是再生产——高价值输出应落文件，反过来增强系统。

### 5.2 操作方式

1. 把你的问题或需求发给 AI Agent
2. 附上提示词：`请按照 prompts/output.md 的要求，基于知识系统回答以下问题`
3. 同时附上 `knowledge/index/index.md`（让 AI 定位相关内容）
4. AI 会：
   - 先读索引，定位相关主题、概念、摘要
   - 阅读相关文件
   - 综合回答，区分"已知结论 / 推断 / 待确认"
   - 引用具体来源
   - 生成文件存入 `outputs/` 对应子目录

### 5.3 输出类型

| 类型 | 目录 | 适用场景 |
|------|------|---------|
| **问答归档** | `outputs/qa/` | 回答具体问题，保留问答记录 |
| **图文长文** | `outputs/article/` | 公众号文章、博客、知识卡 |
| **研究备忘录** | `outputs/memo/` | 内部判断、战略讨论 |
| **海报与 thread** | `outputs/social/` | 社交媒体传播、短内容 |

### 5.4 输出文件命名

```
outputs/类型/YYYY-MM-DD-type-slug.md
```

示例：
```
outputs/qa/2026-04-10-qa-knowledge-system-design.md
outputs/article/2026-04-10-article-compound-engineering.md
```

### 5.5 输出时的注意事项

| ✅ 应该做 | ❌ 不应该做 |
|----------|-----------|
| 先检索知识系统，再综合回答 | 不要直接凭印象作答 |
| 区分已知结论、推断、待确认 | 不要把推断当作事实 |
| 引用具体来源文件 | 不要给一段聊天回复就结束 |
| 产出实际文件 | 不要只留在聊天窗口里 |
| 发现知识缺口时列出来 | 不要假装知识库是完美的 |

---

## 6. 第四步：巡检

### 6.1 这一步做什么

定期审计知识系统的结构性问题，生成巡检报告。巡检是系统持续可信的关键——没有巡检，系统会越用越乱。

### 6.2 操作方式

1. 把以下内容发给 AI Agent：
   - `knowledge/index/index.md`（索引文件）
   - `knowledge/` 目录下的知识文件
   - 提示词：`请按照 prompts/inspect.md 的要求，对知识系统执行巡检`
2. AI 会扫描指定目录，找出问题并生成报告
3. 报告存入 `inspection/` 目录

### 6.3 巡检查什么

| 检查项 | 说明 |
|--------|------|
| **定义冲突** | 同一概念在不同文件中定义不一致 |
| **重复概念** | 应该合并的条目 |
| **孤岛文件** | 没有被任何文件引用的知识条目 |
| **缺来源** | 高频结论缺少原始来源支持 |
| **过时内容** | 长期未更新但仍被依赖 |
| **链接断裂** | `[[]]` 链接指向不存在的文件 |
| **命名不一致** | 文件命名不符合规范 |

### 6.4 巡检报告 Schema

```yaml
---
id: inspection-2026-04-10-scope
title: "巡检报告标题"
type: inspection
created_at: 2026-04-10
scope: [检查范围]
---

## Summary
[一句话概括]

## Findings
### High Priority
1. [问题] → 证据 + 建议动作

### Medium Priority
1. [问题] → 证据 + 建议动作

### Low Priority
1. [问题] → 证据 + 建议动作

## Statistics
- 概念总数：N
- 发现问题数：N

## Suggested Fixes
1. [修复建议]
```

### 6.5 巡检频率建议

| 知识条目数 | 建议巡检频率 |
|:----------:|:----------:|
| < 30 | 每新增 10 个条目巡检一次 |
| 30 - 100 | 每周一次 |
| > 100 | 每周一次，每月深度巡检一次 |

### 6.6 巡检原则

> **只出报告，不自动修复。**
> 审计员的职责是暴露问题，而不是悄悄修改。

---

## 7. 用 Obsidian 浏览知识系统

### 7.1 打开知识库

1. 打开 Obsidian
2. 点击「打开文件夹为仓库」
3. 选择 `knowledge-system/` 目录
4. 等待索引完成

### 7.2 推荐的界面布局

```
┌─────────────┬──────────────────────────┬──────────────┐
│             │                          │              │
│  文件浏览器  │       编辑器/预览          │  反向链接面板  │
│             │                          │              │
│  - raw/     │  （查看和编辑知识条目）     │ （查看谁引用了  │
│  - knowledge│                          │  当前文件）   │
│  - outputs/ │                          │              │
│  - prompts/ │                          │              │
│             │                          │              │
├─────────────┴──────────────────────────┴──────────────┤
│                     标签面板                             │
└────────────────────────────────────────────────────────┘
```

### 7.3 核心操作

| 操作 | 方法 |
|------|------|
| 浏览文件 | 左侧文件浏览器，按目录结构浏览 |
| 跳转链接 | 点击 `[[]]` 链接跳转到对应文件 |
| 查看引用 | 右侧反向链接面板，查看谁引用了当前文件 |
| 全局搜索 | `Ctrl+Shift+F` 搜索所有文件内容 |
| 查看图谱 | `Ctrl+G` 打开知识图谱可视化 |
| 快速切换 | `Ctrl+O` 快速打开文件 |
| 预览模式 | `Ctrl+E` 切换编辑/预览模式 |

### 7.4 推荐安装的插件

| 插件 | 用途 |
|------|------|
| **Templater** | 高级模板功能，快速创建标准化文件 |
| **Dataview** | 动态查询，按 frontmatter 字段筛选文件 |

---

## 8. 用 AI Agent 操作知识系统

### 8.1 通用操作流程

无论执行哪一步，都遵循以下流程：

```
1. 告诉 AI 先阅读 AGENTS.md
2. 说明要执行哪个步骤（摄取/消化/输出/巡检）
3. 提供对应的提示词（prompts/ 目录下的文件）
4. 提供相关的 schema（schemas/ 目录下的文件）
5. 提供输入材料（URL、文本、或已有知识文件）
6. AI 生成产物后，保存到对应目录
```

### 8.2 给 AI 的标准指令模板

#### 摄取指令

```
请先阅读 AGENTS.md 了解系统规则，然后按照 prompts/ingest.md 的要求，
将以下内容摄取为标准化 raw 文件，schema 参考 schemas/raw-schema.md。

[粘贴内容或提供 URL]
```

#### 消化指令

```
请先阅读 AGENTS.md 了解系统规则，然后按照 prompts/digest.md 的要求，
对以下 raw 文件执行消化。

已有知识索引：
[粘贴 knowledge/index/index.md 内容]

待消化的 raw 文件：
[粘贴 raw 文件内容]
```

#### 输出指令

```
请先阅读 AGENTS.md 了解系统规则，然后按照 prompts/output.md 的要求，
基于知识系统回答以下问题。

知识索引：
[粘贴 knowledge/index/index.md 内容]

我的问题：
[你的问题]
```

#### 巡检指令

```
请先阅读 AGENTS.md 了解系统规则，然后按照 prompts/inspect.md 的要求，
对知识系统执行巡检。

知识索引：
[粘贴 knowledge/index/index.md 内容]

待巡检的目录内容：
[粘贴相关文件内容]
```

---

## 9. 日常使用流程

### 9.1 日常摄入新资料

```
发现一篇好文章/一条好推文/一个有趣的视频
        │
        ▼
   摄取为 raw 文件 → raw/YYYY/MM/
        │
        ▼
   （积累几篇后）执行一次消化
        │
        ▼
   更新 knowledge/（摘要 + 概念 + 主题 + 索引）
```

### 9.2 日常问答与研究

```
有一个问题想研究
        │
        ▼
   先查 knowledge/index/index.md 定位相关内容
        │
        ▼
   阅读相关的 summary / concept / topic
        │
        ▼
   综合回答 → 存入 outputs/qa/
        │
        ▼
   如果发现知识缺口，补充到 knowledge/
```

### 9.3 日常记录临时想法

```
突然有一个想法
        │
        ▼
   快速记入 knowledge/fleeting/
        │
        ▼
   （后续消化时）判断是否值得提炼为概念卡
        │
        ▼
   如果值得 → 转入 knowledge/permanent/concepts/
   如果不值得 → 保留在 fleeting/ 或删除
```

### 9.4 定期维护

```
每周/每两周执行一次巡检
        │
        ▼
   生成巡检报告 → inspection/
        │
        ▼
   根据报告修复高优先级问题
        │
        ▼
   更新知识文件
```

---

## 10. 常见问题

### Q1：摄取时 AI 抓不到网页内容怎么办？

尝试以下方法：
1. 用 `r.jina.ai/URL` 获取网页纯文本
2. 手动复制网页正文粘贴给 AI
3. 使用 Obsidian Web Clipper 浏览器扩展
4. 如果是 PDF，直接上传文件给 AI

### Q2：消化时要不要每次都重新消化所有 raw 文件？

不需要。遵循**增量更新**原则：
- 只消化新增的 raw 文件
- 如果已有知识需要更新，只更新相关部分
- 不要全量重建

### Q3：概念卡和主题页有什么区别？

| | 概念卡 | 主题页 |
|---|--------|--------|
| 粒度 | 一个概念 | 多个概念的综合 |
| 类比 | 词典词条 | 教科书章节 |
| 数量 | 多（每个概念一个） | 少（每个主题一个） |
| 更新频率 | 随时补充 | 随研究深入迭代 |

### Q4：什么时候该新建概念，什么时候该更新已有概念？

- 如果已有概念能覆盖新内容 → 更新已有概念（补充 Notes、Where It Appears）
- 如果新内容与已有概念有关但不同 → 新建概念，并在 related 中建立链接
- 如果不确定 → 先记入 `fleeting/`，后续再判断

### Q5：输出一定要落文件吗？

是的。**不把聊天记录当资产，文件才是资产。**
高价值输出（问答、分析、研究结论）必须存入 `outputs/` 对应目录。

### Q6：巡检发现的问题要马上修复吗？

按优先级处理：
- **High**：尽快修复（影响知识准确性）
- **Medium**：在下次消化时顺手修复
- **Low**：有空再处理

### Q7：知识系统可以用于哪些场景？

不只是知识库！同样的方法适用于：
- 内容生产系统
- 行业研究系统
- 产品分析系统
- 销售跟进系统
- 个人生活管理

---

## 11. 扩展指南

### 11.1 添加新的输出类型

在 `outputs/` 下创建新目录即可，例如：
```
outputs/
├── qa/
├── article/
├── memo/
├── social/
├── infographic/    ← 新增：信息图
├── ppt/             ← 新增：演示文稿
└── pdf/             ← 新增：正式文档
```

### 11.2 添加自动化工具

随着系统规模增长，可以考虑：
- **Search CLI**：命令行搜索工具，让 AI 通过 CLI 检索知识库
- **Health Check 脚本**：自动执行基础巡检（检查链接断裂、frontmatter 完整性）
- **自动摄取脚本**：定时抓取指定 RSS/推特账号，自动生成 raw 文件

### 11.3 规模增长后的考虑

| 知识库规模 | 建议引入 |
|:----------:|---------|
| < 100 条 | 当前架构已够用 |
| 100 - 500 条 | 引入 Search CLI，考虑 Dataview 动态查询 |
| 500 - 2000 条 | 考虑引入轻量 RAG |
| > 2000 条 | 考虑合成数据 + 微调 |

### 11.4 迭代提示词和 Schema

`prompts/` 和 `schemas/` 是系统的"元资产"：
- 每次使用中发现提示词不够好 → 更新 `prompts/` 中的模板
- 每次使用中发现 schema 不够用 → 更新 `schemas/` 中的模板
- 随着使用，提示词越来越强大，成为你的个人资产

---

## 12. TRAE + Obsidian 深度集成

> 通过 Obsidian Local REST API 插件，TRAE 可以程序化地操作 Obsidian 中的知识系统——创建笔记、搜索内容、打开文件、执行命令等。

### 12.1 集成架构

```
TRAE (AI Agent)
    │
    ├── 直接读写文件 → knowledge-system/ 目录
    │
    └── 通过 REST API → Obsidian
                          ├── 创建/读取/更新/删除笔记
                          ├── 搜索笔记内容
                          ├── 在 Obsidian 中打开文件
                          ├── 打开知识图谱
                          └── 执行 Obsidian 命令
```

### 12.2 安装配置

详细配置步骤请参考 `tools/OBSIDIAN_SETUP.md`，简要流程：

1. 在 Obsidian 中安装 **Local REST API** 插件（社区插件搜索 "Local REST API"）
2. 在插件设置中启用 API 并记录 **API Key**
3. 配置环境变量：

```bash
export OBSIDIAN_API_KEY="your-api-key-here"
export OBSIDIAN_API_BASE="https://127.0.0.1:27124"
export OBSIDIAN_VAULT_PATH="knowledge-system"
```

4. 安装 Python 依赖：`pip install requests`
5. 验证连接：`python tools/ks.py health`

### 12.3 CLI 命令速查

```bash
# 检查连接
python tools/ks.py health

# 搜索
python tools/ks.py search "关键词"

# 在 Obsidian 中打开文件
python tools/ks.py open knowledge/index/index.md

# 读取文件内容
python tools/ks.py read knowledge/index/index.md

# 列出目录
python tools/ks.py list knowledge/permanent/concepts/

# 摄取新资料
python tools/ks.py ingest --title "标题" --content "正文" --source-url "https://..."

# 创建/覆盖文件
python tools/ks.py create --file "path/to/file.md" --content "# 内容"

# 追加内容
python tools/ks.py append --file "path/to/file.md" --content "追加内容"

# 打开知识图谱
python tools/ks.py graph

# 查看总索引
python tools/ks.py index
```

### 12.4 Python API 速查

```python
from tools.obsidian_client import ObsidianClient

client = ObsidianClient(
    api_base="https://127.0.0.1:27124",
    api_key="your-api-key",
    vault_path="knowledge-system",
)

# 笔记操作
client.create_note("knowledge/fleeting/idea.md", "# 想法\n\n内容")
client.read_note("knowledge/index/index.md")
client.append_to_note("knowledge/fleeting/idea.md", "\n追加内容")
client.insert_at_heading("knowledge/fleeting/idea.md", "## Notes", "新内容")
client.delete_note("knowledge/fleeting/old.md")

# 搜索
client.search("compound engineering")
client.search_simple("关键词")

# Obsidian 交互
client.open_in_obsidian("knowledge/index/index.md")
client.open_knowledge_graph()
client.list_commands()
client.execute_command("graph:open")

# 知识系统专用
client.ingest_raw(title="标题", content="正文", source_url="https://...")
client.read_knowledge_index()
client.quick_search("关键词")
```

### 12.5 TRAE 操作入口设计

TRAE 作为知识系统的**唯一操作入口**，所有操作都通过 TRAE 发起：

| 操作 | TRAE 执行方式 | Obsidian 响应 |
|------|-------------|--------------|
| 摄取资料 | TRAE 生成 raw 文件 → 写入 Obsidian | 文件自动出现在 Obsidian 文件浏览器中 |
| 消化资料 | TRAE 读取 raw → 生成知识文件 → 写入 Obsidian | 新概念卡/主题页自动出现 |
| 问答查询 | TRAE 搜索知识库 → 综合回答 → 写入 outputs/ | 输出文件自动出现 |
| 巡检审计 | TRAE 扫描知识库 → 生成报告 → 写入 inspection/ | 巡检报告自动出现 |
| 浏览知识 | TRAE 调用 API 在 Obsidian 中打开文件 | Obsidian 跳转到对应文件 |
| 查看图谱 | TRAE 调用 API 打开知识图谱 | Obsidian 显示关系网络 |
| 搜索定位 | TRAE 调用 API 搜索 | Obsidian 显示搜索结果 |

### 12.6 注意事项

- Obsidian 必须处于**打开状态**，REST API 才可用
- 插件使用自签名证书，Python 请求时已禁用 SSL 验证
- API 仅在本地运行（127.0.0.1），不会暴露到公网
- 如果端口被占用，可以在 Obsidian 插件设置中修改端口号

---

## 附录：文件速查表

| 文件 | 路径 | 用途 |
|------|------|------|
| 系统规则 | `AGENTS.md` | AI Agent 行为规范 |
| 操作手册 | `MANUAL.md` | 本文件 |
| 摄取提示词 | `prompts/ingest.md` | 摄取步骤的 AI 指令 |
| 消化提示词 | `prompts/digest.md` | 消化步骤的 AI 指令 |
| 输出提示词 | `prompts/output.md` | 输出步骤的 AI 指令 |
| 巡检提示词 | `prompts/inspect.md` | 巡检步骤的 AI 指令 |
| Raw Schema | `schemas/raw-schema.md` | 原始材料格式规范 |
| Summary Schema | `schemas/summary-schema.md` | 摘要格式规范 |
| Concept Schema | `schemas/concept-schema.md` | 概念卡格式规范 |
| Topic Schema | `schemas/topic-schema.md` | 主题页格式规范 |
| Inspection Schema | `schemas/inspection-schema.md` | 巡检报告格式规范 |
| 总索引 | `knowledge/index/index.md` | 所有知识条目的入口 |
| 知识系统 MOC | `knowledge/index/moc-knowledge-system.md` | 知识系统主题导航 |
| Obsidian 客户端 | `tools/obsidian_client.py` | Python Obsidian REST API 客户端 |
| CLI 工具 | `tools/ks.py` | 命令行操作入口 |
| Obsidian 配置指南 | `tools/OBSIDIAN_SETUP.md` | 插件安装和 API 配置教程 |
