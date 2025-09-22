# Test Instructions

This file documents the automated tests in `tests/`, what each test verifies, how the test runs, and what to observe when running them.

## Quick Commands

- **Activate virtualenv:** `source venv/bin/activate`

- **Run full suite:** `pytest -q`

- **Run a single test file:** `pytest tests/test_llm_rendering.py -q`

- **Run a specific test by name:** `pytest -k <substring> -q`

## Tests Overview

- **`tests/test_cli_defaults.py`**

  - **Object:** Verify CLI pipeline-loading defaults and `replace_templates`/merge behavior.

  - **Type:** Unit (uses mocking)

  - **How it runs:** Injects a `FakePipeline` into `epn_core.cli` and uses `monkeypatch` to control `os.path.exists`.

  - **Observations:** Ensure the `Pipeline.load_config` call is recorded and that `replace_templates` is True by default and False when `merge_defaults=True`.

- **`tests/test_config_builder_pytest.py`**

  - **Object:** Smoke-test the builder interactive flow and ensure it writes `layer.json` and `template.json` with canonical fields (`template`, `input_context`, `expected_output`).

  - **Type:** Integration/CLI (non-network)

  - **How it runs:** Copies `scripts/builder_wizard.py` into an isolated temporary directory and executes it with scripted stdin inputs, asserts `layer.json` and `template.json` are created, and validates that each template includes the `template` key and uses `{query}` for the first-layer `input_context`.

  - **Observations:** The test runs the builder in an isolated temporary directory so it does not modify repository-root files. For CI and tests prefer running the builder in a tmp directory or use the test harness which handles cleanup.

- **`tests/test_integration_defaults.py`**

  - **Object:** Sanity-check pipeline execution using bundled default configs.

  - **Type:** Integration (mocked nodes)

  - **How it runs:** Monkeypatches `NodeFactory` with a `DummyFactory` that returns `DummyNode` objects which return deterministic outputs, then runs `Pipeline.process()` with the built-in defaults.

  - **Observations:** The pipeline should run to completion without network calls and return a dict or string final result.

- **`tests/test_llm_rendering.py`**

  - **Object:** Ensure the LLM client renders clean prompts (no `{}` braces) and formats `instructions` as hyphenated lines.

  - **Type:** Unit

  - **How it runs:** Creates an `LLMClient` instance, injects a `FakeClient` that echoes the passed prompt, and asserts `last_rendered_prompt` content and the response.

  - **Observations:** `last_rendered_prompt` must be set; it must not contain `{` or `}`; each instruction should appear as `- <instruction>` on its own line; the fake response equals the rendered prompt.

- **Live / Manual LLM Tests**

  - **Object:** Optional end-to-end sanity checks that exercise the real LLM backend and confirm prompts render correctly with live API responses.

  - **Type:** Manual / Integration (network)

  - **How it runs:** Set the `LIVE_LLM=1` environment variable and provide a test prompt in `TEST_QUERY`. The live-mode tests will use the real `LLMClient` and require a working `GROQ_API_KEY` in the environment.

  - **Environment variables:**

    - `LIVE_LLM=1` — enable live LLM tests.

    - `TEST_QUERY='Why are humans prone to conflict?`' — example query used by the live test harness. If unset, the test will bail out or use a default sample query.

    - `GROQ_API_KEY` — required for running live LLM tests; keep keys out of source control and set them in your CI or local environment securely.

  - **Observations:** Live tests are skipped by default. Use them only when you want a human-in-the-loop verification of the entire pipeline; they may be slower and consume API credits.

- **`tests/test_template_manager.py`**

  - **Object:** Verify `TemplateManager` merging/replacing behavior and validation.

  - **Type:** Unit

  - **How it runs:** Loads templates, verifies `has_template()` after merge/replace operations, and ensures `validate_templates()` raises when templates are missing.

  - **Observations:** After `load_templates(..., replace=False)` templates are merged; `replace=True` replaces current templates; replacing with empty dict should cause validation to fail.

- **`tests/test_validator_placeholders.py`**

  - **Object:** Validate placeholder binding across layers and detection of missing placeholders.

  - **Type:** Unit

  - **How it runs:** Builds a minimal `TemplateManager`, constructs a fake pipeline with `LayerStub`/`NodeStub` objects, then calls `Validator.validate_complete_config()`.

  - **Observations:** Valid configuration returns True; templates referencing missing placeholders cause `Validator` to raise `ValueError`.

## Notes

- Tests are designed to avoid real network calls; the LLM client and node processing are mocked or replaced in tests. `GROQ_API_KEY` is not required to run the test suite.

- Keep long/manual inspection tests separate (if present) so CI runs remain fast. Use markers like `@pytest.mark.integration` for longer tests.

Additional tips and validation steps

-- **Run the builder safely (recommended):** Execute `scripts/builder_wizard.py` from a temporary working directory to avoid overwriting local `layer.json`/`template.json`:

```bash
mkdir -p /tmp/epn-build && cd /tmp/epn-build
python /path/to/repo/scripts/builder_wizard.py
```

- **Validate generated templates:** After running the builder, check each template JSON contains the canonical keys and shapes required by the pipeline loader:

  - Each template object must include a top-level `template` string.

  - `input_context` must be set; the first-layer template should use `{query}` as its `input_context`.

  - `expected_output` must be present and named consistently across layers so downstream placeholders resolve.

- **Quick JSON validation:**

```bash
python - <<'PY'
import json,sys
for p in ('layer.json','template.json'):
    with open(p) as f:
        json.load(f)
print('JSON OK')
PY
```

If you'd like I can:

- Add pytest markers (`integration`, `manual`) to appropriate tests and update `pyproject.toml`/CI to run selected groups.

- Add a short CI workflow snippet that runs the default test suite (`pytest -q`).
