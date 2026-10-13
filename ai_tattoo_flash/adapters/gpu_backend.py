"""Render backend adapter.

`render` is the real path (torch + diffusers, CUDA on Windows). `render_stub`
draws a deterministic placeholder grid with Pillow so the pipeline runs
headless and in CI. Heavy imports are lazy — importing this module must not
pull torch into a machine that only wants the CLI's `presets` command.
"""

from __future__ import annotations

import io
from typing import Any

from PIL import Image, ImageDraw

from ai_tattoo_flash.models.render import RenderedSheet
from ai_tattoo_flash.models.sheet import FlashSheet
from ai_tattoo_flash.utils.errors import BackendError
from ai_tattoo_flash.utils.units import mm_to_px


class GpuBackend:
    def __init__(self, render_config: dict[str, Any]) -> None:
        self._cfg = render_config
        self._pipeline: Any = None

    def _ensure_pipeline(self) -> Any:
        if self._pipeline is not None:
            return self._pipeline
        try:
            import torch  # noqa: PLC0415
            from diffusers import StableDiffusionXLPipeline  # noqa: PLC0415
        except ImportError as exc:
            raise BackendError(
                "diffusers backend requires torch + diffusers; "
                "pip install -e '.[render]' on a CUDA-capable Windows box"
            ) from exc

        model_id = self._cfg.get("model_id", "tattooflash-xl-v2")
        device = self._cfg.get("device", "cuda")
        dtype = torch.float16 if device == "cuda" else torch.float32
        try:
            pipe = StableDiffusionXLPipeline.from_pretrained(model_id, torch_dtype=dtype)
            self._pipeline = pipe.to(device)
        except Exception as exc:
            raise BackendError(f"failed to load model {model_id!r}: {exc}") from exc
        return self._pipeline

    def render(
        self, sheet: FlashSheet, *, steps: int, guidance: float, seed: int | None
    ) -> RenderedSheet:
        import torch  # noqa: PLC0415

        pipe = self._ensure_pipeline()
        generator = None
        if seed is not None:
            generator = torch.Generator(device=self._cfg.get("device", "cuda")).manual_seed(seed)

        canvas = Image.new("RGB", (sheet.width_px, sheet.height_px), sheet.background)
        for cell in sheet.cells:
            w_px = mm_to_px(cell.w_mm, sheet.dpi)
            h_px = mm_to_px(cell.h_mm, sheet.dpi)
            result = pipe(
                prompt=cell.prompt,
                num_inference_steps=steps,
                guidance_scale=guidance,
                width=w_px,
                height=h_px,
                generator=generator,
            )
            piece = result.images[0].convert("RGB")
            canvas.paste(piece, (mm_to_px(cell.x_mm, sheet.dpi), mm_to_px(cell.y_mm, sheet.dpi)))

        buf = io.BytesIO()
        canvas.save(buf, format="PNG", dpi=(sheet.dpi, sheet.dpi))
        return RenderedSheet(width_px=sheet.width_px, height_px=sheet.height_px, png_bytes=buf.getvalue())

    def render_stub(self, sheet: FlashSheet, *, seed: int | None = None) -> RenderedSheet:
        """Deterministic placeholder grid. No GPU, no weights, no network."""
        canvas = Image.new("RGB", (sheet.width_px, sheet.height_px), sheet.background)
        draw = ImageDraw.Draw(canvas)
        for cell in sheet.cells:
            x = mm_to_px(cell.x_mm, sheet.dpi)
            y = mm_to_px(cell.y_mm, sheet.dpi)
            w = mm_to_px(cell.w_mm, sheet.dpi)
            h = mm_to_px(cell.h_mm, sheet.dpi)
            draw.rectangle([x, y, x + w, y + h], outline=sheet.ink, width=max(1, sheet.dpi // 150))
            draw.text((x + 8, y + 8), f"#{cell.index:02d}", fill=sheet.ink)

        buf = io.BytesIO()
        canvas.save(buf, format="PNG", dpi=(sheet.dpi, sheet.dpi))
        return RenderedSheet(width_px=sheet.width_px, height_px=sheet.height_px, png_bytes=buf.getvalue())