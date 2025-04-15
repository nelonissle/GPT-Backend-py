# Use an official Python runtime as a parent image
FROM python:3.12-alpine

# Set the working directory in the container
WORKDIR /app

# Add a placeholder file to avoid errors
RUN echo "Chat service is not implemented yet." > /app/placeholder.txt

# Expose a port (optional, for consistency)
EXPOSE 8003

# Command to keep the container running
CMD ["tail", "-f", "/dev/null"]