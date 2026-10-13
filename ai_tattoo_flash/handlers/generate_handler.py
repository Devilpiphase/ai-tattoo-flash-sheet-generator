"""Handler for a single flash sheet generation request.

No business logic lives here. It validates the request shape, calls the
prompt/layout/render/export services in order, and returns a result record.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

from ai_tattoo_flash.models.sheet import FlashSheet
from ai_tattoo_flash.utils.errors import ValidationError

if TYPE_CHECKING:
    from ai_tattoo_flash.bootstrap.container import Container


@dataclass(frozen=True)
class GenerateRequest:
    prompt: str
    style: str
    count: int
    out: Path
    seed: int | None = None


@dataclass(frozen=True)
class GenerateResult:
    output_path: Path
    pieces: int
    style: str


def handle_generate(req: GenerateRequest, container: "Container") -> GenerateResult:
    if not req.prompt.strip():
        raise ValidationError("prompt must not be empty")
    if req.count < 1 or req.count > 64:
        raise ValidationError("count must be between 1 and 64")

    prompt_svc = container.resolve("prompt_service")
    layout_svc = container.resolve("layout_service")
    render_svc = container.resolve("render_service")
    export_svc = container.resolve("export_service")

    preset = prompt_svc.load_preset(req.style)  # raises ValidationError if unknown
    prompts = prompt_svc.expand(req.prompt, preset, req.count)

    sheet: FlashSheet = layout_svc.plan(prompts, preset)
    rendered = render_svc.render_sheet(sheet, seed=req.seed)
    output_path = export_svc.write_png(rendered, req.out)

    return GenerateResult(output_path=output_path, pieces=len(prompts), style=req.style)