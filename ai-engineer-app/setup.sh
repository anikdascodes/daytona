#!/bin/bash

# AI Engineer Setup Script
# Automated setup for the complete application

set -e

echo "=================================="
echo "AI Engineer - Automated Setup"
echo "=================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check prerequisites
echo "Checking prerequisites..."

# Check Python
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Error: Python 3 is not installed${NC}"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1-2)
echo -e "${GREEN}✓${NC} Python ${PYTHON_VERSION} found"

# Check Node.js
if ! command -v node &> /dev/null; then
    echo -e "${RED}Error: Node.js is not installed${NC}"
    exit 1
fi

NODE_VERSION=$(node --version)
echo -e "${GREEN}✓${NC} Node.js ${NODE_VERSION} found"

# Check npm
if ! command -v npm &> /dev/null; then
    echo -e "${RED}Error: npm is not installed${NC}"
    exit 1
fi

echo -e "${GREEN}✓${NC} npm found"

# Check Docker (optional)
if command -v docker &> /dev/null; then
    echo -e "${GREEN}✓${NC} Docker found"
else
    echo -e "${YELLOW}⚠${NC} Docker not found (optional, needed for local runtime)"
fi

echo ""

# Setup backend
echo "Setting up backend..."
cd /workspaces/daytona/ai-engineer-app/backend

# Create virtual environment
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install OpenHands
echo "Installing OpenHands..."
cd /workspaces/daytona
if [ ! -d "OpenHands" ]; then
    git clone https://github.com/OpenHands/OpenHands.git
fi

cd OpenHands
pip install --upgrade pip
pip install -e ".[third_party_runtimes]"

# Install additional backend dependencies
echo "Installing backend dependencies..."
pip install fastapi uvicorn python-multipart websockets

echo -e "${GREEN}✓${NC} Backend setup complete"
echo ""

# Setup frontend
echo "Setting up frontend..."
cd /workspaces/daytona/ai-engineer-app/frontend

if [ ! -d "node_modules" ]; then
    echo "Installing frontend dependencies..."
    npm install
else
    echo "Frontend dependencies already installed"
fi

echo -e "${GREEN}✓${NC} Frontend setup complete"
echo ""

# Create startup scripts
echo "Creating startup scripts..."

# Backend start script
cat > /workspaces/daytona/ai-engineer-app/backend/start.sh << 'EOF'
#!/bin/bash
cd /workspaces/daytona/ai-engineer-app/backend
source venv/bin/activate
python main.py
EOF

chmod +x /workspaces/daytona/ai-engineer-app/backend/start.sh

# Frontend start script
cat > /workspaces/daytona/ai-engineer-app/frontend/start.sh << 'EOF'
#!/bin/bash
cd /workspaces/daytona/ai-engineer-app/frontend
npm run dev
EOF

chmod +x /workspaces/daytona/ai-engineer-app/frontend/start.sh

# Combined start script
cat > /workspaces/daytona/ai-engineer-app/start-all.sh << 'EOF'
#!/bin/bash

echo "Starting AI Engineer..."
echo ""

# Start backend in background
echo "Starting backend on http://localhost:8000"
cd /workspaces/daytona/ai-engineer-app/backend
./start.sh &
BACKEND_PID=$!

# Wait for backend to start
sleep 3

# Start frontend
echo "Starting frontend on http://localhost:3000"
cd /workspaces/daytona/ai-engineer-app/frontend
./start.sh &
FRONTEND_PID=$!

echo ""
echo "=================================="
echo "AI Engineer is running!"
echo "=================================="
echo ""
echo "Backend:  http://localhost:8000"
echo "Frontend: http://localhost:3000"
echo ""
echo "Press Ctrl+C to stop all services"
echo ""

# Wait for Ctrl+C
trap 'echo ""; echo "Stopping services..."; kill $BACKEND_PID $FRONTEND_PID; exit 0' INT
wait
EOF

chmod +x /workspaces/daytona/ai-engineer-app/start-all.sh

echo -e "${GREEN}✓${NC} Startup scripts created"
echo ""

# Final instructions
echo "=================================="
echo "Setup Complete!"
echo "=================================="
echo ""
echo "To start the application:"
echo ""
echo "  cd /workspaces/daytona/ai-engineer-app"
echo "  ./start-all.sh"
echo ""
echo "Or start services separately:"
echo ""
echo "  # Terminal 1 - Backend"
echo "  cd /workspaces/daytona/ai-engineer-app/backend"
echo "  ./start.sh"
echo ""
echo "  # Terminal 2 - Frontend"
echo "  cd /workspaces/daytona/ai-engineer-app/frontend"
echo "  ./start.sh"
echo ""
echo "Then open http://localhost:3000 in your browser"
echo ""
echo "=================================="
