# Epistemic Propagation Network

[![CI](https://github.com/frquintero/epistemic_prop_network/actions/workflows/ci.yml/badge.svg)](https://github.com/frquintero/epistemic_prop_network/actions/workflows/ci.yml)

This repository contains the Epistemic Propagation Network (EPN) pipeline: a layered LLM orchestration that reformulates, analyzes, and synthesizes input queries using configurable templates and nodes.


## Quick Start

1. Create and activate the virtual environment:

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

1. Export API credentials (example for Groq client):

```bash
export GROQ_API_KEY="gsk_..."
```

1. Run the minimal runner to inspect prompts and responses:

```bash
python scripts/minimal_runner.py "Why are all models wrong yet some are useful?"
```

1. Run the full pipeline (uses `layer.json` and `template.json` at project root):

```bash
python epn_cli.py run "Why are all models wrong yet some are useful?"
```

## Usage Examples

- Inspect pipeline prompts without sending network calls:

```bash
python scripts/minimal_runner.py "Refine this question: Are models useful?"
```

- Run the full pipeline (may make LLM API calls depending on config):

```bash
python epn_cli.py run "Synthesize implications of algorithmic bias"
```

## Examples: Defaults vs Project Config

- Run using the bundled default configs (no project-level `layer.json`/`template.json` required). The pipeline will load the built-in defaults from `epn_core/config/default_layer.json` and `epn_core/config/default_template.json`:

```bash
python epn_cli.py run "Summarize recent advances in explainability" --default
```

- Run using the project's config files located at the repository root (`layer.json` and `template.json`). This makes the pipeline use the exact layers and templates you maintain in the repo:

```bash
python epn_cli.py run "Synthesize implications of algorithmic bias" --layer-config layer.json --template-config template.json
```

Notes:

- **`epn` vs `python epn_cli.py`**: The CLI sets the program name to `epn` (ArgumentParser `prog='epn'`), so invocations shown as `epn ...` are equivalent to `python epn_cli.py ...` when running from the repository root. There is no separate installed `epn` entrypoint by default.
- **Interactive creators**: You can create new layer or template configs interactively in two ways:
- Use the CLI subcommands: `python epn_cli.py create-layer` and `python epn_cli.py create-template` (these invoke `LayerConfigurator` and `TemplateConfigurator`).
- Or run the lightweight script `scripts/builder_wizard.py` which provides a minimal dependency-free wizard and writes `layer.json` / `template.json` (useful for tests or quick creation).

## Running Tests

- Run the full test suite (fast, uses mocks where possible):

```bash
pytest -q
```

- Run a single test file:

```bash
pytest tests/test_llm_rendering.py -q
```

## Contributing

See `AGENTS.md` for developer guidelines, coding style, and how to run and interpret tests.
