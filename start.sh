#!/bin/bash

# AI Resume Parser - Easy Start Script
# This script handles all setup and starts the application

set -e

echo "🚀 AI Resume Parser - Startup Script"
echo "===================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check Python version
echo -e "\n${YELLOW}Checking Python version...${NC}"
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "Python version: $python_version"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo -e "\n${YELLOW}Creating virtual environment...${NC}"
    python3 -m venv venv
fi

# Activate virtual environment
echo -e "\n${YELLOW}Activating virtual environment...${NC}"
source venv/bin/activate

# Install dependencies
echo -e "\n${YELLOW}Installing dependencies...${NC}"
pip install --upgrade pip
pip install -r requirements.txt

# Check for .env file
if [ ! -f ".env" ]; then
    echo -e "\n${YELLOW}Creating .env file from template...${NC}"
    cp .env .env 2>/dev/null || echo "Using default .env"
fi

# Create necessary directories
echo -e "\n${YELLOW}Creating necessary directories...${NC}"
mkdir -p logs uploads

# Start PostgreSQL if not running
echo -e "\n${YELLOW}Checking PostgreSQL...${NC}"
if ! docker ps | grep -q resume_postgres; then
    echo "Starting PostgreSQL database..."
    docker-compose up -d
    echo "Waiting for database to be ready..."
    sleep 5
else
    echo "PostgreSQL is already running ✓"
fi

# Download model (optional, will download on first use)
echo -e "\n${YELLOW}Checking Hugging Face model...${NC}"
echo "Model will be downloaded on first use (this may take a few minutes)"

# Start the application
echo -e "\n${GREEN}Starting AI Resume Parser...${NC}"
echo "API will be available at: http://localhost:8000"
echo "Documentation: http://localhost:8000/docs"
echo -e "\nPress Ctrl+C to stop\n"

# Run the application
python -m uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload