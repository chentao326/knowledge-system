# 可复利知识系统

> 用 AI 搭建一套会复利的知识系统，让每次处理都不是结束，而是下一次处理的输入。

---

## 系统简介

本系统基于 **Compound Engineering（复利工程）** 理念设计，核心思想是：

> 不要只让 AI 生成一次性结果。要让 AI 帮你生成一套能持续使用、自我增强的系统。

系统采用四步流程：**摄取 → 消化 → 输出 → 巡检**，知识层使用 Zettelkasten 笔记法组织。

---

## 目录结构

```
knowledge-system/
├── AGENTS.md              # 系统规则（AI Agent 行为规范）
├── README.md              # 本文件
│
├── raw/                   # 摄取层：原始材料池
│   └── YYYY/MM/           # 按年月组织
│
├── knowledge/             # 知识层（Zettelkasten）
│   ├── fleeting/          # 临时想法
│   ├── literature/        # 阅读笔记与摘要
│   ├── permanent/
│   │   ├── concepts/      # 概念卡（原子化）
│   │   └── topics/        # 主题页（综合深度）
│   └── index/             # 索引、导航页、MOC
│
├── outputs/               # 输出层
│   ├── qa/                # 问答归档
│   ├── article/           # 图文长文
│   ├── memo/              # 研究备忘录
│   └── social/            # 海报与 thread
│
├── inspection/            # 巡检报告
├── prompts/               # 提示词模板库
├── schemas/               # Schema 模板库
└── .obsidian/             # Obsidian 配置
```

---

## 四步流程

### 1. 摄取 (Ingest)
把外部输入（网页、推文、论文、播客等）统一转换为标准化 Markdown 文件，存入 `raw/`。
- 只做标准化，不做知识加工
- 保留原文、保留元信息（来源/时间/作者）
- 参考：`prompts/ingest.md` + `schemas/raw-schema.md`

### 2. 消化 (Digest)
把原始材料编译为可复用的知识结构，存入 `knowledge/`。
- 生成摘要 → `knowledge/literature/`
- 抽取概念 → `knowledge/permanent/concepts/`
- 创建主题页 → `knowledge/permanent/topics/`
- 更新索引 → `knowledge/index/`
- 参考：`prompts/digest.md` + 对应 schema

### 3. 输出 (Output)
基于知识系统回答问题或生成内容，存入 `outputs/`。
- 先检索，再综合，再生成
- 输出既是消费，也是再生产
- 参考：`prompts/output.md`

### 4. 巡检 (Inspect)
定期审计系统结构性问题，生成报告存入 `inspection/`。
- 检查冲突、重复、孤岛、断链、过时、缺来源
- 只出报告，不自动修复
- 参考：`prompts/inspect.md` + `schemas/inspection-schema.md`

---

## 使用方法

### 用 Obsidian 打开
1. 用 Obsidian 打开 `knowledge-system/` 文件夹
2. 通过文件浏览器浏览 raw/ knowledge/ outputs/
3. 利用双向链接 `[[]]` 在知识条目间跳转
4. 使用反向链接面板查看引用关系

### 用 AI Agent 操作
1. 让 AI 先阅读 `AGENTS.md` 了解系统规则
2. 根据任务选择对应步骤的提示词（`prompts/`）
3. 按对应 schema（`schemas/`）输出标准化文件
4. 遵循增量更新原则，不全量重建

---

## 最小闭环

想尽快跑通？做这件事：
1. 摄取一篇文章和一条推文，存到 `raw/`
2. 让 AI 对这两个 raw 文件执行一次消化
3. 让 AI 回答一个具体问题，把回答存到 `outputs/qa/`
4. 让 AI 对 `knowledge/` 做一次巡检，生成报告

跑通这一轮，系统雏形就有了。

---

## 参考资料

- Samuel「用 AI 搭一套会复利的知识系统」
- Andrej Karpathy「LLM Knowledge Bases」
