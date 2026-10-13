"""Typer CLI. Thin — parses args, resolves services, delegates, prints result."""

from __future__ import annotations

import json
from pathlib import Path

import typer
from rich.console import Console

from ai_tattoo_flash.bootstrap.container import Container
from ai_tattoo_flash.handlers.generate_handler import GenerateRequest, handle_generate
from ai_tattoo_flash.utils.config import load_config

app = typer.Typer(add_completion=False, help="AI tattoo flash sheet generator")
console = Console()


@app.command()
def generate(
    prompt: str = typer.Option(..., "--prompt", "-p", help="Base design prompt"),
    style: str = typer.Option("irezumi", "--style", "-s", help="Preset key from presets.yaml"),
    count: int = typer.Option(12, "--count", "-n", help="Number of flash pieces"),
    out: Path = typer.Option(Path("outputs/sheet.png"), "--out", "-o"),
    config: Path = typer.Option(Path("config/default.yaml"), "--config", "-c"),
    seed: int | None = typer.Option(None, "--seed"),
) -> None:
    """Generate a flash sheet PNG from a prompt + style preset."""
    cfg = load_config(config)
    container = Container(cfg)
    req = GenerateRequest(prompt=prompt, style=style, count=count, out=out, seed=seed)
    result = handle_generate(req, container)
    console.print(f"[bold green]wrote[/] {result.output_path} ({result.pieces} pieces)")


@app.command()
def presets(
    config: Path = typer.Option(Path("config/default.yaml"), "--config", "-c"),
) -> None:
    """List available style presets."""
    cfg = load_config(config)
    container = Container(cfg)
    svc = container.resolve("prompt_service")
    console.print_json(json.dumps(svc.list_presets()))


def main() -> None:
    app()


if __name__ == "__main__":
    main()