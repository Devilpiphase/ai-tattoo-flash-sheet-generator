"""Render a planned sheet into a raster image.

Backends are pluggable. `diffusers` is the real one; `stub` produces a
deterministic placeholder grid so the pipeline is testable without a GPU
or model weights. The service only orchestrates — the adapter does the pixels.
"""

from __future__ import annotations

from typing import Any

from ai_tattoo_flash.adapters.gpu_backend import GpuBackend
from ai_tattoo_flash.models.sheet import FlashSheet
from ai_tattoo_flash.models.render import RenderedSheet
from ai_tattoo_flash.utils.errors import BackendError


class RenderService:
    def __init__(self, gpu: GpuBackend, render_config: dict[str, Any]) -> None:
        self._gpu = gpu
        self._cfg = render_config

    def render_sheet(self, sheet: FlashSheet, seed: int | None = None) -> RenderedSheet:
        backend = str(self._cfg.get("backend", "stub")).lower()
        steps = int(self._cfg.get("steps", 28))
        guidance = float(self._cfg.get("guidance", 6.5))
        effective_seed = seed if seed is not None else self._cfg.get("seed")

        try:
            if backend == "diffusers":
                return self._gpu.render(sheet, steps=steps, guidance=guidance, seed=effective_seed)
            if backend == "stub":
                return self._gpu.render_stub(sheet, seed=effective_seed)
        except Exception as exc:  # adapter surfaces a typed error; keep the chain
            raise BackendError(f"render backend {backend!r} failed: {exc}") from exc

        raise BackendError(f"unknown render backend: {backend!r}")