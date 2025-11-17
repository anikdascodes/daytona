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

- Docker & Docker Compose installed
- OpenAI-compatible LLM API access (OpenAI, Anthropic, Ollama, etc.)
- Daytona account and API key ([Get one here](https://app.daytona.io))

### Installation

1. **Clone the repository**:
   ```bash
   git clone <your-repo-url>
   cd agentic-dev-system
   ```

2. **Configure environment**:
   ```bash
   cp .env.example .env
   # Edit .env and add your API keys
   nano .env
   ```

   **Required configurations**:
   - `LLM_API_KEY` - Your LLM API key
   - `LLM_BASE_URL` - Your LLM provider URL
   - `DAYTONA_API_KEY` - Your Daytona API key ([Get it here](https://app.daytona.io/dashboard/keys))
   - `CODE_SERVER_PASSWORD` - Password for VS Code access

3. **Start the system**:
   ```bash
   docker-compose up -d
   ```

4. **Access the interface**:
   ```
   Open http://localhost in your browser
   ```

   You'll see:
   - **Left Panel**: VS Code with your workspace
   - **Right Panel**: Chat interface to assign tasks to the AI agent

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
