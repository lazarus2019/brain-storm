# GitHub Actions

Study notes for CI/CD automation, deployment pipelines, release engineering, and platform engineering with GitHub Actions.

## What this covers

- GitHub Actions concepts: workflows, events, jobs, steps, runners, actions, matrix, artifacts, cache, environments, secrets
- Progressive learning roadmap from newbie to expert
- Setup guides for React, Next.js, Astro, and static sites
- Deployment to Vercel, Cloudflare Pages, GitHub Pages, AWS, and Docker registries
- Production-grade patterns: reusable workflows, composite actions, OIDC, security hardening
- Organization-scale platform engineering and governance

## Docs

- [Deep dive guide](docs/GITHUB_ACTION.md) — Complete learning path and engineering reference
- [Brainstorm prompt](docs/BRAIN_STORM.md) — The AI prompt used to generate the guide

## Key takeaways

- GitHub Actions is an event-driven automation engine, not just CI.
- Treat workflow code as production code — version it, test it, secure it.
- Start simple (single-job CI), evolve to parallel jobs, then to reusable workflows and platform patterns.
- Always cache dependencies, protect production with environments, and design for rollback.
