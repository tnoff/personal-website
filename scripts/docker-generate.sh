#!/usr/bin/env bash
set -euo pipefail

# Regenerate natively when Docker isn't available. The container path exists so
# a developer without rendercv installed can still regenerate, but it relies on
# a Docker daemon that shares the checkout via bind mount. CI's Kubernetes
# runner has no such daemon (its dind service can't see the job's workdir), so
# there `generate.py` runs directly against deps installed in the job image.
if ! command -v docker >/dev/null 2>&1; then
  exec python generate.py
fi

IMAGE_TAG="tyler-north-generate"

docker build -f Dockerfile.generate -t "$IMAGE_TAG" . -q
docker run --rm -v "$(pwd):/work" -w /work "$IMAGE_TAG" python generate.py
