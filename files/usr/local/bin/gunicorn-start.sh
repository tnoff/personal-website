#!/bin/bash

cp /secret/website/secret_key /opt/website/
cp /secret/website/my.cnf /opt/website/

/usr/local/bin/gunicorn -c /etc/gunicorn.conf --chdir /opt/website/ website.wsgi:application
