# Vite — Ultimate Deep-Dive Guide

> From beginner usage to build-system architecture and tooling internals.

---

## Table of Contents

1. [Big Picture](#1-big-picture)
2. [Learning Roadmap by Skill Level](#2-learning-roadmap-by-skill-level)
3. [Vite 8 Deep Dive](#3-vite-8-deep-dive)
4. [Setup Guide](#4-setup-guide)
5. [Vite Ecosystem Comparison](#5-vite-ecosystem-comparison)
6. [Plugin Architecture Deep Dive](#6-plugin-architecture-deep-dive)
7. [Cheatsheet](#7-cheatsheet)
8. [Real-World Engineering Mindset](#8-real-world-engineering-mindset)
9. [Brainstorm / Open Questions](#9-brainstorm--open-questions)
10. [Practice Questions](#10-practice-questions)
11. [Personalized Recommendations](#11-personalized-recommendations)
12. [Official Documentation & Reference Links](#12-official-documentation--reference-links)
13. [Advanced Engineering Topics](#13-advanced-engineering-topics)

---

## 1. Big Picture

### What Vite Actually Is

Vite is **not a bundler**. It is a **frontend build tool** that orchestrates multiple lower-level tools:

- **Dev server** — serves source files over native ESM, transforms on demand
- **Pre-bundler** — uses esbuild to consolidate dependencies into single ESM modules
- **Production bundler** — uses Rollup (and increasingly Rolldown) to produce optimized output
- **Plugin container** — runs a Rollup-compatible plugin pipeline for both dev and build
- **HMR engine** — WebSocket-based module replacement without full page reload

Vite's core insight: **browsers can now natively import ES modules**, so the dev server doesn't need to bundle your source code. It only needs to **transform** individual files on demand.

### Why Vite Exists

Traditional bundlers (Webpack, Parcel) **bundle everything** before serving — even during development. As projects grow:

- Cold start takes 10–60+ seconds
- HMR becomes slow (entire dependency graph walks)
- DX degrades proportionally to project size

Vite solves this by splitting the problem:

| Concern | Traditional Bundler | Vite |
|---------|-------------------|------|
| Dev startup | Bundle everything → serve | Pre-bundle deps → serve source as ESM |
| File change | Rebuild affected chunks | Transform single file, push HMR update |
| Dependencies | Bundle inline | Pre-bundle once with esbuild (~100x faster) |
| Source code | Bundle + transform | Serve as native ESM, transform on request |
| Production | Same bundler | Rollup (different tool, optimized for output) |

### Core Concepts Glossary

| Term | Definition |
|------|-----------|
| **Native ESM** | Browser's built-in `import`/`export` — no bundling needed for dev |
| **Dependency pre-bundling** | esbuild converts node_modules (CJS/UMD/scattered ESM) into single ESM files |
| **Transform pipeline** | Chain of plugin hooks that process source code (TS→JS, JSX→JS, etc.) |
| **Module graph** | In-memory DAG of all imported modules, their dependencies, and HMR state |
| **HMR boundary** | Module that calls `import.meta.hot.accept()` — updates stop propagating here |
| **Plugin container** | Rollup-compatible hook execution engine that runs in both dev and build |
| **SSR** | Server-side rendering — Vite can transform and execute modules in Node.js |
| **Module invalidation** | Marking a module's cached transform result as stale |

### Dev Server Request Lifecycle

```
Browser requests /src/App.tsx
        │
        ▼
┌─────────────────────────┐
│  Vite Dev Server (HTTP)  │
│  Connect middleware       │
└────────┬────────────────┘
         │
         ▼
┌─────────────────────────┐
│  Module Resolution        │
│  resolveId hooks          │
│  - resolve aliases        │
│  - resolve bare imports   │
│  - virtual modules        │
└────────┬────────────────┘
         │
         ▼
┌─────────────────────────┐
│  Load                     │
│  load hooks               │
│  - read file from disk    │
│  - virtual module content │
└────────┬────────────────┘
         │
         ▼
┌─────────────────────────┐
│  Transform Pipeline       │
│  transform hooks          │
│  - TypeScript → JS        │
│  - JSX → JS               │
│  - CSS modules             │
│  - Asset URL rewriting    │
└────────┬────────────────┘
         │
         ▼
┌─────────────────────────┐
│  Module Graph Update      │
│  - Track imports          │
│  - Track importers        │
│  - Set HMR boundaries    │
│  - Cache transform result │
└────────┬────────────────┘
         │
         ▼
  Response to browser
  (with import-rewritten URLs)
```

### HMR Update Flow

```
File changes on disk (chokidar watches)
        │
        ▼
┌─────────────────────────┐
│  Determine affected       │
│  modules via module graph │
└────────┬────────────────┘
         │
         ▼
┌─────────────────────────┐
│  Walk importers upward    │
│  until HMR boundary found │
│  (module with hot.accept) │
└────────┬────────────────┘
         │
         ├── Boundary found → send WebSocket update (partial)
         │
         └── No boundary → full page reload
```

### Production Build Flow

```
Entry points (index.html / config entries)
        │
        ▼
┌─────────────────────────┐
│  Rollup Build             │
│  - resolveId → load →    │
│    transform pipeline     │
│  - Build module graph     │
│  - Tree-shaking           │
│  - Code splitting         │
│  - Chunk generation       │
│  - Asset handling         │
│  - Minification           │
└────────┬────────────────┘
         │
         ▼
  Output: dist/
  - index.html (injected scripts)
  - assets/*.js (hashed chunks)
  - assets/*.css (extracted)
  - assets/* (static assets)
```

### When Vite Is a Good Fit

- Single-page apps (React, Vue, Svelte, Solid)
- Multi-page apps with HTML entry points
- Component libraries (library mode)
- SSR apps (with framework integration)
- Rapid prototyping
- Projects under ~5000 modules in dev

### When Vite Becomes Problematic

- **Very large monorepos** (10k+ modules) — module graph and pre-bundling can slow down
- **Complex SSR** without framework support — you must wire SSR yourself
- **Webpack-specific plugin ecosystem** — no direct compatibility
- **Non-JS-centric projects** — Vite is designed around JS/TS module graphs
- **Legacy browser requirements** — needs @vitejs/plugin-legacy, adds complexity

### Bundler Comparison Overview

| Feature | Vite | Webpack | Parcel | Turbopack | Rspack | Rollup | esbuild |
|---------|------|---------|--------|-----------|--------|--------|---------|
| Dev approach | Native ESM | Bundle | Bundle | Native ESM | Bundle | N/A | N/A |
| Dev speed | ⚡ Fast | 🐌 Slow | 🐢 Medium | ⚡ Fast | ⚡ Fast | N/A | N/A |
| HMR | WebSocket + ESM | WebSocket + chunks | WebSocket | WebSocket + RSC | WebSocket | N/A | N/A |
| Prod bundler | Rollup | Webpack | SWC | Turbopack | Rspack | Rollup | esbuild |
| Plugin system | Rollup-compat | Webpack-specific | Parcel-specific | Webpack-compat | Webpack-compat | Rollup | Go plugins |
| Config | Minimal | Complex | Zero-config | Next.js-integrated | Webpack-compat | Rollup-native | Minimal |
| Tree-shaking | Rollup (excellent) | Good | Good | Good | Good | Excellent | Basic |
| Code splitting | Rollup chunks | Webpack chunks | Auto | Auto | Webpack chunks | Manual/auto | Limited |
| SSR | Built-in primitives | Manual | Limited | Next.js-integrated | Manual | N/A | N/A |
| Maturity | Mature | Very mature | Mature | Early | Growing | Very mature | Mature |

---

## 2. Learning Roadmap by Skill Level

### Level 1 — Newbie

**Goal**: Use Vite comfortably for a React + TypeScript project.

#### Core Topics

1. **Create a Vite project**:
   ```bash
   npm create vite@latest my-app -- --template react-ts
   cd my-app && npm install && npm run dev
   ```

2. **Understand `vite.config.ts`**:
   ```typescript
   import { defineConfig } from 'vite'
   import react from '@vitejs/plugin-react'

   export default defineConfig({
     plugins: [react()],
   })
   ```

3. **Dev server basics**: `vite` starts a dev server at `localhost:5173`. It serves your source files directly — no bundling step.

4. **Environment variables**:
   - `.env`, `.env.local`, `.env.development`, `.env.production`
   - Only `VITE_` prefixed vars are exposed to client code
   - Access via `import.meta.env.VITE_API_URL`
   - `import.meta.env.MODE`, `import.meta.env.DEV`, `import.meta.env.PROD`

5. **Static assets**:
   - `public/` folder — served as-is at root, not processed
   - Import assets in code — get hashed URLs: `import logo from './logo.png'`
   - `?url`, `?raw`, `?worker` suffixes for special handling

6. **Path aliases**:
   ```typescript
   // vite.config.ts
   resolve: {
     alias: {
       '@': path.resolve(__dirname, './src'),
     },
   }
   ```
   Also update `tsconfig.json` paths for TypeScript:
   ```json
   {
     "compilerOptions": {
       "paths": { "@/*": ["./src/*"] }
     }
   }
   ```

7. **CSS handling**:
   - `.css` imports are injected as `<style>` tags in dev, extracted in build
   - `.module.css` — CSS Modules (scoped class names)
   - PostCSS — auto-detected from `postcss.config.js`
   - Sass/Less/Stylus — install preprocessor, import directly

8. **Basic plugins**: Plugins are functions that return objects with hooks:
   ```typescript
   plugins: [react(), somePlugin()]
   ```

9. **Build**: `vite build` produces optimized output in `dist/`.

10. **Preview**: `vite preview` serves the built output locally.

#### Common Beginner Mistakes

- Forgetting `VITE_` prefix on env vars
- Putting processed assets in `public/` instead of `src/`
- Not updating `tsconfig.json` paths when adding aliases
- Using `__dirname` without `import path from 'path'` in config
- Importing Node.js built-ins in client code
- Not understanding that `public/` files don't get hashed
- Confusing `import.meta.env` with `process.env`
- Using CommonJS (`require()`) in source files
- Not installing CSS preprocessors (`sass`, `less`)
- Running `vite build` without checking `base` config for non-root deployments

#### 10 Beginner Exercises

1. Create a React + TS Vite app and deploy to Vercel
2. Add path aliases (`@/components`, `@/utils`) with TS support
3. Use environment variables for API URL in dev vs production
4. Import and display an image, SVG, and JSON file
5. Add Tailwind CSS with PostCSS
6. Create a CSS Module component with scoped styles
7. Add Sass and create a theme variables file
8. Configure the dev server to proxy API requests
9. Build the app and analyze the output in `dist/`
10. Add a custom `index.html` title per environment

---

### Level 2 — Junior

**Goal**: Understand how Vite works under the hood and configure it effectively.

#### Core Topics

1. **Advanced `vite.config.ts`**:
   ```typescript
   import { defineConfig, loadEnv } from 'vite'

   export default defineConfig(({ command, mode }) => {
     const env = loadEnv(mode, process.cwd(), '')
     return {
       define: {
         __APP_VERSION__: JSON.stringify(env.npm_package_version),
       },
       server: {
         port: 3000,
         proxy: {
           '/api': {
             target: 'http://localhost:8080',
             changeOrigin: true,
           },
         },
       },
       build: {
         sourcemap: true,
         rollupOptions: {
           output: {
             manualChunks: {
               vendor: ['react', 'react-dom'],
             },
           },
         },
       },
     }
   })
   ```

2. **Dependency optimization**:
   - Vite pre-bundles `node_modules` with esbuild on first run
   - Cached in `node_modules/.vite/deps`
   - `optimizeDeps.include` — force pre-bundle specific packages
   - `optimizeDeps.exclude` — skip pre-bundling (e.g., for linked packages)
   - WHY: CJS→ESM conversion, reduce HTTP requests (lodash has 600+ modules)

3. **HMR behavior**:
   - React Fast Refresh via `@vitejs/plugin-react`
   - CSS changes are instant (injected style tags)
   - Full reload triggers: config change, HTML change, no HMR boundary found
   - `import.meta.hot.accept()` makes a module an HMR boundary

4. **Code splitting**:
   ```typescript
   // Automatic via dynamic import
   const LazyComponent = React.lazy(() => import('./HeavyComponent'))

   // Manual chunks
   build: {
     rollupOptions: {
       output: {
         manualChunks(id) {
           if (id.includes('node_modules')) {
             return 'vendor'
           }
         },
       },
     },
   }
   ```

5. **Dynamic imports**: `import('./module.ts')` creates a separate chunk. Vite handles this in both dev (native ESM) and build (Rollup chunks).

6. **Environment modes**:
   - `vite` → development mode
   - `vite build` → production mode
   - `vite build --mode staging` → custom mode, loads `.env.staging`
   - `vite --mode test` → custom dev mode

7. **Asset handling strategies**:
   - `import img from './img.png'` → URL (hashed in build)
   - `import img from './img.png?url'` → explicit URL
   - `import raw from './file.txt?raw'` → string content
   - `import worker from './worker.ts?worker'` → Web Worker
   - `new URL('./img.png', import.meta.url)` → works with dynamic paths

8. **SVG strategies**:
   - Import as URL (default): `import svg from './icon.svg'` → URL string
   - `vite-plugin-svgr` → import as React component
   - `?react` suffix with svgr plugin → `import Icon from './icon.svg?react'`
   - Inline SVG via `?raw` → string to dangerouslySetInnerHTML (avoid)

#### Common Anti-Patterns

- Importing everything at top level (defeats code splitting)
- Using `manualChunks` with too many small chunks (more HTTP requests)
- Not configuring `optimizeDeps.include` for problematic packages
- Using `process.env` instead of `import.meta.env`
- Building without `sourcemap` in staging environments
- Ignoring bundle size warnings
- Over-relying on barrel files (`index.ts` re-exports) — hurts tree-shaking and HMR

#### 10 Mini Project Ideas

1. Multi-page app with shared layout and per-page entry points
2. Markdown blog with `import.meta.glob` for content loading
3. Component library in library mode with TypeScript declarations
4. Dashboard with lazy-loaded route modules and loading states
5. App with Web Workers for CPU-intensive computation
6. Internationalized app with dynamic locale loading
7. Theme switcher using CSS variables + CSS modules
8. API dashboard with proxy configuration and mock server
9. App with WASM module integration
10. Micro-frontend shell that lazy-loads remote components

---

### Level 3 — Senior

**Goal**: Architect scalable Vite setups, write plugins, optimize builds, integrate with monorepos and CI/CD.

#### Plugin Architecture

Every Vite plugin is a Rollup plugin superset. Vite adds extra hooks:

```typescript
import type { Plugin } from 'vite'

function myPlugin(): Plugin {
  return {
    name: 'my-plugin',
    enforce: 'pre', // 'pre' | undefined | 'post'
    apply: 'serve', // 'serve' | 'build' | undefined (both)

    // Vite-specific hooks
    config(config, env) { /* modify config */ },
    configResolved(config) { /* read final config */ },
    configureServer(server) { /* add middleware */ },
    transformIndexHtml(html) { /* transform HTML */ },
    handleHotUpdate(ctx) { /* custom HMR */ },

    // Rollup-compatible hooks
    resolveId(source, importer) { /* custom resolution */ },
    load(id) { /* custom loading */ },
    transform(code, id) { /* transform source */ },
  }
}
```

#### Plugin Execution Order

```
Alias resolution
    ↓
enforce: 'pre' plugins
    ↓
Vite core plugins (resolve, CSS, assets, etc.)
    ↓
Normal plugins (no enforce)
    ↓
Vite build plugins
    ↓
enforce: 'post' plugins
    ↓
Vite post-build plugins (minify, manifest, etc.)
```

#### SSR Architecture

```typescript
// vite.config.ts
export default defineConfig({
  ssr: {
    // Dependencies to bundle for SSR (default: externalized)
    noExternal: ['some-css-in-js-lib'],
    // Force externalize
    external: ['heavy-node-lib'],
  },
})

// server.js (Express example)
import { createServer as createViteServer } from 'vite'

const vite = await createViteServer({
  server: { middlewareMode: true },
  appType: 'custom',
})

app.use(vite.middlewares)

app.use('*', async (req, res) => {
  const template = await vite.transformIndexHtml(req.url, rawHtml)
  const { render } = await vite.ssrLoadModule('/src/entry-server.tsx')
  const appHtml = await render(req.url)
  const html = template.replace('<!--app-->', appHtml)
  res.status(200).set({ 'Content-Type': 'text/html' }).end(html)
})
```

#### Monorepo Integration

```typescript
// apps/web/vite.config.ts in a pnpm workspace
import { defineConfig } from 'vite'

export default defineConfig({
  resolve: {
    // Ensure linked packages resolve to source
    conditions: ['development', 'module'],
  },
  optimizeDeps: {
    // Don't pre-bundle workspace packages
    exclude: ['@myorg/ui', '@myorg/utils'],
  },
  server: {
    // Watch workspace packages for HMR
    watch: {
      ignored: ['!**/node_modules/@myorg/**'],
    },
  },
})
```

#### Build Optimization

```typescript
export default defineConfig({
  build: {
    target: 'es2020',
    minify: 'terser', // or 'esbuild' (faster, less optimal)
    cssMinify: 'lightningcss',
    rollupOptions: {
      output: {
        manualChunks(id) {
          if (id.includes('node_modules')) {
            if (id.includes('react')) return 'react-vendor'
            if (id.includes('@mui')) return 'mui-vendor'
            return 'vendor'
          }
        },
      },
    },
    reportCompressedSize: false, // faster builds in CI
    chunkSizeWarningLimit: 1000,
  },
})
```

#### Docker Optimization

```dockerfile
# Multi-stage build
FROM node:20-alpine AS deps
WORKDIR /app
COPY package.json pnpm-lock.yaml ./
RUN corepack enable && pnpm install --frozen-lockfile

FROM node:20-alpine AS builder
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .
RUN pnpm build

FROM nginx:alpine AS runner
COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
```

#### CI/CD Optimization

```yaml
# GitHub Actions
- name: Cache Vite deps
  uses: actions/cache@v4
  with:
    path: |
      node_modules/.vite
      ~/.cache
    key: vite-${{ hashFiles('pnpm-lock.yaml') }}

- name: Build
  run: pnpm build
  env:
    NODE_OPTIONS: '--max-old-space-size=8192'
```

#### Library Mode

```typescript
// vite.config.ts for a library
import { defineConfig } from 'vite'
import { resolve } from 'path'
import dts from 'vite-plugin-dts'

export default defineConfig({
  plugins: [dts({ rollupTypes: true })],
  build: {
    lib: {
      entry: resolve(__dirname, 'src/index.ts'),
      name: 'MyLib',
      formats: ['es', 'cjs'],
      fileName: (format) => `index.${format === 'es' ? 'mjs' : 'cjs'}`,
    },
    rollupOptions: {
      external: ['react', 'react-dom'],
      output: {
        globals: { react: 'React', 'react-dom': 'ReactDOM' },
      },
    },
  },
})
```

#### 10 Production-Grade Project Examples

1. Design system library with Storybook + library mode + npm publishing
2. SSR React app with streaming HTML and API routes
3. Monorepo with shared configs, component library, and 3 apps
4. Multi-page marketing site with per-page JS bundles
5. Dashboard with route-based code splitting and prefetching
6. Cloudflare Workers app with Vite-built worker bundles
7. Internal admin platform with plugin-based feature modules
8. E-commerce storefront with SSR + edge caching
9. CLI tool that uses Vite's JS API for building user plugins
10. Microfrontend host/remote architecture with Module Federation

---

### Level 4 — Expert

**Goal**: Understand Vite internals, debug complex build issues, architect large-scale systems.

#### Module Graph Internals

The module graph is a directed graph where:
- **Nodes** = `EnvironmentModuleNode` instances (url, id, file, transformResult, importers, importedModules, HMR state)
- **Edges** = import relationships discovered during transform

```
EnvironmentModuleNode {
  url: '/src/App.tsx'
  id: '/absolute/path/src/App.tsx'
  file: '/absolute/path/src/App.tsx'
  type: 'js'
  importers: Set<EnvironmentModuleNode>     // who imports me
  importedModules: Set<EnvironmentModuleNode> // who I import
  acceptedHmrDeps: Set<EnvironmentModuleNode> // HMR accepted deps
  isSelfAccepting: boolean                    // has hot.accept()
  transformResult: { code, map, etag }        // cached result
  lastHMRTimestamp: number
  lastInvalidationTimestamp: number
}
```

Key operations:
- `getModuleByUrl(url)` — lookup by request URL
- `getModuleById(id)` — lookup by resolved ID
- `invalidateModule(mod)` — clear cached transform, mark stale
- `onFileChange(file)` — triggered by file watcher

#### HMR Invalidation Algorithm

```
1. File changes detected (chokidar)
2. Find module(s) mapped to that file
3. Invalidate transform cache for those modules
4. For each invalidated module:
   a. If module is self-accepting → update just this module
   b. If module is accepted by an importer → walk up to that importer
   c. If no boundary found after walking entire importer chain → full reload
   d. If circular dependency creates infinite walk → full reload
5. Collect all boundary modules
6. Send WebSocket message: { type: 'update', updates: [...] }
7. Client fetches fresh module via ?t=timestamp cache-busting
8. Client executes accept callback with new module
```

#### Plugin Pipeline Internals

Vite creates a **Plugin Container** that wraps Rollup's plugin driver. In dev, it processes files on demand. In build, Rollup drives it.

```
Request → resolveId() chain → load() chain → transform() chain → serve

Each hook runs through all plugins in order:
  enforce:'pre' → normal → enforce:'post'

Hooks can:
  - Return null → pass to next plugin
  - Return value → stop chain (for resolveId, load)
  - Return transformed code → passed to next transform
```

#### Transform Lifecycle Detail

```
1. resolveId(source, importer, options)
   - Converts import specifier to absolute ID
   - Handles aliases, virtual modules, bare imports
   - First non-null return wins

2. load(id)
   - Reads file content (or generates virtual content)
   - Default: fs.readFile

3. transform(code, id)
   - All plugins run sequentially
   - TypeScript → JS (esbuild)
   - JSX → JS (esbuild or Babel)
   - CSS Modules → JS with class map
   - Each transform receives previous transform's output
```

#### Advanced SSR Internals

Vite's SSR uses a separate **module runner** in Node.js:

- `ssrLoadModule(url)` — transforms code then evaluates in Node.js
- Module runner has its own module cache separate from dev server
- `ssr.noExternal` — bundle dependency into SSR output (needed for CSS-in-JS, ESM-only packages)
- `ssr.external` — leave as Node.js require/import (faster, uses node_modules directly)

Environment API (Vite 6+): Each environment (client, ssr, custom) gets its own module graph, plugin pipeline, and resolve conditions.

#### What Experts Care About That Juniors Miss

1. **Import chain depth** — deep import chains slow HMR because invalidation walks up
2. **Barrel file explosion** — `index.ts` re-exporting everything forces loading unused modules
3. **Pre-bundling cache invalidation** — lockfile changes, config changes, `include` changes trigger full re-prebundle
4. **Chunk deduplication** — shared dependencies between chunks can duplicate if not configured
5. **Source map quality** — `sourcemap: true` in production doubles build time and output size
6. **CSS ordering** — non-deterministic CSS chunk ordering in code-split apps
7. **Module resolution differences** — dev (native ESM conditions) vs build (Rollup conditions) can diverge
8. **Transform caching** — `304 Not Modified` responses depend on ETag, `If-None-Match`
9. **Worker modules** — separate build context, don't share module graph
10. **Environment-specific behavior** — plugins must handle both `serve` and `build` commands

#### 15 Advanced Engineering Discussion Topics

1. How does Vite's module graph differ from Webpack's dependency graph?
2. What are the trade-offs of native ESM dev vs. bundled dev (Turbopack approach)?
3. When does dependency pre-bundling become a bottleneck?
4. How should you architect HMR boundaries in a large app?
5. What causes dev/prod behavior differences and how to prevent them?
6. How does Rollup's tree-shaking interact with barrel files?
7. When should you use `manualChunks` vs let Rollup decide?
8. How do CSS chunk ordering issues manifest and how to solve them?
9. What is the correct architecture for SSR with streaming?
10. How do module resolution conditions affect library compatibility?
11. What causes the "optimized dependency changed" loop?
12. How should plugins handle per-environment state?
13. When is `worker` mode needed vs. `SharedWorker` vs. Service Worker?
14. How does Vite's file watcher strategy affect monorepo performance?
15. What are the implications of Rolldown replacing Rollup in Vite?

---

### Level 5 — Tooling / Bundler Engineer Mindset

**Goal**: Understand WHY build tools work the way they do. Think at the toolchain architecture level.

#### Dev Server Internals

Vite's dev server is a Connect (Express-like) HTTP server that:

1. Intercepts requests for `.ts`, `.tsx`, `.jsx`, `.css`, `.vue`, `.svelte`, etc.
2. Runs the plugin pipeline (resolveId → load → transform)
3. Rewrites bare imports: `import React from 'react'` → `import React from '/node_modules/.vite/deps/react.js?v=abc123'`
4. Adds HMR client injection to HTML
5. Serves pre-bundled deps from `.vite/deps/` with strong caching (`max-age=31536000,immutable`)
6. Serves source files with `304 Not Modified` based on ETag

#### Native ESM Philosophy

The fundamental insight: **the browser is the bundler during development**.

```
Traditional:  Source → [Bundler] → Bundle → Browser
Vite dev:     Source → [Transform] → ESM → Browser (browser resolves imports)
```

This means:
- No bundling step for source code
- File-level caching (change one file, only that file is re-requested)
- Import waterfall problem for dependencies (solved by pre-bundling)
- Browser import map support is emerging (can eventually replace pre-bundling)

#### Browser Caching Behavior in Dev

| Resource | Cache Strategy | Why |
|----------|---------------|-----|
| Pre-bundled deps | `max-age=31536000,immutable` | Content-hashed filename, changes = new URL |
| Source files | `304 Not Modified` + ETag | Allows instant cache validation |
| HMR updates | `?t=timestamp` cache-bust | Forces fresh fetch after invalidation |

#### File Watcher Internals

Vite uses **chokidar** to watch the project root (excluding `node_modules`, `.git`):

- File change → find mapped modules → invalidate → trigger HMR
- File add → may trigger new module discovery
- File delete → remove from module graph, trigger HMR prune
- Config file change → full server restart
- `package.json` / lockfile change → re-run dependency optimization

#### HMR Protocol

WebSocket messages between server and client:

```typescript
// Server → Client
{ type: 'connected' }
{ type: 'update', updates: [{ type: 'js-update', path, acceptedPath, timestamp }] }
{ type: 'full-reload', path?: string }
{ type: 'prune', paths: string[] }
{ type: 'error', err: { message, stack, plugin, id, loc } }
{ type: 'custom', event: string, data: any }
```

Client behavior:
1. Receive `update` → dynamic import module with `?t=timestamp` → execute `accept` callback
2. Receive `full-reload` → `location.reload()`
3. Receive `prune` → execute `prune` callbacks for removed modules

#### Rollup Graph Internals

Rollup builds a module graph, then chunks it:

1. **Module graph phase**: resolve → load → transform for every reachable module
2. **Chunk assignment**: based on entry points, dynamic imports, and `manualChunks`
3. **Chunk optimization**: merge small chunks, handle circular references
4. **Rendering**: generate code per chunk, scope hoisting, banner/footer
5. **Output**: write files with content hashes

#### Plugin Container Internals

```
PluginContainer {
  // Wraps Rollup's plugin driver
  // In dev: processes files on demand
  // In build: Rollup calls hooks

  resolveId(source, importer) {
    // Run through all plugin resolveId hooks in order
    // First non-null return wins
  }

  load(id) {
    // Run through all plugin load hooks
    // Default: fs.readFile
  }

  transform(code, id) {
    // Run through ALL plugin transform hooks sequentially
    // Each receives previous output
    // Source maps are composed
  }
}
```

#### AST Transform Pipelines

```
Source (.tsx)
    │
    ▼ esbuild (TS strip + JSX transform) — FAST, no type checking
    │
    ▼ Plugin transforms (e.g., auto-imports, macro expansion)
    │
    ▼ Import analysis (rewrite bare imports, inject HMR preamble)
    │
    ▼ Final module served to browser
```

In production, Rollup does a full AST parse for tree-shaking and scope hoisting.

#### Future of Frontend Tooling

| Trend | Implication |
|-------|------------|
| **Rolldown** (Rust Rollup) | Will unify dev/build into one tool, massive speed gains |
| **Import maps** | Browser-native dependency resolution, may reduce pre-bundling need |
| **Rust/Go compilers** | SWC, esbuild, oxc — transform speed is no longer the bottleneck |
| **Environment API** | Per-environment module graphs enable better SSR, RSC, edge |
| **Module Runner** | Run Vite-transformed code in any runtime (Node, Deno, Workers) |

---

## 3. Vite 8 Deep Dive

> **Note**: As of the knowledge cutoff, Vite 6 is the latest stable release with Vite 7 in development. This section covers the evolution from Vite 5 → 6 → 7 and the architectural trajectory toward Vite 8. Update this section as Vite 8 is officially released.

### Vite 5 → 6 Migration

**Key changes in Vite 6:**

1. **Environment API** — The biggest architectural change. Each environment (client, ssr, custom) gets its own:
   - Module graph (`EnvironmentModuleGraph`)
   - Plugin pipeline
   - Resolve conditions
   - Dev server processing

2. **`hotUpdate` hook** replaces `handleHotUpdate`:
   ```typescript
   // Old (deprecated)
   handleHotUpdate({ server, modules }) {
     server.ws.send({ type: 'full-reload' })
   }

   // New
   hotUpdate({ modules }) {
     this.environment.hot.send({ type: 'full-reload' })
   }
   ```

3. **`ModuleRunner`** replaces `ssrLoadModule` for running Vite-transformed code in target runtimes.

4. **Per-environment plugins** with `this.environment` context in hooks.

5. **Deprecation warnings** for server-level APIs:
   ```typescript
   future: {
     removeServerModuleGraph: 'warn',
     removeServerTransformRequest: 'warn',
     removeServerHot: 'warn',
   }
   ```

6. **Node.js 18+ required** (dropped Node 16).

### Vite 6 → 7 Migration

Key expected changes:
- **Rolldown integration** — Rust-based bundler replacing esbuild for pre-bundling and potentially Rollup for production
- **Unified dev/build pipeline** — same bundler for both, reducing behavior divergence
- **Performance improvements** — Rust-based transforms and module resolution
- **Deprecated API removal** — server-level module graph, plugin container, hot channel

### Vite 7 → 8 Trajectory

Expected architectural direction:
- **Full Rolldown adoption** for both dev and production builds
- **oxc-based transforms** replacing esbuild for TypeScript/JSX
- **Improved chunking algorithms** from Rolldown
- **Better monorepo performance** via persistent caching
- **Enhanced Environment API** maturity

### WHY These Changes Matter

| Change | For Frontend Engineers | For Plugin Authors | For Large Apps |
|--------|----------------------|-------------------|----------------|
| Environment API | SSR/RSC becomes first-class | Must use `this.environment` | Better isolation, fewer bugs |
| Rolldown | Faster builds | New plugin hooks possible | Unified dev/prod behavior |
| ModuleRunner | Better SSR DX | New runtime targets | Edge/Worker compatibility |
| Per-env plugins | Clearer mental model | Per-env state management | Reduced cross-env bugs |

### Migration Concerns

**Monorepo**: Update all apps simultaneously since shared configs and plugins must be compatible with new APIs.

**CI/CD**: Rolldown may change output chunk structure — update cache keys, asset patterns, and deployment scripts.

**Plugin compatibility**: Check plugin repos for Environment API support. Many plugins need updates for `this.environment` context.

---

## 4. Setup Guide

### React + Vite + TypeScript — Production-Grade Setup

#### Project Structure

```
my-app/
├── public/
│   └── favicon.svg
├── src/
│   ├── assets/
│   ├── components/
│   │   └── ui/
│   ├── features/
│   │   └── auth/
│   │       ├── components/
│   │       ├── hooks/
│   │       ├── api/
│   │       └── index.ts
│   ├── hooks/
│   ├── lib/
│   ├── pages/
│   ├── styles/
│   │   ├── global.css
│   │   └── variables.css
│   ├── types/
│   ├── utils/
│   ├── App.tsx
│   ├── main.tsx
│   └── vite-env.d.ts
├── tests/
│   ├── setup.ts
│   └── utils.tsx
├── .env
├── .env.production
├── index.html
├── package.json
├── postcss.config.js
├── tailwind.config.ts
├── tsconfig.json
├── tsconfig.node.json
├── vite.config.ts
└── vitest.config.ts
```

#### Scalable `vite.config.ts`

```typescript
import { defineConfig, loadEnv, type PluginOption } from 'vite'
import react from '@vitejs/plugin-react'
import tsconfigPaths from 'vite-tsconfig-paths'
import { resolve } from 'path'

export default defineConfig(({ command, mode }) => {
  const env = loadEnv(mode, process.cwd(), '')
  const isProd = mode === 'production'
  const isTest = mode === 'test'

  const plugins: PluginOption[] = [
    react(),
    tsconfigPaths(),
  ]

  return {
    plugins,

    resolve: {
      alias: {
        '@': resolve(__dirname, 'src'),
      },
    },

    server: {
      port: 3000,
      strictPort: true,
      proxy: {
        '/api': {
          target: env.VITE_API_URL || 'http://localhost:8080',
          changeOrigin: true,
          rewrite: (path) => path.replace(/^\/api/, ''),
        },
      },
    },

    build: {
      target: 'es2020',
      sourcemap: isProd ? 'hidden' : true,
      reportCompressedSize: false,
      rollupOptions: {
        output: {
          manualChunks(id) {
            if (id.includes('node_modules')) {
              if (id.includes('react')) return 'react-vendor'
              return 'vendor'
            }
          },
        },
      },
    },

    css: {
      modules: {
        localsConvention: 'camelCase',
      },
      devSourcemap: true,
    },

    test: {
      globals: true,
      environment: 'jsdom',
      setupFiles: './tests/setup.ts',
      css: true,
    },

    define: {
      __APP_VERSION__: JSON.stringify(process.env.npm_package_version),
    },
  }
})
```

#### Vitest Setup

```typescript
// vitest.config.ts (or inline in vite.config.ts)
import { defineConfig } from 'vitest/config'

export default defineConfig({
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: './tests/setup.ts',
    include: ['src/**/*.{test,spec}.{ts,tsx}'],
    coverage: {
      provider: 'v8',
      reporter: ['text', 'lcov'],
      exclude: ['node_modules/', 'tests/'],
    },
  },
})
```

```typescript
// tests/setup.ts
import '@testing-library/jest-dom/vitest'
```

#### Tailwind CSS Setup

```bash
npm install -D tailwindcss @tailwindcss/postcss postcss
```

```javascript
// postcss.config.js
export default {
  plugins: {
    '@tailwindcss/postcss': {},
  },
}
```

```css
/* src/styles/global.css */
@import 'tailwindcss';
```

#### Storybook Setup

```bash
npx storybook@latest init --builder @storybook/builder-vite
```

Storybook auto-detects Vite and reuses your `vite.config.ts`.

#### SVG Setup

```bash
npm install -D vite-plugin-svgr
```

```typescript
// vite.config.ts
import svgr from 'vite-plugin-svgr'

plugins: [
  react(),
  svgr({
    svgrOptions: { icon: true },
  }),
]
```

```typescript
// Usage
import Logo from './logo.svg?react' // React component
import logoUrl from './logo.svg'     // URL string
```

#### ESLint Setup

```bash
npm install -D eslint @eslint/js typescript-eslint eslint-plugin-react-hooks
```

#### Monorepo Integration (pnpm workspace)

```yaml
# pnpm-workspace.yaml
packages:
  - 'apps/*'
  - 'packages/*'
```

```typescript
// apps/web/vite.config.ts
export default defineConfig({
  optimizeDeps: {
    exclude: ['@myorg/ui'], // don't pre-bundle workspace packages
  },
  server: {
    watch: {
      ignored: ['!**/node_modules/@myorg/**'],
    },
  },
})
```

#### Docker Integration

```dockerfile
FROM node:20-alpine AS base
RUN corepack enable

FROM base AS deps
WORKDIR /app
COPY package.json pnpm-lock.yaml ./
RUN pnpm install --frozen-lockfile --prod=false

FROM base AS build
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .
ARG VITE_API_URL
ENV VITE_API_URL=$VITE_API_URL
RUN pnpm build

FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
```

#### Multi-Environment Builds

```bash
# .env.staging
VITE_API_URL=https://staging-api.example.com
VITE_SENTRY_DSN=...

# Build for staging
vite build --mode staging
```

#### SSR Setup

```typescript
// vite.config.ts
export default defineConfig({
  plugins: [react()],
  ssr: {
    noExternal: ['styled-components'], // bundle for SSR
  },
  build: {
    ssr: true, // when building SSR bundle
  },
})
```

#### Library Mode Setup

```typescript
export default defineConfig({
  build: {
    lib: {
      entry: resolve(__dirname, 'src/index.ts'),
      formats: ['es', 'cjs'],
      fileName: (format) => `index.${format === 'es' ? 'mjs' : 'cjs'}`,
    },
    rollupOptions: {
      external: ['react', 'react-dom', 'react/jsx-runtime'],
    },
  },
})
```

### Recommended Architecture for Your Stack

Given your background (React, Next.js, Astro, TypeScript, monorepos, CI/CD, Docker, Cloudflare Workers):

```
monorepo/
├── apps/
│   ├── web/              # Vite + React SPA or SSR
│   ├── docs/             # Astro (uses Vite internally)
│   └── admin/            # Vite + React
├── packages/
│   ├── ui/               # Component library (Vite library mode)
│   ├── utils/            # Pure TS utils
│   ├── config/           # Shared Vite configs
│   │   ├── vite.base.ts
│   │   ├── eslint.config.js
│   │   └── tsconfig.base.json
│   └── types/            # Shared TypeScript types
├── workers/
│   └── api/              # Cloudflare Workers (Wrangler, not Vite)
├── pnpm-workspace.yaml
├── turbo.json            # or nx.json
└── package.json
```

Shared Vite config:
```typescript
// packages/config/vite.base.ts
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tsconfigPaths from 'vite-tsconfig-paths'

export const createViteConfig = (overrides = {}) =>
  defineConfig({
    plugins: [react(), tsconfigPaths()],
    build: {
      target: 'es2020',
      sourcemap: true,
      reportCompressedSize: false,
    },
    ...overrides,
  })
```

---

## 5. Vite Ecosystem Comparison

| Dimension | Vite | Webpack | Turbopack | Rspack | Parcel | Rollup | esbuild | SWC | Rolldown |
|-----------|------|---------|-----------|--------|--------|--------|---------|-----|----------|
| **Language** | JS/TS | JS | Rust | Rust | JS/Rust | JS | Go | Rust | Rust |
| **Philosophy** | Native ESM dev | Bundle everything | Incremental compute | Webpack-compat speed | Zero config | ES output quality | Raw speed | Transform speed | Rollup-compat speed |
| **Dev mode** | ESM + pre-bundle | Full bundle | Turbo engine | Full bundle | Full bundle | N/A (lib) | N/A (lib) | N/A (transform) | ESM + pre-bundle |
| **HMR** | Excellent | Good | Excellent | Good | Good | N/A | N/A | N/A | Excellent |
| **Build speed** | Fast | Slow | Very fast | Very fast | Medium | Medium | Very fast | Very fast (transform) | Very fast |
| **Tree-shaking** | Excellent (Rollup) | Good | Good | Good | Good | Excellent | Basic | N/A | Excellent |
| **Plugin system** | Rollup-compat | Webpack API | Webpack-compat | Webpack-compat | Parcel API | Rollup API | Go API | Rust/JS API | Rollup-compat |
| **SSR** | Built-in primitives | Manual | Next.js native | Manual | Limited | N/A | N/A | N/A | Planned |
| **Monorepo** | Good | Good | Excellent (Turbo) | Good | Limited | N/A | N/A | N/A | Good |
| **Config complexity** | Low | High | Next.js only | Medium | Zero | Medium | Low | Low | Low |
| **Ecosystem** | Large, growing | Massive | Next.js ecosystem | Growing | Medium | Large | Medium | Large | Early |

### When to Choose Each

| Tool | Choose When | Avoid When |
|------|------------|------------|
| **Vite** | New projects, React/Vue/Svelte SPAs, libraries, SSR with frameworks | Legacy Webpack plugin dependency, very large enterprise apps (today) |
| **Webpack** | Existing large apps, need specific Webpack plugins, complex SSR | New projects (too slow), simple apps |
| **Turbopack** | Using Next.js | Not using Next.js (tightly coupled) |
| **Rspack** | Migrating from Webpack, need speed + Webpack compat | New projects without Webpack investment |
| **Parcel** | Quick prototypes, zero-config needs | Production apps needing fine control |
| **Rollup** | Libraries, need best tree-shaking | Applications (no dev server, HMR) |
| **esbuild** | Custom tooling, transform step, extreme speed | Need tree-shaking quality, plugin ecosystem |
| **Rolldown** | Future Vite integration | Production use today (still maturing) |

---

## 6. Plugin Architecture Deep Dive

### Plugin Hook Lifecycle

```
Server start / Build start
│
├── config(config, env)           → Modify config before resolution
├── configResolved(config)        → Read final config
├── configureServer(server)       → Add dev server middleware
├── buildStart()                  → Build begins
│
│   For each module:
│   ├── resolveId(source, importer) → Custom module resolution
│   ├── load(id)                    → Custom module loading
│   └── transform(code, id)         → Transform source code
│
├── handleHotUpdate(ctx)          → Custom HMR handling (deprecated)
├── hotUpdate(options)            → Custom HMR handling (new)
│
│   Build end:
│   ├── generateBundle(options, bundle) → Inspect/modify output
│   ├── writeBundle(options, bundle)    → Post-write actions
│   └── closeBundle()                   → Cleanup
│
└── configurePreviewServer(server) → Add preview server middleware
```

### Virtual Modules

```typescript
import { exactRegex } from '@rolldown/pluginutils'

function virtualModulePlugin(): Plugin {
  const virtualId = 'virtual:app-config'
  const resolvedId = '\0' + virtualId

  return {
    name: 'virtual-app-config',
    resolveId: {
      filter: { id: exactRegex(virtualId) },
      handler() { return resolvedId },
    },
    load: {
      filter: { id: exactRegex(resolvedId) },
      handler() {
        return `
          export const config = {
            version: '${process.env.npm_package_version}',
            buildTime: '${new Date().toISOString()}',
          }
        `
      },
    },
  }
}
```

### Custom Transform Plugin

```typescript
function autoImportPlugin(): Plugin {
  return {
    name: 'auto-import',
    enforce: 'pre',
    transform(code, id) {
      if (!id.endsWith('.tsx') && !id.endsWith('.ts')) return

      // Example: auto-import React if JSX is used
      if (code.includes('<') && !code.includes("from 'react'")) {
        return {
          code: `import React from 'react';\n${code}`,
          map: null,
        }
      }
    },
  }
}
```

### Custom HMR Plugin

```typescript
function hmrNotifyPlugin(): Plugin {
  return {
    name: 'hmr-notify',
    hotUpdate({ file, modules, timestamp }) {
      if (this.environment.name !== 'client') return

      if (file.endsWith('.css')) {
        // CSS-only update — let Vite handle it
        return
      }

      if (file.includes('/config/')) {
        // Config files changed — force full reload
        const invalidated = new Set()
        for (const mod of modules) {
          this.environment.moduleGraph.invalidateModule(mod, invalidated, timestamp, true)
        }
        this.environment.hot.send({ type: 'full-reload' })
        return []
      }
    },
  }
}
```

### Dev Server Middleware Plugin

```typescript
function apiMockPlugin(): Plugin {
  return {
    name: 'api-mock',
    configureServer(server) {
      // Pre-middleware (runs before Vite's internal middleware)
      server.middlewares.use('/api/health', (req, res) => {
        res.setHeader('Content-Type', 'application/json')
        res.end(JSON.stringify({ status: 'ok' }))
      })

      // Post-middleware (runs after Vite's internal middleware)
      return () => {
        server.middlewares.use((req, res, next) => {
          // Fallback handling
          next()
        })
      }
    },
  }
}
```

### HTML Transform Plugin

```typescript
function injectMetaPlugin(): Plugin {
  return {
    name: 'inject-meta',
    transformIndexHtml(html) {
      return {
        html,
        tags: [
          {
            tag: 'meta',
            attrs: { name: 'build-time', content: new Date().toISOString() },
            injectTo: 'head',
          },
          {
            tag: 'script',
            children: `window.__APP_VERSION__ = '${process.env.npm_package_version}'`,
            injectTo: 'head-prepend',
          },
        ],
      }
    },
  }
}
```

### Plugin for Library/Monorepo: Auto-External

```typescript
function autoExternalPlugin(patterns: RegExp[]): Plugin {
  return {
    name: 'auto-external',
    apply: 'build',
    config() {
      return {
        build: {
          rollupOptions: {
            external: (id) => patterns.some(p => p.test(id)),
          },
        },
      }
    },
  }
}
```

### Plugin Debugging Tips

```typescript
function debugPlugin(): Plugin {
  return {
    name: 'debug',
    resolveId(source, importer) {
      console.log(`[resolve] ${source} from ${importer}`)
    },
    load(id) {
      console.log(`[load] ${id}`)
    },
    transform(code, id) {
      console.log(`[transform] ${id} (${code.length} chars)`)
    },
  }
}
```

Use `DEBUG=vite:*` environment variable for Vite's internal debug logs:
```bash
DEBUG=vite:resolve,vite:transform vite
```

---

## 7. Cheatsheet

### vite.config Patterns

```typescript
// Function config (access command/mode)
export default defineConfig(({ command, mode }) => ({ ... }))

// Load env
const env = loadEnv(mode, process.cwd(), '')

// Conditional plugins
plugins: [react(), isProd && legacy()].filter(Boolean)

// Proxy
server: { proxy: { '/api': 'http://localhost:8080' } }

// Aliases
resolve: { alias: { '@': resolve(__dirname, 'src') } }

// Define globals
define: { __VERSION__: JSON.stringify('1.0.0') }
```

### Environment Variables

| File | Loaded When |
|------|------------|
| `.env` | Always |
| `.env.local` | Always (gitignored) |
| `.env.development` | `vite` (dev) |
| `.env.production` | `vite build` |
| `.env.[mode]` | `--mode [mode]` |
| `.env.[mode].local` | `--mode [mode]` (gitignored) |

Priority: `.env.[mode].local` > `.env.[mode]` > `.env.local` > `.env`

### Dynamic Import Patterns

```typescript
// Route-level code splitting
const Page = React.lazy(() => import('./pages/About'))

// Glob import
const modules = import.meta.glob('./modules/*.ts')
// Returns: { './modules/a.ts': () => import('./modules/a.ts'), ... }

// Eager glob
const modules = import.meta.glob('./modules/*.ts', { eager: true })

// Glob with named export
const modules = import.meta.glob('./modules/*.ts', { import: 'setup' })
```

### Asset Handling

```typescript
import imgUrl from './img.png'         // → URL
import rawText from './data.txt?raw'   // → string
import workerUrl from './w.ts?worker'  // → Worker
import wasmInit from './m.wasm?init'   // → init function

// Dynamic asset URL
new URL(`./assets/${name}.png`, import.meta.url).href
```

### Common Commands

```bash
vite                          # Dev server
vite build                    # Production build
vite preview                  # Preview production build
vite build --mode staging     # Build with custom mode
vite optimize                 # Re-run dep optimization
vite --debug hmr              # Debug HMR
DEBUG=vite:* vite             # All debug logs
```

### Common Errors & Fixes

| Error | Cause | Fix |
|-------|-------|-----|
| `require is not defined` | CJS module in ESM context | Add to `optimizeDeps.include` |
| `process is not defined` | Node global used in browser | Use `define: { 'process.env': {} }` |
| Pre-bundling loop | Dep keeps changing | Pin with `optimizeDeps.include` |
| HMR full reload | No HMR boundary found | Check component exports, ensure React Fast Refresh rules |
| Different dev/prod behavior | Conditional module resolution | Check `resolve.conditions`, `ssr.noExternal` |
| CORS in dev | API on different origin | Configure `server.proxy` |
| Module not found after build | Dynamic import path not static | Use `import.meta.glob` instead |

### Build Optimization Tips

```typescript
build: {
  target: 'es2020',                    // Modern targets = smaller output
  minify: 'esbuild',                   // Faster than terser
  cssMinify: 'lightningcss',           // Fastest CSS minification
  reportCompressedSize: false,         // Skip gzip calc in CI
  sourcemap: false,                    // Halves build time
  rollupOptions: {
    output: {
      manualChunks: { vendor: ['react', 'react-dom'] },
    },
    treeshake: { moduleSideEffects: false }, // Aggressive tree-shake
  },
}
```

### Docker Optimization Tips

- Use multi-stage builds (deps → build → serve)
- Cache `node_modules` layer separately
- Pass `VITE_*` vars as build args, not runtime env
- Use `--frozen-lockfile` for reproducibility
- Don't include `node_modules` in final nginx image

### CI/CD Patterns

```yaml
# Cache Vite pre-bundled deps
- uses: actions/cache@v4
  with:
    path: node_modules/.vite
    key: vite-deps-${{ hashFiles('pnpm-lock.yaml') }}

# Parallel build + test
- run: pnpm build & pnpm test --run & wait
```

---

## 8. Real-World Engineering Mindset

### Large React Apps

**Problem**: Bundle size grows linearly, initial load degrades.

| Strategy | Small (<50 routes) | Medium (50–200) | Large (200+) |
|----------|-------------------|-----------------|--------------|
| Route splitting | `React.lazy` | `React.lazy` + prefetch | Lazy + prefetch + skeleton |
| Vendor chunks | Single vendor | Split by domain | Granular per-library |
| Code splitting | Per route | Per feature | Per feature + shared chunks |

**Senior choice**: Route-based splitting with `React.lazy`, vendor chunk per major library, aggressive `sideEffects: false` in `package.json`, avoid barrel files.

### Monorepos

**Problem**: Vite dev server must watch and transform workspace packages.

**Strategy**:
1. Exclude workspace packages from `optimizeDeps` (they're source, not deps)
2. Add them to `server.watch.ignored` exclusion (so changes trigger HMR)
3. Use `vite-tsconfig-paths` for alias resolution via tsconfig
4. Shared base config in a `packages/config` workspace package

**Hidden pitfall**: Workspace packages using CJS will break native ESM dev server. Ensure all workspace packages use ESM.

### Shared Component Libraries

**Build strategy**: Vite library mode with preserved modules (each component is a separate entry).

```typescript
build: {
  lib: {
    entry: {
      index: 'src/index.ts',
      Button: 'src/components/Button.tsx',
      Modal: 'src/components/Modal.tsx',
    },
    formats: ['es'],
  },
  rollupOptions: {
    external: [/^react/, /^react-dom/],
    output: { preserveModules: true },
  },
}
```

**WHY preserved modules**: Consumers can tree-shake at the component level without relying on barrel file analysis.

### SSR Apps

| Approach | Complexity | Performance | Best For |
|----------|-----------|-------------|----------|
| Framework SSR (Next.js, Astro) | Low | High | Most apps |
| Vite SSR primitives + Express | Medium | Medium | Custom SSR needs |
| Vite SSR + streaming | High | Very high | Performance-critical apps |

**Senior choice**: Use a framework (Astro for content sites, Next.js for dynamic apps). Only use Vite SSR primitives if you need custom server logic that frameworks don't support.

### Cloudflare Worker Integration

**Challenge**: Workers run in V8 isolates, not Node.js. Vite's SSR assumes Node.js.

**Strategy**:
- Use Wrangler for Worker builds (not Vite directly)
- Use Vite for the client bundle
- Share types between worker and client via workspace packages
- Use Environment API (Vite 6+) to create a `worker` environment with correct conditions

### Environment Variable Management

| Approach | Security | DX | Best For |
|----------|---------|----|----|
| `.env` files | Low (committed) | High | Defaults, non-secrets |
| `.env.local` | Medium (gitignored) | High | Local secrets |
| CI/CD env vars | High | Medium | Production secrets |
| `define` in config | Medium | Medium | Build-time constants |

**Critical rule**: `VITE_` vars are embedded in client JS — NEVER put secrets there. Use server-side env vars for secrets, expose only via API.

### Microfrontend Architecture

**Problem**: Multiple teams shipping independent frontend apps.

| Strategy | Isolation | Complexity | Vite Support |
|----------|----------|-----------|-------------|
| Module Federation | Runtime | High | `@originjs/vite-plugin-federation` |
| iframe | Full | Low | Native |
| Import maps | ESM-level | Medium | Native browser support |
| Build-time composition | None | Low | Monorepo + code splitting |

**Senior choice for most teams**: Monorepo with code splitting. True microfrontends only when teams genuinely cannot coordinate releases.

---

## 9. Brainstorm / Open Questions

### Build Systems (10)

1. Why does Vite use two different tools (esbuild + Rollup) and what are the tradeoffs?
2. What would change if Vite used a single bundler for both dev and prod?
3. How does pre-bundling affect cold start time as dependency count grows?
4. When should you ship ESM vs CJS from a library built with Vite?
5. What's the cost of `sourcemap: true` in CI pipelines?
6. How do content hashes in filenames interact with CDN caching?
7. What build artifacts should be cached between CI runs?
8. How does `reportCompressedSize: false` affect build time?
9. What happens when two dependencies require different versions of the same package?
10. How would you design a build system for 50 frontend apps in a monorepo?

### Performance (10)

11. Why does initial page load sometimes feel slower with Vite dev than Webpack dev?
12. How does the import waterfall problem manifest in large apps?
13. What's the performance difference between `manualChunks` strategies?
14. How does CSS code splitting interact with render-blocking behavior?
15. When does tree-shaking fail and what patterns prevent it?
16. What's the cost of barrel files on dev server performance?
17. How does `optimizeDeps.include` affect dev server startup?
18. What causes the "optimized dependency changed, reloading" loop?
19. How do you measure and optimize Time to Interactive in a Vite app?
20. What's the performance impact of large `import.meta.glob` patterns?

### HMR (10)

21. Why does HMR become slow in large apps?
22. What causes a full page reload instead of a hot update?
23. How do circular dependencies affect HMR propagation?
24. Why might React Fast Refresh fail silently?
25. How does the HMR boundary concept affect component architecture?
26. What happens when a CSS module import changes?
27. How does HMR work differently for CSS vs JS?
28. What's the relationship between module graph depth and HMR speed?
29. How does `import.meta.hot.invalidate()` differ from a full reload?
30. Why might HMR state preservation fail between updates?

### Plugin Architecture (10)

31. When should a plugin use `enforce: 'pre'` vs `'post'`?
32. How do you prevent plugin transforms from running on node_modules?
33. What's the difference between `resolveId` and `resolve.alias`?
34. How should plugins handle different environments (client vs SSR)?
35. What's the cost of a plugin that runs `transform` on every file?
36. How do virtual modules work and when should you use them?
37. What's the plugin ordering when Vite plugins mix with Rollup plugins?
38. How do you debug why a plugin is slowing down dev server?
39. What state management patterns work for plugins across environments?
40. How does the new `hotUpdate` hook differ from `handleHotUpdate`?

### SSR (10)

41. When should SSR be separated from client builds?
42. What dependencies should be externalized vs bundled for SSR?
43. How does CSS handling differ between client and SSR builds?
44. What's the correct way to handle browser APIs in SSR code?
45. How does streaming SSR interact with code splitting?
46. What's the relationship between Vite SSR and React Server Components?
47. How do you debug SSR hydration mismatches caused by build differences?
48. When should you use `ssr.noExternal` vs `ssr.external`?
49. How does the Environment API change SSR architecture?
50. What's the ModuleRunner and when would you use it directly?

### Monorepos (10)

51. How should workspace packages be handled by Vite's dependency optimizer?
52. What file watching strategy works for monorepo HMR?
53. How do you share Vite configs across monorepo apps?
54. What happens when workspace packages have different module formats?
55. How do you prevent one app's build from breaking another?
56. What's the correct TypeScript config structure for Vite monorepos?
57. How does Turborepo/Nx caching interact with Vite builds?
58. Should workspace packages be pre-built or consumed as source?
59. How do you handle shared CSS/design tokens across workspace packages?
60. What's the correct testing strategy for shared packages vs apps?

### DX (10)

61. How do you keep dev server startup under 1 second?
62. What Vite plugins improve DX the most?
63. How should error overlay be customized for team-specific errors?
64. What's the best debugging setup for Vite + React?
65. How do you create project templates with Vite?
66. What dev server configuration improves team productivity?
67. How should you handle TypeScript strict mode with Vite?
68. What's the cost of running type checking during dev?
69. How do you integrate Vite with browser DevTools effectively?
70. What Vite config patterns reduce "works on my machine" issues?

### CI/CD (10)

71. What Vite artifacts should be cached in CI?
72. How do you run Vite builds in parallel across monorepo apps?
73. What's the optimal Docker build strategy for Vite apps?
74. How do you handle env vars in CI without `.env` files?
75. What build flags optimize CI build speed?
76. How do you validate build output in CI?
77. What's the correct Vite build + deploy strategy for preview environments?
78. How do you handle build failures gracefully in CD pipelines?
79. What monitoring should exist for build performance regression?
80. How do you handle Vite version upgrades across a monorepo in CI?

### Runtime Architecture (5)

81. How does Vite's output interact with browser module caching?
82. What's the preload strategy for code-split chunks?
83. How do Web Workers interact with Vite's module graph?
84. What's the relationship between Vite and Service Worker architecture?
85. How does import map support affect Vite's future architecture?

---

## 10. Practice Questions

### Beginner (25 Questions)

**Q1.** What command creates a new Vite + React + TypeScript project?
- **Type**: Single choice
- a) `npm create vite@latest -- --template react-ts`
- b) `npx create-react-app --template typescript`
- c) `npm init vite react-ts`
- d) `vite create react-ts`
- **Answer**: a
- **Why**: `npm create` is an alias for `npm init`, and `create-vite` is Vite's official scaffolding tool. The `--template` flag selects the project template.

**Q2.** True or False: Vite bundles all your source code before serving it in development.
- **Type**: True/False
- **Answer**: False
- **Why**: Vite serves source files as native ESM. Only `node_modules` dependencies are pre-bundled with esbuild.

**Q3.** Which prefix must environment variables have to be exposed to client-side code?
- **Type**: Fill in the blank
- **Answer**: `VITE_`
- **Why**: Vite only exposes variables prefixed with `VITE_` via `import.meta.env` to prevent accidental secret exposure.

**Q4.** What happens when you put a file in the `public/` directory?
- **Type**: Single choice
- a) It gets processed and hashed by Vite
- b) It is served as-is at the root URL without processing
- c) It is ignored during build
- d) It is inlined into JavaScript
- **Answer**: b
- **Why**: `public/` files are copied verbatim to the build output root. They don't go through the transform pipeline.

**Q5.** How do you access environment variables in Vite client code?
- **Type**: Single choice
- a) `process.env.VITE_API_URL`
- b) `import.meta.env.VITE_API_URL`
- c) `window.env.VITE_API_URL`
- d) `env.VITE_API_URL`
- **Answer**: b
- **Why**: Vite uses `import.meta.env` (ESM standard) instead of Node.js's `process.env`.

**Q6.** What is the default dev server port for Vite?
- **Type**: Single choice
- a) 3000
- b) 8080
- c) 5173
- d) 4200
- **Answer**: c

