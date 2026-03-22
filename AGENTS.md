# AGENTS.md

Workflow guide for coding agents working on `tario`.

## Purpose
- Build `tario` as a small, deterministic, agent-friendly CLI for test execution through Docker Compose.
- Keep CLI behavior discoverable without requiring Markdown docs.

## Product Rules
- Product name is `tario`.
- Keep KISS discipline: one clear path beats many optional paths.
- Configuration file is the single source of truth.
- Avoid hidden environment-variable fallback behavior.
- Keep `tario` fully standalone from other tools.
- Do not couple runtime behavior to `otto` or `indoo`.

## CLI UX
- `tario doctor` is the primary onboarding and recovery command.
- Help text must be enough to discover normal usage.
- Commands must emit deterministic output.
- Automation-relevant commands must support `--output json`.
- JSON envelope must stay stable:
  - `ok`, `code`, `message`, `data`, `next_commands`, `meta`

## Command quality checklist
- Deterministic text output
- Stable JSON output contract
- Explicit error codes + mapped exit codes
- `--dry-run` for mutating commands when applicable
- `tario commands` and `tario describe` remain accurate
- Tests cover success and failure paths

## Repository workflow
- Use `uv` for setup and execution.
- Global usage target: `uv tool install ...`.
- Local development: `uv sync --group dev` and `uv run ...`.
- Keep changes small, readable, and logically scoped.

## Validation checklist
- `uv run tario --help`
- `uv run tario commands --output json`
- `uv run ruff check .`
- `uv run pytest -q`

## Commit style
- Use Conventional Commits.
- Keep commit scope focused and small.

## Agent Identity & Collaboration Log
- Maintain `LEARNING_AND_SHARING.md` in the project root.
- Add an entry for notable lessons, mistakes, or process improvements.
- New entries must be prepended directly below the insertion marker.
