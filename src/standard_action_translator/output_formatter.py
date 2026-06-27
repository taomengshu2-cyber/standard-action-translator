from __future__ import annotations

import json

from .models import DiagnosisResult


def format_markdown(result: DiagnosisResult) -> str:
    if result.is_strong_match:
        return format_positive_markdown(result)

    lines: list[str] = [
        f"# 标准行动转译结果：{result.standard_id} {result.standard_title}",
        "",
        "## 1. 这条标准要求你做到什么",
        "",
        result.expectation,
        "",
        "## 2. 你现在已经体现的地方",
        "",
    ]
    lines.extend(f"- {item}" for item in result.matched_evidence)
    lines.extend(["", "## 3. 你现在最需要补强的地方", ""])
    lines.extend(f"- {item}" for item in result.main_gaps)
    lines.extend(["", "## 4. 下一步具体改哪里", ""])
    lines.extend(f"{index}. {item}" for index, item in enumerate(result.next_actions, start=1))
    lines.extend(["", "## 5. 建议补充的材料或证据", ""])
    lines.extend(f"- {item}" for item in result.materials_to_add or ["补充能证明目标、过程或成效的具体材料。"])
    lines.extend(["", "## 7. 边界提醒", ""])
    lines.extend(result.guardrail_notes)
    return "\n".join(lines) + "\n"


def format_positive_markdown(result: DiagnosisResult) -> str:
    lines: list[str] = [
        f"# 标准行动转译结果：{result.standard_id} {result.standard_title}",
        "",
        "## 1. 这条标准要求你做到什么",
        "",
        result.expectation,
        "",
        "## 2. 你现在已经体现的地方",
        "",
    ]
    lines.extend(f"- {item}" for item in result.matched_evidence)
    lines.extend(["", "## 3. 这份材料符合标准要求的地方", ""])
    lines.extend(f"- {item}" for item in result.main_gaps)
    lines.extend(["", "## 4. 你是否想把这份材料优势提炼为可复用做法？", ""])
    lines.extend(format_positive_choice_block(result.positive_mode))
    if result.positive_mode == "yes":
        lines.extend(["", "## 5. 如果选择继续提炼，可以先回答", ""])
        lines.extend(format_positive_questions(result.standard_id))
        if result.reusable_practices:
            lines.extend(["", "## 6. 根据你的选择生成的可复用做法", ""])
            lines.extend(f"{index}. {item}" for index, item in enumerate(result.reusable_practices, start=1))
            lines.extend(["", "## 7. 边界提醒", ""])
        else:
            lines.extend(["", "## 6. 边界提醒", ""])
    else:
        lines.extend(["", "## 5. 边界提醒", ""])
    lines.extend(result.guardrail_notes)
    return "\n".join(lines) + "\n"


def format_positive_choice_block(positive_mode: str) -> list[str]:
    if positive_mode == "no":
        return [
            "你已选择：否。",
            "",
            "这份材料已经比较符合标准要求，可以作为当前版本保留。后续只需要在提交前检查格式、附件和关键证据是否完整即可。",
        ]
    if positive_mode == "yes":
        return [
            "你已选择：是。",
            "",
            "下面的问题用于帮助你把这份材料中“做得对的地方”提炼成其他教研组也能学习的可复用做法。",
        ]
    return [
        "请选择：",
        "",
        "- 是：继续把这份材料的优势提炼为可复用做法。",
        "- 否：只确认这份材料总体符合标准，保留当前版本。",
        "",
        "如果你在命令行中测试，可以重新运行同一个命令，并加上：",
        "",
        "```bash",
        "--positive-mode yes",
        "```",
        "",
        "或：",
        "",
        "```bash",
        "--positive-mode no",
        "```",
    ]


def format_positive_questions(standard_id: str) -> list[str]:
    if standard_id == "B6":
        return [
            "1. 这份总结最值得其他教研组学习的结构是什么？",
            "   - A. “研修主线—过程证据—成果特色—反思改进—下期规划”的完整闭环结构。",
            "   - B. “计划研修—实际研修—完成情况”的对照复盘结构。",
            "   - C. 其他：请自行输入你认为最值得学习的结构。",
            "",
            "2. 哪一处最能证明它做到了对照计划检视达成度？",
            "   - A. “实际研修与计划研修对比”表，尤其是计划研修主题、实际研修情况和完成情况。",
            "   - B. “反思与不足—改进措施—下学期研修初步规划”的连续安排。",
            "   - C. 其他：请自行输入你认为最能证明达成度的证据。",
            "",
            "3. 反思与下学期规划之间有没有一一对应关系？",
            "   - A. 有，对本期不足已经安排了下学期的对应改进方向。",
            "   - B. 部分有，还需要把每条不足和下学期具体月份、任务或责任人再对应起来。",
            "   - C. 其他：请自行输入你的判断。",
            "",
            "你可以把选择发给我，例如：1A、2A、3B。我会根据你的选择或补充回答，生成这份材料可被复用的做法。",
        ]
    return [
        "1. 这份材料最值得其他教研组学习的做法是什么？",
        "   - A. 学它的结构。",
        "   - B. 学它的证据呈现方式。",
        "   - C. 其他：请自行输入。",
        "",
        "2. 哪一处最能证明它符合标准？",
        "   - A. 材料中的过程证据。",
        "   - B. 材料中的成果或反思。",
        "   - C. 其他：请自行输入。",
        "",
        "3. 这份材料可以迁移给其他教研组的部分是什么？",
        "   - A. 可复用流程。",
        "   - B. 可复用工具或模板。",
        "   - C. 其他：请自行输入。",
        "",
        "你可以把选择发给我，例如：1A、2B、3A。我会根据你的选择或补充回答，生成这份材料可被复用的做法。",
    ]


def format_json(result: DiagnosisResult) -> str:
    return json.dumps(result.model_dump(), ensure_ascii=False, indent=2)


def format_result(result: DiagnosisResult, output_format: str) -> str:
    if output_format == "markdown":
        return format_markdown(result)
    if output_format == "json":
        return format_json(result)
    raise ValueError(f"unsupported format: {output_format}")