**Q7.** How do you add a path alias in `vite.config.ts`?
- **Type**: Fill in the blank
- **Answer**: `resolve: { alias: { '@': path.resolve(__dirname, 'src') } }`

**Q8.** What CSS feature does Vite support out of the box without plugins?
- **Type**: Multiple choice
- a) CSS Modules
- b) PostCSS
- c) Sass (with preprocessor installed)
- d) All of the above
- **Answer**: d

**Q9.** What does `vite build` produce by default?
- **Type**: Single choice
- a) A `build/` directory with bundled output
- b) A `dist/` directory with optimized production output
- c) A `.vite/` directory with cached modules
- d) An `out/` directory with SSR output
- **Answer**: b

**Q10.** True or False: `vite preview` starts a development server with HMR.
- **Type**: True/False
- **Answer**: False
- **Why**: `vite preview` serves the production build output statically. It has no HMR or transform pipeline.

**Q11.** How do you import an image and get its URL?
- **Type**: Single choice
- a) `import img from './photo.png'`
- b) `const img = require('./photo.png')`
- c) `import { url } from './photo.png'`
- d) `fetch('./photo.png')`
- **Answer**: a
- **Why**: Default import of an asset returns its resolved URL (hashed in production).

**Q12.** What file is Vite's HTML entry point?
- **Type**: Single choice
- a) `src/index.html`
- b) `public/index.html`
- c) `index.html` (project root)
- d) `dist/index.html`
- **Answer**: c
- **Why**: Vite uses the root `index.html` as the entry point, unlike CRA which uses `public/index.html`.

