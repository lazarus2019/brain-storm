# ADR-003: Use Zustand for Client-Side State Management

**Status:** Accepted
**Date:** 2026-06-13

## Context
The app needs to manage client/UI state (e.g. modals, filters, cart contents, selection state) separate from server data (which is handled by a data-fetching library). We want minimal boilerplate and a low learning curve for a team of varying experience levels.

## Decision
We will use **Zustand** for client/UI state management, with one store per domain colocated in the relevant entity/feature's `model/` segment. Server state will continue to be managed by TanStack Query, not Zustand.

## Alternatives Considered
- **Redux Toolkit** — Pros: mature ecosystem, strong devtools, well-known patterns / Cons: more boilerplate (actions, reducers, slices), steeper learning curve / Why rejected: overhead not justified for our state needs.
- **React Context + useReducer** — Pros: no extra dependency, built into React / Cons: performance issues with frequent updates, verbose for complex state, re-render management is manual / Why rejected: doesn't scale well for frequently-updated state across many components.
- **Zustand (Chosen)** — Pros: minimal boilerplate, hook-based API, good performance (selective subscriptions), easy to colocate with FSD slices / Cons: less opinionated structure (can lead to inconsistent patterns without conventions), smaller ecosystem than Redux / Why chosen: best fit for our team size and state complexity; pairs naturally with FSD's `model/` segments.

## Consequences
- **Positive:** Significantly less boilerplate than Redux; easy to colocate stores with their owning feature/entity; good render performance via selective subscriptions.
- **Negative:** Less enforced structure than Redux — need team conventions to avoid inconsistent store patterns; smaller pool of community middleware/tools.
- **Other:** Establish a convention doc for store naming, file location, and when to use Zustand vs TanStack Query (client state vs server state).

## Lessons Learned (fill in 6–12 months later)
Did we get the expected benefits? Were trade-offs acceptable? Any surprises? Same decision today?