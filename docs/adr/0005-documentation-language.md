# ADR 0005: All documentation is written in English

## Status
Accepted

## Context
`tario` is a standalone CLI tool maintained by a team that communicates in
multiple languages. Documentation includes ADRs, README, CONTRIBUTING,
LEARNING_AND_SHARING, and inline code comments. Coding agents also read and
write these files during development sessions.

## Decision
All documentation and prose files in this repository are written in English.
This includes ADRs, markdown files, code comments, and agent log entries in
`LEARNING_AND_SHARING.md`.

## Consequences
- Consistent language across all project files.
- Agents operating in any language produce English output when writing docs.
- No ambiguity about which language to use when adding new content.
