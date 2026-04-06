#!/bin/bash

# AlphaGalleon Scaled Deployment Quick Start
# Deploys with load balancing, caching, and monitoring for 10,000+ users
# Usage: bash scale-start.sh [stop|restart|logs|status]

set -euo pipefail

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Configuration
COMMAND="${1:-start}"

echo -e "${BLUE}╔════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║   AlphaGalleon Scaled Deployment (10,000+ users)       ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════╝${NC}"
echo ""

# Check for prerequisites
if ! command -v docker &> /dev/null; then
    echo -e "${RED}✗ Docker not found. Please install Docker first.${NC}"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}✗ Docker Compose not found.${NC}"
    exit 1
fi

# Check for required files
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}⚠ .env file not found. Creating from .env.example...${NC}"
    if [ ! -f ".env.example" ]; then
        echo -e "${RED}✗ .env.example not found${NC}"
        exit 1
    fi
    cp .env.example .env
    echo -e "${YELLOW}Please edit .env with your API keys before proceeding.${NC}"
    exit 1
fi

if [ ! -f "docker-compose.scale.yml" ]; then
    echo -e "${RED}✗ docker-compose.scale.yml not found${NC}"
    exit 1
fi

if [ ! -f "nginx-lb.conf" ]; then
    echo -e "${RED}✗ nginx-lb.conf not found${NC}"
    exit 1
fi

case "$COMMAND" in
    start)
        echo -e "${GREEN}🚀 Starting scaled deployment...${NC}"
        echo ""
        echo -e "${BLUE}Components being started:${NC}"
        echo "  • Nginx Load Balancer (port 80)"
        echo "  • 3x Backend instances (port 8000)"
        echo "  • Redis Cache (port 6379)"
        echo "  • Prometheus Monitoring (port 9090)"
        echo ""
        
        docker-compose \
            -f docker-compose.yml \
            -f docker-compose.scale.yml \
            up -d
        
        echo -e "${GREEN}✓ Containers started${NC}"
        echo ""
        echo "Waiting for services to become healthy (30 seconds)..."
        sleep 30
        
        echo -e "${BLUE}Verifying deployment...${NC}"
        
        # Check load balancer
        if curl -s http://localhost/health > /dev/null 2>&1; then
            echo -e "${GREEN}✓ Nginx Load Balancer${NC}"
        else
            echo -e "${RED}✗ Nginx Load Balancer not responding${NC}"
        fi
        
        # Check Redis
        if docker-compose exec redis redis-cli ping > /dev/null 2>&1; then
            echo -e "${GREEN}✓ Redis Cache${NC}"
        else
            echo -e "${RED}✗ Redis Cache not responding${NC}"
        fi
        
        # Check backend instances
        for i in 1 2 3; do
            if curl -s http://localhost:800$i/health > /dev/null 2>&1 2>&1; then
                echo -e "${GREEN}✓ Backend $i${NC}"
            fi
        done
        
        echo ""
        echo -e "${GREEN}═══════════════════════════════════════════════════════${NC}"
        echo -e "${GREEN}Scaled deployment is RUNNING!${NC}"
        echo -e "${GREEN}═══════════════════════════════════════════════════════${NC}"
        echo ""
        echo "📊 Access Points:"
        echo "  • API: http://localhost (Load Balancer)"
        echo "  • Metrics: http://localhost:9090 (Prometheus)"
        echo "  • Cache: redis://localhost:6379"
        echo ""
        echo "🧪 Test the deployment:"
        echo "  bash test-deployment.sh"
        echo ""
        echo "📈 Monitor in real-time:"
        echo "  ./monitor.sh"
        echo ""
        echo "📖 View load balancer logs:"
        echo "  docker-compose logs -f nginx-lb"
        echo ""
        ;;
    
    stop)
        echo -e "${YELLOW}⏸ Stopping scaled deployment...${NC}"
        docker-compose \
            -f docker-compose.yml \
            -f docker-compose.scale.yml \
            down
        echo -e "${GREEN}✓ Stopped${NC}"
        ;;
    
    restart)
        echo -e "${YELLOW}🔄 Restarting scaled deployment...${NC}"
        docker-compose \
            -f docker-compose.yml \
            -f docker-compose.scale.yml \
            restart
        echo -e "${GREEN}✓ Restarted${NC}"
        sleep 5
        echo ""
        bash "$0" status
        ;;
    
    logs)
        service="${2:-}"
        if [ -z "$service" ]; then
            docker-compose \
                -f docker-compose.yml \
                -f docker-compose.scale.yml \
                logs -f
        else
            docker-compose \
                -f docker-compose.yml \
                -f docker-compose.scale.yml \
                logs -f "$service"
        fi
        ;;
    
    status)
        echo -e "${BLUE}Container Status:${NC}"
        docker-compose \
            -f docker-compose.yml \
            -f docker-compose.scale.yml \
            ps
        
        echo ""
        echo -e "${BLUE}Resource Usage:${NC}"
        docker stats --no-stream | head -10
        
        echo ""
        echo -e "${BLUE}Cache Statistics:${NC}"
        docker-compose exec redis redis-cli info stats 2>/dev/null || echo "Redis not available"
        
        echo ""
        echo -e "${BLUE}Health Check:${NC}"
        if curl -s http://localhost/health | jq . 2>/dev/null; then
            echo -e "${GREEN}✓ API responding${NC}"
        else
            echo -e "${RED}✗ API not responding${NC}"
        fi
        ;;
    
    *)
        echo -e "${YELLOW}Usage: $0 [start|stop|restart|logs|status]${NC}"
        echo ""
        echo "Examples:"
        echo "  bash $0 start              # Start scaled deployment"
        echo "  bash $0 stop               # Stop all containers"
        echo "  bash $0 logs               # View all logs"
        echo "  bash $0 logs nginx-lb      # View load balancer logs"
        echo "  bash $0 status             # Show container status"
        exit 1
        ;;
esac
