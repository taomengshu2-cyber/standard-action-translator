from __future__ import annotations

from .models import ActionTemplate


class ActionGenerator:
    def generate(self, templates: list[ActionTemplate]) -> tuple[list[str], list[str]]:
        actions: list[str] = []
        materials: list[str] = []

        for template in templates:
            actions.append(template.action_summary)
            actions.extend(template.action_steps)
            materials.extend(template.material_to_add)

            if template.micro_example:
                actions.append(f"可参考局部表达：{template.micro_example}")

        return deduplicate(actions), deduplicate(materials)


def deduplicate(items: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for item in items:
        normalized = item.strip()
        if normalized and normalized not in seen:
            seen.add(normalized)
            result.append(normalized)
    return result
