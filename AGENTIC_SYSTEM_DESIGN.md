# Autonomous Agentic Development System
## OpenHands + Daytona Integration for Complete AI-Powered Development

---

## 🎯 SYSTEM OVERVIEW

A complete autonomous development environment where an AI agent has full control over a development workspace, executing tasks without human intervention. The system combines:

- **OpenHands**: Autonomous AI software engineer agent
- **Daytona**: Secure, isolated sandbox runtime
- **VS Code (Web)**: Full-featured IDE in the browser
- **Chat Interface**: Natural language task assignment
- **Any OpenAI-Compatible LLM**: Flexible model integration

### User Experience Flow:
1. Clone repository
2. Add API keys (LLM + Daytona)
3. Run `docker-compose up`
4. Access web interface:
   - **Left Side**: VS Code with complete workspace access
   - **Right Side**: Chat interface for task assignment
5. AI agent autonomously completes tasks

---

## 🏗️ SYSTEM ARCHITECTURE

```
┌─────────────────────────────────────────────────────────────────┐
│                        Web Browser                               │
│  ┌──────────────────────┐  ┌──────────────────────────────────┐│
│  │                      │  │                                  ││
│  │   VS Code (Web)      │  │   Chat Interface                 ││
│  │   - File Explorer    │  │   - Task Input                   ││
│  │   - Code Editor      │  │   - Agent Responses              ││
│  │   - Terminal         │  │   - Progress Tracking            ││
│  │   - Extensions       │  │   - File Changes                 ││
│  │                      │  │                                  ││
│  └──────────┬───────────┘  └──────────┬───────────────────────┘│
└─────────────┼──────────────────────────┼──────────────────────┘
              │                          │
              │ WebSocket/HTTP           │ WebSocket
              │                          │
┌─────────────┼──────────────────────────┼──────────────────────┐
│             │         Backend          │                       │
│  ┌──────────▼───────────┐   ┌─────────▼──────────────┐       │
│  │                      │   │                         │       │
│  │   code-server        │   │   OpenHands Server      │       │
│  │   (VS Code Backend)  │   │   - AgentController     │       │
│  │                      │   │   - Event Stream        │       │
│  └──────────────────────┘   │   - LLM Integration     │       │
│                              │   - Action Dispatcher   │       │
│                              └────────┬────────────────┘       │
│                                       │                        │
│                                       │ Runtime API            │
│                              ┌────────▼────────────────┐       │
│                              │                         │       │
│                              │   Daytona Runtime       │       │
│                              │   - Sandbox Manager     │       │
│                              │   - File Operations     │       │
│                              │   - Git Operations      │       │
│                              │   - Process Execution   │       │
│                              └────────┬────────────────┘       │
└───────────────────────────────────────┼──────────────────────┘
                                        │
                                        │ Daytona API
                                        │
                              ┌─────────▼──────────────┐
                              │                        │
                              │   Daytona Cloud        │
                              │   (Remote Sandbox)     │
                              │   - Isolated Env       │
                              │   - Code Execution     │
                              │   - State Management   │
                              │                        │
                              └────────────────────────┘
```

---

## 🔧 CORE COMPONENTS

### 1. **OpenHands Agent**
- **Purpose**: Autonomous AI developer that can perform any development task
- **Capabilities**:
  - Code generation and modification
  - File system operations (read, write, delete, move)
  - Terminal command execution
  - Web browsing for documentation
  - Git operations (commit, push, pull, branch)
  - Debugging and testing
  - Package management

### 2. **Daytona Runtime**
- **Purpose**: Secure, isolated execution environment
- **Features**:
  - Sub-90ms sandbox creation
  - Stateful environments (persistent across sessions)
  - Complete isolation from host system
  - File, Git, LSP, and Execute APIs
  - Preview URLs for web applications

### 3. **Code-Server (VS Code Web)**
- **Purpose**: Full VS Code experience in browser
- **Features**:
  - Complete VS Code interface
  - Extension support
  - Integrated terminal
  - Git integration
  - File explorer
  - Multi-file editing

