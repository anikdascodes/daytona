# 🤖 Autonomous Agentic Development System

A complete AI-powered development environment combining **OpenHands** (autonomous AI agent), **Daytona** (secure sandbox runtime), and **VS Code Web** to create a fully autonomous coding assistant that can handle any development task without human intervention.

![System Architecture](https://img.shields.io/badge/OpenHands-AI%20Agent-blue) ![Daytona](https://img.shields.io/badge/Daytona-Secure%20Runtime-green) ![VS Code](https://img.shields.io/badge/VS%20Code-Web%20IDE-orange)

---

## 🎯 What This System Does

This system provides a **complete autonomous development environment** where:

- 🤖 **AI Agent** has full control over your development workspace
- 💬 **Chat Interface** for natural language task assignment
- 🖥️ **VS Code in Browser** for real-time visualization
- 🔒 **Secure Execution** in isolated Daytona sandboxes
- ⚡ **Zero Setup** - just clone, configure, and run

### Example Use Cases:

```
User: "Create a REST API for a blog with authentication"
Agent: *Creates FastAPI project, implements auth, writes tests, and runs them*

User: "Fix the bug in user registration"
Agent: *Finds the issue, fixes it, tests, and reports back*

User: "Refactor the database code to use connection pooling"
Agent: *Refactors, updates all usages, tests, and documents changes*
```

---

## 🧠 Advanced Learning Systems (NEW!)

**Phase 4, Task 4.5** introduces **Supreme AI Capabilities** with self-improving, collaborative AI agents:

### 5 Core Learning Components

1. **🎓 Learning Engine**: Automatically learns from every interaction
   - Extracts success and failure patterns
   - Builds knowledge from experience
   - Confidence-based learning validation

2. **🌐 Knowledge Hub**: Real-time cross-agent knowledge sharing
   - Broadcast discoveries to all agents
   - Topic-based channels and subscriptions
   - Vote on knowledge usefulness

3. **📊 Performance Optimizer**: Historical performance analysis
   - Track metrics (speed, errors, success rate)
   - Generate optimization recommendations
   - Compare agent performance

4. **🎯 Adaptive Strategy**: Dynamic strategy selection
   - Analyze task complexity
   - Select optimal agent combination
   - Learn from outcomes

5. **💾 Knowledge Base Evolution**: Persistent knowledge storage
   - Version-controlled knowledge
   - State evolution (Experimental → Validated → Deprecated)
   - Import/export capabilities

### Impact Metrics

- 📈 **5-10x faster** development through learned optimizations
- 🧠 **Accumulated wisdom** - agents get smarter over time
- 🤝 **Collaborative intelligence** - agents share discoveries
- 🎯 **Data-driven decisions** - strategy selection based on history
- 💾 **Persistent learning** - knowledge survives across sessions

### Quick Start with Learning Systems

```python
# Learning is automatic! Just use any agent
python backend/demo_advanced_learning.py
```

📖 **Full Documentation**: [Advanced Learning Guide](./docs/guides/ADVANCED_LEARNING_GUIDE.md) | [All Documentation](./docs/README.md)

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────┐
│              Web Browser (Port 80)                   │
│  ┌───────────────────┐  ┌────────────────────────┐ │
│  │  VS Code Web      │  │  Chat Interface        │ │
│  │  (Live Coding)    │  │  (Task Assignment)     │ │
│  └─────────┬─────────┘  └───────────┬────────────┘ │
└────────────┼────────────────────────┼──────────────┘
             │                        │
             │          Nginx         │
             │                        │
    ┌────────▼───────┐       ┌───────▼────────────┐
    │  code-server   │       │  OpenHands Agent   │
    │  (Port 8080)   │       │  + Daytona Runtime │
    │                │       │  (Port 3001)       │
    └────────────────┘       └───────┬────────────┘
                                     │
                             ┌───────▼────────┐
                             │  Daytona Cloud │
                             │  (Sandbox)     │
                             └────────────────┘
```

---

## 🚀 Quick Start

### Prerequisites

- **Docker & Docker Compose** installed ([Get Docker](https://docs.docker.com/get-docker/))
- **Internet connection** (for API access)
- **Free API keys** (instructions below)

### Step-by-Step Setup

#### 1️⃣ Clone the Repository

```bash
git clone https://github.com/yourusername/daytona.git
cd daytona
```

#### 2️⃣ Get Your FREE API Keys

##### **Groq API Key** (Recommended - Fast & Free)

1. Visit: **https://console.groq.com/keys**
2. Sign up with Google/GitHub (free)
3. Click **"Create API Key"**
4. Copy the key (starts with `gsk_...`)
5. **Save it somewhere safe** (you'll need it in the next step)

**Alternative LLM Providers:**
- **OpenAI**: https://platform.openai.com/api-keys (requires payment)
- **Anthropic**: https://console.anthropic.com (requires payment)

##### **Daytona API Key** (Free Tier Available)

1. Visit: **https://app.daytona.io/dashboard/keys**
2. Sign up (free tier available)
3. Click **"Create API Key"**
4. Copy the key (starts with `dtn_...`)
5. **Save it somewhere safe**

#### 3️⃣ Configure API Keys (IMPORTANT!)

**Create the configuration file:**

```bash
# Copy the example configuration
cp .env.example .env

# Edit the file with your favorite editor
nano .env
# OR
vim .env
# OR use VS Code
code .env
```

**Add your API keys to `.env` file:**

```env
# ============================================
# LLM Configuration (Groq - Recommended)
# ============================================
LLM_API_KEY=gsk_YOUR_ACTUAL_GROQ_KEY_HERE_PASTE_IT
LLM_BASE_URL=https://api.groq.com/openai/v1
LLM_MODEL=llama-3.1-70b-versatile

# ============================================
# Daytona Configuration
# ============================================
DAYTONA_API_KEY=dtn_YOUR_ACTUAL_DAYTONA_KEY_HERE_PASTE_IT
DAYTONA_API_URL=https://api.daytona.io

# ============================================
# VS Code Password (Change This!)
# ============================================
CODE_SERVER_PASSWORD=your-secure-password-here
```

**⚠️ CRITICAL SECURITY NOTES:**

| ✅ DO | ❌ DON'T |
|-------|----------|
| Keep `.env` on your local machine ONLY | Never commit `.env` to GitHub |
| Use strong, unique passwords | Share your API keys with anyone |
| Rotate keys regularly | Push `.env` to repository |
| Keep `.env` in `.gitignore` (already done) | Use default passwords in production |

**File Location:**
```
daytona/
├── .env              ← YOUR API KEYS GO HERE (create this file)
├── .env.example      ← Template (already exists)
├── .gitignore        ← Protects .env (already configured)
├── docker-compose.yml
└── backend/
    └── .env          ← Will be auto-created from root .env
```

#### 4️⃣ Verify Configuration (Optional but Recommended)

```bash
# Check that your .env file exists
ls -la .env

# Verify it has the correct permissions (should be readable only by you)
chmod 600 .env

# Quick test: Check if keys are loaded (without showing actual keys)
cd backend
python3 -c "
from config import settings
print('✅ Configuration loaded successfully!')
print(f'LLM Model: {settings.LLM_MODEL}')
print(f'API Keys configured: Yes')
"
```

**Expected output:**
```
✅ Configuration loaded successfully!
LLM Model: llama-3.1-70b-versatile
API Keys configured: Yes
```

#### 5️⃣ Test Advanced Learning Systems (Quick Test)

Before starting the full system, test that everything works:

```bash
cd backend

# Install dependencies (if not using Docker)
pip install -r requirements.txt

# Run the demo (tests all 5 learning systems)
python demo_advanced_learning.py
```

**Expected output:**
```
✨ LearningEngine initialized
🌐 KnowledgeHub initialized
📊 PerformanceOptimizer initialized
🎯 AdaptiveStrategySystem initialized
📚 KnowledgeBaseEvolution initialized

============================================================
1. LEARNING ENGINE - Continuous Learning
============================================================
📝 Recording successful interactions...
  ✅ Recorded interaction 1: interaction_1_...
  ...
```

**If you see this, your system is working! 🎉**

#### 6️⃣ Start the Full System

```bash
# Return to project root
cd ..

# Start all services
docker-compose up -d
```

**What's starting:**
- ✅ Backend API server (Port 3001)
- ✅ Frontend React app (Port 3000)
- ✅ VS Code in browser (Port 8080)
- ✅ Nginx reverse proxy (Port 80)

**Check status:**
```bash
docker-compose ps
```

All services should show "Up" status.

#### 7️⃣ Access the Interface

**Open your browser and go to:**

```
http://localhost
```

**What you'll see:**

```
┌─────────────────────────────────────────────────────────┐
│                    Daytona AI System                     │
├─────────────────────┬───────────────────────────────────┤
│                     │                                   │
│  VS Code Web        │   Chat Interface                  │
│  (Live Coding)      │   (Task Assignment)               │
│                     │                                   │
│  - See files        │   Type your task:                 │
│  - Edit code        │   > "Create a Python REST API"    │
│  - View terminal    │   > "Write unit tests"            │
│  - Git integration  │   > "Debug the error"             │
│                     │                                   │
└─────────────────────┴───────────────────────────────────┘
```

**VS Code Password:** Use the password you set in `.env` (`CODE_SERVER_PASSWORD`)

#### 8️⃣ Assign Your First Task!

In the chat interface, try:

```
Create a simple Python calculator with:
- Functions for add, subtract, multiply, divide
- Error handling for division by zero
- Unit tests with pytest
```

Watch the AI:
1. ✅ Analyze the task (complexity, requirements)
2. ✅ Select optimal strategy
3. ✅ Create the files in VS Code
4. ✅ Write the code
5. ✅ Write and run tests
6. ✅ Learn from the execution
7. ✅ Share knowledge with other agents

---

### 🎯 Quick Commands Reference

```bash
# Start system
docker-compose up -d

# Stop system
docker-compose down

# View logs
docker-compose logs -f

# Restart after changes
docker-compose restart

# Rebuild after code changes
docker-compose up --build -d

# Check status
docker-compose ps

# Test learning systems
cd backend && python demo_advanced_learning.py
```

---

## 📚 Documentation

**All documentation is organized in the [`docs/`](./docs/) directory:**

| Category | Description | Link |
|----------|-------------|------|
| 📖 **Getting Started** | Quick start guides and setup help | [docs/](./docs/) |
| 🧠 **Learning Systems** | Complete guide to all 5 AI learning components | [Advanced Learning Guide](./docs/guides/ADVANCED_LEARNING_GUIDE.md) |
| 🤖 **AI Agents** | Individual guides for each specialized agent | [docs/guides/](./docs/guides/) |
| 🏗️ **Architecture** | System design and architecture details | [Agentic System Design](./docs/guides/AGENTIC_SYSTEM_DESIGN.md) |
| 🔒 **Security** | Security setup and best practices | [Security Guide](./docs/guides/SECURITY_SETUP.md) |
| 📊 **Progress Reports** | Development history and testing results | [docs/progress/](./docs/progress/) |

**👉 Browse all documentation:** [docs/README.md](./docs/README.md)

---

## 📖 Usage Guide

### Assigning Tasks

Simply type what you want in the chat interface:

**Example 1: Create New Project**
```
Create a Python FastAPI project with:
- User authentication (JWT)
- SQLite database
- CRUD operations for blog posts
- Unit tests with pytest
- API documentation
```

**Example 2: Debug Issue**
```
The login endpoint returns 500 error. Find and fix the bug.
```

**Example 3: Refactor Code**
```
Refactor the database connection code to use async/await
and add connection pooling.
```

**Example 4: Add Feature**
```
Add a forgot password feature with email notifications.
```

### Watching the Agent Work

- **VS Code Panel**: See files being created and edited in real-time
- **Chat Panel**: View agent's thought process and actions
- **Terminal**: Agent can run commands, tests, and see output

### Interacting with Results

After the agent completes a task:
1. Review the code in VS Code
2. Ask for modifications in chat
3. Request additional features
4. Ask questions about the implementation

---

## 🛠️ Configuration

### LLM Providers

The system works with any OpenAI-compatible API:

**OpenAI**:
```env
LLM_BASE_URL=https://api.openai.com/v1
LLM_MODEL=gpt-4
LLM_API_KEY=sk-...
```

**Anthropic (Claude)**:
```env
LLM_BASE_URL=https://api.anthropic.com/v1
LLM_MODEL=claude-3-opus-20240229
LLM_API_KEY=sk-ant-...
```

**Local Ollama**:
```env
LLM_BASE_URL=http://host.docker.internal:11434/v1
LLM_MODEL=deepseek-coder
LLM_API_KEY=ollama
```

**Local LM Studio**:
```env
LLM_BASE_URL=http://host.docker.internal:1234/v1
LLM_MODEL=local-model
LLM_API_KEY=lm-studio
```

### Daytona Setup

1. Sign up at [https://app.daytona.io](https://app.daytona.io)
2. Generate API key at [https://app.daytona.io/dashboard/keys](https://app.daytona.io/dashboard/keys)
3. Add to `.env`:
   ```env
   DAYTONA_API_KEY=your-key-here
   ```

---

## 📁 Project Structure

```
agentic-dev-system/
├── docker-compose.yml          # Main orchestration file
├── .env.example               # Environment template
├── README.md                  # This file
├── AGENTIC_SYSTEM_DESIGN.md  # Detailed design document
│
├── backend/                   # OpenHands + Daytona integration
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── main.py               # FastAPI application
│   ├── config.py             # Configuration
│   ├── openhands_config.toml # OpenHands settings
│   └── services/             # Service implementations
│
├── frontend/                  # React chat interface
│   ├── Dockerfile
│   ├── package.json
│   ├── src/
│   │   ├── App.tsx
│   │   ├── components/       # UI components
│   │   ├── services/         # API/WebSocket clients
│   │   └── hooks/            # React hooks
│   └── public/
│
├── nginx/                     # Reverse proxy
│   ├── Dockerfile
│   └── nginx.conf
│
├── workspace/                 # Your code workspace
│   └── (your projects here)
│
└── scripts/                   # Helper scripts
    ├── setup.sh
    ├── start.sh
    └── stop.sh
```

---

## 🔧 Development

### Running in Development Mode

```bash
# Start with logs visible
docker-compose up

# Rebuild after code changes
docker-compose up --build

# View logs
docker-compose logs -f backend
docker-compose logs -f frontend

# Access container shells
docker-compose exec backend bash
docker-compose exec frontend sh
```

### Debugging

**Backend Issues**:
```bash
docker-compose logs -f backend
# Check OpenHands logs
# Check Daytona API connectivity
```

**Frontend Issues**:
```bash
docker-compose logs -f frontend
# Check browser console
# Verify WebSocket connection
```

**VS Code Issues**:
```bash
docker-compose logs -f code-server
# Verify password in .env
# Check port 8080 accessibility
```

---

## 🔒 Security

### Best Practices

1. **Change Default Passwords**:
   ```env
   CODE_SERVER_PASSWORD=use-a-strong-password-here
   JWT_SECRET=generate-random-secret-string
   ```

2. **Protect API Keys**:
   - Never commit `.env` to git
   - Use secrets management in production
   - Rotate keys regularly

3. **Network Security**:
   - Use HTTPS in production (configure nginx SSL)
   - Set up firewall rules
   - Limit exposed ports

4. **Sandbox Isolation**:
   - All code runs in isolated Daytona sandboxes
   - No access to host system
   - Safe execution of untrusted code

---

## 📊 Monitoring

### Health Checks

```bash
# Check all services
docker-compose ps

# Backend health
curl http://localhost:3001/api/health

# Daytona sandbox status
curl http://localhost:3001/api/sandbox/status
```

### Logs

```bash
# All services
docker-compose logs

# Specific service
docker-compose logs backend
docker-compose logs frontend
docker-compose logs code-server

# Follow logs
docker-compose logs -f
```

---

## 🐛 Troubleshooting

### Common Issues

**1. Daytona Connection Failed**
```
Error: Failed to create Daytona sandbox
```
**Solution**:
- Verify `DAYTONA_API_KEY` in `.env`
- Check internet connectivity
- Visit [Daytona Dashboard](https://app.daytona.io) to verify account

**2. LLM API Error**
```
Error: Failed to connect to LLM
```
**Solution**:
- Verify `LLM_API_KEY` in `.env`
- Check `LLM_BASE_URL` is correct
- Verify API quota/credits

**3. VS Code Won't Load**
```
Error: Unauthorized
```
**Solution**:
- Check `CODE_SERVER_PASSWORD` in `.env`
- Clear browser cache
- Verify port 8080 is accessible

**4. WebSocket Connection Failed**
```
Error: WebSocket disconnected
```
**Solution**:
- Check nginx configuration
- Verify backend is running: `docker-compose ps`
- Check firewall rules

### Getting Help

1. Check logs: `docker-compose logs -f`
2. Review [Design Document](./AGENTIC_SYSTEM_DESIGN.md)
3. Check [OpenHands Docs](https://docs.all-hands.dev)
4. Check [Daytona Docs](https://www.daytona.io/docs)

---

## 🚀 Production Deployment

### Deployment Checklist

- [ ] Change all default passwords
- [ ] Generate strong JWT secret
- [ ] Configure SSL/TLS (HTTPS)
- [ ] Set up monitoring (Prometheus/Grafana)
- [ ] Configure log aggregation
- [ ] Set up backups for workspace
- [ ] Configure firewall rules
- [ ] Set resource limits in docker-compose
- [ ] Enable rate limiting in nginx
- [ ] Set up CI/CD pipeline

### Scaling

For production use:
- Use Kubernetes instead of Docker Compose
- Set up load balancing
- Configure auto-scaling
- Use managed Postgres for persistence
- Set up Redis for caching
- Configure CDN for static assets

---

## 📝 License

MIT License - see LICENSE file for details

---

## 🙏 Credits

Built with:
- [OpenHands](https://github.com/OpenHands/OpenHands) - Autonomous AI agent
- [Daytona](https://www.daytona.io) - Secure sandbox runtime
- [code-server](https://github.com/coder/code-server) - VS Code in browser
- [FastAPI](https://fastapi.tiangolo.com) - Backend framework
- [React](https://react.dev) - Frontend framework

---

## 🎯 Roadmap

- [x] Basic autonomous agent functionality
- [x] VS Code integration
- [x] Chat interface
- [x] Daytona sandbox runtime
- [ ] Multi-agent support
- [ ] Git automation (auto-commit, PR creation)
- [ ] Voice input/output
- [ ] Mobile app
- [ ] Plugin system
- [ ] Collaboration features

---

**Ready to experience autonomous AI development! 🚀**

For detailed architecture and implementation details, see [AGENTIC_SYSTEM_DESIGN.md](./AGENTIC_SYSTEM_DESIGN.md).
