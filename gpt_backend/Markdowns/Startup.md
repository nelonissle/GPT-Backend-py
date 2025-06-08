### Step by Step Guide to run the programm in Docker

## Step 1:
Set the Enviroment Variables you need you have a tamplate for them in the  ```backend``` directory. <br>
***```template-dotenv-secrets.txt```*** in here you see the template for your secrets. <br>
***```template-dotenv.txt```*** in here you see your enviroment variables that are not secret.

## Step 2:
Run the ```dev-docker-init.ps1``` script to generate your .env file and set them into your actual enviroment.  

## Step 3:
Run the ```start-backend.ps1``` script to start your docker compose and build all the services.

## Step 4:
as soon as your services are up you have to run the ```setup_kong.sh``` script. <br>

## Step 5:
run the ```setup_kong.ps1``` and configure it with the ***/chat*** id and after taht kong should be configured correct. <br>
after that you should be able to use the backend with the communication to the ollama model. 