### 4. **Web UI (Chat Interface)**
- **Purpose**: Natural language task assignment and monitoring
- **Features**:
  - Real-time chat with AI agent
  - Task progress visualization
  - File change notifications
  - Agent action logs
  - WebSocket-based real-time updates

### 5. **Reverse Proxy (Nginx)**
- **Purpose**: Unified access point for all services
- **Routes**:
  - `/` → Web UI landing page
  - `/vscode` → Code-Server
  - `/openhands` → OpenHands WebSocket/API
  - `/api` → Backend API

---

## 🛠️ TECHNOLOGY STACK

### Backend
- **OpenHands**: Python-based AI agent framework (MIT License)
- **Daytona SDK**: Python SDK for sandbox management
- **FastAPI**: Additional backend API services
- **WebSocket**: Real-time communication
- **Docker**: Containerization
- **Docker Compose**: Multi-container orchestration

### Frontend
- **React**: UI framework for chat interface
- **TypeScript**: Type-safe development
- **Tailwind CSS**: Styling
- **Socket.io**: WebSocket client
- **Code-Server**: VS Code in browser
- **Monaco Editor**: Embedded code viewing (optional)

### Infrastructure
- **Nginx**: Reverse proxy
- **Redis**: Session management and caching (optional)
- **PostgreSQL**: Persistence for chat history (optional)

---

## 📁 PROJECT STRUCTURE

```
agentic-dev-system/
├── docker-compose.yml
├── .env.example
├── README.md
├── SETUP.md
├── LICENSE
│
├── backend/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── main.py
│   ├── config.py
│   ├── openhands_config.toml
│   ├── services/
│   │   ├── __init__.py
│   │   ├── openhands_service.py
│   │   ├── daytona_service.py
│   │   └── websocket_service.py
│   └── utils/
│       ├── __init__.py
│       ├── logger.py
│       └── validators.py
│
├── frontend/
│   ├── Dockerfile
│   ├── package.json
│   ├── tsconfig.json
│   ├── vite.config.ts
│   ├── public/
│   ├── src/
│   │   ├── App.tsx
│   │   ├── main.tsx
│   │   ├── components/
│   │   │   ├── Layout.tsx
│   │   │   ├── VSCodePanel.tsx
│   │   │   ├── ChatPanel.tsx
│   │   │   ├── ChatMessage.tsx
│   │   │   ├── TaskInput.tsx
│   │   │   ├── AgentStatus.tsx
│   │   │   └── FileChangeNotification.tsx
│   │   ├── services/
│   │   │   ├── websocket.ts
│   │   │   └── api.ts
│   │   ├── hooks/
│   │   │   ├── useWebSocket.ts
│   │   │   └── useAgentStatus.ts
│   │   ├── types/
│   │   │   └── index.ts
│   │   └── styles/
│   │       └── globals.css
│   └── index.html
│
├── nginx/
│   ├── Dockerfile
│   └── nginx.conf
│
├── scripts/
│   ├── setup.sh
│   ├── start.sh
│   └── stop.sh
│
└── docs/
    ├── ARCHITECTURE.md
    ├── API_REFERENCE.md
    ├── TROUBLESHOOTING.md
    └── EXAMPLES.md
```

---

## 🔐 CONFIGURATION SYSTEM

### Environment Variables (.env file)

```bash
# ============================================
# LLM Configuration (OpenAI-Compatible)
# ============================================
LLM_API_KEY=your-llm-api-key-here
LLM_BASE_URL=https://api.openai.com/v1
LLM_MODEL=gpt-4
LLM_TEMPERATURE=0.7
LLM_MAX_TOKENS=4096

# ============================================
# Daytona Configuration
# ============================================
DAYTONA_API_KEY=your-daytona-api-key-here
DAYTONA_API_URL=https://api.daytona.io
DAYTONA_TARGET=default

# ============================================
# OpenHands Configuration
# ============================================
SANDBOX_RUNTIME_CONTAINER_IMAGE=ghcr.io/all-hands-ai/runtime:0.38-nikolaik
WORKSPACE_BASE=/workspace
WORKSPACE_MOUNT_PATH=./workspace
WORKSPACE_MOUNT_PATH_IN_SANDBOX=/workspace

# ============================================
# Code-Server Configuration
# ============================================
CODE_SERVER_PASSWORD=changeme
CODE_SERVER_PORT=8080

# ============================================
# Application Configuration
# ============================================
APP_PORT=3000
BACKEND_PORT=3001
NGINX_PORT=80

# ============================================
# Optional: Logging and Debugging
# ============================================
LOG_LEVEL=INFO
DEBUG=false
LOG_ALL_EVENTS=false

# ============================================
# Optional: Security
# ============================================
ALLOWED_ORIGINS=http://localhost,http://localhost:80
JWT_SECRET=your-jwt-secret-here
SESSION_TIMEOUT=3600
```

