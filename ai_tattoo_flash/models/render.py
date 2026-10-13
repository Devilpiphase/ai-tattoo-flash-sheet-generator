"""Rendered sheet payload — bytes out of a render backend, ready for export."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class RenderedSheet:
    width_px: int
    height_px: int
    png_bytes: bytes
    svg_text: str | None = None

    @property
    def size_bytes(self) -> int:
        return len(self.png_bytes)