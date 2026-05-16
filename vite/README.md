# Vite

Study notes for Vite: from beginner usage to build-system architecture, plugin development, HMR internals, and tooling engineering.

## Contents

- [Deep dive guide — Vite](docs/VITE.md) — comprehensive Vite 8 guide: big picture, plugin architecture, SSR, build internals, and learning roadmaps.
- [Rolldown code splitting deep dive](docs/ROLLDOWN_CODE_SPLITTING.md) — Vite 8 Rolldown code splitting analysis and best practices.
- [Brainstorm prompt](docs/BRAIN_STORM.md)

## Overview

Vite is a frontend build tool that leverages native ES modules for development and Rollup/Rolldown for optimized production builds. It combines:

- Dev server: serve source as native ESM and transform on demand
- Dependency pre-bundler: `esbuild` converts and caches `node_modules`
- Production bundler: Rollup (or Rolldown in Vite 8) for tree-shaking, code splitting, and optimized output
- Plugin container: a Rollup-compatible plugin pipeline
- HMR engine: WebSocket-based module replacement driven by the module graph

## Key Concepts

- Native ESM development — browser `import`/`export` for fast dev
- Dependency pre-bundling — `esbuild` for converting commonjs/legacy packages
- Plugin architecture — Rollup-compatible hooks (`resolveId`, `load`, `transform`, etc.)
- HMR engine & module graph — fine-grained updates and cache invalidation
- Production builds — Rollup / Rolldown for chunking, tree-shaking, minification
- Code splitting (Rolldown in Vite 8) — automatic, groups, and no-splitting modes
- SSR support and middleware mode

## When to use Vite

- Single-page apps (React, Vue, Svelte, Solid)
- Multi-page apps with HTML entry points
- Component libraries (library mode)
- SSR apps (with framework integration)
- Rapid prototyping and developer-focused DX

## When Vite can be problematic

- Very large monorepos (10k+ modules)
- Complex SSR without framework support
- Projects relying on webpack-specific plugins
- Legacy browser support (requires `@vitejs/plugin-legacy`)
- Non-JS-centric build systems

## Quick Links

- [Vite Documentation](https://vite.dev)
- [Vite GitHub](https://github.com/vitejs/vite)
- [Rollup](https://rollupjs.org)
- [esbuild](https://esbuild.github.io)
- [Rolldown](https://rolldown.rs)
- [Vitest](https://vitest.dev)
