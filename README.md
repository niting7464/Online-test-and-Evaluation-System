# Mindsprint — Online Test and Evaluation System

Quick setup (development):

1. Create and activate a virtualenv

```bash
cd mindsprint
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

2. Create a `.env` file at the project root with (example):

```
DJANGO_SECRET_KEY=your-secret-key
DJANGO_DEBUG=True
DJANGO_ALLOWED_HOSTS=127.0.0.1,localhost
EMAIL_HOST_USER=you@example.com
EMAIL_HOST_PASSWORD=yourpassword
```

3. Migrate and run server

```bash
python manage.py migrate
python manage.py runserver
```

Notes:
- Replace secret values before deploying.
- Use the provided dev defaults only locally.
