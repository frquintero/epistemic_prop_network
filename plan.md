# EPN Agnostic Architecture & Configurator Plan

## 1. Objective

The objective of this plan is to make the Epistemological Propagation Network (EPN)
fully agnostic and user-configurable. The system will allow users to define any
pipeline structure (layers, nodes, LLMs) and prompt templates, making EPN
adaptable to any epistemic workflow.

## 2. Scope & Goals

**Scope:**

- Refactor EPN to support arbitrary layer/node structures and prompt templates.
- Provide interactive configurators for both layer-node structure and prompt templates.
- Ensure robust validation and seamless runtime loading of configurations.

**Goals:**

- **Maximum Flexibility:** Any number of layers/nodes, any LLM per node.
- **User Empowerment:** Users can design custom epistemic pipelines.
- **Separation of Concerns:** Prompts and structure are independently configurable.
- **Robustness:** Validation prevents runtime errors due to mismatched configs.

## 3. Implementation Plan

**Key Steps:**

1. Design JSON schemas for `layer_conf.json` and `template.json`.
2. Refactor pipeline and template management to be fully dynamic.
3. Implement configurator wizards (CLI first, GUI optional).
4. Add robust validation logic.
5. Update documentation and provide migration guide.

**New Components:**

- Layer-Nodes Configurator (`epn --create_layer`)
- Template Configurator (`epn --create_template`)
- Validation System
- Runtime Loader

**Required System Modifications:**

- Remove all hardcoded layer/node logic.
- Build pipeline dynamically from `layer_conf.json`.
- Use a factory or builder pattern to instantiate nodes and layers.
- TemplateManager loads from `template/template.json`.
- Prompts are mapped to nodes by unique IDs or names.
- Configurators write to their respective JSON files.
- Validation runs automatically after configurator or before pipeline execution.
- Update README and AGENTS.md to describe new workflow.

## 4. System Overview

**How the System Works:**

1. User runs configurators to define the pipeline structure and prompts.
2. System validates that all nodes have matching prompts.
3. At runtime, EPN loads `layer/layer_conf.json` and `template/template.json` to
   build the pipeline dynamically.
4. If no config is provided, defaults to these files.
5. User can re-run configurators at any time to update structure or prompts.

**Workflow:**

1. `epn --create_layer` → builds `layer/layer_conf.json`
2. `epn --create_template` → builds `template/template.json`
3. Validation step: System checks that all nodes have matching prompts.
4. Production use: User runs EPN as usual; system loads configs and builds pipeline.

**Example Directory Structure:**

```text
epistemic_LLM_network/
  layer/
    layer_conf.json
  template/
    template.json
  main.py
  inspect_pipeline.py
  ...
```

## 5. Configuration Details

### Layer-Nodes Configurator (`epn --create_layer`)

```shell
Welcome to the EPN Layer-Nodes Configurator!
Let's define your epistemic pipeline structure.

How many layers (including input and synthesis)? [3]: 4

Layer 1 (Input/Reformulation) is required and will be created as a single node.

Name for Layer 2? [default: Analysis]: Validation
How many nodes in Layer 2 (Validation)? [3]: 2

- Name of node 1 in Layer 2 (Validation): Coherence
  Select LLM for node 'Coherence': [1] gpt-oss-20b  [2] qwen3-32b  [3] gpt-oss-120b
  Choice: 1
  Temperature (0.0-1.0) for 'Coherence': 0.7
  Reasoning effort for 'Coherence': [1] low  [2] medium  [3] high
  Choice: 2

- Name of node 2 in Layer 2 (Validation): Pragmatic
  Select LLM for node 'Pragmatic': [1] gpt-oss-20b  [2] qwen3-32b  [3] gpt-oss-120b
  Choice: 2
  Temperature (0.0-1.0) for 'Pragmatic': 0.6
  Reasoning effort for 'Pragmatic': 1

Name for Layer 3? [default: Synthesis]: Synthesis
Layer 3 (Synthesis) is required and will be created as a single node.

Summary:
- Layer 1: Input (1 node: Reformulator)
- Layer 2: Validation (2 nodes: Coherence, Pragmatic)
- Layer 3: Synthesis (1 node: Synthesis)

Save this configuration to layer/layer_conf.json? [Y/n]: Y

✅ Layer configuration saved!
```

