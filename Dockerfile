FROM python:3.13-slim-bookworm

RUN apt-get update && apt-get install -y gcc libpq-dev git

RUN mkdir -p /opt/web /var/log/website
COPY homepage/ /opt/web/homepage
COPY templates/ /opt/web/templates
COPY website/ /opt/web/website
COPY otlp.py /opt/web/
COPY startup.sh requirements.txt manage.py /opt/web/
RUN chmod +x /opt/web/startup.sh

RUN pip install -r /opt/web/requirements.txt

# https://github.com/open-telemetry/opentelemetry-python-contrib/pull/3648
# Bug in upstream, fix pending
# Remove git install above and uninstall below
WORKDIR /tmp
RUN git clone https://github.com/open-telemetry/opentelemetry-python.git
WORKDIR /tmp/opentelemetry-python
RUN pip uninstall opentelemetry-semantic-conventions opentelemetry-api opentelemetry-sdk -y && pip install opentelemetry-semantic-conventions/ opentelemetry-api/ opentelemetry-sdk/
WORKDIR /tmp
RUN git clone https://github.com/tnoff/opentelemetry-python-contrib.git
WORKDIR /tmp/opentelemetry-python-contrib
RUN  git checkout tnorth/fix
RUN pip uninstall opentelemetry-instrumentation-wsgi opentelemetry-instrumentation-django opentelemetry-instrumentation opentelemetry-util-http -y
RUN pip install opentelemetry-instrumentation/ instrumentation/opentelemetry-instrumentation-wsgi/ instrumentation/opentelemetry-instrumentation-django/ util/opentelemetry-util-http/

WORKDIR /opt/web
RUN rm -rf  /tmp/opentelemetry-python /tmp/opentelemetry-python-contrib

RUN apt-get remove -y gcc git && apt-get autoremove -y

CMD ["/opt/web/startup.sh"]