---

## 🚀 IMPLEMENTATION PLAN

### Phase 1: Backend Setup (Week 1)

**Task 1.1: OpenHands Integration**
- [ ] Install OpenHands dependencies
- [ ] Configure OpenHands with Daytona runtime
- [ ] Set up LLM connection (OpenAI-compatible)
- [ ] Implement event stream handling
- [ ] Create AgentController wrapper

**Task 1.2: Daytona SDK Integration**
- [ ] Install Daytona Python SDK
- [ ] Implement sandbox creation/management
- [ ] Set up file operation handlers
- [ ] Implement Git operation handlers
- [ ] Configure process execution

**Task 1.3: Backend API Development**
- [ ] Create FastAPI application structure
- [ ] Implement WebSocket endpoint for chat
- [ ] Create REST API endpoints:
  - `POST /api/tasks` - Create new task
  - `GET /api/tasks/{id}` - Get task status
  - `GET /api/sandbox/status` - Sandbox status
  - `GET /api/files` - List workspace files
  - `GET /api/agent/status` - Agent status
- [ ] Implement authentication/authorization
- [ ] Set up error handling and logging

### Phase 2: Frontend Development (Week 2)

**Task 2.1: Project Setup**
- [ ] Initialize React + TypeScript + Vite project
- [ ] Install dependencies (Tailwind, Socket.io, etc.)
- [ ] Set up routing and state management
- [ ] Configure build system

**Task 2.2: Layout Components**
- [ ] Create main layout with split panels
- [ ] Implement responsive design
- [ ] Create header with status indicators
- [ ] Add theme toggle (light/dark mode)

**Task 2.3: VS Code Panel**
- [ ] Embed code-server iframe
- [ ] Implement iframe communication
- [ ] Add loading states
- [ ] Handle authentication

**Task 2.4: Chat Interface**
- [ ] Create chat message components
- [ ] Implement task input form
- [ ] Add message history display
- [ ] Create agent status indicator
- [ ] Add file change notifications
- [ ] Implement auto-scroll
- [ ] Add typing indicators

**Task 2.5: WebSocket Integration**
- [ ] Create WebSocket service
- [ ] Implement event handlers
- [ ] Add reconnection logic
- [ ] Handle connection states

### Phase 3: Infrastructure Setup (Week 3)

**Task 3.1: Docker Configuration**
- [ ] Create Dockerfile for backend
- [ ] Create Dockerfile for frontend
- [ ] Create Dockerfile for nginx
- [ ] Set up code-server container
- [ ] Configure Docker networking

**Task 3.2: Docker Compose**
- [ ] Define all services
- [ ] Configure volumes
- [ ] Set up environment variables
- [ ] Configure service dependencies
- [ ] Add health checks

**Task 3.3: Nginx Configuration**
- [ ] Configure reverse proxy rules
- [ ] Set up SSL/TLS (optional)
- [ ] Configure WebSocket proxying
- [ ] Add security headers
- [ ] Configure CORS

### Phase 4: Integration & Testing (Week 4)

**Task 4.1: End-to-End Integration**
- [ ] Connect all components
- [ ] Test complete workflow
- [ ] Verify agent actions
- [ ] Test error scenarios
- [ ] Validate file operations

**Task 4.2: Testing**
- [ ] Unit tests for backend services
- [ ] Integration tests for API
- [ ] Frontend component tests
- [ ] E2E tests with Playwright
- [ ] Load testing

