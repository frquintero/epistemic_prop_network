# Epistemological Propagation Network Flow

This document outlines the flow of inputs, outputs, and nodes for each
phase of the Epistemological Propagation Network. Each node
corresponds to an LLM call with an integrated prompt that includes
the input(s) from the previous phase and the specific task.

**Note:** LLM configurations (temperature, reasoning effort, tools) vary by phase based on the specific epistemological requirements of each layer.

---

## ~~Phase 1: Input Reformulation~~ ✅ **COMPLETED**

### Node: Reformulator

- **Task:** "Reformulate the following question to remove bias, ensure
  coherence, and add neutral context. Focus on epistemological
  clarity."
- **Input:** Raw user question.
- **Prompt:** [raw_user_question]+ [Task]
- **Expected Output:** A reformulated question that is unbiased,
  coherent, and enriched with neutral context.
- **LLM Configuration:** Medium reasoning effort, temperature 0.9, no tools

---

---

## Phase 2: Definition Generation

### Nodes: Semantic Node, Genealogical Node, Teleological Node

#### Semantic Node

- **Task:** "Provide a strict semantic definition of the concept
  described below. Include etymology, common usage, and logical
  structure."
- **Input:** Reformulated question from ~~Phase 1~~.
- **Prompt:** [reformulated_question] + [Task]
- **Expected Output:** A precise semantic definition.

#### Genealogical Node

- **Task:** "Provide a historical account of the concept described
  below. Include its origin, evolution, and key contributors."
- **Input:** Reformulated question from ~~Phase 1~~.
- **Prompt:** [reformulated_question] + [Task]
- **Expected Output:** A historical account.

#### Teleological Node

- **Task:** "Provide a functional account of the concept described
  below. Explain its purpose, utility, and practical applications."
- **Input:** Reformulated question from ~~Phase 1~~.
- **Prompt:** [reformulated_question] + [Task]
- **Expected Output:** A functional account.

---

## Phase 3: Validation

### Validation Nodes

The nodes are: Correspondence Validator, Coherence Validator, Pragmatic
Validator.

#### Correspondence Validator

- **Task:** "Validate the following outputs for empirical alignment
  with observable reality. Provide evidence-based assessments."
- **Input:** Triple `{O_s, O_g, O_t}` from Phase 2.
- **Prompt:** [triple] + [Task]
- **Expected Output:** Empirical validation results.

#### Coherence Validator

- **Task:** "Validate the following outputs for logical consistency.
  Check internal coherence and alignment with established knowledge."
- **Input:** Triple `{O_s, O_g, O_t}` from Phase 2.
- **Prompt:** [triple] + [Task]
- **Expected Output:** Logical validation results.

#### Pragmatic Validator

- **Task:** "Validate the following outputs for practical utility.
  Assess their usefulness in real-world scenarios."
- **Input:** Triple `{O_s, O_g, O_t}` from Phase 2.
- **Prompt:** [triple] + [Task]
- **Expected Output:** Practical validation results.

---

## Phase 4: Synthesis & Communication

### Node: Synthesis Node

- **Task:** "Synthesize the following validated outputs into a
  holistic narrative. Include a definition, history, function,
  validation-based qualifications, and a thesis."
- **Input:** Triple `{V_c, V_l, V_p}` from Phase 3.
- **Prompt:** [triple] + [Task]
- **Expected Output:** A comprehensive, narrative-driven answer with a
  thesis.
