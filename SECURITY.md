# Security Policy

## Supported versions

| Version | Supported |
|---------|-----------|
| 0.4.x   | yes       |
| 0.3.x   | security fixes only |
| < 0.3   | no        |

## Reporting a vulnerability

Email `security@ai-tattoo-flash.dev` with:

- affected version (`python -m ai_tattoo_flash.bootstrap.cli --version`)
- a minimal repro (prompt, style, config)
- whether it's a local-only issue or reachable via the optional HTTP bridge

We aim to acknowledge within 72 hours.

## Threat model

This is a **local desktop tool**. It reads prompts, writes PNG/SVG flash sheets,
and optionally calls an external image model. The interesting attack surface:

1. **Prompt injection via reference images** — EXIF / embedded text that reaches
   the prompt builder. Sanitized in `utils/sanitize.py`.
2. **Path traversal on export** — user-supplied `--out` paths are normalized and
   confined to the configured output root in `adapters/fs_export.py`.
3. **Model weight loading** — `.safetensors` only by default; `.ckpt` loading is
   gated behind `ALLOW_UNSAFE_CKPT=1` because pickle deserialization is code
   execution.
4. **HTTP bridge** — disabled by default. If enabled, it binds to `127.0.0.1`
   and requires a bearer token from `config/secrets.yaml`.

## Out of scope

- Content of generated art. You are responsible for what you ink.
- Third-party model licenses.
- Anything requiring physical access to an unlocked workstation.