**Q13.** What does `import.meta.env.MODE` return during `vite build`?
- **Type**: Fill in the blank
- **Answer**: `'production'`

**Q14.** True or False: You can use `require()` in Vite source files.
- **Type**: True/False
- **Answer**: False
- **Why**: Vite uses native ESM. `require()` is CJS and not supported in browser ESM context.

**Q15.** What config property sets the base public path for deployment?
- **Type**: Fill in the blank
- **Answer**: `base` (e.g., `base: '/my-app/'`)

**Q16.** How do you proxy API requests to a backend in dev?
- **Type**: Code completion
- **Answer**: `server: { proxy: { '/api': 'http://localhost:8080' } }`

**Q17.** Which file takes highest priority: `.env` or `.env.local`?
- **Type**: Single choice
- a) `.env`
- b) `.env.local`
- **Answer**: b

**Q18.** True or False: Vite automatically installs Sass when you import `.scss` files.
- **Type**: True/False
- **Answer**: False
- **Why**: You must manually install the `sass` package. Vite detects it but doesn't install it.

**Q19.** What does the `define` config option do?
- **Type**: Single choice
- a) Defines TypeScript types
- b) Replaces global constants at build time
- c) Defines environment variables
- d) Defines plugin hooks
- **Answer**: b

**Q20.** What is the difference between `import img from './img.png'` and `import raw from './file.txt?raw'`?
- **Type**: Matching
- **Answer**: First returns a URL string; second returns the file's text content as a string.