**Task 4.3: Documentation**
- [ ] Write setup guide
- [ ] Create API documentation
- [ ] Add architecture diagrams
- [ ] Write troubleshooting guide
- [ ] Create example tasks

### Phase 5: Polish & Deployment (Week 5)

**Task 5.1: UI/UX Improvements**
- [ ] Add loading animations
- [ ] Improve error messages
- [ ] Add tooltips and help text
- [ ] Implement keyboard shortcuts
- [ ] Add accessibility features

**Task 5.2: Performance Optimization**
- [ ] Optimize bundle size
- [ ] Implement code splitting
- [ ] Add caching strategies
- [ ] Optimize WebSocket messages
- [ ] Profile and optimize backend

**Task 5.3: Security Hardening**
- [ ] Implement rate limiting
- [ ] Add input validation
- [ ] Secure API endpoints
- [ ] Audit dependencies
- [ ] Add security headers

**Task 5.4: Deployment**
- [ ] Create deployment scripts
- [ ] Set up CI/CD pipeline
- [ ] Configure production environment
- [ ] Add monitoring and logging
- [ ] Create backup strategies

---

## 💡 DETAILED IMPLEMENTATION GUIDE

### 1. OpenHands Configuration

**openhands_config.toml**:
```toml
[core]
workspace_base = "/workspace"
cache_dir = "/tmp/cache"
run_as_openhands = false
file_uploads_enabled = true
file_uploads_max_file_size_mb = 100

[llm]
model = "openai/gpt-4"
api_key = "${LLM_API_KEY}"
base_url = "${LLM_BASE_URL}"
temperature = 0.7
max_tokens = 4096
timeout = 60

[agent]
name = "CodeActAgent"
max_iterations = 100
micro_agent_dir = "/workspace/.openhands/microagents"

[sandbox]
runtime_type = "daytona"
daytona_api_key = "${DAYTONA_API_KEY}"
daytona_api_url = "${DAYTONA_API_URL}"
daytona_target = "${DAYTONA_TARGET}"
container_image = "${SANDBOX_RUNTIME_CONTAINER_IMAGE}"
use_host_network = false
timeout = 300

[server]
port = 3000
file_store_path = "/tmp/file_store"
file_store_perm = "0777"
session_file_store_path = "/tmp/session_file_store"
```

### 2. Backend Implementation

**main.py**:
```python
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import asyncio
import logging

from services.openhands_service import OpenHandsService
from services.daytona_service import DaytonaService
from services.websocket_service import WebSocketManager
from config import settings

# Configure logging
logging.basicConfig(level=settings.LOG_LEVEL)
logger = logging.getLogger(__name__)

# Initialize services
daytona_service = DaytonaService()
openhands_service = OpenHandsService(daytona_service)
ws_manager = WebSocketManager()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting Agentic Development System...")
    await daytona_service.initialize()
    await openhands_service.initialize()
    yield
    # Shutdown
    logger.info("Shutting down...")
    await openhands_service.cleanup()
    await daytona_service.cleanup()

app = FastAPI(
    title="Agentic Development System",
    description="AI-powered autonomous development environment",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.websocket("/ws/agent")
async def websocket_endpoint(websocket: WebSocket):
    await ws_manager.connect(websocket)
    try:
        while True:
            # Receive task from frontend
            data = await websocket.receive_json()

            # Process task with OpenHands agent
            task_id = data.get("task_id")
            task_description = data.get("task")

            # Stream agent responses back to frontend
            async for event in openhands_service.execute_task(
                task_description,
                task_id
            ):
                await ws_manager.send_message(websocket, event)

    except WebSocketDisconnect:
        ws_manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        await ws_manager.send_error(websocket, str(e))
        ws_manager.disconnect(websocket)

@app.get("/api/health")
async def health_check():
    return {
        "status": "healthy",
        "daytona": await daytona_service.health_check(),
        "openhands": await openhands_service.health_check()
    }

@app.get("/api/sandbox/status")
async def sandbox_status():
    return await daytona_service.get_sandbox_status()

@app.get("/api/workspace/files")
async def list_workspace_files():
    return await daytona_service.list_files()

@app.post("/api/tasks")
async def create_task(task: dict):
    task_id = await openhands_service.create_task(task)
    return {"task_id": task_id, "status": "queued"}

@app.get("/api/tasks/{task_id}")
async def get_task_status(task_id: str):
    return await openhands_service.get_task_status(task_id)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=settings.BACKEND_PORT,
        log_level=settings.LOG_LEVEL.lower()
    )
```

