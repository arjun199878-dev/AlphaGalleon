#!/bin/bash

# AlphaGalleon Quick Start Script
# Run this to setup and run the entire application

set -e

echo "🚀 AlphaGalleon Quick Start"
echo "=========================================="

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check prerequisites
echo -e "\n${YELLOW}📋 Checking prerequisites...${NC}"

if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 not found. Please install Python 3.10+${NC}"
    exit 1
fi

if ! command -v node &> /dev/null; then
    echo -e "${RED}❌ Node.js not found. Please install Node.js 18+${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Prerequisites OK${NC}"

# Setup Python Backend
echo -e "\n${YELLOW}🧠 Setting up Backend...${NC}"

cd alphagalleon-backend

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Create .env if it doesn't exist
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}📝 Create .env file with your API keys${NC}"
    cp .env.example .env
    echo "Please edit alphagalleon-backend/.env with your API keys"
    echo "Then re-run this script"
    exit 1
fi

# Install dependencies
echo "Installing Python dependencies..."
pip install -q -r requirements.txt

echo -e "${GREEN}✅ Backend ready${NC}"

# Setup Mobile App
echo -e "\n${YELLOW}📱 Setting up Mobile App...${NC}"

cd ../mobile

if [ ! -d "node_modules" ]; then
    echo "Installing mobile dependencies..."
    npm install --silent
fi

echo -e "${GREEN}✅ Mobile app ready${NC}"

# Setup Admin Dashboard
echo -e "\n${YELLOW}🎨 Setting up Admin Dashboard...${NC}"

cd ../admin-dashboard

if [ ! -d "node_modules" ]; then
    echo "Installing dashboard dependencies..."
    npm install --silent
fi

echo -e "${GREEN}✅ Admin dashboard ready${NC}"

# Back to root
cd ..

echo -e "\n${GREEN}=========================================="
echo "✅ Setup Complete!"
echo "=========================================${NC}"

echo -e "\n${YELLOW}To start the application, run in separate terminals:${NC}\n"

echo "1. Backend (API):"
echo "   cd alphagalleon-backend"
echo "   source venv/bin/activate"
echo "   python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"

echo -e "\n2. Mobile App:"
echo "   cd mobile"
echo "   npm start"

echo -e "\n3. Admin Dashboard:"
echo "   cd admin-dashboard"
echo "   npm run dev"

echo -e "\n${YELLOW}Note:${NC}"
echo "- Update your computer's IP in mobile/src/api/config.ts"
echo "- Make sure phone and computer are on the same WiFi"
echo "- Get API keys from Google, Upstox, and Telegram"

echo -e "\n${GREEN}Happy building! 🎉${NC}"
