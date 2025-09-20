import pytest

from epn_core.config.template_manager import TemplateManager
from epn_core.config.validator import Validator
from types import SimpleNamespace


# Lightweight local stubs to avoid importing large core package during tests
class NodeStub:
    def __init__(self, node_id, template_id):
        self.node_id = node_id
        self.template_id = template_id
        self.name = node_id
        self.description = ''
        # Minimal llm_config needed by validator.validate_llm_configs
        self.llm_config = SimpleNamespace(model='m', temperature=1.0, reasoning_effort='default', max_tokens=10)


class LayerStub:
    def __init__(self, layer_id, name, nodes):
        self.layer_id = layer_id
        self.name = name
        self.nodes = nodes


class PipelineStub:
    def __init__(self, layers):
        self.layers = layers


def make_node(node_id, template_id):
    return NodeStub(node_id, template_id)


def test_validator_success_and_failure():
    # Build templates where layer1 produces 'first_out' and layer2 consumes it
    tm = TemplateManager()

    tm.load_templates({
        't_first': {
            'template': 'First processing {input}',
            'placeholders': ['input'],
            'metadata': {},
            'expected_output': 'first_out',
            'input_context': '{input}'
        },
        't_second': {
            'template': 'Second uses {first_out}',
            'placeholders': ['first_out'],
            'metadata': {},
            'expected_output': 'second_out',
            'input_context': '{first_out}'
        }
    })

    # Create layers: layer1 with node using t_first, layer2 with node using t_second
    n1 = make_node('n1', 't_first')
    n2 = make_node('n2', 't_second')

    l1 = LayerStub(layer_id='layer1', name='L1', nodes=[n1])
    l2 = LayerStub(layer_id='layer2', name='L2', nodes=[n2])
    pc = PipelineStub(layers=[l1, l2])

    validator = Validator()
    assert validator.validate_complete_config(pc, tm) is True

    # Now create a broken template that references a missing placeholder
    tm2 = TemplateManager()
    tm2.load_templates({
        't_first': {
            'template': 'First processing {input}',
            'placeholders': ['input'],
            'metadata': {},
            'expected_output': 'first_out',
            'input_context': '{input}'
        },
        't_bad': {
            'template': 'Broken {missing_key}',
            'placeholders': ['missing_key'],
            'metadata': {},
            'expected_output': 'bad_out',
            'input_context': '{missing_key}'
        }
    })

    n3 = make_node('n3', 't_first')
    n4 = make_node('n4', 't_bad')
    l1b = LayerStub(layer_id='l1b', name='L1b', nodes=[n3])
    l2b = LayerStub(layer_id='l2b', name='L2b', nodes=[n4])
    pc_bad = PipelineStub(layers=[l1b, l2b])

    with pytest.raises(ValueError):
        validator.validate_complete_config(pc_bad, tm2)
