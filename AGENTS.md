# Epistemic LLM Network Agents

This document describes the agent architecture for the Epistemic LLM Network, detailing the roles, responsibilities, and interactions of each agent within the four-layer propagation system.

## Implementation Status

### ✅ Completed Layers
- **Layer 1**: Reformulator Agent (Fully implemented)
- **Layer 2**: Definition Generation Agents (Fully implemented)
  - Semantic Node ✅
  - Genealogical Node ✅
  - Teleological Node ✅
- **Layer 3**: Validation Agents (Fully implemented)
  - Correspondence Validator ✅
  - Coherence Validator ✅
  - Pragmatic Validator ✅

### 🚧 In Development
- **Layer 4**: Synthesis Node (Planned)

## Agent Overview

The network employs specialized agents that operate in sequence across four layers:

| Layer | Agent Type | Status | Role |
|-------|------------|--------|------|
| 1 | Reformulator | ✅ | Purifies and contextualizes raw user input |
| 2 | Semantic Node | ✅ | Generates precise conceptual definitions |
| 2 | Genealogical Node | ✅ | Traces historical evolution of concepts |
| 2 | Teleological Node | ✅ | Analyzes purpose and functional utility |
| 3 | Correspondence Validator | 🚧 | Tests alignment with empirical evidence |
| 3 | Coherence Validator | 🚧 | Ensures logical consistency |
| 3 | Pragmatic Validator | 🚧 | Evaluates real-world applicability |
| 4 | Synthesis Node | 🚧 | Integrates validated insights into narrative output |

## Current Implementation Details

### Layer 1: Reformulator Agent ✅

**Status**: Fully implemented and tested
**Location**: `layers/layer1_reformulation/reformulator.py`

**Responsibilities**:
- Accepts raw user questions (e.g., "What are mental models?")
- Eliminates bias, loaded language, and framing effects
- Distills the core epistemological intent (definition, history, function)
- Crafts optimized LLM prompts with comprehensive bias analysis framework
- Outputs reformulated, context-aware questions with ~150-word limit for efficiency

**Key Features**:
- Advanced bias detection and elimination
- Epistemological context embedding
- Structured prompt engineering
- Async processing with error handling
- Clean data output (no cross-layer payload)

### Layer 2: Definition Generation Agents ✅

**Status**: Fully implemented with parallel processing
**Location**: `layers/layer2_definition/`
**Architecture**: Concurrent execution using `asyncio.gather`

#### Semantic Node ✅
**Location**: `layers/layer2_definition/semantic_node.py`

**Responsibilities**:
- Focuses on linguistic structure, etymology, and logical relationships
- Produces strict conceptual definitions with academic rigor
- Includes etymological analysis and semantic field mapping
- Maintains ~150-word response limit for efficiency

**Example Output**: Comprehensive semantic analysis of "mental model" including Latin etymology (*mens*, *modellus*), grammatical structure, and logical hierarchies.

#### Genealogical Node ✅
**Location**: `layers/layer2_definition/genealogical_node.py`

**Responsibilities**:
- Traces historical origin and evolution of concepts
- Identifies key contributors and paradigm shifts
- Provides chronological historical narratives
- Connects concepts to broader intellectual movements

**Example Output**: Historical account from Aristotle (350 BCE) through modern cognitive neuroscience, including key figures like Craik, Johnson-Laird, and contemporary researchers.

#### Teleological Node ✅
**Location**: `layers/layer2_definition/teleological_node.py`

**Responsibilities**:
- Analyzes purpose, utility, and functional role
- Evaluates practical applications in real-world contexts
- Explains how concepts enable action and problem-solving
- Connects to human cognitive and behavioral processes

**Example Output**: Functional analysis of mental models as cognitive tools for prediction, decision-making, and problem-solving across education, design, and organizational contexts.

### Layer 2 Parallel Execution ✅
**Location**: `layers/layer2_definition/manager.py`

