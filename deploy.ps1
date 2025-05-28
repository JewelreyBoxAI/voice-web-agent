# JewelryBoxAI Deployment Script for Windows
Write-Host "🔷 JewelryBoxAI Deployment Script" -ForegroundColor Cyan
Write-Host "==================================" -ForegroundColor Cyan

# Check if .env file exists
if (-not (Test-Path ".env")) {
    Write-Host "❌ Error: .env file not found!" -ForegroundColor Red
    Write-Host "Please create a .env file with your OpenAI API key:" -ForegroundColor Yellow
    Write-Host "OPENAI_API_KEY=your_openai_api_key_here" -ForegroundColor Yellow
    Write-Host "ALLOWED_ORIGINS=*" -ForegroundColor Yellow
    exit 1
}

# Check if Docker is running
try {
    docker info | Out-Null
} catch {
    Write-Host "❌ Error: Docker is not running!" -ForegroundColor Red
    Write-Host "Please start Docker Desktop and try again." -ForegroundColor Yellow
    exit 1
}

# Build the Docker image
Write-Host "🔨 Building Docker image..." -ForegroundColor Green
docker build -t jewelrybox-ai:latest .

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Error: Docker build failed!" -ForegroundColor Red
    exit 1
}

# Stop and remove existing container if it exists
Write-Host "🧹 Cleaning up existing container..." -ForegroundColor Yellow
docker stop jewelrybox-ai-bot 2>$null
docker rm jewelrybox-ai-bot 2>$null

# Run the container
Write-Host "🚀 Starting JewelryBoxAI container..." -ForegroundColor Green
docker-compose up -d

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ JewelryBoxAI is now running!" -ForegroundColor Green
    Write-Host "🌐 Access the application at: http://localhost:8000" -ForegroundColor Cyan
    Write-Host "💬 Chat widget available at: http://localhost:8000/widget" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "📊 To view logs: docker-compose logs -f" -ForegroundColor Yellow
    Write-Host "🛑 To stop: docker-compose down" -ForegroundColor Yellow
} else {
    Write-Host "❌ Error: Failed to start the container!" -ForegroundColor Red
    exit 1
} 