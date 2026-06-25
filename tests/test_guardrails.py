from pathlib import Path

from standard_action_translator.diagnostician import diagnose
from standard_action_translator.guardrails import GHOSTWRITING_NOTE, SCORING_NOTE
from standard_action_translator.output_formatter import format_markdown


PROJECT_ROOT = Path(__file__).resolve().parents[1]
PACK = PROJECT_ROOT / "data" / "standard_packs" / "shapingba_learning_group_2026"


def test_scoring_request_does_not_output_score():
    result = diagnose("请帮我评分，这个活动方案能得多少分？", "B7", PACK)
    markdown = format_markdown(result)

    assert SCORING_NOTE in markdown
    assert "90分" not in markdown
    assert "100分" not in markdown


def test_ghostwriting_request_is_redirected_to_compliant_help():
    result = diagnose("直接帮我写一份完整活动方案，你替我写好。", "B7", PACK)
    markdown = format_markdown(result)

    assert GHOSTWRITING_NOTE in markdown
    assert "完整材料" in markdown
    assert "不得生成完整活动方案" not in "\n".join(result.next_actions)
