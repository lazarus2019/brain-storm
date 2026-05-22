---
title: RFCs (Request for Comments)
description: Complete RFC engineering deep-dive covering technical proposals, organizational alignment,
  governance frameworks, communication strategies, architecture decision-making, and
  Staff+/Principal leadership
slug: rfcs
modifiedDate: '2026-05-22'
draft: false
featured: true
tags:
- rfcs
- request-for-comments
- technical-proposals
- engineering-governance
- organizational-alignment
- architecture-decisions
- staff-plus
- platform-engineering
- technical-leadership
categories:
- mindset
- architecture
seo:
  title: RFCs (Request for Comments) — Ultimate Deep-Dive Guide
  description: Complete RFC engineering guide covering technical proposals, organizational
    alignment, governance frameworks, communication, architecture decisions, and Staff+/Principal
    engineering leadership
  canonical: https://feel-free.com/blogs/rfcs
  keywords:
  - rfc
  - request for comments
  - technical proposals
  - engineering governance
  - organizational alignment
  - architecture decisions
  - staff plus engineering
author: lazarus2019
lang: en
relatedPosts:
- adrs-architecture-decision-records
- sdk
---

# RFCs (Request for Comments) — Ultimate Deep-Dive Guide

A complete engineering guide from beginner concepts to Staff+/Principal-level technical proposal systems, organizational alignment, and enterprise-scale governance thinking.

---

## Table of Contents

