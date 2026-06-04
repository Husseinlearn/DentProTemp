# ========= Base layer =========
FROM python:3.12-slim AS base
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1
WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential libpq-dev curl \
 && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /app/requirements.txt
RUN pip install --upgrade pip && pip install -r requirements.txt

# نجعل المجلدات القياسية للملفات
RUN mkdir -p /app/staticfiles /app/media

# ========= Dev layer =========
FROM base AS dev
# أدوات التطوير (اختياري)
RUN pip install watchdog
COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh
COPY . /app

# ========= Prod layer =========
FROM base AS prod
RUN pip install gunicorn
COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh
COPY . /app

