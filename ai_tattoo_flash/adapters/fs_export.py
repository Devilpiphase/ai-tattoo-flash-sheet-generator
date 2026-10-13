"""Filesystem export adapter.

Confines every write to a configured output root so a hostile or fat-fingered
`--out ../../Windows/System32/x.png` cannot escape. Paths are resolved and
checked with `Path.relative_to`.
"""

from __future__ import annotations

from pathlib import Path

from ai_tattoo_flash.utils.errors import ValidationError


class FSExportAdapter:
    def __init__(self, output_root: str | Path) -> None:
        self._root = Path(output_root).resolve()
        self._root.mkdir(parents=True, exist_ok=True)

    @property
    def root(self) -> Path:
        return self._root

    def confine(self, requested: Path) -> Path:
        candidate = (self._root / requested).resolve() if not requested.is_absolute() else requested.resolve()
        try:
            candidate.relative_to(self._root)
        except ValueError as exc:
            raise ValidationError(
                f"refusing to write outside output root {self._root}: {candidate}"
            ) from exc
        return candidate

    def write_bytes(self, target: Path, payload: bytes) -> None:
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(payload)

    def write_text(self, target: Path, payload: str) -> None:
        target.parent.mkdir(parents=True, exist_ok