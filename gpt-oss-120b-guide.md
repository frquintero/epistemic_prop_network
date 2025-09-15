# Groq GPT-OSS-120B Technical Guide

## Overview

This guide provides comprehensive technical specifications, best practices, and implementation details for using OpenAI's GPT-OSS-120B model on the Groq platform. The GPT-OSS-120B is a frontier-grade Mixture-of-Experts (MoE) model designed for high-capability agentic applications, advanced research, and complex reasoning tasks.

## Technical Specifications

### Model Architecture

- **Total Parameters**: 120B (5.1B active per forward pass)
- **Architecture**: Mixture-of-Experts (MoE) with 36 layers
- **Experts**: 128 MoE experts using Top-4 routing per token
- **Attention**: Grouped Query Attention with rotary embeddings
- **Normalization**: RMSNorm pre-layer normalization
- **Residual Width**: 2880

### Performance Metrics

- **MMLU (General Reasoning)**: 90.0%
- **SWE-Bench Verified (Coding)**: 62.4%
- **HealthBench Realistic (Health)**: 57.6%
- **MMMLU (Multilingual)**: 81.3% average

### Limits & Pricing

- **Context Window**: 131,072 tokens
- **Max Output Tokens**: 65,536 tokens
- **Token Speed**: ~500 TPS
- **Pricing**:
  - Input: $0.15 per 6.7M tokens ($1)
  - Cached Input: $0.07 per 13M tokens ($1)
  - Output: $0.75 per 1.3M tokens ($1)

### Quantization

Uses Groq's TruePoint Numerics, which reduces precision only in areas that don't affect accuracy, preserving quality while delivering significant speedup over traditional approaches.

## Capabilities

### Core Features

- **Tool Use**: Function calling and tool integration
- **Browser Search**: Web browsing and information retrieval
- **Code Execution**: Python code execution capabilities
- **JSON Object Mode**: Basic JSON output validation
- **JSON Schema Mode**: Strict schema-compliant structured outputs
- **Reasoning**: Advanced reasoning with variable modes (low, medium, high)

### Use Cases

- **Frontier-Grade Agentic Applications**: High-capability autonomous agents with advanced reasoning and multi-step problem solving
- **Advanced Research & Scientific Computing**: Research applications requiring robust health knowledge and biosecurity analysis
- **High-Accuracy Mathematical & Coding Tasks**: Competitive programming and complex mathematical reasoning
- **Multilingual AI Assistants**: Strong performance across 81+ languages

## Getting Started

### Installation & Setup

```bash
pip install groq
```

### Basic Usage Example

```python
from groq import Groq

client = Groq()
completion = client.chat.completions.create(
    model="openai/gpt-oss-120b",
    messages=[
        {
            "role": "user",
            "content": "Explain why fast inference is critical for reasoning models"
        }
    ]
)
print(completion.choices[0].message.content)
```

### Environment Setup

1. Get API key from [Groq Console](https://console.groq.com/keys)
2. Set environment variable: `export GROQ_API_KEY="your-api-key"`
3. Initialize client and start making requests

## Best Practices

### Reasoning Modes

- Use variable reasoning modes (low, medium, high) to balance performance and latency
- Choose appropriate mode based on task complexity and speed requirements

### Prompt Engineering

- **Harmony Chat Format**: Use proper role hierarchy (System > Developer > User > Assistant)
- **Context Window**: Leverage the full 131K context window for complex workflows
- **Safety Alignment**: Respect safety boundaries and use preparedness testing appropriately

### Tool Integration

- Structure tool definitions clearly for web browsing, Python execution, or function calling
- Provide detailed tool schemas and expected input/output formats
- Test tool integrations thoroughly before production deployment

### Performance Optimization

- **Batch Processing**: Use batch processing for multiple requests
- **Prompt Caching**: Leverage cached input pricing for repeated prompts
- **Context Management**: Be mindful of context window usage for long conversations

## Structured Outputs

### Introduction

Structured Outputs ensure model responses strictly conform to your provided JSON Schema or throw an error if compliance cannot be achieved. This provides reliable, type-safe data structures for programmatic use.

### Key Benefits

1. **Binary Output**: Either returns valid JSON Schema-compliant output or throws an error
2. **Type Safety**: No need to validate or retry malformed outputs
3. **Programmatic Refusal Detection**: Detect safety-based model refusals programmatically
4. **Simplified Prompting**: No complex prompts needed for consistent formatting

### Supported Models

- `openai/gpt-oss-20b`
- `openai/gpt-oss-120b` ⭐
- `moonshotai/kimi-k2-instruct-0905`
- `meta-llama/llama-4-maverick-17b-128e-instruct`
- `meta-llama/llama-4-scout-17b-16e-instruct`

### JSON Schema Mode vs JSON Object Mode

#### JSON Schema Mode (Recommended)

- **Strict Schema Compliance**: Responses must exactly match your JSON Schema
- **Error on Non-Compliance**: Throws error if model cannot produce conforming response
- **Type Safety**: Guaranteed structure and data types
- **Use Case**: When you need exact schema adherence (APIs, data processing, etc.)

#### JSON Object Mode

- **Basic JSON Validation**: Ensures syntactically valid JSON output
- **No Schema Enforcement**: May not match your intended schema structure
- **Retry Logic Required**: May need validation and retries for schema compliance
- **Use Case**: When you need valid JSON but don't require strict schema matching

### Schema Requirements

#### Supported Data Types

- **Primitives**: String, Number, Boolean, Integer
- **Complex**: Object, Array, Enum
- **Composition**: anyOf (union types)

#### Mandatory Constraints

1. **Required Fields**: All schema properties must be marked as `required`
2. **Closed Objects**: All objects must set `additionalProperties: false`
3. **No Optional Fields**: Optional fields are not supported

### Basic Schema Example

```json
{
  "name": "product_review",
  "schema": {
    "type": "object",
    "properties": {
      "product_name": { "type": "string" },
      "rating": { "type": "number" },
      "sentiment": {
        "type": "string",
        "enum": ["positive", "negative", "neutral"]
      },
      "key_features": {
        "type": "array",
        "items": { "type": "string" }
      }
    },
    "required": ["product_name", "rating", "sentiment", "key_features"],
    "additionalProperties": false
  }
}
```

### Implementation Examples

#### Python with Pydantic

```python
from groq import Groq
from pydantic import BaseModel
from typing import List

class ProductReview(BaseModel):
    product_name: str
    rating: float
    sentiment: str  # "positive" | "negative" | "neutral"
    key_features: List[str]

client = Groq()

response = client.chat.completions.create(
    model="openai/gpt-oss-120b",
    messages=[
        {"role": "system", "content": "Extract product review information from the text."},
        {"role": "user", "content": "I bought the UltraSound Headphones last week and I'm really impressed! The noise cancellation is amazing and the battery lasts all day. Sound quality is crisp and clear. I'd give it 4.5 out of 5 stars."}
    ],
    response_format={
        "type": "json_schema",
        "json_schema": {
            "name": "product_review",
            "schema": ProductReview.model_json_schema()
        }
    }
)

# Parse and validate response
result = ProductReview.model_validate_json(response.choices[0].message.content)
print(f"Product: {result.product_name}")
print(f"Rating: {result.rating}")
print(f"Sentiment: {result.sentiment}")
```

#### JavaScript with Zod

```javascript
import Groq from "groq-sdk";
import { z } from "zod";

const groq = new Groq();

const productReviewSchema = z.object({
  product_name: z.string(),
  rating: z.number(),
  sentiment: z.enum(["positive", "negative", "neutral"]),
  key_features: z.array(z.string())
});

const response = await groq.chat.completions.create({
  model: "openai/gpt-oss-120b",
  messages: [
    { role: "system", content: "Extract product review information from the text." },
    {
      role: "user",
      content: "I bought the UltraSound Headphones last week and I'm really impressed! The noise cancellation is amazing and the battery lasts all day. Sound quality is crisp and clear. I'd give it 4.5 out of 5 stars.",
    },
  ],
  response_format: {
    type: "json_schema",
    json_schema: {
      name: "product_review",
      schema: z.toJSONSchema(productReviewSchema)
    }
  }
});

const rawResult = JSON.parse(response.choices[0].message.content || "{}");
const result = productReviewSchema.parse(rawResult);
console.log(result);
```

### Advanced Schema Patterns

#### Union Types (anyOf)

```json
{
  "type": "object",
  "properties": {
    "payment_method": {
      "anyOf": [
        {
          "type": "object",
          "properties": {
            "card_number": {"type": "string"},
            "expiry_date": {"type": "string"},
            "cvv": {"type": "string"}
          },
          "additionalProperties": false,
          "required": ["card_number", "expiry_date", "cvv"]
        },
        {
          "type": "object",
          "properties": {
            "account_number": {"type": "string"},
            "routing_number": {"type": "string"},
            "bank_name": {"type": "string"}
          },
          "additionalProperties": false,
          "required": ["account_number", "routing_number", "bank_name"]
        }
      ]
    }
  },
  "additionalProperties": false,
  "required": ["payment_method"]
}
```

#### Reusable Subschemas ($defs and $ref)

```json
{
  "type": "object",
  "properties": {
    "milestones": {
      "type": "array",
      "items": {
        "$ref": "#/$defs/milestone"
      }
    },
    "project_status": {
      "type": "string",
      "enum": ["planning", "in_progress", "completed", "on_hold"]
    }
  },
  "$defs": {
    "milestone": {
      "type": "object",
      "properties": {
        "title": {"type": "string"},
        "deadline": {"type": "string"},
        "completed": {"type": "boolean"}
      },
      "required": ["title", "deadline", "completed"],
      "additionalProperties": false
    }
  },
  "required": ["milestones", "project_status"],
  "additionalProperties": false
}
```

### Error Handling

Schema validation failures return HTTP 400 errors with the message: `"Generated JSON does not match the expected schema. Please adjust your prompt."`

#### Resolution Strategies

1. **Retry Requests**: For transient failures
2. **Refine Prompts**: For recurring schema mismatches
3. **Simplify Schemas**: If validation consistently fails
4. **Add Examples**: Include system message examples for complex schemas

### Best Practices for Structured Outputs

#### User Input Handling

- Include explicit instructions for invalid or incompatible inputs
- Specify fallback responses (empty fields, error messages) for incompatible inputs
- Models attempt schema adherence even with unrelated data, potentially causing hallucinations

#### Output Quality

- Structured outputs guarantee schema compliance but not semantic accuracy
- For persistent errors, refine instructions or decompose complex tasks
- Use the prompt engineering guide for optimization techniques

#### Schema Design

- Use descriptive property names and clear descriptions
- Create evaluation sets to test schema effectiveness
- Include titles for important structural elements
- Keep schemas as simple as possible while meeting requirements

## Production Considerations

### Rate Limits & Optimization

- Monitor token usage and implement rate limiting
- Use batch processing for multiple simultaneous requests
- Leverage prompt caching to reduce costs for repeated requests

### Monitoring & Logging

- Track response times and success rates
- Log schema validation failures for debugging
- Monitor cost and performance metrics

### Error Recovery

- Implement exponential backoff for retries
- Have fallback models or simplified schemas ready
- Design graceful degradation for critical failures

## Additional Resources

- [Groq Playground](https://console.groq.com/playground) - Test models interactively
- [API Reference](https://console.groq.com/docs/api-reference) - Complete API documentation
- [Prompt Engineering Guide](https://console.groq.com/docs/prompting) - Advanced prompting techniques
- [Production Readiness](https://console.groq.com/docs/production-readiness) - Production deployment guide

---

*Last Updated: September 14, 2025*
*Model: openai/gpt-oss-120b*
*Platform: Groq*
