# data/

此目录中的 JSON 由分析管线生成：

```bash
python -m pipeline.run
```

- **stats.json** — 语料统计与方法说明
- **imagery.json** — 意象节点（频率、诗篇、关联、年份分布）
- **cooccurrence.json** — 意象共现边
- **poems.json** — 诗篇记录与短摘录

这些是**派生数据**，请勿手工编辑——改动 `pipeline/` 后重新运行管线即可。

其中的诗句摘录控制在约 36 字以内（仅含意象所在诗句的片段），不含完整诗篇，以遵守版权约束。
