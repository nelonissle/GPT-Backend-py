# Authentication microservice

## Local environment
Start with `uvicorn app.main:app --host 0.0.0.0 --port 8003`

# Chat Service Documentation

## Overview

This chat service is built using FastAPI and provides functionalities for creating and managing chat sessions. It integrates with an LLM (Large Language Model) using the Ollama API to generate responses based on user input.

## Project Structure

```
chat_service
├── app
│   ├── __init__.py
│   ├── main.py
│   ├── routes
│   │   ├── __init__.py
│   │   └── chat_routes.py
│   ├── services
│   │   ├── __init__.py
│   │   └── ollama_llm.py
│   ├── database.py
│   └── utils.py
├── Dockerfile
├── requirements.txt
└── README.md
```

## Setup Instructions

1. **Clone the Repository**:
   Clone this repository to your local machine.

2. **Environment Variables**:
   Create a `.env` file in the root directory and set the necessary environment variables, including `SECRET_KEY` for JWT authentication and `OLLAMA_API_URL` for the Ollama API endpoint.

3. **Build and Run the Docker Containers**:
   Use Docker Compose to build and run the services:
   ```bash
   docker-compose up --build
   ```

4. **Access the Application**:
   The chat service will be available at `http://localhost:8003`. You can interact with the API using tools like Postman or curl.

## API Endpoints

- **POST /new**: Create a new chat session.
- **POST /add**: Add a message to an existing chat session.
- **GET /history**: Retrieve the history of chats for the authenticated user.
- **GET /{chat_id}**: Fetch a specific chat by its ID.

## Integration with Ollama LLM

The chat service integrates with the Ollama LLM to generate responses based on user queries. The integration is handled in the `app/services/ollama_llm.py` file, which contains functions to interact with the Ollama API.

### Example Usage

When a new chat is created, the service sends the initial user query to the Ollama API to get a response, which is then stored in the chat document.

## Testing

After setting up the service, you can test the integration by sending requests to the chat service endpoints and verifying that the responses from the Ollama LLM are correctly processed and stored.

## License

This project is licensed under the MIT License. See the LICENSE file for more details.