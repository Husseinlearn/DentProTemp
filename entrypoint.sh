#!/usr/bin/env bash
set -e

# تأخير بسيط إلى أن تصبح قاعدة البيانات جاهزة (يعتمد على healthcheck أيضًا)
echo "Waiting for DB..."
python - <<'PYCODE'
import os, time, psycopg2
from psycopg2 import OperationalError
host = os.getenv("POSTGRES_HOST","db")
port = int(os.getenv("POSTGRES_PORT","5432"))
user = os.getenv("POSTGRES_USER","dentuser")
pwd  = os.getenv("POSTGRES_PASSWORD","dentpass")
db   = os.getenv("POSTGRES_DB","dentpro")
for i in range(30):
    try:
        psycopg2.connect(host=host, port=port, user=user, password=pwd, dbname=db).close()
        print("DB is up!")
        break
    except OperationalError:
        print("DB not ready, retry...", i+1)
        time.sleep(1)
else:
    raise SystemExit("DB not reachable")
PYCODE

# ترحيلات وجمع ملفات ثابتة
python manage.py migrate --noinput
python manage.py collectstatic --noinput || true

if [ "$1" = "dev" ]; then
  echo "Starting Django development server..."
  exec python manage.py runserver 0.0.0.0:8000
elif [ "$1" = "gunicorn" ]; then
  echo "Starting Gunicorn..."
  exec gunicorn DentPro.wsgi:application --bind 0.0.0.0:8000 --workers 3 --timeout 120
else
  exec "$@"
fi
