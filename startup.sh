#!/usr/bin/env bash
set -o errexit

/opt/website-venv/bin/python /opt/web/manage.py collectstatic --no-input
/opt/website-venv/bin/python /opt/web/manage.py runserver 0.0.0.0:8000