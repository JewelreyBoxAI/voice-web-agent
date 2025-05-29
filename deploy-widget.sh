#!/bin/bash

# JewelryBox AI Widget - Docker Deployment Script
# Optimized for embeddable widget deployment in GHL and other platforms

echo "🚀 Deploying JewelryBox AI Embeddable Widget..."

# Stop any existing containers
echo "📦 Stopping existing containers..."
docker-compose down

# Build and start the optimized widget container
echo "🔨 Building widget container..."
docker-compose up -d --build

# Wait for container to be ready
echo "⏳ Waiting for widget to be ready..."
sleep 10

# Health check
echo "🔍 Performing health check..."
if curl -f http://localhost:8000/widget > /dev/null 2>&1; then
    echo "✅ Widget deployment successful!"
    echo ""
    echo "📱 Embeddable Widget URLs:"
    echo "   Widget Endpoint: http://localhost:8000/widget"
    echo "   Chat API:        http://localhost:8000/chat"
    echo "   Health Check:    http://localhost:8000/"
    echo ""
    echo "🔗 For GHL Embedding:"
    echo "   Use iframe: <iframe src=\"http://localhost:8000/widget\" width=\"400\" height=\"600\"></iframe>"
    echo ""
    echo "⚠️  Production Notes:"
    echo "   - Replace localhost with your domain"
    echo "   - Ensure HTTPS for production embedding"
    echo "   - Configure CORS for your domains"
else
    echo "❌ Widget deployment failed. Check logs:"
    docker-compose logs
fi

echo "📊 Container status:"
docker-compose ps 