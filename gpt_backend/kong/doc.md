Yes, you need to enter the container as the root user to install packages like curl or wget. By default, the Kong Gateway container runs as a non-root user for security reasons. To gain root access, you can override the user when executing the container shell.

Steps to Enter the Container as Root
Run the following command to enter the container as the root user:
docker exec -u root -it kong-gateway sh

Once inside the container, you can install curl using the following commands:
apt update
apt install -y curl

After installing curl, test the Kong Admin API:
curl http://localhost:8001/status

If You Still Encounter Issues
If you cannot install curl or apt commands fail, you can debug the Kong Gateway from the host machine or extend the Kong image to include debugging tools (as described in the previous response).

Let me know if you need further assistance!




How to Use the kong.yml File with Database Mode
If you want to use the kong.yml file to set up services and routes in Database Mode, you can import the configuration into the database using Kong's Admin API. This way, you don't have to manually configure services and routes via the Admin API.

Steps to Import kong.yml into the Database
Use the following command to import the kong.yml file into the database:
curl -X POST http://localhost:8001/config \
     -F "config=@kong/kong.yml"

http://localhost:8001: The Admin API endpoint.
kong.yml: Specifies the path to the kong.yml file.
After importing, the services and routes will be stored in the database and shared across all Kong nodes connected to the same database.

When Adding New Kong Nodes
If you add a new Kong node to your setup:

Connect the new node to the same database by setting the KONG_DATABASE, KONG_PG_HOST, KONG_PG_USER, and KONG_PG_PASSWORD environment variables in the docker-compose.yml file.
The new node will automatically pull the existing configuration from the database. No additional configuration is needed.