# tario

`tario` is an agent-friendly CLI to run Odoo addon tests through Docker Compose.

The CLI is the primary interface for both humans and agents.
You should be able to discover workflows from the CLI alone.

## Install

Install globally from GitHub:

```bash
uv tool install git+https://github.com/lxkrmr/tario.git
```

Reinstall after updates:

```bash
uv tool install --reinstall git+https://github.com/lxkrmr/tario.git
```

Local development setup:

```bash
uv sync --group dev
uv run tario --help
```

## Quickstart

1. Add a profile:

```bash
tario profile add default \
  --repo-path path-to-repo \
  --compose-file docker-compose.yml \
  --compose-file docker-compose.test.yml \
  --service odoo
```

2. Verify setup:

```bash
tario doctor
```

3. Run tests:

```bash
tario test run --profile default
```

4. Run a subset:

```bash
tario test run --profile default --keyword "foo and not slow"
```

## Core commands

```bash
tario --help
tario commands
tario describe test-run
tario doctor
tario profile list
tario profile show
tario profile add ...
tario profile use ...
tario test run ...
```

## Output contract

`tario` supports a global output option:
- `tario --output json <command>` (default)
- `tario --output text <command>`

Stable JSON envelope:
- `ok`
- `code`
- `message`
- `data`
- `next_commands`
- `meta`

## Configuration

`tario` stores runtime config outside the repository:
- macOS/Linux: `~/.config/tario/tario.toml`
- Windows: `%APPDATA%/tario/tario.toml`

Configuration is the single source of truth.
`tario` does not depend on environment-variable fallback behavior.

Test artifacts are written outside target repositories under:
- `~/.config/tario/artifacts/<profile>/`

## Validation checks

```bash
uv run ruff check .
uv run pytest -q
uv run tario --help
```

## Contributing

See `CONTRIBUTING.md`.
