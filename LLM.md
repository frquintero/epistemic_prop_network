# LLM Models Configuration Guide

## Overview

This document provides detailed information about the available Large Language Models (LLMs) on Groq that can be used in the Epistemological Propagation Network (EPN). Each model has specific characteristics, pricing, performance metrics, and optimal use cases for different EPN layers.

## Available Models

### 1. OpenAI GPT-OSS-120B (`openai/gpt-oss-120b`)

**Status**: Production Model  
**Provider**: OpenAI  
**Token Speed**: ~500 TPS  

#### GPT-OSS-120B Specifications

- **Context Window**: 131,072 tokens
- **Max Output Tokens**: 65,536
- **Architecture**: Mixture-of-Experts (MoE) with 120B total parameters
- **Active Parameters**: ~37B per forward pass
- **Quantization**: Groq TruePoint Numerics

#### GPT-OSS-120B Pricing (per 1M tokens)

- Input: $0.15
- Output: $0.75
- Cached Input: $0.075

#### GPT-OSS-120B Performance

- MMLU (General Reasoning): 87.3%
- SWE-Bench Verified (Coding): 63.7%
- AIME 2025 (Math): 98.7%
- MMMLU (Multilingual): 76.7% average

#### GPT-OSS-120B Capabilities

- Tool Use
- Browser Search
- Code Execution
- JSON Object/Schema Mode
- Reasoning (low/medium/high)
- Long-context processing

#### GPT-OSS-120B EPN Use Cases

- **Layer 4 (Synthesis)**: Complex integration and narrative synthesis
- **Layer 3 (Validation)**: Rigorous coherence and correspondence validation
- **High-complexity reasoning tasks**

#### GPT-OSS-120B Configuration

```json
{
  "model": "openai/gpt-oss-120b",
  "temperature": 0.6,
  "max_tokens": 4000,
  "reasoning_effort": "high",
  "top_p": 1.0
}
```

---

### 2. OpenAI GPT-OSS-20B (`openai/gpt-oss-20b`)

**Status**: Production Model  
**Provider**: OpenAI  
**Token Speed**: ~1000 TPS  

#### GPT-OSS-20B Specifications

- **Context Window**: 131,072 tokens
- **Max Output Tokens**: 65,536
- **Architecture**: Mixture-of-Experts (MoE) with 20B total parameters
- **Active Parameters**: 3.6B per forward pass
- **Quantization**: Groq TruePoint Numerics

#### GPT-OSS-20B Pricing (per 1M tokens)

- Input: $0.10 ($1 per 10M)
- Output: $0.50 ($1 per 2M)
- Cached Input: $0.05 ($1 per 20M)

#### GPT-OSS-20B Performance

- MMLU (General Reasoning): 85.3%
- SWE-Bench Verified (Coding): 60.7%
- AIME 2025 (Math with tools): 98.7%
- MMMLU (Multilingual): 75.7% average

#### GPT-OSS-20B Capabilities

- Tool Use
- Browser Search
- Code Execution
- JSON Object/Schema Mode
- Reasoning (low/medium/high)
- Long-context processing

#### GPT-OSS-20B EPN Use Cases

- **Layer 1 (Reformulation)**: Fast, cost-effective bias elimination
- **Layer 2 (Definition)**: Efficient semantic and genealogical analysis
- **Cost-conscious deployments with good performance**

#### GPT-OSS-20B Configuration

```json
{
  "model": "openai/gpt-oss-20b",
  "temperature": 0.8,
  "max_tokens": 1000,
  "reasoning_effort": "medium",
  "top_p": 1.0
}
```

---

### 3. Qwen 3 32B (`qwen/qwen3-32b`)

**Status**: Preview Model  
**Provider**: Alibaba Cloud  
**Token Speed**: ~400 TPS  

#### Qwen 3 32B Specifications

