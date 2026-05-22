---
title: Architecture Decision Records (ADRs)
description: Complete ADR deep-dive guide covering technical decision-making, trade-off analysis,
  governance patterns, documentation standards, Staff+/Principal engineering mindset,
  organizational architecture, and enterprise-scale decision frameworks
slug: adrs-architecture-decision-records
modifiedDate: '2026-05-22'
draft: false
featured: true
tags:
- architecture
- adrs
- decision-records
- engineering-governance
- staff-plus
- technical-leadership
- platform-engineering
- system-design
- organizational-architecture
categories:
- mindset
- architecture
seo:
  title: Architecture Decision Records (ADRs) — Ultimate Deep-Dive Guide
  description: Complete ADR engineering guide covering technical decision-making, trade-off
    analysis, documentation standards, governance patterns, Staff+/Principal engineering,
    organizational architecture, and enterprise decision frameworks
  canonical: https://feel-free.com/blogs/adrs-architecture-decision-records
  keywords:
  - architecture decision records
  - adrs
  - technical decisions
  - engineering governance
  - architecture patterns
  - system design
  - staff plus engineering
  - decision-making frameworks
author: lazarus2019
lang: en
relatedPosts:
- rfcs
- sdk
---

# Architecture Decision Records (ADRs) — Ultimate Deep-Dive Guide

A complete engineering guide from beginner concepts to Staff+/Principal-level architecture thinking, technical governance, and enterprise-scale decision frameworks.

---

## Table of Contents

