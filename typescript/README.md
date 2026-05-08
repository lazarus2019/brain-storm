# TypeScript

Comprehensive learning and engineering guide for TypeScript mastery — from beginner concepts to compiler-level mental models and large-scale architecture thinking.

## Contents

- [Deep dive guide — TS ULTIMATE](docs/TS_ULTIMATE.md) — Complete learning guide covering 11 sections: big picture, learning roadmap (5 levels), setup guide, tooling comparison, cheatsheet, real-world engineering patterns, 82 brainstorm questions, 100 practice questions, personalized recommendations, references, and advanced topics.
- [Brainstorm prompt](docs/BRAIN_STORM.md) — The original prompt that structures the learning approach and pedagogical philosophy.

## Key topics covered

- Compiler fundamentals: scanner, parser, binder, type checker, emitter
- Type system: structural typing, nominal typing (branded types), generics, constraints, inference
- Advanced types: conditional types, infer keyword, recursive types, template literal types, variance
- Practical patterns: discriminated unions, schema-driven development, runtime validation (Zod)
- API typing: REST clients, tRPC, OpenAPI codegen, type-safe error handling
- React typing: component props, polymorphic components, generic hooks, forwardRef
- Architecture: monorepo setup with project references, declaration files, public API design
- Tooling: tsc vs Babel vs SWC vs esbuild comparison, Zod, Valibot, io-ts
- Performance: compile-time optimization, type computation complexity, profiling with --generateTrace
- Compiler internals: checker.ts, module resolution, type emission, declaration emit strategy
- Soundness trade-offs: when TypeScript intentionally breaks mathematical soundness
- Advanced topics: type-level programming, custom transformers, language service API, future of TypeScript

## Who this is for

Frontend engineers (React, Next.js, Astro, TypeScript) evolving from "using TypeScript" into "architecting type-safe systems" — with focus on compiler behavior, inference mental models, large-scale patterns, library authoring, and design systems.

