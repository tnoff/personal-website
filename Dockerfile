FROM ubuntu:24.04

RUN apt-get update && apt-get -y upgrade
RUN apt-get install -y python3-dev python3-virtualenv

RUN mkdir -p /opt/website /var/log/website
COPY homepage/ templates/ website/ manage.py requirements.txt startup.sh /opt/website
RUN chmod +x /opt/website/startup.sh

RUN virtualenv /opt/website-venv
RUN /opt/website-venv/bin/pip install -r /opt/website/requirements.txt

CMD ["/opt/website/startup.sh"]