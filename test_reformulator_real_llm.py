#!/usr/bin/env python3
"""
Real LLM Reformulator Testing Script

This script tests the Reformulator agent with real LLM integration,
capturing all intermediate steps and generating a comprehensive test report.
"""

import os
import asyncio
import json
from datetime import datetime
from pathlib import Path

from core.config import init_config, NetworkConfig, get_config
from core.schemas import NetworkRequest
from layers.layer1_reformulation.reformulator import Reformulator


class ReformulatorTester:
    """Comprehensive tester for the Reformulator agent with real LLM integration."""

    def __init__(self):
        """Initialize the tester with real LLM configuration."""
        self.setup_config()
        self.reformulator = Reformulator()
        self.test_results = []

    def setup_config(self):
        """Setup configuration for real LLM testing."""
        # Use environment variable or prompt for API key
        api_key = os.getenv('GROQ_API_KEY')
        if not api_key:
            print("🔑 GROQ_API_KEY environment variable not found.")
            api_key = input("Please enter your Groq API key: ").strip()
            if not api_key:
                raise ValueError("API key is required for real LLM testing")

        config = NetworkConfig(
            groq_api_key=api_key,
            groq_model="openai/gpt-oss-120b",
            max_concurrent_requests=1,
            request_timeout=120.0,  # Match playground timeout
            max_retries=3,
            temperature=0.9,  # Updated for creative responses
            max_tokens_per_request=8192,  # Match playground max tokens
            top_p=1.0,  # Match playground setting
            reasoning_effort="medium",  # Medium reasoning for Phase 1
            tools=[],  # No tools for Phase 1
            log_level="INFO",
            enable_structured_logging=True,
            debug_mode=True,
            mock_responses=False  # Use real LLM
        )

        init_config(config)
        print("✅ Configuration initialized with real LLM integration")

    async def test_question(self, question: str, metadata: dict = None) -> dict:
        """Test a single question through the complete reformulation pipeline."""

        print(f"\n🔍 Testing question: {question}")

        # Create network request
        request = NetworkRequest(
            request_id=f"test-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
            original_question=question,
            timestamp=datetime.now().isoformat(),
            metadata=metadata or {}
        )

        # Capture configuration
        config_info = {
            "llm_model": get_config().groq_model,
            "temperature": get_config().temperature,
            "max_tokens": get_config().max_tokens_per_request,
            "top_p": get_config().top_p,
            "reasoning_effort": get_config().reasoning_effort,
            "tools": get_config().tools,
            "mock_responses": get_config().mock_responses
        }

        # Step 1: Initial sanitization
        print("📝 Step 1: Sanitizing input...")
        sanitized, initial_bias = self.reformulator._sanitize_input(question)

        # Step 2: Build LLM prompt
        print("🤖 Step 2: Building LLM prompt...")
        llm_prompt = self.reformulator._build_reformulation_prompt(sanitized, request.metadata)

        # Step 3: Get LLM response (capture raw response)
        print("🚀 Step 3: Sending to LLM...")
        try:
            # Get reformulated question, raw response, and bias tracking
            reformulated_raw, raw_llm_response, llm_bias = await self.reformulator._reformulate_with_llm(
                sanitized, request.metadata
            )

        except Exception as e:
            print(f"❌ LLM call failed: {e}")
            # Fallback to basic reformulation
            reformulated_raw, raw_llm_response, llm_bias = (
                self.reformulator._basic_reformulation(sanitized) + ("LLM_FAILED_FALLBACK_TO_BASIC",)
            )

        # Step 4: Extract clean reformulation
        print("🔧 Step 4: Extracting reformulation...")
        if raw_llm_response != "LLM_FAILED_FALLBACK_TO_BASIC":
            final_reformulation = self.reformulator._extract_reformulated_question(raw_llm_response)
        else:
            final_reformulation = reformulated_raw

        # Step 5: Context enrichment
        print("📚 Step 5: Enriching context...")
        enriched_question, context_added = self.reformulator._enrich_context(final_reformulation)

        # Step 6: Final validation
        print("✅ Step 6: Validating final result...")
        validated_question = self.reformulator._validate_reformulation(enriched_question)

        # Combine bias tracking
        total_bias_removed = initial_bias + llm_bias

        # Create test result
        result = {
            "timestamp": datetime.now().isoformat(),
            "original_question": question,
            "configuration": config_info,
            "steps": {
                "sanitization": {
                    "input": question,
                    "output": sanitized,
                    "bias_removed": initial_bias
                },
                "llm_interaction": {
                    "prompt_sent": llm_prompt,
                    "raw_response": raw_llm_response,
                    "reformulation_extracted": final_reformulation,
                    "bias_detected": llm_bias
                },
                "context_enrichment": {
                    "input": final_reformulation,
                    "output": enriched_question,
                    "context_added": context_added
                },
                "validation": {
                    "input": enriched_question,
                    "output": validated_question,
                    "passed": True
                }
            },
            "final_result": {
                "question": validated_question,
                "total_bias_removed": total_bias_removed,
                "total_context_added": context_added
            }
        }

        self.test_results.append(result)
        return result

    def generate_markdown_report(self, filename: str = None) -> str:
        """Generate a comprehensive Markdown report of all tests."""

        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"reformulator_test_report_{timestamp}.md"

        report_path = Path(filename)

        with open(report_path, 'w', encoding='utf-8') as f:
            f.write("# Reformulator Agent - Real LLM Integration Test Report\n\n")
            f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write(f"**Total Tests:** {len(self.test_results)}\n\n")

            for i, result in enumerate(self.test_results, 1):
                f.write(f"## Test Case {i}\n\n")
                f.write(f"**Original Question:** {result['original_question']}\n\n")

                # Configuration
                f.write("### 🔧 LLM Configuration\n\n")
                config = result['configuration']
                f.write(f"- **Model:** {config['llm_model']}\n")
                f.write(f"- **Temperature:** {config['temperature']}\n")
                f.write(f"- **Max Tokens:** {config['max_tokens']}\n")
                f.write(f"- **Mock Responses:** {config['mock_responses']}\n\n")

                # Steps breakdown
                steps = result['steps']

                f.write("### 📝 Step 1: Input Sanitization\n\n")
                f.write(f"**Input:** {steps['sanitization']['input']}\n\n")
                f.write(f"**Sanitized:** {steps['sanitization']['output']}\n\n")
                if steps['sanitization']['bias_removed']:
                    f.write(f"**Bias Removed:** {steps['sanitization']['bias_removed']}\n\n")
                else:
                    f.write("**Bias Removed:** None\n\n")

                f.write("### 🤖 Step 2: LLM Interaction\n\n")
                f.write("#### Prompt Sent to LLM:\n\n")
                f.write("```\n")
                f.write(steps['llm_interaction']['prompt_sent'])
                f.write("\n```\n\n")

                f.write("#### Raw LLM Response:\n\n")
                f.write("```\n")
                f.write(steps['llm_interaction']['raw_response'])
                f.write("\n```\n\n")

                f.write("#### Extracted Reformulation:\n\n")
                f.write(f"**Result:** {steps['llm_interaction']['reformulation_extracted']}\n\n")
                if steps['llm_interaction']['bias_detected']:
                    f.write(f"**Bias Detected:** {steps['llm_interaction']['bias_detected']}\n\n")

                f.write("### 📚 Step 3: Context Enrichment\n\n")
                f.write(f"**Input:** {steps['context_enrichment']['input']}\n\n")
                f.write(f"**Enriched:** {steps['context_enrichment']['output']}\n\n")
                f.write(f"**Context Added:** {steps['context_enrichment']['context_added']}\n\n")

                f.write("### ✅ Step 4: Final Validation\n\n")
                f.write(f"**Input:** {steps['validation']['input']}\n\n")
                f.write(f"**Validated:** {steps['validation']['output']}\n\n")
                f.write(f"**Validation Passed:** {steps['validation']['passed']}\n\n")

                # Final result
                f.write("### 🎯 Final Result\n\n")
                final = result['final_result']
                f.write(f"**Final Question:** {final['question']}\n\n")
                f.write(f"**Total Bias Removed:** {len(final['total_bias_removed'])} items\n")
                if final['total_bias_removed']:
                    f.write(f"- {', '.join(final['total_bias_removed'])}\n")
                f.write(f"\n**Total Context Added:** {len(final['total_context_added'])} items\n")
                if final['total_context_added']:
                    f.write(f"- {', '.join(final['total_context_added'])}\n")
                f.write("\n---\n\n")

        print(f"📄 Report generated: {report_path.absolute()}")
        return str(report_path)

    def generate_llm_details_text_file(self, filename: str = None) -> str:
        """Generate a simple text file with LLM configuration, prompt, and raw response."""

        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"llm_details_{timestamp}.txt"

        report_path = Path(filename)

        with open(report_path, 'w', encoding='utf-8') as f:
            f.write("LLM Integration Details\n")
            f.write("=" * 50)
            f.write(f"\nGenerated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

            for i, result in enumerate(self.test_results, 1):
                f.write(f"Test Case {i}\n")
                f.write("-" * 20)
                f.write(f"\nOriginal Question: {result['original_question']}\n\n")

                # LLM Configuration
                f.write("LLM CONFIGURATION:\n")
                config = result['configuration']
                f.write(f"Model: {config['llm_model']}\n")
                f.write(f"Temperature: {config['temperature']}\n")
                f.write(f"Max Tokens: {config['max_tokens']}\n")
                f.write(f"Top-p: {config.get('top_p', 'N/A')}\n")
                f.write(f"Reasoning Effort: {config.get('reasoning_effort', 'N/A')}\n")
                f.write(f"Tools: {config.get('tools', 'N/A')}\n")
                f.write(f"Mock Responses: {config['mock_responses']}\n\n")

                # Prompt Sent to LLM
                f.write("PROMPT SENT TO LLM:\n")
                f.write("-" * 20)
                f.write("\n")
                f.write(result['steps']['llm_interaction']['prompt_sent'])
                f.write("\n\n")

                # Raw LLM Response
                f.write("RAW LLM RESPONSE:\n")
                f.write("-" * 20)
                f.write("\n")
                f.write(result['steps']['llm_interaction']['raw_response'])
                f.write("\n\n")

                f.write("=" * 50)
                f.write("\n\n")

        print(f"📄 LLM details text file generated: {report_path.absolute()}")
        return str(report_path)


async def main():
    """Main testing function with interactive user input."""
    print("🚀 Reformulator Agent - Real LLM Integration Tester")
    print("=" * 60)

    tester = ReformulatorTester()

    while True:
        print("\n" + "=" * 40)
        print("Enter a question to test (or 'quit' to exit):")
        question = input("> ").strip()

        if question.lower() in ['quit', 'exit', 'q']:
            break

        if not question:
            print("❌ Please enter a valid question.")
            continue

        try:
            # Test the question
            result = await tester.test_question(question)

            # Show summary
            print("\n✅ Test completed!")
            print(f"📝 Original: {question}")
            print(f"🔄 Final: {result['final_result']['question']}")
            print(f"🧹 Bias removed: {len(result['final_result']['total_bias_removed'])}")
            print(f"📚 Context added: {len(result['final_result']['total_context_added'])}")

        except Exception as e:
            print(f"❌ Test failed: {e}")
            continue

    # Generate final reports
    if tester.test_results:
        print("\n📄 Generating comprehensive test report...")
        report_file = tester.generate_markdown_report()
        print(f"✅ Report saved to: {report_file}")

        print("\n📄 Generating LLM details text file...")
        text_file = tester.generate_llm_details_text_file()
        print(f"✅ Text file saved to: {text_file}")
    else:
        print("📄 No tests were run, skipping report generation.")

    print("\n👋 Testing session completed!")


if __name__ == "__main__":
    asyncio.run(main())