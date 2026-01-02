"""
AI Engineer - Production Backend
A complete AI coding assistant with full task automation
"""

import asyncio
import json
import os
import sys
import uuid
import traceback
from datetime import datetime
from typing import Dict, List, Optional, Any, Callable
from enum import Enum
from contextlib import asynccontextmanager

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field, SecretStr
import uvicorn

# Add OpenHands to path
OPENHANDS_PATH = os.path.join(os.path.dirname(__file__), '../../OpenHands')
if os.path.exists(OPENHANDS_PATH):
    sys.path.insert(0, OPENHANDS_PATH)

# ==================== Models ====================

class TaskStatus(str, Enum):
    PENDING = "pending"
    PLANNING = "planning"
    EXECUTING = "executing"
    COMPLETED = "completed"
    FAILED = "failed"
    AWAITING_INPUT = "awaiting_input"

class LLMProvider(str, Enum):
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GOOGLE = "google"
    CUSTOM = "custom"

class RuntimeProvider(str, Enum):
    DOCKER = "docker"
    DAYTONA = "daytona"
    MODAL = "modal"
    E2B = "e2b"

class LLMConfiguration(BaseModel):
    provider: LLMProvider
    model: str
    api_key: str
    base_url: Optional[str] = None
    temperature: float = Field(default=0.0, ge=0.0, le=2.0)
    max_tokens: Optional[int] = Field(default=4096)

class RuntimeConfiguration(BaseModel):
    provider: RuntimeProvider
    api_key: Optional[str] = None
    api_url: Optional[str] = None
    target: Optional[str] = None
    timeout: int = Field(default=300)

class SessionConfig(BaseModel):
    llm_config: LLMConfiguration
    runtime_config: RuntimeConfiguration

class HealthCheckRequest(BaseModel):
    llm_config: LLMConfiguration
    runtime_config: RuntimeConfiguration

class HealthCheckResponse(BaseModel):
    llm_status: str
    llm_message: str
    llm_latency_ms: Optional[float] = None
    runtime_status: str
    runtime_message: str
    overall_healthy: bool
    timestamp: str

class TaskStep(BaseModel):
    id: str
    description: str
    status: TaskStatus
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    output: Optional[str] = None
    error: Optional[str] = None

class AgentTask(BaseModel):
    id: str
    description: str
    status: TaskStatus
    plan: List[TaskStep] = []
    current_step: int = 0
    started_at: str
    completed_at: Optional[str] = None
    final_output: Optional[str] = None
    error: Optional[str] = None

# ==================== Event Types ====================

class WSEventType(str, Enum):
    # Connection events
    CONNECTED = "connected"
    DISCONNECTED = "disconnected"
    ERROR = "error"
    
    # Status events
    STATUS = "status"
    RUNTIME_STARTING = "runtime_starting"
    RUNTIME_READY = "runtime_ready"
    
    # Task events
    TASK_STARTED = "task_started"
    TASK_PLANNING = "task_planning"
    TASK_PLAN_READY = "task_plan_ready"
    TASK_STEP_STARTED = "task_step_started"
    TASK_STEP_COMPLETED = "task_step_completed"
    TASK_COMPLETED = "task_completed"
    TASK_FAILED = "task_failed"
    
    # Agent events
    AGENT_THINKING = "agent_thinking"
    AGENT_ACTION = "agent_action"
    AGENT_OBSERVATION = "agent_observation"
    AGENT_MESSAGE = "agent_message"
    
    # Terminal events
    TERMINAL_OUTPUT = "terminal_output"
    TERMINAL_ERROR = "terminal_error"
    
    # File events
    FILE_CREATED = "file_created"
    FILE_MODIFIED = "file_modified"
    FILE_DELETED = "file_deleted"
    FILES_LIST = "files_list"
    FILE_CONTENT = "file_content"

class WSEvent(BaseModel):
    type: WSEventType
    data: Dict[str, Any] = {}
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())

# ==================== Session Manager ====================