**services/openhands_service.py**:
```python
import asyncio
from typing import AsyncGenerator
from openhands.controller.agent_controller import AgentController
from openhands.core.config import AppConfig
from openhands.events.action import MessageAction, AgentFinishAction
from openhands.events.observation import AgentStateChangedObservation
import logging

logger = logging.getLogger(__name__)

class OpenHandsService:
    def __init__(self, daytona_service):
        self.daytona_service = daytona_service
        self.config = None
        self.controller = None
        self.tasks = {}

    async def initialize(self):
        """Initialize OpenHands with configuration"""
        try:
            # Load configuration from environment/file
            self.config = AppConfig(
                workspace_base="/workspace",
                sandbox_type="daytona"
            )

            logger.info("OpenHands service initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize OpenHands: {e}")
            raise

    async def execute_task(
        self,
        task_description: str,
        task_id: str
    ) -> AsyncGenerator[dict, None]:
        """
        Execute a task with OpenHands agent
        Yields events as they occur
        """
        try:
            # Create controller for this task
            controller = AgentController(
                agent=self.config.agent,
                max_iterations=self.config.max_iterations,
                max_budget_per_task=self.config.max_budget_per_task,
                agent_to_llm_config=self.config.agent_to_llm_config,
                agent_configs=self.config.agent_configs,
            )

            # Store task
            self.tasks[task_id] = {
                "status": "running",
                "controller": controller
            }

            # Send initial status
            yield {
                "type": "task_started",
                "task_id": task_id,
                "message": f"Starting task: {task_description}"
            }

            # Create initial message action
            action = MessageAction(content=task_description)

            # Subscribe to event stream
            async for event in controller.event_stream:
                # Process different event types
                if isinstance(event, MessageAction):
                    yield {
                        "type": "agent_message",
                        "task_id": task_id,
                        "message": event.content
                    }

                elif isinstance(event, AgentStateChangedObservation):
                    yield {
                        "type": "agent_state_changed",
                        "task_id": task_id,
                        "state": event.agent_state
                    }

                elif isinstance(event, AgentFinishAction):
                    self.tasks[task_id]["status"] = "completed"
                    yield {
                        "type": "task_completed",
                        "task_id": task_id,
                        "outputs": event.outputs
                    }
                    break

                else:
                    # Forward all other events
                    yield {
                        "type": "agent_event",
                        "task_id": task_id,
                        "event": event.to_dict()
                    }

        except Exception as e:
            logger.error(f"Task execution error: {e}")
            self.tasks[task_id]["status"] = "failed"
            yield {
                "type": "task_failed",
                "task_id": task_id,
                "error": str(e)
            }

    async def create_task(self, task: dict) -> str:
        """Create a new task and return task ID"""
        import uuid
        task_id = str(uuid.uuid4())
        self.tasks[task_id] = {
            "status": "queued",
            "task": task
        }
        return task_id

    async def get_task_status(self, task_id: str) -> dict:
        """Get status of a task"""
        return self.tasks.get(task_id, {"status": "not_found"})

    async def health_check(self) -> dict:
        """Check if OpenHands is healthy"""
        return {
            "status": "healthy",
            "active_tasks": len([t for t in self.tasks.values() if t["status"] == "running"])
        }

    async def cleanup(self):
        """Cleanup resources"""
        logger.info("Cleaning up OpenHands service...")
        # Cancel all running tasks
        for task_id, task in self.tasks.items():
            if task["status"] == "running":
                logger.info(f"Canceling task {task_id}")
```

