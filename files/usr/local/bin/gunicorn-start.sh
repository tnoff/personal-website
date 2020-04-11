#!/bin/bash

cp /secret/secret_key /opt/website/
cp /secret/my.cnf /opt/website/

mkdir -p /logs/website
touch /logs/website/website.log
chown -R www-data: /opt/website/secret_key /opt/website/my.cnf /logs/website/

/usr/local/bin/gunicorn -c /etc/gunicorn.conf --chdir /opt/website/ website.wsgi:application
