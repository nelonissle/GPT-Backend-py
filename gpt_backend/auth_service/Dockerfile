# Use an official Python runtime as a parent image
FROM python:3.13-alpine

# Set the working directory in the container
WORKDIR /app

# Install system dependencies for building Python packages
RUN apk add --no-cache gcc musl-dev libffi-dev openssl-dev cargo make

# Copy the requirements.txt first to leverage Docker cache for dependency installation
COPY requirements.txt .

# Upgrade pip and install dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code to the container
COPY ./app ./app
COPY ./.env ./.env

# Expose the port that FastAPI will run on (here, 8002)
EXPOSE 8002

# Define environment variable for Python to not buffer output (helpful for logs)
ENV PYTHONUNBUFFERED=1

# Create a non-root user and switch to it
RUN adduser -D myuser
USER myuser

# Command to run the application using uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8002"]