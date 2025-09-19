# Epistemological Propagation Network - OOP Architecture Design

## Core Classes

### LLMClient

- **Purpose**: Client for interacting with LLM APIs (Groq)
- **Attributes**:
  - `config`: LLMConfig instance with model, temperature, reasoning_effort, max_tokens
  - `client`: Groq API client instance
- **Methods**:
  - `generate(prompt: str) -> str`: Generate response from LLM with automatic reasoning_format handling for Qwen models

### BasicLLMNode

- **Purpose**: Core LLM processing unit that handles template rendering and API calls
- **Attributes**:
  - `config`: NodeConfig with node_id, template_id, llm_config
  - `template`: Template dictionary with content and placeholders
  - `llm_client`: LLMClient instance
- **Methods**:
  - `process(input_data) -> str`: Process input through template rendering and LLM call
  - `_prepare_variables(input_data) -> dict`: Map input data to template placeholders

### Layer

- **Purpose**: Container and orchestrator for nodes within a processing layer
- **Attributes**:
  - `config`: LayerConfig with layer_id, name, description, nodes
  - `nodes`: Dictionary of node_id -> Node instances
- **Methods**:
  - `add_node(node)`: Add a node to the layer
  - `process(input_data) -> dict`: Process input through all nodes (parallel execution)
  - `get_node(node_id) -> Node`: Retrieve specific node

### Pipeline

- **Purpose**: Main orchestrator managing the flow between layers with automatic data mapping
- **Attributes**:
  - `layers`: Dictionary of layer_id -> Layer instances
  - `layer_order`: Ordered list of layer IDs for processing sequence
  - `config_loader`: ConfigLoader instance
  - `template_manager`: TemplateManager instance
  - `validator`: Validator instance
  - `node_factory`: NodeFactory instance
- **Methods**:
  - `load_config(layer_file, template_file)`: Load and validate configuration files
  - `process(input_data) -> dict`: Execute full pipeline with automatic layer transitions
  - `_prepare_input_for_next_layer()`: Generic mapping of layer outputs to next layer inputs
  - `add_layer(layer, position)`: Add layer to pipeline
  - `get_layer(layer_id) -> Layer`: Retrieve specific layer

### ConfigLoader

- **Purpose**: Load and parse JSON configuration files
- **Methods**:
  - `load_layer_config(file_path) -> PipelineConfig`: Load layer configuration
  - `load_template_config(file_path) -> dict`: Load template configuration

### TemplateManager

- **Purpose**: Manage prompt templates and variable substitution
- **Attributes**:
  - `templates`: Dictionary of template_id -> template data
- **Methods**:
  - `load_templates(template_config)`: Load templates from configuration
  - `get_template(template_id) -> dict`: Retrieve template by ID
  - `render_template(template, variables) -> str`: Substitute variables in template content

### NodeFactory

- **Purpose**: Factory for creating node instances from configuration
- **Attributes**:
  - `template_manager`: TemplateManager instance
- **Methods**:
  - `create_node(node_config) -> BasicLLMNode`: Create and configure node instance

### Validator

- **Purpose**: Validate configuration compatibility and data flow integrity
- **Methods**:
  - `validate_complete_config(layer_config, template_config)`: Comprehensive validation
  - `validate_layer_template_compatibility()`: Ensure nodes have required templates
  - `validate_pipeline_flow()`: Verify data can flow between layers
  - `validate_llm_configs()`: Check LLM configuration validity
  - `templates`: Dict of template_id -> template_data
- **Methods**:
  - `get_template(node_id) -> dict`: Get template for a node
  - `render_template(template_id, variables) -> str`: Substitute variables
  - `validate_templates()`: Ensure all required templates exist

### Validator
- **Purpose**: Validate configuration compatibility and data flow integrity
- **Methods**:
  - `validate_complete_config(layer_config, template_config)`: Comprehensive validation
  - `validate_layer_template_compatibility()`: Ensure nodes have required templates
  - `validate_pipeline_flow()`: Verify data can flow between layers
  - `validate_llm_configs()`: Check LLM configuration validity

## Data Flow Architecture

The EPN implements a **1-2-1 layered architecture** with automatic data mapping:

```
Raw Query → Layer 1 (Reformulator) → Reformulated Question
                                      ↓
                 Reformulated Question → Layer 2 (Parallel Processing)
                                      ↓
                 Layer 2 Outputs → Layer 3 (Synthesis) → Final Narrative
                 ├── semantic_output → Synthesis Node
                 └── teleological_output → Synthesis Node
```

