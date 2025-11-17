#!/bin/bash

# ============================================
# Agentic Development System - Start Script
# ============================================

set -e

echo "🤖 Starting Agentic Development System..."
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo "❌ .env file not found!"
    echo "Run ./scripts/setup.sh first"
    exit 1
fi

# Start containers
echo "Starting Docker containers..."
docker-compose up -d || docker compose up -d

echo ""
echo "Waiting for services to be healthy..."
sleep 5

# Check if services are running
BACKEND_STATUS=$(docker-compose ps -q backend | xargs docker inspect -f '{{.State.Status}}' || echo "not running")
FRONTEND_STATUS=$(docker-compose ps -q frontend | xargs docker inspect -f '{{.State.Status}}' || echo "not running")
NGINX_STATUS=$(docker-compose ps -q nginx | xargs docker inspect -f '{{.State.Status}}' || echo "not running")
CODE_STATUS=$(docker-compose ps -q code-server | xargs docker inspect -f '{{.State.Status}}' || echo "not running")

echo ""
echo "Service Status:"
echo "  Backend:     $BACKEND_STATUS"
echo "  Frontend:    $FRONTEND_STATUS"
echo "  Code Server: $CODE_STATUS"
echo "  Nginx:       $NGINX_STATUS"
echo ""

if [ "$BACKEND_STATUS" = "running" ] && [ "$FRONTEND_STATUS" = "running" ] && [ "$NGINX_STATUS" = "running" ]; then
    echo "✅ All services are running!"
    echo ""
    echo "🌐 Access the interface at:"
    echo "   http://localhost"
    echo ""
    echo "📊 View logs with:"
    echo "   docker-compose logs -f"
    echo ""
    echo "🛑 Stop the system with:"
    echo "   ./scripts/stop.sh"
    echo ""
else
    echo "⚠ Some services may not be running properly"
    echo "Check logs with: docker-compose logs"
fi
