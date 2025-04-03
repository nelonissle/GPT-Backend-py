# Usefull docker commands and Information

## Deploy Script 
**Automated Deploy With a Script**
Move in to the Main Directory `cd ./gpt_backend`.<br>
Then run the Script like this:
```bash
./start-backend.ps1
```

## Usefull Commands 

**Stop and remove all containers:**

```bash
 docker compose down
```

**Restart the whole setup (Rebuild and Restart):**

```bash
docker compose down; docker compose up --build -d
```

**Check logs of a specific container:**

```bash
docker logs auth_service -f
```
