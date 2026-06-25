# standard-action-translator

学习型教研组（备课组）标准行动转译工具。

它把评价标准转译为教研组长能执行的改进动作，帮助回答三件事：

1. 标准要求我做到什么？
2. 我现在还缺什么？
3. 下一步具体改哪里？

## 它解决什么问题

很多教研材料的问题不是“不会写”，而是标准、材料和行动之间没有连起来。本项目把标准包、差距规则和行动模板结构化，让诊断更稳定、建议更具体。

## 它不做什么

- 不替评委评分
- 不给排名
- 不代写完整计划、总结、方案或记录
- 不直接复制优秀案例
- 不把论文直接丢给组长

## 快速开始

当前内置标准包：

- `data/standard_packs/shapingba_learning_group_2026`：沙坪坝区 2026 学习型教研组（备课组）建设评估标准包 V1
- `data/standard_packs/template_school_pack`：其他学校或区域迁移模板

```bash
python3 -m pip install -e .
sat validate-pack data/standard_packs/shapingba_learning_group_2026
sat diagnose --pack data/standard_packs/shapingba_learning_group_2026 --standard B7 --input examples/b7_activity_plan_input.md --format markdown
```

如果还没有安装依赖：

```bash
python3 -m pip install -e ".[dev]"
```

## CLI 示例

解释标准：

```bash
sat explain --pack data/standard_packs/shapingba_learning_group_2026 --standard B7
```

诊断材料：

```bash
sat diagnose \
  --pack data/standard_packs/shapingba_learning_group_2026 \
  --standard B7 \
  --input examples/b7_activity_plan_input.md \
  --format markdown
```

校验标准包：

```bash
sat validate-pack data/standard_packs/shapingba_learning_group_2026
```

比较标准包：

```bash
sat diff-pack old_pack_path new_pack_path
```

创建迁移模板：

```bash
sat scaffold-pack --name my_school_learning_group --output data/standard_packs/my_school_learning_group
```

## 标准包结构

```text
standard_pack/
├── metadata.json
├── standards.json
├── gap_rules.json
├── action_templates.json
└── examples.json
```

`standards.json` 存标准解释和证据要求，`gap_rules.json` 存常见差距，`action_templates.json` 存下一步动作。

## 如何更新区级标准

1. 修改或新增标准包目录
2. 更新 `metadata.json` 版本号
3. 更新 `standards.json`
4. 同步检查 `gap_rules.json`
5. 同步检查 `action_templates.json`
6. 运行 `sat validate-pack`
7. 使用 `sat diff-pack` 生成差异报告

## 如何迁移到其他学校

复制 `data/standard_packs/template_school_pack`，替换成本校或本区标准。迁移的不是示例区域的具体内容，而是“标准—差距—行动”的转译逻辑。

如果仓库公开发布，而真实区评标准不适合公开，可以只保留模板和脱敏样例，把真实标准包放在私有仓库或本地目录中使用。

## 与普通大模型的差异

普通大模型适合临时问答；本项目适合形成稳定、可更新、可迁移、可测试的标准行动转译流程。详细说明见 `docs/why_not_plain_llm.md`。

## 路线图

### V1

- 标准包结构
- B1-B15 标准包 V1
- B1/B4/B5 学期初评价反馈转译
- B5/B6/B7/B8/B10 核心行动规则
- 规则式诊断
- Markdown/JSON 输出
- 防评分、防代写
- CLI

### V2

- 基于学期中、学期末评价继续补全真实常见差距
- 优秀案例元数据
- 案例解释，不展示全文
- 局部修改建议
- 多轮版本对比

### V3

- 接入 LLMProvider
- 接入 paper-discovery
- 增加 Evidence Translator，把研究发现转译为教研行动
- Web UI
- 多学校标准包管理
