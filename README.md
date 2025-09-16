# Epistemological Propagation Network

A sophisticated multi-layer LLM system for rigorous epistemological inquiry, implementing a 4-layer propagation architecture that ensures bias-resistant, evidence-based knowledge generation.

## Overview

The Epistemological Propagation Network employs specialized agents that operate in sequence across four layers:

1. **Reformulator** ✅: Purifies and contextualizes raw user input
2. **Definition Generation** ✅: Creates precise conceptual definitions from semantic, genealogical, and teleological perspectives
3. **Validation** 🚧: Tests alignment with empirical evidence, logical consistency, and practical utility
4. **Synthesis** 🚧: Integrates validated insights into comprehensive narrative output

## Current Implementation Status

### ✅ Completed Layers
- **Layer 1**: Input purification and context establishment (Reformulator)
- **Layer 2**: Multi-perspective definition generation (Semantic, Genealogical, Teleological nodes)

### 🚧 In Development
- **Layer 3**: Multi-dimensional validation (Correspondence, Coherence, Pragmatic validators)
- **Layer 4**: Knowledge synthesis and narrative construction

## Architecture

### Layer Structure
- **Layer 1**: Input purification and epistemological framing
- **Layer 2**: Parallel definition generation (3 specialized nodes)
- **Layer 3**: Multi-dimensional validation (3 validator types)
- **Layer 4**: Knowledge synthesis and narrative construction

### Data Flow

```mermaid
Raw Input → Layer 1 → Layer 2 (Parallel) → Layer 3 → Layer 4 → Final Output
```

## Features

- **Bias Resistance**: Multi-agent validation prevents single-perspective bias
- **Parallel Processing**: Concurrent LLM requests for Layer 2 efficiency
- **Structured Output**: Pydantic-based data contracts between layers
- **Async Processing**: High-performance concurrent operations
- **Robust Error Handling**: Comprehensive exception handling and retry logic
- **Optimized Token Usage**: 150-word response limits for efficiency
- **Clean Data Flow**: No cross-layer payload contamination

## Installation

```bash
# Clone the repository
git clone <repository-url>
cd epistemic-llm-network

# Install dependencies
pip install -r requirements.txt

# Set environment variables
export GROQ_API_KEY="your-groq-api-key-here"
```

## Usage

```python
from core.config import init_config, NetworkConfig
from layers.layer1_reformulation.reformulator import Reformulator
from layers.layer2_definition.manager import Layer2DefinitionManager

# Initialize configuration
config = init_config(NetworkConfig.from_env())

# Layer 1: Reformulate input
reformulator = Reformulator()
reformulated = await reformulator.process(user_input)

# Layer 2: Generate definitions
manager = Layer2DefinitionManager()
definitions = await manager.process(reformulated)
```

## Configuration

The system uses environment variables for configuration:

- `GROQ_API_KEY`: Your Groq API key (required)
- `GROQ_MODEL`: Model to use (default: "openai/gpt-oss-120b")
- `MAX_CONCURRENT_REQUESTS`: Concurrent requests (default: 3)
- `REQUEST_TIMEOUT`: Request timeout in seconds (default: 120.0)
- `LOG_LEVEL`: Logging level (default: "INFO")
- `MOCK_RESPONSES`: Use mock responses for testing (default: false)

## Project Structure

```
epistemic-llm-network/
├── core/                          # Core infrastructure
│   ├── config.py                 # Configuration management
│   ├── exceptions.py             # Custom exceptions
│   ├── llm_client.py             # Groq API client
│   ├── logging_config.py         # Structured logging
│   └── schemas.py                # Pydantic data models
├── layers/                       # Agent layers
│   ├── layer1_reformulation/     # Layer 1 implementation
│   │   └── reformulator.py       # Reformulator agent
│   └── layer2_definition/        # Layer 2 implementation
│       ├── semantic_node.py      # Semantic analysis
│       ├── genealogical_node.py  # Historical analysis
│       ├── teleological_node.py  # Functional analysis
│       └── manager.py            # Parallel execution manager
├── tests/                        # Test suite
├── docs/                         # Documentation
├── pyproject.toml               # Project configuration
└── requirements.txt             # Dependencies
```

## API Reference

### Core Classes

- `NetworkConfig`: Main configuration management
- `LLMClient`: Groq API integration with retry logic
- `NetworkRequest`: Input data structure
- `ReformulatedQuestion`: Layer 1 output
- `Phase2Triple`: Layer 2 output (semantic, genealogical, teleological)

### Agent Classes

- `Reformulator`: Layer 1 input purification
- `SemanticNode`: Semantic definition generation
- `GenealogicalNode`: Historical evolution analysis
- `TeleologicalNode`: Functional utility analysis
- `Layer2DefinitionManager`: Parallel execution coordinator

## Development

### Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=core --cov=layers

# Run specific test file
pytest tests/test_core.py
```

### Key Design Principles

1. **Clean Data Flow**: No cross-layer payload contamination
2. **Token Efficiency**: 150-word response limits for downstream processing
3. **Parallel Execution**: Concurrent LLM requests for performance
4. **Structured Logging**: Comprehensive request/response tracking
5. **Error Resilience**: Graceful failure handling with fallbacks

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Built using Groq's GPT-OSS-120B model
- Inspired by epistemological frameworks in cognitive science
- Designed for rigorous, bias-resistant knowledge generation
