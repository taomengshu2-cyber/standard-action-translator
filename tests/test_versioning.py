import json
import shutil
from pathlib import Path

from standard_action_translator.loaders import validate_standard_pack
from standard_action_translator.versioning import compare_packs, format_changelog


PROJECT_ROOT = Path(__file__).resolve().parents[1]
PACK = PROJECT_ROOT / "data" / "standard_packs" / "shapingba_learning_group_2026"


def test_validate_pack_after_copy(tmp_path):
    copied_pack = tmp_path / "copied_pack"
    shutil.copytree(PACK, copied_pack)

    pack = validate_standard_pack(copied_pack)

    assert pack.metadata.pack_id == "shapingba_learning_group_2026"


def test_diff_pack_detects_standard_change(tmp_path):
    old_pack = tmp_path / "old"
    new_pack = tmp_path / "new"
    shutil.copytree(PACK, old_pack)
    shutil.copytree(PACK, new_pack)

    standards_path = new_pack / "standards.json"
    standards = json.loads(standards_path.read_text(encoding="utf-8"))
    standards[6]["original_text"] = standards[6]["original_text"] + " 新增版本说明。"
    standards_path.write_text(json.dumps(standards, ensure_ascii=False, indent=2), encoding="utf-8")

    diff = compare_packs(old_pack, new_pack)
    changelog = format_changelog(diff)

    assert "B7 活动方案" in changelog
    assert "original_text" in changelog
