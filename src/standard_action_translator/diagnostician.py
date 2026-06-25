from __future__ import annotations

from pathlib import Path

from .action_generator import ActionGenerator, deduplicate
from .guardrails import Guardrails
from .interpreter import StandardInterpreter
from .loaders import load_standard_pack
from .models import DiagnosisResult, GapRule


def diagnose(
    text: str,
    standard_id: str,
    pack_path: str | Path,
    mode: str = "diagnose",
) -> DiagnosisResult:
    pack = load_standard_pack(pack_path)
    standard = pack.get_standard(standard_id)
    interpreter = StandardInterpreter()
    guardrails = Guardrails()

    matched_evidence = extract_matched_evidence(text, standard.required_evidence + standard.keywords)
    matched_rules = match_gap_rules(text, pack.rules_for(standard_id))
    matched_rule_ids = {rule.id for rule in matched_rules}
    action_templates = pack.actions_for(standard_id, matched_rule_ids)

    next_actions, materials_to_add = ActionGenerator().generate(action_templates)
    if not matched_rules:
        next_actions = [
            "对照标准逐项标注材料中已有证据，并补充尚未出现的证据来源、评价工具或后续安排。"
        ]

    diagnostic_questions = deduplicate(
        [question for rule in matched_rules for question in rule.diagnostic_questions]
    )
    main_gaps = [rule.gap_description for rule in matched_rules]

    if not matched_evidence:
        matched_evidence = ["暂未识别到与该标准直接对应的明确证据。"]
    if not main_gaps:
        main_gaps = ["未触发明显差距规则，但仍建议检查证据链、过程设计和评价方式是否完整。"]
    if not diagnostic_questions:
        diagnostic_questions = [
            "这份材料中哪一处能证明目标已经达成？",
            "下一次活动或总结中准备补充哪一种证据？",
        ]

    next_actions = guardrails.remove_vague_phrases(next_actions)

    return DiagnosisResult(
        standard_id=standard.id,
        standard_title=standard.title,
        expectation=interpreter.plain_expectation(standard),
        matched_evidence=matched_evidence,
        main_gaps=main_gaps,
        diagnostic_questions=diagnostic_questions,
        next_actions=next_actions,
        materials_to_add=materials_to_add,
        guardrail_notes=guardrails.check_input(text),
    )


def extract_matched_evidence(text: str, evidence_terms: list[str]) -> list[str]:
    matches: list[str] = []
    for term in evidence_terms:
        if term and term in text:
            matches.append(f"材料中出现了“{term}”，可作为进一步展开的证据线索。")
    return deduplicate(matches)


def match_gap_rules(text: str, rules: list[GapRule]) -> list[GapRule]:
    matched: list[GapRule] = []
    for rule in rules:
        has_avoid_phrase = any(phrase in text for phrase in rule.avoid_phrases)
        has_trigger = any(keyword in text for keyword in rule.trigger_keywords)
        should_trigger_by_missing = bool(rule.missing_evidence) and not any(
            evidence in text for evidence in rule.missing_evidence
        )

        if has_avoid_phrase or has_trigger or should_trigger_by_missing:
            matched.append(rule)

    severity_order = {"high": 0, "medium": 1, "low": 2}
    return sorted(matched, key=lambda rule: severity_order[rule.severity])
