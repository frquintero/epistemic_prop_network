#!/usr/bin/env python3
"""Detailed inspection test showing all prompts, raw outputs, and LLM configs per layer."""

import argparse
import asyncio
import os
import sys
from datetime import datetime
from typing import Dict, Any

from core.schemas import NetworkRequest
from core.config import NetworkConfig
from core.llm_client import LLMClient, LLMConfig
from core.template_manager import get_template_manager
from layers.layer1_reformulation import Reformulator
from layers.layer2_definition import Layer2DefinitionManager
from layers.layer3_validation import Layer3ValidationManager
from layers.layer4_synthesis import Layer4SynthesisManager


class DetailedInspectionNetwork:
    """Network that shows detailed prompts, outputs, and configs for each layer."""

    def __init__(self):
        """Initialize with centralized LLM configurations."""
        
        # Get template manager for centralized LLM configurations
        template_manager = get_template_manager()
        
        # Get LLM configurations for each layer component
        self.llm_configs = {
            'reformulator_node': template_manager.get_llm_config('layer1', 'reformulator_node'),
            'semantic_node': template_manager.get_llm_config('layer2', 'semantic_node'),
            'genealogical_node': template_manager.get_llm_config('layer2', 'genealogical_node'),
            'teleological_node': template_manager.get_llm_config('layer2', 'teleological_node'),
            'coherence_validator': template_manager.get_llm_config('layer3', 'coherence_validator'),
            'correspondence_validator': template_manager.get_llm_config('layer3', 'correspondence_validator'),
            'pragmatic_validator': template_manager.get_llm_config('layer3', 'pragmatic_validator'),
            'synthesis_node': template_manager.get_llm_config('layer4', 'synthesis_node'),
        }
        
        # Initialize agents with centralized configs
        self.reformulator = Reformulator(llm_config=self.llm_configs['reformulator_node'])
        self.layer2_manager = Layer2DefinitionManager(llm_configs={
            'semantic_node': self.llm_configs['semantic_node'],
            'genealogical_node': self.llm_configs['genealogical_node'],
            'teleological_node': self.llm_configs['teleological_node'],
        })
        self.layer3_manager = Layer3ValidationManager(llm_configs={
            'coherence_validator': self.llm_configs['coherence_validator'],
            'correspondence_validator': self.llm_configs['correspondence_validator'],
            'pragmatic_validator': self.llm_configs['pragmatic_validator'],
        })
        self.layer4_manager = Layer4SynthesisManager(llm_config=self.llm_configs['synthesis_node'])

    def _extract_metadata_from_question(self, question: str) -> Dict[str, Any]:
        """Extract metadata from question."""
        return {
            "source": "inspection_test",
            "timestamp": datetime.now().isoformat(),
            "topic": "epistemological_analysis"
        }

    async def inspect_full_pipeline(self, question: str) -> None:
        """Run full pipeline with detailed inspection of each layer."""
        print("=" * 100)
        print("🔍 EPISTEMOLOGICAL PROPAGATION NETWORK - DETAILED INSPECTION")
        print("=" * 100)
        print(f"📝 Original Question: {question}")
        print()

        request_id = f"inspect-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        metadata = self._extract_metadata_from_question(question)

        request = NetworkRequest(
            request_id=request_id,
            original_question=question,
            timestamp=datetime.now().isoformat(),
            metadata=metadata
        )

        try:
            # ===== LAYER 1: REFORMULATION =====
            print("🔄 LAYER 1: REFORMULATION")
            print("-" * 50)

            # Show LLM config for Layer 1
            print("🤖 LLM Configuration:")
            config = self.llm_configs['reformulator_node']
            print(f"   Model: {config.model}")
            print(f"   Temperature: {config.temperature}")
            print(f"   Max Tokens: {config.max_tokens}")
            if hasattr(config, 'tools') and config.tools:
                print(f"   Tools: {len(config.tools)} available")
            print()

            # Show the prompt that will be sent
            reformulator_prompt = self.reformulator._build_reformulation_prompt(request.original_question, request.metadata)
            print("📤 PROMPT SENT TO LLM:")
            print("-" * 30)
            print(reformulator_prompt)
            print("-" * 30)
            print()

            # Process and show output
            print("📥 PROCESSED OUTPUT:")
            print("-" * 30)
            reformulated = await self.reformulator.process(request)
            print(f"Reformulated Question: {reformulated.question}")
            print(f"Original Question: {reformulated.original_question}")
            print(f"Context Added: {reformulated.context_added}")
            print(f"Bias Removed: {reformulated.bias_removed}")
            print("-" * 30)
            print()

            # ===== LAYER 2: DEFINITION GENERATION (PARALLEL) =====
            print("🔄 LAYER 2: DEFINITION GENERATION (PARALLEL)")
            print("-" * 50)

            # Show configs for each node
            print("🤖 LLM Configurations for Layer 2 Nodes:")
            for node_name, config_key in [
                ("Semantic", 'semantic_node'),
                ("Genealogical", 'genealogical_node'),
                ("Teleological", 'teleological_node')
            ]:
                config = self.llm_configs[config_key]
                print(f"   {node_name} Node:")
                print(f"     Model: {config.model}")
                print(f"     Temperature: {config.temperature}")
                print(f"     Max Tokens: {config.max_tokens}")
                if hasattr(config, 'tools') and config.tools:
                    print(f"     Tools: {len(config.tools)} available")
            print()

            # Process Layer 2
            phase2_result = await self.layer2_manager.process(reformulated)

            # Show detailed results for each node
            for node_name, node, prompt_method in [
                ("Semantic", self.layer2_manager.semantic_node, "_build_semantic_prompt"),
                ("Genealogical", self.layer2_manager.genealogical_node, "_build_genealogical_prompt"),
                ("Teleological", self.layer2_manager.teleological_node, "_build_teleological_prompt")
            ]:
                print(f"📋 {node_name.upper()} NODE:")
                print("-" * 30)

                # Show the prompt for this node
                prompt = getattr(node, prompt_method)(reformulated.question)
                print("📤 PROMPT SENT TO LLM:")
                print("-" * 20)
                print(prompt)
                print("-" * 20)

                # Get the result for this node
                if node_name == "Semantic":
                    result = phase2_result.semantic
                elif node_name == "Genealogical":
                    result = phase2_result.genealogical
                else:  # Teleological
                    result = phase2_result.teleological

                print("📥 PROCESSED OUTPUT:")
                print(f"Definition: {result}")
                print(f"Word Count: {len(result.split())}")
                print()

            # ===== LAYER 3: VALIDATION =====
            print("🔄 LAYER 3: VALIDATION")
            print("-" * 50)

            # Show configs for each validator
            print("🤖 LLM Configurations for Layer 3 Validators:")
            for validator_name, config_key in [
                ("Correspondence", 'correspondence_validator'),
                ("Coherence", 'coherence_validator'),
                ("Pragmatic", 'pragmatic_validator')
            ]:
                config = self.llm_configs[config_key]
                print(f"   {validator_name} Validator:")
                print(f"     Model: {config.model}")
                print(f"     Temperature: {config.temperature}")
                print(f"     Max Tokens: {config.max_tokens}")
                if hasattr(config, 'tools') and config.tools:
                    print(f"     Tools: {len(config.tools)} available")
            print()

            # Process Layer 3
            phase3_result = await self.layer3_manager.process(phase2_result)

            # Show detailed results for each validator
            for validator_name, validator, prompt_method in [
                ("Correspondence", self.layer3_manager.correspondence_validator, "_build_correspondence_prompt"),
                ("Coherence", self.layer3_manager.coherence_validator, "_build_coherence_prompt"),
                ("Pragmatic", self.layer3_manager.pragmatic_validator, "_build_pragmatic_prompt")
            ]:
                print(f"📋 {validator_name.upper()} VALIDATOR:")
                print("-" * 30)

                # Show the prompt for this validator
                prompt = getattr(validator, prompt_method)(phase2_result)
                print("📤 PROMPT SENT TO LLM:")
                print("-" * 20)
                print(prompt)
                print("-" * 20)

                # Get the result for this validator
                if validator_name == "Correspondence":
                    result = phase3_result.correspondence
                elif validator_name == "Coherence":
                    result = phase3_result.coherence
                else:  # Pragmatic
                    result = phase3_result.pragmatic

                print("📥 PROCESSED OUTPUT:")
                print(f"Validation: {result}")
                print(f"Word Count: {len(result.split())}")
                print()

            # ===== LAYER 4: SYNTHESIS =====
            print("🔄 LAYER 4: SYNTHESIS")
            print("-" * 50)

            # Show config for synthesis
            print("🤖 LLM Configuration for Layer 4 Synthesis:")
            config = self.llm_configs['synthesis_node']
            print(f"   Model: {config.model}")
            print(f"   Temperature: {config.temperature}")
            print(f"   Max Tokens: {config.max_tokens}")
            if hasattr(config, 'tools') and config.tools:
                print(f"   Tools: {len(config.tools)} available")
            print()

            # Show the prompt that will be sent
            synthesis_prompt = self.layer4_manager.synthesis_node._build_synthesis_prompt(phase3_result)
            print("📤 PROMPT SENT TO LLM:")
            print("-" * 30)
            print(synthesis_prompt)
            print("-" * 30)
            print()

            # Process and show output
            print("📥 RAW SYNTHESIS OUTPUT:")
            print("-" * 30)
            final_result = await self.layer4_manager.process(phase3_result)
            print(f"Raw Response: {final_result.raw_response}")
            print("-" * 30)
            print()

            print("=" * 100)
            print("✅ INSPECTION COMPLETE")
            print("=" * 100)

        except Exception as e:
            print(f"❌ Error during inspection: {str(e)}")
            import traceback
            traceback.print_exc()