**Q21.** What does `import.meta.env.DEV` return?
- **Type**: Single choice
- a) `true` in development, `false` in production
- b) The environment name
- c) `undefined`
- d) The dev server URL
- **Answer**: a

**Q22.** What plugin is needed for React support?
- **Type**: Single choice
- a) `vite-plugin-react`
- b) `@vitejs/plugin-react`
- c) `@vitejs/react`
- d) `vite-react`
- **Answer**: b

**Q23.** True or False: Changes to `vite.config.ts` trigger HMR.
- **Type**: True/False
- **Answer**: False
- **Why**: Config changes trigger a full server restart, not HMR.

**Q24.** How do you import a Web Worker in Vite?
- **Type**: Fill in the blank
- **Answer**: `import Worker from './worker.ts?worker'`

**Q25.** What directory stores Vite's pre-bundled dependencies?
- **Type**: Single choice
- a) `.vite/`
- b) `node_modules/.cache/vite`
- c) `node_modules/.vite/deps`
- d) `.cache/vite`
- **Answer**: c

---

### Junior (25 Questions)

**Q26.** What tool does Vite use for dependency pre-bundling?
- **Type**: Single choice
- a) Rollup
- b) Webpack
- c) esbuild
- d) SWC
- **Answer**: c
- **Why**: esbuild is 10–100x faster than JS-based bundlers, making pre-bundling near-instant.

