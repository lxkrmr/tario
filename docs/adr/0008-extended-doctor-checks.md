# ADR 0008: Extend `tario doctor` with daemon and service checks

## Status
Accepted

## Context
`tario doctor` is the primary onboarding and recovery command. Its original
checks covered only static facts: Docker CLI in PATH, repo path exists, compose
files exist. Two common failure modes were not caught:

- The Docker daemon is not running. The CLI is present but every compose command
  fails immediately with a connection error.
- The service name configured in the profile does not exist in the compose
  files. This is silent until `tario test run` is executed.

Both issues cause confusing errors at run time rather than a clear message at
setup time.

## Decision
Add two checks to `tario doctor`:

1. **Docker daemon reachable** — run `docker info` and check the exit code.
   Fails with a clear message if the daemon is not running.

2. **Service name valid** — run `docker compose config --services` and verify
   that the configured service name is present in the output.
   Fails with a clear message listing the available services.

Both checks are added to `runner.py` as separate functions so they can be
tested and reused independently.

## Consequences
- Onboarding failures are caught earlier with actionable messages.
- `tario doctor` remains the single command to run when something feels wrong.
- Slightly slower doctor execution due to two additional subprocess calls.
