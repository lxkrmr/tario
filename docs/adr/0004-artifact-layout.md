# ADR 0004: Separate artifact files per concern

## Status
Accepted

## Context
After each test run, tario wrote a single `last-run-summary.json` that contained
everything: status, profile, executed commands, and the last 20 lines each of
stdout and stderr.

This had several problems:
- stdout and stderr are mixed into one file, though they carry different information.
  stdout is pytest output (test results, tracebacks); stderr is Odoo module loading
  logs and code-quality warnings.
- Only the last 20 lines were kept. On failure, the relevant error output could be
  lost if there was a lot of output.
- The summary file became large and noisy, making it harder for agents and humans
  to quickly assess status.

An option to parse `test-report.xml` into JSON was considered but rejected: it
adds a transformation layer, introduces a potential failure point, and provides no
new information — the data already exists in the XML.

## Decision
Split artifacts into four separate files in `~/.config/tario/artifacts/{profile}/`:

- `last-run-summary.json` — slim status file: `ok`, `code`, `exit_code`,
  `profile`, `timestamp`, and pointers to the other artifact files.
- `stdout.log` — full stdout of the container run (pytest output).
- `stderr.log` — full stderr of the container run (Odoo logs and warnings).
- `test-report.xml` — copy of the JUnit XML written by pytest into the repo
  (`{repo_path}/test-report.xml`), if present.

When `--stream` is active, log files are not written since output is not captured.

## Consequences
- Agents and humans read the slim summary for a quick status check.
- Full logs are available separately when needed, without wading through noise.
- stdout and stderr are clearly separated by concern.
- The XML copy is preserved in a stable location independent of the repo working tree.
- No coupling to internal XML structure — tario does not parse or transform it.
