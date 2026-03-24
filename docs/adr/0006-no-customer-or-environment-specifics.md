# ADR 0006: No customer names or environment-specific details in repository files

## Status
Accepted

## Context
`tario` is a generic tool designed to work with any Docker Compose-based Odoo
project. During development sessions, agents and developers naturally observe
concrete details such as customer project names, local file paths, and
machine-specific configuration. There is a risk that these details leak into
documentation, log entries, ADRs, or code comments.

## Decision
Repository files must not contain:
- Customer or project names (e.g. names of the linked target repository or
  organisation).
- Absolute paths tied to a specific machine or user account.
- Any other detail that would reveal which customer or environment tario is
  being used with.

When examples are needed, use generic placeholders such as `path-to-repo`,
`my-project`, or `~/.config/tario/...`.

## Consequences
- The repository stays safe to share, publish, or hand off without information
  leakage.
- Agents must apply this rule when writing ADRs, log entries, and comments.
- Violations found in existing files should be corrected as part of normal
  housekeeping.
