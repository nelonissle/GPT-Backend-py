# init script for local development

# create a .env file out of ./template-dotenv-secrets.txt and ./template-dotenv.txt
echo "Creating .env file..."
cp template-dotenv-secrets.txt .env
# add template-dotenv.txt to the .env file
cat template-dotenv.txt >> .env

docker compose up -d

