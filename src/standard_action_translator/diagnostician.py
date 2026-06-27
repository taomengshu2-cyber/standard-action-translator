from __future__ import annotations

from pathlib import Path

from .action_generator import ActionGenerator, deduplicate
from .guardrails import Guardrails
from .interpreter import StandardInterpreter
from .loaders import load_standard_pack
from .models import DiagnosisResult, GapRule, StandardItem


def diagnose(
    text: str,
    standard_id: str,
    pack_path: str | Path,
    mode: str = "diagnose",
    positive_mode: str = "ask",
    positive_choices: str | None = None,
) -> DiagnosisResult:
    pack = load_standard_pack(pack_path)
    standard = pack.get_standard(standard_id)
    interpreter = StandardInterpreter()
    guardrails = Guardrails()

    matched_evidence = extract_matched_evidence(text, standard.required_evidence + standard.keywords)
    matched_rules = match_gap_rules(text, pack.rules_for(standard_id))
    is_strong_match = not matched_rules and bool(matched_evidence)
    matched_rule_ids = {rule.id for rule in matched_rules}
    action_templates = pack.actions_for(standard_id, matched_rule_ids)

    next_actions, materials_to_add = ActionGenerator().generate(action_templates)
    reusable_practices: list[str] = []

    diagnostic_questions = deduplicate(
        [question for rule in matched_rules for question in rule.diagnostic_questions]
    )
    main_gaps = [rule.gap_description for rule in matched_rules]

    if not matched_evidence:
        matched_evidence = ["暂未识别到与该标准直接对应的明确证据。"]
    if is_strong_match:
        matched_evidence = build_positive_evidence(text, standard, matched_evidence)
        main_gaps = build_positive_feedback(text, standard, matched_evidence)
        next_actions = build_transfer_actions(text, standard)
        materials_to_add = build_case_library_materials(text, standard)
        diagnostic_questions = build_case_reflection_questions(standard)
        reusable_practices = build_reusable_practices(standard, positive_choices)
    else:
        if matched_rules:
            main_gaps = build_contextual_gaps(text, matched_rules)
            next_actions = build_contextual_actions(text, matched_rules, next_actions)
            materials_to_add = build_contextual_materials(standard, materials_to_add)
        if not main_gaps:
            main_gaps = ["暂未触发具体差距规则。建议继续核对材料中的关键证据是否能直接回应该标准。"]
        if not next_actions:
            next_actions = ["对照标准逐项标注材料中已有证据，再检查是否缺少过程、结果或后续改进证据。"]
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
        is_strong_match=is_strong_match,
        positive_mode=positive_mode if positive_mode in {"ask", "no", "yes"} else "ask",
        positive_choices=positive_choices,
        reusable_practices=reusable_practices,
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
        has_expected_evidence = any(evidence in text for evidence in rule.missing_evidence)
        should_trigger_by_missing = bool(rule.missing_evidence) and not has_expected_evidence

        if has_avoid_phrase:
            matched.append(rule)
            continue

        if rule.missing_evidence:
            if should_trigger_by_missing and (not rule.trigger_keywords or has_trigger):
                matched.append(rule)
            continue

        if has_trigger:
            matched.append(rule)

    severity_order = {"high": 0, "medium": 1, "low": 2}
    return sorted(matched, key=lambda rule: severity_order[rule.severity])


def build_positive_feedback(text: str, standard: StandardItem, matched_evidence: list[str]) -> list[str]:
    if standard.id == "B6":
        feedback = []
        if has_any(text, ["实际研修与计划研修对比", "计划研修主题", "实际研修情况", "完成情况"]):
            feedback.append(
                "符合标准要求：材料用“计划研修—实际研修—完成情况”的方式回应了 B6 对照学期计划检视达成度的要求。"
            )
        if has_any(text, ["反思与不足", "不足", "偏差", "问题"]):
            feedback.append(
                "值得保留：材料单列反思与不足，说明总结不是只写成绩，而是在复盘真实运行中的问题。"
            )
        if has_any(text, ["下学期研修初步规划", "下学期规划", "下学期"]):
            feedback.append(
                "值得沉淀：材料把本学期反思连接到下学期研修规划，形成了“复盘—改进—再规划”的闭环。"
            )
        if feedback:
            return feedback

    evidence_summary = "、".join(extract_terms_from_evidence(matched_evidence)[:4])
    if evidence_summary:
        return [
            f"符合标准要求：材料已经呈现“{evidence_summary}”等关键证据，能看出对 {standard.id} {standard.title} 核心要求有回应。",
            "值得保留：材料不是只停留在结论表述，而是留下了可以继续追溯、复盘和迁移的证据线索。",
        ]
    return ["符合标准要求：材料已经回应了该指标的主要要求，后续重点是把有效做法沉淀成可迁移策略。"]


