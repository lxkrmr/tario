# LEARNING_AND_SHARING

> Shipboard notes from agent shifts on `tario`.

---

<!-- INSERT NEW ENTRIES BELOW THIS LINE (newest first) -->

## Agent's Log — Terminal Time: 2026.03.22 | <model-name>
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
