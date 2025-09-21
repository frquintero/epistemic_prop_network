"""Concrete node implementations for the EPN pipeline."""

from typing import Any, Dict
from ..core.node import Node, NodeConfig


class BasicLLMNode(Node):
    """A basic LLM processing node that renders templates and calls the LLM."""

    async def process(self, input_data: Any) -> str:
        """Process input data through the LLM with the configured template.

        Args:
            input_data: Input data for processing. Can be a string or dict.

        Returns:
            LLM response as a string
        """
        self.logger.info(f"Processing input in node {self.config.node_id}")

        # Prepare variables for template rendering
        variables = self._prepare_variables(input_data)

        # Render the prompt
        prompt = self._render_prompt(variables)

        # Log the rendered prompt for debugging
        self.logger.info(f"Node {self.config.node_id} prompt:\n{prompt}")

        # Call the LLM
        try:
            response = await self.llm_client.generate(prompt)
            self.logger.info(f"Node {self.config.node_id} raw LLM response:\n{response}")
            self.logger.debug(f"Node {self.config.node_id} completed processing")
            return response
        except Exception as e:
            self.logger.error(f"Error in node {self.config.node_id}: {e}")
            raise

    def _prepare_variables(self, input_data: Any) -> Dict[str, Any]:
        """Prepare variables for template rendering from input data.

        This method handles different input data formats and maps them
        to the expected template variables based on the input_context.

        Args:
            input_data: The input data

        Returns:
            Dictionary of variables for template rendering
        """
        variables = {}
        
        # Extract placeholders from input_context strictly using brace syntax as defined
        input_context = self.template['input_context']
        placeholders = set()
        import re
        if isinstance(input_context, list):
            for context_item in input_context:
                found = re.findall(r'\{([^}]+)\}', context_item)
                placeholders.update(found)
        else:
            found = re.findall(r'\{([^}]+)\}', str(input_context))
            placeholders.update(found)

        # Debug: log placeholders and incoming input_data keys
        try:
            self.logger.debug(f"Node {self.config.node_id} detected placeholders: {placeholders}")
            if isinstance(input_data, dict):
                self.logger.debug(f"Node {self.config.node_id} input_data keys: {list(input_data.keys())}")
            else:
                self.logger.debug(f"Node {self.config.node_id} input_data (raw): {type(input_data).__name__}")
        except Exception:
            pass

        # Handle different input types
        if isinstance(input_data, str):
            # For layer 1 reformulator: raw query string
            # Populate only exact placeholders per canonical contract
            if 'question' in placeholders:
                variables['question'] = input_data
            if 'query' in placeholders:
                variables['query'] = input_data
            if 'context_info' in placeholders:
                variables['context_info'] = ''
            # Do NOT perform fuzzy mapping; only set placeholders explicitly
            for placeholder in placeholders:
                if placeholder not in variables:
                    variables[placeholder] = input_data

        elif isinstance(input_data, dict):
            # For layer 2 and 3: dict with specific keys
            # Direct mapping for the new template structure
            for placeholder in placeholders:
                if placeholder in input_data:
                    variables[placeholder] = input_data[placeholder]
                else:
                    # Handle special cases
                    if placeholder == 'context_info':
                        variables[placeholder] = ''  # Empty context
                    else:
                        available_keys = list(input_data.keys())
                        raise ValueError(
                            f"Missing required input variable '{placeholder}' for node {self.config.node_id}. "
                            f"Available input keys: {available_keys}"
                        )

        else:
            # For other types, try to convert to string
            if placeholders:
                variables[list(placeholders)[0]] = str(input_data)

        return variables