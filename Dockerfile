FROM nginx:1.31.10-alpine-otel

# Install Hugo
RUN apk add --no-cache hugo

# Build the site
WORKDIR /src
COPY hugo-site/ .
RUN hugo --minify

# Copy built site to nginx
RUN cp -r /src/public/* /usr/share/nginx/html/ && rm -rf /src

# Copy nginx config and entrypoint
COPY hugo-site/nginx.conf /etc/nginx/nginx.conf
COPY hugo-site/docker-entrypoint.sh /docker-entrypoint.sh
RUN chmod +x /docker-entrypoint.sh

# Smoke test, run by the CronJob in tnoff/docker-apps (apps/personal-website/smoke-cronjob.yaml) with
# this image, so the test that runs is always the one written for the site that is deployed
COPY smoke/site-smoke.sh /usr/local/bin/site-smoke
RUN chmod 0555 /usr/local/bin/site-smoke

# Set up permissions for non-root user
RUN chown -R nginx:nginx /usr/share/nginx/html \
    && chown -R nginx:nginx /var/cache/nginx \
    && chown -R nginx:nginx /var/log/nginx \
    && chown -R nginx:nginx /etc/nginx \
    && touch /var/run/nginx.pid \
    && chown nginx:nginx /var/run/nginx.pid \
    && chmod 1777 /tmp

# Set default environment variables
ENV OTEL_EXPORTER_OTLP_ENDPOINT="localhost:4317"
ENV PORT="8080"
ENV OTEL_SERVICE_NAME="personal-website"

# Switch to non-root user
USER nginx

EXPOSE ${PORT}
ENTRYPOINT ["/docker-entrypoint.sh"]