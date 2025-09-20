# Repository Guidelines

## Setup & Environment

Activate the bundled virtual environment with `source venv/bin/activate` before running tools. Load credentials from `~/.config/env.d/ai.env`, ensuring it exports `GROQ_API_KEY=gsk_...`; confirm with `echo $GROQ_API_KEY`. Keep `.env`-style files untracked and rely on environment variables when writing scripts or tests that reach the Groq API.

## Canonical Contract & Defaults

The pipeline enforces a strict canonical contract for inter-layer data to make execution deterministic and fail-fast at load time:

- **Each template must declare an `expected_output` string** that names the key the node will emit (lowercase letters, digits and underscores only, e.g. `reformulated_question`).
- **Downstream templates must reference those exact keys** in their `input_context` placeholders (e.g. `{reformulated_question}`); placeholders that do not match any prior-layer `expected_output` (or the allowed globals `query`/`input`) will cause configuration validation to fail.
- **Templates should include**: `template` (the full LLM prompt/task string), `placeholders` (list of placeholder names present in the template), `input_context` (string or list of strings showing which placeholders are provided at runtime), `expected_output`, and optional `instructions` (response-formatting guidance).

Bundled defaults are provided under `epn_core/config/default_layer.json` and `epn_core/config/default_template.json`. By design, the system treats defaults explicitly: loading defaults will replace project-level templates unless an explicit merge is requested (see CLI docs below). This avoids accidental silent merges that can hide contract violations.

## Project Structure & Module Organization

Core system modules reside in `epn_core/`: pipeline orchestration in `epn_core/core/`, configuration management in `epn_core/config/`, command-line interfaces in `epn_core/cli/`, and utilities in `epn_core/utils/`. Layered processing includes reformulation (layer1), parallel definition generation (layer2 with semantic and teleological nodes), and synthesis (layer3). Entry points include `main.py` (pipeline runner), `inspect_pipeline.py` (detailed inspection tool), `minimal_runner.py` (simple test runner), and `epn_cli.py` for CLI operations. Documentation and design references live alongside this file. Automated tests mirror the core modules inside `tests/`.

## Build, Test, and Development Commands

- `pip install -r requirements.txt` – install runtime dependencies inside the activated virtual environment.
- `python main.py "Why are all models wrong yet some are useful?"` – execute the full 1-2-1 pipeline for an ad-hoc query.
- `python inspect_pipeline.py "Why are all models wrong yet some are useful?"` – run detailed pipeline inspection with all prompts, outputs, and LLM configurations.
- `python minimal_runner.py "Why are all models wrong yet some are useful?"` – run simplified pipeline execution for testing.
- `python epn_cli.py` – access command-line interface for configuration and management.
- `pytest` – execute the async-aware unit and integration suite configured through `pyproject.toml`.

## Coding Style & Naming Conventions

Follow PEP 8 with 4-space indentation and the repository-wide 88-character line limit. Modules and functions should use snake_case, while agent classes end with `Agent` or `Node`. Format code with `black .` and `isort .`, lint with `flake8`, and type-check non-trivial orchestrations using `mypy` prior to review.

## Testing Guidelines

The suite relies on `pytest` with `pytest-asyncio`; declare async fixtures explicitly and manage event loops deliberately. Name files `test_<feature>.py`, assert structured `Phase2Triple`/`Phase3Triple` outputs, and cover both success and failure paths for new agents. Aim for >90% coverage on touched modules, documenting justified gaps in the pull request.

## Commit & Pull Request Guidelines

Keep commits focused with concise, Title Case subject lines (emojis optional, as reflected in `🧹 Major cleanup and documentation update`). Reference issues in the body when relevant. Pull requests should explain context, outline changes, list validation commands (tests, linting), and attach CLI output snippets when behaviour shifts. Obtain maintainer review and wait for CI to pass before merging.

## Security & Configuration Tips

Never commit API keys or local environment files. When writing integration tests, guard external calls behind environment checks or provide mock responses. Rotate credentials promptly if exposure is suspected.

## Docs Index (brief)

The repository keeps user-facing and design documentation under `docs/` (except `AGENTS.md` which stays at the project root). Below is a short index of the important Markdown files and their purpose:

- `README.md` (root): Project overview and quickstart (where to run the pipeline, env setup, and test commands).
- `docs/canonical_contract.md`: Detailed rules for template shape, placeholders, and the canonical contract enforced by the `Validator`.
- `docs/LLM.md`: Notes on LLM usage, model choices, reasoning effort mapping, and client configuration.
- `docs/TEST_INSTRUCTIONS.md`: Concise instructions for running and interpreting the automated tests (which tests, how to run them, and what to look for).
- `docs/gpt-oss-120b-guide.md`: Model-specific guidance and practical tips for using large models effectively with the pipeline.
- `docs/OOP_ARCHITECTURE.md`: High-level design notes about core classes, layering, and node responsibilities.
- `docs/xai_integration.md`: Guidance for explainability / XAI hooks and integration tests.

If you add or move documentation, please update this index so the next maintainer can find key files quickly.

## Formatting Note

- **Always convert Markdown headings to ATX style (`# Heading`)** to satisfy the repository linter and keep consistency across documentation.
