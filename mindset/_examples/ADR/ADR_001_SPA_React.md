# ADR-001: Use React SPA Architecture

**Status:** Accepted
**Date:** 2026-06-13

## Context
We're building a highly interactive internal dashboard with frequent client-side interactions (filtering, real-time updates, complex forms). SEO is not a requirement since the app sits behind authentication.

## Decision
We will build the application as a **client-side rendered Single Page Application using React**, with routing handled by React Router.

## Alternatives Considered
- **Next.js (SSR/SSG)** — Pros: SEO, server rendering, file-based routing / Cons: added build/deploy complexity, server runtime required / Why rejected: no SEO need; adds overhead for an internal tool.
- **Multi-page app (MPA) with server-rendered templates** — Pros: simple, no JS framework needed / Cons: poor UX for highly interactive UI, full page reloads / Why rejected: doesn't fit the interaction-heavy requirements.
- **React SPA (Chosen)** — Pros: fast client-side navigation, rich interactivity, simple static hosting / Cons: slower initial load, no SEO, requires client-side auth handling / Why chosen: best fit for an internal, interaction-heavy tool with simple deployment.

## Consequences
- **Positive:** Fast navigation after initial load; simple static hosting (CDN); large React ecosystem available.
- **Negative:** Larger initial bundle/load time; no SEO; need client-side handling for auth redirects and loading states.
- **Other:** Need a strategy for code-splitting routes to manage bundle size as the app grows.

## Lessons Learned (fill in 6–12 months later)
Did we get the expected benefits? Were trade-offs acceptable? Any surprises? Same decision today?