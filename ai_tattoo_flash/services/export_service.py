"""Export a rendered sheet to disk via the filesystem adapter.

Owns the policy: output paths are confined to the configured output root.
The adapter owns the mechanics: writing bytes, creating parents.
"""

from __future__ import annotations

from pathlib import Path

from ai_tattoo_flash.adapters.fs_export import FSExportAdapter
from ai_tattoo_flash.models.render import RenderedSheet
from ai_tattoo_flash.utils.errors import ValidationError


class ExportService:
    def __init__(self, fs: FSExportAdapter) -> None:
        self._fs = fs

    def write_png(self, rendered: RenderedSheet, requested: Path) -> Path:
        target = self._fs.confine(requested)
        if target.suffix.lower() not in {".png", ".jpg", ".jpeg", ".webp"}:
            raise ValidationError(f"unsupported export format: {target.suffix!r}")
        self._fs.write_bytes(target, rendered.png_bytes)
        return target

    def write_svg(self, rendered: RenderedSheet, requested: Path) -> Path:
        if rendered.svg_text is None:
            raise ValidationError("rendered sheet has no SVG payload")
        target = self._fs.confine(requested.with_suffix(".svg"))
        self._fs.write_text(target, rendered.svg_text)
        return target