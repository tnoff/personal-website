FROM ubuntu:20.04

VOLUME ["/secret", "/logs"]

ENV DEBIAN_FRONTEND=noninteractive

# Insall packages
RUN apt-get update
RUN apt-get install -y \
   cron \
   firefox \
   jq \
   libmysqlclient-dev \
   logrotate \
   nginx \
   python3-dev \
   python3-pip \
   supervisor \
   # Nice to have
   curl \
   vim \
   less \
   wget \
   # Cleanup
   && apt-get clean && rm -rf /var/lib/apt/lists/*

# Setup gecko driver
RUN wget https://github.com/mozilla/geckodriver/releases/download/v0.26.0/geckodriver-v0.26.0-linux64.tar.gz -O /tmp/geckodriver.tar.gz
RUN tar -xvzf /tmp/geckodriver.tar.gz -C /usr/local/bin/

# Make directories
RUN mkdir -p /opt/website/ /var/log/website/
# Copy files
ADD website /opt/website
COPY files/pip-requires.txt /tmp/pip-requires.txt
COPY files/etc/nginx/conf.d/nginx.conf /etc/nginx/conf.d/nginx.conf
COPY files/etc/supervisor/conf.d/supervisord.conf /etc/supervisor/conf.d/supervisord.conf
COPY files/usr/local/bin/gunicorn-start.sh /usr/local/bin/gunicorn-start.sh
COPY files/etc/gunicorn.conf /etc/gunicorn.conf
COPY files/etc/logrotate.d/website /etc/logrotate.d/website

# Run any needed chowns and chmods
RUN chown -R www-data: /opt/website/
RUN chmod +x /usr/local/bin/gunicorn-start.sh \
    /usr/local/bin/geckodriver

# Setup logrotate files
RUN sed -i 's/su root syslog/su root adm/' /etc/logrotate.conf
RUN chmod 0644 /etc/logrotate.d/website

# Install packages
RUN /usr/bin/pip3 install -r /tmp/pip-requires.txt

# Start supervisord
CMD /usr/bin/supervisord -n
