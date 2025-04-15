# Navigate to your project directory if not already there
Set-Location $PSScriptRoot

Write-Host "🟢 Building Docker Images and Running Docker Compose..." -ForegroundColor Green
docker compose up --build -d

# Wait for services to initialize
$waitTime = 10
Write-Host "⏳ Waiting for $waitTime seconds to allow services to initialize..." -ForegroundColor Yellow
Start-Sleep -Seconds $waitTime

# Check running containers
Write-Host "📌 Running Docker Containers:" -ForegroundColor Cyan
docker ps

# Check MongoDB connectivity and list databases
Write-Host "📌 MongoDB Databases:" -ForegroundColor Cyan
try {
    docker exec mongo_db mongosh -u mongoadmin -p secret --eval "show dbs"
} catch {
    Write-Host "❌ MongoDB is not reachable." -ForegroundColor Red
}

# Check Kong API Gateway Health
Write-Host "📌 Checking Kong API Gateway Status:" -ForegroundColor Cyan
try {
    Invoke-RestMethod http://localhost:8001/status
} catch {
    Write-Host "❌ Kong API Gateway is not reachable." -ForegroundColor Red
}

# Check Microservices
Write-Host "📌 Auth Service Health Check:" -ForegroundColor Cyan
try {
    Invoke-RestMethod http://localhost:8002
} catch {
    Write-Host "❌ Auth Service is not reachable." -ForegroundColor Red
}

Write-Host "📌 Chat Service Health Check:" -ForegroundColor Cyan
try {
    Invoke-RestMethod http://localhost:8003
} catch {
    Write-Host "❌ Chat Service is not reachable." -ForegroundColor Red
}

# To stop and remove containers, uncomment the line below:
# docker compose down