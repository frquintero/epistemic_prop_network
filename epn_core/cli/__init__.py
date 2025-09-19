"""Command-line interface for EPN configuration tools."""

import argparse
import sys
from typing import Optional

from .base_configurator import Configurator
from .layer_configurator import LayerConfigurator
from .template_configurator import TemplateConfigurator
from ..core.pipeline import Pipeline
from epn_core.core.logging_config import get_logger

__all__ = [
    'Configurator',
    'LayerConfigurator',
    'TemplateConfigurator',
    'main',
]


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Epistemological Propagation Network - Configuration Tools",
        prog="epn"
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # create-layer command
    layer_parser = subparsers.add_parser(
        "create-layer",
        help="Create a new layer configuration interactively"
    )
    layer_parser.add_argument(
        "--output", "-o",
        default="config/default_layer.json",
        help="Output file path (default: config/default_layer.json)"
    )

    # create-template command
    template_parser = subparsers.add_parser(
        "create-template",
        help="Create a new template configuration interactively"
    )
    template_parser.add_argument(
        "--output", "-o",
        default="config/default_template.json",
        help="Output file path (default: config/default_template.json)"
    )
    template_parser.add_argument(
        "--layer-config", "-l",
        help="Path to layer config file to determine required templates"
    )

    # run command
    run_parser = subparsers.add_parser(
        "run",
        help="Run the EPN pipeline with a query"
    )
    run_parser.add_argument(
        "query",
        help="The query to process through the EPN pipeline"
    )
    run_parser.add_argument(
        "--layer-config", "-l",
        default="epn_core/config/default_layer.json",
        help="Path to layer configuration file "
             "(default: epn_core/config/default_layer.json)"
    )
    run_parser.add_argument(
        "--template-config", "-t",
        default="epn_core/config/default_template.json",
        help="Path to template configuration file "
             "(default: epn_core/config/default_template.json)"
    )

    # Parse arguments
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    logger = get_logger("CLI")

    try:
        if args.command == "create-layer":
            create_layer_config(args.output)
        elif args.command == "create-template":
            create_template_config(args.output, args.layer_config)
        elif args.command == "run":
            run_pipeline(args.query, args.layer_config, args.template_config)
        else:
            parser.print_help()

    except KeyboardInterrupt:
        print("\n\n⚠️  Configuration cancelled by user.")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Configuration failed: {e}")
        print(f"\n❌ Configuration failed: {e}")
        sys.exit(1)


def create_layer_config(output_file: str):
    """Create layer configuration interactively."""
    print("🚀 Starting Layer Configuration Wizard...")

    configurator = LayerConfigurator(output_file)
    config = configurator.run_interactive()

    # Show summary
    print("\n📋 Configuration Summary:")
    print("-" * 30)
    print(f"Output file: {output_file}")
    print(f"Layers: {len(config['layers'])}")

    for layer in config['layers']:
        print(f"  • {layer['id']}: {layer['name']} ({len(layer['nodes'])} nodes)")

    # Confirm save
    save = input("\n💾 Save this configuration? (y/n) [y]: ").strip().lower()
    if save in ('', 'y', 'yes'):
        configurator.save_config(config)
        print(f"\n✅ Layer configuration saved to {output_file}")
    else:
        print("\n⚠️  Configuration not saved.")


def create_template_config(output_file: str, layer_config_file: Optional[str]):
    """Create template configuration interactively."""
    print("🚀 Starting Template Configuration Wizard...")

    configurator = TemplateConfigurator(output_file, layer_config_file)
    config = configurator.run_interactive()

    # Show summary
    print("\n📋 Configuration Summary:")
    print("-" * 30)
    print(f"Output file: {output_file}")
    print(f"Templates: {len(config['templates'])}")

    for template_id in config['templates']:
        template = config['templates'][template_id]
        placeholders = template['placeholders']
        print(f"  • {template_id}: {len(placeholders)} placeholders")

    # Confirm save
    save = input("\n💾 Save this configuration? (y/n) [y]: ").strip().lower()
    if save in ('', 'y', 'yes'):
        configurator.save_config(config)
        print(f"\n✅ Template configuration saved to {output_file}")
    else:
        print("\n⚠️  Configuration not saved.")


def run_pipeline(query: str, layer_config_file: str, template_config_file: str):
    """Run the EPN pipeline with the given query and configuration."""
    print("🚀 Starting Epistemological Propagation Network...")
    print(f"Query: {query}")
    print(f"Layer config: {layer_config_file}")
    print(f"Template config: {template_config_file}")
    print("-" * 60)

    logger = get_logger("CLI")

    try:
        # Initialize pipeline
        pipeline = Pipeline()

        # Load configuration
        pipeline.load_config(layer_config_file, template_config_file)

        # Run the pipeline
        import asyncio
        result = asyncio.run(pipeline.process(query))

        # Display results
        print("\n📋 Pipeline Results:")
        print("=" * 60)

        if isinstance(result, dict):
            for key, value in result.items():
                print(f"\n🔹 {key}:")
                print(f"{value}")
        else:
            print(result)

        print("\n✅ Pipeline execution completed successfully!")

    except FileNotFoundError as e:
        logger.error(f"Configuration file not found: {e}")
        print(f"\n❌ Configuration file not found: {e}")
        print("💡 Use 'epn create-layer' and 'epn create-template' "
              "to create configuration files.")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Pipeline execution failed: {e}")
        print(f"\n❌ Pipeline execution failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
