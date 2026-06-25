from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from pydantic import ValidationError

from .models import ActionTemplate, GapRule, StandardItem, StandardPack, StandardPackMetadata


PACK_FILES = {
    "metadata": "metadata.json",
    "standards": "standards.json",
    "gap_rules": "gap_rules.json",
    "action_templates": "action_templates.json",
}


class StandardPackError(ValueError):
    pass


def read_json(path: str | Path) -> Any:
    file_path = Path(path)
    try:
        with file_path.open("r", encoding="utf-8") as file:
            return json.load(file)
    except FileNotFoundError as exc:
        raise StandardPackError(f"missing file: {file_path}") from exc
    except json.JSONDecodeError as exc:
        raise StandardPackError(f"invalid JSON in {file_path}: {exc}") from exc


def load_standard_pack(pack_path: str | Path) -> StandardPack:
    root = Path(pack_path)
    try:
        metadata = StandardPackMetadata.model_validate(read_json(root / PACK_FILES["metadata"]))
        standards = [
            StandardItem.model_validate(item)
            for item in read_json(root / PACK_FILES["standards"])
        ]
        gap_rules = [
            GapRule.model_validate(item)
            for item in read_json(root / PACK_FILES["gap_rules"])
        ]
        action_templates = [
            ActionTemplate.model_validate(item)
            for item in read_json(root / PACK_FILES["action_templates"])
        ]
        examples_path = root / "examples.json"
        examples = read_json(examples_path) if examples_path.exists() else []
        pack = StandardPack(
            metadata=metadata,
            standards=standards,
            gap_rules=gap_rules,
            action_templates=action_templates,
            examples=examples,
        )
    except ValidationError as exc:
        raise StandardPackError(str(exc)) from exc

    validate_pack_integrity(pack)
    return pack


def validate_pack_integrity(pack: StandardPack) -> None:
    standard_ids = {standard.id for standard in pack.standards}
    if len(standard_ids) != len(pack.standards):
        raise StandardPackError("duplicate standard id found")

    rule_ids = {rule.id for rule in pack.gap_rules}
    if len(rule_ids) != len(pack.gap_rules):
        raise StandardPackError("duplicate gap rule id found")

    for rule in pack.gap_rules:
        if rule.standard_id not in standard_ids:
            raise StandardPackError(f"gap rule {rule.id} references missing standard {rule.standard_id}")

    for action in pack.action_templates:
        if action.standard_id not in standard_ids:
            raise StandardPackError(
                f"action template {action.id} references missing standard {action.standard_id}"
            )
        if action.gap_rule_id not in rule_ids:
            raise StandardPackError(
                f"action template {action.id} references missing gap rule {action.gap_rule_id}"
            )


def validate_standard_pack(pack_path: str | Path) -> StandardPack:
    return load_standard_pack(pack_path)
