# ADR 0001: Keep `tario` as a standalone tool

## Status
Accepted

## Context
The test workflow already exists in repository-local shell scripts.
We want a globally installable CLI with deterministic, agent-friendly output.

## Decision
Build `tario` as a separate repository and package.
`tario` targets repositories through profile configuration.
`tario` does not import or depend on sibling tools.

## Consequences
- Clear ownership and versioning.
- Easy global installation via `uv tool install`.
- No runtime coupling to other internal CLIs.
- Slightly more setup effort for profile configuration.