**services/daytona_service.py**:
```python
from daytona import Daytona
from daytona.models.sandbox import Sandbox
import logging
import os

logger = logging.getLogger(__name__)

class DaytonaService:
    def __init__(self):
        self.client = None
        self.sandbox = None

    async def initialize(self):
        """Initialize Daytona client and create sandbox"""
        try:
            # Initialize Daytona client
            self.client = Daytona(
                api_key=os.getenv("DAYTONA_API_KEY"),
                api_url=os.getenv("DAYTONA_API_URL"),
                target=os.getenv("DAYTONA_TARGET", "default")
            )

            # Create sandbox
            logger.info("Creating Daytona sandbox...")
            self.sandbox = self.client.create()
            logger.info(f"Sandbox created: {self.sandbox.id}")

        except Exception as e:
            logger.error(f"Failed to initialize Daytona: {e}")
            raise

    async def get_sandbox_status(self) -> dict:
        """Get current sandbox status"""
        if not self.sandbox:
            return {"status": "not_created"}

        # Refresh sandbox info
        self.sandbox.refresh()

        return {
            "id": self.sandbox.id,
            "status": self.sandbox.state,
            "created_at": self.sandbox.created_at,
        }

    async def list_files(self, path: str = "/workspace") -> list:
        """List files in workspace"""
        if not self.sandbox:
            return []

        try:
            files = self.sandbox.fs.list(path)
            return files
        except Exception as e:
            logger.error(f"Failed to list files: {e}")
            return []

    async def health_check(self) -> dict:
        """Check if Daytona sandbox is healthy"""
        if not self.sandbox:
            return {"status": "not_initialized"}

        try:
            self.sandbox.refresh()
            return {"status": "healthy", "sandbox_id": self.sandbox.id}
        except Exception as e:
            return {"status": "unhealthy", "error": str(e)}

    async def cleanup(self):
        """Cleanup Daytona resources"""
        if self.sandbox:
            logger.info(f"Deleting sandbox {self.sandbox.id}...")
            try:
                self.client.delete(self.sandbox)
                logger.info("Sandbox deleted successfully")
            except Exception as e:
                logger.error(f"Failed to delete sandbox: {e}")
```

### 3. Frontend Implementation

**src/App.tsx**:
```tsx
import React, { useState, useEffect } from 'react';
import Layout from './components/Layout';
import VSCodePanel from './components/VSCodePanel';
import ChatPanel from './components/ChatPanel';
import { useWebSocket } from './hooks/useWebSocket';
import { Message, AgentStatus } from './types';

function App() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [agentStatus, setAgentStatus] = useState<AgentStatus>('idle');
  const { sendMessage, connected } = useWebSocket({
    onMessage: (event) => {
      // Handle incoming WebSocket messages
      const newMessage: Message = {
        id: Date.now().toString(),
        type: event.type,
        content: event.message || JSON.stringify(event),
        timestamp: new Date(),
        sender: 'agent'
      };
      setMessages(prev => [...prev, newMessage]);

      // Update agent status
      if (event.type === 'task_started') {
        setAgentStatus('working');
      } else if (event.type === 'task_completed') {
        setAgentStatus('idle');
      } else if (event.type === 'task_failed') {
        setAgentStatus('error');
      }
    },
    onError: (error) => {
      console.error('WebSocket error:', error);
      setAgentStatus('error');
    }
  });

  const handleSendTask = (task: string) => {
    // Add user message to chat
    const userMessage: Message = {
      id: Date.now().toString(),
      type: 'user_message',
      content: task,
      timestamp: new Date(),
      sender: 'user'
    };
    setMessages(prev => [...prev, userMessage]);

    // Send task to agent
    sendMessage({
      task_id: Date.now().toString(),
      task: task
    });
  };

  return (
    <Layout connected={connected} agentStatus={agentStatus}>
      <div className="flex h-full">
        <VSCodePanel />
        <ChatPanel
          messages={messages}
          onSendTask={handleSendTask}
          agentStatus={agentStatus}
        />
      </div>
    </Layout>
  );
}

export default App;
```

