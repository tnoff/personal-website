#!/bin/bash

cp /secret/website/secret_key /opt/website/
cp /secret/website/my.cnf /opt/website/

/usr/local/bin/gunicorn --access-logfile - --workers 3 --bind unix:/run/gunicorn.sock --chdir /opt/website/ website.wsgi:application
