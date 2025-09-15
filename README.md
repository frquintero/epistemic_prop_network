# Epistemological Propagation Network

A sophisticated multi-layer LLM system for rigorous epistemological inquiry, implementing a 4-layer propagation architecture that ensures bias-resistant, evidence-based knowledge generation.

## Overview

The Epistemological Propagation Network employs specialized agents that operate in sequence across four layers:

1. **Reformulator**: Purifies and contextualizes raw user input
2. **Definition Generation**: Creates precise conceptual definitions from semantic, genealogical, and teleological perspectives
3. **Validation**: Tests alignment with empirical evidence, logical consistency, and practical utility
4. **Synthesis**: Integrates validated insights into comprehensive narrative output

## Architecture

### Layer Structure
- **Layer 1**: Input purification and context establishment
- **Layer 2**: Multi-perspective definition generation (Semantic, Genealogical, Teleological)
- **Layer 3**: Multi-dimensional validation (Correspondence, Coherence, Pragmatic)
- **Layer 4**: Knowledge synthesis and narrative construction

### Data Flow
```
Raw Input → Layer 1 → Layer 2 → Layer 3 → Layer 4 → Final Output
```

## Features

- **Bias Resistance**: Multi-agent validation prevents single-perspective bias
- **Evidence-Based**: Correspondence validation ensures empirical grounding
- **Comprehensive**: Genealogical analysis provides historical context
- **Practical**: Teleological and pragmatic validation ensure real-world utility
- **Structured Output**: JSON-based data contracts between layers
- **Async Processing**: Concurrent LLM requests for performance
- **Robust Error Handling**: Comprehensive exception handling and retry logic

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
from core.config import init_config
from layers.layer1 import ReformulatorAgent

# Initialize configuration
init_config()

# Create and run the network
reformulator = ReformulatorAgent()
result = await reformulator.process("What are mental models?")
```

## Configuration

The system uses environment variables for configuration:

- `GROQ_API_KEY`: Your Groq API key (required)
- `GROQ_MODEL`: Model to use (default: "openai/gpt-oss-120b")
- `MAX_CONCURRENT_REQUESTS`: Concurrent requests (default: 3)
- `REQUEST_TIMEOUT`: Request timeout in seconds (default: 120.0)
- `LOG_LEVEL`: Logging level (default: "INFO")

## Development

### Project Structure
```
epistemic-llm-network/
├── core/                 # Core infrastructure
│   ├── config.py        # Configuration management
│   ├── exceptions.py    # Custom exceptions
│   ├── llm_client.py    # Groq API client
│   └── schemas.py       # Pydantic data models
├── layers/              # Agent layers
├── utils/               # Utility functions
├── tests/               # Test suite
├── pyproject.toml       # Project configuration
└── requirements.txt     # Dependencies
```

### Testing
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=core --cov=layers

# Run specific test file
pytest tests/test_core.py
```

## API Reference

### Core Classes

- `NetworkConfig`: Main configuration management
- `LLMClient`: Groq API integration with retry logic
- `Phase2Triple`: Layer 2 output data structure
- `Phase3Triple`: Layer 3 output data structure

### Agent Classes

- `ReformulatorAgent`: Layer 1 processing
- `SemanticNode`: Semantic definition generation
- `GenealogicalNode`: Historical analysis
- `TeleologicalNode`: Purpose analysis
- `CorrespondenceValidator`: Empirical validation
- `CoherenceValidator`: Logical consistency
- `PragmaticValidator`: Practical utility
- `SynthesisNode`: Final integration

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