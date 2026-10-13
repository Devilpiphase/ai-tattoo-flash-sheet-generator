"""Dependency container. Wires adapters into services; services into handlers.

Kept deliberately dumb — a dict of singletons with lazy construction. No DI
framework. If a service needs an adapter, it asks the container at call time,
not at import time, so tests can swap fakes.
"""

from __future__ import annotations

from typing import Any, Callable

from ai_tattoo_flash.adapters.fs_export import FSExportAdapter
from ai_tattoo_flash.adapters.gpu_backend import GpuBackend
from ai_tattoo_flash.adapters.prompt_llm import PromptLlmAdapter
from ai_tattoo_flash.services.export_service import ExportService
from ai_tattoo_flash.services.layout_service import LayoutService
from ai_tattoo_flash.services.prompt_service import PromptService
from ai_tattoo_flash.services.render_service import RenderService


class Container:
    """Lazy singleton registry. Thread-safe enough for a single-user desktop app."""

    def __init__(self, config: dict[str, Any]) -> None:
        self._config = config
        self._built: dict[str, Any] = {}
        self._factories: dict[str, Callable[[], Any]] = {
            "gpu": lambda: GpuBackend(self._config["render"]),
            "llm": lambda: PromptLlmAdapter(self._config.get("bridge", {})),
            "fs": lambda: FSExportAdapter(self._config["app"]["output_root"]),
            "prompt_service": lambda: PromptService(self._config["styles"]["preset_file"]),
            "layout_service": lambda: LayoutService(self._config["sheet"]),
            "render_service": lambda: RenderService(self.resolve("gpu"), self._config["render"]),
            "export_service": lambda: ExportService(self.resolve("fs")),
        }

    def resolve(self, key: str) -> Any:
        if key not in self._built:
            factory = self._factories.get(key)
            if factory is None:
                raise KeyError(f"unknown component: {key!r}")
            self._built[key] = factory()
        return self._built[key]

    def override(self, key: str, instance: Any) -> None:
        """Test hook: inject a fake in place of a real component."""
        self._built[key] = instance