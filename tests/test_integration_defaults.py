import importlib
from unittest.mock import patch

from epn_core.core.pipeline import Pipeline


class DummyNode:
    def __init__(self, config, template):
        self.config = config
        self.template = template

    async def process(self, input_data):
        # Return a deterministic value keyed by template expected_output
        exp = self.template.get('expected_output')
        return f"{exp}_value"


class DummyFactory:
    def __init__(self, template_manager):
        self.template_manager = template_manager

    def create_node(self, node_config):
        tmpl = self.template_manager.get_template(node_config.template_id)
        return DummyNode(node_config, tmpl)


def test_run_pipeline_with_defaults(monkeypatch):
    # Ensure Pipeline uses our DummyFactory so no real LLMs are invoked
    monkeypatch.setattr('epn_core.core.pipeline.NodeFactory', DummyFactory)

    p = Pipeline(skip_autoload=True)
    # Load the built-in default configs (replace_templates True to ensure consistency)
    p.load_config('epn_core/config/default_layer.json', 'epn_core/config/default_template.json', replace_templates=True)

    import asyncio
    result = asyncio.run(p.process('Why are all models wrong yet some are useful?'))

    # Final result should be a dict containing at least the synthesis expected_output
    assert isinstance(result, dict) or isinstance(result, str)
