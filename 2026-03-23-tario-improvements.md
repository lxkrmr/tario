# Tario – Improvement Proposals

## Context
During repeated local test runs with `tario test run` it was observed that
stale data in volumes can cause unexpected side effects between runs.

## Improvement Proposal

### `tario env down` should remove volumes by default
Currently volumes must be removed explicitly via `--volumes`.

**Problem:**
- In test environments, persisted data from previous runs is usually unwanted.
- This leads to hard-to-trace flaky behaviour between runs.

**Proposal:**
- Either:
  1. `tario env down` removes volumes by default
- Or (if breaking change is undesirable):
  2. A new explicit command such as `tario env reset` (`down --volumes`) as the
     recommended standard path for resetting test state.

## Acceptance Criteria
- A standard reset path removes both containers and their associated volumes.
- Documentation makes clear which command reliably produces a fresh test state.
- Fewer stale-data side effects between test runs.
