Migration for kong 
Schritt 3: Kong-Migration durchführen
Da du nun den DB‑Mode verwendest, musst du zunächst die erforderlichen Datenbanktabellen migrieren. Dies machst du mit dem Kong-Migrationsbefehl.

Führe dazu in deinem Kong-Gateway-Container folgenden Befehl aus (bevor du Kong vollständig startest):

bash
Kopieren
docker-compose run --rm kong-gateway kong migrations bootstrap
Dies initialisiert die Datenbank und legt alle benötigten Tabellen und Schemas an.

Falls du später Änderungen an der Konfiguration vornimmst, kannst du auch kong migrations up und kong migrations finish nutzen.





Starte die Container, oder zumindest den kong-database-Container:

bash
Kopieren
docker-compose up kong-database
Warte einige Sekunden (oder prüfe manuell, ob PostgreSQL verfügbar ist).

Führe dann den Migrationsbefehl aus:

bash
Kopieren
docker-compose run --rm kong-migrations kong migrations bootstrap


Kong Setup with CURL:
1. Auth-Service als Kong-Service registrieren
bash
Kopieren
curl -i -X POST "http://localhost:8001/services/" --data "name=auth_service" --data "url=http://auth_service:8002/auth"
1. Route für den Auth-Service erstellen
bash
Kopieren
curl -i -X POST "http://localhost:8001/services/auth_service/routes" --data "paths[]=/auth"
1. Chat-Service als Kong-Service registrieren
bash
Kopieren
curl -i -X POST "http://localhost:8001/services/" --data "name=chat_service" --data "url=http://chat_service:8003/chat"
1. Route für den Chat-Service erstellen
bash
Kopieren
curl -i -X POST "http://localhost:8001/services/chat_service/routes" --data "paths[]=/chat"
1. Routen abfragen (um die Route-ID zu ermitteln)
bash
Kopieren
curl -i "http://localhost:8001/routes"
Notiere dir die "id" der Chat-Route, da du diese für den nächsten Schritt benötigst.

1. JWT-Plugin an die Chat-Route anhängen
Ersetze <ROUTE_ID> durch die zuvor ermittelte Route-ID:
bash
Kopieren
 curl -i -X POST "http://localhost:8001/routes/bd6bf78c-c408-4e33-bc75-d4ca20bcbb71/plugins" \ --data-urlencode "name=jwt" \  --data-urlencode "config.claims_to_verify[]=exp" \ --data-urlencode "config.secret_is_base64=false" \ --data-urlencode "config.key_claim_name=sub"

Diese Befehle richten die Services, Routen und das JWT-Plugin dynamisch über die Kong Admin API ein. Beachte, dass du diese Befehle in einer Unix-kompatiblen Shell (z. B. bash) ausführst – in Linux, macOS oder über WSL auf Windows. Falls du Fragen hast oder weitere Anpassungen benötigst, stehe ich gern zur Verfügung!


Kong setup for admin_service:
Here are the exact one‑liner curl commands you can copy‑&‑paste to set up your admin_service in Kong:

Register the admin service

bash
Kopieren
Bearbeiten
curl -i -X POST http://localhost:8001/services --data name=admin_service --data url=http://admin_service:8004
Create the /admin route

bash
Kopieren
Bearbeiten
curl -i -X POST http://localhost:8001/services/admin_service/routes  --data name=admin_route  --data 'paths[]=/admin' --data strip_path=false
Enable JWT validation on that route

bash
Kopieren
Bearbeiten
curl -i -X POST http://localhost:8001/routes/admin_route/plugins --data name=jwt --data 'config.claims_to_verify[]=exp'

Kong Monitoring 
Promethues setup:
curl -s -X POST http://localhost:8001/plugins --data "name=prometheus" --data "config.scrape_interval=5" --data "config.path=/metrics"