Render deployment checklist

- Ensure `requirements.txt` contains `whitenoise` and other deps (already present).
- Set environment variables on Render:
  - `SECRET_KEY` (production secret)
  - `DEBUG=false`
  - `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT` (or `DATABASE_URL`)
  - `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD` if email is needed
  - `ALLOWED_HOSTS` should include your Render domain
- Build/Start commands on Render:
  - Build command: `python3 manage.py collectstatic --noinput` (ensure virtualenv/setup installs deps first)
  - Start command: `gunicorn mindsprint.wsgi --log-file -`
- Static files:
  - `STATIC_ROOT` is set to `staticfiles` (already configured)
  - WhiteNoise will serve static files via `STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'`
- Optional:
  - Add a `Procfile` with: `web: gunicorn mindsprint.wsgi`
  - Use Render's Postdeploy or Build hooks to run migrations: `python3 manage.py migrate --noinput`
- Verify after deploy:
  - Visit site; inspect network requests for static assets (200 from your domain)
  - Check logs for `collectstatic` and WhiteNoise messages

Commands to run locally before deploy:
```bash
# activate venv
source venv/bin/activate
# collect static
python3 manage.py collectstatic --noinput
# run migrations
python3 manage.py migrate --noinput
# run server
python3 manage.py runserver
```
