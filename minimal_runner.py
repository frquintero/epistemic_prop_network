#!/usr/bin/env python3
"""Minimal pipeline runner that shows only prompts and responses."""

import sys
import logging
from pathlib import Path

# Disable all logging
logging.getLogger().setLevel(logging.CRITICAL)
for name in logging.root.manager.loggerDict:
    logging.getLogger(name).setLevel(logging.CRITICAL)

# Set up paths
root_path = Path(__file__).parent
sys.path.insert(0, str(root_path))

import asyncio
from epn_core.core.pipeline import Pipeline

async def run_minimal_pipeline(query: str):
    """Run pipeline with minimal output showing only prompts and responses."""
    # Pipeline now auto-discovers config files (layer.json/template.json at root, or defaults)
    pipeline = Pipeline()

    # Override the node processing to print minimal output
    from epn_core.core.nodes import BasicLLMNode

    original_process = BasicLLMNode.process

    async def minimal_process(self, input_data):
        # Prepare variables for template rendering
        variables = self._prepare_variables(input_data)

        # Render the prompt
        prompt = self._render_prompt(variables)

        # Print prompt
        print(f"=== NODE {self.config.node_id.upper()} PROMPT ===")
        print(prompt)
        print()

        # Call the LLM
        response = await self.llm_client.generate(prompt)

        # Print response
        print(f"=== NODE {self.config.node_id.upper()} RESPONSE ===")
        print(response)
        print("=" * 80)
        print()

        return response

    # Monkey patch the process method
    BasicLLMNode.process = minimal_process

    try:
        result = await pipeline.process(query)
        print("=== FINAL RESULT ===")
        print(result)
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python minimal_runner.py 'your query here'")
        sys.exit(1)

    query = sys.argv[1]
    asyncio.run(run_minimal_pipeline(query))