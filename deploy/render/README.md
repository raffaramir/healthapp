# Deploying HEALTHAPP to Render

Render supports **ASGI/WebSockets**, so chat + realtime notifications work — unlike PythonAnywhere. ~10 minutes from zero to live.

## What you'll get

- HTTPS at `https://<your-service>.onrender.com`
- Free PostgreSQL (90 days, then $7/mo or migrate elsewhere)
- Auto-deploy on `git push`
- Real-time chat over WebSocket ✅
- The free plan **sleeps after 15 min of inactivity** (~50s cold start). For an always-on demo, upgrade to Starter ($7/mo).

---

## Prereqs

- Your code is pushed to a GitHub repo (private is fine).
- The repo's structure has [`healthapp/manage.py`](../../manage.py) at `<repo>/healthapp/manage.py`. **The repo root is one level above `healthapp/`** — that's why `rootDir: healthapp` is set in [render.yaml](render.yaml).

If your GitHub repo's root **is already** the `healthapp/` folder (i.e. `manage.py` is at the repo root), edit [`render.yaml`](render.yaml) and **delete** the `rootDir: healthapp` line.

---

## 1. Sign up

1. Go to https://render.com → **Get Started**.
2. Sign up with **GitHub** (lets Render see your repos).
3. Authorize Render to access the repo containing HEALTHAPP.

## 2. Deploy with the Blueprint

1. Render dashboard → top-right **+ New** → **Blueprint**.
2. Select the GitHub repo that contains HEALTHAPP.
3. Render finds [`deploy/render/render.yaml`](render.yaml) automatically and shows what it will create:
   - Web service `healthapp`
   - PostgreSQL database `healthapp-db`
4. Click **Apply**.

Render then:
- Provisions the database
- Clones your repo, runs `build.sh` (installs deps, collects static, runs migrations)
- Starts Daphne
- Issues an HTTPS cert

Watch the build logs in the dashboard. First deploy takes 4–6 minutes.

## 3. Create your admin user

Once the service is **Live**, open the **Shell** tab on the web service page and run:

```bash
python manage.py createsuperuser
```

Set an email + password.

> Want demo data? Run `python manage.py seed_data` in the same shell.

## 4. Visit your site

Open `https://healthapp.onrender.com` (the exact URL appears at the top of the service page).

You should see the landing page. Click the globe icon — Arabic / RTL works. Log in with the admin user from step 3. Open `/chat/` — WebSocket connects.

## 5. After every code change

```powershell
git add .
git commit -m "..."
git push
```

Render auto-redeploys. Watch the logs in the dashboard.

---

## Customizing the service name

Want your URL to be something other than `healthapp.onrender.com`?

1. Edit [`render.yaml`](render.yaml) before the first deploy:
   - Change `name: healthapp` → `name: <your-name>`
   - Update `DJANGO_ALLOWED_HOSTS` and `DJANGO_CSRF_TRUSTED_ORIGINS` to match (e.g. `<your-name>.onrender.com`)
2. Commit + push, then run the Blueprint flow.

---

## Troubleshooting

- **Build fails on `pip install`**: check the build log. Most common is a missing system lib for `psycopg2-binary` — Render handles that automatically, so a failure usually means a typo in `requirements-render.txt`.
- **`DisallowedHost`**: `DJANGO_ALLOWED_HOSTS` doesn't include your `.onrender.com` URL. Edit the env var in the Render dashboard → **Environment** → save → manual *Deploy* → *Restart Service*.
- **CSRF "Origin checking failed"**: same fix for `DJANGO_CSRF_TRUSTED_ORIGINS` — must include the `https://` prefix.
- **WebSocket fails to connect**: Daphne must be the start command (already set in render.yaml). Check the service logs for the boot line.
- **App is slow on first hit**: free-tier cold start. Either keep the tab open, ping it from an uptime monitor, or upgrade to Starter.
- **Database "free trial expired"**: after 90 days, Render archives free Postgres. Upgrade or export + reimport into another provider (Neon, Supabase, etc.).
