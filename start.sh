#!/bin/bash

# AlphaGalleon Quick Start Script
# This script sets up and runs AlphaGalleon locally or in production

set -euo pipefail

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Configuration
ENVIRONMENT="${1:-development}"
PORT="${PORT:-8000}"

echo -e "${BLUE}═════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}    AlphaGalleon - Institutional Investment Banker${NC}"
echo -e "${BLUE}═════════════════════════════════════════════════════════${NC}"
echo ""

# Check for Docker
if ! command -v docker &> /dev/null; then
    echo -e "${RED}✗ Docker is not installed. Please install Docker first.${NC}"
    echo "  https://docs.docker.com/get-docker/"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}✗ Docker Compose is not installed.${NC}"
    echo "  https://docs.docker.com/compose/install/"
    exit 1
fi

echo -e "${GREEN}✓ Docker and Docker Compose are installed${NC}"
echo ""

# Check for .env file
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}⚠ .env file not found. Creating from .env.example...${NC}"
    if [ -f ".env.example" ]; then
        cp .env.example .env
        echo -e "${YELLOW}Please edit .env with your API keys before running.${NC}"
        echo ""
        read -p "Press Enter to continue with defaults or Ctrl+C to edit .env first..."
    else
        echo -e "${RED}✗ .env.example not found${NC}"
        exit 1
    fi
fi

echo -e "${BLUE}Starting AlphaGalleon (Environment: $ENVIRONMENT)${NC}"
echo ""

case "$ENVIRONMENT" in
    development)
        echo -e "${BLUE}🚀 Starting development server...${NC}"
        docker-compose up --build
        ;;
    
    production)
        echo -e "${BLUE}🚀 Starting production server...${NC}"
        docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
        
        echo -e "${GREEN}✓ Production deployment started${NC}"
        echo ""
        echo -e "${BLUE}Next steps:${NC}"
        echo "1. Verify backend is running: curl http://localhost:8000/health"
        echo "2. Run deployment tests: bash test-deployment.sh"
        echo "3. Configure Nginx: Update nginx.prod.conf with your domain"
        echo "4. Setup SSL certificate: certbot certonly -d <your-domain>"
        echo ""
        ;;
    
    test)
        echo -e "${BLUE}🧪 Running tests...${NC}"
        bash test-deployment.sh
        ;;
    
    *)
        echo -e "${RED}Unknown environment: $ENVIRONMENT${NC}"
        echo "Usage: ./start.sh [development|production|test]"
        exit 1
        ;;
esac
