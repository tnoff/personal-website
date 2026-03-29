#!/usr/bin/env bash
set -euo pipefail

IMAGE_TAG="tyler-north-generate"

docker build -f Dockerfile.generate -t "$IMAGE_TAG" . -q
docker run --rm -v "$(pwd):/work" -w /work "$IMAGE_TAG" python generate.py
