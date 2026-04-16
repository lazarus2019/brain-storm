# GitLab CI/CD

Study notes for CI/CD automation, pipeline design, deployment strategies, and platform engineering with GitLab CI/CD.

## Contents

- [Deep dive guide](docs/GITLAB_CI.md) — Complete engineering guide covering pipeline architecture, `.gitlab-ci.yml` syntax, runners, stages, jobs, artifacts, caching, environments, deployment strategies, monorepo patterns, security scanning, and organization-scale governance.
- [Brainstorm prompt](docs/BRAIN_STORM.md) — The prompt used to generate the deep dive guide.

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
