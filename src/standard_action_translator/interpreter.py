from __future__ import annotations

from .models import StandardItem


class StandardInterpreter:
    def explain(self, standard: StandardItem) -> str:
        requirements = "；".join(standard.key_requirements)
        return f"{standard.plain_language_expectation} 核心要求包括：{requirements}。"

    def plain_expectation(self, standard: StandardItem) -> str:
        return standard.plain_language_expectation
