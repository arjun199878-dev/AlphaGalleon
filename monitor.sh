#!/bin/bash

# AlphaGalleon System Monitor
# Real-time monitoring of all system components

set -euo pipefail

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

# Configuration
API_BASE_URL="${API_BASE_URL:-http://localhost:8000}"
CHECK_INTERVAL=5
FAILED_CHECKS=0
MAX_FAILURES=3

# Helper functions
print_header() {
    clear
    echo -e "${BLUE}╔════════════════════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║       AlphaGalleon System Monitor (Live)               ║${NC}"
    echo -e "${BLUE}╚════════════════════════════════════════════════════════╝${NC}"
    echo -e "${CYAN}Time: $(date '+%Y-%m-%d %H:%M:%S')${NC}"
    echo ""
}

check_service() {
    local name=$1
    local endpoint=$2
    local expected_code=${3:-200}
    
    local response=$(curl -s -o /dev/null -w "%{http_code}" "$API_BASE_URL$endpoint" 2>/dev/null || echo "connection_refused")
    
    if [ "$response" == "$expected_code" ]; then
        echo -e "${GREEN}✓${NC} $name ${GREEN}✓${NC}"
        return 0
    else
        echo -e "${RED}✗${NC} $name ${RED}[HTTP $response]${NC}"
        return 1
    fi
}

check_database() {
    local response=$(curl -s "$API_BASE_URL/health" 2>/dev/null | grep -o '"database":"[^"]*' | cut -d'"' -f4 || echo "unknown")
    
    if [ "$response" == "connected" ]; then
        echo -e "${GREEN}✓${NC} Database: ${GREEN}Connected${NC}"
        return 0
    else
        echo -e "${RED}✗${NC} Database: ${RED}$response${NC}"
        return 1
    fi
}

check_apis() {
    local google_api=$(curl -s "$API_BASE_URL/health" 2>/dev/null | grep -o '"google_api":"[^"]*' | cut -d'"' -f4 || echo "unknown")
    local upstox_api=$(curl -s "$API_BASE_URL/health" 2>/dev/null | grep -o '"upstox_api":"[^"]*' | cut -d'"' -f4 || echo "unknown")
    
    echo -e "  ${CYAN}External APIs:${NC}"
    [ "$google_api" == "available" ] && echo -e "    ${GREEN}✓${NC} Google Gemini API" || echo -e "    ${YELLOW}⚠${NC} Google Gemini API (offline)"
    [ "$upstox_api" == "available" ] && echo -e "    ${GREEN}✓${NC} Upstox API" || echo -e "    ${YELLOW}⚠${NC} Upstox API (offline)"
}

check_auth() {
    echo -e "${CYAN}  Authentication:${NC}"
    
    # Check if auth endpoint is working but don't test full signup (requires email)
    local response=$(curl -s -o /dev/null -w "%{http_code}" \
        -X POST "$API_BASE_URL/api/v1/auth/verify" \
        -H "Content-Type: application/json" \
        -d '{"token":"test"}' 2>/dev/null || echo "000")
    
    if [ "$response" != "000" ]; then
        echo -e "    ${GREEN}✓${NC} Auth endpoint responding"
    else
        echo -e "    ${RED}✗${NC} Auth endpoint not responding"
    fi
}

check_memory() {
    echo ""
    echo -e "${CYAN}System Resources:${NC}"
    
    if command -v docker &> /dev/null; then
        local backend_status=$(docker ps 2>/dev/null | grep -q "alphagalleon-backend\|backend-1" && echo "running" || echo "stopped")
        echo -e "  Backend Container: ${GREEN}$backend_status${NC}"
        
        if [ "$backend_status" == "running" ]; then
            local memory=$(docker stats --no-stream 2>/dev/null | tail -1 | awk '{print $7}' | sed 's/MiB//' || echo "?")
            echo -e "  Memory Usage: ${memory} MB"
        fi
    fi
}

check_performance() {
    echo ""
    echo -e "${CYAN}Performance Metrics:${NC}"
    
    local start_time=$(date +%s%N | cut -b1-13)
    curl -s "$API_BASE_URL/health" > /dev/null 2>&1 || true
    local end_time=$(date +%s%N | cut -b1-13)
    local response_time=$((end_time - start_time))
    
    if [ "$response_time" -lt 100 ]; then
        echo -e "  Response Time: ${GREEN}${response_time}ms${NC}"
    elif [ "$response_time" -lt 500 ]; then
        echo -e "  Response Time: ${YELLOW}${response_time}ms${NC}"
    else
        echo -e "  Response Time: ${RED}${response_time}ms${NC}"
    fi
}

check_endpoints() {
    echo ""
    echo -e "${CYAN}API Endpoints:${NC}"
    check_service "Health Check" "/health" || return 1
    check_service "Brain (Memo)" "/api/v1/brain/status" || return 1
    check_service "Doctor (Diagnostics)" "/api/v1/doctor/status" || return 1
    check_service "Architect (Portfolio)" "/api/v1/architect/status" || return 1
    check_service "Scout (Market Data)" "/api/v1/scout/status" || return 1
}

show_help() {
    echo -e "${BLUE}Usage: ./monitor.sh [OPTIONS]${NC}"
    echo ""
    echo "Options:"
    echo "  --url <URL>       API base URL (default: http://localhost:8000)"
    echo "  --interval <SEC>  Check interval in seconds (default: 5)"
    echo "  --once            Run checks once and exit"
    echo "  --help            Show this help message"
    echo ""
    echo "Examples:"
    echo "  ./monitor.sh                          # Monitor with defaults"
    echo "  ./monitor.sh --url http://api.example.com"
    echo "  ./monitor.sh --interval 10 --once"
}

# Parse arguments
once_mode=false
while [[ $# -gt 0 ]]; do
    case $1 in
        --url)
            API_BASE_URL="$2"
            shift 2
            ;;
        --interval)
            CHECK_INTERVAL="$2"
            shift 2
            ;;
        --once)
            once_mode=true
            shift
            ;;
        --help)
            show_help
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            show_help
            exit 1
            ;;
    esac
done

# Main monitoring loop
while true; do
    print_header
    
    echo -e "${CYAN}Checking services at: ${API_BASE_URL}${NC}"
    echo ""
    
    # Run all checks
    if check_service "API Server" "/health"; then
        check_database
        check_apis
        check_auth
        check_endpoints
        check_memory
        check_performance
        
        FAILED_CHECKS=0
        echo ""
        echo -e "${GREEN}═══════════════════════════════════════════════════════${NC}"
        echo -e "${GREEN}All systems operational${NC}"
        echo -e "${GREEN}═══════════════════════════════════════════════════════${NC}"
    else
        FAILED_CHECKS=$((FAILED_CHECKS + 1))
        echo ""
        echo -e "${RED}═══════════════════════════════════════════════════════${NC}"
        echo -e "${RED}Connection failed ($FAILED_CHECKS/$MAX_FAILURES)${NC}"
        echo -e "${RED}═══════════════════════════════════════════════════════${NC}"
        
        if [ $FAILED_CHECKS -ge $MAX_FAILURES ]; then
            echo -e "${RED}✗ Maximum failures reached. Exiting.${NC}"
            exit 1
        fi
    fi
    
    if [ "$once_mode" = true ]; then
        exit 0
    fi
    
    sleep "$CHECK_INTERVAL"
done
