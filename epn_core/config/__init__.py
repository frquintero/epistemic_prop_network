"""Configuration management for the EPN pipeline.

This package exposes configuration-related modules. Import specific
components directly from their modules (for example,
`from epn_core.config.template_manager import TemplateManager`) to
avoid circular import issues during package import-time.
"""

__all__ = [
    'template_manager',
    'validator',
    'loader',
]
