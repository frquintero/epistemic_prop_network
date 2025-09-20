#!/usr/bin/env python3
"""Smoke-test script for xAI REST Chat Completions (responses) API.

This script demonstrates creating a response, retrieving it, and deleting it.
It uses `XAI_API_KEY` and optional `XAI_BASE_URL` environment variables.

It is intentionally conservative: if `XAI_API_KEY` is not set the script exits.
"""

import os
import time
import requests
from typing import Optional


def get_base_url() -> str:
    return os.environ.get('XAI_BASE_URL', 'https://api.x.ai')


def get_headers(api_key: str) -> dict:
    return {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }


def create_response(api_key: str, prompt: str, model: str = 'tiiuae/falcon-1.0') -> dict:
    url = f"{get_base_url().rstrip('/')}/v1/responses"
    payload = {
        'model': model,
        'input': prompt
    }
    resp = requests.post(url, json=payload, headers=get_headers(api_key), timeout=20)
    resp.raise_for_status()
    return resp.json()


def get_response(api_key: str, response_id: str) -> dict:
    url = f"{get_base_url().rstrip('/')}/v1/responses/{response_id}"
    resp = requests.get(url, headers=get_headers(api_key), timeout=20)
    resp.raise_for_status()
    return resp.json()


def delete_response(api_key: str, response_id: str) -> Optional[dict]:
    url = f"{get_base_url().rstrip('/')}/v1/responses/{response_id}"
    resp = requests.delete(url, headers=get_headers(api_key), timeout=20)
    if resp.status_code in (200, 204):
        return {'status': 'deleted'}
    resp.raise_for_status()
    return None


def main():
    api_key = os.environ.get('XAI_API_KEY')
    if not api_key:
        print('XAI_API_KEY not set; skipping live test. Set XAI_API_KEY to run.')
        return

    prompt = "Summarize in one sentence: What is life?"

    print('Creating response...')
    created = create_response(api_key, prompt)
    print('Create response result keys:', list(created.keys()))

    response_id = created.get('id') or created.get('response_id')
    if not response_id:
        print('Could not find response id in create response; full payload:')
        print(created)
        return

    print('Response ID:', response_id)

    # Wait a short time before retrieving (some backends are near-instant)
    time.sleep(1.0)

    print('Retrieving response...')
    retrieved = get_response(api_key, response_id)
    print('Retrieve keys:', list(retrieved.keys()))

    # Try to print the output text safely
    output = None
    if 'output' in retrieved:
        output = retrieved['output']
    elif 'choices' in retrieved:
        # Try common shapes
        choices = retrieved['choices']
        if isinstance(choices, list) and choices:
            output = choices[0].get('text') or choices[0].get('message') or choices[0]

    print('\n--- Generated Output ---')
    print(output)
    print('--- End Output ---\n')

    print('Deleting response...')
    deleted = delete_response(api_key, response_id)
    print('Delete result:', deleted)


if __name__ == '__main__':
    main()
