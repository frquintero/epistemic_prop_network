"""Core data models and schemas for the Epistemological Propagation Network."""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, ConfigDict


class BaseTriple(BaseModel):
    """Base class for all triple structures in the network."""

    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        validate_assignment=True
    )


class Phase2Triple(BaseTriple):
    """Triple structure for Phase 2 Definition Generation outputs."""

    semantic: str = Field(
        ...,
        description="Semantic definition output from Semantic Node",
        min_length=10
    )
    genealogical: str = Field(
        ...,
        description="Historical/genealogical output from Genealogical Node",
        min_length=10
    )
    teleological: str = Field(
        ...,
        description="Functional/teleological output from Teleological Node",
        min_length=10
    )


class Phase3Triple(BaseTriple):
    """Triple structure for Phase 3 Validation outputs."""

    correspondence: str = Field(
        ...,
        description="Correspondence validation output from Correspondence Validator",
        min_length=10
    )
    coherence: str = Field(
        ...,
        description="Coherence validation output from Coherence Validator",
        min_length=10
    )
    pragmatic: str = Field(
        ...,
        description="Pragmatic validation output from Pragmatic Validator",
        min_length=10
    )


class ReformulatedQuestion(BaseModel):
    """Structure for reformulated questions from Phase 1."""

    question: str = Field(
        ...,
        description="The reformulated, bias-free question",
        min_length=5
    )
    original_question: str = Field(
        ...,
        description="The original user question for reference"
    )
    context_added: List[str] = Field(
        default_factory=list,
        description="List of contextual elements added during reformulation"
    )
    bias_removed: List[str] = Field(
        default_factory=list,
        description="List of bias elements identified and removed"
    )


class SynthesisOutput(BaseModel):
    """Structure for final synthesis output from Phase 4."""

    raw_response: str = Field(
        ...,
        description="Raw LLM response from Layer 4 synthesis",
        min_length=1
    )


class ValidationResult(BaseModel):
    """Structure for individual validation results."""

    validator_type: str = Field(
        ...,
        description="Type of validator (correspondence, coherence, pragmatic)"
    )
    score: float = Field(
        ...,
        description="Validation score (0.0 to 1.0)",
        ge=0.0,
        le=1.0
    )
    assessment: str = Field(
        ...,
        description="Detailed validation assessment",
        min_length=10
    )
    confidence: float = Field(
        ...,
        description="Confidence in the validation result",
        ge=0.0,
        le=1.0
    )
    issues: List[str] = Field(
        default_factory=list,
        description="List of identified issues or concerns"
    )


class NetworkRequest(BaseModel):
    """Structure for network processing requests."""

    request_id: str = Field(
        ...,
        description="Unique identifier for the request"
    )
    original_question: str = Field(
        ...,
        description="Original user question"
    )
    timestamp: str = Field(
        ...,
        description="Request timestamp in ISO format"
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional request metadata"
    )


class NetworkResponse(BaseModel):
    """Structure for network processing responses."""

    request_id: str = Field(
        ...,
        description="Request identifier"
    )
    success: bool = Field(
        ...,
        description="Whether processing was successful"
    )
    synthesis: Optional[SynthesisOutput] = Field(
        None,
        description="Final synthesis output if successful"
    )
    error_message: Optional[str] = Field(
        None,
        description="Error message if processing failed"
    )
    processing_time: float = Field(
        ...,
        description="Total processing time in seconds"
    )
    phase_timings: Dict[str, float] = Field(
        default_factory=dict,
        description="Processing time for each phase"
    )