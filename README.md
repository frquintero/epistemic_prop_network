# Epistemic Propagation Network (EPN)

Epistemic Propagation Network (EPN) is a small, opinionated pipeline for orchestrating large language models in a layered, forward-propagation structure. It is designed to make end-to-end LLM workflows explicit, auditable, and configurable via JSON runtime artifacts.

EPN is not a single monolithic model — it is a runtime that coordinates multiple LLM calls arranged into layers and nodes, where each node renders a template, executes an LLM query, and forwards a labeled output that downstream nodes can consume.

## Core ideas

- Layers: EPN organizes work into ordered layers. Each layer receives inputs from the previous layer and produces one or more named outputs that downstream layers can reference. The typical structure is "1-N-1": a single input (the query/context) is processed by N nodes in a layer, and their outputs are then aggregated or selected by the next layer.

- Nodes: A node pairs a template with an LLM configuration. Nodes render templates (with brace-delimited placeholders) into prompts, call the configured LLM client, and emit a named `expected_output` token used by downstream templates.

- Templates & placeholders: Templates are text artifacts that contain brace-delimited placeholders (e.g. `{query}`, `{upstream_summary}`). The validator enforces that templates reference only placeholders that are provided by upstream `expected_output` tokens or initial inputs.

- Canonical contract: To keep execution deterministic and auditable, EPN enforces a canonical contract between layers and templates: placeholders must match `expected_output` names from upstream nodes, runtime configs are explicit about node ids, template ids, and LLM parameters, and templates are validated before runs.

- Introspection: EPN includes inspector utilities that capture rendered prompts, request parameters, and raw LLM responses for each node, enabling debugging and external auditing.

## Repository layout (important files)

- `epn_core/` — core runtime, loader, validators, node implementations, and the LLM client abstractions.
- `layer.json`, `template.json` — runtime artifacts (project-level) that define the pipeline structure and templates. The loader expects the runtime shape (layers with node ids, template ids, `expected_output`, and `llm_config`).
- `scripts/builder_wizard.py` — lightweight interactive creator for `layer.json` and `template.json` (useful for quick authoring in tests or demos).
- `scripts/epn_inspect_run.py` — inspector script that runs the pipeline but records rendered prompts and raw responses for each node.
- `scripts/validate_templates.py` — validates templates/layers against the canonical contract and JSON schemas.
- `epn_cli.py` — command-line entrypoint for running, creating, and managing configs.

## How EPN is configured

- A `layer.json` defines a sequence of layers. Each layer lists nodes; nodes have `id`, `name`, `template_id`, `expected_output` (the label they emit), and `llm_config` (model, temperature, tokens, reasoning effort).

- A `template.json` (runtime shape) maps template ids to template text. Templates use brace-delimited placeholders that must match upstream `expected_output` labels or the initial input name (commonly `query`).

- Dataflow is forward-only: outputs from layer L can be used as inputs by layer L+1. The validator enforces cross-file consistency between `expected_output` names and template placeholders.

Quick note on the layer shape (1-N-1 forwarding):

- Each layer receives a single upstream package of named inputs (for the first layer the canonical input is `query`).
- A layer may contain multiple nodes (N). Each node renders a prompt using the available inputs and emits a single named output (`expected_output`).
- Downstream layers reference these named outputs by placeholder, e.g. `{reformulated_query}` or `{analysis_result}`.

## Quick Start

These commands assume you are in the repository root.

1. Create and activate a Python virtual environment:

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

1. Export your LLM credentials (example for Groq client):

```bash
export GROQ_API_KEY="gsk_..."
```

1. Run the minimal runner (no external network calls by default; useful for inspecting rendered prompts):

```bash
python scripts/minimal_runner.py "Why are all models wrong yet some are useful?"
```

1. Run the full pipeline using the project configs at the repository root (this may make LLM API calls depending on node configs):

```bash
python epn_cli.py run "Why are all models wrong yet some are useful?"
```

1. Run the inspector to capture per-node rendered prompts and raw LLM responses (set `TEST_QUERY` to provide an input):

```bash
TEST_QUERY="Why are models useful despite being wrong?" python scripts/epn_inspect_run.py
```

## Examples: Defaults vs Project Config

- Run using the bundled defaults (no project `layer.json`/`template.json` required):

```bash
python epn_cli.py run "Summarize recent advances in explainability" --default
```

- Run using project-level config files located at the repository root:

```bash
python epn_cli.py run "Synthesize implications of algorithmic bias" --layer-config layer.json --template-config template.json
```

## How nodes and templates are authored

- Templates: write plain text with named placeholders in curly braces. Prefer small, focused prompts and name outputs explicitly via the `expected_output` field in the node. Example template snippet:

```
Instruction: Reformulate the user question.
Input: {query}
Output:
```

- Nodes: configure `llm_config` to choose model, temperature, and other inference parameters. Keep individual node prompts focused to make downstream composition easier.

## Running Tests

Run the full test suite:

```bash
pytest -q
```

Run a single test file:

```bash
pytest tests/test_llm_rendering.py -q
```

## Contributing

- Follow `AGENTS.md` for developer guidelines, coding style, and test instructions.
- Make non-trivial changes on a feature branch and open a pull request so the change to workflow files (if any) can be reviewed and merged using an account with appropriate permissions.
- When adding or changing templates or layers, run the validator:

```bash
python scripts/validate_templates.py
```

This helps catch placeholder/expected-output mismatches before executing runs that call the LLM.

## Troubleshooting & Notes

- If prompts contain literal placeholder names like `query` instead of the actual input, ensure you provided the `TEST_QUERY` or that your `template.json` placeholders match upstream `expected_output` values.
- Keep `template.json` and `layer.json` in the runtime shape expected by the loader (templates wrapped under `"templates"` and layers include `id` and node `template_id` fields).

---

If you'd like, I can also:

- Add a short example `layer.json` + `template.json` snippet to the README.
- Add a one-line CLI examples block showing `epn_cli.py create-layer` and `create-template` usage.
