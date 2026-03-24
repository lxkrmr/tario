# ADR 0007: Add `tario env prune` as the standard full-reset command

## Status
Accepted

## Context
`tario env down` stops containers but keeps volumes by default. Removing volumes
requires the explicit `--volumes` flag. In practice, a full clean slate — no
containers, no volumes — is the most common intent before a fresh test run.

`tario env reset` was considered but rejected: "reset" implies restoring to a
known state, which is not what happens here.

## Decision
Add `tario env prune` as a dedicated command that always runs `docker compose
down --volumes`. It is the recommended path for obtaining a clean environment
before a test run.

`tario env down` remains unchanged for cases where keeping volumes is
intentional.

## Consequences
- One clear command for the full-reset path, named after a familiar Docker
  concept (`docker system prune`, `docker volume prune`).
- No breaking change to `tario env down`.
- `tario commands` and `tario describe` updated accordingly.
