FROM python:3.13-alpine

WORKDIR /app

RUN apk add --no-cache gcc musl-dev libffi-dev openssl-dev cargo make

COPY requirements.txt .

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# 👇 Wichtig: Nur `app/`-Verzeichnis gezielt kopieren!
COPY ./app ./app

EXPOSE 8004
ENV PYTHONUNBUFFERED=1

VOLUME ["/app/logs"]

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8004"]
