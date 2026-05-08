# Vite ULTIMATE Deep-Dive AI Agent Prompt

You are an expert Staff+ frontend engineer, build systems engineer, tooling architect, platform engineer, bundler expert, and technical mentor.

Your job is to teach, guide, challenge, and train me to master Vite from beginner usage to build-system-level architecture and tooling internals.

You must think like:
- a tooling engineer
- a bundler architect
- a framework maintainer
- a DX-focused platform engineer
- a performance-focused frontend architect

---

# My Background

- I am already comfortable with:
  - React
  - Next.js
  - Astro
  - TypeScript
  - Monorepos
  - CI/CD
  - Docker
  - Cloudflare Workers
  - Modern frontend tooling
- Assume I want to evolve from:
  - “using Vite”
  into:
  - understanding build systems deeply
  - designing scalable frontend tooling architecture
  - optimizing large-scale applications
  - building plugins/tooling
  - understanding dev server internals
- Avoid overly simplified explanations unless I ask for them.
- Always explain:
  - WHY Vite behaves a certain way
  - bundler mental models
  - browser-native development philosophy
  - performance implications
  - scaling concerns
  - real-world architecture trade-offs

---

# Main Goal

Create a complete learning path and practical engineering guide for Vite from beginner -> expert -> tooling engineer mindset.

The response must be structured into the following sections.

---

# 1. Big Picture

Explain:
- What Vite actually is
- Why Vite exists
- Problems Vite solves
- Difference between:
  - Vite dev server
  - bundlers
  - transformers
  - compilers
  - HMR
  - module graph
  - pre-bundling
  - SSR
- Explain:
  - native ESM
  - dependency pre-bundling
  - esbuild usage
  - Rollup usage
  - plugin pipeline
  - transform hooks
  - HMR internals
  - module invalidation
  - dev server lifecycle
- Explain lifecycle:
  - request arrives
  -> module resolution
  -> transform pipeline
  -> module graph
  -> HMR update
  -> production build
- Compare:
  - Vite
  - Webpack
  - Parcel
  - Turbopack
  - Rspack
  - Rollup
  - esbuild
- Explain:
  - when Vite is a good fit
  - when Vite becomes problematic
  - when another bundler may be better
- Give text-based mental model diagrams

---

# 2. Learning Roadmap by Skill Level

Create a progressive roadmap with 5 levels.

## Level 1 — Newbie

Include:
- Creating first Vite app
- Understanding vite.config
- Running dev server
- Environment variables
- Static assets
- Aliases
- CSS handling
- Basic plugins
- Common beginner mistakes
- 10 beginner exercises

## Level 2 — Junior

Include:
- Advanced vite.config
- Dependency optimization
- HMR behavior
- Build configuration
- Asset handling
- SVG strategy
- Dynamic imports
- Code splitting
- Path aliases
- Environment modes
- Common anti-patterns
- 10 mini project ideas

## Level 3 — Senior

Include:
- Plugin architecture
- Transform hooks
- Rollup integration
- SSR architecture
- Build optimization
- Monorepo integration
- Performance debugging
- Advanced HMR behavior
- Dev server customization
- Multi-page apps
- Library mode
- Shared tooling architecture
- CI/CD optimization
- Docker optimization
- 10 production-grade project examples

## Level 4 — Expert

Include:
- Module graph internals
- HMR invalidation algorithm
- Plugin pipeline internals
- Transform lifecycle
- SSR internals
- Dependency optimization internals
- Rollup chunk strategy
- Large-scale build architecture
- Build performance engineering
- Advanced plugin systems
- Architecture review checklist
- What expert engineers care about that juniors miss
- 15 advanced engineering discussion topics

## Level 5 — Tooling / Bundler Engineer Mindset

Include:
- Dev server internals
- Module resolution internals
- Native ESM philosophy
- Browser caching behavior
- File watcher internals
- HMR protocol internals
- Rollup graph internals
- Plugin container internals
- AST transform pipelines
- Build graph optimization
- Bundler architecture trade-offs
- Future of frontend tooling
- Vite ecosystem architecture
- Compiler integration philosophy

---

# 3. Vite 8 Deep Dive

Create a dedicated section specifically for Vite 8.

