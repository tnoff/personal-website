# personal-website

Tyler North's personal website built with Hugo and served via Nginx with OpenTelemetry instrumentation.

## Prerequisites

- [Hugo](https://gohugo.io/installation/) (v0.139.0 or later)
- [Docker](https://docs.docker.com/get-docker/) (for containerized deployment and content generation)
- [pre-commit](https://pre-commit.com/) (optional, for automatic content regeneration on commit)

## Local Development

### Install Hugo

**macOS:**
```bash
brew install hugo
```

**Linux:**
```bash
# Download and install Hugo extended
wget https://github.com/gohugoio/hugo/releases/download/v0.139.0/hugo_extended_0.139.0_linux-amd64.tar.gz
tar -xzf hugo_extended_0.139.0_linux-amd64.tar.gz
sudo mv hugo /usr/local/bin/
```

**Or use Docker** (no local Hugo installation needed):
```bash
docker run --rm -it -v $(pwd)/hugo-site:/src -p 1313:1313 hugomods/hugo:0.139.4 server --bind 0.0.0.0
```

### Start Development Server

```bash
cd hugo-site
hugo server --bind 0.0.0.0
```

The site will be available at http://localhost:1313

Hugo will automatically rebuild and reload when you make changes to:
- Content files in `hugo-site/content/`
- Layout templates in `hugo-site/layouts/`
- Static assets in `hugo-site/static/`

### Build Static Site

```bash
cd hugo-site
hugo --minify
```

This generates the production site in `hugo-site/public/`

## Docker Development

### Build the Docker Image

```bash
docker build -t personal-website .
```

### Run the Container

**Default (port 8080):**
```bash
docker run -p 8080:8080 personal-website
```

The site will be available at http://localhost:8080

**Custom port:**
```bash
docker run -p 3000:3000 \
  -e PORT="3000" \
  personal-website
```

The site will be available at http://localhost:3000

### Run with Custom Configuration

```bash
docker run -p 9000:9000 \
  -e PORT="9000" \
  -e OTEL_EXPORTER_OTLP_ENDPOINT="your-collector:4317" \
  -e OTEL_SERVICE_NAME="personal-website" \
  personal-website
```

## Resume Content

Resume, projects, and the PDF are all generated from a single source of truth:

```
Tyler_North_CV.yaml  →  generate.py  →  hugo-site/content/resume.html
                                     →  hugo-site/content/projects.html
                                     →  hugo-site/static/Tyler_Daniel_North_CV.pdf
```

**To regenerate content after editing the YAML:**
```bash
bash scripts/docker-generate.sh
```

**To keep generated files automatically in sync on every commit:**
```bash
pip install pre-commit
pre-commit install
# Now editing Tyler_North_CV.yaml and committing will auto-regenerate outputs
```

CI will fail if `Tyler_North_CV.yaml` is changed without regenerating the output files.

## Project Structure

```
.
├── Tyler_North_CV.yaml     # Single source of truth for resume/projects content
├── generate.py             # Generates resume.html, projects.html, and PDF from YAML
├── Dockerfile              # Production image (Hugo + Nginx)
├── Dockerfile.generate     # Image used only for content generation (Python + rendercv)
├── scripts/
│   └── docker-generate.sh  # Builds Dockerfile.generate and runs generate.py
├── hugo-site/              # Hugo website root
│   ├── content/            # Page content (auto-generated, do not edit directly)
│   │   ├── _index.html     # Homepage (manually maintained)
│   │   ├── resume.html     # Generated from Tyler_North_CV.yaml
│   │   └── projects.html   # Generated from Tyler_North_CV.yaml
│   ├── layouts/            # Hugo templates
│   │   ├── _default/
│   │   │   ├── baseof.html # Base template
│   │   │   └── single.html # Single page template
│   │   └── index.html      # Homepage template
│   ├── static/             # Static assets (CSS, JS, fonts, generated PDF)
│   ├── hugo.toml           # Hugo configuration
│   ├── nginx.conf          # Nginx configuration
│   └── docker-entrypoint.sh # Docker entrypoint script
└── AGENTS.md               # AI agent development guide
```

## Features

- **Static Site Generation**: Built with Hugo for fast, efficient static sites
- **Bootstrap 5**: Responsive design with local Bootstrap assets
- **Nginx**: Production-ready web server
- **OpenTelemetry**: Full distributed tracing support with client IP attribution
- **Real Client IP**: Extracts real client IP from `X-Real-IP` header behind ingress
- **Health Check**: `/_health/` endpoint for monitoring
- **Docker**: Single-stage containerized deployment

## Nginx Configuration

### Real Client IP Forwarding

When deployed behind an ingress controller (e.g., ingress-nginx), the real client IP is extracted from the `X-Real-IP` header. The configuration trusts requests from internal cluster networks:

- `10.0.0.0/8` - Internal pod network
- `10.244.0.0/16` - Kubernetes pod CIDR

The real client IP is:
- Used in access logs (`$remote_addr`)
- Added to trace spans as `http.client_ip` attribute

### OpenTelemetry Tracing

Traces are exported via gRPC to the configured OTEL collector. Each request span includes:
- Standard HTTP attributes (method, status, path)
- `http.client_ip` - The real client IP address

## Deployment

The site is designed to be deployed via Docker on Kubernetes:

1. Build the Docker image with a version tag
2. Push to your container registry
3. Deploy to Kubernetes with appropriate environment variables
4. Configure environment variables as needed

### Environment Variables

- `PORT` - Port for Nginx to listen on (default: `8080`)
- `OTEL_EXPORTER_OTLP_ENDPOINT` - OpenTelemetry collector endpoint (default: `localhost:4317`)
- `OTEL_SERVICE_NAME` - Service name for OpenTelemetry traces (required for proper trace identification)

Example Kubernetes deployment snippet:
```yaml
env:
  - name: PORT
    value: "8080"
  - name: OTEL_EXPORTER_OTLP_ENDPOINT
    value: "otel-collector.monitoring.svc.cluster.local:4317"
  - name: OTEL_SERVICE_NAME
    value: "personal-website"
```

## License

Personal project - all rights reserved.