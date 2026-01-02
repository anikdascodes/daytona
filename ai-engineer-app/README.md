# AI Engineer

Open-source AI coding assistant. No login required - bring your own LLM and compute.

## Quick Start

### Prerequisites

- Python 3.10+
- Node.js 18+
- Docker (if using Docker runtime)

### 1. Install Backend

```bash
cd ai-engineer-app/backend

# Install dependencies
pip install -r requirements.txt
```

### 2. Install Frontend

```bash
cd ai-engineer-app/frontend

# Install dependencies
npm install
```

### 3. Start the Application

**Terminal 1 - Start Backend:**
```bash
cd ai-engineer-app/backend
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

**Terminal 2 - Start Frontend:**
```bash
cd ai-engineer-app/frontend
npm run dev
```

### 4. Open in Browser

Open **http://localhost:3000** in your browser.

---

## Usage

### Step 1: Configure LLM

1. Enter your **Model** name:
   - OpenAI: `gpt-4o`, `gpt-4o-mini`, `o1-preview`
   - Anthropic: `claude-sonnet-4-20250514`, `claude-3-5-sonnet-20241022`
   - Google: `gemini-2.0-flash`, `gemini-1.5-pro`
   - Or any other model name

2. Enter your **API Key**

3. (Optional) Enter **Base URL** for custom endpoints

### Step 2: Configure Runtime

Choose where your code will run:

| Provider | Description | Requires |
|----------|-------------|----------|
| Docker | Local containers | Docker running |
| Daytona | Cloud workspaces | API Key + URL |
| Modal | Serverless containers | API Key |
| E2B | Code sandboxes | API Key |

### Step 3: Health Check

Click **Run Health Check** to verify:
- LLM connection works
- Runtime provider is accessible

### Step 4: Start Coding

Once health check passes:
1. Click **Start Session**
2. Describe your task in the chat
3. Watch the AI work!

---

## Example Tasks

```
"Create a Python REST API with Flask that has CRUD operations for a todo list"

"Build a React component that displays a sortable data table"

"Write unit tests for the authentication module"

"Debug this error: TypeError: Cannot read property 'map' of undefined"
```

---

## Troubleshooting

### Port already in use

```bash
# Kill process on port 8000
lsof -ti :8000 | xargs kill -9

# Kill process on port 3000
lsof -ti :3000 | xargs kill -9
```

### Backend won't start

```bash
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

### Frontend won't start

```bash
# Clear and reinstall
rm -rf node_modules
npm install
```

### Docker runtime not working

```bash
# Check Docker is running
docker ps

# Start Docker Desktop if needed
```

---

## Project Structure

```
ai-engineer-app/
├── backend/
│   ├── main.py              # FastAPI server
│   └── requirements.txt     # Python dependencies
├── frontend/
│   ├── src/
│   │   ├── components/      # UI components
│   │   ├── pages/           # Page components
│   │   ├── services/        # API services
│   │   ├── store/           # State management
│   │   └── types/           # TypeScript types
│   ├── package.json
│   └── vite.config.ts
└── README.md
```

---

## Tech Stack

**Backend:**
- FastAPI
- WebSockets
- LiteLLM (for LLM integration)

**Frontend:**
- React 18
- TypeScript
- Tailwind CSS
- Vite
- Zustand (state management)
- xterm.js (terminal)

---

## License

MIT
