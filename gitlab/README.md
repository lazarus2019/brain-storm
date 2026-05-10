# GitLab CI/CD

Study notes for CI/CD automation, pipeline design, deployment strategies, and platform engineering with GitLab CI/CD.

## Contents

- [Deep dive guide — GitLab CI/CD](docs/GITLAB_CI.md) — Complete engineering guide covering pipeline architecture, `.gitlab-ci.yml` syntax, runners, stages, jobs, artifacts, caching, environments, deployment strategies, monorepo patterns, security scanning, and organization-scale governance.
- [Roadmap — GitLab CI Roadmap](docs/GITLAB_CI_ROADMAP.md) — Roadmap and step-by-step guide from basics to production-grade pipelines, patterns, and recommendations.
- [Deep dive guide — GitLab Container Registry](docs/GITLAB_REGISTRY.md) — Complete engineering guide covering container image storage, tagging strategies, CI integration, image promotion, security scanning, cleanup policies, monorepo image organization, and supply chain security.
- [Brainstorm prompt](docs/BRAIN_STORM.md) — The prompts used to generate the deep dive guides.

## Key topics covered

- Pipeline lifecycle: push → stages → jobs → deployment
- `.gitlab-ci.yml` syntax: stages, jobs, rules, needs, extends, include
- Runners: shared, group, project, self-hosted, Kubernetes executor
- Caching and artifacts for fast, reliable pipelines
- Merge request pipelines and workflow rules
- Environment promotion: staging → production with manual gates
- Docker image builds with DinD and Kaniko
- Dynamic child pipelines for monorepos
- Shared CI templates across projects
- Security scanning (SAST, dependency, container, secret detection)
- OIDC-based cloud authentication
- Cost optimization and pipeline performance
- Release automation and rollback strategies

## Who this is for

Frontend engineers (React, Next.js, Astro, TypeScript) expanding into DevOps, CI/CD, and platform engineering — with practical YAML examples and framework-specific pipeline templates.
