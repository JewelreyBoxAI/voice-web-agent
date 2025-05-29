# JewelryBox AI Widget - Docker Deployment Script (PowerShell)
# Optimized for embeddable widget deployment in GHL and other platforms

Write-Host "🚀 Deploying JewelryBox AI Embeddable Widget..." -ForegroundColor Green

# Stop any existing containers
Write-Host "📦 Stopping existing containers..." -ForegroundColor Yellow
docker-compose down

# Build and start the optimized widget container
Write-Host "🔨 Building widget container..." -ForegroundColor Yellow
docker-compose up -d --build

# Wait for container to be ready
Write-Host "⏳ Waiting for widget to be ready..." -ForegroundColor Yellow
Start-Sleep -Seconds 10

# Health check
Write-Host "🔍 Performing health check..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8000/widget" -UseBasicParsing -TimeoutSec 5
    if ($response.StatusCode -eq 200) {
        Write-Host "✅ Widget deployment successful!" -ForegroundColor Green
        Write-Host ""
        Write-Host "📱 Embeddable Widget URLs:" -ForegroundColor Cyan
        Write-Host "   Widget Endpoint: http://localhost:8000/widget" -ForegroundColor White
        Write-Host "   Chat API:        http://localhost:8000/chat" -ForegroundColor White
        Write-Host "   Health Check:    http://localhost:8000/" -ForegroundColor White
        Write-Host ""
        Write-Host "🔗 For GHL Embedding:" -ForegroundColor Cyan
        Write-Host "   Use iframe: <iframe src=`"http://localhost:8000/widget`" width=`"400`" height=`"600`"></iframe>" -ForegroundColor White
        Write-Host ""
        Write-Host "⚠️  Production Notes:" -ForegroundColor Yellow
        Write-Host "   - Replace localhost with your domain" -ForegroundColor White
        Write-Host "   - Ensure HTTPS for production embedding" -ForegroundColor White
        Write-Host "   - Configure CORS for your domains" -ForegroundColor White
    }
} catch {
    Write-Host "❌ Widget deployment failed. Check logs:" -ForegroundColor Red
    docker-compose logs
}

Write-Host ""
Write-Host "📊 Container status:" -ForegroundColor Cyan
docker-compose ps 