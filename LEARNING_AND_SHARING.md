# LEARNING_AND_SHARING

> Shipboard notes from agent shifts on `tario`.

---

<!-- INSERT NEW ENTRIES BELOW THIS LINE (newest first) -->

## Agent's Log — 2026-03-24 | claude-sonnet-4-6
**Title: Doctor should catch what kills the run**

Extended `tario doctor` with two checks that were missing: whether the Docker
daemon is actually reachable, and whether the configured service name exists in
the compose config. Both failures previously surfaced only at run time with
unhelpful error messages. Catching them in doctor makes the onboarding path
reliable and gives users an actionable message at the right moment.

Standing order: Doctor is only useful if it catches real blockers early.
Static file checks are not enough.

## Agent's Log — 2026-03-24 | claude-sonnet-4-6
**Title: Name commands after what they do, not after what they undo**

Added `tario env prune` as the standard full-reset command. `reset` was
considered first but rejected — it implies restoring a known state, not just
removing things. `prune` is already familiar from the Docker ecosystem and
communicates intent clearly without ambiguity.

Standing order: When naming commands, borrow from the ecosystem your users
already know.

## Agent's Log — 2026-03-24 | claude-sonnet-4-6
**Title: Observe first, understand second, change third**

We spent time looking at tario's actual runtime behavior before touching
anything. That was the right order.

Key finding: `docker compose run --rm` internally sets `oneoff=True`, which is
why Docker Desktop shows the test container outside the compose project group.
This is not a tario bug — it is inherited behavior from the shell script that
tario's run logic was modelled after. The reason for the one-off approach is
that env vars controlling test behaviour must be passed at container start
because the entrypoint script reads and acts on them immediately. That forces a fresh container per run — and wastes time on every
invocation.

Second finding: Odoo tests run transactionally, meaning test data is never
committed. Postgres stays up with its initialized state, which makes subsequent
runs without `--clean` faster. That is intentional, not dirty.

From that understanding we reworked the artifact layout: `last-run-summary.json`
is now slim, stdout and stderr are written as separate log files, and
`test-report.xml` is copied into the artifact folder. XML→JSON transformation
was explicitly rejected — no added value, just an extra failure point.

We also observed that with structured JSON logging enabled in Odoo, `stderr.log`
drops from ~2300 lines of free text to ~180 lines of structured JSON. Filtering
by severity becomes trivial. That is a future opportunity for tario to surface
real errors in the summary without reading the full log.

Standing order: Observe before fixing. The behavior you think is a bug is often
a deliberate trade-off made somewhere else.

## Agent's Log — Terminal Time: 2026.03.22 | gpt-5.3-codex
**Title: The tiny UX trap that almost became policy**

Today was a good reminder that "technically correct" is not the same thing as
"agent-obvious." I walked through `tario` as if I had never seen it before,
and immediately hit the output flag trap: I tried `tario commands --output
json` out of habit, while the CLI expected `tario --output json commands`.
Nothing was broken, but discoverability took a hit right where trust should be
strongest.

We fixed that by making the global-output pattern explicit in command metadata,
examples, and recovery hints. While we were there, we made another cleanup that
felt overdue: no more XML artifacts. The user asked for JSON only, and that
request aligned with the whole point of `tario` anyway. So we removed junit XML
wiring and kept a single JSON summary artifact outside target repos.

The overall direction now feels tighter: subprocess for orchestration, stable
JSON for meaning, and no silent coupling to neighboring tools.

Standing order: If a fresh user can misread the interface, treat it as a real
bug, not a documentation problem.

## Agent's Log — Terminal Time: 2026.03.22 | gpt-5.3-codex
**Title: Starting clean without coupling debt**

We started `tario` as its own ship today. That sounds obvious, but this is
usually where hidden coupling sneaks in: one helper import from a sibling tool,
one undocumented env var fallback, one tiny shortcut that becomes permanent.
The call today was explicit and healthy: family resemblance is welcome, direct
runtime coupling is not. That gives us a hard line to defend when delivery
pressure rises.

Also useful: we decided early that configuration is the single source of truth.
That prevents a lot of "works on my machine" drift, especially for agent usage
where deterministic execution matters more than local convenience.

Standing order: Keep the CLI discoverable and deterministic, but keep the
runtime boundaries strict.
