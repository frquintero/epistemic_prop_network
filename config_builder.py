"""Deprecated config builder stub.

The original interactive builder implementation was removed. This module
provides only a deprecation shim to avoid import-time crashes; it will raise
at runtime if instantiated. Use `scripts/builder_wizard.py` or the CLI
subcommands `create-layer` / `create-template` instead.
"""

class ConfigBuilder:
    def __init__(self, *a, **k):
        raise RuntimeError(
            "config_builder.py is deprecated. Use scripts/builder_wizard.py or epn_cli.py create-layer/create-template"
        )


class LayerConfig:
    pass


class NodeConfig:
    pass


class TemplateConfig:
    pass