# ADR-002: Adopt Feature-Sliced Design (FSD) for Code Organization

**Status:** Accepted
**Date:** 2026-06-13

## Context
Multiple teams will work on the same frontend codebase, each owning different features. We need a folder structure that gives clear ownership boundaries, prevents circular dependencies, and scales as the number of features grows.

## Decision
We will organize the codebase using **Feature-Sliced Design**, with layers `app → pages → widgets → features → entities → shared`, where higher layers may import from lower layers but not vice versa.

## Alternatives Considered
- **Flat structure (`components/`, `pages/`, `hooks/`, `utils/`)** — Pros: simple to start, no learning curve / Cons: unclear ownership, imports become tangled as app grows / Why rejected: doesn't scale past a few features or teams.
- **Domain-Driven folders by team name** — Pros: maps to org structure / Cons: encourages duplication across teams, no shared conventions for internal slice structure / Why rejected: lacks the layering rules that prevent circular deps.
- **Feature-Sliced Design (Chosen)** — Pros: explicit layer/import rules, consistent slice structure (`ui/model/api/lib`), well-documented conventions, good for parallel team ownership / Cons: learning curve, can feel like overhead for tiny features / Why chosen: best balance of structure and scalability for a multi-team codebase.

## Consequences
- **Positive:** Clear ownership per feature/entity slice; import direction rules prevent circular dependencies; consistent structure makes onboarding easier.
- **Negative:** Initial learning curve for engineers unfamiliar with FSD; small features may feel over-structured; requires discipline to keep slices properly scoped.
- **Other:** Enforce layer import rules via `eslint-plugin-boundaries` (or similar) in CI; document slice conventions in the repo README.

## Lessons Learned (fill in 6–12 months later)
Did we get the expected benefits? Were trade-offs acceptable? Any surprises? Same decision today?