from pathlib import Path

from standard_action_translator.diagnostician import diagnose
from standard_action_translator.output_formatter import format_markdown


PROJECT_ROOT = Path(__file__).resolve().parents[1]
PACK = PROJECT_ROOT / "data" / "standard_packs" / "shapingba_learning_group_2026"
INPUT = PROJECT_ROOT / "examples" / "b7_activity_plan_input.md"


def test_b7_activity_plan_detects_expected_gaps():
    result = diagnose(INPUT.read_text(encoding="utf-8"), "B7", PACK)
    gaps = "\n".join(result.main_gaps)

    assert "目标偏大偏虚" in gaps
    assert "证据链" in gaps
    assert "评价工具" in gaps
    assert len(result.next_actions) >= 3


def test_b7_markdown_output_has_fixed_sections():
    result = diagnose(INPUT.read_text(encoding="utf-8"), "B7", PACK)
    markdown = format_markdown(result)

    assert "# 标准行动转译结果：B7 活动方案" in markdown
    assert "## 4. 下一步具体改哪里" in markdown
    assert "## 6. 继续修改前，可以先回答这几个问题" not in markdown
    assert "## 7. 边界提醒" in markdown
    assert "90分" not in markdown
    assert "排名第" not in markdown


def test_b7_non_strong_output_uses_contextual_guidance():
    result = diagnose(INPUT.read_text(encoding="utf-8"), "B7", PACK)
    markdown = format_markdown(result)

    assert "材料中的相关表述是" in markdown or "我在材料中暂未看到" in markdown
    assert "针对材料中" in markdown
    assert "优秀材料通常会" in markdown
