#!/bin/bash

# SRE Tier-0 Monitoring Dashboard - Run Script

echo "==================================="
echo "SRE Tier-0 Monitoring Dashboard"
echo "==================================="
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies if needed
if [ ! -f "venv/dependencies_installed" ]; then
    echo "Installing dependencies..."
    pip install -r requirements.txt
    touch venv/dependencies_installed
fi

# Create necessary directories
mkdir -p data/logs data/devices images templates

# Check for .env file
if [ ! -f ".env" ]; then
    echo "Creating .env file from .env.example..."
    cp .env.example .env
    echo "⚠️  Please edit .env file to add your Cohere API key (optional)"
fi

echo ""
echo "Starting application..."
echo "Dashboard will be available at: http://localhost:8000"
echo "Login credentials: admin / secret"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# Run the application
python backend/main.py
