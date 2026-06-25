from __future__ import annotations

from typing import Protocol


class LLMProvider(Protocol):
    def complete(self, prompt: str) -> str:
        """Return a model completion for future LLM-backed workflows."""


class RuleBasedProvider:
    def complete(self, prompt: str) -> str:
        return ""
