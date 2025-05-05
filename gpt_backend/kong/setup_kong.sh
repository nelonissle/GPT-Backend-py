#!/bin/bash

echo "🛠️ Registering auth_service..."
curl -s -X POST "http://localhost:8001/services/" \
--data "name=auth_service" \
--data "url=http://auth_service:8002/auth"

echo "🔀 Creating route for auth_service..."
curl -s -X POST "http://localhost:8001/services/auth_service/routes" \
--data "paths[]=/auth"

echo "🛠️ Registering chat_service..."
curl -s -X POST "http://localhost:8001/services/" \
--data "name=chat_service" \
--data "url=http://chat_service:8003/chat"

echo "🔀 Creating route for chat_service..."
curl -s -X POST "http://localhost:8001/services/chat_service/routes" \
--data "paths[]=/chat"

echo "🔎 Please enter the Chat route ID (use: curl http://localhost:8001/routes to find it):"
curl http://localhost:8001/routes

echo "🔎 Please enter the Chat route ID (use: curl http://localhost:8001/routes to find it):"
read CHAT_ROUTE_ID

if [ -z "$CHAT_ROUTE_ID" ]; then
  echo "❌ No route ID provided for /chat. Exiting."
  exit 1
fi

echo "🧩 Attaching JWT plugin to chat_service route..."
curl -s -X POST "http://localhost:8001/routes/${CHAT_ROUTE_ID}/plugins" \
--data-urlencode "name=jwt" \
--data-urlencode "config.claims_to_verify[]=exp" \
--data-urlencode "config.secret_is_base64=false" \
--data-urlencode "config.key_claim_name=sub"

echo "🛠️ Registering admin_service..."
curl -s -X POST http://localhost:8001/services \
--data name=admin_service \
--data url=http://admin_service:8004

echo "🔀 Creating /admin route..."
curl -s -X POST http://localhost:8001/services/admin_service/routes \
--data name=admin_route \
--data 'paths[]=/admin' \
--data strip_path=false

echo "🧩 Attaching JWT plugin to admin_route..."
curl -s -X POST http://localhost:8001/routes/admin_route/plugins \
--data name=jwt \
--data 'config.claims_to_verify[]=exp'

echo "📊 Enabling Prometheus monitoring plugin..."
curl -s -X POST http://localhost:8001/plugins \
--data "name=prometheus" \
--data "config.scrape_interval=5" \
--data "config.path=/metrics"

echo "✅ Kong configuration complete!"
