#!/usr/bin/env python3
"""Detailed inspection test showing all prompts, raw outputs, and LLM configs per layer."""

import asyncio
import os
import sys
from datetime import datetime
from typing import Dict, Any

from core.schemas import NetworkRequest
from core.config import NetworkConfig
from core.llm_client import LLMClient, LLMConfig
from layers.layer1_reformulation import Reformulator
from layers.layer2_definition import Layer2DefinitionManager
from layers.layer3_validation import Layer3ValidationManager
from layers.layer4_synthesis import Layer4SynthesisManager


class DetailedInspectionNetwork:
    """Network that shows detailed prompts, outputs, and configs for each layer."""

    def __init__(self):
        """Initialize with detailed logging and custom LLM configurations."""
        
        # Create different LLM configs for different layers
        base_config = {
            "api_key": os.getenv("GROQ_API_KEY", ""),
            "model": "openai/gpt-oss-120b",
            "max_tokens": 8192,
            "timeout": 120.0,
            "max_retries": 3
        }
        
        # Layers 1-3: temperature=0.8, reasoning_effort="medium"
        llm_config_layers_1_3 = LLMConfig(
            **base_config,
            temperature=0.8,
            reasoning_effort="medium"
        )
        
        # Layer 4: temperature=0.6, reasoning_effort="high" 
        llm_config_layer_4 = LLMConfig(
            **base_config,
            temperature=0.6,
            reasoning_effort="high"
        )
        
        # Create network configs
        network_config_layers_1_3 = NetworkConfig(
            groq_api_key=base_config["api_key"],
            groq_model="openai/gpt-oss-120b",
            temperature=0.8,
            reasoning_effort="medium",
            max_tokens_per_request=8192,
            request_timeout=120.0,
            max_retries=3
        )
        
        network_config_layer_4 = NetworkConfig(
            groq_api_key=base_config["api_key"],
            groq_model="openai/gpt-oss-120b", 
            temperature=0.6,
            reasoning_effort="high",
            max_tokens_per_request=8192,
            request_timeout=120.0,
            max_retries=3
        )
        
        # Initialize agents with custom configs
        self.reformulator = Reformulator(llm_client=LLMClient(config=llm_config_layers_1_3))
        self.layer2_manager = Layer2DefinitionManager(network_config=network_config_layers_1_3)
        self.layer3_manager = Layer3ValidationManager()
        # Override the validators' LLM clients
        self.layer3_manager.correspondence_validator = type(self.layer3_manager.correspondence_validator)(
            llm_client=LLMClient(config=llm_config_layers_1_3)
        )
        self.layer3_manager.coherence_validator = type(self.layer3_manager.coherence_validator)(
            llm_client=LLMClient(config=llm_config_layers_1_3)
        )
        self.layer3_manager.pragmatic_validator = type(self.layer3_manager.pragmatic_validator)(
            llm_client=LLMClient(config=llm_config_layers_1_3)
        )
        self.layer4_manager = Layer4SynthesisManager(network_config=network_config_layer_4)

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
            # Trigger lazy loading of config and LLM client
            _ = self.reformulator.config
            if self.reformulator.llm_client:
                print(f"   Model: {self.reformulator.llm_client.config.model}")
                print(f"   Temperature: {self.reformulator.llm_client.config.temperature}")
                print(f"   Max Tokens: {self.reformulator.llm_client.config.max_tokens}")
            else:
                print("   LLM Client: Not initialized yet")
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
            for node_name, node in [
                ("Semantic", self.layer2_manager.semantic_node),
                ("Genealogical", self.layer2_manager.genealogical_node),
                ("Teleological", self.layer2_manager.teleological_node)
            ]:
                # Trigger lazy loading
                _ = node.config
                print(f"   {node_name} Node:")
                if node.llm_client:
                    print(f"     Model: {node.llm_client.config.model}")
                    print(f"     Temperature: {node.llm_client.config.temperature}")
                    print(f"     Max Tokens: {node.llm_client.config.max_tokens}")
                else:
                    print("     LLM Client: Not initialized yet")
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
            for validator_name, validator in [
                ("Correspondence", self.layer3_manager.correspondence_validator),
                ("Coherence", self.layer3_manager.coherence_validator),
                ("Pragmatic", self.layer3_manager.pragmatic_validator)
            ]:
                # Trigger lazy loading
                _ = validator.config
                print(f"   {validator_name} Validator:")
                if validator.llm_client:
                    print(f"     Model: {validator.llm_client.config.model}")
                    print(f"     Temperature: {validator.llm_client.config.temperature}")
                    print(f"     Max Tokens: {validator.llm_client.config.max_tokens}")
                else:
                    print("     LLM Client: Not initialized yet")
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
            # Trigger lazy loading
            _ = self.layer4_manager.synthesis_node.config
            if self.layer4_manager.synthesis_node.llm_client:
                print(f"   Model: {self.layer4_manager.synthesis_node.llm_client.config.model}")
                print(f"   Temperature: {self.layer4_manager.synthesis_node.llm_client.config.temperature}")
                print(f"   Max Tokens: {self.layer4_manager.synthesis_node.llm_client.config.max_tokens}")
            else:
                print("   LLM Client: Not initialized yet")
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
    print("🔍 Epistemological Propagation Network - Detailed Inspection Mode")
    print("This will show all prompts, raw outputs, and LLM configurations per layer.")
    print()

    if len(sys.argv) > 1:
        question = " ".join(sys.argv[1:])
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