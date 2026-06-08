"""
AnnabanOS ↔ AnnabanAI Bridge API

FastAPI application providing REST endpoints for:
1. Context processing (AnnabanOS → HaloBridge)
2. LLM pipeline (HaloBridge → AnnabanAI)
3. Governance oversight (Human → System)
4. System state and analytics

Endpoints bridge the gap between:
- AnnabanOS: Context scoring, agent coordination, action planning
- AnnabanAI: LLM generation, empathy engine, covenant framework
"""

import os
import logging
import time
from typing import Dict, List, Any, Optional
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn

from models import (
    ContextInput, ProcessedContext, LLMProcessingRequest, LLMProcessingResponse,
    OversightRequest, OversightDecision, CycleRequest, CycleResponse, SystemState
)
from halo_bridge import HaloBridge

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Global bridge instance
halo_bridge: Optional[HaloBridge] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle context manager for FastAPI app."""
    global halo_bridge
    
    # Startup
    logger.info("[API] Starting AnnabanOS ↔ AnnabanAI Bridge")
    halo_bridge = HaloBridge()
    
    yield
    
    # Shutdown
    logger.info("[API] Shutting down AnnabanOS ↔ AnnabanAI Bridge")


app = FastAPI(
    title="AnnabanOS ↔ AnnabanAI Bridge API",
    description="REST API bridging AnnabanOS context processing with AnnabanAI LLM pipeline",
    version="1.0.0",
    lifespan=lifespan
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================================
# Context Processing Endpoints (AnnabanOS Integration)
# ============================================================================

@app.post(
    "/contexts/process",
    response_model=ProcessedContext,
    tags=["Context Processing"],
    summary="Process raw context through AnnabanOS pipeline"
)
async def process_context(context: ContextInput) -> ProcessedContext:
    """
    Process raw context through AnnabanOS validation, scoring, and ethics pipeline.
    
    This endpoint simulates the AnnabanOS HaloProtocolRuntime.process_context() behavior:
    1. ContextPreprocessor: Strips whitespace
    2. PHIScorer: Evaluates HP, Urgency, Complexity, PHI
    3. EthicalGuidelines: Checks for ethical compliance
    4. PriorityQueue: Evaluates against HP and Priority thresholds
    
    Returns:
    - status: "processed" if context passes all checks
    - status: "rejected" if context fails ethical or HP checks
    - status: "queued_awaiting_priority" if context has insufficient priority
    """
    if not halo_bridge:
        raise HTTPException(status_code=503, detail="HaloBridge not initialized")
    
    try:
        processed = halo_bridge.process_annaban_context(context.raw_context)
        return processed
    except Exception as e:
        logger.error(f"[API] Context processing error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post(
    "/contexts/batch",
    response_model=List[ProcessedContext],
    tags=["Context Processing"],
    summary="Process multiple contexts in batch"
)
async def process_contexts_batch(contexts: List[ContextInput]) -> List[ProcessedContext]:
    """
    Process multiple contexts in batch.
    
    Useful for simulating multiple societal contexts in parallel.
    """
    if not halo_bridge:
        raise HTTPException(status_code=503, detail="HaloBridge not initialized")
    
    results = []
    for context in contexts:
        try:
            processed = halo_bridge.process_annaban_context(context.raw_context)
            results.append(processed)
        except Exception as e:
            logger.error(f"[API] Batch processing error for context: {e}")
    
    return results


@app.get(
    "/contexts/{context_id}",
    response_model=Optional[ProcessedContext],
    tags=["Context Processing"],
    summary="Retrieve processed context by ID"
)
async def get_context(context_id: str) -> Optional[ProcessedContext]:
    """Retrieve a previously processed context."""
    if not halo_bridge:
        raise HTTPException(status_code=503, detail="HaloBridge not initialized")
    
    context = halo_bridge.processed_contexts.get(context_id)
    if not context:
        raise HTTPException(status_code=404, detail=f"Context {context_id} not found")
    
    return context


# ============================================================================
# LLM Pipeline Endpoints (AnnabanAI Integration)
# ============================================================================

@app.post(
    "/llm/process",
    response_model=LLMProcessingResponse,
    tags=["LLM Processing"],
    summary="Process context through AnnabanAI LLM pipeline"
)
async def process_llm(request: LLMProcessingRequest) -> LLMProcessingResponse:
    """
    Process user input and context through AnnabanAI LLM pipeline.
    
    Pipeline steps:
    1. Empathy Engine: Emotional analysis
    2. Covenant Framework: Prompt generation with principles
    3. Reasoning Profile: Select appropriate reasoning mode
    4. Governance Validation: Check high-impact metadata requirements
    5. LLM Generation: Generate response
    6. Empathy Enhancement: Frame response empathetically
    7. Covenant Validation: Ensure alignment
    8. Human Oversight: Request human review if needed
    9. Memory Vault: Store interaction
    10. Provenance: Create audit record
    """
    if not halo_bridge:
        raise HTTPException(status_code=503, detail="HaloBridge not initialized")
    
    try:
        # First, process through AnnabanOS
        context = halo_bridge.process_annaban_context(request.context.get("raw_context", ""))
        
        # Then route through LLM pipeline
        response = await halo_bridge.process_through_llm_pipeline(context, request)
        return response
    except Exception as e:
        logger.error(f"[API] LLM processing error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post(
    "/llm/quick",
    response_model=LLMProcessingResponse,
    tags=["LLM Processing"],
    summary="Quick LLM response (skip AnnabanOS processing)"
)
async def llm_quick(request: LLMProcessingRequest) -> LLMProcessingResponse:
    """
    Quick LLM processing without AnnabanOS context validation.
    
    Useful for direct LLM queries without the full governance pipeline.
    """
    if not halo_bridge:
        raise HTTPException(status_code=503, detail="HaloBridge not initialized")
    
    try:
        # Create minimal context for LLM pipeline
        from models import ContextScores
        minimal_context = ProcessedContext(
            context_id="",
            raw_context=request.user_input,
            processed_context=request.user_input,
            scores=ContextScores(hp=5.0, urgency=5.0, complexity=1.0, phi=2.5),
            status="processed"
        )
        
        response = await halo_bridge.process_through_llm_pipeline(minimal_context, request)
        return response
    except Exception as e:
        logger.error(f"[API] Quick LLM error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# Governance Endpoints (Human Oversight)
# ============================================================================

@app.get(
    "/governance/oversight",
    response_model=List[OversightRequest],
    tags=["Governance"],
    summary="List pending oversight requests"
)
async def list_oversight_requests() -> List[OversightRequest]:
    """Get list of pending human oversight requests."""
    if not halo_bridge:
        raise HTTPException(status_code=503, detail="HaloBridge not initialized")
    
    return list(halo_bridge.active_oversight_requests.values())


@app.get(
    "/governance/oversight/{request_id}",
    response_model=OversightRequest,
    tags=["Governance"],
    summary="Get specific oversight request"
)
async def get_oversight_request(request_id: str) -> OversightRequest:
    """Get details of a specific oversight request."""
    if not halo_bridge:
        raise HTTPException(status_code=503, detail="HaloBridge not initialized")
    
    request = halo_bridge.active_oversight_requests.get(request_id)
    if not request:
        raise HTTPException(status_code=404, detail=f"Oversight request {request_id} not found")
    
    return request


@app.post(
    "/governance/oversight/{request_id}/approve",
    tags=["Governance"],
    summary="Approve oversight request"
)
async def approve_oversight(request_id: str, comments: str = "") -> Dict[str, Any]:
    """
    Approve an oversight request.
    
    This simulates human reviewer approval of a high-impact decision.
    """
    if not halo_bridge:
        raise HTTPException(status_code=503, detail="HaloBridge not initialized")
    
    decision = OversightDecision(
        request_id=request_id,
        decision="approve",
        comments=comments,
        reviewer="Jacob Kinnaird"
    )
    
    success = halo_bridge.submit_oversight_decision(request_id, decision)
    if not success:
        raise HTTPException(status_code=404, detail=f"Oversight request {request_id} not found")
    
    return {
        "status": "approved",
        "request_id": request_id,
        "reviewer": decision.reviewer,
        "timestamp": decision.timestamp
    }


@app.post(
    "/governance/oversight/{request_id}/reject",
    tags=["Governance"],
    summary="Reject oversight request"
)
async def reject_oversight(request_id: str, comments: str = "") -> Dict[str, Any]:
    """Reject an oversight request."""
    if not halo_bridge:
        raise HTTPException(status_code=503, detail="HaloBridge not initialized")
    
    decision = OversightDecision(
        request_id=request_id,
        decision="reject",
        comments=comments,
        reviewer="Jacob Kinnaird"
    )
    
    success = halo_bridge.submit_oversight_decision(request_id, decision)
    if not success:
        raise HTTPException(status_code=404, detail=f"Oversight request {request_id} not found")
    
    return {
        "status": "rejected",
        "request_id": request_id,
        "reviewer": decision.reviewer,
        "timestamp": decision.timestamp
    }


# ============================================================================
# System State & Analytics Endpoints
# ============================================================================

@app.get(
    "/system/state",
    response_model=SystemState,
    tags=["System"],
    summary="Get current system state"
)
async def get_system_state() -> SystemState:
    """Get comprehensive system state including agent count, metrics, and pending tasks."""
    if not halo_bridge:
        raise HTTPException(status_code=503, detail="HaloBridge not initialized")
    
    return halo_bridge.get_system_state()


@app.get(
    "/system/metrics",
    tags=["System"],
    summary="Get analytics metrics"
)
async def get_metrics() -> Dict[str, Any]:
    """Get system analytics and performance metrics."""
    if not halo_bridge:
        raise HTTPException(status_code=503, detail="HaloBridge not initialized")
    
    metrics = halo_bridge.system_metrics
    return {
        "unique_keywords_count": metrics.unique_keywords_count,
        "processed_contexts": metrics.processed_contexts,
        "successful_actions": metrics.successful_actions,
        "rejected_contexts": metrics.rejected_contexts,
        "generalization_score": metrics.generalization_score,
        "queue_size": metrics.queue_size,
        "queue_efficiency": metrics.queue_efficiency
    }


@app.post(
    "/system/cycles",
    response_model=CycleResponse,
    tags=["System"],
    summary="Run system simulation cycles"
)
async def run_cycles(request: CycleRequest) -> CycleResponse:
    """
    Run AnnabanOS simulation cycles.
    
    This simulates the SocietySimulation.simulate_society() behavior,
    processing multiple contexts through the full pipeline.
    """
    if not halo_bridge:
        raise HTTPException(status_code=503, detail="HaloBridge not initialized")
    
    start_time = time.time()
    processed_count = 0
    rejected_count = 0
    llm_responses = []
    
    try:
        # Use provided contexts or defaults
        contexts = request.contexts or [
            "Address human safety crisis in vulnerable communities",
            "Preserve ecological life and biodiversity",
            "Resolve conflict through mediation and dialogue",
            "Optimize energy distribution sustainably",
            "Enhance human well-being and mental health",
            "Promote fair and equitable policies",
            "Support sustainable resource management"
        ]
        
        # Process contexts through cycles
        for cycle in range(request.num_cycles):
            for context_text in contexts:
                # Step 1: AnnabanOS processing
                processed = halo_bridge.process_annaban_context(context_text)
                
                if processed.status == "processed":
                    processed_count += 1
                    
                    # Step 2: LLM pipeline (if enabled)
                    if request.sync_with_llm:
                        llm_request = LLMProcessingRequest(
                            user_input=context_text,
                            context={"raw_context": context_text}
                        )
                        llm_response = await halo_bridge.process_through_llm_pipeline(
                            processed, llm_request
                        )
                        llm_responses.append(llm_response)
                else:
                    rejected_count += 1
        
        execution_time = time.time() - start_time
        
        return CycleResponse(
            success=True,
            cycles_run=request.num_cycles,
            contexts_processed=processed_count,
            contexts_rejected=rejected_count,
            total_agents_active=1,  # Empath_0 (post-pruning)
            llm_responses=llm_responses if request.sync_with_llm else [],
            final_state=halo_bridge.get_system_state(),
            execution_time_seconds=execution_time
        )
    
    except Exception as e:
        logger.error(f"[API] Cycle execution error: {e}")
        return CycleResponse(
            success=False,
            cycles_run=0,
            contexts_processed=0,
            contexts_rejected=0,
            total_agents_active=0,
            final_state=halo_bridge.get_system_state(),
            error=str(e),
            execution_time_seconds=time.time() - start_time
        )


@app.post("/system/reset", tags=["System"], summary="Reset system state")
async def reset_system() -> Dict[str, str]:
    """Reset all system state (for testing/development)."""
    global halo_bridge
    
    if halo_bridge:
        halo_bridge.processed_contexts.clear()
        halo_bridge.active_oversight_requests.clear()
        logger.info("[API] System state reset")
    
    return {"status": "reset_complete"}


# ============================================================================
# Health & Info Endpoints
# ============================================================================

@app.get("/health", tags=["System"], summary="Health check")
async def health() -> Dict[str, str]:
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "AnnabanOS ↔ AnnabanAI Bridge API",
        "version": "1.0.0"
    }


@app.get("/", tags=["System"], summary="API root")
async def root() -> Dict[str, Any]:
    """API root with basic information."""
    return {
        "service": "AnnabanOS ↔ AnnabanAI Bridge API",
        "version": "1.0.0",
        "description": "REST API bridging AnnabanOS context processing with AnnabanAI LLM pipeline",
        "docs_url": "/docs",
        "endpoints": {
            "context_processing": "/docs#/Context%20Processing",
            "llm_processing": "/docs#/LLM%20Processing",
            "governance": "/docs#/Governance",
            "system": "/docs#/System"
        }
    }


# ============================================================================
# Exception Handlers
# ============================================================================

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler."""
    logger.error(f"[API] Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )


if __name__ == "__main__":
    # Development server
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=int(os.getenv("PORT", 4000)),
        reload=os.getenv("ENV", "development") == "development"
    )
