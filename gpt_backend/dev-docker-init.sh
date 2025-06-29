# init script for local development

# create a .env file out of ./template-dotenv-secrets.txt and ./template-dotenv.txt
echo "Creating .env file..."
cp template-dotenv.txt .env
# add template-dotenv.txt to the .env file

docker compose up -d

