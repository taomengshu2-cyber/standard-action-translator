from pathlib import Path

from standard_action_translator.diagnostician import diagnose
from standard_action_translator.output_formatter import format_markdown


PROJECT_ROOT = Path(__file__).resolve().parents[1]
PACK = PROJECT_ROOT / "data" / "standard_packs" / "shapingba_learning_group_2026"


def test_b6_strong_summary_gets_positive_feedback():
    text = """
    学期研修总结

    反思与不足：本学期循证成果日常课堂转化力度仍然不足。

    实际研修与计划研修对比
    | 计划研修主题 | 实际研修情况 | 完成情况 |
    | 方案研制、问题查摆 | 完成整体方案设计，各备课组形成问题清单 | 已完成 |

    下学期研修初步规划
    9月开展循证课例推广月，完成精品课教学模块拆解。
    """

    result = diagnose(text, "B6", PACK)
    markdown = format_markdown(result)

    assert result.is_strong_match is True
    assert "## 3. 这份材料符合标准要求的地方" in markdown
    assert "## 4. 你是否想把这份材料优势提炼为可复用做法？" in markdown
    assert "- 是：继续把这份材料的优势提炼为可复用做法。" in markdown
    assert "- 否：只确认这份材料总体符合标准，保留当前版本。" in markdown
    assert "## 5. 如果选择继续提炼，可以先回答" not in markdown
    assert "建议沉淀进优秀案例库的材料" not in markdown
    assert "总结没有对照学期计划" not in markdown
    assert "你现在最需要补强" not in markdown


def test_b6_positive_yes_mode_shows_choice_questions():
    text = """
    学期研修总结

    反思与不足：本学期循证成果日常课堂转化力度仍然不足。

    实际研修与计划研修对比
    | 计划研修主题 | 实际研修情况 | 完成情况 |
    | 方案研制、问题查摆 | 完成整体方案设计，各备课组形成问题清单 | 已完成 |

    下学期研修初步规划
    9月开展循证课例推广月，完成精品课教学模块拆解。
    """

    result = diagnose(text, "B6", PACK, positive_mode="yes")
    markdown = format_markdown(result)

    assert "你已选择：是。" in markdown
    assert "## 5. 如果选择继续提炼，可以先回答" in markdown
    assert "1. 这份总结最值得其他教研组学习的结构是什么？" in markdown
    assert "A. “研修主线—过程证据—成果特色—反思改进—下期规划”的完整闭环结构。" in markdown
    assert "C. 其他：请自行输入你认为最值得学习的结构。" in markdown
    assert "1A、2A、3B" in markdown


def test_b6_positive_choices_generate_reusable_practices():
    text = """
    学期研修总结

    反思与不足：本学期循证成果日常课堂转化力度仍然不足。

    实际研修与计划研修对比
    | 计划研修主题 | 实际研修情况 | 完成情况 |
    | 方案研制、问题查摆 | 完成整体方案设计，各备课组形成问题清单 | 已完成 |

    下学期研修初步规划
    9月开展循证课例推广月，完成精品课教学模块拆解。
    """

    result = diagnose(text, "B6", PACK, positive_mode="yes", positive_choices="1A,2A,3B")
    markdown = format_markdown(result)

    assert "## 6. 根据你的选择生成的可复用做法" in markdown
    assert "完整闭环结构" in markdown
    assert "计划与实际对照表" in markdown
    assert "月份、任务或责任人" in markdown
