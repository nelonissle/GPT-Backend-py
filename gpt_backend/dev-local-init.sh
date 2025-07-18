# init script for local development

# create a python virtual environment
echo "Creating a python virtual environment..."
if [ ! -f ../.venv ]; then
   python3 -m venv ../.venv
fi

# activate the virtual environment
source ../.venv/bin/activate
# install the required packages
pip install -r admin_service/requirements.txt
pip install -r auth_service/requirements.txt
pip install -r chat_service/requirements.txt

# install ollama with curl
#echo "Installing ollama..."
#curl -sSfL https://ollama.com/download | sh
# install the required models
#ollama pull gemma3:1b

# create a .env file out of ./template-dotenv-secrets.txt and ./template-dotenv.txt
echo "Creating .env file..."
# copy template-dotenv-secrets.txt to .env if it does not exist
if [ ! -f ../.env ]; then
   echo "Creating ../.env file from template-dotenv.txt..."
   cp template-dotenv.txt ../.env
   # add template-dotenv.txt to the .env file
else
   echo ".env file already exists. Skipping creation."
fi
