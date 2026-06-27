from __future__ import annotations


SCORING_RISK_KEYWORDS = [
    "给我打分",
    "帮我评分",
    "能得多少分",
    "排名",
    "评为优秀吗",
]

GHOSTWRITING_RISK_KEYWORDS = [
    "直接帮我写一份",
    "生成完整计划",
    "生成完整总结",
    "生成完整活动方案",
    "你替我写好",
]

SCORING_NOTE = "我不能替代评委进行评分或排名，但可以帮你对照标准查看哪些地方已经体现、哪些地方还需要补强。"

GHOSTWRITING_NOTE = "我不能替你生成完整材料，但可以提供结构框架、诊断问题、局部示例和下一步修改动作。"

VAGUE_PHRASES = [
    "进一步加强",
    "持续优化",
    "全面提升",
    "不断完善",
]


class Guardrails:
    def check_input(self, text: str) -> list[str]:
        notes: list[str] = []
        if any(keyword in text for keyword in SCORING_RISK_KEYWORDS):
            notes.append(SCORING_NOTE)
        if any(keyword in text for keyword in GHOSTWRITING_RISK_KEYWORDS):
            notes.append(GHOSTWRITING_NOTE)
        notes.append("本工具不直接评分，不替你生成完整材料。以上建议用于帮助你理解标准、发现差距，真正的修改和落地仍需要组内教师一起努力。")
        return notes

    def remove_vague_phrases(self, items: list[str]) -> list[str]:
        cleaned: list[str] = []
        for item in items:
            updated = item
            for phrase in VAGUE_PHRASES:
                updated = updated.replace(phrase, "写成可观察、可提交、可复盘的具体动作")
            cleaned.append(updated)
        return cleaned

    def assert_no_scores(self, output: str) -> None:
        risky_score_tokens = ["90分", "优秀等级", "排名第"]
        if any(token in output for token in risky_score_tokens):
            raise ValueError("output contains scoring language")
