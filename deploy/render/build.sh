#!/usr/bin/env bash
# Render build hook — runs once before each deploy.
# `rootDir` in render.yaml means the working directory is already healthapp/.
set -o errexit

pip install --upgrade pip
pip install -r deploy/render/requirements-render.txt

python manage.py collectstatic --noinput
python manage.py migrate --noinput
