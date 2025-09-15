# Reformulator Agent - Real LLM Integration Testing

This script provides comprehensive testing of the Reformulator agent with real LLM integration, capturing all intermediate steps and generating detailed test reports.

## Features

- ✅ **Real LLM Integration**: Tests with actual Groq API calls (not mocks)
- ✅ **Interactive Testing**: Input questions at runtime
- ✅ **Comprehensive Logging**: Captures all intermediate steps
- ✅ **Markdown Reports**: Generates detailed test reports
- ✅ **Step-by-Step Analysis**: Shows sanitization, LLM interaction, context enrichment, and validation
- ✅ **Phase-Specific Configuration**: LLM parameters (temperature, reasoning effort, tools) vary by epistemological layer requirements

## Setup

1. **API Key**: Set your Groq API key as an environment variable:

   ```bash
   export GROQ_API_KEY="your_api_key_here"
   ```

2. **Run the tester**:

   ```bash
   python test_reformulator_real_llm.py
   ```

## Usage

The script will prompt you to enter questions. For each question, it will:

1. **Sanitize Input**: Remove basic bias and clean the text
2. **Build LLM Prompt**: Create the sophisticated epistemic framework prompt
3. **Call Real LLM**: Send prompt to Groq GPT-OSS-120B
4. **Extract Response**: Parse the LLM's reformulation
5. **Enrich Context**: Add epistemic framing and disciplinary perspective
6. **Validate**: Ensure the final question meets quality standards

## Example Session

```text
🚀 Reformulator Agent - Real LLM Integration Tester
============================================================

========================================
Enter a question to test (or 'quit' to exit):
> Why are incompetent politicians making our country worse?

🔍 Testing question: Why are incompetent politicians making our country worse?

📝 Step 1: Sanitizing input...
🤖 Step 2: Building LLM prompt...
🚀 Step 3: Sending to LLM...
✅ Test completed!
📝 Original: Why are incompetent politicians making our country worse?
🔄 Final: How do differing interpretations of governmental effectiveness shape public discourse on national progress, from a political sociology perspective?
🧹 Bias removed: 3
📚 Context added: 2

========================================
Enter a question to test (or 'quit' to exit):
> quit

📄 Generating comprehensive test report...
✅ Report saved to: reformulator_test_report_20241209_143022.md

👋 Testing session completed!
```

## Report Structure

The generated Markdown report includes:

- **LLM Configuration**: Model, temperature, max tokens, mock status
- **Step-by-Step Breakdown**:
  - Input sanitization results
  - Full prompt sent to LLM
  - Raw LLM response
  - Extracted reformulation
  - Context enrichment details
  - Final validation results
- **Final Results**: Complete reformulated question with metadata

## Report Example

```markdown
# Reformulator Agent - Real LLM Integration Test Report

**Generated:** 2024-12-09 14:30:22
**Total Tests:** 1

## Test Case 1

**Original Question:** Why are incompetent politicians making our country worse?

### 🔧 LLM Configuration
- **Model:** openai/gpt-oss-120b
- **Temperature:** 0.9
- **Max Tokens:** 8192
- **Top-p:** 1.0
- **Reasoning Effort:** medium
- **Tools:** []
- **Mock Responses:** false

### 📝 Step 1: Input Sanitization
**Input:** Why are incompetent politicians making our country worse?
**Sanitized:** Why are incompetent politicians making our country worse?
**Bias Removed:** None

### 🤖 Step 2: LLM Interaction

#### Prompt Sent to LLM

```text
You are an epistemological reformulator specializing in bias elimination...
[full prompt]
```

#### Raw LLM Response

```text
How do differing interpretations of governmental effectiveness shape public discourse on national progress, from a political sociology perspective?
```

#### Extracted Reformulation

**Result:** How do differing interpretations of governmental effectiveness shape public discourse on national progress, from a political sociology perspective?
**Bias Detected:** ['LLM bias elimination applied']

### 📚 Step 3: Context Enrichment

**Input:** How do differing interpretations of governmental effectiveness shape public discourse on national progress, from a political sociology perspective?
**Enriched:** From multiple disciplinary and interpretive perspectives, how do differing interpretations of governmental effectiveness shape public discourse on national progress, from a political sociology perspective?
**Context Added:** ['epistemic framing: multi-perspective analysis']

### ✅ Step 4: Final Validation

**Input:** From multiple disciplinary and interpretive perspectives, how do differing interpretations of governmental effectiveness shape public discourse on national progress, from a political sociology perspective?
**Validated:** From multiple disciplinary and interpretive perspectives, how do differing interpretations of governmental effectiveness shape public discourse on national progress, from a political sociology perspective?
**Validation Passed:** true

### 🎯 Final Result

**Final Question:** From multiple disciplinary and interpretive perspectives, how do differing interpretations of governmental effectiveness shape public discourse on national progress, from a political sociology perspective?
**Total Bias Removed:** 1 items

- LLM bias elimination applied

**Total Context Added:** 1 items

- epistemic framing: multi-perspective analysis

## Key Benefits

- **Real-world Testing**: Validates actual LLM integration and API responses
- **Debugging Support**: Detailed step-by-step breakdown for troubleshooting
- **Quality Assurance**: Ensures reformulation quality and epistemic framework effectiveness
- **Documentation**: Creates comprehensive records of LLM behavior and responses
- **Performance Monitoring**: Tracks response times, token usage, and success rates

## Notes

- Requires valid Groq API key with sufficient credits
- Real API calls may incur costs
- Reports are saved as timestamped Markdown files
- Use `quit` or `exit` to end testing session
