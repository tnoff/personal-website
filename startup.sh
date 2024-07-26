#!/usr/bin/env bash
set -o errexit

/opt/website-venv/bin/python /opt/website/manage.py collectstatic --no-input
/opt/website-venv/bin/python /opt/website/manage.py migrate --fake-initial
/opt/website-venv/bin/python /opt/website/manage.py runserver