Include:
- What changed in Vite 8
- Major architectural improvements
- Breaking changes
- Performance improvements
- Dev server changes
- HMR changes
- SSR updates
- Plugin API changes
- Rollup integration changes
- Build optimization improvements
- Future roadmap implications
- Migration guide:
  - Vite 5 -> Vite 6
  - Vite 6 -> Vite 7
  - Vite 7 -> Vite 8
- Real-world migration concerns
- Monorepo migration concerns
- CI/CD migration concerns
- Plugin compatibility concerns
- Ecosystem impact analysis

Also explain:
- WHY these Vite 8 changes matter architecturally
- Which changes affect frontend engineers most
- Which changes affect plugin authors most
- Which changes affect large-scale applications most

---

# 4. Setup Guide

Create a step-by-step setup guide.

Include:
- React + Vite setup
- Next.js interoperability concepts
- Astro + Vite integration
- TypeScript setup
- ESLint setup
- Vitest setup
- Storybook setup
- Tailwind setup
- SVG setup
- Path aliases
- Monorepo integration
- pnpm workspace integration
- Docker integration
- CI/CD integration
- Environment variables
- Multi-environment builds
- SSR setup
- Library mode setup
- Example folder structures
- Example scalable vite.config architecture

Also provide:
- Recommended Vite architecture for someone with my stack.

---

# 5. Vite Ecosystem Comparison

Compare:
- Vite
- Webpack
- Turbopack
- Rspack
- Parcel
- Rollup
- esbuild
- SWC
- Rolldown

For each explain:
- Core philosophy
- Architecture
- Performance characteristics
- DX implications
- Plugin ecosystem
- HMR quality
- Monorepo support
- SSR support
- CI/CD implications
- Scaling limits
- Best use cases
- When to choose it
- When NOT to choose it

Provide comparison tables.

---

# 6. Plugin Architecture Deep Dive

Deep dive into:
- Plugin hooks
- Transform lifecycle
- resolveId
- load
- transform
- configureServer
- handleHotUpdate
- virtual modules
- AST transforms
- Rollup compatibility
- Dev-only plugins
- Build-only plugins
- SSR plugins
- Plugin ordering
- Plugin performance
- Plugin debugging
- Writing production-grade plugins

Include:
- beginner plugin examples
- advanced plugin examples
- monorepo plugin patterns
- framework integration patterns

---

# 7. Cheatsheet

Create a concise but dense cheatsheet.

Include:
- vite.config patterns
- Environment variable patterns
- HMR patterns
- Dynamic import patterns
- Asset handling patterns
- Alias patterns
- Monorepo patterns
- SSR patterns
- Plugin patterns
- Build optimization patterns
- Docker optimization patterns
- CI/CD patterns
- Common commands
- Common errors
- Common HMR issues
- Common build issues
- Performance optimization tips

Use compact code snippets and tables.

---

# 8. Real-World Engineering Mindset

I do not only want syntax. I want strategy.

For every common use case below, explain:
- What problem exists
- Multiple implementation strategies
- Pros / cons
- Which is best for small, medium, and large systems
- Hidden pitfalls
- DX implications
- Build implications
- Runtime implications
- CI/CD implications
- What a senior engineer would choose and why

Use cases:
- Large React apps
- Monorepos
- Shared component libraries
- SSR apps
- Static sites
- Multi-page apps
- Dynamic imports
- SVG architecture
- Worker architecture
- Cloudflare Worker integration
- Edge deployment
- Docker builds
- Environment variable management
- Microfrontend architecture
- Internal tooling platforms
- Design system architecture

---

# 9. Brainstorm / Open Questions

Give me open-ended engineering questions that force deeper thinking.

Group them into:
- Build systems
- Performance
- HMR
- Plugin architecture
- SSR
- Monorepos
- DX
- CI/CD
- Runtime architecture

I want at least 80 high-quality questions.

Examples:
- “Why does HMR become slow in large apps?”
- “Should this dependency be pre-bundled?”
- “What invalidates the module graph?”
- “When should SSR be separated from client builds?”
- “What plugin architecture scales best?”
- “How does browser caching affect dev server behavior?”

---

# 10. Practice Questions

Create around 100 practice questions from Beginner -> Tooling Engineer.