**Features**:
- Concurrent processing of all three nodes using `asyncio.gather`
- Error handling with fallback responses
- Structured output in `Phase2Triple` format
- Performance optimization with ~1.2 second execution time
- Clean data flow without cross-contamination

### Layer 3: Validation Agents ✅

**Status**: Fully implemented with parallel processing
**Location**: `layers/layer3_validation/`
**Architecture**: Concurrent execution using `asyncio.gather`

#### Correspondence Validator ✅
**Location**: `layers/layer3_validation/correspondence_validator.py`

**Responsibilities**:
- Tests whether outputs align with observable reality
- Validates against scientific evidence, historical records, and empirical studies
- Returns verdicts indicating which aspects are empirically supported
- Provides evidence-based assessments with specific citations

**Example Output**: Detailed empirical validation of philosophical claims, identifying historically accurate elements while noting speculative scientific proposals that remain unverified.

#### Coherence Validator ✅
**Location**: `layers/layer3_validation/coherence_validator.py`

**Responsibilities**:
- Assesses internal logical consistency across all components
- Checks if definitions follow from historical development
- Verifies functional claims cohere with established theories
- Identifies logical gaps, circularities, or contradictions

**Example Output**: Analysis of how semantic definitions, historical narratives, and functional claims interlock, identifying subtle circularities while confirming overall logical consistency.

#### Pragmatic Validator ✅
**Location**: `layers/layer3_validation/pragmatic_validator.py`

**Responsibilities**:
- Evaluates practical utility in real-world contexts
- Assesses value in domains like education, business, and cognitive science
- Determines actionable insights derived from the conceptual framework
- Translates abstract concepts into concrete applications

**Example Output**: Practical applications in education (curricula design), business (risk assessment), and policy (evidence-based decision-making), showing how philosophical frameworks yield actionable tools.

### Layer 3 Parallel Execution ✅
**Location**: `layers/layer3_validation/manager.py`

**Features**:
- Concurrent processing of all three validation agents using `asyncio.gather`
- Error handling with fallback responses for individual validator failures
- Structured output in `Phase3Triple` format
- Performance optimization with ~1.5 second execution time
- Clean data flow from Phase2Triple to Phase3Triple

## Agent Responsibilities

### Layer 1: Reformulator Agent

- Accepts raw user questions (e.g., "What are mental models?")
- Eliminates bias, loaded language, and framing effects
- Distills the core epistemological intent (definition, history, function)
- Crafts a single LLM prompt that instructs the model to perform internal validation and generate neutral epistemic context
- Outputs the LLM's reformulated, context-aware question with LLM's own validation (no external validation layer)

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

## Development Environment & Testing

### Virtual Environment Setup

The project uses a Python virtual environment to manage dependencies and isolate the development environment.

```bash
# Navigate to the project directory
cd epistemic-llm-network

# Activate the virtual environment
source venv/bin/activate

# Dependencies are pre-installed in the virtual environment
# If you need to reinstall, run:
pip install -r requirements.txt
```

### API Configuration

The system requires a Groq API key to function. Here's how to get and configure it:

#### Getting a Groq API Key

1. **Sign up at Groq**: Go to <https://console.groq.com/>
2. **Create an account**: Sign up with your email or GitHub account
3. **Generate API key**:
   - Go to the "API Keys" section in your dashboard
   - Click "Create API Key"
   - Copy the key (it starts with `gsk_`)

#### Setting Up the Environment

The system loads the API key from an external environment file for security:

```bash
# Check if the environment file exists
ls ~/.config/env.d/ai.env

# If it doesn't exist, create the directory and file
mkdir -p ~/.config/env.d/
echo 'export GROQ_API_KEY=gsk_your_actual_groq_api_key_here' > ~/.config/env.d/ai.env

# The .zshrc file should already contain this line to auto-load the environment:
# if [[ -r "$HOME/.config/env.d/ai.env" ]]; then
#   source "$HOME/.config/env.d/ai.env"
# fi
```

#### Activating the Environment

