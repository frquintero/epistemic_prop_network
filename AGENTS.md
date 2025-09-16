# Repository Guidelines

## Setup & Environment
Activate the bundled virtual environment with `source venv/bin/activate` before running tools. Load credentials from `~/.config/env.d/ai.env`, ensuring it exports `GROQ_API_KEY=gsk_...`; confirm with `echo $GROQ_API_KEY`. Keep `.env`-style files untracked and rely on environment variables when writing scripts or tests that reach the Groq API.

## Project Structure & Module Organization
Layered agents reside in `layers/`: reformulation lives in `layer1_reformulation/`, definition generators in `layer2_definition/`, and validators in `layer3_validation/`. Shared orchestration helpers are in `core/` and `utils/`. Entry points include `main.py` (pipeline runner), `inspect_pipeline.py` (detailed inspection tool), and `api.py` for service embedding. Documentation and design references live alongside this file and within `docs/`. Automated tests mirror the layering inside `tests/`.

## Build, Test, and Development Commands
- `pip install -r requirements.txt` – install runtime dependencies inside the activated virtual environment.
- `python main.py "What are mental models?"` – execute the full four-layer pipeline for an ad-hoc query.
- `python inspect_pipeline.py "What are mental models?"` – run detailed pipeline inspection with all prompts, outputs, and LLM configurations.
- `pytest` – execute the async-aware unit and integration suite configured through `pyproject.toml`.

## Coding Style & Naming Conventions
Follow PEP 8 with 4-space indentation and the repository-wide 88-character line limit. Modules and functions should use snake_case, while agent classes end with `Agent` or `Node`. Format code with `black .` and `isort .`, lint with `flake8`, and type-check non-trivial orchestrations using `mypy` prior to review.

## Testing Guidelines
The suite relies on `pytest` with `pytest-asyncio`; declare async fixtures explicitly and manage event loops deliberately. Name files `test_<feature>.py`, assert structured `Phase2Triple`/`Phase3Triple` outputs, and cover both success and failure paths for new agents. Aim for >90% coverage on touched modules, documenting justified gaps in the pull request.

## Commit & Pull Request Guidelines
Keep commits focused with concise, Title Case subject lines (emojis optional, as reflected in `🧹 Major cleanup and documentation update`). Reference issues in the body when relevant. Pull requests should explain context, outline changes, list validation commands (tests, linting), and attach CLI output snippets when behaviour shifts. Obtain maintainer review and wait for CI to pass before merging.

## Security & Configuration Tips
Never commit API keys or local environment files. When writing integration tests, guard external calls behind environment checks or provide mock responses. Rotate credentials promptly if exposure is suspected.
