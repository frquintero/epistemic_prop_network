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
        help="Path to layer configuration file "
             "(auto-discovers if not specified)"
    )
    run_parser.add_argument(
        "--template-config", "-t",
        help="Path to template configuration file "
             "(auto-discovers if not specified)"
    )
    run_parser.add_argument(
        "--default",
        action="store_true",
        help="Force use of bundled default configs in `epn_core/config` instead of root files"
    )
    run_parser.add_argument(
        "--merge-defaults",
        action="store_true",
        help="When used with --default, merge bundled defaults with project templates instead of replacing"
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
            run_pipeline(args.query, args.layer_config, args.template_config, args.default, args.merge_defaults)
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


def run_pipeline(query: str, layer_config_file: Optional[str], template_config_file: Optional[str], use_default: bool = False, merge_defaults: bool = False):
    """Run the EPN pipeline with the given query and configuration."""
    print("🚀 Starting Epistemological Propagation Network...")
    print(f"Query: {query}")

    if layer_config_file and template_config_file:
        print(f"Layer config: {layer_config_file}")
        print(f"Template config: {template_config_file}")
    else:
        print("Configuration: Auto-discovering (layer.json/template.json at root, or defaults)")
    print("-" * 60)

    logger = get_logger("CLI")

    try:
        # Initialize pipeline: if using --default, skip auto-discovery so we can load the desired defaults
        if use_default:
            pipeline = Pipeline(skip_autoload=True)

            # Prefer project-level /config/default_*, fall back to bundled epn_core/config defaults
            project_default_layer = "config/default_layer.json"
            project_default_template = "config/default_template.json"

            import os
            if os.path.exists(project_default_layer) and os.path.exists(project_default_template):
                pipeline.load_config(project_default_layer, project_default_template, replace_templates=not merge_defaults)
            else:
                pipeline.load_config("epn_core/config/default_layer.json", "epn_core/config/default_template.json", replace_templates=not merge_defaults)

        else:
            # Initialize with normal auto-discovery
            pipeline = Pipeline()

            # Load configuration if explicitly provided
            if layer_config_file and template_config_file:
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
