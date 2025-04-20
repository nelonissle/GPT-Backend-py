# Init script for local development in PowerShell

Write-Host "Creating .env file..."

# Copy template-dotenv-secrets.txt to .env
Copy-Item -Path "template-dotenv-secrets.txt" -Destination ".env" -Force

# Append the contents of template-dotenv.txt to .env
Get-Content -Path "template-dotenv.txt" | Add-Content -Path ".env"

# Start Docker Compose
docker-compose up -d