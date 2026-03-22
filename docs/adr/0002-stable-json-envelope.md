# ADR 0002: Stable JSON envelope for automation

## Status
Accepted

## Context
Agents and CI automation need deterministic machine-readable output.
Raw command-line text is useful for humans but brittle for parsing.

## Decision
All automation-relevant commands support `--output json` with a stable envelope:
- `ok`
- `code`
- `message`
- `data`
- `next_commands`
- `meta`

## Consequences
- Better interoperability with coding agents.
- Safer contract evolution.
- Requires discipline when changing output fields.
