#!/bin/bash

# ============================================
# Agentic Development System - Stop Script
# ============================================

echo "🛑 Stopping Agentic Development System..."
echo ""

# Stop containers
docker-compose down || docker compose down

echo ""
echo "✅ All services stopped"
echo ""
echo "To start again, run:"
echo "  ./scripts/start.sh"
echo ""
