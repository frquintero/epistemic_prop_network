import importlib
import sys
import types
import os

from unittest.mock import patch


class FakePipeline:
    def __init__(self, skip_autoload=False):
        self.skip_autoload = skip_autoload
        self.loaded = []

    def load_config(self, layer_file, template_file, replace_templates=False):
        # record the call
        self.loaded.append((layer_file, template_file, replace_templates))

    async def process(self, query):
        return {'result': 'ok'}


def import_cli_with_fake_pipeline():
    # Inject fake pipeline module so CLI imports succeed without heavy core imports
    fake_mod = types.ModuleType('epn_core.core.pipeline')
    fake_mod.Pipeline = FakePipeline
    sys.modules['epn_core.core.pipeline'] = fake_mod

    # Import or reload the CLI module
    if 'epn_core.cli' in sys.modules:
        importlib.reload(sys.modules['epn_core.cli'])
    else:
        importlib.import_module('epn_core.cli')

    return sys.modules['epn_core.cli']


def test_default_replaces_by_default(tmp_path, monkeypatch):
    # Import the CLI module fresh
    import_cli_with_fake_pipeline()
    import importlib
    cli = importlib.reload(sys.modules['epn_core.cli'])

    # Monkeypatch the Pipeline class in the CLI module
    created = {}

    class RecordingPipeline(FakePipeline):
        def __init__(self, skip_autoload=False):
            super().__init__(skip_autoload=skip_autoload)
            created['instance'] = self

    monkeypatch.setattr(cli, 'Pipeline', RecordingPipeline)

    # Ensure project defaults don't exist so it falls back to bundled defaults
    monkeypatch.setattr('os.path.exists', lambda p: False)

    # Run pipeline with use_default=True and merge_defaults=False
    cli.run_pipeline('q', None, None, use_default=True, merge_defaults=False)

    inst = created['instance']
    assert len(inst.loaded) == 1
    layer_file, template_file, replace_templates = inst.loaded[0]
    assert replace_templates is True


def test_default_with_merge_keeps_merge(tmp_path, monkeypatch):
    import importlib
    import_cli_with_fake_pipeline()
    cli = importlib.reload(sys.modules['epn_core.cli'])

    created = {}

    class RecordingPipeline(FakePipeline):
        def __init__(self, skip_autoload=False):
            super().__init__(skip_autoload=skip_autoload)
            created['instance'] = self

    monkeypatch.setattr(cli, 'Pipeline', RecordingPipeline)
    monkeypatch.setattr('os.path.exists', lambda p: False)
    # Run with merge_defaults=True so replace_templates should be False
    cli.run_pipeline('q', None, None, use_default=True, merge_defaults=True)
    inst = created['instance']
    assert len(inst.loaded) == 1
    _, _, replace_templates = inst.loaded[0]
    assert replace_templates is False

