# ADR-005: Adopt a Monorepo with pnpm + Turborepo

**Status:** Accepted
**Date:** 2026-06-13

## Context
We anticipate multiple frontend applications (e.g. main app, admin dashboard) that share UI components, schemas, and configuration. We need to share code without publishing/versioning internal npm packages, while keeping CI fast as the codebase grows.

## Decision
We will use a **monorepo managed with pnpm workspaces and Turborepo**, structured as `apps/*` for deployable applications and `packages/*` for shared code (UI kit, schemas, config, API client).

## Alternatives Considered
- **Separate repositories per app, with published internal npm packages for shared code** — Pros: clear separation, independent deploy cadences / Cons: versioning/publishing overhead for shared packages, slower iteration when shared code changes, dependency drift between repos / Why rejected: too much overhead for our team size and the tight coupling between apps and shared schemas/UI.
- **Single repo, no workspace tooling (shared code via relative imports across app folders)** — Pros: simplest setup / Cons: no dependency graph awareness, no caching, easy to create accidental coupling / Why rejected: doesn't scale CI performance or enforce boundaries between packages.
- **pnpm + Turborepo monorepo (Chosen)** — Pros: fast installs via pnpm, Turborepo caching and "affected-only" task running, easy code sharing without publishing / Cons: initial setup/config complexity, all apps share a single repo history and CI pipeline / Why chosen: best balance of code-sharing ease and CI performance for our planned multi-app setup.

## Consequences
- **Positive:** Shared packages (UI kit, Effect schemas, config) consumed directly without publish/version steps; Turborepo caches builds/tests, keeping CI fast; single source of truth for shared contracts.
- **Negative:** Initial tooling setup (workspace config, Turborepo pipeline config) adds complexity; a single repo means all apps share CI infrastructure and release coordination needs more care.
- **Other:** Define `turbo.json` pipeline tasks (build, lint, test) with proper caching and dependency graph; establish conventions for adding new apps/packages to the workspace.

## Lessons Learned (fill in 6–12 months later)
Did we get the expected benefits? Were trade-offs acceptable? Any surprises? Same decision today?