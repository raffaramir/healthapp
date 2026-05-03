# Deploying HEALTHAPP to PythonAnywhere

End-to-end guide for the **free tier**. Time: ~20 minutes.

## What works / what doesn't

| Feature | Works on PA? |
|---|---|
| All page views, dashboards, admin | ✅ |
| REST API (DRF + JWT) | ✅ |
| User registration / login | ✅ |
| Service requests, medical records, pharmacy | ✅ |
| Static files (CSS/JS/images, PWA icons) | ✅ via WhiteNoise |
| PWA install on phones | ✅ (HTTPS provided by PA) |
| English / Arabic toggle | ✅ |
| **Real-time chat (WebSocket)** | ❌ no ASGI on PA |
| **Live push notifications** | ❌ same reason |
| Periodic tasks (medication reminders) | ⚠️ requires PA's "Scheduled tasks" tab (free: 1/day, paid: more) |

> If real-time chat is critical, redeploy on **Render** or **Fly.io** instead — both support ASGI/Daphne for free.

---

## 1. Get your code onto PythonAnywhere

Either push to GitHub and clone, or upload a zip.

**Option A — GitHub clone (recommended):**
```bash
# In a PythonAnywhere "Bash" console:
cd ~
git clone https://github.com/<youruser>/<yourrepo>.git projet-sante
```

**Option B — Upload a zip via the *Files* tab,** then extract in a Bash console:
```bash
unzip projet-sante.zip -d ~/
```

Either way you should end up with `/home/<youruser>/projet-sante/healthapp/manage.py`.

---

## 2. Create the virtualenv and install requirements

```bash
cd ~/projet-sante/healthapp
mkvirtualenv --python=/usr/bin/python3.10 healthapp-venv
pip install -r deploy/pythonanywhere/requirements-pa.txt
```

> Free tier RAM is tight — install the trimmed `requirements-pa.txt`, **not** the full `requirements.txt` (which pulls Daphne, Celery, Redis — unused here).

---

## 3. Configure the *Web* tab

1. Go to **Web** → **Add a new web app** → choose **Manual configuration** → **Python 3.10**.
2. Under **Virtualenv**, enter: `/home/<youruser>/.virtualenvs/healthapp-venv`
3. Under **Code → Source code**: `/home/<youruser>/projet-sante/healthapp`
4. Under **Code → Working directory**: `/home/<youruser>/projet-sante/healthapp`
5. **WSGI configuration file** → click the link, replace its content with the file at
   [`deploy/pythonanywhere/wsgi.py`](wsgi.py) in this repo. **Edit the two `TODO` blocks** (your username + a fresh `DJANGO_SECRET_KEY`).

   To generate a secret key, run in any Bash console:
   ```bash
   python -c 'import secrets; print(secrets.token_urlsafe(60))'
   ```

---

## 4. Static & media file mappings (Web tab → *Static files*)

Add **two** mappings:

| URL | Directory |
|---|---|
| `/static/` | `/home/<youruser>/projet-sante/healthapp/staticfiles` |
| `/media/`  | `/home/<youruser>/projet-sante/healthapp/media` |

WhiteNoise will also serve `/static/` from inside Django, but the explicit mapping makes it faster and offloads the work from the Python worker.

---

## 5. First-time database setup

In a Bash console:
```bash
workon healthapp-venv
cd ~/projet-sante/healthapp

# Apply migrations
python manage.py migrate

# Compile translations (English/Arabic) — pure-Python, no gettext required
python scripts/compile_messages.py

# Collect static files (PWA icons, CSS, JS) into staticfiles/
python manage.py collectstatic --noinput

# (Optional) seed demo data
python manage.py seed_data

# Create your real admin user
python manage.py createsuperuser
```

---

## 6. Reload + test

Web tab → green **Reload** button.

Open **`https://<youruser>.pythonanywhere.com`**. You should see the landing page in English. Click the globe icon — Arabic + RTL.

---

## 7. After every code update

```bash
cd ~/projet-sante/healthapp
git pull
workon healthapp-venv
pip install -r deploy/pythonanywhere/requirements-pa.txt   # only if requirements changed
python manage.py migrate                                    # only if migrations were added
python manage.py collectstatic --noinput
python scripts/compile_messages.py                          # only if .po files changed
```

Then click **Reload** in the Web tab.

---

## Troubleshooting

- **"DisallowedHost"** → set `DJANGO_ALLOWED_HOSTS` in the WSGI file to your full PA hostname.
- **CSRF "Origin checking failed"** → set `DJANGO_CSRF_TRUSTED_ORIGINS=https://<youruser>.pythonanywhere.com` in the WSGI file.
- **Static files 404** → re-run `collectstatic`, double-check the `/static/` mapping in the Web tab points at `staticfiles/` (not `static/`).
- **Server error 500** → tail the error log: Web tab → "Error log".
- **PWA not installable** → must be served over HTTPS (PA does this for you on the default `*.pythonanywhere.com` domain) and the manifest + service worker must respond 200 at `/manifest.webmanifest` and `/sw.js`.
- **Chat page blank** → expected. WebSocket connection fails on PA. Either deploy elsewhere or hide the chat menu item from the sidebar.
