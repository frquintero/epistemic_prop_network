# Builder Wizard Spec

Purpose
- Provide a small interactive CLI that guides users to author `template.json` and `layer.json` safely.

Design Goals
- Minimize fields the user must enter: `expected_output` name, `node_epistemic_task`, optional `instructions` (0-3 short lines).
- Auto-fill `input_context` for subsequent layers from previous `expected_output` names.
- Generate `template.template` strings automatically as: `"{node_epistemic_task}: {<input_placeholder(s)>}"`.
- Provide a preview using a sample query before writing files and run basic validation.

Usage
- Run: `python scripts/builder_wizard.py --sample-query "Why are humans prone to conflict?"`
- Flags:
  - `--timestamped` Write files as `template.YYYYMMDDHHMM.json` and `layer.YYYYMMDDHHMM.json`.
  - `--overwrite` Overwrite `template.json`/`layer.json` without prompt.
  - `--dry-run` Print generated JSON and validation results but do not save files.

Preview & Validation
- The wizard always shows a final rendered prompt using the provided `--sample-query`.
- Validation checks:
  - Each template entry has `template`, `input_context`, `expected_output`.
  - `template` contains the `{<input_context>}` placeholder.
  - `expected_output` names are unique and snake_case.

Saving
- If validation passes, wizard writes the files in safe mode (timestamped) unless `--overwrite` is supplied.
