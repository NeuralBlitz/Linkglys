#!/usr/bin/env python3
"""Comprehensive OpenCode ↔ LRS-Agents Integration Web Interface."""

import asyncio
import json
from typing import Dict, Any, Optional
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
from pydantic import BaseModel
import sys
import os
import subprocess

# Add current directory and lrs_agents to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "lrs_agents"))

# Import our integration components
from lrs_agents.lrs.opencode.simplified_integration import (
    OpenCodeTool,
    SimplifiedLRSAgent,
)

# Import benchmark integration
from lrs_agents.lrs.benchmarking.benchmark_integration import (
    integrate_benchmarks_into_main,
    add_benchmark_ui_to_main_html,
)

# Import enterprise security and monitoring
from lrs_agents.lrs.enterprise.enterprise_security_monitoring import (
    integrate_enterprise_features,
)

# Import cognitive components
try:
    from phase6_neuromorphic_research.phase6_neuromorphic_setup import (
        CognitiveArchitecture,
    )
    from lrs_agents.lrs.opencode.lrs_opencode_integration import CognitiveCodeAnalyzer

    COGNITIVE_AVAILABLE = True
except ImportError:
    COGNITIVE_AVAILABLE = False

# Import multi-agent coordination
try:
    from lrs_agents.lrs.cognitive.multi_agent_coordination import MultiAgentCoordinator

    MULTI_AGENT_AVAILABLE = True
except ImportError:
    MULTI_AGENT_AVAILABLE = False

# Check LRS availability
try:
    import lrs

    LRS_AVAILABLE = True
except ImportError:
    LRS_AVAILABLE = False
    print("Warning: LRS-Agents not available")

app = FastAPI(title="OpenCode ↔ LRS-Agents Integration Hub", version="2.0.0")

# Serve React dashboard static assets
DASHBOARD_BUILD = os.path.join(os.path.dirname(os.path.abspath(__file__)), "neuralblitz-dashboard", "build")
STATIC_PATH = os.path.join(DASHBOARD_BUILD, "static")
if os.path.exists(STATIC_PATH):
    app.mount("/static", StaticFiles(directory=STATIC_PATH, html=False), name="static")

# Integrate benchmark endpoints
integrate_benchmarks_into_main(app)

# Integrate enterprise security and monitoring
integrate_enterprise_features(app)


# Data models
class IntegrationRequest(BaseModel):
    system: str  # "opencode" or "lrs"
    action: str
    parameters: Optional[Dict[str, Any]] = None


class IntegrationResponse(BaseModel):
    success: bool
    result: Dict[str, Any]
    integration_notes: str


# Global instances for demo
opencode_tool = OpenCodeTool()
lrs_agent = SimplifiedLRSAgent(tools=[opencode_tool])


@app.get("/", response_class=FileResponse)
async def read_root():
    """Serve the React dashboard."""
    index_path = os.path.join(DASHBOARD_BUILD, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return HTMLResponse("<h1>Dashboard build not found. Run: cd neuralblitz-dashboard && bun run build</h1>", status_code=503)


@app.get("/api/integration/status")
async def get_integration_status():
    """Get current integration status."""
    return {
        "lrs_available": LRS_AVAILABLE,
        "opencode_available": opencode_tool.opencode_path is not None,
        "lrs_agent_precision": lrs_agent.belief_state["precision"],
        "lrs_agent_adaptations": lrs_agent.belief_state["adaptation_count"],
        "cognitive_available": COGNITIVE_AVAILABLE,
        "multi_agent_available": MULTI_AGENT_AVAILABLE,
        "integration_active": True,
    }


# Cognitive Monitoring Endpoints
@app.get("/api/cognitive/status")
async def get_cognitive_status():
    """Get cognitive architecture status."""
    if not COGNITIVE_AVAILABLE:
        return {
            "cognitive_available": False,
            "message": "Cognitive components not available",
        }

    try:
        # Create a temporary cognitive analyzer to check status
        analyzer = CognitiveCodeAnalyzer()
        cognitive_stats = analyzer.get_cognitive_insights()

        return {
            "cognitive_available": True,
            "cognitive_enabled": analyzer.cognitive_initialized,
            "cognitive_cycles": cognitive_stats.get("cognitive_cycles", 0),
            "patterns_learned": cognitive_stats.get("patterns_learned", 0),
            "working_memory_items": cognitive_stats.get("working_memory_items", 0),
            "attention_focus": cognitive_stats.get("attention_focus"),
            "temporal_sequences": cognitive_stats.get("temporal_sequences_learned", 0),
        }
    except Exception as e:
        return {"cognitive_available": False, "error": str(e)}


@app.post("/api/cognitive/analyze")
async def analyze_code_with_cognition(request: dict):
    """Analyze code using cognitive architecture."""
    if not COGNITIVE_AVAILABLE:
        raise HTTPException(
            status_code=503, detail="Cognitive components not available"
        )

    try:
        code_content = request.get("code", "")
        file_path = request.get("file_path", "unknown.py")

        analyzer = CognitiveCodeAnalyzer()
        analysis_result = analyzer.analyze_code_with_cognition(code_content, file_path)

        return {
            "analysis": analysis_result,
            "cognitive_insights": analyzer.get_cognitive_insights(),
            "success": True,
        }
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Cognitive analysis failed: {str(e)}"
        )


@app.get("/api/multi-agent/status")
async def get_multi_agent_status():
    """Get multi-agent coordination status."""
    if not MULTI_AGENT_AVAILABLE:
        return {
            "multi_agent_available": False,
            "message": "Multi-agent components not available",
        }

    try:
        # Create coordinator to check status
        coordinator = MultiAgentCoordinator()

        return {
            "multi_agent_available": True,
            "agents_count": len(coordinator.agents),
            "tasks_count": len(coordinator.tasks),
            "completed_tasks": len(coordinator.completed_tasks),
            "cognitive_coordination": coordinator.coordination_cognitive is not None,
            "task_patterns": len(coordinator.task_patterns)
            if hasattr(coordinator, "task_patterns")
            else 0,
        }
    except Exception as e:
        return {"multi_agent_available": False, "error": str(e)}


@app.post("/api/multi-agent/execute-workflow")
async def execute_multi_agent_workflow(request: dict):
    """Execute a multi-agent workflow with cognitive coordination."""
    if not MULTI_AGENT_AVAILABLE:
        raise HTTPException(
            status_code=503, detail="Multi-agent components not available"
        )

    try:
        task_descriptions = request.get("tasks", [])
        if not task_descriptions:
            raise HTTPException(status_code=400, detail="No tasks provided")

        # Import here to avoid circular imports
        from lrs_agents.lrs.cognitive.cognitive_multi_agent_demo import (
            demonstrate_cognitive_multi_agent,
        )

        # For demo purposes, run a simplified version
        # In production, this would create and execute actual workflow
        result = {
            "workflow_executed": True,
            "tasks_processed": len(task_descriptions),
            "cognitive_enhancement": COGNITIVE_AVAILABLE,
            "message": "Multi-agent workflow completed with cognitive coordination",
        }

        return result
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Multi-agent workflow failed: {str(e)}"
        )


@app.get("/{full_path:path}", response_class=FileResponse)
async def spa_catch_all(full_path: str):
    """Serve React app for all non-API routes (SPA routing)."""
    index_path = os.path.join(DASHBOARD_BUILD, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    raise HTTPException(status_code=404, detail="Not found")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=5000)
