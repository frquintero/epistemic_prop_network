# EPN Canonical Data Contract

## Purpose

This document defines the canonical data contract for inter-layer communication in the Epistemic Propagation Network (EPN). It makes explicit the expected naming, structure, and validation rules so pipelines are deterministic and fail fast when configurations are invalid.

## Core Rules

- **Node Output Identity**: Each node template must declare a single `expected_output` string. When a node executes, the pipeline must place its result in the layer outputs dictionary under the exact `expected_output` key.

- **Placeholder Binding**: Templates' `input_context` placeholders must reference exact `expected_output` names emitted by nodes in earlier layers. Placeholders use the existing curly-brace syntax (e.g. `{semantic_analysis}`).

- **Layer Ordering**: A node can only depend on outputs produced by nodes in previous layers (lower index). Forward or same-layer dependencies are invalid.

- **Normalization / Naming Rules**:
  - Allowed characters: lowercase `a-z`, digits `0-9`, and underscore `_` only.
  - Authors must provide `expected_output` values using only allowed characters.
  - The runtime will not perform automatic normalization or fuzzy matching. Use the migration helper or the validator to find and fix mismatches.

- **Single Responsibility**: Each node template should produce exactly one `expected_output`. For multiple logical outputs, define multiple nodes.

- **Node ID vs expected_output**: Node IDs (defined per `layer.json`) are orchestration identifiers only. They must not be used as placeholder names in `input_context`.

## Validation Guarantees

On configuration load, the system will validate that for every node in layer `L`, every placeholder referenced in its template's `input_context` exists as an `expected_output` produced by some node in layer indices `< L`. If not, configuration loading fails with a descriptive error.

## Error Examples

- Missing placeholder:

```
ValidationError: Node `synthesis_node` (layer 3) template `synthesis` references missing placeholder `{teleological_output}`. Available prior outputs: ['query','reformulated_question','semantic_analysis']
```

- Invalid `expected_output` name:

```
ValidationError: Template `teleological_node` declared `expected_output='Teleological Output'` — invalid characters; use lowercase letters, digits, and underscores.
```

## Loading Semantics

- `replace` mode: Loads the supplied templates and replaces any currently loaded templates (no merging).
- `merge` mode: Explicit opt-in; merges template sets with a defined precedence (project templates override defaults).

Command-line semantics:
- `--default` will load defaults in `replace` mode by default. Use `--merge-defaults` to explicitly merge.

## Migration Guidance

- Use the migration helper (`tools/migrate_templates.py`) in dry-run mode to find placeholder mismatches and suggested fixes.
- Apply fixes manually or with `--apply` after reviewing the proposed changes.

## Acceptance Criteria

- Validator rejects any pipeline where placeholders are not exact matches to prior-layer `expected_output` keys.
- `--default` runs load only the specified defaults (no silent merge).
- Runtime remapping of node IDs to `expected_output` is removed once validator ensures correctness.
