# Quick Start Guide

## Fastest Way to Get Started

### 1. Run Setup Script

```bash
cd /workspaces/daytona/ai-engineer-app
chmod +x setup.sh
./setup.sh
```

This will:
- Check all prerequisites
- Clone OpenHands
- Install all dependencies
- Create startup scripts

### 2. Start the Application

```bash
./start-all.sh
```

This starts both backend and frontend.

### 3. Open in Browser

Navigate to: **http://localhost:3000**

---

## Manual Setup (Alternative)

### Backend

```bash
cd /workspaces/daytona/ai-engineer-app/backend

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
cd /workspaces/daytona
git clone https://github.com/OpenHands/OpenHands.git
cd OpenHands
pip install -e ".[third_party_runtimes]"

# Install backend requirements
cd /workspaces/daytona/ai-engineer-app/backend
pip install -r requirements.txt

# Start server
python main.py
```

### Frontend

```bash
cd /workspaces/daytona/ai-engineer-app/frontend

# Install dependencies
npm install

# Start dev server
npm run dev
```

---

## First Time Usage

### 1. Configure LLM

- **Provider**: Choose your LLM provider (OpenAI, Anthropic, Google, Custom)
- **Model**: Select the model (e.g., gpt-4o, claude-3-5-sonnet)
- **API Key**: Enter your API key
- **Base URL**: (Optional) For custom OpenAI-compatible APIs

### 2. Configure Runtime

- **Provider**: Choose runtime (Docker, Daytona, Modal, E2B)
- **API Key**: Enter if required
- **API URL**: Enter if required
- **Target**: For Daytona, specify region (eu, us, etc.)

### 3. Health Check

Click "Run Health Check" to verify:
- LLM connection
- Runtime connection
- Overall system status

### 4. Start Coding

Once health check passes:
- Click "Start Session"
- Use the chat interface to describe tasks
- Switch to Terminal tab for direct command execution

---

## Example Tasks

### Web Development
```
Build a REST API with FastAPI that has CRUD endpoints for a todo list
```

### Data Science
```
Create a Python script to analyze CSV data and generate visualizations
```

### Debugging
```
Debug this Python function: [paste code]
```

### DevOps
```
Write a Dockerfile for a Node.js application with multi-stage build
```

---

## Configuration Examples

### Using OpenAI

```
Provider: openai
Model: gpt-4o
API Key: sk-...
Base URL: (leave empty)
```

### Using Custom LLM (e.g., Ollama, LM Studio)

```
Provider: custom
Model: llama2
API Key: not-needed
Base URL: http://localhost:11434/v1
```

### Using Docker (Local)

```
Provider: docker
API Key: (not needed)
```

### Using Daytona

```
Provider: daytona
API Key: your-key
API URL: https://app.daytona.io/api
Target: eu
```

---

## Troubleshooting

### "Connection refused" on backend

```bash
# Check if port 8000 is available
lsof -i :8000

# If in use, kill the process or change port in main.py
```

### "Module not found" errors

```bash
# Reinstall dependencies
cd /workspaces/daytona/ai-engineer-app/backend
source venv/bin/activate
pip install --force-reinstall -e ../../OpenHands[third_party_runtimes]
```

### Frontend won't start

```bash
# Clear npm cache
cd /workspaces/daytona/ai-engineer-app/frontend
rm -rf node_modules package-lock.json
npm install
```

### Health check fails

**LLM Issues:**
- Verify API key is correct
- Check internet connection
- Ensure API has credits

**Runtime Issues:**
- Docker: Ensure daemon is running (`docker ps`)
- Daytona: Verify API key and URL
- Modal: Check token format (starts with `ak-`)

---

## Advanced Features

### Using Multiple LLMs

You can configure different LLMs for different purposes by modifying the configuration.

### Custom Agent Behavior

Edit the agent configuration in the backend to customize behavior.

### Persistent Sessions

Sessions can be saved and resumed (feature coming soon).

---

## Development

### Backend Development

```bash
cd /workspaces/daytona/ai-engineer-app/backend
source venv/bin/activate
python main.py  # Auto-reloads on changes
```

### Frontend Development

```bash
cd /workspaces/daytona/ai-engineer-app/frontend
npm run dev  # Hot module replacement enabled
```

---

## Production Deployment

### Using Docker Compose (Recommended)

```yaml
version: '3.8'

services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - BACKEND_HOST=0.0.0.0
      - BACKEND_PORT=8000
    volumes:
      - ./OpenHands:/app/OpenHands

  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    depends_on:
      - backend
```

### Using Nginx (Reverse Proxy)

```nginx
server {
    listen 80;
    server_name yourdomain.com;

    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }

    location /api {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }

    location /ws {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "Upgrade";
        proxy_set_header Host $host;
    }
}
```

---

## Support

For issues:
1. Check the troubleshooting section
2. Review backend logs
3. Check browser console for frontend errors
4. Consult OpenHands documentation: https://docs.all-hands.dev

---

## License

MIT License - See LICENSE file for details
