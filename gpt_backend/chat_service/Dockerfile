# Basis-Image
FROM python:3.10-alpine

# Arbeitsverzeichnis festlegen
WORKDIR /app

# Install system dependencies for building Python packages
RUN apk add --no-cache gcc musl-dev libffi-dev openssl-dev cargo make

# requirements.txt kopieren und Python-Pakete installieren
COPY requirements.txt .

# Upgrade pip and install dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Anwendungscode kopieren
COPY . .

# Create logs directory inside container
RUN mkdir -p /app/logs

# Port freigeben
EXPOSE 8003

VOLUME ["/app/logs"]
VOLUME ["/app/global_logs"]

# Anwendung mit uvicorn starten
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8003"]