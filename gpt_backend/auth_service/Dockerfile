# Use an official Python runtime as a parent image
FROM python:3.12-alpine

# Set the working directory in the container
WORKDIR /app

# Copy the requirements.txt first to leverage Docker cache for dependency installation
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code to the container
COPY ./app ./app
COPY ./.env ./.env

# Expose the port that FastAPI will run on (here, 8002)
EXPOSE 8002

# Define environment variable for Python to not buffer output (helpful for logs)
ENV PYTHONUNBUFFERED=1

# Command to run the application using uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8002"]
