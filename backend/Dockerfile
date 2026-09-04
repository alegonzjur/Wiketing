FROM python:3.12-slim

# Evita .pyc y fuerza salida sin buffer (logs visibles al instante en docker logs)
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev gcc \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

# En desarrollo, docker-compose sobreescribe este CMD con runserver.
# En producción se usa tal cual (gunicorn).
CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000"]