**Q27.** True or False: Vite uses Rollup for development mode.
- **Type**: True/False
- **Answer**: False
- **Why**: Dev mode uses native ESM + esbuild for transforms. Rollup is only used for production builds.

**Q28.** What is an HMR boundary?
- **Type**: Single choice
- a) The edge of the browser viewport
- b) A module that calls `import.meta.hot.accept()`
- c) The server-client connection limit
- d) The maximum number of modules that can be updated
- **Answer**: b
- **Why**: HMR boundaries stop update propagation. If a changed module or its importers don't accept updates, a full reload occurs.

**Q29.** Your dependency keeps reloading the entire app during HMR. What should you investigate?
- **Type**: Scenario-based
- **Answer**: Check if the dependency is pre-bundled (`optimizeDeps.include`). If not pre-bundled, each import may create a new module, breaking HMR boundaries. Also check if there's an HMR boundary between the dependency and the app root.
- **Why**: Non-pre-bundled dependencies with many internal modules cause import waterfalls and may not have proper HMR boundaries.

**Q30.** What does `optimizeDeps.include` do?
- **Type**: Single choice
- a) Includes dependencies in the final bundle
- b) Forces Vite to pre-bundle specific dependencies with esbuild
- c) Includes dependencies in TypeScript type checking
- d) Adds dependencies to the import map
- **Answer**: b

