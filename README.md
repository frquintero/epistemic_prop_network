# Epistemic LLM Network (EPN)

A multi-layered Large Language Model pipeline for epistemological analysis and narrative synthesis. The system transforms user queries through sequential layers of reformulation, definition generation, and synthesis to produce coherent epistemological narratives.

## 🏗️ Architecture

The EPN implements a **1-2-1 layered architecture**:

```
Layer 1: Reformulation (1 node)
├── Reformulator: Transforms biased questions into neutral, epistemologically-grounded inquiries

Layer 2: Definition Generation (2 nodes - parallel processing)
├── Semantic Node: Analyzes conceptual meaning and narrative motifs
└── Teleological Node: Explores functional purposes and historical contexts

Layer 3: Synthesis (1 node)
└── Synthesis Node: Combines semantic and teleological analyses into unified narratives
```

### Key Features

- **Modular Pipeline**: Configurable layers with automatic data flow
- **Template-Driven**: JSON-based prompt templates for consistent LLM interactions
- **Multi-Model Support**: Groq API integration with models like Qwen, GPT-OSS, etc.
- **Async Processing**: Concurrent node execution within layers
- **Validation Framework**: Comprehensive configuration and data flow validation
- **Extensible Design**: Easy to add new layers, nodes, and templates

## 🚀 Quick Start

### Prerequisites

- Python 3.13+
- Virtual environment support
- Groq API key

### Installation

1. **Clone and setup environment:**

   ```bash
   git clone <repository-url>
   cd epistemic_LLM_network
   source venv/bin/activate  # On Linux/Mac
   # or venv\Scripts\activate on Windows
   ```

2. **Install dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

3. **Configure API access:**

   ```bash
   # Set your Groq API key
   export GROQ_API_KEY="gsk_your_api_key_here"
   ```

### Basic Usage

**Command Line:**

```bash
python main.py "Why are all models wrong yet some are useful?"
```

**Python API:**

```python
from epn_core.core.pipeline import Pipeline

# Load and run pipeline
pipeline = Pipeline()
await pipeline.load_config()
result = await pipeline.process("Why are all models wrong yet some are useful?")
print(result)
```

**Detailed Inspection:**

```bash
python inspect_pipeline.py "Why are all models wrong yet some are useful?"
```

## 📋 Configuration

### Layer Configuration (`epn_core/config/default_layer.json`)

Defines the pipeline structure, node assignments, and LLM models:

```json
{
  "layers": [
    {
      "id": "layer1",
      "name": "Input Reformulation",
      "nodes": [
        {
          "id": "reformulator",
          "template_id": "reformulator",
          "llm_config": {
            "model": "openai/gpt-oss-20b",
            "temperature": 0.8,
            "reasoning_effort": "medium",
            "max_tokens": 8192
          }
        }
      ]
    }
  ]
}
```

### Template Configuration (`epn_core/config/default_template.json`)

Defines prompt templates with placeholders for dynamic content:

```json
{
  "templates": {
    "reformulator": {
      "placeholders": ["question", "context_info"],
      "content": "You are an epistemological reformulator...\n\nORIGINAL QUESTION: {question}{context_info}\n\nREFORMULATED QUESTION:"
    }
  }
}
```

## 🔧 Development

### Project Structure

```
epistemic_LLM_network/
├── epn_core/                    # Core system modules
│   ├── cli/                     # Command-line interfaces
│   ├── config/                  # Configuration files
│   ├── core/                    # Core pipeline logic
│   └── utils/                   # Utilities
├── tests/                       # Test suite
├── main.py                      # Main entry point
├── inspect_pipeline.py          # Detailed inspection tool
├── minimal_runner.py            # Simple test runner
└── requirements.txt             # Python dependencies
```

### Testing

Run the complete test suite:

```bash
pytest tests/
```

Run specific test categories:

```bash
pytest tests/test_core.py        # Core functionality
pytest tests/test_layer2_definition.py  # Definition layer
pytest tests/test_layer3_validation.py  # Validation layer
```

### Code Quality

Format and lint code:

```bash
black .                          # Format code
isort .                          # Sort imports
flake8 .                         # Lint code
mypy .                           # Type check
```

## 📚 API Reference

### Pipeline Class

```python
class Pipeline:
    async def load_config(self, layer_file: str, template_file: str) -> None
    async def process(self, input_data: Any) -> Any
    def add_layer(self, layer: Layer, position: Optional[int] = None) -> None
    def get_layer(self, layer_id: str) -> Layer
```

### Node Classes

```python
class BasicLLMNode:
    def __init__(self, config: NodeConfig, template: Dict, llm_client: LLMClient)
    async def process(self, input_data: Any) -> str
```

### Configuration Classes

```python
@dataclass
class LLMConfig:
    model: str
    temperature: float
    reasoning_effort: str  # 'low', 'medium', 'high'
    max_tokens: int

@dataclass
class NodeConfig:
    node_id: str
    template_id: str
    llm_config: LLMConfig
```

## 🤝 Contributing

### Development Workflow

1. **Fork** the repository
2. **Create** a feature branch: `git checkout -b feature/your-feature`
3. **Make** your changes with tests
4. **Run** tests: `pytest tests/`
5. **Format** code: `black . && isort .`
6. **Commit** changes: `git commit -m "feat: add your feature"`
7. **Push** branch: `git push origin feature/your-feature`
8. **Create** pull request

### Guidelines

- **Commits**: Use conventional commits (`feat:`, `fix:`, `docs:`, etc.)
- **Tests**: Maintain >90% coverage, test both success and failure paths
- **Documentation**: Update README and docstrings for API changes
- **Code Style**: Follow PEP 8 with 88-character line limits
- **Security**: Never commit API keys or sensitive credentials

### Adding New Layers/Nodes

1. **Define** template in `default_template.json`
2. **Configure** layer in `default_layer.json`
3. **Implement** node logic if needed
4. **Add** tests for new functionality
5. **Update** documentation

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Built with [Groq API](https://groq.com/) for fast LLM inference
- Inspired by epistemological theories and narrative analysis
- Uses [Pydantic](https://pydantic-docs.helpmanual.io/) for data validation
- Async processing with Python's `asyncio`

## 📞 Support

For questions, issues, or contributions:

- **Issues**: GitHub Issues
- **Discussions**: GitHub Discussions
- **Email**: [your-email@example.com](mailto:your-email@example.com)

---

**Epistemic LLM Network** - Transforming questions into epistemological narratives through layered AI analysis.