### Template Configurator (`epn --create_template`)

```shell
Welcome to the EPN Template Configurator!
Let's define the prompt templates for each node.

Loading structure from layer/layer_conf.json...

Node: Reformulator (Layer 1)
Prompt for 'Reformulator':
> [User enters prompt text here]

Node: Coherence (Layer 2)
Prompt for 'Coherence':
> [User enters prompt text here]

Node: Pragmatic (Layer 2)
Prompt for 'Pragmatic':
> [User enters prompt text here]

Node: Synthesis (Layer 3)
Prompt for 'Synthesis':
> [User enters prompt text here]

Summary:
- 4 prompts defined for 4 nodes.

Save this configuration to template/template.json? [Y/n]: Y

✅ Template configuration saved!
```

**Validation:**

- System checks that every node in `layer_conf.json` has a corresponding prompt in
  `template.json` (and vice versa).
- Validation runs automatically after configurator or before pipeline execution.

---

**This plan will make the EPN system truly agnostic, modular, and user-driven.**

---

## 2. Key Components

### a. Layer-Nodes Configurator

- **Purpose:** Guides the user to define the number of layers, nodes per layer, and
  LLM model per node (for all intermediate layers).

- **Output:** `layer/layer_conf.json`

- **Features:**

  - Interactive CLI or GUI wizard (`epn --create_layer`)
  - Enforces that Layer 1 and last layer are single-node and present
  - Lets user add, remove, or reorder intermediate layers and nodes
  - Lets user select LLM model for each node
  - Optionally, allows naming nodes for clarity

### b. Template Configurator

- **Purpose:** Guides the user to define prompt templates for each node in the
  configured structure.

- **Output:** `template/template.json`

- **Features:**

  - Interactive CLI or GUI wizard (`epn --create_template`)
  - Loads current `layer_conf.json` to show required nodes
  - Lets user assign or edit prompt templates for each node
  - Supports prompt inheritance or reuse for similar nodes

### c. Validation System

- **Purpose:** Ensures that every node in `layer_conf.json` has a corresponding
  prompt in `template.json` (and vice versa).

- **Features:**

  - Checks for missing or extra prompts
  - Validates required fields (e.g., LLM model, prompt text)
  - Reports mismatches and guides user to fix them

### d. Runtime Loader

- **Purpose:** At runtime, loads `layer/layer_conf.json` and `template/template.json`
  to build the EPN pipeline dynamically.

- **Features:**

  - If no config is provided, defaults to these files
  - Instantiates nodes and layers as per config
  - Ensures Layer 1 and last layer are always present and single-node

---

## 3. Workflow Overview

1. **User runs configurators:**

   - `epn --create_layer` → builds `layer/layer_conf.json`
   - `epn --create_template` → builds `template/template.json`

2. **Validation step:** System checks that all nodes have matching prompts.

3. **Production use:** User runs EPN as usual; system loads configs and builds pipeline.

4. **User can re-run configurators at any time to update structure or prompts.

---

## 4. Required System Modifications

### a. Refactor Pipeline Construction

- Remove all hardcoded layer/node logic.
- Build pipeline dynamically from `layer_conf.json`.
- Use a factory or builder pattern to instantiate nodes and layers.

### b. Refactor Template Management

- TemplateManager loads from `template/template.json`.
- Prompts are mapped to nodes by unique IDs or names.

### c. Add Configurator Modules

- New CLI entrypoints: `epn --create_layer`, `epn --create_template`
- Each configurator is a guided wizard (CLI or GUI)
- Configurators write to their respective JSON files

### d. Add Validation Logic

- New validation module checks for config-template compatibility.
- Validation runs automatically after configurator or before pipeline execution.

### e. Update Documentation

- Update README and AGENTS.md to describe new workflow.
- Provide examples of custom layer-node and template configurations.

---

## 5. Example Directory Structure

epistemic_LLM_network/
  layer/
    layer_conf.json
  template/
    template.json
  main.py
  inspect_pipeline.py
  ...

```text
epistemic_LLM_network/
  layer/
    layer_conf.json
  template/
    template.json
  main.py
  inspect_pipeline.py
  ...
```

---
