#!/usr/bin/env python3
"""Main int        # Set up         # Set up template manager with specified file
if template_file != 'layers/templates2.json':  # Only change if not default
    global _template_manager
    from core.template_manager import TemplateManager, _template_manager

    # Store original template manager
    self._original_template_manager = _template_manager

    # Clear cache and create custom template manager
    _template_manager = None  # Clear cache
    custom_template_manager = TemplateManager(template_file=template_file)
    custom_template_manager.load_templates()

    # Replace global template manager
    _template_manager = custom_template_manager
    template_manager = custom_template_manager
else:
    template_manager = get_template_manager()ith specified file
if template_file != 'layers/templates2.json':  # Only change if not default
    global _template_manager
    from core.template_manager import TemplateManager, _template_manager

    # Store original template manager
    self._original_template_manager = _template_manager

    # Clear cache and create custom template manager
    _template_manager = None  # Clear cache
    custom_template_manager = TemplateManager(template_file=template_file)
    custom_template_manager.load_templates()

    # Replace global template manager
    _template_manager = custom_template_manager
    template_manager = custom_template_manager
else:
    template_manager = get_template_manager()stemological Propagation Network - shows raw Layer 4 output.
"""

import argparse
import asyncio
import os
import uuid
from datetime import datetime
from typing import Any, Dict, Optional

from rich.console import Console
from rich.markdown import Markdown

from core.config import NetworkConfig, init_config
from core.llm_client import LLMClient, LLMConfig
from core.schemas import NetworkRequest
from core.template_manager import _template_manager, get_template_manager
from layers.layer1_reformulation import Reformulator
from layers.layer2_definition import Layer2DefinitionManager
from layers.layer3_validation import Layer3ValidationManager
from layers.layer4_synthesis import Layer4SynthesisManager

# Initialize configuration and logging will be done in main() after parsing args
# init_config()  # Removed - will be called with proper logging config


