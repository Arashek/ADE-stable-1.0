from fastapi import FastAPI, Depends, WebSocket, HTTPException
from typing import Dict, Any
import asyncio
from datetime import datetime

from core.caching.cache_manager import CacheManager, BatchRequestManager
from core.monitoring.telemetry import TelemetryManager
from core.security.rbac import RBACManager, require_permission, AuditLogger
from core.collaboration.realtime_manager import RealtimeManager
from core.quality.code_analyzer import CodeAnalyzer
from core.experimentation.ab_testing import ABTestingManager, Experiment

# Initialize components
app = FastAPI()
telemetry = TelemetryManager("ade-platform")
cache_manager = CacheManager(redis_client)
batch_manager = BatchRequestManager()
realtime_manager = RealtimeManager(telemetry)
code_analyzer = CodeAnalyzer(telemetry)
ab_manager = ABTestingManager(telemetry)

# Example: Set up an A/B test for code analysis features
code_analysis_experiment = Experiment(
    id="code_analysis_v2",
    name="Enhanced Code Analysis",
    description="Testing new code analysis features",
    variants={
        "control": 50,
        "enhanced": 50
    },
    metrics=["analysis_time", "issues_found", "user_satisfaction"],
    start_date=datetime.utcnow()
)
ab_manager.create_experiment(code_analysis_experiment)

@app.websocket("/ws/collaboration/{session_id}")
async def collaboration_websocket(
    websocket: WebSocket,
    session_id: str,
    current_user: str = Depends(get_current_user)
):
    """Real-time collaboration endpoint"""
    await websocket.accept()
    
    try:
        # Join collaboration session
        await realtime_manager.join_session(
            session_id=session_id,
            resource_id=f"project_{session_id}",
            user_id=current_user,
            websocket=websocket
        )
        
        while True:
            data = await websocket.receive_json()
            
            if data["type"] == "cursor_update":
                await realtime_manager.update_cursor(
                    session_id=session_id,
                    user_id=current_user,
                    line=data["line"],
                    column=data["column"]
                )
            elif data["type"] == "edit":
                await realtime_manager.send_edit(
                    session_id=session_id,
                    user_id=current_user,
                    edit=data["edit"]
                )
                
    except Exception as e:
        telemetry.create_span(
            "websocket_error",
            {"error": str(e), "user": current_user}
        )
    finally:
        await realtime_manager.leave_session(session_id, current_user)
        await websocket.close()

@app.post("/api/analyze-code")
@require_permission("code", "read")
@cache_manager.cached(ttl=300)  # Cache for 5 minutes
async def analyze_code(
    file_path: str,
    current_user: str = Depends(get_current_user)
):
    """Analyze code with A/B testing and batching"""
    # Get experiment variant
    variant = ab_manager.get_variant("code_analysis_v2", current_user)
    
    start_time = datetime.utcnow()
    
    # Add request to batch
    result = await batch_manager.add_to_batch(
        "code_analysis",
        {
            "file_path": file_path,
            "user_id": current_user,
            "variant": variant
        }
    )
    
    # Analyze code
    issues = await code_analyzer.analyze_file(file_path)
    metrics = await code_analyzer.calculate_metrics(file_path)
    
    analysis_time = (datetime.utcnow() - start_time).total_seconds()
    
    # Record experiment metrics
    await ab_manager.record_metric(
        "code_analysis_v2",
        current_user,
        "analysis_time",
        analysis_time
    )
    
    await ab_manager.record_metric(
        "code_analysis_v2",
        current_user,
        "issues_found",
        len(issues)
    )
    
    # Log audit event
    await audit_logger.log_action(
        user_id=current_user,
        action="analyze_code",
        resource=file_path,
        status="success",
        details={
            "issues_count": len(issues),
            "metrics": metrics.__dict__
        }
    )
    
    return {
        "issues": [issue.__dict__ for issue in issues],
        "metrics": metrics.__dict__,
        "variant": variant
    }

# GraphQL integration example
@strawberry.type
class Query:
    @strawberry.field
    async def get_code_analysis(
        self,
        info,
        file_path: str
    ) -> Dict[str, Any]:
        # Get current user from context
        current_user = info.context["user_id"]
        
        # Use the REST endpoint through internal routing
        return await analyze_code(file_path, current_user)

# Example usage in client code:
"""
# Connect to collaboration session
ws = await websocket_connect("ws://localhost:8000/ws/collaboration/session1")

# Send cursor update
await ws.send_json({
    "type": "cursor_update",
    "line": 10,
    "column": 5
})

# Analyze code
analysis = await client.post(
    "/api/analyze-code",
    json={"file_path": "main.py"}
)

# GraphQL query
query = '''
    query {
        getCodeAnalysis(filePath: "main.py") {
            issues {
                line
                message
                severity
            }
            metrics {
                complexity
                testCoverage
            }
        }
    }
'''
result = await client.post("/graphql", json={"query": query})
"""