class Session:
    def __init__(self, session_id: str, config: SessionConfig):
        self.id = session_id
        self.config = config
        self.created_at = datetime.now()
        self.runtime = None
        self.controller = None
        self.agent = None
        self.event_stream = None
        self.is_initialized = False
        self.is_running = False
        self.current_task: Optional[AgentTask] = None
        self.task_history: List[AgentTask] = []
        self.websocket: Optional[WebSocket] = None
        self._agent_loop_task: Optional[asyncio.Task] = None
        self._stop_event = asyncio.Event()
    
    async def send_event(self, event: WSEvent):
        """Send event to connected WebSocket"""
        if self.websocket:
            try:
                await self.websocket.send_json(event.model_dump())
            except Exception as e:
                print(f"Failed to send event: {e}")
    
    async def initialize(self):
        """Initialize runtime and agent"""
        try:
            await self.send_event(WSEvent(
                type=WSEventType.RUNTIME_STARTING,
                data={"message": "Starting runtime environment..."}
            ))
            
            # Configure environment
            self._configure_environment()
            
            # Import OpenHands components
            from openhands.core.config import OpenHandsConfig
            from openhands.core.config.llm_config import LLMConfig
            from openhands.core.config.sandbox_config import SandboxConfig
            from openhands.core.setup import create_agent, create_runtime, create_controller
            from openhands.utils.utils import create_registry_and_conversation_stats
            
            # Build OpenHands config
            llm_config = LLMConfig(
                model=self.config.llm_config.model,
                api_key=SecretStr(self.config.llm_config.api_key),
                base_url=self.config.llm_config.base_url,
                temperature=self.config.llm_config.temperature,
                max_output_tokens=self.config.llm_config.max_tokens,
            )
            
            sandbox_config = SandboxConfig(
                timeout=self.config.runtime_config.timeout,
            )
            
            oh_config = OpenHandsConfig(
                runtime=self.config.runtime_config.provider.value,
                llms={"llm": llm_config},
                sandbox=sandbox_config,
                max_iterations=100,
                max_budget_per_task=10.0,
            )
            
            # Create components
            llm_registry, conversation_stats, oh_config = create_registry_and_conversation_stats(
                oh_config, self.id, None
            )
            
            await self.send_event(WSEvent(
                type=WSEventType.STATUS,
                data={"message": "Creating AI agent..."}
            ))
            
            self.agent = create_agent(oh_config, llm_registry)
            
            await self.send_event(WSEvent(
                type=WSEventType.STATUS,
                data={"message": "Starting sandbox environment..."}
            ))
            
            self.runtime = create_runtime(
                oh_config,
                llm_registry,
                sid=self.id,
                headless_mode=True,
                agent=self.agent,
            )
            
            await self.runtime.connect()
            self.event_stream = self.runtime.event_stream
            
            self.controller, _ = create_controller(
                self.agent, self.runtime, oh_config, conversation_stats
            )
            
            self.is_initialized = True
            
            await self.send_event(WSEvent(
                type=WSEventType.RUNTIME_READY,
                data={"message": "AI Engineer is ready!", "session_id": self.id}
            ))
            
        except Exception as e:
            error_msg = f"Failed to initialize: {str(e)}\n{traceback.format_exc()}"
            await self.send_event(WSEvent(
                type=WSEventType.ERROR,
                data={"message": error_msg}
            ))
            raise
    
    def _configure_environment(self):
        """Set environment variables for runtime providers"""
        llm = self.config.llm_config
        runtime = self.config.runtime_config
        
        os.environ["LLM_MODEL"] = llm.model
        os.environ["LLM_API_KEY"] = llm.api_key
        if llm.base_url:
            os.environ["LLM_BASE_URL"] = llm.base_url
        
        if runtime.provider == RuntimeProvider.DAYTONA:
            if runtime.api_key:
                os.environ["DAYTONA_API_KEY"] = runtime.api_key
            if runtime.api_url:
                os.environ["DAYTONA_API_URL"] = runtime.api_url
            if runtime.target:
                os.environ["DAYTONA_TARGET"] = runtime.target
        elif runtime.provider == RuntimeProvider.MODAL:
            if runtime.api_key:
                os.environ["MODAL_TOKEN"] = runtime.api_key
        elif runtime.provider == RuntimeProvider.E2B:
            if runtime.api_key:
                os.environ["E2B_API_KEY"] = runtime.api_key
    
    async def run_task(self, task_description: str):
        """Run an agent task with full automation"""
        if not self.is_initialized:
            await self.initialize()
        
        if self.is_running:
            await self.send_event(WSEvent(
                type=WSEventType.ERROR,
                data={"message": "A task is already running. Please wait."}
            ))
            return
        
        self.is_running = True
        self._stop_event.clear()
        
        # Create task object
        task = AgentTask(
            id=str(uuid.uuid4()),
            description=task_description,
            status=TaskStatus.PLANNING,
            started_at=datetime.now().isoformat()
        )
        self.current_task = task
        
        await self.send_event(WSEvent(
            type=WSEventType.TASK_STARTED,
            data={"task": task.model_dump()}
        ))
        
        try:
            # Import OpenHands event types
            from openhands.events.action import MessageAction
            from openhands.events import EventSource, EventStreamSubscriber
            from openhands.events.observation import (
                CmdOutputObservation, 
                AgentStateChangedObservation,
                FileReadObservation,
                FileWriteObservation,
            )
            from openhands.core.schema import AgentState
            
            # Subscribe to events for streaming
            def event_callback(event):
                asyncio.create_task(self._handle_agent_event(event))
            
            self.event_stream.subscribe(
                EventStreamSubscriber.MAIN, 
                event_callback, 
                self.id
            )
            
            # Add user task
            action = MessageAction(content=task_description)
            self.event_stream.add_event(action, EventSource.USER)
            
            await self.send_event(WSEvent(
                type=WSEventType.TASK_PLANNING,
                data={"message": "AI is analyzing your task..."}
            ))
            
            # Run agent loop
            end_states = [
                AgentState.FINISHED,
                AgentState.REJECTED,
                AgentState.ERROR,
                AgentState.PAUSED,
                AgentState.STOPPED,
            ]
            
            task.status = TaskStatus.EXECUTING
            
            iteration = 0
            max_iterations = 100
            
            while iteration < max_iterations and not self._stop_event.is_set():
                iteration += 1
                
                try:
                    # Step the controller
                    state = await self.controller.step()
                    
                    if state and state.agent_state in end_states:
                        break
                    
                    # Small delay to prevent tight loop
                    await asyncio.sleep(0.1)
                    
                except Exception as step_error:
                    await self.send_event(WSEvent(
                        type=WSEventType.AGENT_OBSERVATION,
                        data={
                            "type": "error",
                            "content": f"Step error: {str(step_error)}"
                        }
                    ))
                    # Continue trying
                    await asyncio.sleep(1)
            
            # Task completed
            task.status = TaskStatus.COMPLETED
            task.completed_at = datetime.now().isoformat()
            
            # Get final state
            final_state = self.controller.get_state()
            if final_state:
                task.final_output = f"Task completed after {iteration} iterations"
            
            await self.send_event(WSEvent(
                type=WSEventType.TASK_COMPLETED,
                data={"task": task.model_dump()}
            ))
            
        except Exception as e:
            task.status = TaskStatus.FAILED
            task.error = str(e)
            task.completed_at = datetime.now().isoformat()
            
            await self.send_event(WSEvent(
                type=WSEventType.TASK_FAILED,
                data={"task": task.model_dump(), "error": str(e)}
            ))
        finally:
            self.is_running = False
            self.task_history.append(task)
            self.current_task = None
    
    async def _handle_agent_event(self, event):
        """Handle events from the OpenHands agent"""
        try:
            from openhands.events.action import (
                CmdRunAction, 
                FileReadAction, 
                FileWriteAction,
                MessageAction,
                AgentFinishAction,
            )
            from openhands.events.observation import (
                CmdOutputObservation,
                FileReadObservation,
                FileWriteObservation,
                AgentStateChangedObservation,
            )
            
            event_type = event.__class__.__name__
            
            # Handle different event types
            if isinstance(event, CmdRunAction):
                await self.send_event(WSEvent(
                    type=WSEventType.AGENT_ACTION,
                    data={
                        "action_type": "command",
                        "command": event.command,
                        "thought": getattr(event, 'thought', None)
                    }
                ))
            
            elif isinstance(event, CmdOutputObservation):
                await self.send_event(WSEvent(
                    type=WSEventType.TERMINAL_OUTPUT,
                    data={
                        "output": event.content,
                        "exit_code": event.exit_code
                    }
                ))
            
            elif isinstance(event, FileWriteAction):
                await self.send_event(WSEvent(
                    type=WSEventType.AGENT_ACTION,
                    data={
                        "action_type": "file_write",
                        "path": event.path,
                        "thought": getattr(event, 'thought', None)
                    }
                ))
            
            elif isinstance(event, FileWriteObservation):
                await self.send_event(WSEvent(
                    type=WSEventType.FILE_MODIFIED,
                    data={"path": event.path}
                ))
            
            elif isinstance(event, FileReadAction):
                await self.send_event(WSEvent(
                    type=WSEventType.AGENT_ACTION,
                    data={
                        "action_type": "file_read",
                        "path": event.path
                    }
                ))
            
            elif isinstance(event, MessageAction):
                if hasattr(event, 'content') and event.content:
                    await self.send_event(WSEvent(
                        type=WSEventType.AGENT_MESSAGE,
                        data={"content": event.content}
                    ))
            
            elif isinstance(event, AgentFinishAction):
                await self.send_event(WSEvent(
                    type=WSEventType.AGENT_MESSAGE,
                    data={
                        "content": getattr(event, 'thought', 'Task completed'),
                        "is_final": True
                    }
                ))
            
            elif isinstance(event, AgentStateChangedObservation):
                await self.send_event(WSEvent(
                    type=WSEventType.STATUS,
                    data={"agent_state": str(event.agent_state)}
                ))
            
            else:
                # Generic event handling
                if hasattr(event, 'thought') and event.thought:
                    await self.send_event(WSEvent(
                        type=WSEventType.AGENT_THINKING,
                        data={"thought": event.thought}
                    ))
                
                if hasattr(event, 'content') and event.content:
                    await self.send_event(WSEvent(
                        type=WSEventType.AGENT_OBSERVATION,
                        data={
                            "type": event_type,
                            "content": str(event.content)[:2000]  # Limit size
                        }
                    ))
        
        except Exception as e:
            print(f"Error handling agent event: {e}")
    
    async def execute_command(self, command: str) -> Dict[str, Any]:
        """Execute a terminal command directly"""
        if not self.is_initialized:
            return {"error": "Session not initialized"}
        
        try:
            from openhands.events.action import CmdRunAction
            
            action = CmdRunAction(command=command)
            obs = await self.runtime.run_action(action)
            
            result = {
                "command": command,
                "output": obs.content if hasattr(obs, 'content') else str(obs),
                "exit_code": getattr(obs, 'exit_code', 0)
            }
            
            await self.send_event(WSEvent(
                type=WSEventType.TERMINAL_OUTPUT,
                data=result
            ))
            
            return result
        
        except Exception as e:
            error_result = {"command": command, "error": str(e), "exit_code": 1}
            await self.send_event(WSEvent(
                type=WSEventType.TERMINAL_ERROR,
                data=error_result
            ))
            return error_result
    
    async def list_files(self, path: str = "/workspace") -> List[Dict[str, Any]]:
        """List files in the workspace"""
        if not self.is_initialized:
            return []
        
        try:
            result = await self.execute_command(f"find {path} -maxdepth 3 -type f -o -type d 2>/dev/null | head -100")
            files = []
            
            if result.get("output"):
                for line in result["output"].strip().split("\n"):
                    if line:
                        files.append({
                            "path": line,
                            "name": os.path.basename(line),
                            "is_dir": not "." in os.path.basename(line)  # Simple heuristic
                        })
            
            await self.send_event(WSEvent(
                type=WSEventType.FILES_LIST,
                data={"files": files, "base_path": path}
            ))
            
            return files
        except Exception as e:
            return []
    
    async def read_file(self, path: str) -> str:
        """Read file content"""
        if not self.is_initialized:
            return ""
        
        try:
            from openhands.events.action import FileReadAction
            
            action = FileReadAction(path=path)
            obs = await self.runtime.run_action(action)
            
            content = obs.content if hasattr(obs, 'content') else ""
            
            await self.send_event(WSEvent(
                type=WSEventType.FILE_CONTENT,
                data={"path": path, "content": content}
            ))
            
            return content
        except Exception as e:
            return f"Error reading file: {e}"
    
    async def stop_task(self):
        """Stop the current running task"""
        self._stop_event.set()
        await self.send_event(WSEvent(
            type=WSEventType.STATUS,
            data={"message": "Stopping task..."}
        ))
    
    async def cleanup(self):
        """Cleanup session resources"""
        self._stop_event.set()
        
        if self._agent_loop_task:
            self._agent_loop_task.cancel()
        
        if self.runtime:
            try:
                self.runtime.close()
            except:
                pass

