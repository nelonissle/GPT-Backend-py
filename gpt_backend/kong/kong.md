# Migration for Kong

## Schritt 3: Kong-Migration durchführen

Da du nun den **DB‑Mode** verwendest, musst du zunächst die erforderlichen Datenbanktabellen migrieren. Dies machst du mit dem Kong-Migrationsbefehl.

Führe dazu in deinem Kong-Gateway-Container folgenden Befehl aus (bevor du Kong vollständig startest):

```bash
docker-compose run --rm kong-gateway kong migrations bootstrap
# Dies initialisiert die Datenbank und legt alle benötigten Tabellen und Schemas an.
# Falls du später Änderungen an der Konfiguration vornimmst:
kong migrations up
kong migrations finish

# Starte die Container oder zumindest die Datenbank
docker-compose up kong-database

# Warte, bis PostgreSQL läuft und führe ggf. nochmal die Migration aus
docker-compose run --rm kong-migrations kong migrations bootstrap

# Auth-Service registrieren
curl -i -X POST "http://localhost:8001/services/" \
--data "name=auth_service" \
--data "url=http://auth_service:8002/auth"

# Route für Auth-Service
curl -i -X POST "http://localhost:8001/services/auth_service/routes" \
--data "paths[]=/auth"

# Chat-Service registrieren
curl -i -X POST "http://localhost:8001/services/" \
--data "name=chat_service" \
--data "url=http://chat_service:8003/chat"

# Route für Chat-Service
curl -i -X POST "http://localhost:8001/services/chat_service/routes" \
--data "paths[]=/chat"

# Routen abfragen
curl -i "http://localhost:8001/routes"
# Notiere dir die "id" der Chat-Route

# JWT Plugin an Chat-Route anhängen (ersetze <ROUTE_ID>)
curl -i -X POST "http://localhost:8001/routes/<ROUTE_ID>/plugins" \
--data-urlencode "name=jwt" \
--data-urlencode "config.claims_to_verify[]=exp" \
--data-urlencode "config.secret_is_base64=false" \
--data-urlencode "config.key_claim_name=sub"

# Admin-Service registrieren
curl -i -X POST http://localhost:8001/services \
--data name=admin_service \
--data url=http://admin_service:8004

# Route für Admin-Service
curl -i -X POST http://localhost:8001/services/admin_service/routes \
--data name=admin_route \
--data 'paths[]=/admin' \
--data strip_path=false

# JWT Plugin an Admin-Route anhängen
curl -i -X POST http://localhost:8001/routes/admin_route/plugins \
--data name=jwt \
--data 'config.claims_to_verify[]=exp'

# Prometheus Plugin aktivieren
curl -s -X POST http://localhost:8001/plugins \
--data "name=prometheus" \
--data "config.scrape_interval=5" \
--data "config.path=/metrics"
