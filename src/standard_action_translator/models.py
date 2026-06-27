from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


GapType = Literal[
    "understanding_gap",
    "behavior_gap",
    "structure_gap",
    "evidence_gap",
    "evaluation_gap",
]

Severity = Literal["low", "medium", "high"]

ActionType = Literal[
    "add_evidence",
    "redesign_process",
    "clarify_goal",
    "add_evaluation_tool",
    "align_plan",
    "summarize_reflection",
]


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class StandardPackMetadata(StrictModel):
    pack_id: str
    name: str
    version: str
    region_or_school: str
    description: str
    created_at: str
    updated_at: str
    applicable_users: list[str]
    supported_document_types: list[str]


class StandardItem(StrictModel):
    id: str = Field(..., min_length=1)
    title: str
    category: str
    original_text: str
    plain_language_expectation: str
    key_requirements: list[str]
    required_evidence: list[str]
    related_document_types: list[str]
    keywords: list[str]
    version: str

    @field_validator("key_requirements", "required_evidence", "keywords")
    @classmethod
    def require_non_empty_list(cls, value: list[str]) -> list[str]:
        if not value:
            raise ValueError("list must not be empty")
        return value


class GapRule(StrictModel):
    id: str
    standard_id: str
    gap_type: GapType
    gap_description: str
    trigger_keywords: list[str]
    missing_evidence: list[str]
    diagnostic_questions: list[str]
    severity: Severity
    avoid_phrases: list[str] = []


class ActionTemplate(StrictModel):
    id: str
    standard_id: str
    gap_rule_id: str
    action_type: ActionType
    action_summary: str
    action_steps: list[str]
    material_to_add: list[str]
    micro_example: str | None = None
    output_constraints: list[str]

    @field_validator("micro_example")
    @classmethod
    def micro_example_must_stay_short(cls, value: str | None) -> str | None:
        if value and len(value) > 150:
            raise ValueError("micro_example must not exceed 150 Chinese characters")
        return value


class StandardPack(StrictModel):
    metadata: StandardPackMetadata
    standards: list[StandardItem]
    gap_rules: list[GapRule]
    action_templates: list[ActionTemplate]
    examples: list[dict] = []

    def get_standard(self, standard_id: str) -> StandardItem:
        for standard in self.standards:
            if standard.id == standard_id:
                return standard
        raise KeyError(f"standard not found: {standard_id}")

    def rules_for(self, standard_id: str) -> list[GapRule]:
        return [rule for rule in self.gap_rules if rule.standard_id == standard_id]

    def actions_for(self, standard_id: str, gap_rule_ids: set[str]) -> list[ActionTemplate]:
        return [
            action
            for action in self.action_templates
            if action.standard_id == standard_id and action.gap_rule_id in gap_rule_ids
        ]


class DiagnosisResult(StrictModel):
    standard_id: str
    standard_title: str
    expectation: str
    matched_evidence: list[str]
    main_gaps: list[str]
    diagnostic_questions: list[str]
    next_actions: list[str]
    materials_to_add: list[str]
    guardrail_notes: list[str]
    is_strong_match: bool = False
    positive_mode: Literal["ask", "no", "yes"] = "ask"
    positive_choices: str | None = None
    reusable_practices: list[str] = []
