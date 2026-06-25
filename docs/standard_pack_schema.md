# 标准包 Schema

一个标准包至少包含四个文件：

- `metadata.json`
- `standards.json`
- `gap_rules.json`
- `action_templates.json`

可选文件：

- `examples.json`

## metadata.json

描述标准包版本、适用区域、适用用户和支持的材料类型。

## standards.json

每条标准包含：

- `id`
- `title`
- `category`
- `original_text`
- `plain_language_expectation`
- `key_requirements`
- `required_evidence`
- `related_document_types`
- `keywords`
- `version`

## gap_rules.json

差距规则用于把材料问题从“泛泛感觉”变成可追踪诊断。`gap_type` 取值包括：

- `understanding_gap`
- `behavior_gap`
- `structure_gap`
- `evidence_gap`
- `evaluation_gap`

## action_templates.json

行动模板用于把差距转成下一步动作。动作必须落到流程、证据、工具、材料、时间或责任人之一。
