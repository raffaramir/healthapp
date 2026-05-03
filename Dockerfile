# Koyeb deployment — Django + Daphne (ASGI) + Channels.
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PORT=8000

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY deploy/koyeb/requirements-koyeb.txt ./requirements.txt
RUN pip install --upgrade pip && pip install -r requirements.txt

COPY . .

RUN python manage.py collectstatic --noinput

EXPOSE 8000

# Migrations + idempotent superuser bootstrap + Daphne ASGI server.
CMD sh -c "python manage.py migrate --noinput && \
           (python manage.py createsuperuser --noinput || true) && \
           daphne -b 0.0.0.0 -p ${PORT} healthapp.asgi:application"
