#!/usr/bin/env bash
set -o errexit

python /opt/web/manage.py collectstatic --no-input
python /opt/web/manage.py runserver 0.0.0.0:8000