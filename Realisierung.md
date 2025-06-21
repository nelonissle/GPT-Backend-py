# Teil 4 Realisierung

Für die Realisierung habe ich eine Arbeitsumgebung aufgebaut, diese besteht aus dem Sourcecode (in github) und der Entwicklungsumgebung. Ich entwickle unter Windows 11 oder Windows 11 Subsystem for Linux (WSL). Unter Windows 11 nutze ich ein paar Powershell Scripts (.ps1) um arbeiten zu erleichtern, unter WSL, in den Containers nutze ich Unix Shell Scripts (.sh).

## Struktur Sourcecode

Dieses Repository enthält eine containerisierte KI Chat Anwendung mit Kubernetes-Deployment-Konfigurationen. Die Struktur ist in zwei Hauptbereiche unterteilt:

1. **Anwendungscode** (`gpt_backend/`) - Python-basierte Microservices
2. **Kubernetes-Konfigurationen** (`kub-*/`) - Helm Charts und Deployment-Skripte

---

## 1. Anwendungscode (`gpt_backend/`)

### Architektur
Das Backend folgt einer **Microservices-Architektur** mit den folgenden Services:

### 1.1 Admin Service (`gpt_backend/admin_service/`)
```
admin_service/
├── Dockerfile                 # Python 3.13 Alpine Container
├── requirements.txt           # Python Dependencies
├── app/
│   ├── main.py               # FastAPI Hauptanwendung
│   ├── setup_kong.sh         # Kong Gateway Konfigurationsskript
│   └── ...
└── logs/                     # Log-Verzeichnis (Volume Mount)
```

**Zweck:** Administrations-API für Kong Gateway Setup und Konfiguration
- **Port:** 8004
- **Framework:** FastAPI + Uvicorn
- **Besonderheiten:** Enthält Kong-Setup-Skripte für Service-Registrierung für die Initialisierung einer Neuinstallation

### 1.2 Auth Service (`gpt_backend/auth_service/`)
```
auth_service/
├── Dockerfile
├── requirements.txt
├── app/
│   ├── main.py               # Authentication API
│   └── ...
└── logs/
```

**Zweck:** Authentifizierung und Autorisierung
- **Port:** 8002
- **Framework:** FastAPI + Uvicorn
- **Features:** JWT Token Management

### 1.3 Chat Service (`gpt_backend/chat_service/`)
```
chat_service/
├── Dockerfile
├── requirements.txt
├── app/
│   ├── main.py               # Chat API
│   └── ...
└── logs/
```

**Zweck:** Chat-Interface für GPT/LLM-Integration
- **Port:** 8003
- **Framework:** FastAPI
- **Integration:** Ollama/LLM Services

### 1.5 Kong Service (`gpt_backend/chat_service/`)
Dies sind nur Dateien für die Konfiguration von Kong.

### 1.6 Monitoring Services (`gpt_backend/monitoring/`)
Dies sind Arbeitsdokumente welche ich für die Realisierung verwendete.

### 1.7 Ollama (`gpt_backend/ollama/`)
Hilfestellungen für die automatisierte Erstellung von einem einfachen LLM innerhalb von ollama. Dies wird nur im lokalen und Docker Umfeld verwendet. Im Kubernetes erstelle ich alles über API calls nach dem erfolgreichen Start.

### 1.8 Dokumentation (`gpt_backend/Markdowns/`)
Dies sind Arbeitsdokumente welche ich für die Realisierung verwendete.

### 1.9 Entwicklungstools
- **`dev-local-init.sh`** - Lokale Entwicklungsumgebung Setup um lokale die Python Services zu starten
- **`dev-docker-init.sh`** - Lokale Entwicklungsumgebung Setup um den docker-compose zu starten
- **`docker-compose.yml`** - Lokale Container-Orchestrierung

---

## 2. Kubernetes-Konfigurationen (`kub-*/`)

### 2.1 Cluster Management (`kub-cluster/`)
```
kub-cluster/
├── kub-deploy.sh             # Hauptdeployment-Skript
├── kub-ports.sh              # Port-Forwarding für Services
├── kub-list.sh               # Status-Monitoring
├── ingress-extern.yaml       # Ingress Controller NodePort Konfiguration
└── kub-metallb.sh            # MetalLB LoadBalancer Setup
```

