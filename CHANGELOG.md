# Changelog

All notable changes to the personal website will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.0.7] - 2026-08-25

### Changed

- chore(deps): update nginx docker tag to v1.31.4

## [0.0.6] - 2026-08-23

### Changed

- Requests to `/_health/` are no longer traced. The endpoint is called by the kubelet's readiness and liveness probes and by nothing else, so every trace the site produced was a probe landing as its own single-span trace. Page views are traced exactly as before.

## [0.0.5] - 2026-07-21

### Changed

- chore(deps): update nginx docker tag to v1.31.3

## [0.0.4] - 2026-06-30

### Changed

- Bumped nginx to v1.31.2

## [0.0.3] - 2026-05-24

### Changed

- Bumped nginx to v1.31.1

## [0.0.2] - 2026-05-14

### Changed

- Bumped nginx to v1.31.0

## [0.0.1] - 2026-05-01

### Added

- Initial release.
