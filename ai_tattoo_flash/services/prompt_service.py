"""Prompt expansion: base prompt + style preset -> N per-piece prompts.

Deterministic given a seed. Preset motifs are sampled without replacement per
sheet so a 12-piece sheet never repeats a motif twice.
"""

from __future__ import annotations

import random
from pathlib import Path
from typing import Any

import yaml

from ai_tattoo_flash.models.style import StylePreset
from ai_tattoo_flash.utils.errors import ValidationError


class PromptService:
    def __init__(self, preset_file: str | Path) -> None:
        self._preset_path = Path(preset_file)
        self._cache: dict[str, StylePreset] | None = None

    def _load_all(self) -> dict[str, StylePreset]:
        if self._cache is None:
            if not self._preset_path.exists():
                raise ValidationError(f"preset file not found: {self._preset_path}")
            raw = yaml.safe_load(self._preset_path.read_text(encoding="utf-8")) or {}
            self._cache = {key: StylePreset.from_dict(key, val) for key, val in raw.items()}
        return self._cache

    def list_presets(self) -> dict[str, str]:
        return {key: preset.label for key, preset in self._load_all().items()}

    def load_preset(self, key: str) -> StylePreset:
        presets = self._load_all()
        if key not in presets:
            raise ValidationError(f"unknown style preset: {key!r} (have: {sorted(presets)})")
        return presets[key]

    def expand(self, base: str, preset: StylePreset, count: int) -> list[str]:
        rng = random.Random(f"{base}|{preset.key}|{count}")
        pool = list(preset.motifs)
        rng.shuffle(pool)
        motifs = [pool[i % len(pool)] for i in range(count)] if pool else [""] * count
        return [self._compose(base, preset, motif) for motif in motifs]

    @staticmethod
    def _compose(base: str, preset: StylePreset, motif: str) -> str:
        parts: list[str] = [base.strip()]
        if motif:
            parts.append(motif)
        parts.append(f"{preset.linework} linework")
        parts.append(f"{preset.shading} shading")
        if preset.palette:
            parts.append("palette: " + ", ".join(preset.palette))
        return ", ".join(parts)

    def negative_prompt(self, preset: StylePreset) -> str:
        return preset.negative

    def describe(self, preset: StylePreset) -> dict[str, Any]:
        return {
            "key": preset.key,
            "label": preset.label,
            "motifs": preset.motifs,
            "palette": preset.palette,
        }