```bash
# Activate the virtual environment
source venv/bin/activate

# Load the API key (if not auto-loaded by .zshrc)
source ~/.config/env.d/ai.env

# Verify the API key is loaded
echo "GROQ_API_KEY: $GROQ_API_KEY"
```

**Note**: The API key should start with `gsk_` - if you see `your-groq-api-key-here`, it's still a placeholder.

### Running the Application

#### Main Interactive Interface

```bash
# Activate virtual environment and load API key
source venv/bin/activate
source ~/.config/env.d/ai.env

# Run the main application (interactive mode)
python main.py

# Or run with a specific question
python main.py "What is artificial intelligence?"
```

**Expected Output**: The system will process your question through all 4 layers and display the **raw Layer 4 synthesis output** - a comprehensive epistemological narrative as originally planned in the build documents.

### Running Tests

#### Live End-to-End Test

Run a complete 4-layer test with the Tezcatlipoca question:

```bash
# Activate virtual environment and load API key
source venv/bin/activate
source ~/.config/env.d/ai.env

# Run the live test
python live_test_tezcatlipoca.py
```

**Expected Output**: A comprehensive epistemological analysis processing through all 4 layers in ~8 seconds, including:

- Layer 1: Question reformulation
- Layer 2: Parallel definition generation (semantic, genealogical, teleological)
- Layer 3: Multi-dimensional validation (correspondence, coherence, pragmatic)
- Layer 4: Synthesis and narrative integration

#### Unit Tests

Run individual layer tests:

```bash
# Run all tests
pytest

# Run specific layer tests
pytest tests/test_layer1_reformulator.py
pytest tests/test_layer2_definition.py
pytest tests/test_layer3_validation.py
pytest tests/test_layer4_synthesis.py

# Run with coverage
pytest --cov=core --cov=layers
```

#### Custom Test Questions

To test with different questions, modify the `question` variable in `live_test_tezcatlipoca.py`:

```python
# Example: Test with a different question
question = "What is the significance of quantum entanglement in modern physics?"
```

### Test Results Interpretation

Successful test output includes:

- **Performance metrics**: Layer-by-layer timing (typically 1-4 seconds each)
- **Raw Layer 4 output**: Complete holistic narrative synthesis as originally planned
- **Total processing time**: Usually 6-10 seconds for complete 4-layer processing
- **Error-free execution**: No exceptions or API failures

### Troubleshooting

**Common Issues:**

- **Missing API Key**: Ensure `GROQ_API_KEY` environment variable is set in `~/.config/env.d/ai.env`
- **Invalid API Key**: Verify your key starts with `gsk_` and is active in your Groq console
- **Virtual Environment**: Always activate venv before running tests
- **Dependencies**: Run `pip install -r requirements.txt` if import errors occur
- **Network Issues**: Check internet connection for Groq API access

**Performance Notes:**

- Layer 2 and 3 use parallel processing for optimal performance
- Layer 4 synthesis may take longer due to complex narrative integration
- Total processing time scales with question complexity

## Documentation

This project includes comprehensive documentation covering all aspects of the Epistemological Propagation Network:

### Core Documentation

- **README.md** - Main project readme with setup and usage instructions
- **AGENTS.md** - Agent architecture documentation (this file)
- **architecture.md** - System architecture overview
- **project_concept.md** - Project concept and vision

### Development & Planning

- **build_plan_and_flow.md** - Build plan, development roadmap, and data flow specifications
- **implementation_plan.md** - Implementation details and technical specifications
- **layered_architecture_plan.md** - Detailed layered architecture plan
- **build_plan_and_flow.md** - Build plan and data flow specifications between layers

### Technical Documentation

- **REAL_LLM_TESTING_README.md** - Testing documentation and LLM integration guide
- **gpt-oss-120b-guide.md** - LLM integration guide for Groq GPT-OSS-120B model

### Additional Resources

- **docs/examples/demonstrate_pydantic.py** - Pydantic model examples and demonstrations
- **test_results/** - Generated test reports and LLM interaction details
