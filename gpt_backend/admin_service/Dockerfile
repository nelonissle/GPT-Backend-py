# Basis‑Image
FROM python:3.10-alpine

# Arbeitsverzeichnis
WORKDIR /app

# System‑Deps für Kompilierung
RUN apk add --no-cache gcc musl-dev

# 1) requirements installieren
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 2) gesamten Code kopieren (einschließlich app/, .env, …)
COPY . .

# Port freigeben
EXPOSE 8004

# Starten – jetzt ist /app in PYTHONPATH und "app" wird gefunden
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8004"]
