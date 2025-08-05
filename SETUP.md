# Setup

## Ports Overview

### Exposed Ports

| Port  | Service      | Description |
|-------|--------------|-------------|
| 443   | Web Page     | Web server |
| 8000  | Kong Gateway | HTTP Proxy (API Gateway) |
| 3000  | Grafana      | Monitoring dashboard |
| 11434 | Ollama       | Local LLM inference server |

### Kong ports

| Port | Service       | Description |
|------|---------------|-------------|
| 8000 | Kong Gateway  | HTTP Proxy (API Gateway) |
| 8443 | Kong Gateway  | HTTPS Proxy (API Gateway) |
| 8001 | Kong Gateway  | Admin API HTTP |
| 8444 | Kong Gateway  | Admin API HTTPS |
| 8002 | Auth Service  | User authentication and authorization |
| 8003 | Chat Service  | Chat/messaging functionality |
| 8004 | Admin Service | Administrative operations |

### Internal service ports

| Port | Service | Description |
|------|---------|-------------|
| 27017 | MongoDB | Database for chat and user data |
| 3100 | Loki | Log aggregation system |
| 9080 | Promtail | Log collection agent |
| 9090 | Prometheus | Metrics collection and monitoring |

## Local with Docker

## Docker only

## Kubernetes

