"""
Main FastAPI application for the Agentic Development System.
"""
import uuid
from contextlib import asynccontextmanager
from typing import Dict, Set
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from config import settings
from utils.logger import logger
from services.daytona_service import daytona_service
from services.agent_service import agent_service


# ============================================
# Lifespan Context Manager
# ============================================
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifespan (startup and shutdown)."""
    # Startup
    logger.info("🚀 Starting Agentic Development System...")
    logger.info(f"LLM: {settings.LLM_MODEL} @ {settings.LLM_BASE_URL}")
    logger.info(f"Daytona: {settings.DAYTONA_API_URL}")

    try:
        await daytona_service.initialize()
        logger.info("✅ System initialized successfully")
    except Exception as e:
        logger.error(f"❌ Failed to initialize system: {e}")
        raise

    yield

    # Shutdown
    logger.info("🛑 Shutting down...")
    await daytona_service.cleanup()
    logger.info("✅ Shutdown complete")


# ============================================
# FastAPI Application
# ============================================
app = FastAPI(
    title="Agentic Development System API",
    description="Backend API for autonomous AI development environment",
    version="1.0.0",
    lifespan=lifespan
)

# ============================================
# CORS Middleware
# ============================================
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================
# WebSocket Manager
# ============================================
class ConnectionManager:
    """Manage WebSocket connections."""

    def __init__(self):
        self.active_connections: Set[WebSocket] = set()

    async def connect(self, websocket: WebSocket):
        """Accept and store WebSocket connection."""
        await websocket.accept()
        self.active_connections.add(websocket)
        logger.info(f"WebSocket connected. Total connections: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        """Remove WebSocket connection."""
        self.active_connections.discard(websocket)
        logger.info(f"WebSocket disconnected. Total connections: {len(self.active_connections)}")

    async def send_message(self, websocket: WebSocket, message: dict):
        """Send message to specific WebSocket."""
        try:
            await websocket.send_json(message)
        except Exception as e:
            logger.error(f"Failed to send message: {e}")

    async def broadcast(self, message: dict):
        """Broadcast message to all connected WebSockets."""
        for connection in self.active_connections.copy():
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.error(f"Failed to broadcast to connection: {e}")
                self.disconnect(connection)


ws_manager = ConnectionManager()


# ============================================
# Pydantic Models
# ============================================
class TaskRequest(BaseModel):
    """Request model for creating tasks."""
    task: str
    task_id: str = None


class TaskResponse(BaseModel):
    """Response model for task creation."""
    task_id: str
    status: str
    message: str


# ============================================
# API Endpoints
# ============================================
@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "service": "Agentic Development System API",
        "status": "running",
        "version": "1.0.0"
    }


@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    daytona_health = await daytona_service.health_check()

    return {
        "status": "healthy",
        "daytona": daytona_health,
        "llm_model": settings.LLM_MODEL,
        "llm_provider": "Groq (Free)",
    }


@app.get("/api/sandbox/status")
async def sandbox_status():
    """Get Daytona sandbox status."""
    status = await daytona_service.get_sandbox_status()
    return status


@app.get("/api/workspace/files")
async def list_workspace_files(path: str = "/workspace"):
    """List files in workspace."""
    result = await daytona_service.list_files(path)
    return result


@app.post("/api/workspace/read")
async def read_file(file_path: str):
    """Read a file from workspace."""
    result = await daytona_service.read_file(file_path)
    if not result["success"]:
        raise HTTPException(status_code=404, detail=result["error"])
    return result


@app.post("/api/workspace/write")
async def write_file(file_path: str, content: str):
    """Write a file to workspace."""
    result = await daytona_service.write_file(file_path, content)
    if not result["success"]:
        raise HTTPException(status_code=500, detail=result["error"])
    return result


@app.post("/api/tasks", response_model=TaskResponse)
async def create_task(request: TaskRequest):
    """Create a new task for the AI agent."""
    task_id = request.task_id or str(uuid.uuid4())

    logger.info(f"Creating task {task_id}: {request.task}")

    return TaskResponse(
        task_id=task_id,
        status="queued",
        message="Task created successfully"
    )


# ============================================
# WebSocket Endpoint
# ============================================
@app.websocket("/ws/agent")
async def websocket_agent_endpoint(websocket: WebSocket):
    """WebSocket endpoint for agent communication."""
    await ws_manager.connect(websocket)

    try:
        while True:
            # Receive message from client
            data = await websocket.receive_json()

            logger.info(f"Received WebSocket message: {data}")

            # Extract task information
            task_id = data.get("task_id", str(uuid.uuid4()))
            task_description = data.get("task", "")

            if not task_description:
                await ws_manager.send_message(websocket, {
                    "type": "error",
                    "message": "Task description is required"
                })
                continue

            # Send acknowledgment
            await ws_manager.send_message(websocket, {
                "type": "task_received",
                "task_id": task_id,
                "message": f"Task received: {task_description}"
            })

            # Execute task with agent
            async for event in agent_service.execute_task(task_description, task_id):
                await ws_manager.send_message(websocket, event)

    except WebSocketDisconnect:
        ws_manager.disconnect(websocket)
        logger.info("WebSocket disconnected normally")

    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        try:
            await ws_manager.send_message(websocket, {
                "type": "error",
                "message": str(e)
            })
        except:
            pass
        ws_manager.disconnect(websocket)


# ============================================
# Run Application
# ============================================
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=settings.BACKEND_PORT,
        log_level=settings.LOG_LEVEL.lower(),
        reload=settings.DEBUG
    )