def build_positive_evidence(
    text: str, standard: StandardItem, matched_evidence: list[str]
) -> list[str]:
    if standard.id == "B6":
        evidence = []
        if has_any(text, ["实际研修与计划研修对比", "计划研修主题", "实际研修情况", "完成情况"]):
            evidence.append("材料设置了计划研修与实际研修对照表，能直接呈现任务达成情况。")
        if has_any(text, ["反思与不足", "不足"]):
            evidence.append("材料单列反思与不足，能看出对问题偏差有主动复盘。")
        if has_any(text, ["改进措施"]):
            evidence.append("材料写出了改进措施，具备从问题走向行动的基础。")
        if has_any(text, ["下学期研修初步规划", "下学期规划", "下学期"]):
            evidence.append("材料包含下学期研修规划，能把本学期总结延伸到下一轮改进。")
        if evidence:
            return evidence

    return matched_evidence[:8]


def build_transfer_actions(text: str, standard: StandardItem) -> list[str]:
    if standard.id == "B6":
        return [
            "把“计划研修主题—实际研修情况—完成情况”的对照表沉淀为学期总结模板。",
            "从反思与不足中提炼 2-3 个真实偏差，标注对应的改进动作和下学期安排。",
            "把下学期研修规划与本学期反思逐条对应，形成“本期问题—下期动作”的转化表。",
            "提炼这份总结的写作策略：先交代研修主线，再呈现过程证据，最后用对照表和规划形成闭环。",
        ]
    return [
        f"把材料中最能体现 {standard.id} {standard.title} 的做法提炼成 3 条可复用策略。",
        "为每条策略补一句“为什么有效”，说明它回应了哪一条标准要求。",
        "把关键证据截图、表格或片段保存为优秀案例库素材。",
    ]


def build_case_library_materials(text: str, standard: StandardItem) -> list[str]:
    if standard.id == "B6":
        return [
            "计划研修与实际研修对照表",
            "反思与不足部分",
            "改进措施与下学期研修规划",
            "能够说明研修主线和循证闭环的过程材料",
            "可复用的学期总结结构模板",
        ]
    return [
        "最能体现标准要求的局部片段",
        "对应的过程证据或成果证据",
        "可迁移策略说明",
        "不建议照抄的情境信息说明",
    ]


def build_case_reflection_questions(standard: StandardItem) -> list[str]:
    if standard.id == "B6":
        return [
            "这份总结最值得其他教研组学习的结构是什么？",
            "哪一处最能证明它做到了对照计划检视达成度？",
            "反思与下学期规划之间有没有一一对应关系？",
            "如果沉淀为优秀案例，应该提醒别人学结构、学证据，还是学表达方式？",
        ]
    return [
        f"这份材料最值得其他教研组学习的 {standard.title} 策略是什么？",
        "它为什么符合标准要求？",
        "哪些内容可以迁移，哪些内容只适用于本校情境？",
    ]


def extract_terms_from_evidence(evidence_items: list[str]) -> list[str]:
    terms: list[str] = []
    for item in evidence_items:
        if "“" in item and "”" in item:
            terms.append(item.split("“", 1)[1].split("”", 1)[0])
    return deduplicate(terms)


def has_any(text: str, terms: list[str]) -> bool:
    return any(term in text for term in terms)


def build_contextual_gaps(text: str, matched_rules: list[GapRule]) -> list[str]:
    gaps: list[str] = []
    for rule in matched_rules:
        context = find_rule_context(text, rule)
        if context:
            gaps.append(f"{rule.gap_description} 材料中的相关表述是：“{context}”。")
        elif rule.missing_evidence:
            evidence_hint = "、".join(rule.missing_evidence[:4])
            gaps.append(f"{rule.gap_description} 我在材料中暂未看到“{evidence_hint}”等关键证据。")
        else:
            gaps.append(rule.gap_description)
    return deduplicate(gaps)


def build_contextual_actions(
    text: str, matched_rules: list[GapRule], actions: list[str]
) -> list[str]:
    if not actions:
        return actions

    contexts = [find_rule_context(text, rule) for rule in matched_rules]
    contexts = [context for context in contexts if context]
    contextual_actions: list[str] = []
    for index, action in enumerate(actions):
        if index < len(contexts):
            contextual_actions.append(f"针对材料中“{contexts[index]}”这一处，{action}")
        else:
            contextual_actions.append(action)
    return contextual_actions


