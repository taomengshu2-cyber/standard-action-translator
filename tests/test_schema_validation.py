from pathlib import Path

from standard_action_translator.loaders import validate_standard_pack


PROJECT_ROOT = Path(__file__).resolve().parents[1]
PACK = PROJECT_ROOT / "data" / "standard_packs" / "shapingba_learning_group_2026"
TEMPLATE_PACK = PROJECT_ROOT / "data" / "standard_packs" / "template_school_pack"


def test_sample_pack_schema_validation_passes():
    pack = validate_standard_pack(PACK)

    assert pack.metadata.version == "2026.0.1"


def test_template_pack_schema_validation_passes():
    pack = validate_standard_pack(TEMPLATE_PACK)

    assert pack.metadata.pack_id == "template_school_pack"
