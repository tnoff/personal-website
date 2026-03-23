# AGENTS.md

This file provides guidance to AI coding agents when working with code in this repository.

## Development Commands

**Start development server:**
```bash
cd hugo-site && hugo server --bind 0.0.0.0
```

**Build static site:**
```bash
cd hugo-site && hugo --minify
```

**Run in Docker:**
```bash
docker build -t personal-website .
docker run -p 8080:8080 personal-website
```

**Regenerate resume/projects content from YAML:**
```bash
bash scripts/docker-generate.sh
```

## Architecture Overview

This is a Hugo static website served via Nginx with the following structure:

- **Hugo site:** `hugo-site/` - Contains all Hugo configuration and content
- **Content:** `hugo-site/content/` - HTML pages for the site
- **Layouts:** `hugo-site/layouts/` - Hugo templates using Bootstrap 5
- **Static files:** Served directly from generated `public/` directory

### Key Components

**Hugo Configuration (`hugo-site/hugo.toml`):**
- BaseURL set to https://tyler-north.com
- Disables unused taxonomy features
- Enables HTML rendering in markdown

**Content Structure:**
- `content/_index.html` - Homepage with introduction and social links (manually maintained)
- `content/resume.html` - Auto-generated from `Tyler_North_CV.yaml`, do not edit directly
- `content/projects.html` - Auto-generated from `Tyler_North_CV.yaml`, do not edit directly

To update resume or projects content, edit `Tyler_North_CV.yaml` and run `bash scripts/docker-generate.sh`.

**Layouts:**
- `layouts/_default/baseof.html` - Base template with Bootstrap 5, custom CSS, navbar, and footer
- `layouts/_default/single.html` - Single page layout
- `layouts/index.html` - Homepage layout

**Nginx Configuration (`hugo-site/nginx.conf`):**
- Listens on port 8080
- Health check endpoint at `/_health/`
- Gzip compression enabled
- Security headers configured

### Production Deployment

**Docker:**
- Single-stage build using `nginx:1.27-alpine`
- Hugo installed from Alpine packages (v0.139.0)
- Site built during image creation
- Final image serves static files via Nginx (~103 MiB)

**Kubernetes:**
- Deploy via standard K8s deployment
- Service exposes port 8080
- Health checks use `/_health/` endpoint