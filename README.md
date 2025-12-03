# personal-website

Tyler North's personal website built with Hugo and served via Nginx with OpenTelemetry instrumentation.

## Prerequisites

- [Hugo](https://gohugo.io/installation/) (v0.139.0 or later)
- [Docker](https://docs.docker.com/get-docker/) (optional, for containerized deployment)

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

```bash
docker run -p 8080:8080 personal-website
```

The site will be available at http://localhost:8080

### Run with Custom OpenTelemetry Endpoint

```bash
docker run -p 8080:8080 \
  -e OTEL_EXPORTER_OTLP_ENDPOINT="your-collector:4317" \
  personal-website
```

## Project Structure

```
.
├── hugo-site/              # Hugo website root
│   ├── content/            # Page content (HTML)
│   │   ├── _index.html     # Homepage
│   │   ├── resume.html     # Resume page
│   │   └── projects.html   # Projects page
│   ├── layouts/            # Hugo templates
│   │   ├── _default/
│   │   │   ├── baseof.html # Base template
│   │   │   └── single.html # Single page template
│   │   └── index.html      # Homepage template
│   ├── static/             # Static assets (CSS, JS, fonts)
│   ├── hugo.toml           # Hugo configuration
│   ├── nginx.conf          # Nginx configuration
│   └── docker-entrypoint.sh # Docker entrypoint script
├── Dockerfile              # Multi-stage Docker build
└── AGENTS.md               # AI agent development guide
```

## Features

- **Static Site Generation**: Built with Hugo for fast, efficient static sites
- **Bootstrap 5**: Responsive design with local Bootstrap assets
- **Nginx**: Production-ready web server
- **OpenTelemetry**: Full distributed tracing support
- **Health Check**: `/_health/` endpoint for monitoring
- **Docker**: Single-stage containerized deployment

## Deployment

The site is designed to be deployed via Docker on Kubernetes:

1. Build the Docker image with a version tag
2. Push to your container registry
3. Deploy to Kubernetes with appropriate environment variables
4. Configure `OTEL_EXPORTER_OTLP_ENDPOINT` to point to your OpenTelemetry collector

## License

Personal project - all rights reserved.