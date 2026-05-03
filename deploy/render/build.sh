#!/usr/bin/env bash
# Render build hook — runs once per deploy.
# Note: the database is NOT reachable from the build environment on Render's
# free plan, so `migrate` runs in the start command instead (see render.yaml).
set -o errexit

pip install --upgrade pip
pip install -r deploy/render/requirements-render.txt

python manage.py collectstatic --noinput
