"""Sheet layout: N prompts -> a page of N cells with deterministic geometry.

The layout is pure math. No rendering, no IO. Given the same sheet config and
the same piece count it produces byte-identical geometry, which keeps sheet
snapshots stable in tests.
"""

from __future__ import annotations

from typing import Any

from ai_tattoo_flash.models.sheet import FlashCell, FlashSheet
from ai_tattoo_flash.models.style import StylePreset
from ai_tattoo_flash.utils.errors import ValidationError

_MM_PER_INCH = 25.4
_PAGE_SIZES_MM: dict[str, tuple[float, float]] = {
    "A4": (210.0, 297.0),
    "A3": (297.0, 420.0),
    "LETTER": (215.9, 279.4),
    "TABLOID": (279.4, 431.8),
}


class LayoutService:
    def __init__(self, sheet_config: dict[str, Any]) -> None:
        self._cfg = sheet_config

    def plan(self, prompts: list[str], preset: StylePreset) -> FlashSheet:
        page = str(self._cfg.get("page", "A3")).upper()
        if page not in _PAGE_SIZES_MM:
            raise ValidationError(f"unknown page size: {page!r} (have: {sorted(_PAGE_SIZES_MM)})")

        dpi = int(self._cfg.get("dpi", 300))
        columns = int(self._cfg.get("columns", 4))
        rows = int(self._cfg.get("rows", 3))
        gutter = float(self._cfg.get("gutter_mm", 6))
        margin = float(self._cfg.get("margin_mm", 18))

        capacity = columns * rows
        if len(prompts) > capacity:
            raise ValidationError(
                f"sheet fits {capacity} pieces ({columns}x{rows}); got {len(prompts)}"
            )

        page_w_mm, page_h_mm = _PAGE_SIZES_MM[page]
        cell_w_mm = (page_w_mm - 2 * margin - (columns - 1) * gutter) / columns
        cell_h_mm = (page_h_mm - 2 * margin - (rows - 1) * gutter) / rows

        cells: list[FlashCell] = []
        for index, prompt in enumerate(prompts):
            row, col = divmod(index, columns)
            x_mm = margin + col * (cell_w_mm + gutter)
            y_mm = margin + row * (cell_h_mm + gutter)
            cells.append(
                FlashCell(
                    index=index,
                    prompt=prompt,
                    x_mm=round(x_mm, 4),
                    y_mm=round(y_mm, 4),
                    w_mm=round(cell_w_mm, 4),
                    h_mm=round(cell_h_mm, 4),
                )
            )

        return FlashSheet(
            page=page,
            dpi=dpi,
            width_px=int(round(page_w_mm / _MM_PER_INCH * dpi)),
            height_px=int(round(page_h_mm / _MM_PER_INCH * dpi)),
            background=str(self._cfg.get("background", "#f4efe6")),
            ink=str(self._cfg.get("ink", "#111111")),
            label_style=str(self._cfg.get("label_style", "handscript")),
            style_key=preset.key,
            cells=tuple(cells),
        )