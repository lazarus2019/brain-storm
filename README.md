# Brain Storm

Repository for researching and collecting notes on technology, architecture, and system design.

## Purpose

This repository is an index of study materials, experiments, and references. Each concept should have its own README, with deeper notes and examples stored beside it.

## Current concepts

### Nix Flakes

Study notes for reproducible development environments, multi-shell setups, project recipes, automation, and developer experience improvements.

- [Concept overview](nix-flake-samples/README.md)
- [Deep dive guide](nix-flake-samples/docs/NIX_FLAKE.md)
- [Brainstorm prompt](nix-flake-samples/docs/BRAIN_STORM.md)

### Cloudflare Workers

Study notes for edge computing, runtime constraints, storage primitives, and frontend-to-edge architecture.

- [Concept overview](cloudflare/README.md)
- [Deep dive guide](cloudflare/docs/CLOUDFLARE_WORKER.md)
- [Brainstorm prompt](cloudflare/docs/BRAIN_STORM.md)

### GitHub Actions

Study notes for CI/CD automation, deployment pipelines, release engineering, and platform engineering with GitHub Actions.

- [Concept overview](github/README.md)
- [Deep dive guide](github/docs/GITHUB_ACTION.md)
- [Brainstorm prompt](github/docs/BRAIN_STORM.md)

### Docker / Docker Compose

Study notes for containerization, orchestration, and deployment with Docker and Docker Compose.

- [Concept overview](docker/README.md)
- [Deep dive guide](docker/docs/DOCKER_DOCKER_COMPOSE.md)
- [Brainstorm prompt](docker/docs/BRAIN_STORM.md)

### GitLab CI/CD

Study notes for CI/CD automation, pipeline design, deployment strategies, and platform engineering with GitLab CI/CD.

- [Concept overview](gitlab/README.md)
- [Deep dive guide — GitLab CI/CD](gitlab/docs/GITLAB_CI.md)
- [Roadmap — GitLab CI Roadmap](gitlab/docs/GITLAB_CI_ROADMAP.md)
- [Deep dive guide — GitLab Container Registry](gitlab/docs/GITLAB_REGISTRY.md)
- [Brainstorm prompt](gitlab/docs/BRAIN_STORM.md)

### React Core

Study notes for React internals, rendering model, fiber architecture, concurrent rendering, state architecture, and production-grade frontend engineering.

- [Concept overview](react/README.md)
- [Deep dive guide](react/docs/CORE_REACT.md)
- [Brainstorm prompt](react/docs/BRAIN_STORM.md)

### TypeScript

Comprehensive learning path and engineering guide for TypeScript: from beginner concepts to compiler-level mental models and large-scale architecture thinking.

- [Concept overview](typescript/README.md)
- [Ultimate deep-dive guide](typescript/docs/TS_ULTIMATE.md)
- [Brainstorm prompt](typescript/docs/BRAIN_STORM.md)

### Frontend System Design — Monorepo Architecture

Complete engineering guide for monorepo architecture: dependency graphs, build orchestration, incremental builds, remote caching, CI optimization, and organization-scale patterns.

- [Concept overview](system-design/frontend/README.md)
- [Deep dive guide — Monorepo](system-design/frontend/docs/MONOREPO.md)
- [Deep dive guide — Accessibility](system-design/frontend/docs/ACCESSIBILITY.md)
- [Brainstorm prompt](system-design/frontend/docs/BRAIN_STORM.md)

### System Design — Frontend

Study notes for frontend system design, accessibility (A11Y), monorepo architecture, and production-grade frontend engineering.

- [Concept overview](system-design/frontend/README.md)
- [Deep dive — Accessibility](system-design/frontend/docs/ACCESSIBILITY.md)
- [Deep dive — Monorepo](system-design/frontend/docs/MONOREPO.md)
- [Brainstorm prompt](system-design/frontend/docs/BRAIN_STORM.md)

### Vite

Complete engineering guide for Vite: from beginner usage to build-system architecture, plugin development, HMR internals, module graph algorithms, and tooling engineer mindset.

- [Concept overview](vite/README.md)
- [Deep dive guide](vite/docs/VITE.md)
- [Brainstorm prompt](vite/docs/BRAIN_STORM.md)

### Browser — Web Vitals

Comprehensive engineering guide to Core Web Vitals (LCP, CLS, INP), supporting metrics, browser rendering pipeline, React/Next.js/Astro optimization, performance tooling, and production monitoring strategy.

- [Concept overview](browser/README.md)
- [Deep dive guide — Web Vitals](browser/docs/WEB_VITALS.md)
- [Brainstorm prompt](browser/docs/BRAIN_STORM.md)

## Suggested structure

- README.md — repository home and concept index
- <topic>/README.md — concept overview
- <topic>/docs/*.md — detailed research notes
- <topic>/assets/ — diagrams, screenshots, and reference images

## How to use this repo

1. Pick a topic to research.
2. Create a folder for the topic.
3. Add a README that explains the concept at a high level.
4. Add supporting docs for deeper analysis, tradeoffs, examples, and open questions.
5. Keep links from this root README updated as new concepts are added.

## Notes

The current focus is Nix Flakes, but this repository can grow to cover broader topics such as platform engineering, distributed systems, software architecture, and system design.
