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
  - **Object:** Smoke-test `config_builder.py` interactive flow and ensure it writes `layer.json` and `template.json` with canonical fields (`template`, `input_context`, `expected_output`).
  - **Type:** Integration/CLI (non-network)
  - **How it runs:** Executes `config_builder.py` from the repository root with scripted stdin inputs, asserts `layer.json` and `template.json` are created, and validates that each template includes the `template` key and uses `{query}` for the first-layer `input_context`.
  - **Observations:** The test cleans up generated `layer.json` and `template.json` after validation; backups (e.g. `layer.backup.*`) may remain and are expected when existing files were present.

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

If you'd like I can:
- Add pytest markers (`integration`, `manual`) to appropriate tests and update `pyproject.toml`/CI to run selected groups.
- Add a short CI workflow snippet that runs the default test suite (`pytest -q`).
