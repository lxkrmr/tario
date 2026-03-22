# ADR 0003: Configuration file is the single source of truth

## Status
Accepted

## Context
Test execution can be affected by implicit environment values.
This makes behavior hard to reason about for humans and agents.

## Decision
`tario` resolves execution settings only from profile configuration.
No environment-variable fallback is used for core runtime values.

## Consequences
- Deterministic behavior across sessions.
- Better reproducibility for agent execution.
- Users must configure profiles explicitly.