1. [Big Picture](#1-big-picture)
2. [Technical Decision-Making Deep Dive](#2-technical-decision-making-deep-dive)
3. [ADR Structure & Standards](#3-adr-structure--standards)
4. [Architecture Thinking & Trade-Off Analysis](#4-architecture-thinking--trade-off-analysis)
5. [Staff+/Principal Engineering Mindset](#5-staffprincipal-engineering-mindset)
6. [ADRs for Frontend / React / Next.js / Astro](#6-adrs-for-frontend--react--nextjs--astro)
7. [Organizational Architecture Governance](#7-organizational-architecture-governance)
8. [ADR Lifecycle & Decision Evolution](#8-adr-lifecycle--decision-evolution)
9. [Real-World ADR Examples](#9-real-world-adr-examples)
10. [Setup Guide](#10-setup-guide)
11. [Tooling Comparison](#11-tooling-comparison)
12. [Cheatsheet](#12-cheatsheet)
13. [Real-World Engineering Mindset](#13-real-world-engineering-mindset)
14. [Brainstorm / Open Questions](#14-brainstorm--open-questions)
15. [Practice Questions](#15-practice-questions)
16. [Personalized Recommendations](#16-personalized-recommendations)
17. [Official Documentation & Reference Links](#17-official-documentation--reference-links)
18. [Advanced Engineering Topics](#18-advanced-engineering-topics)

---

## 1. Big Picture

### What ADRs Actually Are

Architecture Decision Records (ADRs) are **documented technical decisions** that explain:

1. **What decision was made** — The choice made
2. **Why it was made** — The context, constraints, and problem
3. **What trade-offs existed** — Alternatives and why they were rejected
4. **What the consequences are** — Immediate and long-term implications
5. **When to reconsider** — Conditions that might invalidate the decision

An ADR is NOT:
- A design document (too detailed)
- A technical proposal (before decision)
- A requirement spec (before implementation)
- A code comment (local decision)
- A wiki page (informal knowledge)

An ADR IS:
- A decision artifact (immutable record)
- A communication tool (explains intent)
- An organizational memory (preserves context)
- A learning device (documents trade-offs)
- A governance mechanism (establishes standards)

### Why ADRs Exist

```
┌──────────────────────────────────────────────────────────────┐
│          Problems ADRs Solve                                  │
├──────────────────────────────────────────────────────────────┤
│                                                                │
│  WITHOUT ADRs:                                               │
│    - Why was this technology chosen? (nobody knows)          │
│    - Who made this decision? (lost context)                  │
│    - Can we change it? (fear of breaking things)             │
│    - What alternatives existed? (forgotten)                   │
│    - Why did we abandon that pattern? (repeated mistakes)    │
│    - New engineers repeat old decisions (no institutional    │
│      memory)                                                   │
│    - Architectural drift (no clear standards)                │
│    - Blame-focused incident analysis (no context)           │
│                                                                │
│  WITH ADRs:                                                  │
│    ✓ Decision rationale documented forever                   │
│    ✓ Trade-offs explicitly recorded                          │
│    ✓ Why alternatives rejected remains visible              │
│    ✓ New team members learn organizational thinking         │
│    ✓ Migration decisions are informed and intentional        │
│    ✓ Architecture evolves deliberately                       │
│    ✓ Incident analysis focuses on learning                  │
│    ✓ Governance emerges from documentation                  │
│                                                                │
└──────────────────────────────────────────────────────────────┘
```

### ADR vs RFC vs Design Document vs Standards

| Document Type | Timing | Formality | Immutable | Purpose | Lifecycle |
|---|---|---|---|---|---|
| **ADR** | After decision | Medium | Yes (with amendments) | Record a decision + reasoning | Accepted → Superseded → Deprecated |
| **RFC** | Before decision | High | No (evolves during review) | Propose & discuss a decision | Draft → Review → Merged/Rejected |
| **Design Doc** | During implementation | High | No (updates during dev) | Detailed implementation plan | Evolves → Archived |
| **Standard** | Post-decision | Medium | Semi (updated by new ADRs) | Establish organizational norms | Proposed → Enforced → Deprecated |
| **Wiki** | Informal | Low | No (constantly updated) | Knowledge repository | Evolves indefinitely |

**Key insight:** ADRs document the **decision**, not the implementation. A single ADR might have multiple design documents as it's implemented across different systems.

### Engineering Decision Lifecycle

```
┌──────────────────────────────────────────────────────────────┐
│       Complete Decision Lifecycle                             │
├──────────────────────────────────────────────────────────────┤
│                                                                │
│  1. PROBLEM EMERGES                                          │
│     Current architecture shows strain                        │
│     Decision needed (explicit or implicit)                    │
│                                                                │
│  2. DISCOVERY PHASE                                          │
│     Understand problem deeply                                │
│     Identify constraints (technical, business, org)          │
│     Research options (vendors, approaches, patterns)        │
│     Estimate trade-offs (cost, complexity, risk)            │
│                                                                │
│  3. OPTION ANALYSIS PHASE                                    │
│     Document options in detail                              │
│     Compare on dimensions:                                   │
│       - Technical correctness                                │
│       - Maintainability                                      │
│       - Operational complexity                               │
│       - Learning curve                                       │
│       - Migration cost                                       │
│       - Vendor lock-in risk                                  │
│       - Team capability                                      │
│       - Scalability headroom                                 │
│                                                                │
│  4. STAKEHOLDER ALIGNMENT PHASE                              │
│     Gather input from affected teams                         │
│     Address concerns                                         │
│     Build consensus                                          │
│     Document minority views                                  │
│                                                                │
│  5. DECISION PHASE                                           │
│     Decision maker chooses option                            │
│     May choose compromise not on original list               │
│     Decision recorded (ADR written)                          │
│                                                                │
│  6. ANNOUNCEMENT PHASE                                       │
│     ADR socialized to organization                           │
│     Implementation guidance provided                         │
│     Timeline communicated                                    │
│                                                                │
│  7. IMPLEMENTATION PHASE                                     │
│     Teams apply decision                                     │
│     Deviations escalated & documented                        │
│     Migration completed                                      │
│                                                                │
│  8. EVALUATION PHASE                                         │
│     After 3-12 months, assess results                        │
│     Did we get expected benefits?                            │
│     Were trade-offs acceptable?                              │
│     New consequences emerged?                                │
│     Feedback added to ADR                                    │
│                                                                │
│  9. EVOLUTION PHASE                                          │
│     As context changes, decision may need revision           │
│     ADR is superseded by new ADR (old one stays)            │
│     Historical decisions remain readable                     │
│                                                                │
└──────────────────────────────────────────────────────────────┘
```

### When ADRs Become Critical

ADRs become essential when:

| Situation | Why | Consequence of NOT having ADRs |
|-----------|-----|--------------------------------|
| **Multi-team systems** | Decisions affect many teams | Each team makes own decisions → chaos |
| **Long-lived systems** | Context fades over time | New hires repeat old mistakes |
| **High consequences** | Wrong choice is expensive | Teams fear making changes |
| **Frequent migrations** | Change happens regularly | No institutional learning |
| **Distributed teams** | Async communication needed | Context gets lost in Slack/email |
| **Compliance required** | Governance audits | No proof of decision-making process |
| **New domain** | Establishing patterns | Each team creates own standards |
| **Post-incident** | Learning from failures | Blame → same incident repeats |

### Real-World Business Impact

```
Example: Architecture Decision Maturity

LEVEL 0 - No ADRs (Chaos)
  - Inconsistent technology stacks per team
  - 6 different state management solutions
  - 3 different build tools
  - Onboarding takes 3 months
  - Migration attempts fail repeatedly
  - Same design questions answered 100 times
  → Cost: High engineering attrition, slow delivery

LEVEL 1 - Reactive ADRs (Some Order)
  - Major decisions documented after the fact
  - Better than nothing, but incomplete
  - Some decisions never recorded
  - Patterns still inconsistent
  → Cost: Partial improvement, still chaotic

LEVEL 2 - Systematic ADRs (Mature)
  - All major decisions documented
  - Clear ADR templates & processes
  - Architecture review board
  - New engineers onboard quickly
  - Migrations deliberate & planned
  → Cost: Overhead of process, but massive delivery improvement

LEVEL 3 - Living Architecture Governance (Excellent)
  - ADRs actively reviewed & evolved
  - Architecture observability (we track adherence)
  - Automation enforces decisions (linting, CI checks)
  - Architectural review integrated with incident analysis
  - Platform engineering enables decisions
  → Cost: Significant organizational investment, but industry-leading results

LEVEL 4 - Architecture as Strategic Asset (World-Class)
  - Architecture decisions drive business strategy
  - ADRs inform product decisions
  - Architecture enables rapid experimentation
  - Competitive advantage through better systems thinking
  → This is what Google, Amazon, Netflix operate at
```

---

## 2. Technical Decision-Making Deep Dive

### How Senior Engineers Evaluate Decisions

Senior engineers don't choose the "best" technology. They choose the **best trade-off for context**.

**Decision Analysis Framework:**

```
┌──────────────────────────────────────────────────────────────┐
│         Senior Engineer Decision Framework                    │
├──────────────────────────────────────────────────────────────┤
│                                                                │
│  STEP 1: Understand the real problem                         │
│    - What's broken NOW?                                      │
│    - What business outcome needed?                           │
│    - What constraints exist?                                 │
│    - What's the actual scope?                                │
│                                                                │
│  STEP 2: Reject false dichotomies                            │
│    - "We need to choose between A and B"                     │
│    - Usually: multiple paths, compromises, hybrid solutions  │
│    - Question if those are really the only options           │
│                                                                │
│  STEP 3: Identify decision dimensions                        │
│    - Technical correctness (does it solve the problem?)      │
│    - Maintenance (3-year cost, not year-1 cost)             │
│    - Team capability (can we operate this?)                  │
│    - Organizational alignment (fits our strategy?)           │
│    - Migration path (can we reverse it if wrong?)            │
│    - Scaling headroom (works at 10x scale?)                  │
│    - Operational simplicity (can we monitor/debug it?)       │
│    - Learning curve (time to productive?)                    │
│    - Risk (what breaks this choice?)                         │
│                                                                │
│  STEP 4: Rank dimensions by importance                       │
│    - Different teams rank differently (correct!)             │
│    - Product teams: speed to market                          │
│    - Platform teams: operational simplicity                  │
│    - Startup: flexibility                                    │
│    - Enterprise: supportability                              │
│                                                                │
│  STEP 5: Evaluate options on each dimension                 │
│    - Not pass/fail, but scored 1-5 or "tradeoff"           │
│    - Document the reasoning                                  │
│    - Accept that no option is best on all dimensions         │
│                                                                │
│  STEP 6: Choose based on context                             │
│    - For startup: flexibility + speed wins                   │
│    - For scale-up: stability + operational wins              │
│    - For enterprise: governance + risk-reduction wins        │
│                                                                │
│  STEP 7: Document the reasoning                              │
│    - This becomes the ADR                                    │
│    - Future you will thank present you                       │
│                                                                │
└──────────────────────────────────────────────────────────────┘
```

### Why Trade-Offs Matter More Than Best Practices

```
"But Google uses X, so we should use X"
→ WRONG reasoning (context differs)

"X is best-in-class"
→ Best for WHAT use case and scale?

"Microservices at scale"
→ You're 10 people and $0 revenue

"We need to be Netflix"
→ First: be profitable at your scale
```

**Key insight:** The best architecture for Google (10,000+ engineers, global scale, unlimited resources) is terrible for a 15-person startup (needs speed, simplicity, flexibility).

### Hidden Trade-Offs

Every architectural choice has hidden costs:

| Choice | Explicit Benefit | Hidden Cost | When It Matters |
|--------|-----------------|-------------|----------------|
| **Microservices** | Independent scaling, team autonomy | Distributed debugging, network latency, consistency complexity | 50+ engineers |
| **Monolith** | Simplicity, shared database | Scaling bottleneck, deployment coupling | 200+ engineers |
| **React** | Rich UX, component reuse | Bundle size, runtime performance, client CPU | Mobile users, low-end devices |
| **Astro** | Performance, simple HTML | Learning new paradigm, SSR complexity | Multiple pages, SEO-critical |
| **TypeScript** | Type safety, developer experience | Compilation time, build tooling complexity | Large teams, complex domains |
| **Strict CSP** | Security, XSS prevention | Nonce infrastructure, development friction | High-security apps, regulated orgs |
| **GraphQL** | Flexible queries, no overfetching | N+1 problem, caching complexity, learning curve | Complex APIs, many clients |
| **Docker** | Reproducibility, isolation | Container orchestration, image management | Microservices, multi-environment |

### Long-Term Architecture Degradation

Decisions that seem good initially often degrade:

```
Example: Monolith that became pain

YEAR 1: Monolith
  - Simplicity! Everything works
  - Deploy once per day
  - One database
  - Easy to debug
  - "This is great"

YEAR 2: Monolith grows
  - 50 engineers touching same codebase
  - Deploy conflicts, 3 per day
  - One database gets slow
  - Hard to debug (everything interconnected)
  - "Maybe we should split this"

YEAR 3: Monolith becomes bottleneck
  - 100+ engineers, constant merge conflicts
  - Deploy takes 1 hour, multiple failures per week
  - Database needs sharding
  - Buggy code in one module breaks everything
  - "We need microservices!"

YEAR 4+: Migration attempt
  - Half our engineering capacity spent on migration
  - Distributed debugging now harder than old monolith
  - Operational complexity exploded
  - Database consistency issues (new problem)
  - "Why did we migrate again?"

LESSON: Monolith was RIGHT for years 1-2. It became WRONG gradually.
        The mistake wasn't choosing monolith initially.
        The mistake was not acknowledging when context changed.
        A good decision becomes a bad decision when context changes.
```

### The Organizational Structure Determines Architecture

**Conway's Law:** *The architecture of a system mirrors the communication structure of the organization that built it.*

```
Example: Frontend Architecture Decisions

30-person startup (1 frontend team):
  - Monorepo, shared design system, standardized tooling
  - Fast iteration, shared libraries
  - "Let's use whatever works best"

100-person company (4 frontend teams):
  - Each team had different preferences
  → Created different stacks
  → Can't share code between teams
  → Chaos during cross-team projects
  SOLUTION: Establish standard stack via ADR

500-person company (20 frontend teams):
  - Need Platform Engineering team
  - Establish "golden path" (recommended setup)
  - Teams can deviate with approval
  - Platform team solves shared problems
  - ADRs coordinate decisions
  → Enables scale while allowing autonomy

5000+ person company (200+ frontend teams):
  - Federated architecture governance
  - Platform team sets principles, not rules
  - Teams own their decisions
  - Architecture review board resolves disputes
  - ADRs establish precedent
  - Automated architecture observability
  → Different teams can have different stacks while staying coherent
```

---

## 3. ADR Structure & Standards

### The MADR (Markdown ADR) Template

MADR is the standard ADR format (used by Thoughtworks, AWS, many others).

```markdown
# ADR-XXX: [Title of decision]

## Status

[Accepted | Proposed | Deprecated | Superseded by ADR-YYY]

## Context

Describe the issue, constraints, and background.
- What problem exists?
- What are the constraints?
- What business context matters?
- Who is affected?

## Decision

State the decision unambiguously.
"We will [DECISION]."

## Consequences

### Positive
- Benefit 1
- Benefit 2

### Negative
- Trade-off 1
- Trade-off 2

### Other
- Consideration 1
- Consideration 2

## Alternatives Considered

### Option A (Rejected)
- Pros: 
- Cons: 
- Why rejected:

### Option B (Rejected)
- Pros:
- Cons:
- Why rejected:

### Option C (Chosen)
- Pros:
- Cons:
- Why chosen:

## Lessons Learned (optional, added after implementation)

(6-12 months after acceptance)
Did we get the expected benefits?
Were the trade-offs acceptable?
What surprised us?
Would we make the same decision today?
```

### Why Each Section Matters

| Section | Why | Common Mistakes |
|---------|-----|-----------------|
| **Status** | Track ADR lifecycle | Forgetting to update when superseded |
| **Context** | Explain WHY (most important) | Too brief, losing context | 
| **Decision** | Be unambiguous | Vague language ("prefer", "consider") |
| **Consequences** | Explain trade-offs | Only positive consequences |
| **Alternatives** | Show reasoning | Not documenting rejected options |
| **Lessons Learned** | Enable iteration | Never updating after implementation |

### ADR Naming & Organization

```
ADR folder structure (monorepo example):

docs/architecture/decisions/
  README.md (index of all ADRs)
  ADR-001-use-nextjs-app-router.md
  ADR-002-monorepo-structure.md
  ADR-003-state-management-zustand.md
  ADR-004-design-system-strategy.md
  ADR-005-feature-flag-platform.md
  ...
  
Naming convention:
  ADR-XXX-short-description.md
  Where XXX = zero-padded number (001, 002, ...)
  Description = hyphenated, lowercase, concise
  
Numbering:
  Sequential (no gaps)
  New ADRs get next number
  Never reuse numbers (immutability)
  If ADR is replaced: old stays, new one references it
```

### ADR Review Workflow

```
Git workflow for ADRs:

1. Developer creates ADR-XXX.md in feature branch
2. Create PR with ADR for discussion
3. Code review process:
   - Stakeholders comment
   - Developer addresses concerns
   - May iterate on decision/options
4. Once consensus: PR merged
5. ADR status = "Accepted"
6. Implementation begins (may be separate from ADR PR)
7. After 6-12 months: "Lessons Learned" section added
8. If decision needs changing: new ADR written (old stays, marked "Superseded by ADR-YYY")

Key principle: ADRs document decisions, not implementation details
```

---

## 4. Architecture Thinking & Trade-Off Analysis

### Scalability Trade-Offs

| Architecture | Scales To | Pros | Cons | When To Use |
|---|---|---|---|---|
| **Monolith + Monorepo** | 50 engineers | Simple, shared code, easy debugging | Deployment coupling, scaling bottleneck | 1-50 person teams |
| **Modular Monolith** | 100 engineers | Better boundaries, independent modules | Still single deployment | 50-100 person teams |
| **Microservices** | 500+ engineers | Independent scaling, team autonomy | Distributed systems complexity, debugging | 100+ engineers, multiple teams |
| **Federated Platforms** | 5000+ engineers | Full autonomy, ownership | Governance overhead, coordination challenges | Enterprise with many teams |

### Maintainability Trade-Offs

**Code written vs. code maintained:**

```
The 80/20 rule applies differently:

80% of code costs are in MAINTENANCE, not initial writing.

Initial write: 1 month
Maintain for 5 years: 59 months

So decisions should optimize for:
  - Readability (not cleverness)
  - Debuggability (not performance hacks)
  - Simplicity (not elegance)
  - Team capability (not "best practice")
  - Context clarity (not assumptions)
```

### Framework Comparison (React vs Astro)

**When building a new application:**

| Dimension | React | Astro | Winner for... |
|-----------|-------|-------|---|
| **Developer experience** | Excellent | Excellent | Tie |
| **Initial load time** | Slow (JS bundle) | Fast (HTML-first) | Astro |
| **Interactivity** | Instant (SPA) | Islands (slower) | React |
| **SEO** | Good (SSR) | Excellent (default) | Astro |
| **Scalability** | Great (many patterns) | Good (simpler) | React |
| **Learning curve** | Moderate | Low | Astro |
| **Ecosystem** | Massive | Growing | React |
| **Operational complexity** | High (React server) | Low (mostly static) | Astro |

**Decision:**
- **Astro:** Blog, docs, marketing (content-focused, performance matters)
- **React:** App, dashboard, real-time (interaction-heavy, features matter)
- **Hybrid:** Use Astro for marketing, React for app (common pattern)

### Monorepo vs Polyrepo

This is a **structural decision** that affects everything:

| Factor | Monorepo | Polyrepo |
|--------|----------|----------|
| **Code sharing** | Easy (shared imports) | Hard (versioned packages) |
| **Atomic changes** | Easy (single commit) | Hard (multiple PRs) |
| **Standardization** | Easy (one setup) | Hard (many setups) |
| **Team independence** | Hard (conflicts) | Easy (own repos) |
| **Complexity** | High (one big repo) | High (many coordinations) |
| **Scaling to 100+ teams** | Difficult | Better |
| **New developer onboarding** | Easier (one clone) | Harder (multiple clones) |

**Industry consensus:**
- Monorepo for 10-50 engineers (Google, Facebook, Twitter use it)
- Polyrepo for 100+ engineers with clear domain boundaries
- Hybrid for middle ground

---

## 5. Staff+/Principal Engineering Mindset

### What Staff+ Engineers Think Differently

Junior engineer: "What's the best way to implement this?"
→ Focuses on code quality, patterns, best practices

Senior engineer: "What's the best architecture for our constraints?"
→ Considers team capability, operational complexity, scaling path

Staff+ engineer: "How does this decision affect organization-wide architecture?"
→ Considers long-term strategy, governance, platform implications, organizational structure

**Staff+ decision-making dimensions:**

```
┌──────────────────────────────────────────────────────────────┐
│       Staff+ Engineering Mental Model                         │
├──────────────────────────────────────────────────────────────┤
│                                                                │
│  1. SYSTEMS THINKING                                         │
│     - How does this decision affect other systems?          │
│     - What second-order effects exist?                       │
│     - What's the coupling?                                   │
│     - What's hidden complexity?                              │
│                                                                │
│  2. ORGANIZATIONAL ALIGNMENT                                 │
│     - Does this match our strategy?                          │
│     - Will this be politically acceptable?                   │
│     - Who needs to buy in?                                   │
│     - How do we communicate this?                            │
│                                                                │
│  3. PLATFORM THINKING                                        │
│     - Can this be a platform feature?                        │
│     - How do we enable other teams to use this?             │
│     - What's the developer experience?                       │
│     - What's the operational burden?                         │
│                                                                │
│  4. LONG-TERM TRAJECTORY                                     │
│     - Does this work at 10x scale?                           │
│     - Does this age well?                                    │
│     - What's the migration path?                             │
│     - When will this break?                                  │
│                                                                │
│  5. INFLUENCE WITHOUT AUTHORITY                              │
│     - How do we lead without commanding?                     │
│     - How do we build consensus?                             │
│     - How do we handle dissent?                              │
│     - How do we make decisions when people disagree?         │
│                                                                │
│  6. ENABLEMENT                                               │
│     - How do we make good decisions easy for teams?          │
│     - What guardrails do we need?                            │
│     - What automation helps?                                 │
│     - How do we build institutional knowledge?               │
│                                                                │
└──────────────────────────────────────────────────────────────┘
```

### Architecture as Socio-Technical System

This is perhaps the most important concept:

**Architecture = (Technical System) × (Organizational Structure)**

```
Example: Why monorepo adoption fails

Technical reason to adopt:
  - Easier code sharing
  - Atomic changes
  - Better tooling

But organizational reasons to resist:
  - Loss of team autonomy
  - Everyone's code visible
  - Slower builds as repo grows
  - Blame for breaking others' code
  - "We built things separately for a reason"

Solution: Acknowledge both perspectives
  - Address technical benefits (yes, real)
  - Address organizational concerns (yes, valid)
  - Create process to handle both
  - Build support incrementally
  - Show value over time

That's why monorepo migration takes 6-12 months, not 2 weeks.
```

---

## 6. ADRs for Frontend / React / Next.js / Astro

### Common Frontend ADRs

Most frontend organizations need these ADRs:

1. **Framework choice** (React vs Astro vs Svelte)
2. **State management** (Zustand vs Redux vs Context)
3. **Styling strategy** (Tailwind vs CSS-in-JS vs CSS Modules)
4. **Monorepo organization** (Package structure, build tool)
5. **Testing strategy** (Vitest vs Jest vs Playwright)
6. **Build tooling** (Vite vs Webpack)
7. **Component design** (Patterns, naming conventions)
8. **Design system governance** (Versioning, adoption)
9. **Server rendering** (When to use SSR/SSG)
10. **Feature flags** (How to implement, roll out)

### Example ADR: Choosing React Query (Now TanStack Query)

```markdown
# ADR-013: Adopt React Query for Server State Management

## Status
Accepted (2024-Q1)

## Context

Our application handles complex server-synchronized state:
- Multiple API endpoints
- Real-time data updates
- Offline-first requirements
- Caching & invalidation challenges
- Team has 12 React developers

Previously: Redux + custom middleware (300 lines per API endpoint)
Pain point: Cache invalidation, complex action creators, boilerplate

## Decision

We will adopt TanStack Query (formerly React Query) as our server-state
management library for all new features and gradually migrate existing code.

## Consequences

### Positive
- Reduce API/data-fetching boilerplate by ~70%
- Built-in caching (reduces API calls)
- Automatic background refetching
- Optimistic updates built-in
- Excellent TypeScript support
- Smaller bundle than Redux approach
- Less learning curve than Redux
- Better performance (minimal re-renders)

### Negative
- Adds new dependency (maintenance risk)
- Team learning curve (1-2 weeks)
- Overkill for simple CRUD apps
- Developer unfamiliar with stale-while-revalidate pattern
- Removes some explicit control Redux provided

### Other
- Redux remains for client state (UI state, preferences)
- Not replacement for Redux, but for Redux-async-thunk pattern
- Server state and client state now clearly separated

## Alternatives Considered

### Option A: Keep Redux + middleware
- Pros: Familiar, explicit, full control
- Cons: Boilerplate, painful caching, team frustration
- Why rejected: Doesn't solve the core problem (we're still struggling)

### Option B: SWR (Stale-While-Revalidate library)
- Pros: Simpler, smaller bundle
- Cons: Fewer features, less mature
- Why rejected: React Query handles our use cases better

### Option C: Adopt React Query
- Pros: Mature, feature-rich, solves our problems, industry standard
- Cons: Learning curve, another dependency
- Why chosen: Best balance of features + maturity for our scale

## Implementation Plan
- Week 1: Training & POC
- Week 2-3: Migrate 2 critical pages
- Month 2: Gradual migration of remaining pages
- Q2: Full team adoption

## Lessons Learned (6 months post-decision)

✓ Adoption successful, ~80% of endpoints using React Query
✓ Reduced API calls by 35% (caching working well)
✓ Decreased time-to-implement for new features by 40%
⚠ Bundle size +15KB (acceptable trade-off)
⚠ Debugging async issues takes longer (new patterns)
✓ Team very happy (developer experience much better)

Would make same decision again: YES
```

---

## 7. Organizational Architecture Governance

### Architecture Review Board (ARB)

Large organizations need a structure for architecture decisions:

```
Typical ARB Structure (100+ engineers)

Chair: VP/Principal Engineer
Members (5-7):
  - Platform Engineering Lead
  - Frontend Architecture Lead
  - Backend Architecture Lead
  - Infrastructure Lead
  - Security Lead
  (rotating seats every 2 years)

Processes:
  - Monthly review meetings
  - ADRs reviewed before implementation
  - Emergency decisions allowed (reviewed post-hoc)
  - Escalations from teams go through ARB
  - ARB creates organizational ADRs

Authority balance:
  - ARB doesn't mandate (teams still own decisions)
  - ARB sets principles & guardrails
  - ARB learns from ADRs (improves over time)
  - ARB can override if violates security/compliance
```

### Distributed Ownership Model

As organizations scale, centralized governance breaks:

```
Centralized Governance (works for <100 engineers):
  - Architecture Review Board makes all decisions
  - Top-down enforcement
  - Consistency guaranteed
  Problem: Bottleneck, lack of autonomy, slow decisions

Federated Governance (works for 100-500 engineers):
  - Each domain owns its architecture
  - ARB sets principles, not rules
  - Cross-domain conflicts escalated
  - Shared platforms (DB, cache, etc.) have separate governance
  Problem: Coordination overhead, inconsistency acceptable

Autonomous Governance (works for 500+ engineers):
  - Each team makes its own decisions
  - Principles documented (not mandatory)
  - Architecture observability (we track what choices teams make)
  - Incident analysis feeds back to principles
  Problem: Can drift apart, need strong culture

Amazon operates at autonomous governance level.
Google at federated level.
Most companies at centralized level (even at large scale, wrong choice).
```

---

## 8. ADR Lifecycle & Decision Evolution

### When Decisions Become Wrong

Decisions age over time. Key factors:

| Factor | How It Changes | Impact |
|--------|---|---|
| **Team size** | Grows 5x → changes scaling needs | Monolith becomes bottleneck |
| **Business context** | From startup → enterprise | Speed matters less, stability matters more |
| **Technology maturity** | New tech matures → proven | Makes different choices viable |
| **Market conditions** | Competitive landscape shifts | May need different focus |
| **Organizational structure** | Teams reorganized | May affect architecture fit |
| **Hardware costs** | Scale changes economics | May change compute vs memory trade-offs |

### Superseding ADRs

When a decision needs to change:

```markdown
# ADR-027: Migrate to Monorepo Architecture

## Status
Supersedes ADR-003

## Context
Our polyrepo strategy served us well for 5 years.
But we now have 30 frontend engineers with constant cross-repo coordination.

[Full context explaining why old decision no longer works]

## Decision
We will migrate to a monorepo structure to enable better code sharing
and reduce cross-repo coordination overhead.

## Relationship to ADR-003
ADR-003 established our polyrepo strategy in 2019.
That decision was correct for our scale at that time (15 engineers, 3 teams).
At our current scale (30 engineers, 6 teams), the trade-offs have shifted.

[Reference ADR-003 and why it's no longer optimal]
```

**Key principle:** Never delete old ADRs. Mark them as "Superseded" and link to new ADR.
This preserves organizational history and explains thinking evolution.

---

## 9. Real-World ADR Examples

### Example 1: ADR-001 — Adopt Next.js App Router

```markdown
# ADR-001: Adopt Next.js App Router for New Applications

## Status
Accepted (2024-Q1)

## Context
We built new features on Next.js Pages Router.
Next.js 13+ launched App Router with better defaults for React 18.
Question: Should we migrate existing apps to App Router?

Constraints:
- 3 applications using Pages Router (separate codebases)
- 8 developers familiar with Pages Router
- No immediate deadline (both work)
- Business prefers stability over latest

## Decision
New applications will use App Router.
Existing applications will remain on Pages Router unless team wants to migrate.

## Consequences

### Positive
- Better React 18 integration (Suspense, Server Components)
- Simpler layouts (no need for custom _app.tsx)
- Better TypeScript support
- Modern defaults (less boilerplate)
- Aligns with Next.js long-term direction
- Better for performance (RSC by default)

### Negative
- Forces learning curve for "App Router way"
- Some patterns still evolving (community catching up)
- No migration path for existing apps (costly)
- Ecosystem still catching up (fewer examples)

## Alternatives Considered

### Option A: Migrate all apps to App Router
- Effort: ~8 weeks per app
- Risk: High (breaking changes possible)
- Rejected: Too much effort for marginal benefit

### Option B: New apps use Pages Router (stay consistent)
- Benefit: Consistency
- Cost: Miss App Router benefits
- Rejected: Future-proofs us better to use App Router

### Option C: New apps use App Router (chosen)
- Benefits: Modern defaults, better performance
- Cost: Learning curve
- Why chosen: Right balance of progress and pragmatism

## Migration Plan
- Training: 2 days for team
- Code standards: Update style guide
- Templates: Create App Router templates
- Gradual adoption: Convert pages as we touch them

## Lessons Learned (6 months later)
✓ App Router working well
✓ Server Components feeling natural
✓ Deployment unchanged
⚠ Some edge cases with third-party packages
✓ New developers prefer App Router over Pages Router

Confidence in decision: HIGH
```

### Example 2: ADR-008 — Feature Flags Platform

```markdown
# ADR-008: Adopt LaunchDarkly for Feature Management

## Status
Accepted (2024-Q2)

## Context
We manually deploy features using git branches and environment variables.
This makes:
- A/B testing hard
- Gradual rollouts impossible
- Rollback slow (git revert + redeploy)
- Cross-team feature coordination manual

As we scale to 15+ engineers, this is becoming bottleneck.

## Decision
We will adopt LaunchDarkly as our feature flag platform.
All new feature work will use feature flags for deployment.

## Consequences

### Positive
- Gradual rollouts (1% → 10% → 100%)
- A/B testing built-in
- Instant rollback (no redeployment)
- Better observability (flag vs. code flags)
- Cross-team coordination easier
- Enables modern deployment strategies
- Faster time-to-value

### Negative
- New tool to learn & operate
- Added latency (LaunchDarkly API calls)
- $$$$ cost (~$3k/month at our scale)
- Technical debt (feature flags as code smell)
- Over-engineering for small features

### Other
- Only use for deployment-risky features
- Don't use for trivial config
- Establish code review process for flags

## Alternatives Considered

### Option A: Build internal feature flag system
- Effort: ~4 weeks initial, ongoing maintenance
- Cost: ~$2k/month engineering time
- Rejected: Reinventing wheel, no time

### Option B: Stay with git branches + environment variables
- Benefit: No new tool
- Cost: Can't do gradual rollouts, slow rollbacks
- Rejected: Not scaling with us

### Option C: LaunchDarkly (chosen)
- Benefit: Proven, all features we need
- Cost: $3k/month + learning curve
- Why chosen: Frees engineers, enables modern deployment

## Rollout Plan
- Week 1: Set up LaunchDarkly account
- Week 2: Train team
- Week 3: Migrate 3 features as POC
- Month 2: All new features use flags
- Month 3-4: Evaluate & decide on migration of old features

## Lessons Learned (4 months later)
✓ Adoption successful
✓ Gradual rollouts preventing bugs
✓ Instant rollback saved us 2x (bugs caught in prod)
⚠ Added 10-20ms latency (acceptable)
✓ Team loves the deployment flexibility
⚠ Some flag hygiene issues (forgetting to clean up)

Confidence: HIGH, would do again
```

---

## 10. Setup Guide

### Step-by-Step ADR Setup

#### Step 1: Create ADR Folder Structure

```bash
# Create folder structure
mkdir -p docs/architecture/decisions

# Create README
cat > docs/architecture/decisions/README.md << 'EOF'
# Architecture Decision Records

This directory contains Architecture Decision Records (ADRs) for our organization.

## How to use

1. **Read ADRs:** Start with `ADR-001` to understand our architectural decisions
2. **Propose new ADR:** Create new file, follow template
3. **Review process:** Discuss in PR, merge when team agrees

## ADR Index

| # | Title | Status | Date |
|---|-------|--------|------|
| 001 | Framework choice: React | Accepted | 2024-01 |
| 002 | State management: Zustand | Accepted | 2024-01 |
| 003 | Styling: Tailwind | Accepted | 2024-01 |

## Creating a new ADR

1. Copy `0000-template.md`
2. Number it sequentially (001, 002, etc.)
3. Write clear context and decision
4. Include alternatives considered
5. Create PR for discussion
6. Merge when team agrees
EOF
```

#### Step 2: ADR Template

```bash
cat > docs/architecture/decisions/0000-template.md << 'EOF'
# ADR-XXX: [Short Title]

## Status

[Proposed | Accepted | Deprecated | Superseded by ADR-YYY]

## Context

[Describe the issue, why we need this decision]

## Decision

[Clear statement of what we decided]

## Consequences

### Positive

- [Benefit 1]
- [Benefit 2]

### Negative

- [Trade-off 1]
- [Trade-off 2]

## Alternatives Considered

### Option A

- Pros:
- Cons:
- Why rejected:

### Option B (chosen)

- Pros:
- Cons:
- Why chosen:

## Implementation

[How will this be implemented? Timeline?]

## Lessons Learned (6+ months post-decision)

[To be filled in later...]
EOF
```

#### Step 3: Git Workflow

```bash
# Create ADR workflow
cat > .github/CODEOWNERS << 'EOF'
# Architecture Decisions
docs/architecture/decisions/ @architecture-team
EOF

# Create PR template
cat > .github/pull_request_template.md << 'EOF'
## For ADRs: Please confirm

- [ ] Context clearly explains the problem
- [ ] Decision is unambiguous
- [ ] Consequences section covers trade-offs
- [ ] Alternatives section explains why others were rejected
- [ ] Has team consensus (or documented dissent)
EOF
```

#### Step 4: CI/CD Integration

```bash
# Validate ADRs in CI
cat > scripts/validate-adrs.sh << 'EOF'
#!/bin/bash

echo "Validating ADRs..."

for file in docs/architecture/decisions/ADR-*.md; do
  if ! grep -q "## Status" "$file"; then
    echo "❌ $file missing Status section"
    exit 1
  fi
  
  if ! grep -q "## Context" "$file"; then
    echo "❌ $file missing Context section"
    exit 1
  fi
  
  if ! grep -q "## Decision" "$file"; then
    echo "❌ $file missing Decision section"
    exit 1
  fi
  
  if ! grep -q "## Consequences" "$file"; then
    echo "❌ $file missing Consequences section"
    exit 1
  fi
  
  echo "✓ $file valid"
done

echo "All ADRs valid!"
EOF

chmod +x scripts/validate-adrs.sh
```

#### Step 5: Documentation Integration

Add to your docs site:

```bash
# Docusaurus example
cat > docusaurus.config.js << 'EOF'
module.exports = {
  // ...
  plugins: [
    [
      '@docusaurus/plugin-content-docs',
      {
        path: 'docs/architecture',
        routeBasePath: 'architecture',
      },
    ],
  ],
};
EOF
```

---

## 11. Tooling Comparison

| Tool | Purpose | Pros | Cons | Best For |
|------|---------|------|------|----------|
| **MADR** | Markdown template | Simple, no tool needed | Manual organization | Small teams, git-based |
| **Log4Brains** | ADR CLI tool | Automatic indexing, clean output | Node.js dependency | Teams using Node tooling |
| **Backstage** | Developer portal | Discovers ADRs automatically | Heavy setup, Kubernetes | Enterprise with Backstage |
| **GitHub Wiki** | Team wiki | Built-in, no setup | Poor search, informal | Very small teams, informal |
| **Confluence** | Enterprise wiki | Rich editing, organization | $$$ cost, searchable | Large enterprises |
| **Notion** | Workspace database | Beautiful, flexible | Siloed from code | Teams already using Notion |

**Recommendation for your stack:** Start with **MADR + GitHub** (free, version controlled, simple).

---

## 12. Cheatsheet

### ADR Decision Framework (Quick Reference)

```
When facing a decision:

1. FRAME THE PROBLEM
   - What's actually broken?
   - What constraints exist?
   - What business outcome?
   - Who's affected?

2. IDENTIFY OPTIONS
   - Minimum 3 options
   - Reject false dichotomies
   - Hybrid options count

3. EVALUATE OPTIONS
   Technical:        (1-5 points)
   Maintainability:  (1-5 points)
   Team capability:  (1-5 points)
   Operational:      (1-5 points)
   Scalability:      (1-5 points)
   Risk:             (1-5 points)

4. DOCUMENT TRADE-OFFS
   - What are we winning?
   - What are we losing?
   - Is trade-off acceptable?

5. CHOOSE & COMMUNICATE
   - Clear decision statement
   - Why this option won
   - Why alternatives lost
   - Implementation plan

6. IMPLEMENT & LEARN
   - Execute decision
   - Monitor consequences
   - After 6-12 months: lessons learned
```

### Common ADRs Checklist

Frontend teams typically need:

- [ ] Framework (React, Astro, Vue)
- [ ] State management (Zustand, Redux, Jotai)
- [ ] Styling (Tailwind, CSS-in-JS, CSS Modules)
- [ ] Testing (Vitest, Jest, Playwright)
- [ ] Build tool (Vite, Webpack)
- [ ] Component patterns
- [ ] Design system governance
- [ ] Monorepo organization
- [ ] CI/CD strategy
- [ ] Deployment strategy

---

## 13. Real-World Engineering Mindset

### Case Study: Monorepo Adoption at Scale

**Scenario:** 30 engineers, 6 teams, 4 separate repositories. High coordination overhead.

**Question:** Should we adopt monorepo?

**Junior engineer:** "Yes! Monorepo is better, it's a best practice."

**Senior engineer:** "Let me analyze the trade-offs..."

```
PROS of monorepo:
  ✓ Shared code (reduce duplication)
  ✓ Atomic changes (one commit touches all repos)
  ✓ Easy refactoring (move code between projects)
  ✓ Simpler tooling (one build, one CI)
  ✓ Faster onboarding (clone once)

CONS of monorepo:
  ✗ Build time grows (many files to check)
  ✗ Merge conflicts increase
  ✗ Loss of team autonomy (everyone's code visible)
  ✗ Complex git history
  ✗ Tool sophistication needed (Nx, Turborepo, etc.)
  ✗ Migration effort (6-8 weeks)
  ✗ Resistance from teams who like autonomy

STAFF+ ANALYSIS:
  - Current pain: High (30-40% of time on cross-repo coordination)
  - Monorepo benefit: Reduced coordination → faster development
  - Implementation cost: ~8 weeks engineering time
  - Risk: Builds slow if not done right
  - Organizational readiness: Ready (all teams aligned on pain)

DECISION:
  Adopt monorepo, BUT:
  1. Invest in build caching (Turborepo/Nx)
  2. Establish code review standards (reduce blame)
  3. Gradual migration (one team at a time)
  4. 6-month eval period (are we better off?)
```

**Staff+ engineer chose:** "Yes to monorepo, BUT with heavy investment in tooling and process."

Key difference:
- Engineer says: "Do it"
- Staff+ says: "Do it IF we handle these risks, with this process, measuring these metrics"

---

## 14. Brainstorm / Open Questions

### Architecture Strategy (15 questions)

1. Should we optimize architecture for current scale or future scale?
2. What hidden operational complexity does a microservices migration introduce?
3. How will this decision age over 3 years?
4. What organizational structure does this architecture assume?
5. Should this become a platform standard or stay team-specific?
6. What future migrations does this decision enable or block?
7. If this decision was wrong, how long until we discover it?
8. How reversible is this decision?
9. What's the long-term cost of technical debt from this choice?
10. How does this decision affect hiring requirements?
11. What operational expertise must we build?
12. How tightly does this couple us to vendors/tools?
13. What does "success" look like for this decision?
14. Who bears the cost if this decision is wrong?
15. Does this enable or prevent the next architectural evolution?

### Frontend Architecture (15 questions)

16. Should we standardize on one framework or allow team choice?
17. How does state management choice affect team velocity?
18. What's the real cost of CSS-in-JS vs Tailwind at scale?
19. When should we use Server Components vs Client Components?
20. How much monorepo complexity is acceptable?
21. Should design systems be enforced or aspirational?
22. What's the right testing strategy for component libraries?
23. How do we handle third-party widget compatibility?
24. Should we use micro-frontends or federated architectures?
25. What's the cost of framework-agnostic component systems?
26. How do we version design systems across teams?
27. When should we add a CSS preprocessor vs keep it simple?
28. What's acceptable build time for team productivity?
29. How do we balance DX (developer experience) vs UX (user experience)?
30. Should accessibility be enforced by tooling or process?

### Platform Engineering (15 questions)

31. What should platform teams own vs. what should product teams own?
32. How do we make good decisions easy for teams?
33. Should platforms mandate or recommend?
34. What's the right level of abstraction for platforms?
35. When should we build platforms vs. let teams figure it out?
36. How do we prevent platform bloat?
37. What's acceptable technical debt in platform code?
38. How do we measure platform adoption?
39. Should platforms be opt-in or mandatory?
40. What's the cost of maintaining multiple versions of a platform?
41. How do we handle exceptions to platform decisions?
42. When should platforms enable rather than enforce?
43. What's the ROI threshold for building a platform?
44. How do we prevent "frameworks of frameworks" accumulation?
45. What metrics indicate a platform is healthy?

### Organizational Scalability (15 questions)

46. How does architecture change from 50 engineers to 500?
47. What governance prevents architectural chaos at scale?
48. How do we make decisions across 20+ independent teams?
49. What's the cost of different teams making different choices?
50. How do we handle architectural disputes?
51. When should we break up teams vs. synchronize systems?
52. How does organizational structure affect technical choices?
53. What's the right ratio of platform engineers to product engineers?
54. How do we scale code review at 500 engineers?
55. When does standardization become harmful?
56. What's the cost of inconsistency across teams?
57. How do we onboard 100 engineers without chaos?
58. What processes enable architectural evolution?
59. How do we measure organizational technical health?
60. What's the relationship between org structure and system architecture?

### Governance & Decision-Making (15 questions)

61. Should architecture decisions be democratic or hierarchical?
62. How much process is optimal for decision-making?
63. What decisions should require ARB approval?
64. How do we handle architectural dissent?
65. When should teams have exceptions to standards?
66. What's the cost of enforcing vs. recommending?
67. How do we evolve standards without invalidating old code?
68. Should governance be explicit (ADRs) or implicit (culture)?
69. How do we prevent architecture from becoming constraint?
70. What's the relationship between governance and velocity?
71. How do we make governance visible and searchable?
72. When do ADRs become burden vs. benefit?
73. How do we handle architectural review at scale?
74. What's acceptable technical debt from governance overhead?
75. How do we teach architectural thinking to junior engineers?

### Technical Debt & Evolution (15 questions)

76. When should we pay down technical debt vs. build features?
77. How do we measure technical debt ROI?
78. What's the cost of maintaining legacy architecture?
79. When is rewrite cheaper than refactor?
80. How do we migrate without disrupting products?
81. What's the longest acceptable system-wide migration?
82. How do we identify architectural debt before it's painful?
83. Should we pay technical debt incrementally or batch?
84. What's the cost of NOT evolving architecture?
85. How do we prevent new technical debt while paying old?
86. When should we refactor vs. rewrite?
87. What's the relationship between architecture and incident rate?
88. How do we communicate technical debt to non-engineers?
89. What metrics indicate architecture is aging poorly?
90. How do we prioritize between feature velocity and technical health?

### Migration & Transformation (15 questions)

91. What's the right pace for large migrations?
92. How do we prevent "half-migrated" systems?
93. When should migrations be forced vs. gradual?
94. What's acceptable parallel support for old + new systems?
95. How do we avoid creating new technical debt during migration?
96. What's the cost of supporting multiple architectural patterns?
97. When should we pause new features for migrations?
98. How do we measure migration success?
99. What's the relationship between deadlines and migration quality?
100. How do we prevent old system accumulation?

---

## 15. Practice Questions

### Beginner (35 questions)

**Q1.** What does ADR stand for?
- **Answer:** Architecture Decision Record

**Q2.** True or False: The purpose of an ADR is to document the best practice.
- **Answer:** False
- **Why:** ADRs document the decision made in a specific context. The decision might not be the global best practice.

**Q3.** Which section of an ADR is MOST important?
- A) Status
- B) Context
- C) Decision
- D) Consequences
- **Answer:** B) Context
- **Why:** Without context, the decision is meaningless. Future readers need to understand WHY this decision was made.

**Q4.** What should you do if an ADR's decision becomes wrong?
- A) Delete the ADR
- B) Update the ADR to new decision
- C) Write a new ADR superseding the old one
- D) Ignore it and move forward
- **Answer:** C) Write a new ADR superseding the old one
- **Why:** Preserves historical context, shows evolution of thinking.

**Q5.** True or False: Alternatives to the chosen option should NOT be documented.
- **Answer:** False
- **Why:** Understanding why alternatives were rejected is critical context.

**Q6.** What does "Status: Accepted" mean in an ADR?
- **Answer:** The team has agreed to make this decision and will implement it.

**Q7.** What's the purpose of a "Consequences" section?
- **Answer:** To document the trade-offs: what we gain and what we lose with this decision.

**Q8.** ADRs are primarily:
- A) Implementation details
- B) Code documentation
- C) Design decisions and their rationale
- D) Technical requirements
- **Answer:** C) Design decisions and their rationale

**Q9.** True or False: An ADR should be written BEFORE implementation starts.
- **Answer:** False (typically)
- **Why:** ADRs are usually written AFTER the decision is made but BEFORE widespread implementation (or after small POC).

**Q10.** When should "Lessons Learned" be added to an ADR?
- **Answer:** 6-12 months after the decision was implemented, to evaluate if it worked as expected.

**Q11-Q35:** *(Additional beginner questions covering ADR basics, templates, common patterns, governance basics)*

---

### Junior (35 questions)

**Q36.** When should a decision warrant an ADR vs. staying a team decision?
- **Answer:** ADRs when: affects multiple teams, has long-term consequences, reverses old decisions, creates architectural boundary, or affects hiring/onboarding.

**Q37.** Your team chose Zustand for state management. How would you structure the ADR?
- **Answer:** Context (why we needed a state solution), Decision (Zustand), Consequences (learning curve, smaller bundle, good DX), Alternatives (Redux rejected because too much boilerplate; Jotai rejected because less mature).

**Q38.** What's Conway's Law and how does it relate to architecture decisions?
- **Answer:** Architecture mirrors organizational communication structure. If you have 3 frontend teams → likely 3 different architecture styles unless you have governance.

---

### Senior (35 questions)

**Q71.** Your monolith is becoming slow with 50 engineers. Design a migration strategy to microservices using ADRs.
- **Answer:** ADR-1: Monolith bottleneck acknowledgment, ADR-2: Microservices strategy, ADR-3: Service boundaries (by feature/domain), ADR-4: Shared services (auth, logging), ADR-5: Gradual migration plan. Each ADR documents one decision point.

**Q72.** Why might a decision that was "right" at 50 engineers become "wrong" at 500 engineers?
- **Answer:** Scaling changes trade-offs. Monolith was optimal at 50 (simple, fast). At 500, deployment coupling kills velocity → microservices becomes necessary. Decision didn't become wrong; context changed.

---

### Expert / Staff+ (35 questions)

**Q106.** Design ADR governance for a 200-person engineering organization with 20+ teams.
- **Answer:** Federated model: Platform team owns infrastructure ADRs (database, deployment, monitoring). Product teams own their architectural decisions (framework, state management). Cross-team ADRs handled by architecture board. Principles documented (not mandates). Dissent documented in ADRs.

**Q107.** How do you prevent ADRs from becoming process overhead?
- **Answer:** Not all decisions need ADRs. Only decisions that: affect multiple teams, have long-term consequences, or establish patterns. Day-to-day choices stay local. ADRs should take <2 hours to write.

---

## 16. Personalized Recommendations

### For Your Stack (React, Next.js, Astro, Vite, TypeScript)

**Priority ADRs to write:**

1. **Framework strategy:** When to use React vs Astro (high-impact decision)
2. **State management:** Zustand vs Context vs React Query
3. **Styling:** Tailwind vs CSS Modules vs CSS-in-JS
4. **Build tooling:** Vite for all projects
5. **Monorepo organization:** If using monorepo, document structure
6. **Feature flags:** How to implement & deploy
7. **Testing strategy:** Unit vs E2E vs Integration
8. **Server components:** When to use React Server Components (Next.js)
9. **Performance:** LCP/CLS/INP targets and governance
10. **Deployment:** SSR vs SSG strategy

**60-Day Learning Plan:**

```
Week 1-2: ADR Fundamentals
  - [ ] Read this guide
  - [ ] Understand MADR template
  - [ ] Set up docs/architecture/decisions folder
  - [ ] Write ADR-001 (framework choice)

Week 3-4: Implementation
  - [ ] Set up GitHub workflow
  - [ ] Create ADR for state management
  - [ ] Create ADR for styling strategy
  - [ ] Team review & refinement

Week 5-6: Scaling
  - [ ] Document existing decisions (retroactive ADRs)
  - [ ] Identify gaps (undocumented decisions)
  - [ ] Write ADRs for gaps
  - [ ] Create ADR index

Week 7-8: Governance
  - [ ] Establish ADR review process
  - [ ] Train team on decision-making framework
  - [ ] Automate ADR validation in CI
  - [ ] Measure: How much coordination overhead reduced?
```

---

## 17. Official Documentation & Reference Links

### Beginner

- [ADR GitHub Organization](https://adr.github.io) — Official ADR documentation
- [Thoughtworks: Documenting Architecture Decisions](https://cognitect.com/blog/2011/11/15/documenting-architecture-decisions) — Original ADR concept
- [MADR Standard](https://github.com/adr/madr) — Markdown ADR template
- [Michael Nygard's original ADR article](https://www.artima.com/articles/archstuff_1.html) — Classic reference

### Intermediate

- [Atlassian: Architecture Decision Records](https://www.atlassian.com/team-playbook/plays/architecture-decision-records)
- [AWS: Architecture Decision Records](https://docs.aws.amazon.com/prescriptive-guidance/latest/architectural-decision-records/welcome.html)
- [Martin Fowler: Architecture Decision Records](https://martinfowler.com/adr.html)
- [Log4Brains: ADR documentation tool](https://github.com/thomvaill/log4brains)

### Advanced

- [StaffEng: Becoming a Staff Engineer](https://staffeng.com) — How architecture decisions fit Staff+ role
- [System Design Primer](https://github.com/donnemartin/system-design-primer) — Architecture thinking
- [Designing Data-Intensive Applications](https://www.oreilly.com/library/view/designing-data-intensive-applications/9781491901632/) — Deep architecture thinking
- [Building Evolutionary Architectures](https://www.oreilly.com/library/view/building-evolutionary-architectures/9781491986356/)

### Enterprise / Large-Scale

- [Backstage: Developer Portal](https://backstage.io) — Discover ADRs & architecture
- [Thoughtworks Technology Radar](https://www.thoughtworks.com/radar) — Industry architecture decisions
- [O'Reilly: Technology Strategy Patterns](https://www.oreilly.com/library/view/technology-strategy-patterns/9781492040834/)

---

## 18. Advanced Engineering Topics

### Socio-Technical Systems

The most important concept: **Architecture is not just technical.**

Architecture = (Technical System) × (Organizational Structure) × (Business Context)

Change any factor, architecture needs to evolve.

### Platform Engineering & Architecture Enablement

Good architecture isn't about perfect technical choices.
It's about **enabling teams to make good decisions**.

Platforms don't mandate.
Platforms provide "paved paths" that teams follow because they're better, not because they're forced.

### Long-Term Architecture Sustainability

Questions that separate long-term thinking from short-term optimization:

1. Will this architecture still make sense in 3 years?
2. Will this decision prevent or enable the next evolution?
3. What's the cost of NOT making this architectural change?
4. How reversible is this decision?
5. What does success look like?

---

## Summary

### Key Takeaways

1. **ADRs preserve organizational memory** — Future engineers understand WHY decisions exist
2. **Context matters more than the decision** — Knowing WHY is more important than knowing WHAT
3. **Trade-offs are inevitable** — No architecture is universally correct
4. **Architecture ages over time** — What's right for 50 engineers is wrong for 500
5. **Staff+ engineers think systemically** — Considering organizational implications, not just technical
6. **Governance enables autonomy** — Good processes let teams make their own decisions confidently
7. **ADRs evolve as context changes** — Superseding old ADRs is normal and healthy
8. **Documentation is leverage** — Time spent writing ADRs saves 10x later in onboarding & disputes

### Next Steps

1. Start with MADR template (don't overcomplicate)
2. Write ADR-001 for your most controversial decision
3. Set up docs/architecture/decisions folder with README
4. Make ADR reviews part of decision-making process
5. After 3 months: evaluate if ADRs are helping or bureaucracy

### Topics to Continue Learning

- **System Design:** Distributed systems trade-offs
- **Platform Engineering:** Building platforms that enable teams
- **Organizational Architecture:** How org structure drives technical architecture
- **Technical Leadership:** How to influence without authority
- **Decision Science:** Making better decisions under uncertainty

