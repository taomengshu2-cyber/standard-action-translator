from pathlib import Path

from standard_action_translator.loaders import load_standard_pack


PROJECT_ROOT = Path(__file__).resolve().parents[1]
PACK = PROJECT_ROOT / "data" / "standard_packs" / "shapingba_learning_group_2026"


def test_load_standard_pack():
    pack = load_standard_pack(PACK)

    assert pack.metadata.pack_id == "shapingba_learning_group_2026"
    assert len(pack.standards) == 15
    assert pack.get_standard("B7").title == "活动方案"