- **Context Window**: 131,072 tokens
- **Max Output Tokens**: 40,960
- **Architecture**: 32B parameters with dual-mode system
- **Quantization**: Groq TruePoint Numerics

#### Qwen 3 32B Pricing (per 1M tokens)

- Input: $0.29 ($1 per 3.4M)
- Output: $0.59 ($1 per 1.7M)

#### Qwen 3 32B Performance

- ArenaHard: 93.8%
- AIME 2024: 81.4% pass rate
- LiveCodeBench: 65.7%
- BFCL: 30.3%
- MultiIF: 73.0%
- AIME 2025: 72.9%
- LiveBench: 71.6%

#### Qwen 3 32B Capabilities

- Tool Use
- JSON Object Mode
- Reasoning (thinking vs non-thinking modes)
- Multilingual support (100+ languages)

#### Qwen 3 32B EPN Use Cases

- **Layer 2 (Definition)**: Complex semantic analysis and logical relationships
- **Layer 3 (Validation)**: Rigorous coherence checking with mathematical precision
- **Tasks requiring deep logical reasoning**

#### Qwen 3 32B Configuration

```json
{
  "model": "qwen/qwen3-32b",
  "temperature": 0.6,
  "max_tokens": 1500,
  "reasoning_effort": "high",
  "top_p": 0.95,
  "top_k": 20,
  "min_p": 0.0
}
```

---

### 4. Groq Compound (`groq/compound`)

**Status**: Production System  
**Provider**: Groq  
**Token Speed**: ~450 TPS  

#### Compound Specifications

- **Context Window**: 131,072 tokens
- **Max Output Tokens**: 8,192
- **Architecture**: Multi-model system (GPT-OSS-120B + Llama 4 Scout)
- **Quantization**: Groq TruePoint Numerics

#### Compound Pricing

- Variable (depends on underlying models used)
- GPT-OSS-120B: Input $0.15, Output $0.75 per 1M tokens
- Llama 4 Scout: Input $0.11, Output $0.34 per 1M tokens
- Tool usage: Web search $5/1000 requests, Code execution $0.18/hour

#### Compound Capabilities

- Web Search (built-in)
- Code Execution (built-in)
- Visit Website
- Browser Automation
- Wolfram Alpha integration
- JSON Object Mode

#### Compound EPN Use Cases

- **Layer 2 (Teleological)**: Functional analysis requiring real-time data access
- **Layer 3 (Validation)**: Correspondence validation needing external verification
- **Tasks requiring tool use and external data access**

#### Compound Configuration

```json
{
  "model": "groq/compound",
  "temperature": 0.7,
  "max_tokens": 1500,
  "reasoning_effort": "medium",
  "top_p": 1.0
}
```

---

### 5. Groq Compound Mini (`groq/compound-mini`)

**Status**: Production System  
**Provider**: Groq  
**Token Speed**: ~450 TPS (3x lower latency than Compound)  

#### Compound Mini Specifications

- **Context Window**: 131,072 tokens
- **Max Output Tokens**: 8,192
- **Architecture**: Multi-model system (GPT-OSS-120B + Llama 3.3 70B)
- **Quantization**: Groq TruePoint Numerics
- **Limitation**: One tool per request (vs multiple in regular Compound)

#### Compound Mini Pricing

- Variable (depends on underlying models used)
- GPT-OSS-120B: Input $0.15, Output $0.75 per 1M tokens
- Llama 3.3 70B: Input $0.59, Output $0.79 per 1M tokens
- Tool usage: Web search $5/1000 requests, Code execution $0.18/hour

#### Compound Mini Capabilities

- Web Search (built-in)
- Code Execution (built-in)
- Visit Website
- Browser Automation
- Wolfram Alpha integration
- JSON Object Mode

#### Compound Mini EPN Use Cases

- **Layer 2 (Genealogical)**: Historical research requiring web access
- **Layer 3 (Pragmatic)**: Real-world validation needing current data
- **Faster inference requirements with tool access**

