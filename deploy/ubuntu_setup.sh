#!/usr/bin/env bash
set -euo pipefail

PROJECT_DIR="/var/www/tracking_web"
DOMAIN="_"
DB_NAME="tracking_db"
DB_USER="tracking_user"
DB_PASSWORD="change-me"
PYTHON_BIN="python3"
APP_USER="www-data"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --project-dir)
      PROJECT_DIR="$2"
      shift 2
      ;;
    --domain)
      DOMAIN="$2"
      shift 2
      ;;
    --db-name)
      DB_NAME="$2"
      shift 2
      ;;
    --db-user)
      DB_USER="$2"
      shift 2
      ;;
    --db-password)
      DB_PASSWORD="$2"
      shift 2
      ;;
    --python)
      PYTHON_BIN="$2"
      shift 2
      ;;
    *)
      echo "Unknown argument: $1"
      exit 1
      ;;
  esac
done

if [[ $EUID -ne 0 ]]; then
  echo "Run as root: sudo bash deploy/ubuntu_setup.sh ..."
  exit 1
fi

echo "[1/8] Installing OS packages..."
apt update
apt -y install git nginx postgresql postgresql-contrib ${PYTHON_BIN} ${PYTHON_BIN}-venv ${PYTHON_BIN}-dev build-essential

if [[ ! -d "$PROJECT_DIR" ]]; then
  echo "Project directory not found: $PROJECT_DIR"
  exit 1
fi

echo "[2/8] Preparing Python environment..."
cd "$PROJECT_DIR"
if [[ ! -d .venv ]]; then
  ${PYTHON_BIN} -m venv .venv
fi

.venv/bin/pip install --upgrade pip
.venv/bin/pip install -r requirements.txt gunicorn psycopg2-binary

echo "[3/8] Configuring PostgreSQL database..."
sudo -u postgres psql <<SQL
DO
\$\$
BEGIN
   IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = '${DB_USER}') THEN
      CREATE ROLE ${DB_USER} LOGIN PASSWORD '${DB_PASSWORD}';
   ELSE
      ALTER ROLE ${DB_USER} WITH LOGIN PASSWORD '${DB_PASSWORD}';
   END IF;
END
\$\$;
SQL

sudo -u postgres psql -tc "SELECT 1 FROM pg_database WHERE datname = '${DB_NAME}'" | grep -q 1 || sudo -u postgres createdb -O "${DB_USER}" "${DB_NAME}"

echo "[4/8] Writing production .env if missing..."
if [[ ! -f .env ]]; then
  SECRET_KEY=$(.venv/bin/python - <<'PY'
from django.core.management.utils import get_random_secret_key
print(get_random_secret_key())
PY
)

  cat > .env <<ENV
DEBUG=0
SECRET_KEY=${SECRET_KEY}
ALLOWED_HOSTS=${DOMAIN},$(hostname -I | awk '{print $1}'),127.0.0.1
DB_ENGINE=django.db.backends.postgresql
DB_NAME=${DB_NAME}
DB_USER=${DB_USER}
DB_PASSWORD=${DB_PASSWORD}
DB_HOST=127.0.0.1
DB_PORT=5432
SECURE_SSL_REDIRECT=0
SESSION_COOKIE_SECURE=0
CSRF_COOKIE_SECURE=0
SECURE_HSTS_SECONDS=0
ENV
fi

echo "[5/8] Running Django migrations and static collection..."
.venv/bin/python manage.py migrate
.venv/bin/python manage.py collectstatic --noinput

echo "[6/8] Creating systemd service..."
cat > /etc/systemd/system/tracking_web.service <<SERVICE
[Unit]
Description=Gunicorn for tracking_web
After=network.target

[Service]
User=${APP_USER}
Group=www-data
WorkingDirectory=${PROJECT_DIR}
EnvironmentFile=${PROJECT_DIR}/.env
ExecStart=${PROJECT_DIR}/.venv/bin/gunicorn --workers 3 --bind unix:${PROJECT_DIR}/tracking_web.sock tracking_web.wsgi:application
Restart=always

[Install]
WantedBy=multi-user.target
SERVICE

chown -R ${APP_USER}:www-data "${PROJECT_DIR}"
chmod 750 "${PROJECT_DIR}"

systemctl daemon-reload
systemctl enable tracking_web
systemctl restart tracking_web

echo "[7/8] Configuring Nginx..."
cat > /etc/nginx/sites-available/tracking_web <<NGINX
server {
    listen 80;
    server_name ${DOMAIN};

    location /static/ {
        alias ${PROJECT_DIR}/staticfiles/;
    }

    location / {
        include proxy_params;
        proxy_pass http://unix:${PROJECT_DIR}/tracking_web.sock;
    }
}
NGINX

ln -sf /etc/nginx/sites-available/tracking_web /etc/nginx/sites-enabled/tracking_web
rm -f /etc/nginx/sites-enabled/default
nginx -t
systemctl restart nginx

echo "[8/8] Opening firewall ports..."
ufw allow OpenSSH || true
ufw allow 'Nginx Full' || true
ufw --force enable || true

echo "Deployment complete."
echo "Create admin user if needed:"
echo "sudo -u ${APP_USER} ${PROJECT_DIR}/.venv/bin/python ${PROJECT_DIR}/manage.py createsuperuser"
