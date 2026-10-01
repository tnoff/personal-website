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
pip install "rendercv[full]" pyyaml
```

`generate.py` is the only Python entry point; it has two runtime deps --
`pyyaml` to parse the CV, and the `rendercv` CLI (shelled out to via
`subprocess.run`) to produce the PDF. Missing `rendercv` fails only at
that step, after `resume.html` has already been (re)written, so the
failure can look partial.

## Local dev server

```bash
cd hugo-site
hugo server --bind 0.0.0.0
```

Serves on http://localhost:1313 and rebuilds on changes to `hugo-site/content/`,
`layouts/` and `static/`. No local Hugo? Use Docker:

```bash
docker run --rm -it -v $(pwd)/hugo-site:/src -p 1313:1313 hugomods/hugo:0.139.4 server --bind 0.0.0.0
```

## Regenerating resume content

`hugo-site/content/resume.html` is **generated** from
`Tyler_North_CV.yaml`. Don't edit it by hand —
`generate.py` overwrites it. (`hugo-site/content/projects.html` is
hand-authored, not generated.)

To regenerate after editing the YAML:

```bash
bash scripts/docker-generate.sh
```

The script runs `generate.py` inside a Docker container so the host
doesn't need a Python environment (it falls back to running `generate.py`
directly when Docker is unavailable). The script also rebuilds the
RenderCV PDF in `rendercv_output/` and copies it into
`hugo-site/static/`.

To regenerate automatically on every commit that touches the YAML, install
the pre-commit hook (`pip install pre-commit && pre-commit install`). The
`pre-commit` job in CI runs the same hook, so a PR that changes
`Tyler_North_CV.yaml` without the regenerated outputs fails.

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

Override the listen port or telemetry settings with `-e PORT=...`,
`-e OTEL_EXPORTER_OTLP_ENDPOINT=...`, `-e OTEL_SERVICE_NAME=...`
(see [README.md](README.md#environment-variables)). `docker-compose.yml` runs
the same image on 8080.

The image is `nginx:alpine` serving the static output from
`/usr/share/nginx/html`. Health check endpoint: `GET /_health/`.

## CI / release

CI is GitHub Actions, calling reusable workflows from
`tnoff/github-workflows` (pinned by SHA):

- `ci.yml` (PRs): `trufflehog.yml` (secret scan), `pre-commit.yml` (bandit +
  resume regeneration check), `spellcheck.yml`, `docker-build-check.yml`
  (image build + image secret scan, only when image-input files changed),
  `bump-version.yml` (on `renovate/dev-*` PRs), `check-workflow-contracts.yml`.
  The `CI result` job aggregates them and is the one required check.
- `release.yml` (push to `main`): `assemble-changelog.yml`, `tag.yml`,
  `docker-push.yml` (only when image-input files changed), then
  `trigger-bump-dispatch.yml`, which sends a `repository_dispatch` to
  docker-apps to open the image-pin bump PR.
- `scheduled.yml`: `renovate.yml`, `branch-cleanup.yml`
- `notify-failure.yml`: `discord-notify.yml`
- `techdocs-publish.yml`: publishes this site to Backstage TechDocs when
  `docs/**`, `mkdocs.yml` or `catalog-info.yaml` change.

`VERSION` at the repo root is the single source of truth for tagging.
