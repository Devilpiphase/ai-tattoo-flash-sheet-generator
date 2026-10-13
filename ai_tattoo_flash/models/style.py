"""Style preset model."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from ai_tattoo_flash.utils.errors import ValidationError


@dataclass(frozen=True)
class StylePreset:
    key: str
    label: str
    palette: tuple[str, ...]
    linework: str
    shading: str
    motifs: tuple[str, ...]
    negative: str

    @classmethod
    def from_dict(cls, key: str, raw: dict[str, Any]) -> "StylePreset":
        try:
            return cls(
                key=key,
                label=str(raw["label"]),
                palette=tuple(str(c) for c in raw.get("palette", [])),
                linework=str(raw["linework"]),
                shading=str(raw["shading"]),
                motifs=tuple(str(m) for m in raw.get("motifs", [])),
                negative=str(raw.get("negative", "")),
            )
        except KeyError as exc:
            raise ValidationError(f"preset {key!r} missing required field: {exc}") from exc