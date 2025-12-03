FROM nginx:1.27-alpine-otel

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

# Set default environment variables
ENV OTEL_EXPORTER_OTLP_ENDPOINT="localhost:4317"
ENV PORT="8080"

EXPOSE ${PORT}
ENTRYPOINT ["/docker-entrypoint.sh"]