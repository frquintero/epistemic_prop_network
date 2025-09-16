#!/usr/bin/env python3
"""FastAPI web service for the Epistemological Propagation Network."""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
import uvicorn
import asyncio
import os
from datetime import datetime

from main import EpistemologicalPropagationNetwork


class QuestionRequest(BaseModel):
    """Request model for user questions."""
    question: str
    user_id: Optional[str] = None


class QuestionResponse(BaseModel):
    """Response model for EPN results."""
    success: bool
    request_id: str
    original_question: str
    metadata: dict
    result: Optional[dict] = None
    error: Optional[str] = None
    processing_time: str


app = FastAPI(
    title="Epistemological Propagation Network API",
    description="A sophisticated multi-layer LLM system for rigorous epistemological inquiry",
    version="1.0.0"
)

# Global EPN instance
epn = None


@app.on_event("startup")
async def startup_event():
    """Initialize the EPN on startup."""
    global epn
    if not os.getenv("GROQ_API_KEY"):
        raise RuntimeError("GROQ_API_KEY environment variable not found!")
    epn = EpistemologicalPropagationNetwork()
    print("🧠 EPN initialized and ready to process questions!")


@app.post("/api/query", response_model=QuestionResponse)
async def process_query(request: QuestionRequest):
    """Process a user question through the complete EPN.

    This endpoint automatically:
    - Extracts metadata from the question content
    - Creates appropriate NetworkRequest objects
    - Processes through all 4 layers
    - Returns comprehensive epistemological analysis
    """
    if not epn:
        raise HTTPException(status_code=500, detail="EPN not initialized")

    try:
        result = await epn.process_question(request.question, request.user_id)
        return QuestionResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")


@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "Epistemological Propagation Network"
    }


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": "Epistemological Propagation Network API",
        "version": "1.0.0",
        "endpoints": {
            "POST /api/query": "Process a question through the EPN",
            "GET /api/health": "Health check"
        },
        "example": {
            "method": "POST",
            "url": "/api/query",
            "body": {
                "question": "What does Tezcatlipoca mean to our current society?",
                "user_id": "optional_user_id"
            }
        }
    }


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)