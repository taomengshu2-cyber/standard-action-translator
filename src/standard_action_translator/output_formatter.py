from __future__ import annotations

import json

from .models import DiagnosisResult


def format_markdown(result: DiagnosisResult) -> str:
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
    lines.extend(["", "## 6. 继续修改前，可以先回答这几个问题", ""])
    lines.extend(f"- {item}" for item in result.diagnostic_questions)
    lines.extend(["", "## 7. 边界提醒", ""])
    lines.extend(result.guardrail_notes)
    return "\n".join(lines) + "\n"


def format_json(result: DiagnosisResult) -> str:
    return json.dumps(result.model_dump(), ensure_ascii=False, indent=2)


def format_result(result: DiagnosisResult, output_format: str) -> str:
    if output_format == "markdown":
        return format_markdown(result)
    if output_format == "json":
        return format_json(result)
    raise ValueError(f"unsupported format: {output_format}")
