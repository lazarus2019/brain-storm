# ADR-004: Use Effect Schema for Runtime Data Validation

**Status:** Accepted
**Date:** 2026-06-13

## Context
API responses are not guaranteed to match our TypeScript types at runtime (backend changes, network issues, third-party APIs). We need runtime validation at the network boundary that also produces accurate TypeScript types, ideally with composable error handling.

## Decision
We will use **Effect Schema** (`@effect/schema`) to define and validate data shapes for all data crossing the network boundary (API requests/responses), with TypeScript types inferred from schemas rather than maintained separately.

## Alternatives Considered
- **Zod** — Pros: very popular, simple API, large ecosystem / Cons: not integrated with a broader effect-management system; error handling is separate from async/data-fetching logic / Why rejected: team wants a unified approach to async + validation + error handling via Effect.
- **No runtime validation (trust TypeScript types only)** — Pros: zero overhead, simplest / Cons: TypeScript types are not enforced at runtime; bad data can silently flow through the app / Why rejected: too risky for data integrity, especially with evolving APIs.
- **Effect Schema (Chosen)** — Pros: runtime validation + type inference in one definition, integrates with Effect's composable error handling and retry logic, schemas reusable across frontend/backend in monorepo / Cons: requires learning the Effect ecosystem, smaller community than Zod / Why chosen: aligns with broader move to Effect for async/data-fetching logic and enables shared schema packages across apps.

## Consequences
- **Positive:** Runtime-validated data with inferred types eliminates type/schema drift; composable error handling for parsing failures; schemas can be shared in a monorepo package between frontend and backend.
- **Negative:** Team must learn Effect concepts (Effect.gen, pipe, etc.), which is a different paradigm from typical async/await code; smaller ecosystem/community support compared to Zod.
- **Other:** Create a shared `packages/schemas` package for contracts used by multiple apps; provide internal documentation/examples for common Effect Schema patterns to ease onboarding.

## Lessons Learned (fill in 6–12 months later)
Did we get the expected benefits? Were trade-offs acceptable? Any surprises? Same decision today?