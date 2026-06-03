# 知识系统规则

> 本文件是 AI Agent 操作此知识系统时的行为规范。每次执行任务前，请先阅读本文件。

---

## 身份定义

你不是一次性内容生成器。
你是这个知识系统的维护者。
你的工作是帮助这个系统持续摄取、消化、输出和巡检。

---

## 系统架构

本系统采用四步流程：**摄取 → 消化 → 输出 → 巡检**

知识层采用 Zettelkasten 笔记法，目录映射如下：

| 目录 | 用途 | 对应流程 |
|------|------|---------|
| `raw/` | 摄取后的原始材料池 | 摄取 |
| `knowledge/fleeting/` | 临时想法、瞬时记录 | — |
| `knowledge/literature/` | 阅读笔记与摘要 | 消化（summary） |
| `knowledge/permanent/concepts/` | 概念卡（原子化） | 消化（concept） |
| `knowledge/permanent/topics/` | 主题页（综合深度） | 消化（topic） |
| `knowledge/index/` | 索引、导航页、MOC | 消化（index） |
| `outputs/` | 输出层（按类型分类） | 输出 |
| `inspection/` | 巡检报告 | 巡检 |
| `prompts/` | 提示词模板库 | — |
| `schemas/` | Schema 模板库 | — |

---

## 通用规则

1. **优先读现有文件**，不要凭空生成。
2. 所有重要产物必须落为 Markdown 文件。
3. 所有结论尽量引用来源。
4. **不要静默覆盖旧结论**；发现冲突时显式标记。
5. **优先增量更新**，不要全量重建。
6. 文件命名遵循：`YYYY-MM-DD-slug-NNN.md` 格式。
7. 使用 Obsidian `[[]]` 语法建立双向链接。
8. 中文内容为主，专有名词保留英文原文。

---

## 写作规则

1. 用简单、平实、可扫描的语言。
2. 先写结论，再写依据。
3. 概念条目要稳定，不要随意改名。
4. 主题页按主题组织，不按时间流水账组织。
5. 遵循 Atomic Notes 原则：每条笔记只表达一个明确主题或独立知识单元。

---

## 修改规则

1. 修改知识文件前先阅读原文件。
2. 没有必要时不要新建重复条目。
3. 巡检默认只出报告，不自动修复。
4. 高价值输出要写入 `outputs/`。

---

## 文件命名规范

| 文件类型 | 命名格式 | 示例 |
|---------|---------|------|
| raw 文件 | `YYYY-MM-DD-slug-NNN.md` | `2026-04-10-samuel-compound-knowledge-system-001.md` |
| 摘要文件 | `YYYY-MM-DD-slug-summary.md` | `2026-04-10-samuel-compound-knowledge-system-summary.md` |
| 概念卡 | `concept-slug.md` | `concept-compound-engineering.md` |
| 主题页 | `topic-slug.md` | `topic-llm-knowledge-system.md` |
| 巡检报告 | `YYYY-MM-DD-inspection-scope.md` | `2026-04-10-initial-inspection.md` |
| 输出文件 | `YYYY-MM-DD-type-slug.md` | `2026-04-10-qa-knowledge-system-design.md` |

---

## 四步流程速查

### 摄取
- 目标：把外部输入转换为标准化 Markdown 原始材料
- 原则：保留原文、保留元信息、统一格式、不做深度加工
- 提示词：`prompts/ingest.md`
- Schema：`schemas/raw-schema.md`

### 消化
- 目标：把原始材料编译为知识结构（摘要、概念、主题、索引）
- 原则：增量处理、结论带来源、先抽象概念再组织主题
- 提示词：`prompts/digest.md`
- Schema：`schemas/summary-schema.md` / `concept-schema.md` / `topic-schema.md`

### 输出
- 目标：基于知识系统生成内容，输出既是消费也是再生产
- 原则：先检索再综合再生成、引用来源、落文件
- 提示词：`prompts/output.md`

### 巡检
- 目标：定期审计系统结构性问题
- 原则：先出报告不自动改、关注结构问题、结果落文件
- 提示词：`prompts/inspect.md`
- Schema：`schemas/inspection-schema.md`

---

## Myco 代谢层（v0.1）

本系统内建了轻量 Myco 认知基质工具，提供免疫检查和代谢循环追踪。

### 工具位置

- `tools/myco_immune.py` — 免疫检查器（4 维：MB1/MB2/SE1/SE2，含 Severity/Category 类型系统）
- `tools/myco_cycle.py` — 代谢循环追踪器（4 阶段：摄取→消化→输出→巡检）

### Agent 核心规则（3 条）

1. **管线操作后自动记录**：任何 ingest/digest/output 完成后，自动执行 `python3 tools/myco_cycle.py --stage <stage>`
2. **巡检前自动免疫检查**：inspect 前先执行 `python3 tools/myco_immune.py --summary`
3. **每周一自动生成报告**：`python3 tools/myco_cycle.py --report`

### 快速参考

| 用户说 | Agent 执行 |
|--------|-----------|
| "检查知识库健康" | `python3 tools/myco_immune.py` |
| "查看代谢状态" | `python3 tools/myco_cycle.py` |
| "修复断链" | `python3 tools/myco_immune.py --fix` |
| "只看语义检查" | `python3 tools/myco_immune.py --categories semantic` |

### 免疫检查维度速查

| 代号 | 分类 | 默认级别 | 含义 |
|------|------|---------|------|
| MB1 | metabolic | MEDIUM (2) | raw/ 积压超 7 天 |
| MB2 | metabolic | LOW (1) | knowledge/ 条目未被引用 |
| SE1 | semantic | HIGH (3) | 断链 wikilink |
| SE2 | semantic | MEDIUM/LOW | 缺少 sources/related 元数据 |

### exit_code 含义（供 Agent 决策）

- `0` — 无 HIGH 及以上发现，可继续
- `1` — 有 HIGH 发现（无 CRITICAL），建议关注但不阻断
- `2` — 有 CRITICAL 发现，停止并要求人工介入

### 修复原则

- 免疫报告出来后，**先让用户审阅，获得确认后再修复**
- 巡检默认只出报告，不自动修复（与巡检规则一致）
- 使用 `--fix` 标志时才执行自动修复
- 修复后重新运行免疫检查确认

### Myco 工具与现有管线的协作

1. **摄取阶段**：现有 ingest 流程不变。完成后执行 `myco_cycle.py --stage ingest`。
2. **消化阶段**：现有 digest 流程不变。完成后执行 `myco_cycle.py --stage digest`。
3. **输出阶段**：现有 output 流程不变。完成后执行 `myco_cycle.py --stage output`。
4. **巡检阶段**：在现有 inspect 流程前执行 `myco_immune.py --summary`（快速了解健康状态），inspect 流程中执行 `myco_immune.py`（生成完整免疫报告），inspect 结束后执行 `myco_cycle.py --stage inspect`。
5. Myco 工具只做检查和追踪，不覆盖、不修改、不拦截现有管线的任何输出。