async def main():
    """Main entry point for detailed inspection."""
    parser = argparse.ArgumentParser(
        description="Detailed inspection of the Epistemological Propagation Network",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s "What are mental models?"
  %(prog)s --mock "What are mental models?"
        """
    )
    parser.add_argument(
        'question',
        nargs='*',
        help='The question to process through the network'
    )
    parser.add_argument(
        '--mock',
        action='store_true',
        help='Use mock LLM responses for testing (no API calls)'
    )

    args = parser.parse_args()

    # Set up mock responses based on the --mock flag
    if args.mock:
        os.environ['MOCK_RESPONSES'] = 'true'
    else:
        os.environ['MOCK_RESPONSES'] = 'false'

    print("🔍 Epistemological Propagation Network - Detailed Inspection Mode")
    print("This will show all prompts, raw outputs, and LLM configurations per layer.")
    print()

    if args.question:
        question = " ".join(args.question)
    else:
        print("🤔 Please enter your question for detailed inspection:")
        try:
            question = input("> ").strip()
            if not question:
                print("❌ No question provided. Goodbye!")
                return
        except (EOFError, KeyboardInterrupt):
            print("\n👋 Goodbye!")
            return

    if len(question) < 5:
        print("❌ ERROR: Question too short! Please provide a more detailed question.")
        return
    if len(question) > 500:
        print("❌ ERROR: Question too long! Please keep it under 500 characters.")
        return

    inspector = DetailedInspectionNetwork()
    await inspector.inspect_full_pipeline(question)


if __name__ == "__main__":
    asyncio.run(main())