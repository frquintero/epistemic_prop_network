# Epistemological Propagation Network

A multi-layer LLM system for rigorous epistemological inquiry, implementing a propagation architecture that fosters bias-resistant, evidence-based knowledge generation.

## Overview

The Epistemological Propagation Network employs specialized agents operating sequentially across four layers:

1. **Reformulator** ✅ – Purifies and contextualizes raw user input
2. **Definition Generation** ✅ – Produces semantic, genealogical, and teleological definitions in parallel
3. **Validation** ✅ – Tests correspondence, coherence, and pragmatic soundness of generated definitions
4. **Synthesis** 🚧 – Integrates validated insights into a cohesive narrative output

## Current Implementation Status

### ✅ Completed Layers
- **Layer 1**: Input purification and context establishment (Reformulator)
- **Layer 2**: Multi-perspective definition generation (Semantic, Genealogical, Teleological nodes)
- **Layer 3**: Multi-dimensional validation (Correspondence, Coherence, Pragmatic validators)

### 🚧 In Development
- **Layer 4**: Knowledge synthesis and narrative construction

## Architecture

### Layer Structure
- **Layer 1**: Input purification and epistemological framing
- **Layer 2**: Parallel definition generation (three specialized nodes)
- **Layer 3**: Multi-dimensional validation (three validator types)
- **Layer 4**: Knowledge synthesis and narrative construction

### Data Flow

```mermaid
Raw Input → Layer 1 → Layer 2 (Parallel) → Layer 3 → Layer 4 → Final Output
```

## Features

- **Bias Resistance**: Multi-agent validation avoids single-perspective bias
- **Parallel Processing**: Concurrent LLM requests for Layer 2 efficiency
- **Structured Output**: Pydantic-based data contracts between layers
- **Async Processing**: High-performance concurrent operations
- **Robust Error Handling**: Comprehensive exception handling and retry logic
- **Optimized Token Usage**: Layer 2 definitions and Layer 3 validations stay within ~150 words for downstream efficiency
- **Clean Data Flow**: No cross-layer payload contamination

## Installation & Environment Setup

```bash
# Clone the repository
git clone <repository-url>
cd epistemic-llm-network

# Activate the bundled virtual environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure Groq credentials (example)
mkdir -p ~/.config/env.d/
echo 'export GROQ_API_KEY=gsk_your_actual_groq_api_key_here' > ~/.config/env.d/ai.env
source ~/.config/env.d/ai.env  # ensure the key is loaded
```

Verify the key with `echo $GROQ_API_KEY`. Keep credential files out of version control.

## Usage

Run the full pipeline via the CLI or programmatically:

```bash
# CLI entry points
python main.py "What are mental models?"
python cli.py --question "What is epistemology?"
```

```python
import asyncio

from core.config import init_config, NetworkConfig
from layers.layer1_reformulation.reformulator import Reformulator
from layers.layer2_definition.manager import Layer2DefinitionManager
from layers.layer3_validation.manager import Layer3ValidationManager

async def run_pipeline(user_input: str):
    config = init_config(NetworkConfig.from_env())

    reformulator = Reformulator(config=config)
    reformulated = await reformulator.process(user_input)

    definitions_manager = Layer2DefinitionManager(config=config)
    definitions = await definitions_manager.process(reformulated)

    validation_manager = Layer3ValidationManager(config=config)
    validations = await validation_manager.process(definitions)
    return validations

asyncio.run(run_pipeline("What are mental models?"))
```

## Configuration

The system reads configuration from environment variables:

- `GROQ_API_KEY`: Groq API key (required)
- `GROQ_MODEL`: Model identifier (default: `openai/gpt-oss-120b`)
- `MAX_CONCURRENT_REQUESTS`: Max concurrent requests (default: 3)
- `REQUEST_TIMEOUT`: Request timeout in seconds (default: 120.0)
- `LOG_LEVEL`: Logging verbosity (default: `INFO`)
- `MOCK_RESPONSES`: Toggle mocked responses for tests (default: `false`)

## Project Structure

```
epistemic-llm-network/
├── core/                          # Core infrastructure (config, logging, schemas)
├── layers/                        # Layered agents
│   ├── layer1_reformulation/      # Layer 1 implementation
│   ├── layer2_definition/         # Layer 2 nodes and manager
│   └── layer3_validation/         # Layer 3 validators and manager
├── tests/                         # Async unit and integration tests
├── docs/                          # Supplemental documentation
├── AGENTS.md                      # Contributor guidelines
├── main.py / cli.py / api.py      # Entry points
├── pyproject.toml                 # Tooling configuration
└── requirements.txt               # Dependencies
```

## API Reference

### Core Classes

- `NetworkConfig`: Configuration management
- `LLMClient`: Groq API integration with retry logic
- `NetworkRequest`: Input data structure
- `ReformulatedQuestion`: Layer 1 output
- `Phase2Triple`: Layer 2 output (semantic, genealogical, teleological)
- `Phase3Triple`: Layer 3 output (correspondence, coherence, pragmatic)

### Agent Classes

- `Reformulator`: Layer 1 input purification
- `SemanticNode`: Semantic definition generation
- `GenealogicalNode`: Historical evolution analysis
- `TeleologicalNode`: Functional utility analysis
- `Layer2DefinitionManager`: Parallel execution coordinator
- `CorrespondenceValidator`, `CoherenceValidator`, `PragmaticValidator`: Layer 3 validators
- `Layer3ValidationManager`: Validation orchestrator

## Development

### Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=core --cov=layers

# Run a specific test file
pytest tests/test_layer3_validation.py
```

### Key Design Principles

1. **Clean Data Flow**: No cross-layer payload contamination
2. **Token Efficiency**: Enforce ~150-word limits for Layers 2–3 and cap synthesis at 800 words
3. **Parallel Execution**: Concurrent LLM requests for performance
4. **Structured Logging**: Comprehensive request/response tracking
5. **Error Resilience**: Graceful failure handling with fallbacks

## Contributing

1. Fork the repository
2. Create a feature branch
3. Implement your changes with tests
4. Run `pytest` and linting tools before submission
5. Submit a pull request detailing context and validation steps

## License

This project is licensed under the MIT License – see the `LICENSE` file for details.

## Acknowledgments

- Built using Groq's GPT-OSS-120B model
- Inspired by epistemological frameworks in cognitive science
- Designed for rigorous, bias-resistant knowledge generation
