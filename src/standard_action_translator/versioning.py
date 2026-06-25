from __future__ import annotations

from pathlib import Path

from .loaders import load_standard_pack
from .models import StandardItem


def read_pack_version(pack_path: str | Path) -> str:
    return load_standard_pack(pack_path).metadata.version


def compare_packs(old_pack_path: str | Path, new_pack_path: str | Path) -> dict[str, list[str]]:
    old_pack = load_standard_pack(old_pack_path)
    new_pack = load_standard_pack(new_pack_path)

    old_standards = {standard.id: standard for standard in old_pack.standards}
    new_standards = {standard.id: standard for standard in new_pack.standards}

    added = sorted(set(new_standards) - set(old_standards))
    removed = sorted(set(old_standards) - set(new_standards))
    modified: list[str] = []

    for standard_id in sorted(set(old_standards) & set(new_standards)):
        changed_fields = changed_standard_fields(old_standards[standard_id], new_standards[standard_id])
        if changed_fields:
            title = new_standards[standard_id].title
            modified.append(f"{standard_id} {title}：{' / '.join(changed_fields)} 有变化")

    return {
        "added": added,
        "removed": removed,
        "modified": modified,
        "need_review": ["gap_rules", "action_templates", "examples"] if added or removed or modified else [],
    }


def changed_standard_fields(old: StandardItem, new: StandardItem) -> list[str]:
    fields = [
        "title",
        "category",
        "original_text",
        "plain_language_expectation",
        "key_requirements",
        "required_evidence",
        "related_document_types",
        "keywords",
    ]
    changed: list[str] = []
    for field in fields:
        if getattr(old, field) != getattr(new, field):
            changed.append(field)
    return changed


def format_changelog(diff: dict[str, list[str]]) -> str:
    lines = [
        "# 标准包差异报告",
        "",
        "## 新增指标",
        *format_items(diff["added"]),
        "",
        "## 删除指标",
        *format_items(diff["removed"]),
        "",
        "## 修改指标",
        *format_items(diff["modified"]),
        "",
        "## 需要同步检查",
        *format_items(diff["need_review"]),
    ]
    return "\n".join(lines) + "\n"


def format_items(items: list[str]) -> list[str]:
    if not items:
        return ["- 无"]
    return [f"- {item}" for item in items]
