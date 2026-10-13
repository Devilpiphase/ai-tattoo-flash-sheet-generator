# Contributing to ai-tattoo-flash-sheet-generator

Thanks for wanting to put ink on the repo. This project generates tattoo flash
sheets — grids of stylized tattoo designs — from text prompts, reference
sketches, and style presets. It is a Windows-first desktop tool built in Python
with a thin PySide6 shell over a service-oriented core.

## Repo layout

```
ai_tattoo_flash/
  bootstrap/     entry point, DI container, CLI
  handlers/      thin request handlers (no business logic)
  services/      business logic: layout, prompt, render, export
  models/        dataclasses + ORM-ish records
  adapters/      platform + external IO (GPU, filesystem, LLM backends)
  utils/         small pure helpers
config/          YAML defaults + presets
tests/           pytest suite
```

## Dev setup (Windows, Python 3.12+)

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
pip install -e .
```

CUDA users: install a matching `torch` wheel first
(`pip install torch --index-url https://download.pytorch.org/whl/cu124`),
then install the rest.

## Running

```powershell
python -m ai_tattoo_flash.bootstrap.app --config config/default.yaml
```

Headless batch generation:

```powershell
python -m ai_tattoo_flash.bootstrap.cli generate ^
  --prompt "japanese blackwork koi, heavy linework" ^
  --style irezumi ^
  --count 12 ^
  --out outputs/koi_sheet.png
```

## Tests

```powershell
pytest -q
ruff check .
mypy ai_tattoo_flash
```

## Style

- `ruff` for lint + format, line length 100.
- Type hints everywhere. `from __future__ import annotations` at the top of every module.
- Handlers stay thin: parse, validate, delegate to a service, return.
- No business logic in adapters. Adapters talk to the outside world; services decide.

## Pull requests

- One concern per PR.
- Add a test for any new service or adapter.
- Update `config/presets.yaml` if you add a style preset.
- Don't commit generated flash sheets or model weights.

## Community vocab

We use the community's real words — flash sheet, stencil, linework, blackwork,
irezumi, neo-traditional, dotwork, script, sleeve panel. Don't sanitize them.