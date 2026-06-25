from pathlib import Path

from standard_action_translator.cli import main


PROJECT_ROOT = Path(__file__).resolve().parents[1]
PACK = PROJECT_ROOT / "data" / "standard_packs" / "shapingba_learning_group_2026"
INPUT = PROJECT_ROOT / "examples" / "b7_activity_plan_input.md"


def test_cli_diagnose_outputs_markdown_file(tmp_path):
    output = tmp_path / "diagnosis.md"

    exit_code = main(
        [
            "diagnose",
            "--pack",
            str(PACK),
            "--standard",
            "B7",
            "--input",
            str(INPUT),
            "--format",
            "markdown",
            "--output",
            str(output),
        ]
    )

    assert exit_code == 0
    markdown = output.read_text(encoding="utf-8")
    assert "# 标准行动转译结果：B7 活动方案" in markdown


def test_cli_validate_pack(capsys):
    exit_code = main(["validate-pack", str(PACK)])

    captured = capsys.readouterr()
    assert exit_code == 0
    assert "标准包校验通过" in captured.out
