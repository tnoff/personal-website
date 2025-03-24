FROM python:3.13-slim-bookworm

RUN apt-get update && apt-get install -y gcc libpq-dev

RUN mkdir -p /opt/web /var/log/website
COPY homepage/ /opt/web/homepage
COPY templates/ /opt/web/templates
COPY website/ /opt/web/website
COPY startup.sh requirements.txt manage.py /opt/web/
RUN chmod +x /opt/web/startup.sh

RUN pip install -r /opt/web/requirements.txt

RUN apt-get remove -y gcc && apt-get autoremove -y

CMD ["/opt/web/startup.sh"]