class SessionManager:
    def __init__(self):
        self.sessions: Dict[str, Session] = {}
    
    def create_session(self, config: SessionConfig) -> Session:
        session_id = str(uuid.uuid4())
        session = Session(session_id, config)
        self.sessions[session_id] = session
        return session
    
    def get_session(self, session_id: str) -> Optional[Session]:
        return self.sessions.get(session_id)
    
    async def delete_session(self, session_id: str):
        if session_id in self.sessions:
            await self.sessions[session_id].cleanup()
            del self.sessions[session_id]

# ==================== Application ====================

session_manager = SessionManager()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("AI Engineer Backend Starting...")
    yield
    # Shutdown
    print("Shutting down...")
    for session_id in list(session_manager.sessions.keys()):
        await session_manager.delete_session(session_id)

app = FastAPI(
    title="AI Engineer",
    description="Open-source Devin alternative - No login required",
    version="2.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==================== Health Check Functions ====================

async def test_llm_connection(config: LLMConfiguration) -> tuple[str, str, Optional[float]]:
    """Test LLM connectivity with latency measurement"""
    import time
    
    try:
        import litellm
        
        start = time.time()
        response = await asyncio.to_thread(
            litellm.completion,
            model=config.model,
            messages=[{"role": "user", "content": "Say OK"}],
            api_key=config.api_key,
            base_url=config.base_url,
            temperature=0,
            max_tokens=5,
            timeout=15,
        )
        latency = (time.time() - start) * 1000
        
        if response and response.choices:
            return "healthy", f"Connected to {config.model}", latency
        return "unhealthy", "Empty response from LLM", None
    
    except Exception as e:
        return "unhealthy", f"LLM error: {str(e)}", None

async def test_runtime_connection(config: RuntimeConfiguration) -> tuple[str, str]:
    """Test runtime provider connectivity"""
    try:
        if config.provider == RuntimeProvider.DOCKER:
            import docker
            client = docker.from_env()
            client.ping()
            return "healthy", "Docker daemon accessible"
        
        elif config.provider == RuntimeProvider.DAYTONA:
            if not config.api_key:
                return "unhealthy", "Daytona API key required"
            
            from daytona import Daytona, DaytonaConfig
            daytona_config = DaytonaConfig(
                api_key=config.api_key,
                server_url=config.api_url or "https://app.daytona.io/api",
                target=config.target or "eu",
            )
            daytona = Daytona(daytona_config)
            await asyncio.to_thread(daytona.list, {})
            return "healthy", "Daytona API accessible"
        
        elif config.provider == RuntimeProvider.MODAL:
            if config.api_key and len(config.api_key) > 10:
                return "healthy", "Modal token configured"
            return "unhealthy", "Invalid Modal token"
        
        elif config.provider == RuntimeProvider.E2B:
            if config.api_key and len(config.api_key) > 10:
                return "healthy", "E2B API key configured"
            return "unhealthy", "Invalid E2B API key"
        
        return "unhealthy", f"Unknown provider: {config.provider}"
    
    except Exception as e:
        return "unhealthy", f"Runtime error: {str(e)}"

# ==================== API Routes ====================

@app.get("/")
async def root():
    return {"app": "AI Engineer", "version": "2.0.0", "status": "running"}

@app.get("/api/providers/llm")
async def get_llm_providers():
    return {
        "providers": [
            {
                "id": "openai",
                "name": "OpenAI",
                "models": ["gpt-4o", "gpt-4o-mini", "gpt-4-turbo", "o1-preview", "o1-mini"],
                "requires_base_url": False,
            },
            {
                "id": "anthropic",
                "name": "Anthropic",
                "models": ["claude-sonnet-4-20250514", "claude-3-5-sonnet-20241022", "claude-3-opus-20240229"],
                "requires_base_url": False,
            },
            {
                "id": "google",
                "name": "Google",
                "models": ["gemini-2.0-flash-exp", "gemini-1.5-pro", "gemini-1.5-flash"],
                "requires_base_url": False,
            },
            {
                "id": "custom",
                "name": "Custom (OpenAI Compatible)",
                "models": [],
                "requires_base_url": True,
                "placeholder_url": "https://api.your-provider.com/v1",
            },
        ]
    }

@app.get("/api/providers/runtime")
async def get_runtime_providers():
    return {
        "providers": [
            {
                "id": "docker",
                "name": "Docker (Local)",
                "description": "Run locally using Docker - Free",
                "requires_api_key": False,
                "requires_api_url": False,
            },
            {
                "id": "daytona",
                "name": "Daytona",
                "description": "Cloud development environments",
                "requires_api_key": True,
                "requires_api_url": True,
                "default_api_url": "https://app.daytona.io/api",
                "signup_url": "https://daytona.io",
            },
            {
                "id": "modal",
                "name": "Modal",
                "description": "Serverless GPU containers",
                "requires_api_key": True,
                "requires_api_url": False,
                "signup_url": "https://modal.com",
            },
            {
                "id": "e2b",
                "name": "E2B",
                "description": "AI-native sandboxes",
                "requires_api_key": True,
                "requires_api_url": False,
                "signup_url": "https://e2b.dev",
            },
        ]
    }

@app.post("/api/health-check", response_model=HealthCheckResponse)
async def health_check(request: HealthCheckRequest):
    """Comprehensive health check for all services"""
    
    # Test LLM
    llm_status, llm_message, llm_latency = await test_llm_connection(request.llm_config)
    
    # Test Runtime
    runtime_status, runtime_message = await test_runtime_connection(request.runtime_config)
    
    return HealthCheckResponse(
        llm_status=llm_status,
        llm_message=llm_message,
        llm_latency_ms=llm_latency,
        runtime_status=runtime_status,
        runtime_message=runtime_message,
        overall_healthy=(llm_status == "healthy" and runtime_status == "healthy"),
        timestamp=datetime.now().isoformat()
    )

@app.post("/api/sessions")
async def create_session(config: SessionConfig):
    """Create a new agent session"""
    session = session_manager.create_session(config)
    return {
        "session_id": session.id,
        "created_at": session.created_at.isoformat(),
        "status": "created"
    }

@app.get("/api/sessions/{session_id}")
async def get_session(session_id: str):
    session = session_manager.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return {
        "session_id": session.id,
        "created_at": session.created_at.isoformat(),
        "is_initialized": session.is_initialized,
        "is_running": session.is_running,
        "current_task": session.current_task.model_dump() if session.current_task else None,
        "task_count": len(session.task_history)
    }

@app.delete("/api/sessions/{session_id}")
async def delete_session(session_id: str):
    session = session_manager.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    await session_manager.delete_session(session_id)
    return {"status": "deleted", "session_id": session_id}

@app.post("/api/sessions/{session_id}/stop")
async def stop_session_task(session_id: str):
    session = session_manager.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    await session.stop_task()
    return {"status": "stopping", "session_id": session_id}

# ==================== WebSocket Handler ====================

@app.websocket("/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    """WebSocket endpoint for real-time bidirectional communication"""
    
    await websocket.accept()
    
    session = session_manager.get_session(session_id)
    if not session:
        await websocket.send_json({
            "type": "error",
            "data": {"message": "Session not found"},
            "timestamp": datetime.now().isoformat()
        })
        await websocket.close()
        return
    
    session.websocket = websocket
    
    try:
        # Send connected event
        await session.send_event(WSEvent(
            type=WSEventType.CONNECTED,
            data={"session_id": session_id, "message": "Connected to AI Engineer"}
        ))
        
        # Initialize if needed
        if not session.is_initialized:
            await session.initialize()
        
        # Handle messages
        while True:
            try:
                data = await websocket.receive_json()
                await handle_websocket_message(session, data)
            except WebSocketDisconnect:
                break
            except json.JSONDecodeError:
                await session.send_event(WSEvent(
                    type=WSEventType.ERROR,
                    data={"message": "Invalid JSON message"}
                ))
    
    except Exception as e:
        await session.send_event(WSEvent(
            type=WSEventType.ERROR,
            data={"message": f"WebSocket error: {str(e)}"}
        ))
    finally:
        session.websocket = None
        await session.send_event(WSEvent(
            type=WSEventType.DISCONNECTED,
            data={"session_id": session_id}
        ))

async def handle_websocket_message(session: Session, data: dict):
    """Handle incoming WebSocket messages"""
    
    msg_type = data.get("type", "")
    payload = data.get("data", {})
    
    if msg_type == "chat":
        # User sent a task/message
        content = payload.get("content", "")
        if content:
            # Run task in background
            asyncio.create_task(session.run_task(content))
    
    elif msg_type == "terminal":
        # Direct terminal command
        command = payload.get("command", "")
        if command:
            await session.execute_command(command)
    
    elif msg_type == "list_files":
        # List files in workspace
        path = payload.get("path", "/workspace")
        await session.list_files(path)
    
    elif msg_type == "read_file":
        # Read file content
        path = payload.get("path", "")
        if path:
            await session.read_file(path)
    
    elif msg_type == "stop":
        # Stop current task
        await session.stop_task()
    
    elif msg_type == "ping":
        await session.send_event(WSEvent(
            type=WSEventType.STATUS,
            data={"pong": True}
        ))

# ==================== Main ====================

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
