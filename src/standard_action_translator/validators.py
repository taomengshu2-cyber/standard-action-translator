from __future__ import annotations

from pathlib import Path

from .loaders import load_standard_pack
from .models import StandardPack


def validate_pack(pack_path: str | Path) -> StandardPack:
    return load_standard_pack(pack_path)
