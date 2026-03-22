"""
EPA REST API Server
Provides HTTP endpoints for the Emergent Prompt Architecture system
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional
import time
import uuid

from epa import Onton, OntologicalLattice, GenesisAssembler, SafetyValidator
from epa.onton import OntonType
from epa.feedback import FeedbackEngine
from epa.config import SystemMode


# Pydantic models for API requests/responses
class IngestRequest(BaseModel):
    source: str
    content: str
    timestamp: Optional[float] = Field(default_factory=time.time)
    metadata: Optional[Dict[str, Any]] = {}


class IngestResponse(BaseModel):
    status: str
    trace_id: str
    activated_nodes: int
    new_nodes_created: int


class CrystallizeRequest(BaseModel):
    session_id: Optional[str] = ""
    target_model: Optional[str] = "default"
    mode: Optional[SystemMode] = SystemMode.SENTIO


class CrystallizeResponse(BaseModel):
    prompt_object: Dict[str, Any]
    provenance: Dict[str, List[str]]
    goldendag_hash: str
    trace_id: str


class FeedbackRequest(BaseModel):
    trace_id: str
    feedback_score: float = Field(ge=-1.0, le=1.0)
    reason: Optional[str] = ""
    session_id: Optional[str] = ""


class FeedbackResponse(BaseModel):
    status: str
    onton_updates: Dict[str, str]
    affected_count: int
    feedback_id: int


class LatticeStatsResponse(BaseModel):
    total_ontons: int
    type_distribution: Dict[str, int]
    total_associations: int
    average_weight: float
    active_sessions: int


class HealthResponse(BaseModel):
    status: str
    timestamp: float
    version: str


# Initialize FastAPI app
app = FastAPI(
    title="Emergent Prompt Architecture API",
    description="REST API for the EPA dynamic prompt generation system",
    version="1.0.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize EPA components
lattice = OntologicalLattice()
assembler = GenesisAssembler(lattice)
safety_validator = SafetyValidator()
feedback_engine = FeedbackEngine(lattice)

# Store active sessions and assembly results
active_sessions: Dict[str, Dict[str, Any]] = {}
assembly_cache: Dict[str, Dict[str, Any]] = {}


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(status="healthy", timestamp=time.time(), version="1.0.0")


@app.post("/api/v1/ingest", response_model=IngestResponse)
async def ingest_stimuli(request: IngestRequest):
    """
    Feed raw data into the Ontological Lattice
    """
    try:
        # Validate input safety
        is_safe, reason = safety_validator.validate_input(
            request.content, request.metadata
        )
        if not is_safe:
            raise HTTPException(
                status_code=400, detail=f"Safety validation failed: {reason}"
            )

        # Create Ontons from input
        new_ontons = []

        # Create content Onton
        content_onton = Onton(
            id="",  # Will be generated
            content=request.content,
            type=OntonType.CONTEXT,
            weight=0.8,
            metadata=request.metadata or {},
        )
        new_ontons.append(content_onton)

        # Create source marker Onton if metadata provided
        if request.metadata:
            source_onton = Onton(
                id="",  # Will be generated
                content=f"Source: {request.source}",
                type=OntonType.MEMORY,
                weight=0.6,
                metadata={"source": request.source},
            )
            new_ontons.append(source_onton)

        # Add Ontons to lattice
        nodes_before = len(lattice.ontons)
        for onton in new_ontons:
            lattice.add_onton(onton)
        nodes_after = len(lattice.ontons)

        # Query for activated nodes
        activated_ontons = lattice.query(request.content)

        # Generate trace ID
        trace_id = f"INGEST-{uuid.uuid4().hex[:16]}"

        return IngestResponse(
            status="success",
            trace_id=trace_id,
            activated_nodes=len(activated_ontons),
            new_nodes_created=nodes_after - nodes_before,
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ingestion failed: {str(e)}")


@app.post("/api/v1/crystallize", response_model=CrystallizeResponse)
async def crystallize_prompt(request: CrystallizeRequest):
    """
    Generate a dynamic prompt based on current lattice state
    """
    try:
        # For demonstration, we'll use a simple user input
        # In a real implementation, this would come from session context
        user_input = "Generate a helpful response"

        # Set assembler mode
        if request.mode:
            assembler.mode = request.mode

        # Crystallize prompt
        result = assembler.crystallize(user_input, request.session_id or "")

        # Cache result for feedback
        assembly_cache[result.trace_id] = {"result": result, "timestamp": time.time()}

        # Update session
        if request.session_id:
            active_sessions[request.session_id] = {
                "last_interaction": time.time(),
                "last_trace_id": result.trace_id,
            }

        return CrystallizeResponse(
            prompt_object={
                "system_message": result.system_message,
                "user_message": result.user_message,
                "context_window": result.context_window,
            },
            provenance=result.provenance,
            goldendag_hash=result.goldendag_hash,
            trace_id=result.trace_id,
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Crystallization failed: {str(e)}")


@app.post("/api/v1/feedback", response_model=FeedbackResponse)
async def process_feedback(request: FeedbackRequest):
    """
    Apply feedback to refine the lattice
    """
    try:
        # Process feedback
        result = feedback_engine.process_user_feedback(
            request.trace_id,
            request.feedback_score,
            request.reason or "",
            request.session_id or "",
        )

        return FeedbackResponse(
            status=result["status"],
            onton_updates=result["onton_updates"],
            affected_count=result["affected_count"],
            feedback_id=result["feedback_id"],
        )

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Feedback processing failed: {str(e)}"
        )


@app.get("/api/v1/lattice/stats", response_model=LatticeStatsResponse)
async def get_lattice_statistics():
    """Get statistics about the lattice"""
    try:
        stats = lattice.get_statistics()
        return LatticeStatsResponse(**stats)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get stats: {str(e)}")


@app.get("/api/v1/feedback/stats")
async def get_feedback_statistics():
    """Get feedback and learning statistics"""
    try:
        stats = feedback_engine.get_feedback_statistics()
        return stats
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to get feedback stats: {str(e)}"
        )


@app.post("/api/v1/maintenance/decay")
async def apply_decay():
    """Apply natural decay to the lattice"""
    try:
        lattice.apply_decay()
        return {"status": "decay_applied", "timestamp": time.time()}
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Decay application failed: {str(e)}"
        )


@app.post("/api/v1/maintenance/cleanup")
async def cleanup_old_feedback(max_age_days: int = 30):
    """Clean up old feedback signals"""
    try:
        cleaned_count = feedback_engine.cleanup_old_feedback(max_age_days)
        return {
            "status": "cleanup_complete",
            "cleaned_count": cleaned_count,
            "max_age_days": max_age_days,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Cleanup failed: {str(e)}")


@app.get("/api/v1/sessions/{session_id}")
async def get_session_info(session_id: str):
    """Get information about a specific session"""
    if session_id not in active_sessions:
        raise HTTPException(status_code=404, detail="Session not found")

    return active_sessions[session_id]


@app.delete("/api/v1/sessions/{session_id}")
async def end_session(session_id: str):
    """End a session and clean up its data"""
    if session_id not in active_sessions:
        raise HTTPException(status_code=404, detail="Session not found")

    del active_sessions[session_id]
    return {"status": "session_ended", "session_id": session_id}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