### Key Data Flow Features

- **Automatic Mapping**: Pipeline automatically maps layer outputs to next layer inputs based on template placeholders
- **Parallel Processing**: Layer 2 executes semantic and teleological nodes concurrently
- **Template-Driven**: All prompts use JSON templates with variable substitution
- **Generic Architecture**: Works for any number of layers and nodes with proper configuration

## Configuration Schema

### default_layer.json
```json
{
  "layers": [
    {
      "id": "layer1",
      "name": "Input Reformulation",
      "description": "Purifies and contextualizes raw user input",
      "nodes": [
        {
          "id": "reformulator",
          "name": "Reformulator",
          "type": "reformulator",
          "template_id": "reformulator",
          "description": "Bias elimination and epistemic contextualization",
          "llm_config": {
            "model": "openai/gpt-oss-20b",
            "temperature": 0.8,
            "reasoning_effort": "medium",
            "max_tokens": 8192
          }
        }
      ]
    },
    {
      "id": "layer2",
      "name": "Definition Generation",
      "description": "Parallel generation of semantic and teleological definitions",
      "nodes": [
        {
          "id": "semantic_node",
          "name": "Semantic Node",
          "type": "semantic",
          "template_id": "semantic_node",
          "description": "Linguistic structure and conceptual definitions",
          "llm_config": {
            "model": "qwen/qwen3-32b",
            "temperature": 0.8,
            "reasoning_effort": "medium",
            "max_tokens": 8192
          }
        },
        {
          "id": "teleological_node",
          "name": "Teleological Node",
          "type": "teleological",
          "template_id": "teleological_node",
          "description": "Functional purpose and practical applications",
          "llm_config": {
            "model": "openai/gpt-oss-120b",
            "temperature": 0.8,
            "reasoning_effort": "medium",
            "max_tokens": 8192
          }
        }
      ]
    },
    {
      "id": "layer3",
      "name": "Synthesis",
      "description": "Comprehensive synthesis of all analyses",
      "nodes": [
        {
          "id": "synthesis_node",
          "name": "Synthesis Node",
          "type": "synthesis",
          "template_id": "synthesis_node",
          "description": "Unified narrative synthesis",
          "llm_config": {
            "model": "openai/gpt-oss-120b",
            "temperature": 0.8,
            "reasoning_effort": "high",
            "max_tokens": 8192
          }
        }
      ]
    }
  ]
}
```

### default_template.json
```json
{
  "templates": {
    "reformulator": {
      "description": "Template for query reformulation",
      "placeholders": ["question", "context_info"],
      "content": "You are an epistemological reformulator...\n\nORIGINAL QUESTION: {question}{context_info}\n\nREFORMULATED QUESTION:"
    },
    "semantic_node": {
      "description": "Template for semantic definition generation",
      "placeholders": ["reformulated_question"],
      "content": "You are a semantic epistemologist...\n\nREFORMULATED QUESTION: {reformulated_question}\n\nSEMANTIC NARRATIVE:"
    },
    "teleological_node": {
      "description": "Template for teleological definition generation",
      "placeholders": ["reformulated_question"],
      "content": "You are a functional epistemologist...\n\nREFORMULATED QUESTION: {reformulated_question}\n\nTELEOLOGICAL PLOT:"
    },
    "synthesis_node": {
      "description": "Template for comprehensive synthesis",
      "placeholders": ["semantic_output", "teleological_output"],
      "content": "You are a master synthesizer...\n\nSEMANTIC OUTPUT: {semantic_output}\n\nTELEOLOGICAL OUTPUT: {teleological_output}\n\nEMERGENT NARRATIVE SYNTHESIS:"
    }
  }
}
```

## Key Design Principles

1. **Composition over Inheritance**: Pipeline composes Layers, Layers compose Nodes
2. **Dependency Injection**: All components receive dependencies through constructor injection
3. **Single Responsibility**: Each class has one clear purpose (LLMClient for API calls, BasicLLMNode for processing, etc.)
4. **Dynamic Construction**: Pipeline built from JSON configuration at runtime
5. **Validation First**: Configurations validated before pipeline construction
6. **Generic Data Flow**: Automatic mapping between layers based on template placeholders
7. **Extensibility**: Easy to add new node types, layers, or execution modes
8. **Template-Driven**: All prompts managed through JSON templates with variable substitution
9. **Async Processing**: Concurrent node execution within layers for performance