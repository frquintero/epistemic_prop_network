"""Template Manager for Epistemological Propagation Network

This module provides centralized management of all LLM prompt templates
used across the EPN layers. Templates are loaded from JSON and provide
consistent prompt engineering with validation and fallback mechanisms.
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, Optional, List, Union
from dataclasses import dataclass
from string import Formatter

from core.logging_config import get_logger
from core.exceptions import ConfigurationError
from core.llm_client import LLMConfig


@dataclass
class TemplateMetadata:
    """Metadata for a template."""
    version: str
    last_updated: str
    author: str
    description: Optional[str] = None


@dataclass
class Template:
    """Represents a single prompt template."""
    template: str
    placeholders: List[str]
    metadata: Optional[Dict[str, Any]] = None


class TemplateManager:
    """Centralized manager for all EPN prompt templates.

    Provides loading, validation, and rendering of templates from JSON.
    Includes fallback mechanisms to prevent system failure.
    """

    def __init__(self, template_file: Optional[str] = None, llm_config_file: Optional[str] = None):
        """Initialize the TemplateManager.

        Args:
            template_file: Path to the JSON template file. If None, uses default.
            llm_config_file: Path to the JSON LLM config file. If None, uses default.
        """
        self.logger = get_logger(__name__)
        self.template_file = template_file or self._get_default_template_path()
        self.llm_config_file = llm_config_file or self._get_default_llm_config_path()
        self.templates: Dict[str, Dict[str, Template]] = {}
        self.llm_configs: Dict[str, Dict[str, Any]] = {}
        self.metadata: Optional[TemplateMetadata] = None
        self.llm_metadata: Optional[Dict[str, Any]] = None
        self._loaded = False

    def _get_default_template_path(self) -> str:
        """Get the default path to the templates file."""
        # Assume templates.json is in the project root
        project_root = Path(__file__).parent.parent
        return str(project_root / "templates.json")

    def _get_default_llm_config_path(self) -> str:
        """Get the default path to the LLM config file."""
        # Assume llm.json is in the project root
        project_root = Path(__file__).parent.parent
        return str(project_root / "llm.json")

    def load_templates(self) -> None:
        """Load templates and LLM configurations from JSON files with validation."""
        try:
            # Load templates
            if not os.path.exists(self.template_file):
                self.logger.warning(
                    "Template file not found at %s, using fallback mode",
                    self.template_file
                )
                self._loaded = False
                return

            with open(self.template_file, 'r', encoding='utf-8') as f:
                template_data = json.load(f)

            # Validate template structure
            self._validate_template_structure(template_data)

            # Load template metadata
            if 'metadata' in template_data:
                meta = template_data['metadata']
                self.metadata = TemplateMetadata(
                    version=meta.get('version', '1.0.0'),
                    last_updated=meta.get('last_updated', 'unknown'),
                    author=meta.get('author', 'unknown'),
                    description=meta.get('description')
                )

            # Load templates
            self.templates = {}
            for layer_name, layer_templates in template_data.get('templates', {}).items():
                self.templates[layer_name] = {}
                for template_name, template_data_item in layer_templates.items():
                    template = Template(
                        template=template_data_item['template'],
                        placeholders=template_data_item.get('placeholders', []),
                        metadata=template_data_item.get('metadata')
                    )
                    self.templates[layer_name][template_name] = template

            # Load LLM configurations
            if os.path.exists(self.llm_config_file):
                with open(self.llm_config_file, 'r', encoding='utf-8') as f:
                    llm_data = json.load(f)

                # Load LLM metadata
                if 'metadata' in llm_data:
                    self.llm_metadata = llm_data['metadata']

                # Load LLM configs
                self.llm_configs = llm_data.get('layer_configs', {})

                self.logger.info(
                    "Loaded LLM configs for %d layer components from %s",
                    len(self.llm_configs),
                    self.llm_config_file
                )
            else:
                self.logger.warning(
                    "LLM config file not found at %s, LLM configs will not be available",
                    self.llm_config_file
                )

            self._loaded = True
            self.logger.info(
                "Loaded %d templates from %s",
                sum(len(layer) for layer in self.templates.values()),
                self.template_file
            )

        except Exception as e:
            self.logger.error("Failed to load templates and LLM configs: %s", e)
            self._loaded = False
            raise ConfigurationError(f"Template loading failed: {e}") from e

    def _validate_template_structure(self, data: Dict[str, Any]) -> None:
        """Validate the basic structure of the template JSON."""
        if not isinstance(data, dict):
            raise ConfigurationError("Template file must contain a JSON object")

        if 'templates' not in data:
            raise ConfigurationError("Template file must contain 'templates' key")

        templates = data['templates']
        if not isinstance(templates, dict):
            raise ConfigurationError("'templates' must be an object")

        # Validate each layer
        for layer_name, layer_templates in templates.items():
            if not isinstance(layer_templates, dict):
                raise ConfigurationError(f"Layer '{layer_name}' must be an object")

            for template_name, template_data in layer_templates.items():
                if not isinstance(template_data, dict):
                    raise ConfigurationError(f"Template '{layer_name}.{template_name}' must be an object")

                if 'template' not in template_data:
                    raise ConfigurationError(f"Template '{layer_name}.{template_name}' must have 'template' field")

                if not isinstance(template_data['template'], str):
                    raise ConfigurationError(f"Template '{layer_name}.{template_name}.template' must be a string")

    def get_template(self, layer: str, name: str) -> Optional[Template]:
        """Get a template by layer and name.

        Args:
            layer: Layer name (e.g., 'layer1', 'layer2')
            name: Template name (e.g., 'reformulator', 'semantic_node')

        Returns:
            Template object or None if not found
        """
        if not self._loaded:
            return None

        return self.templates.get(layer, {}).get(name)

    def get_llm_config(self, layer: str, name: str) -> Optional[LLMConfig]:
        """Get LLM configuration for a layer component.

        Args:
            layer: Layer name (e.g., 'layer1', 'layer2')
            name: Component name (e.g., 'reformulator_node', 'semantic_node')

        Returns:
            LLMConfig object or None if not found
        """
        if not self._loaded:
            return None

        config_key = f"{layer}.{name}"
        config_data = self.llm_configs.get(config_key)

        if config_data:
            try:
                # Create LLMConfig from the configuration data
                return LLMConfig(**config_data)
            except Exception as e:
                self.logger.warning(
                    "Failed to create LLMConfig for %s: %s",
                    config_key, e
                )
                return None

        # Try to get defaults if available
        defaults = self.llm_configs.get('defaults')
        if defaults:
            try:
                self.logger.info(
                    "Using default LLM config for %s",
                    config_key
                )
                return LLMConfig(**defaults)
            except Exception as e:
                self.logger.warning(
                    "Failed to create default LLMConfig: %s", e
                )

        self.logger.warning("No LLM config found for %s", config_key)
        return None

    def render_template(self, layer: str, name: str, **kwargs) -> str:
        """Render a template with the given parameters.

        Args:
            layer: Layer name
            name: Template name
            **kwargs: Template parameters

        Returns:
            Rendered template string

        Raises:
            ConfigurationError: If template not found or rendering fails
        """
        template = self.get_template(layer, name)
        if template is None:
            raise ConfigurationError(f"Template not found: {layer}.{name}")

        try:
            # Validate required placeholders are provided
            formatter = Formatter()
            required_placeholders = set()
            for literal_text, field_name, format_spec, conversion in formatter.parse(template.template):
                if field_name:
                    required_placeholders.add(field_name)

            missing = required_placeholders - set(kwargs.keys())
            if missing:
                raise ConfigurationError(f"Missing required placeholders for {layer}.{name}: {missing}")

            # Render template
            return template.template.format(**kwargs)

        except KeyError as e:
            raise ConfigurationError(f"Template rendering failed for {layer}.{name}: missing placeholder {e}") from e
        except ValueError as e:
            raise ConfigurationError(f"Template rendering failed for {layer}.{name}: {e}") from e

    def is_loaded(self) -> bool:
        """Check if templates are loaded."""
        return self._loaded

    def get_available_templates(self) -> Dict[str, List[str]]:
        """Get a summary of available templates."""
        if not self._loaded:
            return {}

        return {
            layer: list(templates.keys())
            for layer, templates in self.templates.items()
        }


# Global instance for easy access
_template_manager: Optional[TemplateManager] = None


def get_template_manager() -> TemplateManager:
    """Get the global template manager instance."""
    global _template_manager
    if _template_manager is None:
        _template_manager = TemplateManager()
        try:
            _template_manager.load_templates()
        except ConfigurationError:
            # Log but don't fail - fallback mode
            pass
    return _template_manager