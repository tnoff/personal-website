# Development

Local dev, content regeneration, build, and CI for this site. User-facing
docs (what the site is) live in [README.md](README.md); for non-obvious
internals see [AGENTS.md](AGENTS.md).

## Prerequisites

- [Hugo](https://gohugo.io/installation/) (the Dockerfile pins
  `apk add hugo`; locally any 0.139+ release works)
- Python 3.11+ (for `generate.py`)
- Docker (for the production-image build)

## Setup

Optional virtualenv for the Python generator:

```bash
virtualenv venv
source venv/bin/activate
pip install pyyaml
```

`generate.py` is the only Python entry point; it has a single
runtime dep (`pyyaml`).

## Local dev server

```bash
cd hugo-site
hugo server --bind 0.0.0.0
```

Default Hugo listen port: 1313.

## Regenerating resume content

`hugo-site/content/resume.html` is **generated** from
[`Tyler_North_CV.yaml`](Tyler_North_CV.yaml). Don't edit it by hand —
`generate.py` overwrites it. (`hugo-site/content/projects.html` is
hand-authored, not generated.)

To regenerate after editing the YAML:

```bash
bash scripts/docker-generate.sh
```

The script runs `generate.py` inside a Docker container so the host
doesn't need a Python environment. The script also rebuilds the
RenderCV PDF in `rendercv_output/` and copies it into
`hugo-site/static/`.

## Building the static site manually

```bash
cd hugo-site
hugo --minify
# output in hugo-site/public/
```

## Production Docker image

```bash
docker build -t personal-website .
docker run --rm -p 8080:8080 personal-website
```

The image is `nginx:alpine` serving the static output from
`/usr/share/nginx/html`. Health check endpoint: `GET /_health/`.

## CI / release

CI is GitLab CI pulling shared templates from
`tnoff-projects/github-workflows`. The image is built and pushed via
`buildkit-docker-push.yml`; the SHA pin in
[`tnoff-projects/docker-apps`](https://gitlab.com/tnoff-projects/docker-apps)
is bumped automatically by `trigger-bump.yml`.

`VERSION` at the repo root is the single source of truth for tagging.
Bump it and push to `main` — CI handles tagging and the release.
