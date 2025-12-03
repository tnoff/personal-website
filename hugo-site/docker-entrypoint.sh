#!/bin/sh
set -e

# Set default OTLP endpoint if not provided
export OTEL_EXPORTER_OTLP_ENDPOINT=${OTEL_EXPORTER_OTLP_ENDPOINT:-"localhost:4317"}

# Substitute environment variables in nginx config
envsubst '${OTEL_EXPORTER_OTLP_ENDPOINT}' < /etc/nginx/nginx.conf > /tmp/nginx.conf
mv /tmp/nginx.conf /etc/nginx/nginx.conf

# Test nginx configuration
nginx -t

# Start nginx
exec nginx -g "daemon off;"
