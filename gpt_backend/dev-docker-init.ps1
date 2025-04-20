# Init script for local development in PowerShell

Write-Host "Creating .env file..."

# Copy template-dotenv-secrets.txt to .env
Copy-Item -Path "template-dotenv-secrets.txt" -Destination ".env" -Force

# Append the contents of template-dotenv.txt to .env
Get-Content -Path "template-dotenv.txt" | Add-Content -Path ".env"

# Replace the values in .env with the values from the secrets file
Get-Content -Path "template-dotenv-secrets.txt" | ForEach-Object {
    $line = $_
    $key, $value = $line -split '=', 2
    (Get-Content -Path ".env") -replace "^\s*$key=.*", "$key=$value" | Set-Content -Path ".env"
}

# Start Docker Compose
docker-compose up -d