# GPT-Backend-py
 Backend for GPT app in python 

## Ausgangslage

### Ausgangslage der Micro Services

**Auth Service**

**chat Service**
Der Chat Service soll als schnittpunkt gelten von den anfragen des LLMs und des frontends hier wird also die Logik für 
die daten speicherung stattfinden also die funktion "Remember chats" so dass das LLM (das LLM muss ich noch auswählen entweder eines von Olma oder LM Studio also einen LLM das ich local herunterladen kann) das iel ist es die anfrage und das ergebniss von dem LLM in eine Mongo DB zu schreiben. Wichtig ist aber wenn ich mich anmelde oder registriere mit verschiedenen usern dan müssen die anfragen dem entsprechend in ein eigene db gespeichert werden also zb: ich registriere mich als nelo und schicke dan eine anfrage von meinem frontend u meinem backend dann muss im backend einen Collection mit dem namen des users erstellt werden und für jeden chat den ich mache (also es gibt dan die Funktion "New chat" so wie es sie in chatGPT gibt) das heisst wen ein neuere user sich registiert dan macht es automatisch einen neue collection für ihn mit dem nahmen und jeder neue chat soll dan eine Document sein mit dem namen des chats der name des chats sind immer die ersten drei wörter der ersten such anfrage. Wichtig ist das wen ich mich anmelde also bei einem bestehenden user anmelde ich dan einfach weiter an dieser db arbeite also das heisst das ich dan einfach weiter dokumente mit neuen chats erstelle für diese user collection. das gane muss mit JWT geschütt sein also ich melde/ logge mich im auth service an. Ich Benute dafür Kong API Gateway und fast api ich schicke dir aber noch den code vom auth Service.

## Ziele und Anforderungen

**Zwingende Anforderungen:**
- Python (FastAPI)
- Python Unit Tests 
- API Gateway (Kong)
- Läuft in Docker
- Authentifizierung
- MicroServices
- Produktions Standart
- Git WorkFlow
- Deploy auf Microk8s
- Frontend mit react typescript
- Konzept Schreiebn mit Vorgehen

**Optional:**
- DNS
- Desaster Recovery (velero)
- Multi CLuster
- Tiefer eingehende punkte im bereich Kubernetes
- Monitoring (Grafana, Elasticsearch und prometheus)
- Test Processe mit Kubernetes (END TO END Tests)
- Frontend Unit Tests
- Selenium
- Code COvgerage
- Patterns

# Entwicklungsumgebung
Um mit LLM's zu arbeiten, wird Ollama verwendet. LM Studio und https://github.com/open-webui/open-webui dienen als Hilfe.

## Ubuntu
### Notwendige Software
Ubuntu 24 LTS mit Docker und Microk8s

Ollama via https://ollama.com/download/
ollama run gemma3:1b (test prompt and exit mit /bye)
Clone repository
run gpt_backend/dev-local-init.sh

## Windows
### Notwendige Software
Windows 11 mit WSL 2
WSL 2 Ubuntu 24 LTS, systemd muss laufen (https://learn.microsoft.com/en-us/windows/wsl/systemd)
Docker Desktop

Für WSL Ubuntu:
! weitere Software siehe unter Ubuntu

Nur Windows:
Clone repository

## Environment variables

### Postgres Container
POSTGRES_DB = kong
POSTGRES_USER = kong
POSTGRES_PASSWORD = pwd1

### Kong and Kong Migration
POSTGRES_GPT_SERVICE_HOST ip
POSTGRES_GPT_SERVICE_PORT 5432
KONG_DATABASE = postgres
KONG_PG_DATABASE = kong
KONG_PG_HOST = POSTGRES_GPT_SERVICE_HOST
KONG_PG_PORT = POSTGRES_GPT_SERVICE_PORT
KONG_PG_USER = kong
KONG_PG_PASSWORD = pwd1

KONG_PROXY_ACCESS_LOG: Path for the proxy access log.
KONG_ADMIN_ACCESS_LOG: Path for the admin access log.
KONG_PROXY_ERROR_LOG: Path for the proxy error log.
KONG_ADMIN_ERROR_LOG: Path for the admin error log.
KONG_ADMIN_LISTEN: Address and port for the Admin API.
KONG_PROXY_LISTEN: Address and port for the Proxy.
KONG_LOG_LEVEL: Log level (notice, info, warn, etc.).
KONG_DECLARATIVE_CONFIG: Path to a declarative config file (for DB-less mode).


### Mongo
MONGO_INITDB_ROOT_USERNAME = root
MONGO_INITDB_ROOT_PASSWORD = pwd2


### Admin-service
MONGO_GPT_SERVICE_HOST = ip
MONGO_GPT_SERVICE_PORT = 27017