**Q31.** How does `import.meta.glob` work?
- **Type**: Single choice
- a) Imports all matching files eagerly at build time
- b) Returns an object mapping file paths to lazy import functions
- c) Searches the file system at runtime
- d) Only works in Node.js
- **Answer**: b
- **Why**: By default it's lazy. Use `{ eager: true }` for synchronous imports.

**Q32.** What causes Vite to trigger a full page reload instead of HMR?
- **Type**: Multiple choice
- a) No HMR boundary found in the importer chain
- b) HTML file changed
- c) `vite.config.ts` changed
- d) All of the above
- **Answer**: d

**Q33.** What is the purpose of `manualChunks` in build config?
- **Type**: Single choice
- a) Split code into specific named chunks
- b) Manually resolve module IDs
- c) Control HMR chunk size
- d) Set chunk size limits
- **Answer**: a

**Q34.** What's the difference between `vite build` and `vite build --mode staging`?
- **Type**: Scenario-based
- **Answer**: `--mode staging` loads `.env.staging` and sets `import.meta.env.MODE` to `'staging'`. Default build uses `production` mode.

**Q35.** True or False: Dynamic imports (`import()`) create separate chunks in production build.
- **Type**: True/False
- **Answer**: True

**Q36.** What does `ssr.noExternal` do?
- **Type**: Single choice
- a) Prevents modules from being loaded in the browser
- b) Forces Vite to bundle the dependency for SSR instead of externalizing it
- c) Excludes modules from production build
- d) Disables external network requests
- **Answer**: b
- **Why**: By default, SSR externalizes `node_modules`. `noExternal` forces bundling, needed for CSS-in-JS libs and ESM-only packages.

**Q37.** How do you conditionally apply a plugin only during build?
- **Type**: Fill in the blank
- **Answer**: `apply: 'build'` in the plugin object.

**Q38.** What is the relationship between `import.meta.hot.dispose()` and `import.meta.hot.data`?
- **Type**: Scenario-based
- **Answer**: `dispose` is called before a module is replaced, receiving a `data` object. You store state on `data`. The next module instance accesses that state via `import.meta.hot.data`.

**Q39.** Why might dependency pre-bundling fail?
- **Type**: Scenario-based
- **Answer**: Common causes: CJS dependency with dynamic `require()`, dependency with native addons, circular CJS dependencies, package with incorrect `exports` field, or dependency that uses Node.js built-ins.

**Q40.** What does `build.target: 'es2020'` control?
- **Type**: Single choice
- a) TypeScript compilation target
- b) Minimum browser support for output syntax
- c) Node.js version requirement
- d) ESLint parser target
- **Answer**: b

**Q41.** How do you force Vite to re-run dependency optimization?
- **Type**: Single choice
- a) Delete `node_modules` and reinstall
- b) Delete `node_modules/.vite` or run `vite --force`
- c) Restart the dev server
- d) Clear browser cache
- **Answer**: b

**Q42.** What is the `enforce` property on a plugin?
- **Type**: Single choice
- a) Forces the plugin to run
- b) Controls plugin execution order (`'pre'` or `'post'`)
- c) Enforces TypeScript types
- d) Makes the plugin required
- **Answer**: b

**Q43.** True or False: CSS changes trigger a full page reload in Vite dev.
- **Type**: True/False
- **Answer**: False
- **Why**: CSS changes are hot-updated by injecting/replacing `<style>` tags without page reload.

**Q44.** What does `import.meta.hot.invalidate()` do?
- **Type**: Single choice
- a) Removes the module from disk
- b) Forces update propagation to importers when the module can't self-handle the update
- c) Clears browser cache
- d) Rebuilds the entire application
- **Answer**: b

**Q45.** How do you create a CSS Module in Vite?
- **Type**: Fill in the blank
- **Answer**: Name the file with `.module.css` extension (e.g., `Button.module.css`).

**Q46.** What's the difference between `server.proxy` rewrite and `changeOrigin`?
- **Type**: Scenario-based
- **Answer**: `rewrite` modifies the URL path before forwarding. `changeOrigin` changes the `Host` header to match the target, needed when the backend validates the Host header.

**Q47.** What plugin hook runs when a file changes during dev?
- **Type**: Single choice
- a) `transform`
- b) `hotUpdate` (or legacy `handleHotUpdate`)
- c) `resolveId`
- d) `buildStart`
- **Answer**: b

**Q48.** True or False: `import.meta.glob` patterns are resolved at build time.
- **Type**: True/False
- **Answer**: True
- **Why**: The glob pattern is statically analyzed and transformed into explicit import statements at build time.

**Q49.** What does `build.sourcemap: 'hidden'` do?
- **Type**: Single choice
- a) Generates source maps but doesn't add the `//# sourceMappingURL` comment
- b) Encrypts source maps
- c) Only generates source maps for vendor code
- d) Disables source maps in development
- **Answer**: a
- **Why**: Useful for error tracking (upload to Sentry) without exposing source maps to end users.

**Q50.** How does `sideEffects: false` in `package.json` help Vite builds?
- **Type**: Scenario-based
- **Answer**: It tells Rollup that unused exports can be safely tree-shaken without worrying about side effects. This dramatically improves tree-shaking for libraries with barrel files.

---

### Senior (25 Questions)

**Q51.** You notice HMR is slow in your monorepo. `vite --debug hmr` shows deep importer chains. What architectural change would help?
- **Type**: Scenario-based
- **Answer**: Flatten the module graph by reducing barrel file re-exports. Instead of importing from `@myorg/ui` (which re-exports everything), import directly from `@myorg/ui/Button`. This reduces the importer chain depth that HMR must traverse.

**Q52.** Your production build creates 200+ small chunks. What's the problem and how do you fix it?
- **Type**: Scenario-based
- **Answer**: Too many dynamic imports or overly granular `manualChunks`. Each chunk creates an HTTP request. Fix: consolidate related routes into larger chunks, use `output.experimentalMinChunkSize`, or adjust `manualChunks` to group related modules.

**Q53.** A Vite plugin's `transform` hook is called for every file including `node_modules`. How do you fix it?
- **Type**: Scenario-based
- **Answer**: Use the `filter` option on the hook or add an early return: `if (id.includes('node_modules')) return`. Better: use `filter: { id: /\.tsx?$/ }` to let Vite skip non-matching files entirely (no JS overhead).

**Q54.** What's the correct way to share Vite configuration across a monorepo?
- **Type**: Scenario-based
- **Answer**: Create a `packages/config` workspace package that exports a factory function (`createViteConfig(overrides)`). Each app imports and extends it. Don't share the config object directly — use a function to avoid mutation issues.

**Q55.** Your CI build takes 5 minutes for a Vite app. What optimizations would you apply?
- **Type**: Scenario-based
- **Answer**: (1) `reportCompressedSize: false` — skip gzip calculation. (2) `sourcemap: false` or `'hidden'` — halves output. (3) Cache `node_modules/.vite`. (4) Use `esbuild` minifier instead of `terser`. (5) Increase `NODE_OPTIONS='--max-old-space-size=8192'`. (6) Consider `build.target: 'esnext'` for internal apps.

**Q56.** How do you debug why a specific module is included in the production bundle?
- **Type**: Scenario-based
- **Answer**: Use `rollup-plugin-visualizer` to generate a treemap. Check if the module is imported statically somewhere unexpected (barrel files are common culprits). Use `npx vite build --debug` for build-time logs.

**Q57.** What's the difference between `resolve.conditions` in Vite vs Node.js package exports?
- **Type**: Scenario-based
- **Answer**: `resolve.conditions` controls which export conditions Vite uses when resolving package `exports` field. In dev, Vite uses `['development', 'module', 'browser']`. In build, it uses `['production', 'module', 'browser']`. SSR uses `['node', 'module']`. Mismatches between dev and build conditions cause the "works in dev, breaks in build" bug.

**Q58.** How should you handle CSS ordering issues in a code-split Vite app?
- **Type**: Scenario-based
- **Answer**: CSS chunk ordering is non-deterministic when multiple async chunks share CSS. Solutions: (1) Use CSS-in-JS for critical ordering. (2) Use CSS layers (`@layer`). (3) Ensure CSS specificity doesn't depend on load order. (4) Use `cssCodeSplit: false` for small apps (single CSS file).

**Q59.** Write a plugin that adds build metadata to every HTML file.
- **Type**: Code
- **Answer**:
  ```typescript
  function buildMetaPlugin(): Plugin {
    return {
      name: 'build-meta',
      transformIndexHtml(html) {
        return {
          html,
          tags: [{
            tag: 'meta',
            attrs: { name: 'build-version', content: process.env.npm_package_version || 'dev' },
            injectTo: 'head',
          }],
        }
      },
    }
  }
  ```

**Q60.** What's the correct Docker layer caching strategy for a Vite monorepo?
- **Type**: Scenario-based
- **Answer**: Layer 1: Copy only `package.json`, `pnpm-lock.yaml`, `pnpm-workspace.yaml`. Layer 2: `pnpm install --frozen-lockfile`. Layer 3: Copy source. Layer 4: Build. This way, source changes don't invalidate the dependency install layer.

**Q61.** How do you configure Vite library mode to output both ESM and CJS with correct `package.json` exports?
- **Type**: Code
- **Answer**:
  ```json
  {
    "type": "module",
    "exports": {
      ".": {
        "import": "./dist/index.mjs",
        "require": "./dist/index.cjs"
      }
    },
    "main": "./dist/index.cjs",
    "module": "./dist/index.mjs",
    "types": "./dist/index.d.ts"
  }
  ```

**Q62.** Your app has a dev/prod behavior difference: a library works in dev but throws in production. What do you investigate?
- **Type**: Scenario-based
- **Answer**: Check `resolve.conditions` differences. In dev, Vite may resolve to the library's `development` export. In build, Rollup resolves to `production` export. Also check if the library has `browser` vs `node` exports that resolve differently. Use `vite build --debug` to compare resolved paths.

**Q63.** How do you implement a Vite plugin that provides type-safe virtual modules?
- **Type**: Scenario-based
- **Answer**: Create the plugin with `resolveId`/`load` hooks, then create a `.d.ts` declaration file:
  ```typescript
  // virtual-module.d.ts
  declare module 'virtual:app-config' {
    export const config: { version: string; buildTime: string }
  }
  ```

**Q64.** What's the optimal chunk strategy for a dashboard app with 50 routes?
- **Type**: Scenario-based
- **Answer**: Route-based code splitting via `React.lazy`. Group vendor chunks by domain (e.g., `chart-vendor`, `form-vendor`). Use `manualChunks` for shared utilities. Implement route prefetching for likely next routes. Target: initial bundle < 200KB gzipped.

