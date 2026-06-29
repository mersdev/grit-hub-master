# Multi-stage Dockerfile for Portal Generator
# Build from the repository ROOT (docker build context = .)

# ---- Stage 1: generate the portal ----
FROM docker.artifactory.dhl.com/library/python:3.11-slim AS builder
WORKDIR /build

ARG PIP_INDEX_URL
ARG PIP_TRUSTED_HOST

COPY skills/portal-generation/scripts/dist/ ./dist/
# Generator + its inputs (all live under skills/portal-generation/scripts/)
COPY skills/portal-generation/scripts/generate_portal.py \
     skills/portal-generation/scripts/portal-config.json \
     skills/portal-generation/scripts/requirements.txt ./
COPY skills/portal-generation/scripts/assets/    ./assets/
COPY skills/portal-generation/scripts/templates/ ./templates/
COPY skills/portal-generation/scripts/git-metadata.json ./

# Catalog content (lives at repo root — the generator scans these)
COPY agents/ ./agents/
COPY skills/  ./skills/

RUN pip install --no-cache-dir \
      --index-url "$PIP_INDEX_URL" \
      --trusted-host "$PIP_TRUSTED_HOST" \
      -r requirements.txt

# ---- Stage 2: serve with nginx ----
FROM docker.artifactory.dhl.com/nginx:1.29.7-alpine3.23-slim

COPY --from=builder /build/dist /usr/share/nginx/html
COPY skills/portal-generation/scripts/nginx.conf /etc/nginx/conf.d/default.conf

# Run as an arbitrary non-root UID (OpenShift restricted SCC)
RUN sed -i 's,/var/run/nginx.pid,/tmp/nginx.pid,' /etc/nginx/nginx.conf \
 && sed -i '/^http {/a \    client_body_temp_path /tmp/client_temp;\n    proxy_temp_path /tmp/proxy_temp;\n    fastcgi_temp_path /tmp/fastcgi_temp;\n    uwsgi_temp_path /tmp/uwsgi_temp;\n    scgi_temp_path /tmp/scgi_temp;' /etc/nginx/nginx.conf \
 && chgrp -R 0 /var/cache/nginx /var/run /var/log/nginx /etc/nginx/conf.d \
 && chmod -R g=u /var/cache/nginx /var/run /var/log/nginx /etc/nginx/conf.d

EXPOSE 8080
CMD ["nginx", "-g", "daemon off;"]

