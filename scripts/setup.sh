#!/bin/bash

# ============================================
# Agentic Development System - Setup Script
# ============================================

set -e

echo "🤖 Agentic Development System Setup"
echo "===================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker is not installed${NC}"
    echo "Please install Docker from https://docs.docker.com/get-docker/"
    exit 1
fi

echo -e "${GREEN}✓ Docker is installed${NC}"

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    echo -e "${RED}❌ Docker Compose is not installed${NC}"
    echo "Please install Docker Compose from https://docs.docker.com/compose/install/"
    exit 1
fi

echo -e "${GREEN}✓ Docker Compose is installed${NC}"

# Check if .env file exists
if [ ! -f .env ]; then
    echo ""
    echo -e "${YELLOW}⚠ .env file not found${NC}"
    echo "Creating .env from .env.example..."
    cp .env.example .env
    echo -e "${GREEN}✓ .env file created${NC}"
    echo ""
    echo -e "${YELLOW}⚠ IMPORTANT: Please edit .env and add your API keys:${NC}"
    echo "  - LLM_API_KEY (OpenAI, Anthropic, or compatible)"
    echo "  - DAYTONA_API_KEY (from https://app.daytona.io/dashboard/keys)"
    echo "  - CODE_SERVER_PASSWORD (choose a strong password)"
    echo ""
    read -p "Press Enter to open .env for editing..."
    ${EDITOR:-nano} .env
else
    echo -e "${GREEN}✓ .env file exists${NC}"
fi

# Validate required environment variables
echo ""
echo "Validating configuration..."

source .env

if [ -z "$LLM_API_KEY" ] || [ "$LLM_API_KEY" = "your-llm-api-key-here" ]; then
    echo -e "${RED}❌ LLM_API_KEY is not set in .env${NC}"
    exit 1
fi

if [ -z "$DAYTONA_API_KEY" ] || [ "$DAYTONA_API_KEY" = "your-daytona-api-key-here" ]; then
    echo -e "${RED}❌ DAYTONA_API_KEY is not set in .env${NC}"
    exit 1
fi

if [ -z "$CODE_SERVER_PASSWORD" ] || [ "$CODE_SERVER_PASSWORD" = "changeme" ] || [ "$CODE_SERVER_PASSWORD" = "changeme123" ]; then
    echo -e "${YELLOW}⚠ Warning: CODE_SERVER_PASSWORD is using default value${NC}"
    echo "  Please set a strong password in .env"
fi

echo -e "${GREEN}✓ Configuration validated${NC}"

# Create workspace directory
echo ""
echo "Creating workspace directory..."
mkdir -p workspace
echo -e "${GREEN}✓ Workspace directory created${NC}"

# Pull Docker images
echo ""
echo "Pulling Docker images (this may take a few minutes)..."
docker-compose pull || docker compose pull

echo -e "${GREEN}✓ Docker images pulled${NC}"

# Build custom images
echo ""
echo "Building application containers..."
docker-compose build || docker compose build

echo -e "${GREEN}✓ Containers built successfully${NC}"

# Setup complete
echo ""
echo "============================================"
echo -e "${GREEN}✅ Setup Complete!${NC}"
echo "============================================"
echo ""
echo "To start the system, run:"
echo "  ./scripts/start.sh"
echo ""
echo "Or manually with:"
echo "  docker-compose up -d"
echo ""
echo "Access the interface at:"
echo "  http://localhost"
echo ""
echo "VS Code (standalone):"
echo "  http://localhost:${CODE_SERVER_PORT:-8080}"
echo ""
echo "Backend API:"
echo "  http://localhost:${BACKEND_PORT:-3001}"
echo ""
