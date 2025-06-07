# Basis-Image
FROM python:3.10-alpine

# Arbeitsverzeichnis festlegen
WORKDIR /app

# Abhängigkeiten für den Build installieren
RUN apk add --no-cache gcc musl-dev

# requirements.txt kopieren und Python-Pakete installieren
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Anwendungscode kopieren
COPY ./app /app

# Port freigeben
EXPOSE 8003

VOLUME ["/app/logs"]

# Anwendung mit uvicorn starten
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8003"]