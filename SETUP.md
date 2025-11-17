# 🚀 Setup Guide - Agentic Development System

Complete setup instructions to get your autonomous AI development environment running.

---

## 📋 Prerequisites

Before you begin, ensure you have:

### Required Software

1. **Docker Desktop** (or Docker Engine + Docker Compose)
   - **Mac**: [Download Docker Desktop for Mac](https://docs.docker.com/desktop/install/mac-install/)
   - **Windows**: [Download Docker Desktop for Windows](https://docs.docker.com/desktop/install/windows-install/)
   - **Linux**: [Install Docker Engine](https://docs.docker.com/engine/install/) + [Docker Compose](https://docs.docker.com/compose/install/)

2. **Git** (for cloning the repository)
   - Check if installed: `git --version`
   - Install: [Git Downloads](https://git-scm.com/downloads)

### Required API Keys

1. **LLM API Key** (Choose one):
   - **OpenAI**: Get API key from [https://platform.openai.com/api-keys](https://platform.openai.com/api-keys)
   - **Anthropic (Claude)**: Get API key from [https://console.anthropic.com/](https://console.anthropic.com/)
   - **Local LLM**: Use Ollama or LM Studio (free, no API key needed)
   - **Other OpenAI-compatible providers**: Groq, Together AI, etc.

2. **Daytona API Key**:
   - Sign up at [https://app.daytona.io](https://app.daytona.io)
   - Generate API key at [https://app.daytona.io/dashboard/keys](https://app.daytona.io/dashboard/keys)
   - Free tier includes initial compute credits

---

## 🎯 Quick Setup (5 minutes)

### Step 1: Clone the Repository

```bash
git clone https://github.com/your-username/agentic-dev-system.git
cd agentic-dev-system
```

### Step 2: Run Setup Script

```bash
chmod +x scripts/setup.sh
./scripts/setup.sh
```

The setup script will:
- Check for Docker installation
- Create `.env` file from template
- Prompt you to add API keys
- Validate configuration
- Pull and build Docker images

### Step 3: Configure API Keys

Edit the `.env` file and add your keys:

```bash
nano .env  # or use your preferred editor
```

**Minimum required configuration**:
```env
# Your LLM API key
LLM_API_KEY=sk-your-openai-key-here
LLM_BASE_URL=https://api.openai.com/v1
LLM_MODEL=gpt-4

# Your Daytona API key
DAYTONA_API_KEY=your-daytona-key-here

# Set a secure password for VS Code
CODE_SERVER_PASSWORD=your-secure-password-here
```

### Step 4: Start the System

```bash
./scripts/start.sh
```

### Step 5: Access the Interface

Open your browser and navigate to:
```
http://localhost
```

You should see:
- **Left Panel**: VS Code with your workspace
- **Right Panel**: Chat interface for the AI agent

---

## 🔧 Detailed Configuration

### LLM Provider Configuration

#### Option 1: OpenAI (Recommended for best results)

```env
LLM_API_KEY=sk-your-openai-key-here
LLM_BASE_URL=https://api.openai.com/v1
LLM_MODEL=gpt-4  # or gpt-4-turbo, gpt-3.5-turbo
LLM_TEMPERATURE=0.7
LLM_MAX_TOKENS=4096
```

**Cost**: ~$0.03 per 1K tokens (input), ~$0.06 per 1K tokens (output)

#### Option 2: Anthropic Claude

```env
LLM_API_KEY=sk-ant-your-anthropic-key-here
LLM_BASE_URL=https://api.anthropic.com/v1
LLM_MODEL=claude-3-opus-20240229  # or claude-3-sonnet-20240229
LLM_TEMPERATURE=0.7
LLM_MAX_TOKENS=4096
```

**Cost**: Varies by model (~$0.015 per 1K tokens for Sonnet)

#### Option 3: Local LLM with Ollama (Free)

1. Install Ollama: [https://ollama.ai/download](https://ollama.ai/download)

2. Pull a model:
   ```bash
   ollama pull deepseek-coder
   # or
   ollama pull codellama
   ```

3. Configure `.env`:
   ```env
   LLM_API_KEY=ollama
   LLM_BASE_URL=http://host.docker.internal:11434/v1
   LLM_MODEL=deepseek-coder
   LLM_TEMPERATURE=0.7
   LLM_MAX_TOKENS=4096
   ```

**Cost**: Free (runs on your machine)
**Note**: Requires powerful hardware (16GB+ RAM recommended)

#### Option 4: Local LLM with LM Studio (Free)

1. Install LM Studio: [https://lmstudio.ai/](https://lmstudio.ai/)

2. Download a model in LM Studio UI

3. Start the local server in LM Studio

4. Configure `.env`:
   ```env
   LLM_API_KEY=lm-studio
   LLM_BASE_URL=http://host.docker.internal:1234/v1
   LLM_MODEL=local-model
   LLM_TEMPERATURE=0.7
   LLM_MAX_TOKENS=4096
   ```

### Daytona Configuration

1. **Sign Up**: Visit [https://app.daytona.io](https://app.daytona.io)

2. **Generate API Key**:
   - Go to [Dashboard → API Keys](https://app.daytona.io/dashboard/keys)
   - Click "Create New Key"
   - Copy the key

3. **Add to .env**:
   ```env
   DAYTONA_API_KEY=your-daytona-key-here
   DAYTONA_API_URL=https://api.daytona.io
   DAYTONA_TARGET=default
   ```

**Free Tier**: Includes initial compute credits for testing

### Port Configuration

If ports 80, 3000, 3001, or 8080 are already in use:

```env
# Main access port (default: 80)
NGINX_PORT=8000

# Frontend port (default: 3000)
APP_PORT=3030

# Backend port (default: 3001)
BACKEND_PORT=3031

# VS Code port (default: 8080)
CODE_SERVER_PORT=8888
```

Then access at `http://localhost:8000` (or your chosen NGINX_PORT)

---

## 🏃 Running the System

### Start Everything

```bash
./scripts/start.sh
```

Or manually:
```bash
docker-compose up -d
```

### View Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f code-server
```

### Stop Everything

```bash
./scripts/stop.sh
```

Or manually:
```bash
docker-compose down
```

### Restart Services

```bash
docker-compose restart
```

### Rebuild After Code Changes

```bash
docker-compose up --build
```

---

## 🧪 Testing the System

### 1. Check Service Health

```bash
# Check all services
docker-compose ps

# Should show all services as "running"
```

### 2. Test Backend API

```bash
curl http://localhost:3001/api/health

# Should return: {"status":"healthy",...}
```

### 3. Test Frontend

Open browser to `http://localhost` - you should see the interface

### 4. Test VS Code

Open `http://localhost:8080` (or your CODE_SERVER_PORT)
- Enter password from `.env`
- Should see VS Code interface

### 5. Test AI Agent

In the chat interface, try:
```
Create a simple Python hello world script
```

The agent should:
1. Create a file in the workspace
2. Write the code
3. Report back
4. You can see the file in VS Code

---

## 🐛 Troubleshooting

### Problem: Docker containers won't start

**Solution 1**: Check Docker is running
```bash
docker ps
```

**Solution 2**: Check for port conflicts
```bash
# macOS/Linux
lsof -i :80
lsof -i :3000
lsof -i :3001
lsof -i :8080

# Windows PowerShell
netstat -ano | findstr :80
netstat -ano | findstr :3000
```

**Solution 3**: Clear Docker cache and rebuild
```bash
docker-compose down -v
docker system prune -a
docker-compose up --build
```

### Problem: "Failed to create Daytona sandbox"

**Possible causes**:

1. **Invalid API key**
   - Verify key at [https://app.daytona.io/dashboard/keys](https://app.daytona.io/dashboard/keys)
   - Ensure no extra spaces in `.env`

2. **No internet connection**
   - Daytona requires internet to connect to cloud sandboxes

3. **Account limits**
   - Check Daytona dashboard for quota/limits
   - Free tier has resource limits

**Debug**:
```bash
# Check backend logs
docker-compose logs backend | grep -i daytona
```

### Problem: "LLM API Error" or "Failed to connect to LLM"

**Possible causes**:

1. **Invalid API key**
   - Check key is correct in `.env`
   - Verify key works: `curl https://api.openai.com/v1/models -H "Authorization: Bearer $LLM_API_KEY"`

2. **Wrong base URL**
   - OpenAI: `https://api.openai.com/v1`
   - Anthropic: `https://api.anthropic.com/v1`
   - Ollama: `http://host.docker.internal:11434/v1`

3. **Rate limits or quota exceeded**
   - Check provider dashboard for limits

**Debug**:
```bash
# Check backend logs
docker-compose logs backend | grep -i llm
```

### Problem: VS Code shows "Unauthorized"

**Solution**:
- Check `CODE_SERVER_PASSWORD` in `.env`
- Restart code-server: `docker-compose restart code-server`
- Clear browser cache and try again

### Problem: WebSocket connection fails

**Solution**:
```bash
# Check nginx configuration
docker-compose logs nginx

# Restart nginx
docker-compose restart nginx

# Check firewall
# Make sure port 80 (or NGINX_PORT) is not blocked
```

### Problem: Agent not responding to messages

**Debug steps**:

1. Check backend is running:
   ```bash
   docker-compose ps backend
   ```

2. Check backend logs:
   ```bash
   docker-compose logs -f backend
   ```

3. Verify WebSocket connection in browser console (F12)

4. Restart backend:
   ```bash
   docker-compose restart backend
   ```

---

## 🔐 Security Recommendations

### For Development

1. **Change default password**:
   ```env
   CODE_SERVER_PASSWORD=use-strong-password-here
   ```

2. **Keep `.env` private**:
   - Never commit to git
   - Already in `.gitignore`

### For Production

1. **Use HTTPS**:
   - Configure SSL certificate in nginx
   - Use Let's Encrypt for free certs

2. **Set strong secrets**:
   ```env
   JWT_SECRET=generate-long-random-string-here
   CODE_SERVER_PASSWORD=very-strong-password
   ```

3. **Restrict CORS**:
   ```env
   ALLOWED_ORIGINS=https://yourdomain.com
   ```

4. **Use secrets manager**:
   - AWS Secrets Manager
   - HashiCorp Vault
   - Don't use .env in production

5. **Set resource limits** in docker-compose.yml

6. **Enable rate limiting** (already configured in nginx)

---

## 📊 Monitoring

### View Resource Usage

```bash
docker stats
```

### Check Daytona Usage

Visit [https://app.daytona.io/dashboard](https://app.daytona.io/dashboard)

### View Application Logs

```bash
# All logs
docker-compose logs

# Tail logs (follow)
docker-compose logs -f

# Last 100 lines
docker-compose logs --tail=100

# Specific service
docker-compose logs -f backend
```

---

## 🔄 Updating the System

### Pull Latest Changes

```bash
git pull origin main
```

### Rebuild Containers

```bash
docker-compose down
docker-compose up --build -d
```

### Update Docker Images

```bash
docker-compose pull
docker-compose up -d
```

---

## 📚 Next Steps

After successful setup:

1. **Read the README**: `README.md` for usage examples

2. **Review Architecture**: `AGENTIC_SYSTEM_DESIGN.md` for detailed design

3. **Try Example Tasks**:
   - "Create a FastAPI REST API with user authentication"
   - "Build a React todo app with TypeScript"
   - "Write unit tests for the existing code"

4. **Customize Configuration**: Tune LLM parameters, agent settings, etc.

5. **Explore OpenHands**: [https://docs.all-hands.dev](https://docs.all-hands.dev)

6. **Learn Daytona**: [https://www.daytona.io/docs](https://www.daytona.io/docs)

---

## 🆘 Getting Help

If you encounter issues:

1. **Check logs**: `docker-compose logs -f`

2. **Review documentation**:
   - [README.md](./README.md)
   - [AGENTIC_SYSTEM_DESIGN.md](./AGENTIC_SYSTEM_DESIGN.md)

3. **Check upstream docs**:
   - [OpenHands Documentation](https://docs.all-hands.dev)
   - [Daytona Documentation](https://www.daytona.io/docs)

4. **Community support**:
   - OpenHands Slack/Discord
   - Daytona Slack: [go.daytona.io/slack](https://go.daytona.io/slack)

---

## ✅ Setup Complete!

You're ready to start using your autonomous AI development system!

Access at: **http://localhost**

Happy coding! 🚀
