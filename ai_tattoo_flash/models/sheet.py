"""Sheet geometry models."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class FlashCell:
    index: int
    prompt: str
    x_mm: float
    y_mm: float
    w_mm: float
    h_mm: float


@dataclass(frozen=True)
class FlashSheet:
    page: str
    dpi: int
    width_px: int
    height_px: int
    background: str
    ink: str
    label_style: str
    style_key: str
    cells: tuple[FlashCell, ...]

    @property
    def piece_count(self) -> int:
        return len(self.cells)