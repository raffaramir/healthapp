"""WSGI configuration for PythonAnywhere — copy the contents of this file into:

    /var/www/<your-username>_pythonanywhere_com_wsgi.py

(opened from the *Web* tab > "WSGI configuration file" link).

Replace the two TODO blocks below before saving.
"""
import os
import sys

# ─────────────────────────────────────────────────────────────────────
# 1. TODO — change "yourusername" to your actual PythonAnywhere username.
# ─────────────────────────────────────────────────────────────────────
PROJECT_DIR = '/home/yourusername/projet-sante/healthapp'

# Make the project importable.
if PROJECT_DIR not in sys.path:
    sys.path.insert(0, PROJECT_DIR)

# ─────────────────────────────────────────────────────────────────────
# 2. TODO — production environment variables.
# These override anything in settings.py.
# ─────────────────────────────────────────────────────────────────────
os.environ['DJANGO_SETTINGS_MODULE'] = 'healthapp.settings'
os.environ['DJANGO_DEBUG']           = 'False'
os.environ['DJANGO_SECRET_KEY']      = 'CHANGE-ME-LONG-RANDOM-STRING-AT-LEAST-50-CHARS'
os.environ['DJANGO_ALLOWED_HOSTS']   = 'yourusername.pythonanywhere.com'
os.environ['DJANGO_CSRF_TRUSTED_ORIGINS'] = 'https://yourusername.pythonanywhere.com'

# Optional: switch to MySQL on PythonAnywhere (paid tiers; free is SQLite).
# os.environ['DB_ENGINE']   = 'mysql'
# os.environ['DB_NAME']     = 'yourusername$healthapp'
# os.environ['DB_USER']     = 'yourusername'
# os.environ['DB_PASSWORD'] = 'your-mysql-password'
# os.environ['DB_HOST']     = 'yourusername.mysql.pythonanywhere-services.com'

# ─── Django entry point ─────────────────────────────────────────────
from django.core.wsgi import get_wsgi_application  # noqa: E402

application = get_wsgi_application()