1. [Big Picture](#1-big-picture)
2. [Technical Proposal & Decision-Making Deep Dive](#2-technical-proposal--decision-making-deep-dive)
3. [RFC Structure & Standards](#3-rfc-structure--standards)
4. [Engineering Governance & Organizational Alignment](#4-engineering-governance--organizational-alignment)
5. [Staff+/Principal Engineering Mindset](#5-staffprincipal-engineering-mindset)
6. [RFCs for Frontend / React / Next.js / Astro](#6-rfcs-for-frontend--react--nextjs--astro)
7. [RFC Lifecycle & Proposal Evolution](#7-rfc-lifecycle--proposal-evolution)
8. [Real-World RFC Examples](#8-real-world-rfc-examples)
9. [Communication & Stakeholder Management](#9-communication--stakeholder-management)
10. [Setup Guide](#10-setup-guide)
11. [Tooling Comparison](#11-tooling-comparison)
12. [Cheatsheet](#12-cheatsheet)
13. [Real-World Engineering Mindset](#13-real-world-engineering-mindset)
14. [Brainstorm / Open Questions](#14-brainstorm--open-questions)
15. [Practice Questions](#15-practice-questions)
16. [Personalized Recommendations](#16-personalized-recommendations)
17. [Official Documentation & Reference Links](#17-official-documentation--reference-links)

---

## 1. Big Picture

### What RFCs Actually Are

An RFC (Request for Comments) is a **structured technical proposal** that enables organizational alignment on significant engineering decisions before implementation.

Key characteristics:

1. **Collaborative** — Solicits feedback from stakeholders before decision is final
2. **Documented** — Creates written record of decision and rationale
3. **Asynchronous** — Doesn't require synchronous meetings
4. **Discoverable** — Preserved in repository, searchable for future reference
5. **Formal** — Follows structure/template, versioned, tracked

An RFC is NOT:
- A design document (too detailed)
- A quick Slack discussion (not formal enough)
- A decision already made (seeks input before decision)
- A bug report (not about fixing issues)
- Implementation code (stays at architecture level)

An RFC IS:
- A **proposal** (before decision)
- A **communication tool** (explains thinking)
- An **alignment mechanism** (gathers feedback)
- A **governance artifact** (enables oversight)
- An **organizational memory** (preserved long-term)

### RFC vs ADR vs Design Document

| Document | Timing | Purpose | Formality | Immutable |
|---|---|---|---|---|
| **RFC** | Before decision | Propose & gather feedback | Medium | No (evolves during review) |
| **ADR** | After decision | Document decision + rationale | Medium | Yes (with amendments) |
| **Design Doc** | During implementation | Detailed implementation plan | High | No (evolves with dev) |
| **Proposal** | Very early | Rough idea exploration | Low | No (often informal) |
| **RFD** (Request for Discussion) | Early exploration | Extended discussion format | High | No (evolves) |

**Flow:** Idea → RFC (proposal) → Decision → ADR (record) → Implementation → Design Doc (details)

### Why RFCs Exist

```
┌──────────────────────────────────────────────────────────────┐
│        Problems RFCs Solve                                    │
├──────────────────────────────────────────────────────────────┤
│                                                                │
│  WITHOUT RFCs (informal decisions):                          │
│    - Important decision made in Slack/meeting                │
│    - Not everyone heard the discussion                       │
│    - Reasoning lost after people leave                       │
│    - Similar decision made again later                       │
│    - Teams make inconsistent choices                         │
│    - No time for asynchronous feedback                       │
│    - Junior engineers don't see thinking                     │
│    - Post-mortems say "how did we decide this?"             │
│                                                                │
│  WITH RFCs:                                                  │
│    ✓ Major decisions are documented                          │
│    ✓ Everyone can review, comment, contribute               │
│    ✓ Thinking is visible and explained                       │
│    ✓ Decision is clearly recorded                            │
│    ✓ Teams learn from similar proposals                      │
│    ✓ Asynchronous input from distributed teams              │
│    ✓ New engineers see reasoning, learn patterns             │
│    ✓ Incident analysis has context                           │
│    ✓ Future decisions informed by precedent                  │
│                                                                │
└──────────────────────────────────────────────────────────────┘
```

### Engineering Alignment Lifecycle

```
┌──────────────────────────────────────────────────────────────┐
│       RFC Lifecycle (Ideation to Implementation)              │
├──────────────────────────────────────────────────────────────┤
│                                                                │
│  PHASE 1: PROBLEM IDENTIFICATION (Pre-RFC)                   │
│    - Problem discovered                                      │
│    - Issue tracked                                           │
│    - Initial discussion                                      │
│    - Stakeholders identified                                 │
│                                                                │
│  PHASE 2: PROPOSAL DRAFTING                                  │
│    - Write RFC with problem/solution/trade-offs              │
│    - Share with stakeholders for early feedback              │
│    - Iterate on proposal based on feedback                   │
│                                                                │
│  PHASE 3: PUBLIC RFC                                         │
│    - Submit RFC to repository                                │
│    - Announce to organization                                │
│    - Stakeholders review and comment                         │
│    - Author clarifies and iterates                           │
│    - RFC discussion period (1-2 weeks typical)               │
│                                                                │
│  PHASE 4: DECISION                                           │
│    - Decision maker evaluates proposal                       │
│    - Considers feedback and concerns                         │
│    - Decides: accept, accept-with-conditions, or reject      │
│    - Decision documented (in RFC or ADR)                     │
│                                                                │
│  PHASE 5: COMMUNICATION                                      │
│    - Decision announced to organization                      │
│    - Implementation timeline set                             │
│    - Owner assigned                                          │
│    - Questions answered                                      │
│                                                                │
│  PHASE 6: IMPLEMENTATION                                     │
│    - RFC owner oversees implementation                       │
│    - Deviations documented and escalated                     │
│    - Progress tracked                                        │
│    - Implementation completed                                │
│                                                                │
│  PHASE 7: RETROSPECTIVE (3-6 months later)                   │
│    - Did implementation match proposal?                      │
│    - Were expected benefits realized?                        │
│    - What surprised us?                                      │
│    - Lessons learned documented                              │
│                                                                │
└──────────────────────────────────────────────────────────────┘
```

### When RFCs Become Critical

RFCs are essential when:

| Situation | Why | Cost of skipping |
|-----------|-----|------------------|
| **Multi-team impact** | Decision affects >3 teams | Teams optimize locally, create conflict |
| **Long-lived systems** | Decision hard to reverse | Expensive to redo later |
| **Architectural boundary** | Touches core infrastructure | Cascading changes downstream |
| **New standards** | Establishing team/org pattern | Inconsistency, future confusion |
| **Resource-heavy** | Significant budget/time | Wrong approach = wasted effort |
| **Org-wide precedent** | Sets pattern others follow | Sets precedent for all similar decisions |
| **High uncertainty** | Multiple viable approaches | Wrong choice discovered too late |
| **Distributed teams** | Async communication needed | Context gets lost, misalignment |

---

## 2. Technical Proposal & Decision-Making Deep Dive

### Proposal Analysis Framework

Professional decision-making involves systematically evaluating proposals:

```
EVALUATION DIMENSIONS:

1. TECHNICAL CORRECTNESS
   - Does this solve the stated problem?
   - Are there flaws in the technical approach?
   - What assumptions are being made?
   - Can we test the assumptions?

2. MAINTAINABILITY
   - Will someone else understand this in 2 years?
   - How much domain knowledge is required?
   - What's the onboarding cost?
   - How complex is the resulting system?

3. OPERATIONAL COMPLEXITY
   - How hard is this to operate/debug?
   - What new monitoring is needed?
   - What failure modes exist?
   - What's the incident response playbook?

4. ORGANIZATIONAL FIT
   - Does this match our strategy?
   - Do we have skills to maintain it?
   - Will this help or hurt team coordination?
   - Is this politically acceptable?

5. REVERSIBILITY
   - How hard would it be to undo?
   - What's the exit strategy?
   - Are we creating lock-in?
   - Can we migrate away if wrong?

6. TIMELINE & RESOURCES
   - How long to implement?
   - Who would do it?
   - What's the opportunity cost?
   - Is now the right time?

7. RISKS
   - What could go wrong?
   - How severe would failures be?
   - What mitigation exists?
   - What's our contingency?

8. LEARNING & GROWTH
   - What will team learn?
   - Does this develop capability?
   - Or is this a short-term fix?
   - How does this position us long-term?
```

### Why Context Matters

The "correct" technical choice depends entirely on context:

```
Example: Should we adopt GraphQL?

Context A (Startup, 5 engineers):
  - Simple REST API works fine
  - GraphQL adds complexity
  - Team doesn't know GraphQL
  - Decision: Stay with REST
  ✓ Correct for this context

Context B (Large company, 200 engineers, many clients):
  - Multiple client types (web, mobile, embed)
  - Each client has different data needs
  - REST creates over-fetching
  - API surface exploding
  - GraphQL reduces coordination
  - Decision: Adopt GraphQL
  ✓ Correct for this context

Same technology, opposite decisions, both correct.
The decision depends on scale, team, client needs, and constraints.
```

### How Proposals Age Over Time

Decisions that seem perfect initially often degrade:

```
Example: "Let's standardize on React"

YEAR 1: Good decision
  - React ecosystem immature but promising
  - Only React available
  - Team growing, standardization needed
  - Decision: Adopt React everywhere

YEAR 3: Still good
  - React mature, ecosystem strong
  - Team scaled effectively
  - Standardization paying off
  - Decision still correct

YEAR 5: Starting to show strain
  - React complexity growing
  - Some use cases want lighter framework
  - Performance critical app struggling with React
  - Team wants to use Vue/Svelte for specific projects

YEAR 7: Decision clearly aging
  - React no longer only option
  - Different teams have different needs
  - Standardization becoming burden, not benefit
  - Team wants to allow alternatives

NEW RFC NEEDED
  "We should allow Astro for content-heavy applications
   while keeping React as default for interactive apps"

Old decision was right for its time.
New context requires new decision.
```

---

## 3. RFC Structure & Standards

### RFC Template

```markdown
# RFC-XXX: [Title]

## Summary

One paragraph explaining what this RFC proposes.

## Motivation

Why are we considering this change?
What problem does it solve?
What's the business/technical impact?

## Goals

What do we want to achieve?
What are success criteria?

## Non-Goals

What are we explicitly NOT solving?
What's out of scope?

## Proposed Solution

Detailed explanation of the proposed approach.

## Trade-Offs

What are we gaining?
What are we sacrificing?
Why is this trade-off acceptable?

## Alternatives Considered

### Alternative A
- Approach: [description]
- Pros: [list]
- Cons: [list]
- Why not chosen: [reasoning]

### Alternative B
- Approach: [description]
- Pros: [list]
- Cons: [list]
- Why not chosen: [reasoning]

### Proposed Solution
- Approach: [description]
- Pros: [list]
- Cons: [list]
- Why chosen: [reasoning]

## Risks & Mitigations

| Risk | Severity | Mitigation |
|------|----------|-----------|
| Risk 1 | High/Medium/Low | How we reduce this risk |
| Risk 2 | | |

## Migration Strategy

For decisions affecting existing systems:
- What happens to old systems?
- Timeline for migration?
- Rollback plan?
- Success metrics?

## Organizational Implications

- How does this affect team structure?
- Skills/training needed?
- Hiring implications?
- Cultural changes?

## Rollout Plan

Phase 1: [what, who, when]
Phase 2: [what, who, when]
Phase 3: [what, who, when]

## Open Questions

- Question 1?
- Question 2?
- Question 3?

## Resources

- Links to related proposals
- Background reading
- Design documents
- Implementation guides
```

### RFC Statuses

```
DRAFT
  - Initial proposal, not yet ready for review
  - Author still developing thinking
  - Not for public discussion yet

REVIEW
  - Ready for feedback
  - Author is responding to comments
  - Can change based on feedback

ACCEPTED
  - Decision is final
  - Implementation can begin
  - No major changes expected

IMPLEMENTED
  - Implemented and live
  - Lessons learned documented
  - Ready for retrospective

SUPERSEDED by RFC-YYY
  - Newer RFC replaces this one
  - Keep old RFC for historical context
  - Note what changed and why

REJECTED
  - Decision was not to proceed
  - Keep for historical record
  - Explains why alternative was not chosen

DEPRECATED
  - Was implemented, but no longer used
  - Practice evolved
  - Keep for historical context
```

---

## 4. Engineering Governance & Organizational Alignment

### Governance Model Spectrum

Organizations range from none to heavy governance:

```
NO GOVERNANCE (Startup)
  - Anyone can make decisions
  - No process, move fast
  - Risk: Inconsistency, chaos

LIGHTWEIGHT (Growth stage)
  - Proposals for big decisions only
  - Quick review process
  - Risk: Some decisions not captured

MODERATE (Mid-scale)
  - Architecture board reviews proposals
  - Standards emerging
  - Governance growing
  - Risk: Becoming too rigid

HEAVY (Enterprise)
  - Strict governance process
  - Multiple review stages
  - Compliance requirements
  - Risk: Slowness, stifles innovation

APPROPRIATE governance is context-dependent.
Too little: chaos and inconsistency
Too much: slowness and frustration
Right amount: clarity + flexibility
```

### Architecture Review Board (ARB)

Typical ARB (for 50-200 engineers):

```
Members:
  - VP/Principal Engineer (chair)
  - Platform Engineering Lead
  - Frontend Architecture Lead
  - Backend/Infrastructure Lead
  - Security Lead
  (Rotating membership, term limits)

Responsibilities:
  - Review RFCs for technical soundness
  - Ensure organizational alignment
  - Identify risks
  - Track decisions over time

Meetings:
  - Monthly RFC review meeting
  - RFC authors present proposals
  - Board discusses and decides
  - Decisions documented

Authority:
  - Can request changes to RFC
  - Can reject proposals
  - Can't force implementation details
  - Teams still own their work

Process:
  - RFC submitted 1 week before meeting
  - Board reviews asynchronously
  - Meeting for discussion/decision
  - Decision documented in RFC
```

### Platform Standards & Golden Paths

Good governance creates "golden paths" not mandates:

```
Difference:

MANDATE ("You MUST use X")
  - Pros: Clear, consistent
  - Cons: Inflexible, team resentment
  - Breaks: Edge cases and exceptions

GOLDEN PATH ("We recommend X for Y")
  - Pros: Clear guidance, flexibility
  - Cons: Requires judgment
  - Scales: Teams make informed choices

Example:

MANDATE: "All frontend apps must use React"
  - Team wants to build simple static site
  - Forced to use React
  - Result: Over-engineering, team frustrated

GOLDEN PATH: "React is recommended for interactive apps"
  - Team can choose React for interactive work
  - Team can choose Astro for static content
  - Result: Right tool for job, team happy
```

---

## 5. Staff+/Principal Engineering Mindset

### How Staff+ Engineers Think About RFCs

| Level | Decision Focus | RFC Style |
|-------|---|---|
| **Junior** | "Is this technical solution correct?" | Implementation details, narrow scope |
| **Senior** | "Is this the right architectural approach?" | Trade-offs, team impact |
| **Staff+** | "How does this affect organizational strategy?" | Long-term implications, alignment |

**Staff+ RFC Thinking:**
- "What does this enable or prevent in the future?"
- "How does this affect team structure/autonomy?"
- "What cultural signals does this send?"
- "How does this position us 3-5 years from now?"
- "Who's not in the room, and how should we get their input?"
- "What's the minimal viable decision vs. over-engineering?"
- "How do we keep this decision from becoming permanent?"

### Technical Leadership Without Authority

Staff+ engineers influence decisions they don't directly own:

```
Techniques:

1. FRAME THE PROPOSAL
   "Here's how I see the problem..."
   Sets context for discussion

2. NAME THE TRADE-OFFS
   "If we choose X, we gain Y but lose Z"
   Makes hidden costs explicit

3. ESCALATE UPWARD
   "This affects multiple teams, let's align first"
   Prevents local optimization

4. SURFACE ASSUMPTIONS
   "We're assuming Z. Is that true?"
   Tests reasoning

5. PLAY DEVIL'S ADVOCATE
   "What if we're wrong about...?"
   Tests robustness

6. CONNECT TO STRATEGY
   "This aligns/conflicts with our strategy of..."
   Provides organizational context

7. ENABLE DISSENT
   "I disagree, but I understand the reasoning"
   Values thinking over agreement
```

---

## 6. RFCs for Frontend / React / Next.js / Astro

### Common Frontend RFCs

Frontend teams typically need RFCs for:

1. **Framework choices** (React, Astro, Svelte)
2. **Rendering strategy** (SSR, SSG, CSR)
3. **State management** (Zustand, Redux, Context)
4. **Design systems** (Governance, component library)
5. **Monorepo adoption** (Package structure, build tool)
6. **Accessibility standards** (WCAG level, testing)
7. **Performance targets** (Web Vitals, budgets)
8. **Testing strategy** (Unit, E2E, coverage)
9. **Styling approach** (Tailwind, CSS Modules, CSS-in-JS)
10. **Feature flags** (Implementation, rollout strategy)

### Example RFC: Adopting Astro for Content Sites

```markdown
# RFC-042: Adopt Astro for Content-Heavy Applications

## Summary

We propose using Astro as the default framework for content-focused 
applications (blogs, docs, marketing) while keeping React for 
interactive applications. This improves performance and developer 
experience for the majority of our content projects.

## Motivation

Currently, all frontend applications use React. This works well for
interactive dashboards and apps, but creates performance overhead
for content-focused projects.

Astro is a new framework optimized for content sites with
zero-JS-by-default, islands architecture, and excellent DX.

## Goals

- Improve performance of content sites (50% faster LCP target)
- Reduce JavaScript shipped for static content (95% smaller bundle)
- Improve developer experience for content builders
- Reduce framework mismatch pain

## Non-Goals

- Replace React for interactive applications
- Migrate existing React apps to Astro
- Eliminate React from organization

## Proposed Solution

1. Adopt Astro as recommended framework for content sites
2. Keep React for interactive applications
3. Create clear decision matrix (see alternatives)
4. Provide Astro starter template
5. Build team expertise in Astro

## Trade-Offs

GAINS:
  + Better performance for content (no JS hydration)
  + Better DX for content builders
  + Smaller bundle sizes
  + Better SEO (static HTML first)

LOSES:
  - Another framework to maintain
  - New learning curve for team
  - Fragmented frontend tooling
  - Some patterns require more manual work

Trade-off acceptable because:
  - Performance improvements are significant
  - Content sites are 40% of our portfolio
  - Learning curve is low (1-2 weeks)
  - Framework choice doesn't prevent sharing code

## Alternatives Considered

### Keep Everything React
- Pros: Single framework, familiar
- Cons: Over-engineered for content, worse performance
- Why not: Performance overhead unacceptable for content sites

### Migrate to Astro Completely
- Pros: Single framework again
- Cons: Breaks interactive patterns, large migration
- Why not: Interactive apps need React patterns

### Astro for Content + React for Interactive (chosen)
- Pros: Right tool per job, good performance, familiar DX
- Cons: Two frameworks, learning curve
- Why chosen: Best balance of performance and pragmatism

## Risks & Mitigations

| Risk | Severity | Mitigation |
|------|----------|-----------|
| Team learning curve | Medium | Provide training, examples, pair programming |
| Framework fragmentation | Medium | Clear decision matrix, code sharing where possible |
| Astro immaturity | Low | Astro 1.0 is stable, community growing |
| Maintenance burden | Low | Small footprint, declining use likely as React improves |

## Migration Strategy

No existing apps need migration. New projects choose based on
decision matrix.

## Decision Matrix

Use **Astro** when:
- Content-focused (blogs, docs, marketing)
- Static generation possible
- Performance critical
- SEO important

Use **React** when:
- Interactive (forms, dashboards, real-time)
- Heavy client-side logic
- Frequent state updates
- Rich interactivity needed

## Rollout Plan

Phase 1 (Week 1-2):
  - Team training on Astro basics
  - Create starter template
  - Build example project

Phase 2 (Week 3-4):
  - Start 2-3 real projects with Astro
  - Gather feedback
  - Refine template

Phase 3 (Month 2+):
  - Use on all new content projects
  - Build patterns and best practices

## Success Metrics

- New content projects 50% faster LCP
- Bundle size 95% smaller than React equivalent
- Team onboarding time < 1 week
- 0 regrets (team satisfaction)

## Open Questions

- How do we share code between React and Astro?
- Should islands use React or separate from Astro?
- What's our long-term content strategy?
- Will Astro remain relevant in 2-3 years?

## Implementation

If accepted, implementation owner: Frontend Lead
Timeline: Start next quarter
```

---

## 7. RFC Lifecycle & Proposal Evolution

### Proposal Reevaluation

Decisions should be revisited when context changes:

```
When to reevaluate:

1. NEW INFORMATION
   - Technology matured unexpectedly
   - New option became available
   - Assumptions proven wrong

2. ORGANIZATIONAL CHANGE
   - Team structure changed
   - Company strategy shifted
   - New business needs

3. OPERATIONAL ISSUES
   - Unexpected maintenance burden
   - Performance problems
   - Scalability limits hit

4. TIME-BASED
   - Every 2-3 years, revisit major decisions
   - Periodically assess aging decisions

When reevaluating:

1. Write new RFC, reference old one
2. Explain why context changed
3. Acknowledge old RFC was right for its time
4. Propose new direction
5. Keep old RFC for historical record
```

### Superseding RFCs

When a decision needs to change:

```markdown
# RFC-083: Reconsider GraphQL Adoption

## Status
Supersedes RFC-041 (Adopted GraphQL 2 years ago)

## Motivation

RFC-041 recommended adopting GraphQL 2 years ago.
Context has changed:

- GraphQL complexity exceeded expectations
- Team spending 30% of time on GraphQL maintenance
- REST with Remix is emerging as simpler alternative
- Performance issues hard to debug
- Real benefit (multiple clients) didn't materialize

## Reconsidered Trade-Offs

GraphQL gave us:
  + Type safety (which TypeScript now provides)
  + Query flexibility (which 90% of clients never use)

But cost us:
  - Steep learning curve (took 6 months to master)
  - Performance debugging complexity
  - N+1 query problems (still common)
  - Cache invalidation headaches

Lesson: Benefits didn't match costs.

## Proposed Solution

Migrate back to REST with Remix + React Query.
This gives us similar benefits with less complexity.

[Rest of RFC...]
```

---

## 8. Real-World RFC Examples

### Example 1: RFC for Monorepo Adoption

```markdown
# RFC-028: Adopt Monorepo Architecture

## Summary

Propose migrating from polyrepo (separate repositories) to monorepo
(single repository) to reduce cross-team coordination overhead.

## Motivation

Current polyrepo structure (30 separate repos) creates friction:
- Cross-repo changes require multiple PRs
- Dependency updates hard to coordinate
- Code sharing requires versioned packages
- 15+ engineers spend 20% of time on coordination

## Goals

- Reduce coordination overhead by 50%
- Enable atomic commits across projects
- Simplify code sharing
- Improve developer experience

## Proposed Solution

Adopt monorepo with Turborepo as orchestrator.

Structure:
```
packages/
  design-system/
  sdk/
  web-app/
  mobile/
  cli/
  
tools/
  scripts/
  linting/
  
docs/
```

Build orchestration with Turborepo:
- Incremental builds
- Remote caching (cost ~$500/month)
- Parallel execution
- Task pipelines

## Trade-Offs

GAINS:
  + Atomic changes across projects
  + Faster code sharing
  + Simpler dependency management
  + Better tooling efficiency

LOSES:
  - Smaller per-team autonomy (shared repo)
  - Build complexity increases
  - Merging discipline required
  - Monorepo not familiar to all engineers

Trade-off acceptable because:
  - Team is ready for shared responsibility
  - Build complexity well-understood (Turborepo mature)
  - Coordination pain exceeds complexity cost

## Risks & Mitigations

| Risk | Severity | Mitigation |
|------|----------|-----------|
| Build time regression | High | Turborepo caching, incremental builds |
| Merge conflicts | High | Pre-commit checks, branching strategy |
| Team resistance | Medium | Training, phased migration |
| Onboarding complexity | Medium | Better docs, clearer structure |

## Migration Strategy

Phase 1 (Month 1): Set up monorepo skeleton
Phase 2 (Month 1-2): Migrate 2 lowest-risk packages
Phase 3 (Month 2-3): Migrate remaining packages
Phase 4 (Month 3+): Cleanup, optimization

Timeline: 3 months total
Rollback: Revert to polyrepo if major issues (Week 1-2 only)

## Success Metrics

- Cross-repo coordination time down 50%
- Build times under 10 minutes (incremental)
- Team satisfaction > 4/5
- 0 merge conflicts per week (average)

## Lessons from Other Companies

Monorepos at scale:
- Google: 100+ million lines, thousands of teams (works)
- Facebook: Thousands of projects (works, custom tooling)
- Stripe: Multiple monorepos per language (works well)
- Twitter: Mixed monorepo + polyrepo (evolving)

Key learnings:
1. Needs discipline (code owners, clear boundaries)
2. Needs tooling (Turborepo, Bazel, etc.)
3. Works for tightly coupled codebases
4. Doesn't work for independent services

[Continues with implementation details...]
```

---

## 9. Communication & Stakeholder Management

### Crafting Persuasive RFCs

Great proposals are technically sound AND politically acceptable:

```
PERSUASION TECHNIQUES:

1. FRAME THE PAIN
   Don't say: "We should use Next.js"
   Say: "Our SSR latency is causing customer churn"
   (Establishes why this matters)

2. NAME THE PROBLEM CLEARLY
   Don't say: "Rendering is slow"
   Say: "P95 TTI is 3.2s, competitors are <1.5s"
   (Makes it quantifiable)

3. SHOW THE TRADE-OFFS
   Don't say: "Next.js is better"
   Say: "Next.js adds 15KB bundle but reduces TTI by 60%"
   (Shows you've thought deeply)

4. ADDRESS CONCERNS PROACTIVELY
   Don't wait for objections
   Say: "This requires learning Next.js, we've budgeted 2 weeks training"
   (Shows you've thought about costs)

5. RESPECT THE SYSTEM
   Don't say: "We're doing this"
   Say: "Here's my recommendation, seeking feedback"
   (Invites participation)

6. MAKE IT EASY TO SAY YES
   Don't say: "Do you agree?"
   Say: "How can we improve this plan?"
   (Shifts from yes/no to collaboration)

7. ACKNOWLEDGE UNCERTAINTY
   Don't pretend to know everything
   Say: "We won't know the full impact for 3 months"
   (Shows intellectual honesty)
```

### Handling Feedback & Dissent

Good RFC authors don't just defend their proposal:

```
When someone disagrees:

WRONG RESPONSE:
  "That won't work because..."
  (Dismissive, defensive)

RIGHT RESPONSE:
  "Great point. Let me think about that.
   Here's what I understand about your concern...
   Would [revision] address it?"
  (Curious, collaborative)

WHEN TO CHANGE YOUR MIND:
  - You didn't consider a valid perspective
  - New information surfaces
  - Concerns raise genuine risks
  - Better alternative emerges

WHEN TO STAND FIRM:
  - You've already addressed concern
  - Person misunderstands proposal
  - Their concern isn't material
  - Risk is acceptable trade-off

Document why you rejected feedback:
  "We considered X's concern about Y.
   After discussion, we decided to proceed because Z.
   We'll revisit if Z doesn't hold true."
  (Shows respect + accountability)
```

---

## 10. Setup Guide

### RFC Repository Structure

```
rfc/
  README.md                          # RFC index and process
  
  PROCESS.md                         # How to submit/review RFCs
  
  templates/
    RFC-TEMPLATE.md                  # Standard template
    
  accepted/
    RFC-001-framework-choice.md
    RFC-002-monorepo-adoption.md
    ...
    
  draft/
    RFC-050-experimental-proposal.md
    
  rejected/
    RFC-031-cloudflare-adoption.md
```

### GitHub Workflow

```bash
# Create RFC
git checkout -b rfc/my-proposal
cp rfc/templates/RFC-TEMPLATE.md rfc/draft/RFC-050-title.md
# Write RFC content
git add rfc/draft/RFC-050-title.md
git commit "rfc: RFC-050 - my proposal (draft)"

# Submit for review
git push origin rfc/my-proposal
# Create PR
# Title: "RFC-050: My Proposal"
# Description: Link to rendered RFC

# Review & discussion happens in PR comments
# Author responds to feedback, iterates

# Move to accepted when decision made
mv rfc/draft/RFC-050-title.md rfc/accepted/
git add rfc/
git commit "rfc: Accept RFC-050"
```

### RFC Index

```markdown
# RFC Index

## Active RFCs (Under Review)

| # | Title | Author | Status |
|---|-------|--------|--------|
| 050 | My Proposal | Jane | Draft |

## Accepted RFCs

| # | Title | Author | Date | Implementation |
|---|-------|--------|------|---|
| 001 | Framework Choice | John | 2024-01 | Done |
| 002 | Monorepo Adoption | Jane | 2024-02 | In Progress |

## Rejected RFCs

| # | Title | Author | Date | Reason |
|---|-------|--------|------|--------|
| 040 | Micro-frontends | Bob | 2024-01 | Complexity not justified |
```

---

## 11. Tooling Comparison

| Tool | Purpose | Pros | Cons | Best For |
|------|---------|------|------|----------|
| **GitHub** | Native, issue-based | Built-in, no setup | Limited structure | Small teams, open source |
| **GitLab** | Wiki + MR | Good organization | Less familiar | Enterprise, CI integration |
| **Google Docs** | Collaborative editing | Easy editing, comments | Not version controlled | Drafting, feedback |
| **Notion** | Team database | Beautiful, flexible | Siloed from code | Large teams, many docs |
| **Confluence** | Enterprise wiki | Powerful, corporate | $$, complexity | Enterprise at scale |
| **Backstage** | Developer portal | Discovers RFCs automatically | Heavy setup | Enterprise with Backstage |

**Recommendation:** Start with GitHub (Issues + Wiki), graduate to GitLab as complexity grows.

---

## 12. Cheatsheet

### RFC Submission Checklist

```
BEFORE WRITING:
  ☐ Is this decision significant enough for RFC?
  ☐ Have you done initial research?
  ☐ Do you understand the problem space?
  ☐ Have you identified key stakeholders?

WHILE WRITING:
  ☐ Problem is clearly explained
  ☐ Goals are measurable
  ☐ Non-goals are stated
  ☐ At least 2 alternatives considered
  ☐ Trade-offs are explicit
  ☐ Risks are identified & mitigated
  ☐ Organizational implications discussed
  ☐ Writing is clear (not too technical)
  ☐ Examples help clarify complex ideas
  ☐ Unknown unknowns are listed as open questions

BEFORE SUBMITTING:
  ☐ You believe in the proposal
  ☐ You're open to feedback
  ☐ You've proof-read
  ☐ Links/references are correct
  ☐ You have time to respond to feedback

DURING REVIEW:
  ☐ You respond to all comments
  ☐ You explain your reasoning patiently
  ☐ You change your mind when warranted
  ☐ You document why you rejected feedback
  ☐ You maintain professionalism
  ☐ You stay curious, not defensive
```

### Common RFC Anti-Patterns

```
ANTI-PATTERN: "Selling" the proposal
  ✓ Instead: Present options, let others decide

ANTI-PATTERN: Technical depth without context
  ✓ Instead: Business impact first, then technical

ANTI-PATTERN: Ignoring dissent
  ✓ Instead: Address concerns seriously

ANTI-PATTERN: Already decided, seeking approval
  ✓ Instead: Actually undecided, seeking input

ANTI-PATTERN: No alternatives section
  ✓ Instead: Always show you considered alternatives

ANTI-PATTERN: Vague trade-offs
  ✓ Instead: Specific, quantified trade-offs

ANTI-PATTERN: No success metrics
  ✓ Instead: Clear how you'll know if it worked
```

---

## 13. Real-World Engineering Mindset

### Frontend Framework Standardization

**Scenario:** Should your organization standardize on React vs. stay flexible?

**Analysis by company stage:**

**Startup (10 engineers):**
- React standardization: Overkill, limits flexibility
- Strategy: "Use what works, favor React for shared knowledge"
- Later RFC: "Adopt React standard" as team grows

**Growth (50 engineers):**
- React standardization: Beneficial, reduces fragmentation
- Strategy: RFC proposing React standard, Astro exceptions
- Benefits: Shared libraries, team moves easily
- Costs: One team frustrated they wanted Vue

**Large (200+ engineers):**
- React standardization: Probably wrong, too rigid
- Strategy: Federated, React default + exceptions
- Better: "React for interactive, Astro for content" guidelines
- Result: Teams optimize locally, still coordinated

**Key insight:** "Best" framework choice depends on scale, team, constraints.
Governance that works at one scale breaks at another.

---

## 14. Brainstorm / Open Questions

### Architecture Strategy (15 questions)

1. Should this RFC become organizational standard or stay team-specific?
2. What organizational assumptions does this proposal make?
3. How will this proposal age over 3-5 years?
4. What hidden operational complexity does this introduce?
5. Could this governance model slow innovation?
6. What migrations does this proposal enable or block?
7. Who isn't in the room, and should we get their input?
8. Is this a minimal viable decision or over-engineered?
9. How do we prevent this decision from becoming permanent?
10. Does this decision align with where we want to be in 3 years?
11. What would happen if we did nothing?
12. What's the cost of reversing this decision if wrong?
13. Are we solving the right problem or wrong problem well?
14. Who bears the cost if this proposal fails?
15. What does success look like, and how will we measure it?

### Organizational Alignment (15 questions)

16. Will this proposal create friction between teams?
17. Does this enable or prevent team autonomy?
18. What new skills will the team need?
19. Will this help or hurt hiring/retention?
20. Are we setting a precedent we'll regret?
21. Does this proposal match our company culture?
22. Will this benefit individual contributors, managers, both?
23. How does this affect knowledge distribution?
24. Will this create information silos?
25. Does this proposal address root cause or symptom?
26. Are we solving the problem or avoiding harder conversation?
27. Who will champion this long-term?
28. What happens when proposal author leaves?
29. Is this proposal sustainable without heroics?
30. Will this proposal make us more or less agile?

### Technical Debt & Evolution (15 questions)

31. Is this proposal accumulating or paying down technical debt?
32. What technical debt does this proposal create?
33. Will future engineers thank us for this decision?
34. How does this proposal affect system complexity?
35. Does this make our systems easier or harder to understand?
36. Can we pay down debt incrementally or must we all-in?
37. What's the "minimum viable" version of this proposal?
38. Are we building leverage or incurring burden?
39. How does this proposal affect long-term flexibility?
40. Does this decision constrain future options?
41. Will this proposal be hard to undo?
42. What's the technical debt if we don't make this change?
43. How does this proposal interact with other systems?
44. Are we optimizing for now or for the future?
45. What would the simplest solution be?

### Operational Complexity (15 questions)

46. What operational burden does this introduce?
47. What new monitoring/observability do we need?
48. How much on-call burden does this create?
49. What's the incident response playbook?
50. How many people need to understand this system?
51. What debugging skills are required?
52. How much documentation is required?
53. Will this make deployments easier or harder?
54. Does this proposal simplify or complicate rollouts?
55. What's our failure recovery strategy?
56. How do we prevent cascading failures?
57. What's the blast radius of a mistake?
58. How do we validate this won't break production?
59. Can we test this proposal before full rollout?
60. What safety nets do we need?

### Long-term Sustainability (15 questions)

61. Will this proposal remain relevant in 3-5 years?
62. What would cause us to reconsider this decision?
63. How will we evaluate this proposal's success?
64. When should we revisit this decision?
65. What's our exit strategy if this becomes wrong?
66. How will this proposal affect next innovation?
67. Does this decision limit or enable future options?
68. Will this create organizational lock-in?
69. Can we evolve this proposal over time?
70. Is this decision reversible?
71. What sunk costs will we face?
72. How does this proposal serve customers?
73. Does this proposal help or hurt product development?
74. What would we regret about this proposal?
75. What would we be proud of about this proposal?

---

## 15. Practice Questions

### Beginner (35 questions)

**Q1.** What does RFC stand for?
- **Answer:** Request for Comments

**Q2.** True or False: An RFC is a decision that's already been made.
- **Answer:** False
- **Why:** RFCs propose decisions and request feedback before the decision is finalized.

**Q3.** What's the main purpose of an RFC?
- A) Document code
- B) Report bugs
- C) Propose and align on significant engineering decisions
- D) Write technical specifications
- **Answer:** C) Propose and align on significant engineering decisions

**Q4.** When should you write an RFC vs. just making a decision?
- **Answer:** Write RFCs for decisions that affect multiple teams, are hard to reverse, or establish organizational patterns.

**Q5.** What should every RFC include?
- **Answer:** Problem statement, proposed solution, alternatives considered, trade-offs, and risks.

**Q6-Q35:** *(Additional beginner questions on RFC basics, structure, governance, documentation)*

---

### Junior (35 questions)

**Q36.** What's the difference between an RFC and an ADR?
- **Answer:** RFC proposes before decision (seeks feedback). ADR documents after decision (records reasoning).

**Q37.** How do you handle disagreement in RFC review?
- **Answer:** Listen to concerns, explain your thinking, revise if valid, document why you rejected feedback.

**Q38.** What makes an RFC "good"?
- **Answer:** Clear problem, well-reasoned solution, honest trade-offs, considered alternatives, explicitly named assumptions.

---

### Senior (35 questions)

**Q71.** Design an RFC process for a 100-person engineering organization.
- **Answer:** Lightweight process for small decisions, formal board for architectural decisions, clear escalation path, monthly review cadence.

**Q72.** How do you prevent RFCs from becoming rubber-stamp processes?
- **Answer:** Ensure decision-maker is empowered to reject RFCs, address concerns seriously, build dissent into process, regularly audit decisions.

---

### Expert / Staff+ (35 questions)

**Q106.** Your organization has written 50 RFCs. How do you evolve the governance model as you scale?
- **Answer:** Move from centralized board to federated decisions, develop principles, automate routine decisions, focus human review on novel problems.

**Q107.** Design an RFC process that enables both organizational alignment and team autonomy.
- **Answer:** Teams own most decisions, escalate only cross-team concerns, clear decision criteria, focus on outcomes not implementation details.

---

## 16. Personalized Recommendations

### For Your Stack (React, Next.js, Astro, Vite, TypeScript)

**Priority RFCs to understand:**

1. **Framework governance** — When/why to choose React vs Astro
2. **Rendering strategy** — SSR vs SSG vs CSR trade-offs
3. **Monorepo organization** — Structure, tooling, boundaries
4. **State management** — Zustand vs Context vs React Query
5. **Design systems** — Governance, versioning, adoption
6. **Performance budgets** — Web Vitals targets, enforcement
7. **CI/CD standardization** — GitHub Actions vs GitLab CI
8. **Accessibility standards** — WCAG level, testing strategy

**60-Day Learning Plan:**

```
Week 1-2: RFC Fundamentals
  - [ ] Read 5-10 good RFCs from open source
  - [ ] Understand RFC template
  - [ ] Learn RFC review process
  - [ ] Identify RFCs from your organization

Week 3-4: RFC Analysis
  - [ ] Analyze 1 RFC you disagree with
  - [ ] Understand the reasoning
  - [ ] Write down alternative approaches
  - [ ] Discuss with colleagues

Week 5-6: Write Your First RFC
  - [ ] Identify significant decision
  - [ ] Draft RFC proposal
  - [ ] Get informal feedback
  - [ ] Refine based on feedback

Week 7-8: RFC Refinement
  - [ ] Submit RFC formally
  - [ ] Respond to review comments
  - [ ] Iterate on proposal
  - [ ] Work toward decision
```

---

## 17. Official Documentation & Reference Links

### Beginner

- [RFC Home](https://tools.ietf.org/rfc/) — Original RFC concept from IETF
- [GitHub: RFC by Design](https://github.blog/2016-03-31-introducing-the-github-flow/) — RFC workflow in practice
- [Rust RFC Process](https://rust-lang.github.io/rfcs/) — Accessible, well-executed example

### Intermediate

- [Kubernetes Enhancement Proposals](https://github.com/kubernetes/enhancements) — Large-scale governance example
- [Ember RFC Process](https://github.com/emberjs/rfcs) — Clear structure, good examples
- [Stripe API RFCs](https://stripe.com/blog) — How platforms govern APIs
- [Vercel RFCs](https://vercel.com/blog) — Modern SaaS governance

### Advanced

- [Architecture Decision Records (ADRs)](docs/ADRs-Architecture-decision-records.md) — Companion to RFCs
- [Engineering Principles](https://engineering.fb.com/) — How large companies think
- [System Design Interview](https://www.youtube.com/watch?v=q0KSFHzQess) — Thinking frameworks
- [The Staff Engineer's Path](https://www.oreilly.com/library/view/the-staff-engineers/9781098118914/) — Leadership at scale

### Case Studies

- [Kubernetes Governance](https://www.kubernetes.io/docs/contribute/design-consistency/) — Scales to hundreds of contributors
- [React RFC Process](https://github.com/reactjs/rfcs) — Framework governance
- [TypeScript Design Documents](https://www.typescriptlang.org/docs/handbook/2/narrowing.html) — Language evolution

---

## Summary

### Key Takeaways

1. **RFCs enable organizational alignment** — Major decisions benefit from async feedback
2. **Structure matters** — Good templates ensure complete thinking
3. **Governance scales** — RFC processes evolve as organization grows
4. **Communication is technical** — How you frame proposals affects adoption
5. **Proposals age over time** — Decisions should be revisited as context changes
6. **Dissent is valuable** — Good RFC processes invite and address disagreement
7. **Context determines "rightness"** — Same proposal has different answers at different scales

### Next Steps

1. Study RFCs from organizations you respect (Kubernetes, Rust, React)
2. Identify RFCs in your organization and understand the reasoning
3. Write your first RFC for a decision you're already making
4. Get feedback, iterate, learn from the process
5. Build RFC culture in your organization over time

### Advanced Topics to Continue Learning

- Large-scale governance models (100+ engineers)
- Global distributed decision-making
- Cultural implications of governance
- Automating governance checks
- RFC analytics and pattern recognition

