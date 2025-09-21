"""Run the pipeline and print raw prompt and raw response per node.

This script patches each node's `process` method to call the node's LLM client
and print the raw prompt (placeholders substituted by pipeline) and the raw
response object and parameters in a compact, human-readable format.

Usage:
  LIVE_LLM=1 TEST_QUERY="your question" python scripts/epn_inspect_run.py
"""
import asyncio
import os
from pathlib import Path
import pprint

from epn_core.core.pipeline import Pipeline


def format_llm_params(cfg):
    return [cfg.model, cfg.temperature, cfg.reasoning_effort]


def patch_node(node, layer_index, layer_id):
    """Replace node.process with a wrapper that prints prompt/response."""
    # Keep original in case needed
    orig_process = node.process

    async def wrapped_process(input_data):
        # Prepare variables and render raw prompt (template + metadata)
        variables = node._prepare_variables(input_data)
        prompt = node._render_prompt(variables)

        # Ensure client present
        client = node.llm_client
        if not hasattr(client, 'client') or client.client is None:
            print(f"Skipping live call for node {node.config.node_id}: LLM client unavailable")
            # Fall back to original behavior (may raise)
            return await orig_process(input_data)

        # Capture raw response from underlying completions.create
        base_create = client.client.chat.completions.create
        request_capture = {}
        response_capture = {}

        def wrapper_create(**kwargs):
            request_capture['kwargs'] = kwargs
            resp = base_create(**kwargs)
            response_capture['resp'] = resp
            return resp

        # Install wrapper
        client.client.chat.completions.create = wrapper_create

        # Call generate (this will set client.last_rendered_prompt)
        try:
            response_text = await client.generate(prompt)
        finally:
            # Restore original create to avoid side-effects
            try:
                client.client.chat.completions.create = base_create
            except Exception:
                pass

        rendered = getattr(client, 'last_rendered_prompt', None)

        raw_resp = response_capture.get('resp')
        resp_text = ''
        resp_reasoning = None
        if raw_resp is not None:
            try:
                resp_text = raw_resp.choices[0].message.content or ''
            except Exception:
                resp_text = ''
            try:
                resp_reasoning = raw_resp.choices[0].message.reasoning
            except Exception:
                resp_reasoning = None

        # Print in requested format
        print(f"\nRaw prompt sent to node {node.config.node_id} Layer [{layer_index}]")
        print()
        print(rendered or '(not set)')
        print()
        print(f"Raw response received from node {node.config.node_id}")
        print()
        if resp_text:
            print(resp_text)
        else:
            if resp_reasoning:
                print("[Reasoning field present]")
                print(resp_reasoning)
            print("\n[Full raw response object]")
            pprint.pprint(raw_resp)

        print()
        print("Main LLM parameters: [" + ", ".join(map(str, format_llm_params(node.config.llm_config))) + "]")
        print('\n' + ('-' * 80))

        return response_text

    node.process = wrapped_process


async def main():
    # Build pipeline (auto-discovers configs)
    p = Pipeline()

    # Patch nodes
    for idx, layer_id in enumerate(p.layer_order, start=1):
        layer = p.layers[layer_id]
        for node in layer.nodes.values():
            patch_node(node, idx, layer_id)

    # Run pipeline with provided TEST_QUERY
    test_query = os.getenv('TEST_QUERY', 'Are you really listening to me?')
    print("Starting pipeline run (wrapped)\n")
    result = await p.process(test_query)
    print('\nPipeline run completed. Final output:')
    pprint.pprint(result)


if __name__ == '__main__':
    asyncio.run(main())
"""
This file has been removed. Use the canonical pipeline runner instead.
"""

# intentionally empty

