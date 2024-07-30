FROM ubuntu:24.04

RUN apt-get update && apt-get -y upgrade
RUN apt-get install -y python3-dev python3-virtualenv libpq-dev

RUN mkdir -p /opt/web /var/log/website
COPY homepage/ /opt/web/homepage
COPY templates/ /opt/web/templates
COPY website/ /opt/web/website
COPY startup.sh requirements.txt manage.py /opt/web/
RUN chmod +x /opt/web/startup.sh

RUN virtualenv /opt/website-venv
RUN /opt/website-venv/bin/pip install -r /opt/web/requirements.txt

CMD ["/opt/web/startup.sh"]