**src/components/ChatPanel.tsx**:
```tsx
import React, { useState, useRef, useEffect } from 'react';
import ChatMessage from './ChatMessage';
import TaskInput from './TaskInput';
import AgentStatus from './AgentStatus';
import { Message, AgentStatus as AgentStatusType } from '../types';

interface ChatPanelProps {
  messages: Message[];
  onSendTask: (task: string) => void;
  agentStatus: AgentStatusType;
}

const ChatPanel: React.FC<ChatPanelProps> = ({
  messages,
  onSendTask,
  agentStatus
}) => {
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  return (
    <div className="flex flex-col h-full w-2/5 border-l border-gray-300 dark:border-gray-700">
      {/* Header */}
      <div className="bg-gray-100 dark:bg-gray-800 p-4 border-b border-gray-300 dark:border-gray-700">
        <h2 className="text-xl font-bold">AI Agent Chat</h2>
        <AgentStatus status={agentStatus} />
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.length === 0 ? (
          <div className="text-center text-gray-500 mt-8">
            <p className="text-lg mb-2">👋 Welcome!</p>
            <p>Describe any development task you want me to complete.</p>
            <p className="text-sm mt-4">Examples:</p>
            <ul className="text-sm text-left max-w-md mx-auto mt-2 space-y-1">
              <li>• Create a REST API with FastAPI</li>
              <li>• Add unit tests for the authentication module</li>
              <li>• Refactor the database connection code</li>
              <li>• Fix the bug in user registration</li>
            </ul>
          </div>
        ) : (
          messages.map(message => (
            <ChatMessage key={message.id} message={message} />
          ))
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <TaskInput
        onSend={onSendTask}
        disabled={agentStatus === 'working'}
      />
    </div>
  );
};

export default ChatPanel;
```

### 4. Docker Compose Configuration

**docker-compose.yml**:
```yaml
version: '3.8'

services:
  # Backend service (OpenHands + Daytona integration)
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    container_name: agentic-backend
    ports:
      - "${BACKEND_PORT:-3001}:3001"
    environment:
      - LLM_API_KEY=${LLM_API_KEY}
      - LLM_BASE_URL=${LLM_BASE_URL}
      - LLM_MODEL=${LLM_MODEL}
      - DAYTONA_API_KEY=${DAYTONA_API_KEY}
      - DAYTONA_API_URL=${DAYTONA_API_URL}
      - DAYTONA_TARGET=${DAYTONA_TARGET}
      - LOG_LEVEL=${LOG_LEVEL:-INFO}
    volumes:
      - ./workspace:/workspace
      - ./backend:/app
    networks:
      - agentic-network
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:3001/api/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  # Frontend service (React UI)
  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    container_name: agentic-frontend
    ports:
      - "${APP_PORT:-3000}:3000"
    environment:
      - VITE_BACKEND_URL=http://backend:3001
      - VITE_WS_URL=ws://backend:3001/ws
    volumes:
      - ./frontend:/app
      - /app/node_modules
    networks:
      - agentic-network
    restart: unless-stopped
    depends_on:
      - backend

  # Code-Server (VS Code in browser)
  code-server:
    image: codercom/code-server:latest
    container_name: agentic-vscode
    ports:
      - "${CODE_SERVER_PORT:-8080}:8080"
    environment:
      - PASSWORD=${CODE_SERVER_PASSWORD}
    volumes:
      - ./workspace:/home/coder/workspace
      - ./code-server-config:/home/coder/.config
    networks:
      - agentic-network
    restart: unless-stopped
    command: --auth password --bind-addr 0.0.0.0:8080 /home/coder/workspace

  # Nginx reverse proxy
  nginx:
    build:
      context: ./nginx
      dockerfile: Dockerfile
    container_name: agentic-nginx
    ports:
      - "${NGINX_PORT:-80}:80"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
    networks:
      - agentic-network
    depends_on:
      - backend
      - frontend
      - code-server
    restart: unless-stopped

networks:
  agentic-network:
    driver: bridge

volumes:
  workspace:
```

---

## 🎮 USER WORKFLOW EXAMPLES

### Example 1: Create a REST API

**User Input**:
```
Create a FastAPI REST API for a todo list application with:
- CRUD operations for todos
- SQLite database
- Pydantic models
- API documentation
- Unit tests
```