**Zweck:** Cluster-weite Konfiguration und Management
- **Ingress:** NGINX Ingress Controller mit NodePort (30800, 30801, 31434)
- **LoadBalancer:** MetalLB für externe Service-Exposition
- **Monitoring:** Überwachung von Deployments und Services

### 2.2 GPT Backend Services (`kub-gpt/`)
```
kub-gpt/
├── Chart.yaml                # Helm Chart Definition
├── values.yaml               # Standard-Konfiguration
├── kub-deploy.sh             # Deployment-Skript
├── kub-shell.sh              # Admin Pod Shell-Zugang
├── templates/
│   ├── deployment.yaml       # Kubernetes Deployments
│   ├── service.yaml          # ClusterIP Services
│   ├── ingress.yaml          # Ingress Routing
│   ├── secret.yaml           # Secrets Management
│   └── pvc.yaml              # Persistent Volume Claims
└── charts/
    ├── kong/                 # Kong Gateway Helm Chart
    │   ├── templates/
    │   │   ├── kong-deployment.yaml
    │   │   ├── kong-service.yaml
    │   │   ├── kong-ingress.yaml
    │   │   └── kong-migrations.yaml
    │   └── values.yaml
    ├── postgres/             # PostgreSQL Helm Chart
    └── mongo/                # MongoDB Helm Chart
```

**Services:**
- **Kong Gateway** (Port 8000/8001) - API Gateway und Proxy
- **PostgreSQL** - Kong Gateway Datenbank
- **MongoDB** - Anwendungsdatenbank
- **Admin/Auth/Chat Services** - Microservices

### 2.3 LLM Services (`kub-llm/`)
Dies umfasst Ollama.
```
kub-llm/
├── Chart.yaml
├── values.yaml
├── kub-deploy.sh
├── kub-curl.sh               # API-Tests für Ollama
└── charts/
    └── ollama/               # Ollama LLM Service
        ├── templates/
        │   ├── deployment.yaml
        │   ├── service.yaml
        │   └── ingress.yaml
        └── values.yaml
```

**Zweck:** Large Language Model Services
- **Ollama** (Port 11434) - LLM API Server
- **Model:** TinyLlama/Gemma3 Integration
- **Storage:** Persistent Volumes für Modelle

---

## 3. Netzwerk-Architektur

### 3.1 Service-Kommunikation

```
┌─────────────────┐
│  Internet       │
│  Browser App    │
│  (Frontend)     │
└─────────┬───────┘
          │ HTTP/HTTPS
          │ Port 8000
          ▼
┌─────────────────┐
│  Kong Gateway   │
│  API Proxy      │
│  Port 8000      │
└─────────┬───────┘
          │ Internal
          │ Service Call
          │ Port 8003
          ▼
┌─────────────────┐     ┌─────────────────┐
│  Chat Service   │────▶│    MongoDB      │
│  FastAPI        │     │  Datenbank      │
│  Port 8003      │     │  Port 27017     │
└─────────┬───────┘     └─────────────────┘
          │ HTTP API Call
          │ Port 11434
          ▼
┌─────────────────┐
│  Ollama LLM     │
│  AI Service     │
│  Port 11434     │
└─────────────────┘
```

### 3.2 Kubernetes-Kommunikation
In Kubernetes ist die Netzwerkkommunikation sehr komplex. Es braucht zusätzlich einen Ingress Controller und ein Loadbalacer um die internen
IP Adressen und Ports von ausserhalb des Kubernetes anzusprechen. Ich habe auch Kubernetes in die drei Teile Ollama, meine GPT services und Monitoring aufgeteilt. So könnte ich es auf verschiedene Rechner verteilen.

#### 3.2.1 Port-Mapping
- **8000** → Kong Proxy (via LoadBalancer/NodePort 30800)
- **8001** → Kong Admin (via LoadBalancer/NodePort 30801)
- **11434** → Ollama API (via LoadBalancer/NodePort 31434)

#### 3.2.2 Ingress-Routing
- **kong.local** → Kong Gateway Service
- **chat.local** → Chat Service
- **ollama.local** → Ollama Service

---

