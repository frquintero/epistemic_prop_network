"""Template management for the EPN pipeline."""

from typing import Dict, Any, Optional
import logging


class TemplateManager:
    """Manages prompt templates for the EPN pipeline.

    Provides methods to retrieve, validate, and render templates for nodes.
    """

    def __init__(self, templates: Optional[Dict[str, Dict[str, Any]]] = None):
        """Initialize the template manager.

        Args:
            templates: Optional dictionary of templates to load initially
        """
        # Use stdlib logging here to avoid importing into epn_core.core
        self.logger = logging.getLogger("TemplateManager")
        if not self.logger.handlers:
            self.logger.setLevel(logging.INFO)
        self.templates: Dict[str, Dict[str, Any]] = templates or {}

        if templates:
            self.logger.info(f"Initialized with {len(templates)} templates")

    def load_templates(self, templates: Dict[str, Dict[str, Any]], replace: bool = False) -> None:
        """Load templates into the manager.

        Args:
            templates: Dictionary mapping template IDs to template data
            replace: If True, replace existing templates with this set. If False, merge.
        """
        if replace:
            self.templates = dict(templates)
            self.logger.info(f"Replaced templates with {len(templates)} entries")
        else:
            self.templates.update(templates)
            self.logger.info(f"Loaded {len(templates)} templates, total: {len(self.templates)}")

    def get_template(self, template_id: str) -> Dict[str, Any]:
        """Get a template by its ID.

        Args:
            template_id: The template identifier

        Returns:
            Template data dictionary

        Raises:
            KeyError: If template doesn't exist
        """
        if template_id not in self.templates:
            raise KeyError(f"Template '{template_id}' not found")
        return self.templates[template_id]

    def has_template(self, template_id: str) -> bool:
        """Check if a template exists.

        Args:
            template_id: The template identifier

        Returns:
            True if template exists
        """
        return template_id in self.templates

    def render_template(self, template_id: str, variables: Dict[str, Any]) -> str:
        """Render a template with provided variables.

        Args:
            template_id: The template to render
            variables: Dictionary of variable names to values

        Returns:
            Rendered template string

        Raises:
            KeyError: If template doesn't exist
            ValueError: If required variables are missing
        """
        template = self.get_template(template_id)
        template_text = template['template']
        placeholders = template['placeholders']

        # Check that all required variables are provided
        missing_vars = []
        for placeholder in placeholders:
            if placeholder not in variables:
                missing_vars.append(placeholder)

        if missing_vars:
            raise ValueError(f"Missing required variables for template "
                             f"'{template_id}': {missing_vars}")

        # Render the template by replacing placeholders
        rendered = template_text
        for placeholder in placeholders:
            value = variables[placeholder]
            rendered = rendered.replace(f"{{{placeholder}}}", str(value))

        self.logger.debug(f"Rendered template '{template_id}' with "
                          f"variables: {list(variables.keys())}")
        return rendered

    def validate_templates(self) -> bool:
        """Validate that all loaded templates are properly structured.

        Returns:
            True if all templates are valid

        Raises:
            ValueError: If any template is invalid
        """
        if not self.templates:
            raise ValueError("No templates loaded")

        for template_id, template in self.templates.items():
            self._validate_single_template(template_id, template)

        self.logger.info(f"Validated {len(self.templates)} "
                         f"templates successfully")
        return True

    def _validate_single_template(self, template_id: str, template: Dict[str, Any]) -> None:
        """Validate a single template.

        Args:
            template_id: The template identifier
            template: The template data

        Raises:
            ValueError: If template is invalid
        """
        required_keys = ['template', 'placeholders',
                         'metadata']
        for key in required_keys:
            if key not in template:
                raise ValueError(f"Template '{template_id}' missing required key: {key}")

        if not isinstance(template['template'], str):
            raise ValueError(f"Template '{template_id}' template must be a string")

        if not isinstance(template['placeholders'], list):
            raise ValueError(f"Template '{template_id}' placeholders must be a list")

        if not isinstance(template['metadata'], dict):
            raise ValueError(f"Template '{template_id}' metadata must be a dictionary")

        # Check that all placeholders appear in the template
        template_text = template['template']
        for placeholder in template['placeholders']:
            placeholder_pattern = f"{{{placeholder}}}"
            if placeholder_pattern not in template_text:
                raise ValueError(f"Template '{template_id}' placeholder "
                                 f"'{placeholder}' not found in template text")

    def list_templates(self) -> list[str]:
        """Get a list of all available template IDs.

        Returns:
            List of template IDs
        """
        return list(self.templates.keys())

    def get_template_info(self, template_id: str) -> Dict[str, Any]:
        """Get information about a template.

        Args:
            template_id: The template identifier

        Returns:
            Dictionary with template information
        """
        template = self.get_template(template_id)
        return {
            'id': template_id,
            'placeholders': template['placeholders'],
            'metadata': template['metadata']
        }

    def __repr__(self) -> str:
        return f"TemplateManager(templates={len(self.templates)})"