def build_contextual_materials(standard: StandardItem, materials: list[str]) -> list[str]:
    if not materials:
        return materials

    if standard.id == "B7":
        return [
            "优先补充“问题来源证据”：例如课堂观察记录、作业样本、质量监测数据或访谈摘录。优秀材料通常会先说明研修问题从哪里来，再进入活动流程设计。",
            "优先补充“证据分析环节”：在活动流程中写清教师共同分析哪份证据、分析什么、怎样从证据生成策略。",
            "优先补充“评价工具”：例如评价表、课堂观察表或成果达成标准。优秀材料通常会在活动前就说明评价维度，而不是活动后只写效果良好。",
            "优先补充“连续活动关系”：说明本次活动承接前一次的什么产出，又为下一次留下什么问题或材料。",
        ]

    result: list[str] = []
    for material in materials[:6]:
        result.append(
            f"补充“{material}”：优秀材料通常会说明它如何回应 {standard.id} {standard.title} 的标准要求，并把它和具体问题、过程或成效对应起来。"
        )
    return result


def find_rule_context(text: str, rule: GapRule) -> str | None:
    terms = rule.avoid_phrases + rule.trigger_keywords
    if not terms:
        terms = rule.missing_evidence

    paragraphs = split_text_units(text)
    for term in terms:
        for paragraph in paragraphs:
            if term and term in paragraph:
                return shorten(paragraph)
    return None


def split_text_units(text: str) -> list[str]:
    units: list[str] = []
    for raw_line in text.replace("\r\n", "\n").split("\n"):
        line = raw_line.strip().strip("|").strip()
        if not line or line.startswith("<!--"):
            continue
        if len(line) > 12:
            units.append(" ".join(line.split()))
    return units


def shorten(text: str, limit: int = 90) -> str:
    if len(text) <= limit:
        return text
    return text[: limit - 1] + "…"


def build_reusable_practices(standard: StandardItem, positive_choices: str | None) -> list[str]:
    if not positive_choices:
        return []

    choices = normalize_choices(positive_choices)
    if standard.id == "B6":
        practices: list[str] = []
        if choices.get("1") == "A":
            practices.append("可复用做法一：按“研修主线—过程证据—成果特色—反思改进—下期规划”组织总结，让读者看到一学期工作的完整闭环。")
        elif choices.get("1") == "B":
            practices.append("可复用做法一：用“计划研修—实际研修—完成情况”对照表复盘任务达成度，避免总结只停留在活动罗列。")
        else:
            practices.append("可复用做法一：把最有价值的总结结构提炼成固定栏目，方便下次继续使用。")

        if choices.get("2") == "A":
            practices.append("可复用做法二：保留计划与实际对照表，并在表中写清完成状态，让达成度证据一眼可见。")
        elif choices.get("2") == "B":
            practices.append("可复用做法二：把“反思与不足—改进措施—下学期规划”连在一起写，让问题能自然转化为下一轮行动。")
        else:
            practices.append("可复用做法二：选出最能证明达成度的证据位置，并说明它对应哪一项计划任务。")

        if choices.get("3") == "A":
            practices.append("可复用做法三：让每条不足都能在下学期规划中找到对应改进方向，形成持续改进链。")
        elif choices.get("3") == "B":
            practices.append("可复用做法三：把不足进一步对应到月份、任务或责任人，提升下学期规划的可执行性。")
        else:
            practices.append("可复用做法三：检查反思和规划之间的对应关系，把泛泛改进改成可执行安排。")
        return practices

    return [
        f"可复用做法一：提炼这份材料中最能回应 {standard.id} {standard.title} 的结构，并保留为模板。",
        "可复用做法二：把关键证据和标准要求一一对应，避免只展示结果、不说明依据。",
        "可复用做法三：标注哪些做法适合迁移，哪些内容需要结合本校情境调整。",
    ]


def normalize_choices(positive_choices: str) -> dict[str, str]:
    normalized = positive_choices.upper().replace("，", ",").replace("、", ",").replace("；", ",")
    result: dict[str, str] = {}
    for part in normalized.split(","):
        compact = part.strip().replace(" ", "")
        if len(compact) >= 2 and compact[0].isdigit():
            result[compact[0]] = compact[1]
    return result