## 4. Entwicklungsumgebungen
In meinem Projekt setze ich Mongo DB, Kong und Ollama ein. Es ist am einfachsten diese 3 Dienste mit einem Docker Container zu betreiben und nicht lokal zu installieren. Auch bei der lokalen Entwicklung, werden diese Dienste im Docker Container genutzt.

Ich entwickle mit Microsoft Visual Code und nutze Ertweiterungen für Python, Mongo, Git etc. Dies ermöglicht mir möglichst alles aus Visual Code zu machen.

### 4.1 Lokal
Folgende Software muss installiert sein:
* Visual Code
* Python
* Docker Desktop
* git

Danach muss die Umgebung korrekt definiert werden. Diese unterscheidet sich für lokal, docker und kubernetes. Es gibt auch Anpassungen zwischen Windows und Linux. Ich nutze .env für diesen Zweck. Ich habe eine Vorlage für .env erstellt `template-dotenv-secretes.txt/` und `template-dotenv.txt/`. Diese zwei Templates müssen als ein .env mit entsprechenden Anpassungen
gepseichert werden.

Für Pyhton gibt es eine eigene Virutalisierung, diese hilft kein Durcheinander bei den Abhängigkeiten zu haben. Ich kann aber mit einem `virtual-env` für alle 3 microservices arbeiten. Siehe auch im Script (`gpt_backend/dev-local-init.sh`) welche Schritte notwendig sind um das virtuelle Python zu erstellen. Das pip install installiert effektiv die Abhängigkeiten des jeweiligen Service.

Die entsprechenden Dockerfile's führen im Prinzip die gleichen Schritte aus.

Die jeweiligen microservices können mit `uvicorn app.main:app --host 0.0.0.0 --port 8004` gestartet werden. Mit Visual Code kann auch das Python Programm so gestartet werden, damit man gleich debuggen kann.

Mit `docker-compose up -d mongo` start ich zuerst mongo, das gleich mache ich für kong und ollama. Somit kann ich lokal mit allen services entwicklen, debuggen und testen.

### 4.2 Docker Compose
Neben der lokalen Entwicklung, kann auch nur mit Docker Compose entwickelt werden. Dies ist aber am Anfang umständlich, deshalb wird dies erst genutzt, wenn der Code schon fertig ist.

Um mit Docker Compose zu arbeiten, muss jeder Service ein Dockerfile besitzen, dies dokumentiert auch die Erstellung des Service. Nach einer Code Anpassung müssen die Dockerfile's als images erstellt werden bevor sie gestartet werden.

Der grosse Vorteil ist, dass es hier bereits wie in der Produktion ist und somit dann die Umsetzung auf Kubernetes viel leichter wird. Ich kann damit auch rasch auf einen neuen Rechner gehen, ohne dass ich viel Konfigurieren muss.





## 5. Technologie-Stack

### Backend Services
- **Runtime:** Python 3.13 (Alpine Linux)
- **Framework:** FastAPI + Uvicorn
- **Authentication:** JWT
- **API Gateway:** Kong Gateway

### Infrastructure
- **Container:** Docker
- **Orchestration:** Kubernetes (MicroK8s)
- **Package Management:** Helm 3
- **Load Balancing:** MetalLB
- **Ingress:** NGINX Ingress Controller

### Datenbanken
- **PostgreSQL** - Kong Gateway Konfiguration
- **MongoDB** - Anwendungsdaten

### AI/ML
- **Ollama** - LLM Runtime
- **Models:** TinyLlama, Gemma3

---

## 6. Besonderheiten

### 6.1 Secrets Management
- Helm-basierte Secret-Injection
- Umgebungsvariablen für Passwörter
- Kubernetes Secret Resources

### 6.2 Storage
- **Persistent Volumes** für Datenbanken und Logs
- **Volume Mounts** für Log-Sammlung
- **Model Storage** für LLM-Modelle

### 6.3 Entwicklung vs. Produktion
- **Development:** Port-Forwarding, lokale Services
- **Production:** LoadBalancer, Ingress-basiertes Routing
- **Monitoring:** Prometheus-Integration (Kong Plugin)

Diese Architektur ermöglicht eine skalierbare, containerisierte GPT-Backend-Lösung mit vollständiger Kubernetes-Integration und flexiblen Deployment-Optionen.