**Q65.** How does Vite handle circular dependencies differently in dev vs build?
- **Type**: Scenario-based
- **Answer**: In dev (native ESM), circular imports work due to live bindings — the module is partially initialized when the circular reference is hit. In build (Rollup), circular dependencies are handled via scope hoisting, but may produce warnings and can cause runtime errors if the circular access happens before initialization.

**Q66.** What plugin hook would you use to generate a service worker with the list of all built assets?
- **Type**: Single choice
- a) `transform`
- b) `generateBundle`
- c) `resolveId`
- d) `buildStart`
- **Answer**: b
- **Why**: `generateBundle` has access to all output files in the bundle, so you can enumerate them for the SW precache manifest.

**Q67.** How do you profile Vite plugin performance?
- **Type**: Scenario-based
- **Answer**: Use `DEBUG=vite:plugin-resolve,vite:transform vite`. Use `vite-plugin-inspect` to visualize transform chains. Wrap individual hooks with `performance.now()` measurements. Check which plugins run `transform` on the most files.

**Q68.** True or False: `build.rollupOptions.external` and `ssr.external` serve the same purpose.
- **Type**: True/False
- **Answer**: False
- **Why**: `build.rollupOptions.external` excludes modules from the client bundle (they must be available at runtime). `ssr.external` tells Vite to use Node.js's native resolution for SSR instead of bundling — the module is still available, just not processed by Rollup.

**Q69.** What's the correct testing strategy when using Vitest with Vite path aliases?
- **Type**: Scenario-based
- **Answer**: Vitest automatically reads `vite.config.ts` and inherits aliases. Alternatively, use `vite-tsconfig-paths` plugin which works in both Vite and Vitest. No manual alias duplication needed.

**Q70.** How do you implement A/B testing that doesn't increase bundle size for all users?
- **Type**: Scenario-based
- **Answer**: Use dynamic imports for experiment variants: `const Variant = React.lazy(() => import(\`./experiments/\${experimentId}\`))`. Each variant is a separate chunk loaded only for enrolled users. Use `import.meta.glob` for type-safe variant discovery.

**Q71.** Write a plugin that logs build timing per hook.
- **Type**: Code
- **Answer**:
  ```typescript
  function timingPlugin(): Plugin {
    const times: Record<string, number> = {}
    return {
      name: 'timing',
      buildStart() { times.buildStart = performance.now() },
      transform(code, id) {
        // Track per-file times if needed
      },
      generateBundle() {
        times.generateBundle = performance.now()
      },
      closeBundle() {
        console.log('Total build time:', performance.now() - times.buildStart, 'ms')
      },
    }
  }
  ```

**Q72.** How do you set up Vite for a multi-page app (MPA)?
- **Type**: Code
- **Answer**:
  ```typescript
  build: {
    rollupOptions: {
      input: {
        main: resolve(__dirname, 'index.html'),
        about: resolve(__dirname, 'about/index.html'),
        dashboard: resolve(__dirname, 'dashboard/index.html'),
      },
    },
  }
  ```

**Q73.** What's the difference between `vite-plugin-inspect` and `DEBUG=vite:*`?
- **Type**: Scenario-based
- **Answer**: `vite-plugin-inspect` provides a visual web UI showing transform chains for each module — what each plugin did to the code. `DEBUG=vite:*` logs internal Vite operations (resolution, transforms, HMR) to the terminal. Use `inspect` for plugin debugging, `DEBUG` for server/HMR debugging.

**Q74.** How do you handle environment variables in a Docker build for a Vite app?
- **Type**: Scenario-based
- **Answer**: Pass `VITE_*` vars as Docker build args: `docker build --build-arg VITE_API_URL=https://api.prod.com .` In Dockerfile: `ARG VITE_API_URL` + `ENV VITE_API_URL=$VITE_API_URL` before `RUN pnpm build`. Never use runtime env vars for Vite client builds — they're embedded at build time.

**Q75.** Your Vite build succeeds but the deployed app shows a blank page. What do you check?
- **Type**: Scenario-based
- **Answer**: (1) Check `base` config matches deployment path. (2) Check browser console for 404s on chunks. (3) Verify `index.html` has correct script/link paths. (4) Check for absolute vs relative paths in assets. (5) Check for runtime errors in entry module. (6) Verify SPA routing server config (nginx `try_files`).

---

### Expert / Tooling Engineer (25 Questions)

**Q76.** Explain the difference between Vite's module graph and Rollup's module graph.
- **Type**: Scenario-based
- **Answer**: Vite's module graph is **incremental** — built on demand as requests arrive, with nodes tracking HMR state (`isSelfAccepting`, `acceptedHmrDeps`, `lastHMRTimestamp`). Rollup's graph is **complete** — built by traversing all reachable modules from entry points before any output. Vite's graph is mutable and long-lived (survives HMR), Rollup's is rebuilt each build.

**Q77.** Why does Vite pre-bundle dependencies into single files?
- **Type**: Scenario-based
- **Answer**: Two reasons: (1) **CJS→ESM conversion** — browser can't handle `require()`. (2) **Request waterfall** — lodash-es has 600+ files. Without pre-bundling, importing lodash triggers 600 HTTP requests in dev. Pre-bundling collapses them into one file with one request.

**Q78.** How does Vite's dev server determine when to send a full-reload vs HMR update?
- **Type**: Scenario-based
- **Answer**: After a file change, Vite walks the importer chain from the changed module upward. If it reaches a module with `isSelfAccepting: true` or one that's in another module's `acceptedHmrDeps`, that's the boundary — send a targeted update. If the walk reaches the root without finding any boundary, or encounters a circular dependency loop, send `full-reload`.

**Q79.** What architectural problem does native ESM development solve that bundled development doesn't?
- **Type**: Scenario-based
- **Answer**: **Startup time scaling**. In bundled dev, startup time = O(n) where n is total modules. In native ESM dev, startup time = O(1) for server + O(route) for the current page's modules. Adding 1000 modules to the project doesn't affect cold start if those modules aren't on the current page.

**Q80.** True or False: Vite's plugin container in dev mode runs all Rollup hooks in the same order as Rollup.
- **Type**: True/False
- **Answer**: False
- **Why**: Vite's plugin container processes files on demand (when requested), not by traversing the graph upfront. Some hooks like `buildStart`/`buildEnd` run at server start/stop, not per-request. Also, Vite adds its own hooks (`config`, `configureServer`, `hotUpdate`) that Rollup doesn't have.

**Q81.** How does browser module caching interact with Vite's dev server?
- **Type**: Scenario-based
- **Answer**: Pre-bundled deps get `Cache-Control: max-age=31536000,immutable` (strong caching via content hash in URL). Source files get `304 Not Modified` with ETag validation. On HMR update, Vite appends `?t=timestamp` to bust the ETag cache. This means unchanged modules are served from browser cache (no network), changed modules are fetched fresh.

**Q82.** Design a plugin that implements incremental CSS extraction with source maps.
- **Type**: Scenario-based
- **Answer**: Use `transform` to intercept `.css` imports, extract CSS content into a side channel (Map), emit CSS via `generateBundle`. Track which JS modules reference which CSS. On rebuild, only re-extract CSS for changed modules. Compose source maps from the transform chain. This is essentially what Vite's internal CSS plugin does.

**Q83.** What are the implications of Rolldown replacing Rollup in Vite?
- **Type**: Scenario-based
- **Answer**: (1) **Unified pipeline** — same engine for dev pre-bundling and prod build, eliminating dev/prod divergence. (2) **Speed** — Rust-based, 10–100x faster builds. (3) **Plugin compat** — Rolldown aims for Rollup API compatibility, but edge cases will break. (4) **Chunk strategy** — Rolldown's chunking may differ from Rollup's, changing output structure. (5) **Memory** — Rust's memory model means larger projects won't OOM.

**Q84.** How does `transformRequest` work internally in Vite?
- **Type**: Scenario-based
- **Answer**: `transformRequest(url)` → resolve the URL to a module ID (`resolveId` hooks) → check module graph cache (return if fresh) → `load` the module content → run `transform` hooks sequentially → update module graph node with new `transformResult` → return `{ code, map, etag }`. In dev, this happens per-request. In build, Rollup drives this for all modules.

**Q85.** Why does HMR become slow in a large app with deep component trees?
- **Type**: Scenario-based
- **Answer**: HMR speed depends on: (1) **Invalidation walk depth** — must traverse importers until finding a boundary. Deep trees = more traversal. (2) **Module re-transform time** — changed module must be re-transformed. (3) **Client-side execution** — the `accept` callback must re-render the component subtree. (4) **Barrel files** — re-exporting everything means one change invalidates the barrel, which invalidates all importers.

**Q86.** What is the `\0` prefix convention in virtual module IDs?
- **Type**: Scenario-based
- **Answer**: The `\0` prefix (null character) is a Rollup convention meaning "this ID is virtual, don't try to read it from disk." Other plugins see the `\0` prefix and know to skip `resolveId`/`load` for this ID. Vite and Rollup both respect this convention.

**Q87.** How would you implement a Vite plugin that provides compile-time macros (like Babel macros)?
- **Type**: Scenario-based
- **Answer**: Use the `transform` hook. Parse imports matching a macro pattern (e.g., `import { sql } from 'sql.macro'`). Parse the AST (using `@babel/parser` or `acorn`), find call expressions using macro imports, evaluate them at compile time, replace the call with the result. Return transformed code with source map.

**Q88.** Explain the Environment API architecture in Vite 6+.
- **Type**: Scenario-based
- **Answer**: Each environment (client, ssr, custom) is a `DevEnvironment` instance with its own: module graph (`EnvironmentModuleGraph`), plugin pipeline, resolve conditions, hot channel. Plugins access the current environment via `this.environment`. This replaces the single `server.moduleGraph` + `server.pluginContainer` model. WHY: SSR and client need different resolution (e.g., `node` vs `browser` conditions), different module graphs, different HMR channels.

**Q89.** What causes the "optimized dependency changed" infinite loop?
- **Type**: Scenario-based
- **Answer**: Vite discovers a new dependency during dev (not in the initial scan), re-runs optimization, which changes the pre-bundled output, which triggers a page reload, which may discover the dependency again due to dynamic imports or conditional requires. Fix: add the dependency to `optimizeDeps.include` explicitly.

**Q90.** How does Vite's file watcher (chokidar) handle performance in large monorepos?
- **Type**: Scenario-based
- **Answer**: Chokidar uses OS-native file watchers (`inotify` on Linux, `FSEvents` on macOS). Performance issues arise from: (1) watching too many files (`node_modules`), (2) too many directories (monorepo with many packages), (3) `usePolling: true` on network filesystems. Mitigation: `server.watch.ignored` to exclude directories, use `awaitWriteFinish` for network drives.

**Q91.** Design a build performance monitoring system for a Vite monorepo.
- **Type**: Scenario-based
- **Answer**: (1) Plugin that hooks `buildStart`/`closeBundle` with `performance.now()`. (2) Track per-plugin `transform` time using wrapped hooks. (3) Track chunk count and sizes from `generateBundle`. (4) Emit metrics to monitoring system (DataDog, Grafana). (5) Set CI thresholds: fail if build time > X, if bundle size > Y. (6) Track trends over time to catch regressions.

**Q92.** What's the difference between `ModuleRunner` and `ssrLoadModule`?
- **Type**: Scenario-based
- **Answer**: `ssrLoadModule` is the legacy Vite 5 API — runs in the same Node.js process, shares the server's module graph. `ModuleRunner` (Vite 6+) is runtime-agnostic — communicates with the Vite server via `transport` (WebSocket, HTTP, etc.), can run in any V8 runtime (Node, Workers, Deno). `ModuleRunner` supports the Environment API with per-environment isolation.

**Q93.** How would you architect Vite for a 100-app monorepo?
- **Type**: Scenario-based
- **Answer**: (1) Shared config package with factory function. (2) Turborepo/Nx for build orchestration with remote caching. (3) Persistent dep optimization cache (share `node_modules/.vite` via remote cache). (4) Incremental builds — only build apps with changed dependencies. (5) Parallel builds in CI with dependency-aware scheduling. (6) Library packages pre-built (not consumed as source) to reduce module graph size per app.

**Q94.** What are the trade-offs of serving source as ESM vs bundling for dev?
- **Type**: Scenario-based
- **Answer**: 
  - **ESM (Vite)**: O(1) startup, per-file transform, import waterfall for deep graphs, browser does module resolution
  - **Bundled (Webpack/Turbopack)**: O(n) startup, single file serve, no waterfall, server does resolution
  - ESM wins for: smaller pages, faster iteration, simpler architecture
  - Bundled wins for: huge pages with 1000+ imports (waterfall kills load time), complex module resolution needs

