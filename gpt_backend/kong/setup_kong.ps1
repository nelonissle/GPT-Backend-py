Write-Host "🛠️ Registering auth_service..."
Invoke-RestMethod -Method Post -Uri "http://localhost:8001/services/" -Body @{
    name = "auth_service"
    url  = "http://auth_service:8002/auth"
}

Write-Host "🔀 Creating route for auth_service..."
Invoke-RestMethod -Method Post -Uri "http://localhost:8001/services/auth_service/routes" -Body @{
    "paths[]" = "/auth"
}

Write-Host "🛠️ Registering chat_service..."
Invoke-RestMethod -Method Post -Uri "http://localhost:8001/services/" -Body @{
    name = "chat_service"
    url  = "http://chat_service:8003/chat"
}

Write-Host "🔀 Creating route for chat_service..."
Invoke-RestMethod -Method Post -Uri "http://localhost:8001/services/chat_service/routes" -Body @{
    "paths[]" = "/chat"
}

Write-Host "🔎 Please enter the Chat route ID (see output below):"
Invoke-RestMethod -Uri "http://localhost:8001/routes"

$CHAT_ROUTE_ID = Read-Host "🔎 Enter the Chat route ID for /chat"

if ([string]::IsNullOrWhiteSpace($CHAT_ROUTE_ID)) {
    Write-Host "❌ No route ID provided for /chat. Exiting."
    exit 1
}

Write-Host "🧩 Attaching JWT plugin to chat_service route..."
Invoke-RestMethod -Method Post -Uri "http://localhost:8001/routes/$CHAT_ROUTE_ID/plugins" -Body @{
    name = "jwt"
    "config.claims_to_verify[]" = "exp"
    "config.secret_is_base64" = "false"
    "config.key_claim_name" = "sub"
}

Write-Host "🛠️ Registering admin_service..."
Invoke-RestMethod -Method Post -Uri "http://localhost:8001/services" -Body @{
    name = "admin_service"
    url  = "http://admin_service:8004"
}

Write-Host "🔀 Creating /admin route..."
Invoke-RestMethod -Method Post -Uri "http://localhost:8001/services/admin_service/routes" -Body @{
    name = "admin_route"
    "paths[]" = "/admin"
    strip_path = "false"
}

Write-Host "🧩 Attaching JWT plugin to admin_route..."
Invoke-RestMethod -Method Post -Uri "http://localhost:8001/routes/admin_route/plugins" -Body @{
    name = "jwt"
    "config.claims_to_verify[]" = "exp"
}

Write-Host "📊 Enabling Prometheus monitoring plugin..."
Invoke-RestMethod -Method Post -Uri "http://localhost:8001/plugins" -Body @{
    name = "prometheus"
    "config.scrape_interval" = "5"
    "config.path" = "/metrics"
}

Write-Host "✅ Kong configuration complete!"

Write-Host "Shows all registered plugins:"
Invoke-RestMethod -Uri "http://localhost:8001/plugins"

Write-Host "Shows all registered services:"
Invoke-RestMethod -Uri "http://localhost:8001/services"