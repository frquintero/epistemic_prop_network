# Epistemic LLM Network Agents

This document describes the agent architecture for the Epistemic LLM Network, detailing the roles, responsibilities, and interactions of each agent within the four-layer propagation system.

## Agent Overview

The network employs specialized agents that operate in sequence across four layers:

| Layer | Agent Type | Role |
|-------|------------|------|
| 1 | Reformulator | Purifies and contextualizes raw user input |
| 2 | Semantic Node | Generates precise conceptual definitions |
| 2 | Genealogical Node | Traces historical evolution of concepts |
| 2 | Teleological Node | Analyzes purpose and functional utility |
| 3 | Correspondence Validator | Tests alignment with empirical evidence |
| 3 | Coherence Validator | Ensures logical consistency |
| 3 | Pragmatic Validator | Evaluates real-world applicability |
| 4 | Synthesis Node | Integrates validated insights into narrative output |

## Agent Responsibilities

### Layer 1: Reformulator Agent

- Accepts raw user questions (e.g., "What are mental models?")
- Eliminates bias, loaded language, and framing effects
- Distills the core epistemological intent (definition, history, function)
- Adds neutral factual context without providing answers
- Outputs a refined, context-aware question for downstream processing

### Layer 2: Definition Generation Agents

#### Semantic Node

- Focuses on linguistic structure, etymology, and logical relationships
- Produces a strict conceptual definition
- Example output: "A mental model is an internal, simplified cognitive representation of an external system or process, used for understanding, reasoning, and prediction."

#### Genealogical Node

- Traces the historical origin and evolution of concepts
- Identifies key contributors and paradigm shifts
- Example output: "The concept was formally introduced by Kenneth Craik in 1943, expanded by Philip Johnson-Laird in human reasoning, and popularized in decision-making by Charlie Munger."

#### Teleological Node

- Analyzes purpose, utility, and functional role
- Evaluates how the concept enables action or problem-solving
- Example output: "The primary function of mental models is to allow individuals to simulate outcomes, form explanations, and make decisions efficiently without direct experience, thus navigating complexity."

### Layer 3: Validation Agents

#### Correspondence Validator

- Tests whether outputs align with observable reality
- Validates against scientific evidence, historical records, and empirical studies
- Returns verdicts indicating which aspects are empirically supported

#### Coherence Validator

- Assesses internal logical consistency
- Checks if definitions follow from historical development
- Verifies functional claims cohere with established theories

#### Pragmatic Validator

- Evaluates practical utility in real-world contexts
- Assesses value in domains like education, business, and cognitive science
- Determines actionable insights derived from the conceptual framework

### Layer 4: Synthesis Agent

- Integrates validated outputs from all previous layers
- Constructs a cohesive narrative connecting definition, history, function, and validation
- Builds meaningful connections between concepts and disciplines
- Formulates a concise thesis statement encapsulating the core insight
- Delivers a comprehensive, nuanced answer with context, qualification, and value

## Agent Interactions

- Strictly feed-forward flow: Output of one layer becomes input to the next
- No feedback loops or lateral communication between agents in the same layer
- Each agent operates independently on the same input from the prior layer
- Final synthesis combines all validated perspectives into a unified output

## Data Formats and Serialization

### Triple Structure

The network uses structured JSON containers for data passing between layers, while allowing rich, unstructured narrative content within each element:

#### Phase 2 Output Triple

```json
{
  "semantic": "Unstructured narrative text from Semantic Node...",
  "genealogical": "Unstructured narrative text from Genealogical Node...",
  "teleological": "Unstructured narrative text from Teleological Node..."
}
```

#### Phase 3 Output Triple

```json
{
  "correspondence": "Unstructured validation narrative from Correspondence Validator...",
  "coherence": "Unstructured validation narrative from Coherence Validator...",
  "pragmatic": "Unstructured validation narrative from Pragmatic Validator..."
}
```

### Hybrid Approach Benefits

- **Structured Containers**: JSON schema ensures data integrity and reliable parsing between layers
- **Unstructured Content**: Preserves rich, narrative-driven LLM outputs without forced formatting constraints
- **Type Safety**: Pydantic models validate container structure while allowing flexible content
- **Maintainability**: Clear data contracts between layers with adaptable content formats

This agent architecture ensures rigorous, bias-resistant epistemological inquiry while delivering rich, narrative-driven insights.

## Documentation

This project includes comprehensive documentation covering all aspects of the Epistemological Propagation Network:

### Core Documentation

- **README.md** - Main project readme with setup and usage instructions
- **AGENTS.md** - Agent architecture documentation (this file)
- **architecture.md** - System architecture overview
- **project_concept.md** - Project concept and vision

### Development & Planning

- **build_plan.md** - Development roadmap and current status
- **implementation_plan.md** - Implementation details and technical specifications
- **layered_architecture_plan.md** - Detailed layered architecture plan
- **network_flow.md** - Data flow specifications between layers

### Technical Documentation

- **REAL_LLM_TESTING_README.md** - Testing documentation and LLM integration guide
- **gpt-oss-120b-guide.md** - LLM integration guide for Groq GPT-OSS-120B model

### Additional Resources

- **docs/examples/demonstrate_pydantic.py** - Pydantic model examples and demonstrations
- **test_results/** - Generated test reports and LLM interaction details