**Agent Actions**:
1. Creates project structure
2. Installs dependencies (fastapi, sqlalchemy, pytest)
3. Creates database models
4. Implements API endpoints
5. Writes unit tests
6. Generates API documentation
7. Runs tests to verify everything works

**User Experience**:
- Watches code being written in VS Code (left panel)
- Sees agent progress in chat (right panel)
- Reviews completed code
- Can ask for modifications

### Example 2: Debug an Error

**User Input**:
```
There's a bug in the user authentication. Users can't log in.
Find and fix the issue.
```

**Agent Actions**:
1. Reads authentication code
2. Checks logs for errors
3. Identifies the bug (e.g., password comparison issue)
4. Fixes the code
5. Runs tests to verify fix
6. Reports back with explanation

### Example 3: Refactor Code

**User Input**:
```
Refactor the database connection code to use connection pooling
and add proper error handling.
```

**Agent Actions**:
1. Analyzes current database code
2. Implements connection pooling
3. Adds error handling and retries
4. Updates all code that uses database
5. Adds logging
6. Runs tests to ensure nothing broke

---

## 🔒 SECURITY CONSIDERATIONS

### 1. **Sandbox Isolation**
- All code execution happens in Daytona sandboxes
- Complete isolation from host system
- No access to host files or processes

### 2. **API Key Security**
- API keys stored in environment variables
- Never committed to git
- Can use secrets management (AWS Secrets Manager, etc.)

### 3. **Network Security**
- Nginx reverse proxy with rate limiting
- CORS configuration
- Optional SSL/TLS

### 4. **Access Control**
- Password protection for code-server
- Optional JWT authentication for API
- Session management

### 5. **Input Validation**
- Validate all user inputs
- Sanitize file paths
- Prevent command injection

---

## 📊 MONITORING & LOGGING

### Application Logs
- Backend: All API requests, agent actions, errors
- Frontend: User interactions, WebSocket events
- OpenHands: Task execution, command outputs
- Daytona: Sandbox operations

### Metrics to Track
- Task completion rate
- Average task duration
- Error rates
- Sandbox creation time
- API response times
- WebSocket connection stability

### Tools
- **Prometheus**: Metrics collection
- **Grafana**: Visualization
- **ELK Stack**: Log aggregation
- **Sentry**: Error tracking

---

## 🚨 TROUBLESHOOTING

### Common Issues

**1. Sandbox Creation Fails**
- Check Daytona API key
- Verify network connectivity
- Check Daytona account limits

**2. Agent Not Responding**
- Check LLM API key and quota
- Verify base URL is correct
- Check network connectivity
- Review backend logs

**3. Code-Server Won't Load**
- Verify password is set
- Check port mapping
- Review nginx configuration

**4. WebSocket Connection Drops**
- Check firewall rules
- Verify nginx WebSocket proxy
- Check timeout settings

---

## 🎯 NEXT STEPS & ENHANCEMENTS

### Phase 6: Advanced Features

1. **Multi-Agent Support**
   - Run multiple specialized agents
   - Agent coordination and delegation

2. **Git Integration**
   - Automatic commit messages
   - Branch management
   - Pull request creation

3. **CI/CD Integration**
   - Automatic testing on changes
   - Deployment automation

4. **Collaboration Features**
   - Multiple users
   - Shared workspaces
   - Real-time collaboration

5. **Advanced Monitoring**
   - Real-time metrics dashboard
   - Cost tracking
   - Performance analytics

6. **Plugin System**
   - Custom tools for agent
   - IDE extensions
   - Webhook integrations

---

## 📝 CONCLUSION

This system provides a complete autonomous development environment where:

✅ **Zero Setup Friction**: Clone, configure API keys, run
✅ **Full Autonomy**: Agent has complete control
✅ **Visual Feedback**: See code changes in real-time
✅ **Natural Interaction**: Chat interface for task assignment
✅ **Secure Execution**: Isolated sandbox environment
✅ **Production Ready**: Scalable, monitored, documented

The combination of OpenHands (autonomous agent) + Daytona (secure runtime) + VS Code Web (visual interface) creates a powerful platform for AI-driven development with human oversight and control.

---

**Ready to build the future of autonomous development! 🚀**
