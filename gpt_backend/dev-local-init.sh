# init script for local development

# create a python virtual environment
echo "Creating a python virtual environment..."
python3 -m venv .venv
# activate the virtual environment
source .venv/bin/activate
# install the required packages
pip install -r admin_service/requirements.txt
pip install -r auth_service/requirements.txt
pip install -r chat_service/requirements.txt

# install ollama with curl
echo "Installing ollama..."
curl -sSfL https://ollama.com/download | sh
# install the required models
ollama pull gemma3:1b

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

