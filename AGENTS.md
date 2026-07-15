# AGENTS.md

This project's operating instructions live in **[`CLAUDE.md`](CLAUDE.md)** — the single source of
truth for orchestration, model routing, the write→grade→visual→schedule pipeline, and the saving
conventions.

- **Claude Code** reads `CLAUDE.md` natively.
- **opencode** loads it via `opencode.json` → `"instructions": ["CLAUDE.md"]`.

This file is a thin pointer so any AGENTS.md-aware tool finds the same guide. Do not duplicate
content here — edit `CLAUDE.md`.
