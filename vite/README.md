# Vite

Study notes for Vite: from beginner usage to build-system architecture, plugin development, and tooling internals.

## Overview

Vite is a frontend build tool that leverages native ES modules for development and Rollup for optimized production builds. It provides near-instant dev server startup, fast HMR, and a Rollup-compatible plugin system.

## Key Concepts

- **Native ESM development** — browser imports modules directly, no bundling during dev
- **Dependency pre-bundling** — esbuild converts node_modules to single ESM files
- **Plugin architecture** — Rollup-compatible hooks for resolveId, load, transform
- **HMR engine** — WebSocket-based module replacement via module graph traversal
- **Production builds** — Rollup for tree-shaking, code splitting, scope hoisting
- **Environment API** — per-target module graphs (client, SSR, custom runtimes)
- **Module graph** — in-memory DAG tracking imports, HMR boundaries, and cached transforms

## Resources

- [Deep dive guide](docs/VITE.md)
- [Brainstorm prompt](docs/BRAIN_STORM.md)

## Quick Links

- [Vite Documentation](https://vite.dev)
- [Vite GitHub](https://github.com/vitejs/vite)
- [Rollup](https://rollupjs.org)
- [esbuild](https://esbuild.github.io)
- [Rolldown](https://rolldown.rs)
- [Vitest](https://vitest.dev)
