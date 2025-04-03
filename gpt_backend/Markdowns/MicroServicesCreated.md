# Doku for the Creation of each service

## Create the Main Project Directory
```bash
mkdir gpt_backend
cd gpt_backend
```

## Create Docker Compose & Kong folders
```bash
# Create docker-compose.yml
New-Item -Path docker-compose.yml -ItemType File

# Create the kong directory and kong.yml inside it
New-Item -Path kong -ItemType Directory
New-Item -Path kong/kong.yml -ItemType File
```

## Create the AuthService
```bash
# AuthService setup
New-Item -Path auth_service/app -ItemType Directory -Force
New-Item auth_service/Dockerfile
New-Item auth_service/requirements.txt
New-Item auth_service/.env
New-Item auth_service/auth.db
New-Item auth_service/app/main.py
New-Item auth_service/app/database.py
```

## Create the ChatService
```bash
# ChatService setup
New-Item -Path chat_service/app -ItemType Directory -Force
New-Item chat_service/Dockerfile
New-Item chat_service/requirements.txt
New-Item chat_service/.env
New-Item chat_service/app/main.py
New-Item chat_service/app/database.py
```

# Final Directory Check

**For Detaild View**
```bash
Get-ChildItem -Recurse
```

**For Tree View run:**
```bash
tree .
```

