#!/bin/bash

# AI Talk Travel Agent Startup Script

echo "🤖 Starting AI Talk Travel Agent..."
echo "=================================="

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3 first."
    exit 1
fi

# Check if .env file exists
if [ ! -f .env ]; then
    echo "⚠️  .env file not found. Creating from template..."
    if [ -f env.example ]; then
        cp env.example .env
        echo "📝 Please edit .env file and add your API keys before running again."
        echo "   Required: OPENAI_API_KEY"
        exit 1
    else
        echo "❌ env.example not found. Please create a .env file with your API keys."
        exit 1
    fi
fi

# Check if requirements are installed
echo "📦 Checking dependencies..."
if ! python3 -c "import fastapi, litellm, uvicorn" 2>/dev/null; then
    echo "📥 Installing dependencies..."
    pip3 install -r requirements.txt
fi

# Start the server
echo "🚀 Starting FastAPI server..."
echo "   Server will be available at: http://localhost:8000"
echo "   API docs will be available at: http://localhost:8000/docs"
echo ""
echo "   To use the console interface, open another terminal and run:"
echo "   python3 console_client.py"
echo ""
echo "   Press Ctrl+C to stop the server"
echo ""

python3 main.py
