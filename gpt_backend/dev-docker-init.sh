# init script for local development

# create a .env file out of ./template-dotenv-secrets.txt and ./template-dotenv.txt
echo "Creating .env file..."
cp template-dotenv-secrets.txt .env
# add template-dotenv.txt to the .env file
cat template-dotenv.txt >> .env
# replace the values in .env with the values from the secrets file
while IFS= read -r line; do
  key=$(echo "$line" | cut -d '=' -f 1)
  value=$(echo "$line" | cut -d '=' -f 2-)
  sed -i "s|^$key=.*|$key=$value|" .env
done < template-dotenv-secrets.txt

docker compose up -d

