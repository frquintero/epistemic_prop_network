import pytest

from epn_core.config.template_manager import TemplateManager


def make_template(tid, tpl_text, placeholders, expected_output=None):
    data = {
        'template': tpl_text,
        'placeholders': placeholders,
        'metadata': {'purpose': 'test'}
    }
    if expected_output is not None:
        data['expected_output'] = expected_output
    return tid, data


def test_load_templates_replace_and_merge():
    tm = TemplateManager()

    t1_id, t1 = make_template('a', 'Hello {name}', ['name'], expected_output='a_out')
    t2_id, t2 = make_template('b', 'Bye {who}', ['who'], expected_output='b_out')

    # initial load (merge by default)
    tm.load_templates({t1_id: t1})
    assert tm.has_template('a')

    # merge new templates
    tm.load_templates({t2_id: t2}, replace=False)
    assert tm.has_template('a') and tm.has_template('b')

    # replace with only t1
    tm.load_templates({t1_id: t1}, replace=True)
    assert tm.has_template('a')
    assert not tm.has_template('b')

    # replacing with empty dict should clear all templates
    tm.load_templates({}, replace=True)
    with pytest.raises(ValueError):
        tm.validate_templates()
