# 🚀 START HERE - Quick Setup Guide

## Welcome to the Agentic Development System!

This is your **complete autonomous AI development environment**. Follow these steps to get started.

---

## ⚡ Quick Setup (5 minutes)

### Step 1: Clone the Repository

```bash
git clone <your-repo-url>
cd daytona
```

### Step 2: Get API Keys (FREE)

You need 2 API keys:

1. **Groq API Key** (FREE)
   - Go to: https://console.groq.com/
   - Sign up for free
   - Create API key: https://console.groq.com/keys
   - Copy your key (starts with `gsk_`)

2. **Daytona API Key** (FREE tier available)
   - Go to: https://app.daytona.io
   - Sign up for free
   - Create API key: https://app.daytona.io/dashboard/keys
   - Copy your key (starts with `dtn_`)

### Step 3: Configure Locally (SECURE)

```bash
# Copy the example file
cp .env.example .env

# Edit with your keys (NEVER commit this file!)
nano .env
```

Add your keys to `.env`:

```env
LLM_API_KEY=gsk_YOUR_GROQ_KEY_HERE
LLM_BASE_URL=https://api.groq.com/openai/v1
LLM_MODEL=llama-3.1-70b-versatile

DAYTONA_API_KEY=dtn_YOUR_DAYTONA_KEY_HERE
DAYTONA_API_URL=https://app.daytona.io/api

CODE_SERVER_PASSWORD=YourSecurePassword123!
```

⚠️ **IMPORTANT**: Your `.env` file should NEVER be committed to git!

### Step 4: Start the System

```bash
# Make scripts executable
chmod +x scripts/*.sh

# Start everything
./scripts/start.sh
```

### Step 5: Access the Interface

Open your browser to: **http://localhost**

You'll see:
- **Left Panel**: VS Code with your workspace
- **Right Panel**: Chat interface for AI agent

---

## 💡 Try Your First Task

In the chat interface, type:

```
Create a Python script that prints "Hello from Agentic Dev System!"
```

Watch the agent:
1. Create the file
2. Write the code
3. Report completion
4. See the file appear in VS Code!

---

## 🔐 Security Notice

**CRITICAL**: Your `.env` file contains secret API keys!

✅ **DO**:
- Keep `.env` on your local machine only
- It's already in `.gitignore`
- Set secure permissions: `chmod 600 .env`

❌ **DON'T**:
- Never commit `.env` to git
- Never share your API keys
- Never push `.env` to GitHub

📖 **Read**: [SECURITY_SETUP.md](./SECURITY_SETUP.md) for complete security guide

---

## 📚 Documentation

- **START_HERE.md** - This file (you are here!)
- **SECURITY_SETUP.md** - Secure API key setup (READ THIS!)
- **QUICK_START.md** - Quick start guide
- **README.md** - Complete user guide
- **SETUP.md** - Detailed setup instructions
- **AGENTIC_SYSTEM_DESIGN.md** - System architecture

---

## 🛠️ Commands

```bash
# Start the system
./scripts/start.sh

# Stop the system
./scripts/stop.sh

# View logs
docker-compose logs -f

# Restart services
docker-compose restart

# Rebuild after changes
docker-compose up --build
```

---

## 🎯 Example Tasks

Try these with the AI agent:

### Simple:
```
Create a Python hello world script
```

### Intermediate:
```
Build a FastAPI REST API with GET /users endpoint
```

### Advanced:
```
Create a complete blog API with:
- User authentication
- CRUD for posts
- SQLite database
- Input validation
```

---

## 🐛 Common Issues

### Containers won't start

```bash
# Check Docker is running
docker ps

# Rebuild
docker-compose down
docker-compose up --build
```

### API Key errors

```bash
# Verify .env exists
ls -la .env

# Check keys are set
cat .env | grep API_KEY

# Restart
docker-compose restart
```

### Can't access interface

```bash
# Check all services running
docker-compose ps

# Check logs
docker-compose logs nginx
docker-compose logs frontend
```

---

## ✅ Verification Checklist

Before using the system:

- [ ] Cloned the repository
- [ ] Got Groq API key
- [ ] Got Daytona API key
- [ ] Created `.env` from `.env.example`
- [ ] Added actual API keys to `.env`
- [ ] Verified `.env` is NOT in git: `git status`
- [ ] Started the system: `./scripts/start.sh`
- [ ] Accessed http://localhost
- [ ] Tried a simple task

---

## 🆘 Need Help?

1. **Check logs**: `docker-compose logs -f backend`
2. **Health check**: `curl http://localhost/api/health`
3. **Read docs**: [SECURITY_SETUP.md](./SECURITY_SETUP.md), [SETUP.md](./SETUP.md)
4. **Restart**: `docker-compose restart`

---

## 🎉 You're Ready!

Your autonomous AI development system is ready to use!

**Next**: Open http://localhost and start coding with AI! 🤖💻

---

**Important Security Reminder**: Always keep your `.env` file local and NEVER commit it to git! 🔐
