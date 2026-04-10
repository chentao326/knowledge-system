# 消化提示词

你正在执行"消化"步骤。

## 目标

把新增的 raw 原始材料编译为知识层内容，包括摘要、概念条目、主题页和索引更新。

## 工作要求

1. 只处理新增或指定的 raw 文件。
2. 先阅读原始材料，再判断它应该更新哪些知识文件。
3. 先复用已有概念和主题页，必要时再新建。
4. 所有结论都尽量保留来源引用。
5. 不要把知识层写成流水账。
6. 不要只按时间组织内容，优先按主题、观点、关系组织。
7. 如果发现内容与现有知识冲突，标记冲突，不要偷偷覆盖。
8. 处理原则遵循 Atomic Notes：每条笔记只表达一个明确主题或一个独立知识单元，不要把多个概念混在一条笔记里。

## 任务顺序

1. 阅读 raw 文件。
2. 输出结构化摘要 → `knowledge/literature/`
3. 抽取关键概念 → `knowledge/permanent/concepts/`
4. 判断应更新的主题页 → `knowledge/permanent/topics/`
5. 给出索引更新建议 → `knowledge/index/`
6. 严格按照对应 schema 输出。

## Schema 参考

- 摘要：`schemas/summary-schema.md`
- 概念卡：`schemas/concept-schema.md`
- 主题页：`schemas/topic-schema.md`

## 关键原则

> 你不是在总结一篇文章，而是在更新一个系统。