class EpistemologicalPropagationNetwork:
    """Main interface for the Epistemological Propagation Network."""

    def __init__(
        self,
        enable_structlog: bool = False,
        template_file: str = "layers/templates2.json",
    ):
        """Initialize the EPN with all layer managers using centralized LLM configurations."""
        self.enable_structlog = enable_structlog

        # Set up template manager with specified file
        if template_file != "layers/templates2.json":  # Only change if not default
            global _template_manager
            from core.template_manager import TemplateManager, _template_manager

            # Store original template manager
            self._original_template_manager = _template_manager

            # Clear cache and create custom template manager
            _template_manager = None  # Clear cache
            custom_template_manager = TemplateManager(template_file=template_file)
            custom_template_manager.load_templates()

            # Replace global template manager
            _template_manager = custom_template_manager
            template_manager = custom_template_manager
        else:
            template_manager = get_template_manager()

        # Get LLM configurations for each layer component
        llm_configs = {
            "reformulator_node": template_manager.get_llm_config(
                "layer1", "reformulator_node"
            ),
            "semantic_node": template_manager.get_llm_config("layer2", "semantic_node"),
            "genealogical_node": template_manager.get_llm_config(
                "layer2", "genealogical_node"
            ),
            "teleological_node": template_manager.get_llm_config(
                "layer2", "teleological_node"
            ),
            "coherence_validator": template_manager.get_llm_config(
                "layer3", "coherence_validator"
            ),
            "pragmatic_validator": template_manager.get_llm_config(
                "layer3", "pragmatic_validator"
            ),
            "tension_validator": template_manager.get_llm_config(
                "layer3", "tension_validator"
            ),
            "synthesis_node": template_manager.get_llm_config(
                "layer4", "synthesis_node"
            ),
        }

        # Initialize agents with centralized configs
        self.reformulator = Reformulator(llm_config=llm_configs["reformulator_node"])
        self.layer2_manager = Layer2DefinitionManager(
            llm_configs={
                "semantic_node": llm_configs["semantic_node"],
                "genealogical_node": llm_configs["genealogical_node"],
                "teleological_node": llm_configs["teleological_node"],
            }
        )
        self.layer3_manager = Layer3ValidationManager(
            llm_configs={
                "coherence_validator": llm_configs["coherence_validator"],
                "pragmatic_validator": llm_configs["pragmatic_validator"],
                "tension_validator": llm_configs["tension_validator"],
            }
        )
        self.layer4_manager = Layer4SynthesisManager(
            llm_config=llm_configs["synthesis_node"]
        )

    def cleanup(self):
        """Restore the original template manager if it was changed."""
        if hasattr(self, "_original_template_manager"):
            global _template_manager
            from core.template_manager import _template_manager

            _template_manager = self._original_template_manager

    def _extract_metadata_from_question(self, question: str) -> Dict[str, Any]:
        """Automatically extract metadata from the question content."""
        metadata = {
            "source": "user_query",
            "timestamp": datetime.now().isoformat(),
        }

        # Simple topic detection based on keywords
        question_lower = question.lower()

        if any(
            word in question_lower
            for word in ["mind", "mental", "cognitive", "brain", "psychology"]
        ):
            metadata["topic"] = "Cognitive Science"
            metadata["domain"] = "cognitive_science"
        elif any(
            word in question_lower
            for word in ["philosophy", "epistemology", "knowledge", "truth"]
        ):
            metadata["topic"] = "Philosophy"
            metadata["domain"] = "philosophy"
        elif any(
            word in question_lower
            for word in ["science", "physics", "biology", "chemistry"]
        ):
            metadata["topic"] = "Natural Sciences"
            metadata["domain"] = "natural_sciences"
        elif any(
            word in question_lower
            for word in ["history", "historical", "past", "ancient"]
        ):
            metadata["topic"] = "History"
            metadata["domain"] = "history"
        elif any(
            word in question_lower for word in ["art", "culture", "society", "social"]
        ):
            metadata["topic"] = "Arts & Culture"
            metadata["domain"] = "arts_culture"
        elif any(
            word in question_lower
            for word in ["technology", "computer", "ai", "artificial"]
        ):
            metadata["topic"] = "Technology"
            metadata["domain"] = "technology"
        elif any(
            word in question_lower
            for word in ["economics", "business", "market", "finance"]
        ):
            metadata["topic"] = "Economics"
            metadata["domain"] = "economics"
        else:
            metadata["topic"] = "General Inquiry"
            metadata["domain"] = "general"

        return metadata

    async def process_question(
        self, question: str, user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Process a user question through the complete 4-layer network."""
        request_id = f"epn-{uuid.uuid4().hex[:12]}"
        metadata = self._extract_metadata_from_question(question)

        if user_id:
            metadata["user_id"] = user_id

        request = NetworkRequest(
            request_id=request_id,
            original_question=question,
            timestamp=datetime.now().isoformat(),
            metadata=metadata,
        )

        print(f"🧠 Processing question: {question}")
        if self.enable_structlog:
            print(f"📊 Auto-detected metadata: {metadata}")

        try:
            if self.enable_structlog:
                print("\n🔄 Layer 1: Reformulation...")
            reformulated = await self.reformulator.process(request)

            if self.enable_structlog:
                print("🔄 Layer 2: Definition Generation...")
            phase2_result = await self.layer2_manager.process(reformulated)

            if self.enable_structlog:
                print("🔄 Layer 3: Validation...")
            phase3_result = await self.layer3_manager.process(phase2_result)

            if self.enable_structlog:
                print("🔄 Layer 4: Synthesis...")
            final_result = await self.layer4_manager.process(phase3_result)

            return {
                "success": True,
                "request_id": request_id,
                "original_question": question,
                "reformulated_question": reformulated.question,
                "metadata": metadata,
                "result": {"raw_response": final_result.raw_response},
                "processing_time": datetime.now().isoformat(),
            }

        except Exception as e:
            print(f"❌ Error processing question: {str(e)}")
            return {
                "success": False,
                "request_id": request_id,
                "original_question": question,
                "error": str(e),
                "metadata": metadata,
            }


async def main():
    """Main entry point for the CLI interface."""
    parser = argparse.ArgumentParser(
        description="Epistemological Propagation Network - Process questions through multi-layer analysis",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s "What are mental models?"
  %(prog)s --template templates.json "What are mental models?"
  %(prog)s --template layers/templates3.json "What are mental models?"
  %(prog)s --structlog "What are mental models?"
  %(prog)s --mock "What are mental models?"
  %(prog)s  # Interactive mode
        """,
    )
    parser.add_argument(
        "question",
        nargs="*",
        help="The question to process (if not provided, enters interactive mode)",
    )
    parser.add_argument(
        "--structlog",
        action="store_true",
        help="Enable detailed structured logging for debugging",
    )
    parser.add_argument(
        "--mock",
        action="store_true",
        help="Use mock LLM responses for testing (no API calls)",
    )
    parser.add_argument(
        "--template",
        default="layers/templates2.json",
        choices=["templates.json", "layers/templates2.json", "layers/templates3.json"],
        help="Template file to use (default: layers/templates2.json)",
    )

    args = parser.parse_args()

    # Set up logging based on the --structlog flag
    if args.structlog:
        os.environ["STRUCTURED_LOGGING"] = "true"
    else:
        os.environ["STRUCTURED_LOGGING"] = "false"

    # Set up mock responses based on the --mock flag
    if args.mock:
        os.environ["MOCK_RESPONSES"] = "true"
    else:
        os.environ["MOCK_RESPONSES"] = "false"

    # Initialize configuration with proper logging setup
    init_config()

    # Determine the question
    if args.question:
        question = " ".join(args.question)
    else:
        print("🤔 Welcome to the Epistemological Propagation Network!")
        print("Please enter your question (or 'quit' to exit):")
        try:
            question = input("> ").strip()
            if not question:
                print("❌ No question provided. Goodbye!")
                return
            if question.lower() in ["quit", "exit", "q"]:
                print("👋 Goodbye!")
                return
        except (EOFError, KeyboardInterrupt):
            print("\n👋 Goodbye!")
            return

    # Only show setup message if structlog is enabled
    if args.structlog:
        print("Setting up Epistemological Propagation Network...")

    if len(question) < 5:
        print("❌ ERROR: Question too short! Please provide a more detailed question.")
        return
    if len(question) > 500:
        print("❌ ERROR: Question too long! Please keep it under 500 characters.")
        return

    print(f"🔍 Processing question: {question}")
    print("-" * 60)

    epn = EpistemologicalPropagationNetwork(
        enable_structlog=args.structlog, template_file=args.template
    )
    try:
        result = await epn.process_question(question)

        if result["success"]:
            print("\n" + "=" * 80)
            print("🎯 EPISTEMOLOGICAL PROPAGATION NETWORK RESULT")
            print("=" * 80)
            print("\n📄 MARKDOWN HANDOFF DOCUMENT:")
            print("-" * 50)
            print()

            # Initialize Rich console for markdown rendering
            console = Console()

            # Format as Markdown document with reformulated question as header
            markdown_content = f"""# {result['reformulated_question']}

## Epistemological Analysis

{result['result']['raw_response']}

---
*Generated by Epistemological Propagation Network - Layer 4 Synthesis*
"""

            # Render markdown with Rich
            console.print(Markdown(markdown_content))

            print("\n" + "=" * 80)
            print(
                "✅ Analysis complete! The Epistemological Propagation Network has processed your question."
            )
            print(
                "\n📝 Note: This is formatted as a Markdown handoff document with the reformulated question as header."
            )
        else:
            print(f"❌ Processing failed: {result['error']}")
    finally:
        epn.cleanup()


if __name__ == "__main__":
    asyncio.run(main())
