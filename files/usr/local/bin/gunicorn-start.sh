#!/bin/bash

cp /secret/secret_key /opt/website/
cp /secret/my.cnf /opt/website/

chown -R www-data: /opt/website/secret_key /opt/website/my.cnf

/usr/local/bin/gunicorn -c /etc/gunicorn.conf --chdir /opt/website/ website.wsgi:application
