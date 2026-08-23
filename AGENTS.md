# AGENTS.md

Guidance for AI coding agents working in this repository. For an
overview of the site and how to build/run it see [README.md](README.md);
for dev server, content regeneration, and CI see [DEVELOPMENT.md](DEVELOPMENT.md).

## What this repo is

A Hugo static site served by nginx. The resume page is generated from a
single YAML CV; everything else is hand-authored markdown/HTML.

```
.
├── Tyler_North_CV.yaml          # Single source of truth for the resume page + PDF
├── generate.py                  # Renders YAML → resume.html + RenderCV PDF
├── hugo-site/
│   ├── hugo.toml                # baseURL, taxonomy disabled, HTML in MD
│   ├── content/
│   │   ├── _index.html          # Homepage — hand-authored
│   │   ├── resume.html          # GENERATED — do not edit
│   │   └── projects.html        # Hand-authored
│   ├── layouts/                 # Bootstrap 5 templates
│   ├── static/                  # Static assets + the generated PDF
│   └── nginx.conf               # Serves :8080, /_health/ liveness, gzip + headers
├── scripts/docker-generate.sh   # Wrapper that runs generate.py in Docker
├── Dockerfile                   # nginx:alpine + Hugo build
└── Dockerfile.generate          # Used by scripts/docker-generate.sh
```

## Non-obvious internals

### `resume.html` is generated — never hand-edit

`generate.py` reads `Tyler_North_CV.yaml` and overwrites
`hugo-site/content/resume.html` on every run. A hand-edit there will be
wiped the next time `scripts/docker-generate.sh` runs. To change resume
content, edit the YAML and re-run the script. `projects.html` is *not*
generated — it is hand-authored and edited directly.

### `rendercv_output/` flows into the site

`generate.py` also copies `rendercv_output/Tyler_Daniel_North_CV.pdf`
to `hugo-site/static/Tyler_Daniel_North_CV.pdf` so the homepage's PDF
link points at the latest render. The `rendercv_output/` directory is
the canonical artifact location — don't move it without updating the
constants at the top of `generate.py`.

### Nginx listens on 8080 (not 80)

The image runs nginx as the non-root `nginx` user, which cannot bind
80. `hugo-site/nginx.conf` listens on 8080; the Kubernetes Service
forwards 80 → 8080. If you change the port, also update the Service
manifest in `tnoff-projects/docker-apps` and the
`HEALTHCHECK` in the Dockerfile.

### `/_health/` is the readiness/liveness probe

`hugo-site/nginx.conf` defines `/_health/` returning `200 OK`. The
Kubernetes manifests in `docker-apps` reference this path. Don't rename
it without updating both.

That location carries `access_log off;` **and** `otel_trace off;`. Both
are deliberate: the kubelet probes it every few seconds and nothing else
calls it — measured 2026-08-22 at 0.28 spans/s against 0.0006 spans/s of
real page views — so tracing it meant the site's entire span output was
probes, each landing in Tempo as its own single-span trace.

`otel_trace on` is set in the `http` block and inherited by every
location, so turning it off has to be explicit here. If you add another
probe-only or machine-only location, turn it off there too.

### Hugo version pinning is via the Alpine package

The Dockerfile installs Hugo via `apk add --no-cache hugo`, which pulls
whatever version Alpine has for the base image's release. Major Hugo
upgrades occasionally break theme/template syntax — when bumping the
nginx base image (which usually means a new Alpine version), build
locally first and check the rendered output.

## Conventions

- **Bootstrap 5** for layout. Add new components as Hugo partials, not
  inline `<style>` blocks.
- **Generated files carry a warning header** — `resume.html` starts with
  an `<!-- AUTO-GENERATED from Tyler_North_CV.yaml — do not edit
  directly -->` banner written by `generate.py`. `projects.html` has no
  banner because it is hand-authored. If you're unsure whether a content
  file is generated, check for the banner or `grep` `generate.py` for its
  filename.
