"""Base configurator classes for EPN pipeline configuration."""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import json
from pathlib import Path

from epn_core.core.logging_config import get_logger


class Configurator(ABC):
    """Abstract base class for configuration wizards."""

    def __init__(self, output_file: str):
        """Initialize the configurator.

        Args:
            output_file: Path where the configuration will be saved
        """
        self.output_file = Path(output_file)
        self.logger = get_logger(f"{self.__class__.__name__}")

    @abstractmethod
    def run_interactive(self) -> Dict[str, Any]:
        """Run the interactive configuration wizard.

        Returns:
            Configuration dictionary
        """
        pass

    def save_config(self, config: Dict[str, Any]) -> None:
        """Save configuration to file.

        Args:
            config: Configuration dictionary to save
        """
        try:
            # Ensure output directory exists
            self.output_file.parent.mkdir(parents=True, exist_ok=True)

            # Save with nice formatting
            with open(self.output_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)

            self.logger.info(f"Configuration saved to {self.output_file}")

        except Exception as e:
            self.logger.error(f"Failed to save configuration: {e}")
            raise

    def load_existing(self, file_path: str) -> Optional[Dict[str, Any]]:
        """Load existing configuration for editing.

        Args:
            file_path: Path to existing configuration file

        Returns:
            Configuration dictionary or None if file doesn't exist
        """
        config_file = Path(file_path)
        if not config_file.exists():
            return None

        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
            self.logger.info(f"Loaded existing configuration from {file_path}")
            return config
        except Exception as e:
            self.logger.error(f"Failed to load existing configuration: {e}")
            return None
