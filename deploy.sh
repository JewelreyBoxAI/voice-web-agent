#!/bin/bash

# JewelryBoxAI Deployment Script
echo "🔷 JewelryBoxAI Deployment Script"
echo "=================================="

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "❌ Error: .env file not found!"
    echo "Please create a .env file with your OpenAI API key:"
    echo "OPENAI_API_KEY=your_openai_api_key_here"
    echo "ALLOWED_ORIGINS=*"
    exit 1
fi

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Error: Docker is not running!"
    echo "Please start Docker and try again."
    exit 1
fi

# Build the Docker image
echo "🔨 Building Docker image..."
docker build -t jewelrybox-ai:latest .

if [ $? -ne 0 ]; then
    echo "❌ Error: Docker build failed!"
    exit 1
fi

# Stop and remove existing container if it exists
echo "🧹 Cleaning up existing container..."
docker stop jewelrybox-ai-bot 2>/dev/null || true
docker rm jewelrybox-ai-bot 2>/dev/null || true

# Run the container
echo "🚀 Starting JewelryBoxAI container..."
docker-compose up -d

if [ $? -eq 0 ]; then
    echo "✅ JewelryBoxAI is now running!"
    echo "🌐 Access the application at: http://localhost:8000"
    echo "💬 Chat widget available at: http://localhost:8000/widget"
    echo ""
    echo "📊 To view logs: docker-compose logs -f"
    echo "🛑 To stop: docker-compose down"
else
    echo "❌ Error: Failed to start the container!"
    exit 1
fi 