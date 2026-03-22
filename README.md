# Parcel Pulse Tracking

A Django web application for parcel tracking with a public tracking page and a secure admin dashboard (2FA).

## Features
- Public tracking page with timeline view
- Admin dashboard with CRUD for tracking numbers
- Status event history per tracking number
- Admin audit logs
- Two-factor authentication support

## Tech Stack
- Django 5
- PostgreSQL (recommended) or SQLite for local dev

## Local Setup (Windows or Linux)
1. Create and activate virtual environment
2. Install dependencies from `requirements.txt`
3. Copy `.env.example` to `.env` and adjust values
4. Run migrations
5. Create a superuser
6. Start the server

Example:

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# Linux/macOS
source .venv/bin/activate

pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

## Admin Access
- Admin dashboard: /admin/
- Admin login: /auth/account/login/
- Two-factor setup: /auth/account/two_factor/setup/
- Django admin (optional): /django-admin/

## Notes
- For production, set DEBUG=0 and enable secure cookie settings.
- Use a real SECRET_KEY in production.
- Configure PostgreSQL using DB_* variables in .env and install `psycopg2-binary`.

## Ubuntu VPS Deployment (High Level)
- Install Python, pip, and PostgreSQL
- Create a virtual environment and install requirements
- Set up environment variables in .env
- Run migrations and create a superuser
- Use a production WSGI server (gunicorn) behind a reverse proxy
- Enable HTTPS and set SECURE_SSL_REDIRECT=1

## Ubuntu VPS Deployment (One-Command Setup)
1. Upload/clone project to `/var/www/tracking_web`
2. Run:

```bash
cd /var/www/tracking_web
chmod +x deploy/ubuntu_setup.sh
sudo bash deploy/ubuntu_setup.sh \
	--project-dir /var/www/tracking_web \
	--domain YOUR_DOMAIN_OR_IP \
	--db-name tracking_db \
	--db-user tracking_user \
	--db-password 'STRONG_DB_PASSWORD'
```

3. Create admin user:

```bash
sudo -u www-data /var/www/tracking_web/.venv/bin/python /var/www/tracking_web/manage.py createsuperuser
```

4. Validate services:

```bash
sudo systemctl status tracking_web --no-pager
sudo systemctl status nginx --no-pager
```
