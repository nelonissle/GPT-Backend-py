#!/usr/bin/env sh

# install jq on this alpine container
apk add --no-cache jq
# install curl on this alpine container
apk add --no-cache curl

echo "🛠️ Registering auth_service..."
curl -s -X POST "http://${KONG_GATEWAY_SERVICE_HOST}:${KONG_GATEWAY_SERVICE_PORT_ADMIN}/services/" \
--data "name=auth_service" \
--data "url=http://${AUTH_SERVICE_GPT_SERVICE_HOST}:${AUTH_SERVICE_GPT_SERVICE_PORT}/auth"

echo "🔀 Creating route for auth_service..."
curl -s -X POST "http://${KONG_GATEWAY_SERVICE_HOST}:${KONG_GATEWAY_SERVICE_PORT_ADMIN}/services/auth_service/routes" \
--data "paths[]=/auth"

echo "🛠️ Registering chat_service..."
curl -s -X POST "http://${KONG_GATEWAY_SERVICE_HOST}:${KONG_GATEWAY_SERVICE_PORT_ADMIN}/services/" \
--data "name=chat_service" \
--data "url=http://${CHAT_SERVICE_GPT_SERVICE_HOST}:${CHAT_SERVICE_GPT_SERVICE_PORT}/chat"

echo "🔀 Creating route for chat_service..."
curl -s -X POST "http://${KONG_GATEWAY_SERVICE_HOST}:${KONG_GATEWAY_SERVICE_PORT_ADMIN}/services/chat_service/routes" \
--data "paths[]=/chat"

# getting route service ID for chat_service
CHAT_ROUTE_ID=$(curl -s http://${KONG_GATEWAY_SERVICE_HOST}:${KONG_GATEWAY_SERVICE_PORT_ADMIN}/routes | \
jq -r '.data[] | select(.paths[] == "/chat") | .id')
if [ -z "$CHAT_ROUTE_ID" ]; then
  echo "❌ No route ID provided for /chat. Exiting."
  exit 1
fi

echo "🧩 Attaching JWT plugin to chat_service route..."
curl -s -X POST "http://${KONG_GATEWAY_SERVICE_HOST}:${KONG_GATEWAY_SERVICE_PORT_ADMIN}/routes/${CHAT_ROUTE_ID}/plugins" \
--data-urlencode "name=jwt" \
--data-urlencode "config.claims_to_verify[]=exp" \
--data-urlencode "config.secret_is_base64=false" \
--data-urlencode "config.key_claim_name=sub"

echo "🛠️ Registering admin_service..."
curl -s -X POST http://${KONG_GATEWAY_SERVICE_HOST}:${KONG_GATEWAY_SERVICE_PORT_ADMIN}/services \
--data name=admin_service \
--data url=http://${ADMIN_SERVICE_GPT_SERVICE_HOST}:${ADMIN_SERVICE_GPT_SERVICE_PORT}

echo "🔀 Creating /admin route..."
curl -s -X POST http://${KONG_GATEWAY_SERVICE_HOST}:${KONG_GATEWAY_SERVICE_PORT_ADMIN}/services/admin_service/routes \
--data name=admin_route \
--data 'paths[]=/admin' \
--data strip_path=false

echo "🧩 Attaching JWT plugin to admin_route..."
curl -s -X POST http://${KONG_GATEWAY_SERVICE_HOST}:${KONG_GATEWAY_SERVICE_PORT_ADMIN}/routes/admin_route/plugins \
--data name=jwt \
--data 'config.claims_to_verify[]=exp'

echo "📊 Enabling Prometheus monitoring plugin..."
curl -s -X POST http://${KONG_GATEWAY_SERVICE_HOST}:${KONG_GATEWAY_SERVICE_PORT_ADMIN}/plugins \
--data "name=prometheus"

echo "✅ Kong configuration complete!"

echo "Shows all registered plugins:"
curl http://${KONG_GATEWAY_SERVICE_HOST}:${KONG_GATEWAY_SERVICE_PORT_ADMIN}/plugins | jq .

echo "Shows all registered services:"
curl http://${KONG_GATEWAY_SERVICE_HOST}:${KONG_GATEWAY_SERVICE_PORT_ADMIN}/services | jq .