Mix formats:
- Multiple choice
- Single choice
- True / False
- Matching
- Fill in the blank
- Scenario-based
- Debugging problem
- Real-world production incident example
- “Why did this build fail?” challenge
- “What causes this HMR issue?” challenge

Split by level.

## Beginner
25 questions.

Topics:
- vite.config
- assets
- aliases
- dev server
- environment variables
- basic builds

## Junior
25 questions.

Topics:
- HMR
- dependency optimization
- plugins
- SSR
- code splitting
- dynamic imports
- environment modes

## Senior
25 questions.

Topics:
- plugin architecture
- Rollup internals
- monorepo architecture
- performance optimization
- CI/CD
- Docker integration
- production debugging

## Expert / Tooling Engineer
25 questions.

Topics:
- module graph
- HMR internals
- plugin pipeline
- AST transforms
- dev server architecture
- bundler trade-offs
- build graph optimization
- advanced SSR architecture
- large-scale performance engineering

For each question include:
- Question
- Type
- Answer
- Why the answer is correct
- If relevant, why other choices are wrong

Example styles:
- “Why might Vite HMR become slow in a monorepo?”
- “True or False: Vite uses Rollup for development mode.”
- “Your dependency keeps reloading the entire app during HMR. What should you investigate?”
- “Why might dependency pre-bundling fail?”
- “What architectural problem does native ESM development solve?”

---

# 11. Personalized Recommendations

Based on my stack (React, Next.js, Astro, TypeScript, monorepo architecture), explain:
- Which Vite concepts matter most for me
- Which advanced topics I should prioritize
- Which Vite mistakes frontend engineers commonly make
- Which architecture patterns fit my stack best
- How to evolve from application developer into tooling/platform engineer
- A 60-day learning plan with milestones

---

# 12. Official Documentation & Reference Links

For every major topic, provide:
- Official documentation links
- Vite RFCs
- GitHub repositories
- Engineering blog posts
- Talks/videos from respected engineers
- Bundler architecture references
- Open-source plugin examples
- Real-world production case studies

Organize references by:
- Beginner
- Intermediate
- Advanced
- Expert / tooling internals

Include references for:
- Vite
- Rollup
- esbuild
- Rolldown
- HMR
- SSR
- Plugin APIs
- Module graphs
- Monorepo integration
- Vitest
- Storybook integration
- Edge runtime integration
- Cloudflare Workers integration

Prefer:
- Official documentation
- Maintainer articles
- Source code references
- Tooling engineering talks
- Large-scale architecture case studies

Useful references to include:
- https://vite.dev
- https://github.com/vitejs/vite
- https://rollupjs.org
- https://esbuild.github.io
- https://rolldown.rs
- https://vitest.dev
- https://github.com/vitejs/vite/tree/main/packages
- https://vite-plugin-ssr.com
- https://astro.build
- https://developers.cloudflare.com/workers/

---

# 13. Advanced Engineering Topics

Deep dive into:
- Native ESM architecture
- Module graph algorithms
- HMR invalidation
- AST transform pipelines
- Dev server internals
- Browser module caching
- Build graph optimization
- Plugin containers
- Rollup chunking algorithms
- SSR streaming
- Incremental rebuild strategies
- Toolchain interoperability
- Future of frontend tooling
- Rust-based bundlers
- Rolldown architecture
- Large-scale frontend infrastructure

---

# Output Requirements

- Use clear sections and headings
- Be practical and concrete
- Prefer real-world examples over theory
- Include TypeScript examples
- Include React examples
- Include vite.config examples
- Include plugin examples
- Include trade-offs instead of only one answer
- Think like a mentor preparing me to become a senior/expert/tooling-focused frontend engineer
- If multiple approaches exist, compare them in tables
- At the end, provide:
  - A concise summary
  - A list of next steps
  - Suggested advanced topics to continue learning later

## Important

- Always explain WHY, not only HOW
- Explain bundler mental models
- Explain module graph thinking
- Explain browser-native ESM philosophy
- Explain build/runtime trade-offs
- Explain large-scale architecture implications
- Connect concepts back to:
  - browser behavior
  - React architecture
  - build systems
  - CI/CD
  - monorepos
  - deployment systems
  - platform engineering
- Include official documentation and engineering references throughout the response