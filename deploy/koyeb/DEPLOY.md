# Déploiement Koyeb — HEALTHAPP

Stack 100 % gratuite : **Koyeb** (web Daphne) + **Neon** (Postgres) + **Upstash** (Redis pour Channels).

## 1. Créer la base Postgres sur Neon

1. https://neon.tech → Sign up (GitHub)
2. Create project → région la plus proche (Frankfurt par ex.)
3. Database name : `healthapp`
4. Copier la **Connection string** (format `postgres://user:pass@ep-xxx.region.aws.neon.tech/healthapp?sslmode=require`)
   → ce sera la valeur de `DATABASE_URL`

## 2. Créer le Redis sur Upstash

1. https://upstash.com → Sign up (GitHub)
2. Create Database → région proche, type **Regional**
3. Onglet **Details** → copier la **Redis URL** (format `rediss://default:xxxx@usw1-xxxx.upstash.io:6379`)
   → ce sera la valeur de `REDIS_URL`

## 3. Créer le service Koyeb

1. https://app.koyeb.com → Create App
2. **Source** : GitHub → autoriser le repo
3. **Builder** : Dockerfile (auto-détecté à la racine `healthapp/`)
4. **Instance** : Free (Eco - Nano)
5. **Port** : `8000`, protocole `HTTP`
6. **Variables d'environnement** :

| Key | Value |
|---|---|
| `DJANGO_DEBUG` | `False` |
| `DJANGO_SECRET_KEY` | une chaîne aléatoire de 50+ caractères |
| `DJANGO_ALLOWED_HOSTS` | `.koyeb.app` (préfixe leading dot pour les sous-domaines) |
| `DJANGO_CSRF_TRUSTED_ORIGINS` | `https://*.koyeb.app` |
| `DATABASE_URL` | (depuis Neon, étape 1) |
| `REDIS_URL` | (depuis Upstash, étape 2) |
| `DJANGO_SUPERUSER_EMAIL` | votre email |
| `DJANGO_SUPERUSER_PASSWORD` | mot de passe fort ≥8 caractères mixtes |
| `DJANGO_SUPERUSER_USERNAME` | `admin` |

7. Deploy → Koyeb build l'image, lance `migrate` + `createsuperuser` + Daphne.

## 4. Vérification

- Logs Koyeb : voir `Listening on TCP address 0.0.0.0:8000` (Daphne) → OK
- Ouvrir l'URL `https://<app-name>-<org>.koyeb.app`
- Se connecter avec l'email/mot de passe de superuser

## 5. Limites du free tier — à savoir

- **Filesystem éphémère** : `media/` est perdu à chaque redéploiement.
  Pour persistance des `profile_image`, configurer Cloudflare R2 ou S3 avec `django-storages`.
- **512 Mo RAM** sur l'instance — OK pour démo, juste pour gros trafic.
- **Upstash free** : 10 000 commandes Redis/jour — suffit pour démo.
- **Neon free** : 0,5 Go stockage Postgres — suffit pour milliers d'utilisateurs.

## Mise à jour

Push sur la branche `main` → Koyeb redéploie automatiquement (autoDeploy par défaut).
