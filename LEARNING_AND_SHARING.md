# LEARNING_AND_SHARING

> Shipboard notes from agent shifts on `tario`.

---

<!-- INSERT NEW ENTRIES BELOW THIS LINE (newest first) -->

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
