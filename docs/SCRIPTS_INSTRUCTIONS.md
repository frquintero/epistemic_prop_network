# Scripts Usage & Instructions

This document describes the small utility scripts provided in `scripts/`, their purpose, required dependencies, and common usage examples.

Location: `scripts/`

## Quick Setup

Activate the project's venv then run commands below.

`source venv/bin/activate`

## Environment

- GROQ API key: set `GROQ_API_KEY` in your environment for any live LLM calls.
- LIVE_LLM toggle: set `LIVE_LLM=1` to enable live requests in scripts that call the LLM.
- TEST_QUERY: used by the inspection wrapper to supply the query when running live examples.

## Config Location & Runtime Behavior

- **Root-only for validator:** `scripts/validate_templates.py` expects `template.json` and `layer.json` to be present in the current working directory (repository root). If either file is missing the validator prints an error and exits with a non-zero code (exit code `2`).
- **Pipeline fallback:** the runtime pipeline will search for `template.json` and `layer.json` in the repo root. If they are not present the pipeline **does** load fallback defaults from `epn_core/config/default_template.json` and `epn_core/config/default_layer.json`. The validator intentionally enforces the presence of explicit config files in root for authoring and CI workflows; runtime fallback exists to allow quick experiments but should not be relied on for production runs.
- **Recommendation:** treat the validator as the authoritative check: put `template.json` and `layer.json` in the repo root and run `python scripts/validate_templates.py` as part of authoring and CI to catch schema, placeholder, and cross-file errors early.

## Scripts Overview

### `builder_wizard.py`

- Purpose: Interactive and non-interactive (heredoc-friendly) authoring tool that builds canonical `template.json` and `layer.json` from minimal, guided inputs. It enforces a minimal 1-1-1 topology (>= 3 layers, >= 1 node per layer) and sanitizes identifiers.
- Dependencies: None (intentionally dependency-free so tests can run non-interactively).

- Behavior (detailed):
  - The script prompts for a sequence of layers. Each layer requires a name and a one-line description (default: "Process and transform input").
  - For each layer, you add one or more nodes. For each node the script asks for:
    - node id (short identifier),
    - `expected_output` (a single snake_case token; the script suggests a sanitized default derived from the node id),
    - `node_epistemic_task` (one-line instruction describing the node's goal), and
    - zero or more `instructions` (additional free-form guidance; stop entering instructions with a blank line).
  - The helper `ask()` returns `None` on EOF; the script treats EOF specially so the wizard can run non-interactively using heredoc inputs. EOF in required contexts will abort with exit code `1`.
  - Duplicate `expected_output` tokens are rejected: the script will prompt for a unique token (interactive) and will report an error (exit code `2`) if duplicates remain.

- Flags and output modes:
  - `--dry-run`: print the generated `template.json` and `layer.json` JSON to stdout and exit without writing files.
  - `--timestamped`: write `template.<YYYYMMDDHHMM>.json` and `layer.<YYYYMMDDHHMM>.json` instead of `template.json`/`layer.json`.
  - `--overwrite`: allow overwriting existing `template.json` and `layer.json`. Without this flag the script prompts to confirm overwriting and exits with code `3` if the user declines.
  - `--preview`: render an example preview by substituting a neutral `<USER_QUERY>` into generated templates (calls into `builder_utils.preview`).

- Exit codes (summary):
  - `0` — success and files written (or printed with `--dry-run`).
  - `1` — early abort due to EOF or insufficient inputs (e.g., fewer than three layers when EOF encountered).
  - `2` — duplicate `expected_output` tokens detected.
  - `3` — user declined to overwrite existing files.
  - `130` — aborted via KeyboardInterrupt (Ctrl-C).

- Non-obvious details & edge cases:
  - Identifiers are sanitized via `sanitize_name()` before being used as `expected_output` tokens — the script suggests sanitized defaults.
  - In non-interactive/heredoc mode, missing or duplicate fields can cause the script to abort; provide deterministic, unique `expected_output` tokens when scripting the wizard.
  - The script intentionally avoids external dependencies so tests can simulate user input via heredoc; prefer `--dry-run` in CI.

- Usage examples:

  Interactive:

  ```bash
  python scripts/builder_wizard.py
  ```

  Non-interactive dry run (heredoc):

  ```bash
  python scripts/builder_wizard.py --dry-run <<'EOF'
  InputLayer
  Layer description
  node_a
  idea
  Summarize ideas

  EOF
  ```

  Timestamped output:

  ```bash
  python scripts/builder_wizard.py --timestamped
  ```

  Preview templates without writing files:

  ```bash
  python scripts/builder_wizard.py --preview --dry-run
  ```

### `epn_inspect_run.py`

- Purpose: Run the pipeline while intercepting per-node LLM calls to print the exact rendered prompt, the raw response object, and the node's primary LLM parameters. Useful for debugging live behaviour and auditing prompts the system sends.
- Dependencies: Runs against the canonical `Pipeline` implementation in `epn_core.core.pipeline` and requires live LLM client availability to show real responses.
- Important: The script patches node `process` methods at runtime. It may be noisy and will attempt live LLM calls when `LIVE_LLM=1` is set and a configured LLM client and API key are available.
- Env variables: `LIVE_LLM=1`, `TEST_QUERY` (the input query to run the pipeline with), and `GROQ_API_KEY` for live calls.
- Usage example:

  ```bash
  source venv/bin/activate
  LIVE_LLM=1 TEST_QUERY="why are there something instead of nothing?" python scripts/epn_inspect_run.py
  ```

- Output: Prints for each node:
  - The rendered prompt (placeholders substituted),
  - The raw response text (or `reasoning` fallback) and full raw response object,
  - The node's main LLM parameters (`model`, `temperature`, `reasoning_effort`),
  - Final pipeline synthesized output printed at the end.

### `validate_templates.py`

- Purpose: Validate `template.json` and `layer.json` against `schemas/template_schema.json` and `schemas/layer_schema.json`, and check that each template contains its declared `input_context` placeholder.
- Dependencies: `jsonschema` Python package.
- Usage: Run from repository root where `template.json` and `layer.json` exist:

  ```bash
  python scripts/validate_templates.py
  ```

- Exit codes:
  - `0` success
  - Non-zero indicates missing files, schema validation errors, or placeholder mismatches (see script output)

## Notes for CI and Tests

- `builder_wizard.py` is intentionally dependency-free so tests can simulate input with heredoc or file redirection. In CI, prefer `--dry-run` and inspect JSON output rather than writing files.
- `epn_inspect_run.py` invokes live LLM calls when `LIVE_LLM=1`; gate it in CI or use mocks for deterministic tests.
- `validate_templates.py` is safe to run in CI but requires `jsonschema` installed; add `jsonschema` to test environment or install in CI steps.

## Troubleshooting

- If `validate_templates.py` errors: ensure `jsonschema` is installed (`pip install jsonschema`) and `template.json`/`layer.json` exist in the CWD.
- If `epn_inspect_run.py` prints "LLM client unavailable" or skips calls: confirm `GROQ_API_KEY` and that the configured LLM client is reachable; also ensure `LIVE_LLM=1` is set to allow live calls.
- If `builder_wizard.py` exits unexpectedly in non-interactive mode: provide a complete heredoc input or prefer `--dry-run` and scripted inputs.

## Next Steps / Suggestions

- Consider adding a `--save-logs` option to `epn_inspect_run.py` to write per-run outputs to `logs/` for auditing.
- Optionally add a `--node-filter` flag to `epn_inspect_run.py` to limit inspection to a subset of nodes.
