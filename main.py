#!/usr/bin/env python3
"""Main interface for the Epistemological Propagation Network - shows raw Layer 4 output."""

import asyncio
import os
import uuid
from datetime import datetime
from typing import Dict, Any, Optional

from rich.console import Console
from rich.markdown import Markdown

from core.schemas import NetworkRequest
from core.config import NetworkConfig, init_config
from core.llm_client import LLMClient, LLMConfig
from layers.layer1_reformulation import Reformulator
from layers.layer2_definition import Layer2DefinitionManager
from layers.layer3_validation import Layer3ValidationManager
from layers.layer4_synthesis import Layer4SynthesisManager


# Initialize configuration and logging
init_config()


class EpistemologicalPropagationNetwork:
    """Main interface for the Epistemological Propagation Network."""

    def __init__(self):
        """Initialize the EPN with all layer managers and optimized LLM configurations."""
        
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
        
        # Initialize agents with optimized configs
        self.reformulator = Reformulator(llm_client=LLMClient(config=llm_config_layers_1_3))
        self.layer2_manager = Layer2DefinitionManager(network_config=network_config_layers_1_3)
        self.layer3_manager = Layer3ValidationManager()
        # Override the validators' LLM clients with optimized config
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
        """Automatically extract metadata from the question content."""
        metadata = {
            "source": "user_query",
            "timestamp": datetime.now().isoformat(),
        }

        # Simple topic detection based on keywords
        question_lower = question.lower()
        
        if any(word in question_lower for word in ["mind", "mental", "cognitive", "brain", "psychology"]):
            metadata["topic"] = "Cognitive Science"
            metadata["domain"] = "cognitive_science"
        elif any(word in question_lower for word in ["philosophy", "epistemology", "knowledge", "truth"]):
            metadata["topic"] = "Philosophy"
            metadata["domain"] = "philosophy"
        elif any(word in question_lower for word in ["science", "physics", "biology", "chemistry"]):
            metadata["topic"] = "Natural Sciences"
            metadata["domain"] = "natural_sciences"
        elif any(word in question_lower for word in ["history", "historical", "past", "ancient"]):
            metadata["topic"] = "History"
            metadata["domain"] = "history"
        elif any(word in question_lower for word in ["art", "culture", "society", "social"]):
            metadata["topic"] = "Arts & Culture"
            metadata["domain"] = "arts_culture"
        elif any(word in question_lower for word in ["technology", "computer", "ai", "artificial"]):
            metadata["topic"] = "Technology"
            metadata["domain"] = "technology"
        elif any(word in question_lower for word in ["economics", "business", "market", "finance"]):
            metadata["topic"] = "Economics"
            metadata["domain"] = "economics"
        else:
            metadata["topic"] = "General Inquiry"
            metadata["domain"] = "general"

        return metadata

    async def process_question(self, question: str, user_id: Optional[str] = None) -> Dict[str, Any]:
        """Process a user question through the complete 4-layer network."""
        request_id = f"epn-{uuid.uuid4().hex[:12]}"
        metadata = self._extract_metadata_from_question(question)

        if user_id:
            metadata["user_id"] = user_id

        request = NetworkRequest(
            request_id=request_id,
            original_question=question,
            timestamp=datetime.now().isoformat(),
            metadata=metadata
        )

        print(f"🧠 Processing question: {question}")
        print(f"📊 Auto-detected metadata: {metadata}")

        try:
            print("\n🔄 Layer 1: Reformulation...")
            reformulated = await self.reformulator.process(request)

            print("🔄 Layer 2: Definition Generation...")
            phase2_result = await self.layer2_manager.process(reformulated)

            print("🔄 Layer 3: Validation...")
            phase3_result = await self.layer3_manager.process(phase2_result)

            print("🔄 Layer 4: Synthesis...")
            final_result = await self.layer4_manager.process(phase3_result)

            return {
                "success": True,
                "request_id": request_id,
                "original_question": question,
                "reformulated_question": reformulated.question,
                "metadata": metadata,
                "result": {
                    "raw_response": final_result.raw_response
                },
                "processing_time": datetime.now().isoformat()
            }

        except Exception as e:
            print(f"❌ Error processing question: {str(e)}")
            return {
                "success": False,
                "request_id": request_id,
                "original_question": question,
                "error": str(e),
                "metadata": metadata
            }


async def main():
    """Main entry point for the CLI interface."""
    print("Setting up Epistemological Propagation Network...")

    if len(os.sys.argv) > 1:
        question = " ".join(os.sys.argv[1:])
    else:
        print("🤔 Welcome to the Epistemological Propagation Network!")
        print("Please enter your question (or 'quit' to exit):")
        try:
            question = input("> ").strip()
            if not question:
                print("❌ No question provided. Goodbye!")
                return
            if question.lower() in ['quit', 'exit', 'q']:
                print("👋 Goodbye!")
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

    print(f"🔍 Processing question: {question}")
    print("-" * 60)

    epn = EpistemologicalPropagationNetwork()
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
        print("✅ Analysis complete! The Epistemological Propagation Network has processed your question.")
        print("\n📝 Note: This is formatted as a Markdown handoff document with the reformulated question as header.")
    else:
        print(f"❌ Processing failed: {result['error']}")


if __name__ == "__main__":
    asyncio.run(main())
