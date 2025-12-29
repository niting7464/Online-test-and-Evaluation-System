# Mindsprint — Online Test and Evaluation System

This is a Django-based online test and evaluation system. The repository contains the Django project `mindsprint`, an `accounts` app, `tests` app, templates and static assets.

Quick start (development)

1. Clone the repo and enter the project:

```bash
git clone <your-repo-url>
cd mindsprint
```

2. Create and activate a virtual environment, then install dependencies:

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

3. Create a `.env` file at the project root (example values):

```env
DJANGO_SECRET_KEY=your-secret-key
DJANGO_DEBUG=True
DJANGO_ALLOWED_HOSTS=127.0.0.1,localhost
EMAIL_HOST_USER=you@example.com
EMAIL_HOST_PASSWORD=yourpassword
PASSWORD_RESET_DOMAIN=http://127.0.0.1:8000
```

4. Apply migrations and run the dev server:

```bash
python manage.py migrate
python manage.py runserver
```

Testing password reset (local)
- By default emails are sent via SMTP as configured in `.env`. If you prefer to see emails in the console during development, set `EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend` in `.env`.
- If you want to test password reset links from a phone on the same network, set `PASSWORD_RESET_DOMAIN` to your machine's LAN address (for example `http://192.168.1.10:8000`) and run the server with `python manage.py runserver 0.0.0.0:8000`.

Deploy notes (Render)
- Use Gunicorn as the process manager: `gunicorn mindsprint.wsgi:application --bind 0.0.0.0:$PORT`.
- Set `DEBUG=False`, `DJANGO_SECRET_KEY`, `DATABASE_URL`, `PASSWORD_RESET_DOMAIN`, and SMTP env vars on the host.
- Run `python manage.py migrate` and `python manage.py collectstatic --noinput` during deployment.

Contributing
- Create issues or pull requests. Keep changes focused and include tests for new logic where possible.

License
- Add your project license here.

For full details about the project layout, see the repository files and the `mindsprint` app.