**Q95.** True or False: Vite's transform pipeline composes source maps automatically.
- **Type**: True/False
- **Answer**: True
- **Why**: Each `transform` hook can return a source map. Vite composes them using `@ampproject/remapping` so the final source map maps back to the original source through all transform steps.

**Q96.** How does scope hoisting in Rollup differ from Webpack's module wrapping?
- **Type**: Scenario-based
- **Answer**: Rollup places all modules in a single scope (flat), renaming variables to avoid conflicts. This eliminates module wrapper functions and enables better minification and tree-shaking. Webpack wraps each module in a function (`__webpack_require__`), adding overhead per module. Scope hoisting produces smaller, faster output.

**Q97.** What's the `import.meta.hot` protocol between client and server?
- **Type**: Scenario-based
- **Answer**: WebSocket connection at `/__vite_hmr`. Server sends typed messages: `connected`, `update` (with list of modules to update), `full-reload`, `prune` (removed modules), `error` (overlay), `custom` (plugin events). Client receives updates, fetches new modules via `import()` with `?t=timestamp`, executes `accept`/`dispose`/`prune` callbacks.

**Q98.** How would you implement a Vite plugin that provides React Server Components support?
- **Type**: Scenario-based
- **Answer**: (1) Create a new environment (`rsc`) with `react-server` resolve condition. (2) Use `resolveId` to split client/server module boundaries. (3) Transform `"use client"` directives into client reference objects on the server. (4) Generate client manifest mapping component IDs to chunk URLs. (5) Use `ModuleRunner` to execute RSC in a separate environment from the SSR renderer.

**Q99.** What's the fundamental architectural difference between Vite and Turbopack?
- **Type**: Scenario-based
- **Answer**: Vite uses **native ESM** — browser loads modules individually, transforms are on-demand, module graph is lazily built. Turbopack uses **incremental computation** — Rust-based bundler that incrementally recomputes only changed portions of the bundle graph, serving bundled output. Turbopack trades simplicity (Vite's approach) for raw throughput (no import waterfalls, single bundled response).

**Q100.** Design the ideal frontend build architecture for 2026 and beyond.
- **Type**: Scenario-based
- **Answer**: (1) **Dev**: Rolldown-based dev server with native ESM + incremental bundling hybrid — ESM for source, bundled for deps. (2) **Build**: Rolldown with parallel Rust transforms (oxc), persistent cross-build caching. (3) **Plugin**: Universal plugin API (Rollup-compat) running in both Rust and JS. (4) **Environments**: Unified pipeline for client, SSR, RSC, Workers, edge — each with own module graph and conditions. (5) **Monorepo**: Built-in remote caching, dependency-aware parallel builds. (6) **Output**: Optimized per-target (browser modules, Service Worker, Workers). This is essentially Vite's roadmap.

---

## 11. Personalized Recommendations

### Which Concepts Matter Most for Your Stack

Given React + Next.js + Astro + TypeScript + monorepos:

1. **Plugin architecture** — you'll need to write/modify plugins for monorepo setups
2. **Library mode** — building shared component libraries across apps
3. **Monorepo integration** — `optimizeDeps`, watch config, shared base configs
4. **Build optimization** — chunk strategies, tree-shaking, CI speed
5. **SSR mental model** — understand how Vite SSR works even if you use Next.js/Astro (they use Vite internally)
6. **Environment API** — critical for understanding Astro's multi-target builds

### Advanced Topics to Prioritize

1. Module graph internals (debug HMR issues in monorepos)
2. Rollup chunk strategy (optimize production bundles)
3. Plugin development (build internal tooling)
4. Dependency optimization internals (fix pre-bundling issues)
5. Dev/prod parity (prevent deployment bugs)

### Common Mistakes Frontend Engineers Make with Vite

1. Using barrel files everywhere (kills tree-shaking and HMR)
2. Not configuring `optimizeDeps` for monorepo packages
3. Using `process.env` instead of `import.meta.env`
4. Not understanding that `VITE_` vars are embedded in the client bundle
5. Ignoring chunk size warnings
6. Not testing production builds locally before deploying
7. Over-splitting with too many dynamic imports
8. Not configuring `base` for non-root deployments
9. Using `terser` when `esbuild` minification is sufficient
10. Not caching Vite artifacts in CI

### From Application Developer to Tooling/Platform Engineer

1. **Week 1–2**: Read Vite source code — start with `packages/vite/src/node/server/index.ts`
2. **Week 3–4**: Write 3 plugins (virtual module, transform, HMR)
3. **Week 5–6**: Build a shared Vite config package for your monorepo
4. **Week 7–8**: Profile and optimize build performance across your apps
5. **Week 9–10**: Implement custom dev server middleware for team DX
6. **Week 11–12**: Study Rollup/Rolldown internals and chunk algorithms
7. **Week 13–16**: Build an internal Vite plugin that solves a team-wide problem
8. **Week 17–20**: Contribute to Vite open source (bug fix or feature)

### 60-Day Learning Plan

| Week | Focus | Milestone |
|------|-------|-----------|
| 1 | Vite fundamentals, config, dev server | Can configure any Vite project from scratch |
| 2 | Build optimization, code splitting, assets | Optimized production build for existing app |
| 3 | Plugin architecture, write first plugin | Working virtual module plugin |
| 4 | HMR internals, module graph | Can debug any HMR issue |
| 5 | Monorepo integration, shared configs | Monorepo running with shared Vite config |
| 6 | SSR architecture, Environment API | SSR prototype with custom server |
| 7 | Library mode, component library build | Published component library with Vite |
| 8 | CI/CD optimization, Docker integration | CI pipeline under 3 minutes |
| 9 | Read Vite source code (server, plugins) | Understand dev server internals |

---

## 12. Official Documentation & Reference Links

### Core Documentation

- [Vite Official Documentation](https://vite.dev)
- [Vite GitHub Repository](https://github.com/vitejs/vite)
- [Vite Plugin API](https://vite.dev/guide/api-plugin.html)
- [Vite HMR API](https://vite.dev/guide/api-hmr.html)
- [Vite JavaScript API](https://vite.dev/guide/api-javascript.html)
- [Vite Environment API](https://vite.dev/guide/api-environment.html)
- [Vite SSR Guide](https://vite.dev/guide/ssr.html)
- [Vite Config Reference](https://vite.dev/config/)

### Bundler References

- [Rollup Documentation](https://rollupjs.org)
- [esbuild Documentation](https://esbuild.github.io)
- [Rolldown](https://rolldown.rs)
- [SWC](https://swc.rs)

### Testing & Tooling

- [Vitest](https://vitest.dev)
- [Storybook + Vite](https://storybook.js.org/docs/builders/vite)
- [vite-plugin-inspect](https://github.com/antfu/vite-plugin-inspect)

### Framework Integration

- [Astro (uses Vite)](https://astro.build)
- [Remix (Vite)](https://remix.run/docs/en/main/guides/vite)
- [@vitejs/plugin-react](https://github.com/vitejs/vite-plugin-react)

### Deployment & Edge

- [Cloudflare Workers](https://developers.cloudflare.com/workers/)
- [Vite Plugin SSR / vike](https://vike.dev)

### Vite Source Code (Key Files)

- [packages/vite/src/node/server](https://github.com/vitejs/vite/tree/main/packages/vite/src/node/server) — Dev server
- [packages/vite/src/node/plugins](https://github.com/vitejs/vite/tree/main/packages/vite/src/node/plugins) — Built-in plugins
- [packages/vite/src/node/optimizer](https://github.com/vitejs/vite/tree/main/packages/vite/src/node/optimizer) — Dependency pre-bundling
- [packages/vite/src/client](https://github.com/vitejs/vite/tree/main/packages/vite/src/client) — HMR client

### Talks & Articles

- [Evan You — Vite: Rethinking Frontend Tooling (ViteConf)](https://www.youtube.com/results?search_query=evan+you+vite+viteconf)
- [Vite Blog](https://vite.dev/blog/)
- [ViteConf Recordings](https://viteconf.org)

---

## 13. Advanced Engineering Topics

### Native ESM Architecture

The browser's `import` statement triggers an HTTP request per module. This creates a **request waterfall**:

```
index.js imports → App.js imports → Header.js imports → Logo.js
                                  → Nav.js imports → NavItem.js
                → Router.js imports → Route.js
```

Each import is a sequential HTTP request in the worst case (browser parallelizes siblings, but depth is sequential). For `node_modules`, Vite pre-bundles to collapse deep dependency trees into single files. For source code, the waterfall is acceptable because:
1. Files are local (< 1ms per request)
2. Browser caches unchanged modules
3. Only the current page's modules are loaded

### Module Graph Algorithms

**Construction**: Lazy — modules added when first requested. On transform, new imports are discovered and added as edges.

**HMR propagation**: BFS/DFS upward through importers until boundary found. The algorithm must handle:
- Self-accepting modules (boundary = changed module itself)
- Accepted dependencies (boundary = the importer that accepts the dep)
- Circular references (prevent infinite walk)
- Multiple boundaries (update all of them)
- No boundary (full reload)

**Invalidation**: Clearing `transformResult` on a module. Cascading invalidation walks importers and clears their results too (since they may inline or reference the changed module's exports).

### HMR Invalidation Deep Dive

```typescript
// Simplified invalidation algorithm
function invalidateModule(mod: EnvironmentModuleNode, seen: Set, timestamp: number) {
  if (seen.has(mod)) return // prevent cycles
  seen.add(mod)

  mod.transformResult = null
  mod.lastInvalidationTimestamp = timestamp

  // Cascade to importers that don't have HMR boundaries
  for (const importer of mod.importers) {
    if (!importer.acceptedHmrDeps.has(mod)) {
      invalidateModule(importer, seen, timestamp)
    }
  }
}
```

### Build Graph Optimization

Rollup's chunk generation:

1. **Entry chunks**: One per entry point
2. **Dynamic chunks**: One per dynamic `import()`
3. **Common chunks**: Modules imported by multiple chunks are extracted
4. **Manual chunks**: Override via `manualChunks` config

Optimization goals conflict:
- Fewer chunks → fewer HTTP requests → faster initial load
- More chunks → better caching → faster subsequent loads
- Balanced chunks → predictable loading → easier debugging

### Incremental Rebuild Strategies

Current Vite: Full Rollup rebuild for production. No incremental production builds.

Future (Rolldown): Persistent module graph, only re-transform changed modules, incrementally update chunk assignments. This would reduce rebuild time from O(n) to O(changed).

### Rust-Based Bundlers Architecture

| Tool | Language | Role | Architecture |
|------|----------|------|-------------|
| esbuild | Go | Transform + bundle | Single-pass, no AST plugins |
| SWC | Rust | Transform | AST-level plugins via WASM |
| Rolldown | Rust | Bundle | Rollup-compatible, parallel transforms |
| oxc | Rust | Parse + transform | Fastest parser, linter, transformer |
| Turbopack | Rust | Bundle + dev server | Incremental computation engine |

The trend: **Rust for compute-intensive work (parse, transform, bundle), JavaScript for configuration and plugin authoring**.

### Toolchain Interoperability

```
                ┌─────────────────────┐
                │    Vite (orchestrator) │
                └──────┬──────────────┘
                       │
          ┌────────────┼────────────┐
          │            │            │
    ┌─────▼─────┐ ┌───▼────┐ ┌────▼────┐
    │  esbuild   │ │ Rollup  │ │  oxc    │
    │ (pre-bundle)│ │ (build) │ │(future) │
    └────────────┘ └────────┘ └─────────┘
          │            │            │
          └────────────┼────────────┘
                       │
              ┌────────▼────────┐
              │    Rolldown      │
              │ (unified future) │
              └─────────────────┘
```

---

## Summary

**Key takeaways**:

1. Vite is a **build tool orchestrator**, not a bundler — it coordinates esbuild, Rollup, and plugins
2. The **native ESM dev server** is Vite's core innovation — transforms on demand, no bundling
3. **Pre-bundling** solves the dependency waterfall problem
4. **Plugin architecture** is Rollup-compatible, making the ecosystem portable
5. **HMR** works by walking the module graph upward to find boundaries
6. **Production builds** use Rollup for optimal output (tree-shaking, scope hoisting)
7. **Environment API** (Vite 6+) enables per-target module graphs and plugins

**Next steps**:

1. Write your first Vite plugin (virtual module)
2. Set up a monorepo with shared Vite config
3. Profile your existing app's build performance
4. Read Vite's dev server source code
5. Experiment with library mode for shared packages

**Advanced topics to continue**:

- Rolldown architecture and migration path
- React Server Components with Vite
- Edge runtime module execution
- Build performance engineering at scale
- Contributing to Vite open source
