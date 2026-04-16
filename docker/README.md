# Docker & Docker Compose

Study notes for containerization, orchestration, and deployment with Docker and Docker Compose.

## What this covers

- Docker concepts: images, containers, volumes, networks, layers, registries, Dockerfiles
- Progressive learning roadmap from newbie to expert
- Setup guides and Dockerfiles for React, Next.js, Astro, and Node.js APIs
- Docker Compose for multi-service local development and production
- Production patterns: multi-stage builds, security hardening, reverse proxies, CI/CD integration
- Platform-scale topics: base images, supply chain security, multi-architecture, orchestration decisions

## Docs

- [Deep dive guide](docs/DOCKER_DOCKER_COMPOSE.md) — Complete learning path and engineering reference
- [Brainstorm prompt](docs/BRAIN_STORM.md) — The AI prompt used to generate the guide

## Key takeaways

- Docker solves "works on my machine" at the infrastructure level.
- Multi-stage builds are essential for frontend apps — build big, run small.
- Docker Compose replaces the "install these things" README with `docker compose up`.
- Treat containers as disposable. Persist data in volumes, not in containers.
- Start with Docker Compose; move to Kubernetes only when you need multi-node scaling.
