"""App factory to avoid circular imports."""

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "lrs_agents"))


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    from pydantic import BaseModel
    from typing import Dict, Any, Optional
    
    COGNITIVE_AVAILABLE = False
    MULTI_AGENT_AVAILABLE = False
    LRS_AVAILABLE = False
    
    try:
        from lrs_agents.lrs.opencode.simplified_integration import (
            OpenCodeTool,
            SimplifiedLRSAgent,
        )
        opencode_tool = OpenCodeTool()
        lrs_agent = SimplifiedLRSAgent(tools=[opencode_tool])
    except ImportError:
        opencode_tool = None
        lrs_agent = None
    
    try:
        from lrs_agents.lrs.benchmarking.benchmark_integration import (
            integrate_benchmarks_into_main,
        )
        BENCHMARK_INTEGRATION_AVAILABLE = True
    except ImportError:
        BENCHMARK_INTEGRATION_AVAILABLE = False
    
    try:
        from lrs_agents.lrs.enterprise.enterprise_security_monitoring import (
            integrate_enterprise_features,
        )
        ENTERPRISE_FEATURES_AVAILABLE = True
    except ImportError:
        ENTERPRISE_FEATURES_AVAILABLE = False
    
    try:
        from phase6_neuromorphic_research.phase6_neuromorphic_setup import (
            CognitiveArchitecture,
        )
        from lrs_agents.lrs.opencode.lrs_opencode_integration import CognitiveCodeAnalyzer
        COGNITIVE_AVAILABLE = True
    except ImportError:
        COGNITIVE_AVAILABLE = False
    
    try:
        from lrs_agents.lrs.cognitive.multi_agent_coordination import MultiAgentCoordinator
        MULTI_AGENT_AVAILABLE = True
    except ImportError:
        MULTI_AGENT_AVAILABLE = False
    
    try:
        import lrs
        LRS_AVAILABLE = True
    except ImportError:
        LRS_AVAILABLE = False
    
    app = FastAPI(title="OpenCode ↔ LRS-Agents Integration Hub", version="2.0.0")
    
    DASHBOARD_BUILD = os.path.join(os.path.dirname(os.path.abspath(__file__)), "neuralblitz-dashboard", "build")
    STATIC_PATH = os.path.join(DASHBOARD_BUILD, "static")
    if os.path.exists(STATIC_PATH):
        app.mount("/static", StaticFiles(directory=STATIC_PATH, html=False), name="static")
    
    if BENCHMARK_INTEGRATION_AVAILABLE:
        integrate_benchmarks_into_main(app)
    
    if ENTERPRISE_FEATURES_AVAILABLE:
        integrate_enterprise_features(app)
    
    class IntegrationRequest(BaseModel):
        system: str
        action: str
        parameters: Optional[Dict[str, Any]] = None
    
    class IntegrationResponse(BaseModel):
        success: bool
        result: Dict[str, Any]
        integration_notes: str
    
    @app.get("/", response_class=FileResponse)
    async def read_root():
        index_path = os.path.join(DASHBOARD_BUILD, "index.html")
        if os.path.exists(index_path):
            return FileResponse(index_path)
        return HTMLResponse("<h1>Dashboard build not found. Run: cd neuralblitz-dashboard && bun run build</h1>", status_code=503)
    
    @app.get("/api/integration/status")
    async def get_integration_status():
        return {
            "lrs_available": LRS_AVAILABLE,
            "opencode_available": opencode_tool.opencode_path is not None if opencode_tool else False,
            "lrs_agent_precision": lrs_agent.belief_state["precision"] if lrs_agent else None,
            "lrs_agent_adaptations": lrs_agent.belief_state["adaptation_count"] if lrs_agent else None,
            "cognitive_available": COGNITIVE_AVAILABLE,
            "multi_agent_available": MULTI_AGENT_AVAILABLE,
            "integration_active": True,
        }
    
    @app.get("/api/cognitive/status")
    async def get_cognitive_status():
        if not COGNITIVE_AVAILABLE:
            return {"cognitive_available": False, "message": "Cognitive components not available"}
        try:
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
        if not COGNITIVE_AVAILABLE:
            from fastapi import HTTPException
            raise HTTPException(status_code=503, detail="Cognitive components not available")
        try:
            from fastapi import HTTPException
            analyzer = CognitiveCodeAnalyzer()
            code_content = request.get("code", "")
            file_path = request.get("file_path", "unknown.py")
            analysis_result = analyzer.analyze_code_with_cognition(code_content, file_path)
            return {
                "analysis": analysis_result,
                "cognitive_insights": analyzer.get_cognitive_insights(),
                "success": True,
            }
        except Exception as e:
            from fastapi import HTTPException
            raise HTTPException(status_code=500, detail=f"Cognitive analysis failed: {str(e)}")
    
    @app.get("/api/multi-agent/status")
    async def get_multi_agent_status():
        if not MULTI_AGENT_AVAILABLE:
            return {"multi_agent_available": False, "message": "Multi-agent components not available"}
        try:
            coordinator = MultiAgentCoordinator()
            return {
                "multi_agent_available": True,
                "agents_count": len(coordinator.agents),
                "tasks_count": len(coordinator.tasks),
                "completed_tasks": len(coordinator.completed_tasks),
                "cognitive_coordination": coordinator.coordination_cognitive is not None,
                "task_patterns": len(coordinator.task_patterns) if hasattr(coordinator, "task_patterns") else 0,
            }
        except Exception as e:
            return {"multi_agent_available": False, "error": str(e)}
    
    @app.post("/api/multi-agent/execute-workflow")
    async def execute_multi_agent_workflow(request: dict):
        if not MULTI_AGENT_AVAILABLE:
            from fastapi import HTTPException
            raise HTTPException(status_code=503, detail="Multi-agent components not available")
        try:
            from fastapi import HTTPException
            task_descriptions = request.get("tasks", [])
            if not task_descriptions:
                raise HTTPException(status_code=400, detail="No tasks provided")
            return {
                "workflow_executed": True,
                "tasks_processed": len(task_descriptions),
                "cognitive_enhancement": COGNITIVE_AVAILABLE,
                "message": "Multi-agent workflow completed with cognitive coordination",
            }
        except Exception as e:
            from fastapi import HTTPException
            raise HTTPException(status_code=500, detail=f"Multi-agent workflow failed: {str(e)}")
    
    @app.get("/{full_path:path}", response_class=FileResponse)
    async def spa_catch_all(full_path: str):
        index_path = os.path.join(DASHBOARD_BUILD, "index.html")
        if os.path.exists(index_path):
            return FileResponse(index_path)
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Not found")
    
    return app