#### Compound Mini Configuration

```json
{
  "model": "groq/compound-mini",
  "temperature": 0.7,
  "max_tokens": 1500,
  "reasoning_effort": "medium",
  "top_p": 1.0
}
```

## EPN Layer Recommendations

### Layer-Specific Model Assignments

```json
{
  "layer_configs": {
    "layer1.reformulator_node": {
      "model": "openai/gpt-oss-20b",
      "temperature": 0.8,
      "max_tokens": 1000,
      "reasoning_effort": "medium"
    },
    "layer2.genealogical_node": {
      "model": "groq/compound-mini",
      "temperature": 0.7,
      "max_tokens": 1500,
      "reasoning_effort": "medium"
    },
    "layer2.semantic_node": {
      "model": "qwen/qwen3-32b",
      "temperature": 0.6,
      "max_tokens": 1500,
      "reasoning_effort": "high"
    },
    "layer2.teleological_node": {
      "model": "groq/compound",
      "temperature": 0.7,
      "max_tokens": 1500,
      "reasoning_effort": "medium"
    },
    "layer3.coherence_validator": {
      "model": "qwen/qwen3-32b",
      "temperature": 0.5,
      "max_tokens": 2000,
      "reasoning_effort": "high"
    },
    "layer3.correspondence_validator": {
      "model": "openai/gpt-oss-120b",
      "temperature": 0.6,
      "max_tokens": 2000,
      "reasoning_effort": "high"
    },
    "layer3.pragmatic_validator": {
      "model": "groq/compound",
      "temperature": 0.6,
      "max_tokens": 2000,
      "reasoning_effort": "medium"
    },
    "layer4.synthesis_node": {
      "model": "openai/gpt-oss-120b",
      "temperature": 0.6,
      "max_tokens": 4000,
      "reasoning_effort": "high"
    }
  }
}
```

### Performance vs Cost Trade-offs

| Model | Performance | Cost | Speed | Best For |
|-------|-------------|------|-------|----------|
| GPT-OSS-120B | Highest | High | Medium | Complex synthesis, validation |
| GPT-OSS-20B | High | Low | Highest | Fast processing, reformulation |
| Qwen 3 32B | Very High | Medium | Medium | Logical reasoning, validation |
| Compound | High + Tools | Variable | Medium | Tool-augmented tasks |
| Compound Mini | High + Tools | Variable | High | Fast tool use |

### Configuration Guidelines

#### Temperature Settings by Layer

- **Layer 1 (Reformulation)**: 0.7-0.9 (creative rephrasing)
- **Layer 2 (Definition)**: 0.6-0.8 (balanced creativity/accuracy)
- **Layer 3 (Validation)**: 0.4-0.6 (consistency and rigor)
- **Layer 4 (Synthesis)**: 0.5-0.7 (integrative thinking)

#### Reasoning Effort

- **Low**: Simple tasks, fast responses
- **Medium**: Balanced reasoning (most layers)
- **High**: Complex analysis (validation, synthesis)

#### Token Limits

- **Layer 1**: 500-1500 tokens (focused reformulation)
- **Layer 2**: 1000-2000 tokens (detailed definitions)
- **Layer 3**: 1500-2500 tokens (comprehensive validation)
- **Layer 4**: 3000-6000 tokens (integrated synthesis)

## Implementation Notes

- All models support the same LLMConfig parameters
- Tool-enabled models (Compound variants) add capabilities for external data access
- Preview models (Qwen 3 32B) should be evaluated before production use
- Cost optimization: Use smaller models for simpler tasks, larger models for complex reasoning
- Performance optimization: Match model capabilities to layer requirements

## References

- [Groq Models Documentation](https://console.groq.com/docs/models)
- [Compound Systems](https://console.groq.com/docs/compound)
- [Pricing Information](https://groq.com/pricing)
- [Rate Limits](https://console.groq.com/docs/rate-limits)