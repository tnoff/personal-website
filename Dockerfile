FROM ubuntu:18.04

VOLUME ["/secret", "/logs"]

# Insall packages
RUN apt-get update
RUN apt-get install -y \
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
   # Cleanup
   && apt-get clean && rm -rf /var/lib/apt/lists/*

# Make directories
RUN mkdir -p /opt/website/ /var/log/website/
# Copy files
ADD website /opt/website
COPY files/pip-requires.txt /tmp/pip-requires.txt
COPY files/etc/nginx/conf.d/nginx.conf /etc/nginx/conf.d/nginx.conf
COPY files/etc/supervisor/conf.d/supervisord.conf /etc/supervisor/conf.d/supervisord.conf
COPY files/usr/local/bin/gunicorn-start.sh /usr/local/bin/gunicorn-start.sh
COPY files/etc/gunicorn.conf /etc/gunicorn.conf
COPY files/etc/logrotate.d/nginx /etc/logrotate.d/nginx
# Run any needed chowns and chmods
RUN chown -R www-data: /opt/website/ /var/log/website
RUN chmod +x /usr/local/bin/gunicorn-start.sh
# Install packages
RUN /usr/bin/pip3 install -r /tmp/pip-requires.txt
# Start supervisord
CMD /usr/bin/supervisord -n
