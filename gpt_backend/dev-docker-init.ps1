# Init script for local development in PowerShell

Write-Host "Creating .env file..."

# Copy template-dotenv-secrets.txt to .env
Copy-Item -Path "template-dotenv.txt" -Destination ".env" -Force

# Start Docker Compose
#docker-compose up -d