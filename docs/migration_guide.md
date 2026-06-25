# 迁移指南

## 其他学校如何迁移

1. 复制 `template_school_pack`
2. 修改 `metadata.json`
3. 把本校或本区标准填入 `standards.json`
4. 为每条标准补充 `plain_language_expectation`
5. 为每条标准补充 `key_requirements`
6. 为每条标准补充 `required_evidence`
7. 根据本校常见问题填写 `gap_rules.json`
8. 根据希望组长采取的动作填写 `action_templates.json`
9. 运行 `sat validate-pack`
10. 用一份真实材料测试诊断效果

核心迁移原则：

不是迁移某个区域的具体标准，而是迁移“标准—差距—行动”的转译逻辑。
