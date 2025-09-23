# OOP Node Proof-Of-Concept

This document describes a standalone proof-of-concept (PoC) implementing a node-centric
object model for the Epistemic Propagation Network (EPN). The PoC is intentionally
non-invasive — it runs as a separate script/application under `scripts/` and does not
modify the existing pipeline or core modules.

## Overview

- Primitive: Node — an LLM actor that receives inputs, runs a processing
  routine (the internal LLM machine), and emits an output stored in its
  `response_state` attribute. Nodes do not store `input_context` or `last_response`.
- Wiring: a separate `Network`/`Orchestrator` holds the network wiring mapping
  node IDs to the placeholder keys they expect as inputs.
- Grouping: logical groups (layers) are computed at runtime by grouping nodes that
  share the same canonical `input_context` signature (sorted tuple of placeholders).
- Seed node: there is a special node that contains only the user query (no task,
  no LLM). This node's `expected_output` key is typically `query` and seeds the
  `context` map used for execution.

## Key Design Decisions

- Node minimal surface area: node objects contain `id`, `expected_output`, `task`,
  `instructions`, `llm_config`, and `response_state` only. Wiring is external.
- No NodeState enum: node lifecycle is ephemeral and not persisted on node objects.
- Two-pass node processing: when multiple inputs exist, nodes first synthesize
  inputs with a summary call, then run the task call using the summary (configurable).
- Start rule: execution always begins with nodes whose `input_context` contains
  `query` (the seed user query).

## Prototype Goals

1. Reproduce the logical behavior of a 1-3-1 network (one seed node, three mid
   nodes that consume `query`, one final node that consumes the three mid-node outputs).
2. Demonstrate node movement by re-wiring a mid node to consume a different input
   signature and re-running the prototype without touching Node code.
3. Provide mock mode (deterministic) and optional live-xAI mode (if `XAI_API_KEY`
   is present in the environment) using `grok-4-fast-reasoning` as the example model.
4. Output a clear execution trace: prompts rendered, per-node intermediate summaries
   (if two-pass), final outputs stored in the shared `context` map.

## Command-line Interface

- `scripts/epn_oop_prototype.py --mode {mock|live-xai} --query "..." [--model MODEL] [--workers N]`
- Modes:
  - `mock`: deterministic fake LLM responses derived from node id and task.
  - `live-xai`: perform real calls to xAI using `XAI_API_KEY`.

## Object Model (PoC)

- Node:
  - `id: str`
  - `expected_output: str`
  - `task: str` (task template)
  - `instructions: list[str]`
  - `llm_config: dict` (model, temperature, two_pass flag)
  - `response_state: Optional[str]` (None until LLM output produced)
  - Methods:
    - `render_prompt(inputs: dict) -> str`
    - `process(context: dict, inputs: list[str], client) -> None`

- Network/Orchestrator:
  - `nodes: Dict[str, Node]`
  - `wiring: Dict[str, List[str]]` (node_id -> placeholder keys to read)
  - `context: Dict[str, str]` (expected_output -> value)
  - `compute_groups()` -> Dict[group_key, List[node_id]]
  - `run()` - orchestrates execution using grouping rule and start rule.

## Node Processing Semantics

- Single-input nodes: call LLM once with `compose_task_prompt(inputs[0], task, instructions)`.
- Multi-input nodes (two_pass=True):
  1. `synth = client.call(compose_summary_prompt(inputs, instructions))`
  2. `out = client.call(compose_task_prompt(synth, task, instructions))`
  Store `out` in `node.response_state` and `context[node.expected_output]`.

## xAI Integration

- Live mode uses the openai-style client pattern: `client.responses.create(...)`.
- Use `scripts/run_xai_batch.py` extractor helpers where appropriate to extract
  assistant text from `resp.output` robustly.

## Validation Rules

- `expected_output` tokens must follow canonical naming (lowercase a-z, digits, underscore).
- Wiring must only reference placeholder keys that are eventual `expected_output` tokens.
- The orchestrator will fail-fast on missing inputs (or optionally defer and retry).

## Acceptance Criteria

- The script runs a mock 1-3-1 network and prints a deterministic trace.
- Re-wiring a node (change entry in `wiring`) and re-running demonstrates node movement.
- Live-xAI mode returns real LLM outputs when `XAI_API_KEY` is present.

## Implementation Plan (step-by-step)

1. Create `scripts/epn_oop_prototype.py` implementing the classes and CLI.
2. Implement a deterministic mock client (returns `f"{node.id}: response to {task}"`).
3. Add a small in-script example network (1-3-1) and wiring mapping. Provide
   an option to load network spec from a JSON/YAML file for more complex tests.
4. Implement grouping logic (sorted tuple as group key) and start-rule (`query`).
5. Implement two-pass processing and make it configurable via `llm_config['two_pass']`.
6. Add optional live-xAI client path using `XAI_API_KEY` and model selection.
7. Add logging and pretty-print execution trace. Add `--dry-run` to only show prompts.
8. Run the mock example and validate outputs. Save example run trace to `logs/`.

## Testing & Observability

- Unit test: mock client with 1-3-1 to validate context map and ordering.
- Manual test: rewire one mid node to consume another mid-node `expected_output` and
  re-run; confirm group recomputation and new execution order.

## Future integration notes

- If the PoC proves valuable, consider refactoring into `epn_core` as a new
  orchestrator implementation that keeps the canonical contract (exact placeholder names).
- When integrating, ensure validators are updated to accept wiring stored in the
  network spec rather than `Node` objects.

## Appendix: Example 1-3-1 spec (inline)

Nodes:
- `node_a` (seed): expected_output = `query` (seeded by CLI)
- `node_b1`: expected_output = `summary`, wiring = [`query`], task = "Summarize the query in 30 words"
- `node_b2`: expected_output = `topics`, wiring = [`query`], task = "List 5 topic keywords from the query"
- `node_b3`: expected_output = `reformulated`, wiring = [`query`], task = "Reformulate the query for clarity"
- `node_c`: expected_output = `final_answer`, wiring = [`summary`,`topics`,`reformulated`], task = "Answer the query using the summary, topics and reformulation"
