# Monorepo Architecture — Complete Engineering Guide

A comprehensive learning path and practical engineering guide for Monorepo architecture, from fundamentals to organization-scale systems.

---

# 1. Big Picture

## What Is a Monorepo?

A monorepo is a **single repository** containing multiple distinct projects — applications, libraries, shared packages, tooling — with well-defined relationships between them. It is NOT "all code in one folder." It is a **structured, dependency-aware, build-optimized** repository architecture.

**Why monorepos exist:**

1. **Atomic changes** — A single commit can update a shared library AND every consumer simultaneously. No version dance across repos.
2. **Single source of truth** — Shared code lives once. No drift between copies.
3. **Unified tooling** — One CI pipeline, one linting setup, one test runner configuration.
4. **Dependency graph visibility** — The build system knows what depends on what, enabling incremental builds and affected-only CI.
5. **Cross-team collaboration** — Engineers can see, search, and contribute to any part of the codebase.

**Problems monorepos solve:**

| Problem | Polyrepo Reality | Monorepo Solution |
|---------|-----------------|-------------------|
| Shared code drift | Copy-paste or publish/consume cycle | Single source, direct imports |
| Breaking change detection | Discover at npm install time | Discover at build/test time immediately |
| Cross-repo refactoring | PRs across N repos, coordinated merges | One PR, one review, one merge |
| Tooling inconsistency | Each repo configures its own ESLint, TS, etc. | Shared configs inherited by all packages |
| CI/CD fragmentation | N pipelines to maintain | One pipeline with intelligent filtering |
| Dependency version conflicts | Different repos on different React versions | Single version policy (or explicit overrides) |

## Key Terminology

```
monorepo
├── apps/                    ← Applications (deployable units)
│   ├── web/                 ← Next.js app
│   ├── docs/                ← Astro docs site
│   └── api/                 ← Backend service
├── packages/                ← Libraries (shared code)
│   ├── ui/                  ← Shared React component library
│   ├── utils/               ← Shared utility functions
│   ├── config-ts/           ← Shared TypeScript config
│   ├── config-eslint/       ← Shared ESLint config
│   └── types/               ← Shared TypeScript types
├── package.json             ← Root workspace config
├── pnpm-workspace.yaml      ← Workspace definition
└── turbo.json               ← Build orchestration config
```

| Term | Definition |
|------|-----------|
| **Monorepo** | Single repository with multiple projects, managed by a build system that understands their relationships |
| **Polyrepo** | Each project in its own repository. Standard model. |
| **Workspace** | Package manager feature that links local packages together (pnpm/yarn/npm workspaces) |
| **Package** | Any folder with a `package.json`. Can be an app or library. |
| **Application** | A deployable unit (web app, API server, worker) |
| **Library** | A non-deployable package consumed by other packages |
| **Shared package** | A library consumed by multiple apps/packages |
| **Internal package** | A package that is NOT published to npm — consumed only within the monorepo |

## Core Concepts

### Dependency Graph

The dependency graph is a **directed acyclic graph (DAG)** of package relationships. Every `import` or dependency declaration creates an edge.

```
web ──→ ui ──→ utils
 │              ↑
 └──→ types ───┘
docs ──→ ui
api ──→ utils ──→ types
```

**Why it matters:** The build system uses this graph to determine:
- Build order (topological sort)
- What to rebuild when something changes (affected analysis)
- What to cache and invalidate

### Task Graph

The task graph maps **tasks** (build, test, lint) across packages, respecting dependencies.

```
build:web depends on build:ui, build:types
build:ui depends on build:utils
test:web depends on build:web
```

Turborepo, Nx, and other orchestrators construct this graph and execute tasks with maximum parallelism while respecting ordering constraints.

### Incremental Builds

Only rebuild what changed. If `utils` hasn't changed since the last build, skip it. This requires:

1. **Input hashing** — Hash source files, dependencies, environment variables, config
2. **Output caching** — Store build artifacts keyed by input hash
3. **Cache restoration** — On cache hit, restore artifacts instead of rebuilding

### Remote Caching

Store build caches in a shared location (Vercel Remote Cache, Nx Cloud, S3, etc.) so that:
- CI doesn't rebuild what a developer already built locally
- Developer B doesn't rebuild what Developer A already built
- Different CI runs share cache

**Cost implication:** Remote caching can reduce CI minutes by 40-80% in mature monorepos.

### Affected Builds

Given a set of changed files, determine which packages are affected and only build/test those.

```
Changed: packages/utils/src/format.ts
Affected: packages/utils, packages/ui (depends on utils), apps/web (depends on ui)
NOT affected: apps/docs (doesn't depend on utils)
```

### Package Boundaries

Rules that prevent packages from importing things they shouldn't:

- `apps/web` can import from `packages/ui` but NOT from `apps/api`
- `packages/utils` should NOT import from `packages/ui` (would create a circular dependency)
- Enforced via TypeScript project references, ESLint rules (e.g., `@nx/enforce-module-boundaries`), or build system constraints

### Code Ownership

At scale, packages have owners. CODEOWNERS files map paths to teams:

```
# CODEOWNERS
packages/ui/        @frontend-team
packages/api-client/ @platform-team
apps/web/           @web-team
apps/api/           @backend-team
```

### Internal Package Versioning

Two strategies:

| Strategy | How it works | Best for |
|----------|-------------|----------|
| **Fixed/locked** | All internal packages at `"workspace:*"` — always use latest | Most monorepos. Simpler. |
| **Independent** | Each package has its own semver, published to registry | Large orgs with external consumers |

**Recommendation:** Start with `workspace:*`. Move to independent versioning only when you have external consumers or strict API contracts between teams.

## Change Lifecycle

```
Developer changes packages/utils/src/format.ts
         │
         ▼
Build system detects changed files
         │
         ▼
Dependency graph identifies affected packages:
  utils → ui → web (affected)
  docs (not affected — no dependency on utils)
         │
         ▼
Task graph schedules builds in topological order:
  1. build:utils (changed)
  2. build:ui (depends on utils)
  3. build:web (depends on ui)
         │
         ▼
Cache check for each task:
  - build:utils → cache MISS (source changed) → rebuild
  - build:ui → cache MISS (dependency changed) → rebuild
  - build:web → cache MISS (dependency changed) → rebuild
         │
         ▼
CI runs tests only for affected packages
         │
         ▼
Deploy only affected apps (web)
```

## Monorepo vs Microfrontend vs Multi-Repo

| Dimension | Monorepo | Microfrontend | Multi-Repo |
|-----------|----------|---------------|------------|
| **Code location** | Single repo | Can be mono or multi | Separate repos |
| **Deployment** | Can deploy independently | Independent by design | Independent by default |
| **Shared code** | Direct imports | Runtime federation or npm | npm packages |
| **Dependency management** | Unified | Per-app | Per-repo |
| **Build complexity** | High (needs orchestration) | Medium (federation config) | Low (per-repo) |
| **Refactoring** | Easy (atomic changes) | Hard (runtime contracts) | Hard (cross-repo PRs) |
| **Team autonomy** | Medium (shared constraints) | High | High |
| **CI complexity** | High (needs filtering) | Medium | Low (per-repo) |
| **Best for** | 1-30 teams, shared platform | 5+ teams needing deploy independence | Isolated projects |

**Key insight:** Monorepo and microfrontend are NOT mutually exclusive. You can have a monorepo that deploys microfrontends. Module Federation + Turborepo is a real pattern.

## When Monorepo Is Useful

- Multiple apps sharing significant code (UI library, types, utils)
- Teams that need to make atomic cross-project changes
- Organizations wanting unified tooling and CI/CD
- Design system + consuming apps
- Frontend + BFF (Backend for Frontend) that share types
- Cloudflare Workers + web app sharing business logic

## When Monorepo Becomes Dangerous

- **No build orchestration** — Without Turborepo/Nx, builds become O(n) where n = all packages
- **God packages** — One package that everything depends on; any change rebuilds everything
- **No ownership** — "Everybody owns everything" means nobody maintains anything
- **CI without filtering** — Running all tests on every PR makes CI unusably slow
- **No package boundaries** — Spaghetti imports across packages
- **Too many languages** — Polyglot monorepos need Bazel-level tooling; JS-only tools won't scale

---

# 2. Learning Roadmap by Skill Level

## Level 1 — Newbie

### What to learn

1. **Understand what a monorepo is** — Not just "one repo," but structured multi-project workspace
2. **Workspace basics** — `pnpm-workspace.yaml`, `packages` field in `package.json`
3. **Shared package basics** — Create a `packages/utils` consumed by `apps/web`
4. **Installing dependencies** — Root vs package-level deps, `pnpm add -w`, `pnpm add --filter`
5. **Running multiple apps** — `pnpm --filter web dev`, `turbo dev`
6. **Shared TypeScript config** — Base `tsconfig.json` extended by all packages
7. **Shared ESLint config** — Single ESLint config package, extended everywhere

### Shared TypeScript Config Pattern

```jsonc
// packages/config-ts/tsconfig.base.json
{
  "compilerOptions": {
    "strict": true,
    "target": "ES2022",
    "module": "ESNext",
    "moduleResolution": "bundler",
    "jsx": "react-jsx",
    "esModuleInterop": true,
    "skipLibCheck": true,
    "forceConsistentCasingInFileNames": true,
    "declaration": true,
    "declarationMap": true,
    "sourceMap": true
  }
}

// apps/web/tsconfig.json
{
  "extends": "@acme/config-ts/tsconfig.base.json",
  "compilerOptions": {
    "outDir": "dist"
  },
  "include": ["src"]
}
```

### Shared ESLint Config Pattern

```js
// packages/config-eslint/index.js
module.exports = {
  extends: ["eslint:recommended", "plugin:@typescript-eslint/recommended", "prettier"],
  parser: "@typescript-eslint/parser",
  plugins: ["@typescript-eslint"],
  rules: {
    "no-console": "warn",
    "@typescript-eslint/no-unused-vars": "error",
  },
};

// apps/web/.eslintrc.js
module.exports = {
  root: true,
  extends: ["@acme/config-eslint"],
};
```

### Common Beginner Mistakes

| Mistake | Why it's wrong | Fix |
|---------|---------------|-----|
| Installing deps at root for everything | Bloats root, hides what packages actually need | Install deps in the package that uses them |
| No workspace protocol | Direct `"^1.0.0"` for internal packages | Use `"workspace:*"` |
| Copy-pasting tsconfig | Drift across packages | Create shared config package |
| No `.npmrc` with `shamefully-hoist=false` | Phantom dependencies | Set `shamefully-hoist=false` in pnpm |
| Running all scripts manually | Slow, error-prone | Use Turborepo or Nx for orchestration |

### 5 Beginner Exercises

1. **Hello Monorepo** — Create a pnpm workspace with 2 apps and 1 shared `utils` package. Import a function from `utils` into both apps.
2. **Shared Config** — Create a `config-ts` package with a base `tsconfig.json`. Have both apps extend it.
3. **Shared ESLint** — Create a `config-eslint` package. Have both apps use it.
4. **Workspace Scripts** — Set up `turbo.json` with `build`, `dev`, `lint` tasks. Run them with Turborepo.
5. **Dependency Exploration** — Run `pnpm ls --filter web` and `pnpm why react --filter web` to explore the dependency graph.

---

## Level 2 — Junior

### What to learn

1. **Internal package architecture** — `packages/ui` with proper `package.json`, exports, and build step
2. **Shared UI library** — React component library consumed by multiple apps
3. **Shared utility library** — Pure functions, helpers, formatters
4. **Build orchestration** — `turbo.json` pipelines, `dependsOn`, `outputs`
5. **Task pipelines** — Understanding topological task execution
6. **Package linking** — How `workspace:*` resolves, how `node_modules` linking works
7. **Versioning basics** — `workspace:*` vs `workspace:^` vs fixed versions
8. **Workspace protocols** — `pnpm` workspace protocol, `yarn` portal/link protocols
9. **Monorepo tooling basics** — Turborepo vs Nx vs plain workspaces

### Internal Package Structure

```
packages/ui/
├── src/
│   ├── Button.tsx
│   ├── Input.tsx
│   └── index.ts          ← barrel export
├── package.json
└── tsconfig.json
```

```jsonc
// packages/ui/package.json
{
  "name": "@acme/ui",
  "version": "0.0.0",
  "private": true,
  "exports": {
    ".": {
      "types": "./src/index.ts",
      "default": "./src/index.ts"
    }
  },
  "dependencies": {
    "react": "^18.3.0"
  },
  "devDependencies": {
    "@acme/config-ts": "workspace:*",
    "typescript": "^5.5.0"
  }
}
```

**Key insight:** For internal packages consumed only within the monorepo, you can skip the build step entirely by pointing `exports` directly at source `.ts` files. The consuming app's bundler (Next.js, Vite) will compile them. This is the **"internal packages" or "just-in-time" pattern** — massively simplifies DX.

When to add a build step:
- Package has complex build (e.g., CSS extraction, codegen)
- Package is consumed by tools that can't handle raw TS (e.g., some Node.js scripts)
- Package will eventually be published to npm

### Turborepo Pipeline Configuration

```jsonc
// turbo.json
{
  "$schema": "https://turbo.build/schema.json",
  "globalDependencies": ["**/.env.*local"],
  "tasks": {
    "build": {
      "dependsOn": ["^build"],     // Build dependencies first
      "outputs": ["dist/**", ".next/**", "!.next/cache/**"]
    },
    "dev": {
      "cache": false,              // Never cache dev
      "persistent": true           // Long-running process
    },
    "lint": {},                    // No dependencies, run in parallel
    "test": {
      "dependsOn": ["build"]      // Test after build
    },
    "type-check": {}               // No dependencies, run in parallel
  }
}
```

**`^build` explained:** The caret `^` means "run `build` in my dependencies first, then run `build` in me." Without `^`, it means "run `build` in me after `build` in me completes" (self-dependency — rarely useful).

### Common Anti-Patterns

| Anti-pattern | Problem | Solution |
|-------------|---------|----------|
| **Mega-package** | One `shared` package with everything | Split into focused packages: `ui`, `utils`, `types` |
| **Circular dependencies** | A imports B, B imports A | Extract shared code into a third package |
| **No task caching** | Every CI run rebuilds everything | Configure `outputs` in `turbo.json` |
| **Root-level everything** | All deps in root `package.json` | Deps belong in the package that uses them |
| **No filtering** | CI runs all tasks for all packages | Use `--filter` to scope to affected packages |

### 5 Mini Project Ideas

1. **Shared UI Library** — Build `@acme/ui` with Button, Input, Card components. Consume in a Next.js and Astro app.
2. **API Client Package** — Create `@acme/api-client` with typed fetch wrappers. Share between web app and Cloudflare Worker.
3. **Design Tokens** — Create `@acme/tokens` with colors, spacing, typography as TypeScript constants. Consume in `@acme/ui`.
4. **Multi-App Dashboard** — Next.js admin + Astro marketing site sharing `@acme/ui` and `@acme/utils`.
5. **Turborepo Pipeline** — Set up a full pipeline: `lint` → `type-check` → `build` → `test` with caching.

---

## Level 3 — Senior

### What to learn

1. **Scalable architecture** — Package graph design, boundary enforcement
2. **Incremental builds** — Input hashing, cache invalidation, output restoration
3. **Remote caching** — Vercel Remote Cache, Nx Cloud, custom S3 cache
4. **Affected builds** — `turbo run build --filter=...[HEAD^1]`, `nx affected`
5. **CI optimization** — Parallel jobs, cache warming, selective test runs
6. **Multi-team architecture** — Package ownership, CODEOWNERS, review requirements
7. **Ownership boundaries** — Enforcing import rules between packages
8. **Package governance** — RFC process for new packages, deprecation strategy
9. **Shared design system** — Versioned component library with Storybook
10. **Shared API clients** — Typed clients generated from OpenAPI/GraphQL schemas
11. **Build performance** — Profiling builds, reducing critical path, parallelism
12. **Release management** — Changesets, conventional commits, automated publishing
13. **Deployment strategy** — Independent deploy, blue-green, preview deployments per app

### CI Optimization Strategy

```yaml
# .github/workflows/ci.yml
name: CI
on:
  pull_request:
    branches: [main]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0  # Full history for affected analysis

      - uses: pnpm/action-setup@v4
      - uses: actions/setup-node@v4
        with:
          node-version: 20
          cache: "pnpm"

      - run: pnpm install --frozen-lockfile

      # Only build affected packages
      - run: pnpm turbo build --filter="...[origin/main]"

      # Only test affected packages
      - run: pnpm turbo test --filter="...[origin/main]"

      # Lint and type-check can run on everything (fast with cache)
      - run: pnpm turbo lint type-check
```

**`--filter="...[origin/main]"` explained:**
- `[origin/main]` = packages with changes since `origin/main`
- `...` prefix = include all dependents (downstream packages)
- So if `utils` changed, this runs `utils`, `ui`, `web` — everything that depends on `utils`

### Remote Caching Setup (Turborepo + Vercel)

```bash
# Link to Vercel for remote cache
npx turbo login
npx turbo link

# Or self-hosted with environment variables
TURBO_TOKEN=your-token
TURBO_TEAM=your-team
TURBO_API=https://your-cache-server.com
```

**Impact:** First CI run takes 8 minutes. Subsequent runs with cache hits: 45 seconds.

### Release Management with Changesets

```bash
# Install
pnpm add -Dw @changesets/cli @changesets/changelog-github

# Init
pnpm changeset init
```

```jsonc
// .changeset/config.json
{
  "$schema": "https://unpkg.com/@changesets/config@3.0.0/schema.json",
  "changelog": "@changesets/changelog-github",
  "commit": false,
  "fixed": [],
  "linked": [],
  "access": "restricted",
  "baseBranch": "main",
  "updateInternalDependencies": "patch",
  "ignore": []
}
```

Workflow:
1. Developer runs `pnpm changeset` → creates a changeset file describing the change
2. PR includes the changeset file
3. On merge, Changesets bot opens a "Version Packages" PR
4. Merging that PR bumps versions and publishes

### Multi-App Docker Strategy

```dockerfile
# Dockerfile (from repo root)
FROM node:20-slim AS base
RUN corepack enable

FROM base AS pruned
WORKDIR /app
COPY . .
# Turbo prune creates a sparse monorepo with only the target app + its dependencies
RUN npx turbo prune --scope=@acme/web --docker

FROM base AS installer
WORKDIR /app
COPY --from=pruned /app/out/json/ .
RUN pnpm install --frozen-lockfile
COPY --from=pruned /app/out/full/ .
RUN pnpm turbo build --filter=@acme/web

FROM base AS runner
WORKDIR /app
COPY --from=installer /app/apps/web/.next/standalone ./
COPY --from=installer /app/apps/web/.next/static ./apps/web/.next/static
COPY --from=installer /app/apps/web/public ./apps/web/public
CMD ["node", "apps/web/server.js"]
```

**`turbo prune` is critical.** Without it, Docker copies the entire monorepo. With prune, only the relevant packages are included, making images dramatically smaller.

### 5 Production-Grade Project Examples

1. **Design System Monorepo** — `@acme/tokens` → `@acme/ui` → `@acme/storybook` + `apps/docs`. Versioned with Changesets, published to private npm.
2. **Full-Stack SaaS** — Next.js web + Express API + shared `@acme/types` + shared `@acme/api-client`. Docker build with `turbo prune`. Deploy to Vercel (web) + Railway (API).
3. **Multi-Site Platform** — Marketing site (Astro) + App (Next.js) + Admin (Next.js) sharing `@acme/ui`, `@acme/auth`, `@acme/analytics`.
4. **Edge + Web** — Cloudflare Worker + Next.js sharing `@acme/business-logic`, `@acme/types`. Worker deployed via Wrangler, web via Vercel.
5. **Internal Developer Platform** — CLI tools (`@acme/cli`), shared configs (`@acme/config-*`), code generators, linting rules — all in one monorepo powering DX for the organization.

---

## Level 4 — Expert

### What to learn

1. **Organization-scale monorepo systems** — 50+ packages, 10+ teams
2. **Build systems architecture** — How Turborepo/Nx/Bazel work internally
3. **Custom task orchestration** — Custom scripts for complex build graphs
4. **Dependency graph optimization** — Reducing critical path length
5. **Distributed caching** — S3/GCS/R2 cache backends, cache key design
6. **Build invalidation strategy** — Environment-aware hashing, platform-specific caches
7. **Multi-language monorepos** — JS + Go + Python + Rust in one repo (Bazel territory)
8. **Monorepo governance** — RFC process, package creation guidelines, deprecation
9. **Platform engineering mindset** — Treating the monorepo as a product
10. **DX platform architecture** — Internal tools, code generators, migration scripts

### Architecture Review Checklist

```markdown
□ Is the dependency graph a clean DAG? No cycles?
□ Are package boundaries enforced (lint rules, TS project references)?
□ Is there a "god package" that everything depends on?
□ Can each app be deployed independently?
□ Is remote caching configured and working?
□ Is CI using affected-only builds?
□ Are build times under 5 minutes for typical PRs?
□ Is there CODEOWNERS for every package?
□ Are shared configs centralized (TS, ESLint, Prettier)?
□ Is there a process for creating new packages?
□ Is there a deprecation/removal process?
□ Are dependency versions consistent across packages?
□ Is Docker build optimized with turbo prune?
□ Are environment variables managed consistently?
□ Is there documentation for the package architecture?
```

### What Expert Engineers Care About That Juniors Miss

| Expert Focus | Junior Blind Spot |
|-------------|------------------|
| **Dependency graph shape** | "It works" without understanding build order |
| **Cache hit rate** | Not measuring cache effectiveness |
| **Critical path length** | Not understanding what serializes the build |
| **Package boundary enforcement** | Free-for-all imports |
| **Build invalidation correctness** | "Just clear the cache" |
| **Incremental adoption** | "Rewrite everything at once" |
| **Governance and process** | Technical solution without organizational solution |
| **Cost of shared code** | "Share everything" without considering coupling |
| **Migration strategy** | No plan for evolving architecture |
| **DX measurement** | Not tracking build times, cache hit rates, developer wait times |

### 10 Advanced Engineering Discussion Topics

1. **Graph theory in build systems** — How topological sort, critical path analysis, and cycle detection apply to monorepo builds
2. **Cache key design** — What inputs should be included in a cache key? Environment variables? Node version? OS? Architecture?
3. **The "diamond dependency problem"** — When A→B→D and A→C→D, how to ensure D is built only once with consistent inputs
4. **Incremental computation frameworks** — How Salsa (Rust), Build Systems à la Carte (Haskell), and Turborepo's approach differ
5. **Remote execution** — Moving beyond caching to executing builds on remote machines (Bazel RBE)
6. **Monorepo vs polyrepo organizational dynamics** — Conway's Law implications, team topology effects
7. **Package boundary evolution** — How to split, merge, and refactor packages without breaking consumers
8. **Multi-runtime type sharing** — Sharing types between Node.js, Cloudflare Workers, Deno, and browser environments
9. **Custom developer platforms** — Building internal CLIs, package generators, migration scripts
10. **The scaling ceiling** — When JS-ecosystem monorepo tools (Turborepo, Nx) hit their limits and you need Bazel/Buck2/Pants

---

# 3. Setup Guide

## pnpm Workspace Setup (Recommended)

### Step 1: Initialize

```bash
mkdir acme-monorepo && cd acme-monorepo
pnpm init
git init
```

### Step 2: Configure workspace

```yaml
# pnpm-workspace.yaml
packages:
  - "apps/*"
  - "packages/*"
```

```ini
# .npmrc
shamefully-hoist=false
strict-peer-dependencies=true
auto-install-peers=true
```

### Step 3: Root package.json

```jsonc
{
  "name": "acme-monorepo",
  "private": true,
  "scripts": {
    "build": "turbo build",
    "dev": "turbo dev",
    "lint": "turbo lint",
    "type-check": "turbo type-check",
    "test": "turbo test",
    "clean": "turbo clean && rm -rf node_modules"
  },
  "devDependencies": {
    "turbo": "^2.0.0"
  },
  "packageManager": "pnpm@9.0.0"
}
```

### Step 4: Turbo configuration

```jsonc
// turbo.json
{
  "$schema": "https://turbo.build/schema.json",
  "globalDependencies": ["**/.env.*local"],
  "tasks": {
    "build": {
      "dependsOn": ["^build"],
      "outputs": ["dist/**", ".next/**", "!.next/cache/**"]
    },
    "dev": {
      "cache": false,
      "persistent": true
    },
    "lint": {},
    "type-check": {},
    "test": {
      "dependsOn": ["build"]
    },
    "clean": {
      "cache": false
    }
  }
}
```

### Step 5: Create shared config packages

```bash
mkdir -p packages/config-ts packages/config-eslint
```

### Step 6: Create your first app

```bash
cd apps
pnpm create next-app@latest web --typescript --tailwind --eslint --app --src-dir
```

### Step 7: Create your first shared package

```bash
mkdir -p packages/ui/src
```

```jsonc
// packages/ui/package.json
{
  "name": "@acme/ui",
  "version": "0.0.0",
  "private": true,
  "exports": {
    ".": "./src/index.ts"
  },
  "devDependencies": {
    "@acme/config-ts": "workspace:*",
    "typescript": "^5.5.0"
  },
  "peerDependencies": {
    "react": "^18.0.0 || ^19.0.0"
  }
}
```

## npm Workspace Setup

```jsonc
// package.json
{
  "name": "acme-monorepo",
  "private": true,
  "workspaces": ["apps/*", "packages/*"]
}
```

Commands: `npm run build --workspace=apps/web`, `npm install lodash --workspace=packages/utils`

## Yarn Workspace Setup

```jsonc
// package.json
{
  "name": "acme-monorepo",
  "private": true,
  "workspaces": ["apps/*", "packages/*"]
}
```

Yarn Berry (v4) supports `yarn workspace web build`, PnP for zero-installs.

## Recommended Folder Structures

### Frontend-Only Monorepo

```
├── apps/
│   ├── web/           (Next.js)
│   ├── docs/          (Astro)
│   └── storybook/     (Storybook)
├── packages/
│   ├── ui/            (shared React components)
│   ├── hooks/         (shared React hooks)
│   ├── utils/         (shared utilities)
│   ├── tokens/        (design tokens)
│   ├── types/         (shared TypeScript types)
│   ├── config-ts/     (shared tsconfig)
│   └── config-eslint/ (shared ESLint config)
├── turbo.json
├── pnpm-workspace.yaml
└── package.json
```

### Frontend + Backend Monorepo

```
├── apps/
│   ├── web/           (Next.js)
│   ├── api/           (Express/Fastify)
│   └── worker/        (Cloudflare Worker)
├── packages/
│   ├── ui/
│   ├── api-client/    (typed API client)
│   ├── types/         (shared types between FE & BE)
│   ├── validation/    (shared Zod schemas)
│   ├── utils/
│   ├── config-ts/
│   └── config-eslint/
├── turbo.json
├── pnpm-workspace.yaml
└── package.json
```

### Design System Monorepo

```
├── apps/
│   ├── docs/          (Storybook or custom docs site)
│   └── playground/    (dev testing app)
├── packages/
│   ├── core/          (base components: Button, Input, etc.)
│   ├── icons/         (icon library)
│   ├── tokens/        (colors, spacing, typography)
│   ├── themes/        (light/dark/brand themes)
│   ├── hooks/         (UI hooks: useModal, useToast)
│   ├── utils/         (component utilities)
│   └── config/        (shared build/lint/TS config)
├── turbo.json
├── pnpm-workspace.yaml
└── package.json
```

### Microservices Monorepo

```
├── apps/
│   ├── gateway/       (API gateway)
│   ├── auth-service/
│   ├── user-service/
│   ├── payment-service/
│   └── web/           (frontend)
├── packages/
│   ├── proto/         (protobuf/gRPC definitions)
│   ├── types/
│   ├── logger/        (shared logging)
│   ├── config/        (shared service config)
│   ├── testing/       (shared test utilities)
│   └── db/            (shared database utilities)
├── docker-compose.yml
├── turbo.json
├── pnpm-workspace.yaml
└── package.json
```

## Shared Environment Variable Strategy

```typescript
// packages/env/src/index.ts
import { z } from "zod";

const envSchema = z.object({
  DATABASE_URL: z.string().url(),
  NEXT_PUBLIC_API_URL: z.string().url(),
  NODE_ENV: z.enum(["development", "production", "test"]).default("development"),
});

export const env = envSchema.parse(process.env);
export type Env = z.infer<typeof envSchema>;
```

**Why Zod for env?** Fail-fast at startup if environment variables are missing or invalid, with clear error messages.

## Internal Package Naming Strategy

```
@acme/ui           ← organization scope
@acme/utils
@acme/config-ts    ← prefix with category
@acme/config-eslint
@acme/api-client
@acme/types
```

**Rules:**
- Always use an org scope (`@acme/`)
- Use lowercase kebab-case
- Be descriptive but concise
- Prefix config packages with `config-`
- Avoid generic names like `@acme/shared` or `@acme/common`

## Recommended Starter Architecture

For your stack (React, Next.js, Astro, TypeScript):

```
acme-monorepo/
├── apps/
│   ├── web/              (Next.js — main app)
│   └── docs/             (Astro — documentation site)
├── packages/
│   ├── ui/               (shared React components)
│   ├── utils/            (shared pure functions)
│   ├── types/            (shared TypeScript types)
│   ├── config-ts/        (shared tsconfig)
│   └── config-eslint/    (shared ESLint config)
├── turbo.json
├── pnpm-workspace.yaml
├── .npmrc
├── .gitignore
└── package.json
```

**Start here. Grow organically.** Don't over-engineer the package structure before you have real code sharing needs.

---

# 4. Monorepo Tooling Comparison

## Overview Comparison Table

| Feature | Turborepo | Nx | pnpm workspaces | Yarn workspaces | Lage | Rush | Bazel |
|---------|-----------|----|-----------------|-----------------| -----|------|-------|
| **Philosophy** | Simple, fast, convention | Full-featured platform | Package manager feature | Package manager feature | MS task runner | MS enterprise | Google build system |
| **Learning curve** | Low | Medium-High | Very Low | Very Low | Low | High | Very High |
| **Task orchestration** | ✅ | ✅ | ❌ | ❌ | ✅ | ✅ | ✅ |
| **Dependency graph** | Auto (package.json) | Auto + explicit | Manual | Manual | Auto | Explicit | Explicit (BUILD files) |
| **Remote cache** | ✅ (Vercel) | ✅ (Nx Cloud) | ❌ | ❌ | ❌ | ✅ (custom) | ✅ (RBE) |
| **Affected builds** | ✅ | ✅ | ❌ | ❌ | ✅ | ✅ | ✅ |
| **Code generation** | ❌ | ✅ (generators) | ❌ | ❌ | ❌ | ❌ | ❌ |
| **Module boundary enforcement** | ❌ | ✅ (lint rules) | ❌ | ❌ | ❌ | ✅ (rush policies) | ✅ (visibility) |
| **Multi-language** | JS/TS only | Primarily JS/TS | JS/TS only | JS/TS only | JS/TS only | JS/TS only | Any language |
| **Best for** | Small-large JS monorepos | Medium-large, opinionated | Simple workspaces | Simple workspaces | MS-style monorepos | Enterprise JS | Massive multi-lang |
| **Scaling limit** | ~500 packages | ~1000 packages | N/A (no orchestration) | N/A | ~500 packages | ~1000 packages | Unlimited |

## Turborepo

**Core philosophy:** Zero-config, convention-over-configuration task runner for JS/TS monorepos. "Make it fast by doing less work."

**Pros:**
- Minimal setup (one `turbo.json` file)
- Excellent cache hit rates
- Vercel integration for remote caching
- Fast — written in Rust
- Simple mental model
- Great for React/Next.js ecosystem

**Cons:**
- No code generation
- No module boundary enforcement (need ESLint plugins)
- No dependency graph visualization (basic only)
- Limited plugin system
- JS/TS only

**When to choose:** Your stack is JS/TS, you want fast setup, you use Vercel or want simple remote caching. Teams of 1-50 engineers.

**When NOT to choose:** You need code generators, strict module boundaries, multi-language support, or enterprise governance features.

## Nx

**Core philosophy:** Smart, extensible build framework with deep understanding of your workspace. "A build system with knowledge."

**Pros:**
- Rich plugin ecosystem (Next.js, React, Node, etc.)
- Code generators (`nx generate`)
- Module boundary enforcement (`@nx/enforce-module-boundaries`)
- Dependency graph visualization (`nx graph`)
- Nx Cloud for distributed caching and CI
- Supports non-JS (Go, Rust, Python via plugins)
- Affected commands with fine-grained analysis

**Cons:**
- Higher learning curve
- More configuration needed
- Opinionated project structure
- Can feel "heavy" for small projects
- Plugin lock-in concerns

**When to choose:** Medium to large teams, need governance, want generators and structured workflows. Enterprise frontend teams.

**When NOT to choose:** Small projects, want minimal tooling overhead, prefer convention over configuration.

## pnpm Workspaces

**Core philosophy:** Fast, disk-efficient package manager with workspace support. Not a build system.

**What it provides:**
- Workspace linking (symlinks via content-addressable store)
- `--filter` for scoping commands
- Strict dependency resolution (no phantom deps)
- `workspace:*` protocol

**What it doesn't provide:**
- Task orchestration
- Caching
- Affected builds
- Dependency graph analysis for builds

**When to choose:** Always use as your package manager in a monorepo. Pair with Turborepo or Nx for orchestration.

## Bazel

**Core philosophy:** Google's build system. Correct, reproducible, scalable builds for any language.

**Pros:**
- Unlimited scale (Google uses it for billions of lines of code)
- Multi-language (JS, TS, Go, Java, Python, C++, Rust)
- Remote execution (distribute builds across machines)
- Hermetic builds (fully reproducible)
- Fine-grained caching (file-level, not package-level)

**Cons:**
- Extremely steep learning curve
- Requires `BUILD` files for every target
- Poor DX for JS/TS ecosystem
- Significant migration effort
- Overkill for most JS/TS monorepos

**When to choose:** Multi-language monorepo, 100+ engineers, need hermetic builds and remote execution. Companies like Google, Stripe, Twitter.

**When NOT to choose:** JS/TS-only projects, small-medium teams, want fast setup.

## Decision Matrix

| Scenario | Recommendation |
|----------|---------------|
| Solo/small team, JS/TS, want fast start | **pnpm + Turborepo** |
| Medium team, want structure and generators | **pnpm + Nx** |
| Enterprise, need governance and policies | **pnpm + Nx** or **Rush** |
| Multi-language, massive scale | **Bazel** |
| Already on Vercel | **pnpm + Turborepo** |
| Design system library | **pnpm + Turborepo** |
| Microsoft ecosystem | **Rush** or **Lage** |

---

# 5. Cheatsheet

## Workspace Commands (pnpm)

| Command | Description |
|---------|-------------|
| `pnpm install` | Install all deps across all workspaces |
| `pnpm add <pkg> --filter <workspace>` | Add dep to specific workspace |
| `pnpm add <pkg> -w` | Add dep to root workspace |
| `pnpm remove <pkg> --filter <workspace>` | Remove dep from workspace |
| `pnpm --filter <workspace> <script>` | Run script in specific workspace |
| `pnpm --filter "./apps/**" build` | Run build in all apps |
| `pnpm --filter "!./apps/docs" build` | Run build in all except docs |
| `pnpm ls --filter <workspace>` | List deps for a workspace |
| `pnpm why <pkg> --filter <workspace>` | Why is this dep installed? |

## Turborepo Commands

| Command | Description |
|---------|-------------|
| `turbo build` | Build all packages (topological order) |
| `turbo build --filter=web` | Build only web app + deps |
| `turbo build --filter=web...` | Build web and all its deps |
| `turbo build --filter=...web` | Build web and all its dependents |
| `turbo build --filter="...[HEAD~1]"` | Build packages changed since last commit |
| `turbo build --filter="...[origin/main]"` | Build packages changed since main |
| `turbo build --dry` | Show what would run without running it |
| `turbo build --graph` | Output dependency graph (DOT format) |
| `turbo build --summarize` | Generate build summary JSON |
| `turbo prune --scope=web` | Create sparse monorepo for Docker |
| `turbo daemon status` | Check Turbo daemon status |

## Internal Package Pattern

```jsonc
// packages/utils/package.json — "Just-in-Time" (no build step)
{
  "name": "@acme/utils",
  "private": true,
  "exports": {
    ".": { "types": "./src/index.ts", "default": "./src/index.ts" }
  }
}

// packages/ui/package.json — with build step
{
  "name": "@acme/ui",
  "private": true,
  "exports": {
    ".": { "types": "./dist/index.d.ts", "default": "./dist/index.js" }
  },
  "scripts": {
    "build": "tsup src/index.ts --format esm,cjs --dts"
  }
}
```

## Common Build Issues & Fixes

| Issue | Cause | Fix |
|-------|-------|-----|
| Package not found | Missing `workspace:*` in deps | Add dependency: `pnpm add @acme/utils --filter web` |
| Type errors in shared package | TS not resolving source | Point `exports` types field to source or build first |
| Stale builds | Old cached output | `turbo build --force` or `rm -rf node_modules/.cache` |
| Circular dependency | A→B→A | Extract shared code to C, then A→C, B→C |
| Phantom dependency | Using undeclared dep | Set `shamefully-hoist=false` in `.npmrc` |
| Build order wrong | Missing `^` in `dependsOn` | Use `"dependsOn": ["^build"]` in turbo.json |

## Performance Tips

1. **Use `--filter`** — Never build everything when you only changed one package
2. **Enable remote caching** — Saves 40-80% CI time
3. **Use internal packages without build step** — Skip compilation, let the consumer's bundler handle it
4. **Parallelize independent tasks** — `lint` and `type-check` have no dependencies; run in parallel
5. **Use `turbo prune` for Docker** — Dramatically smaller Docker build contexts
6. **Profile builds** — `turbo build --summarize` shows where time is spent
7. **Avoid barrel re-exports** — `index.ts` that re-exports everything defeats tree-shaking
8. **Split large packages** — One change shouldn't invalidate cache for unrelated code
9. **Pin external dependencies** — Inconsistent versions across packages cause duplicate bundles
10. **Use TypeScript project references** — Enables incremental type-checking

---

# 6. Real-World Engineering Mindset

## Shared UI Library

**Problem:** Multiple apps need the same Button, Input, Modal components. Copy-paste leads to drift.

**Strategies:**

| Strategy | How | Pros | Cons |
|----------|-----|------|------|
| **Internal package (JIT)** | `@acme/ui` exports raw `.tsx`, consumed app bundles it | Zero build step, fast DX | Consumer must handle TS compilation |
| **Internal package (built)** | `@acme/ui` built with tsup/Vite lib mode | Clean separation, works with any consumer | Extra build step, slower dev |
| **Published package** | `@acme/ui` published to npm/private registry | External teams can consume | Version management overhead |

**Senior recommendation:** Start with JIT internal package. Add a build step only when you need CSS extraction, have non-TS consumers, or plan to publish externally.

## Shared API Client

**Problem:** Frontend and BFF/Worker both call the same API. Types and fetch logic duplicated.

**Strategy:**
```typescript
// packages/api-client/src/client.ts
import { z } from "zod";

const UserSchema = z.object({
  id: z.string(),
  name: z.string(),
  email: z.string().email(),
});

export type User = z.infer<typeof UserSchema>;

export async function getUser(id: string): Promise<User> {
  const res = await fetch(`/api/users/${id}`);
  return UserSchema.parse(await res.json());
}
```

Share between Next.js app and Cloudflare Worker. Both get type safety and runtime validation.

## Cloudflare Workers Inside Monorepo

**Problem:** Workers have different runtime constraints (no Node.js APIs), but need to share business logic with the web app.

**Strategy:**

```
packages/
  business-logic/     ← Pure functions, no Node/browser APIs
  types/              ← Shared types
apps/
  web/                ← Next.js (uses business-logic + types)
  worker/             ← Cloudflare Worker (uses business-logic + types)
```

```toml
# apps/worker/wrangler.toml
name = "acme-worker"
main = "src/index.ts"
compatibility_date = "2024-01-01"

[build]
command = "pnpm turbo build --filter=@acme/worker"
```

**Key constraint:** Shared packages consumed by Workers MUST be runtime-agnostic. No `fs`, `path`, `process`, `Buffer`, `node:*` imports.

## Multi-Team Ownership

**Problem:** 5 teams, 30 packages. Who reviews what? Who can break what?

**Strategy:**

```
# CODEOWNERS
packages/ui/          @design-system-team
packages/auth/        @platform-team
packages/analytics/   @data-team
apps/web/             @web-team
apps/api/             @backend-team
packages/config-*/    @dx-team
turbo.json            @dx-team
pnpm-workspace.yaml   @dx-team
```

Combined with Nx module boundary rules or ESLint import restrictions:
```jsonc
// .eslintrc — enforce that apps/web cannot import from apps/api
{
  "rules": {
    "@nx/enforce-module-boundaries": ["error", {
      "depConstraints": [
        { "sourceTag": "scope:web", "onlyDependOnLibsWithTags": ["scope:shared"] },
        { "sourceTag": "scope:api", "onlyDependOnLibsWithTags": ["scope:shared"] }
      ]
    }]
  }
}
```

## Selective CI Pipelines

**Small org (1-5 devs):** Run everything, rely on Turborepo cache.

**Medium org (5-30 devs):**
```yaml
- run: pnpm turbo build test lint --filter="...[origin/main]"
```

**Large org (30+ devs):**
```yaml
jobs:
  detect-changes:
    outputs:
      web: ${{ steps.filter.outputs.web }}
      api: ${{ steps.filter.outputs.api }}
    steps:
      - uses: dorny/paths-filter@v3
        id: filter
        with:
          filters: |
            web: ['apps/web/**', 'packages/ui/**', 'packages/utils/**']
            api: ['apps/api/**', 'packages/types/**']

  build-web:
    needs: detect-changes
    if: needs.detect-changes.outputs.web == 'true'
    # ...

  build-api:
    needs: detect-changes
    if: needs.detect-changes.outputs.api == 'true'
    # ...
```

---

# 7. Brainstorm / Open Questions

## Architecture (10 questions)

1. Should every piece of shared code become its own package, or is co-location in a larger package better?
2. How do you decide between a "utils" grab-bag package vs multiple focused packages?
3. When should a monorepo be split into multiple monorepos?
4. How do you handle a package that only two apps use — is it worth extracting?
5. Should your monorepo contain infrastructure code (Terraform, Pulumi) alongside application code?
6. How do you architect a monorepo that contains both browser-runtime and edge-runtime code?
7. When does a shared package become "too shared" and start coupling unrelated teams?
8. How should you handle packages that have fundamentally different release cadences?
9. What's the right granularity for a package — one component? One feature? One domain?
10. Should test utilities be in the package they test or in a shared testing package?

## Scaling (8 questions)

11. At what point does `pnpm install` become a bottleneck, and how do you fix it?
12. How do you handle a monorepo with 500+ packages where Turborepo's task scheduling becomes the bottleneck?
13. When should you consider migrating from Turborepo to Bazel?
14. How do you handle monorepo git performance as the repo grows beyond 10GB?
15. What's the impact of adding a new package that depends on 80% of existing packages?
16. How do you manage lock file conflicts when 20 developers merge PRs daily?
17. At what scale do you need to consider sparse checkouts or virtual file systems?
18. How do you measure and track monorepo health metrics over time?

## DX / Maintainability (8 questions)

19. How do you onboard a new developer to a 100-package monorepo?
20. What documentation should every package have?
21. How do you prevent "package sprawl" — too many small packages?
22. Should you have a CLI tool that scaffolds new packages with templates?
23. How do you handle the tension between "move fast" and "maintain consistency"?
24. What's the cost of NOT having a dedicated DX/platform team maintaining the monorepo?
25. How should IDE performance be managed in large monorepos (TypeScript language server slowness)?
26. How do you maintain a "golden path" for common development workflows?

## CI/CD (8 questions)

27. How do you handle CI minutes costs as the monorepo grows?
28. Should each app have its own deployment pipeline, or should there be one unified pipeline?
29. How do you handle preview deployments for multiple apps changed in a single PR?
30. What happens when a shared package update needs to deploy 15 apps simultaneously?
31. How do you handle rollbacks when a shared package deployment breaks one app but not others?
32. Should CI build Docker images for all apps or only affected apps?
33. How do you handle secrets management across different apps in CI?
34. What's the right strategy for E2E tests in a monorepo — per-app or cross-app?

## Dependency Management (8 questions)

35. How do you enforce a single version policy for critical dependencies (React, TypeScript)?
36. What happens when upgrading a dependency breaks one package but not others?
37. How should peer dependencies work in internal packages?
38. Should you use Renovate/Dependabot in a monorepo, and how do you handle the PR flood?
39. How do you handle transitive dependency conflicts across packages?
40. When should an internal package declare a dependency vs inherit it from the consuming app?
41. How do you audit dependency sizes across a monorepo to prevent bundle bloat?
42. What's the strategy for handling packages that need different versions of the same dependency?

## Build Systems (8 questions)

43. How does Turborepo determine if a cache is valid or stale?
44. What's the difference between content-based hashing and timestamp-based invalidation?
45. How do you debug a cache miss that shouldn't have been a miss?
46. What are the trade-offs of coarse-grained (package-level) vs fine-grained (file-level) caching?
47. How do you handle non-deterministic builds (timestamps in output, random IDs)?
48. What's the impact of environment variables on cache hit rates?
49. How do you cache builds that depend on external services (API calls during build)?
50. When is it better to NOT cache a task?

## Performance (7 questions)

51. How do you identify the critical path in your build graph?
52. What causes unnecessary rebuilds, and how do you diagnose them?
53. How do you reduce TypeScript type-checking time across 50 packages?
54. What's the performance impact of barrel exports (`index.ts`) on build and bundle size?
55. How do you optimize `pnpm install` time in CI?
56. Should you use SWC/esbuild/tsup for building internal packages, and when does it matter?
57. How do you measure and track build performance regressions?

## Organization Strategy (8 questions)

58. Should monorepo structure mirror team structure or domain structure?
59. Who should own the root configuration (turbo.json, pnpm-workspace.yaml)?
60. How do you handle the politics of shared code ownership?
61. What governance is needed before teams start creating packages?
62. How do you handle a team that wants to leave the monorepo?
63. What's the process for deprecating and removing an internal package?
64. How do you align monorepo architecture with Conway's Law?
65. Should each team have "protected" packages that other teams cannot depend on?

---

# 8. Practice Questions

## Beginner (20 Questions)

### Q1
**Question:** What file defines which folders are part of a pnpm workspace?
**Type:** Single choice
**Options:** A) package.json B) turbo.json C) pnpm-workspace.yaml D) tsconfig.json
**Answer:** C
**Why:** `pnpm-workspace.yaml` declares the workspace package globs. `package.json` can define workspaces for npm/yarn, but for pnpm it's the YAML file.

### Q2
**Question:** True or False: In a monorepo, all packages must use the same version of React.
**Type:** True/False
**Answer:** False
**Why:** While a single version policy is recommended, it's not technically required. Multiple versions can coexist but will increase bundle sizes and cause subtle bugs.

### Q3
**Question:** What does `workspace:*` mean in a package.json dependency?
**Type:** Single choice
**Options:** A) Install from npm B) Link to the local workspace package at any version C) Install the latest version D) Create a symbolic link
**Answer:** B
**Why:** `workspace:*` tells the package manager to resolve this dependency from the local workspace, not from the npm registry. It links to whatever version the local package declares.

### Q4
**Question:** Which command adds `lodash` as a dependency specifically to the `web` app in a pnpm workspace?
**Type:** Single choice
**Options:** A) `pnpm add lodash` B) `pnpm add lodash -w` C) `pnpm add lodash --filter web` D) `cd apps/web && npm install lodash`
**Answer:** C
**Why:** `--filter web` scopes the command to the `web` workspace. `-w` adds to root. Plain `pnpm add` in root fails without `-w` or `--filter`.

### Q5
**Question:** True or False: A root `node_modules` folder in a pnpm workspace contains all dependencies for all packages.
**Type:** True/False
**Answer:** False
**Why:** pnpm uses a content-addressable store with symlinks. Each package gets only its declared dependencies. This prevents phantom dependencies.

### Q6
**Question:** What is a "phantom dependency"?
**Type:** Fill in the blank
**Answer:** A dependency that a package can use in code but has NOT explicitly declared in its `package.json`. This happens because hoisting makes it available in `node_modules`.
**Why:** Phantom deps work locally but break in production or when the undeclared transitive dep is removed. pnpm prevents this with strict isolation.

### Q7
**Question:** You have `apps/web` and `packages/ui`. Web imports from UI. Which `package.json` should declare the dependency on `@acme/ui`?
**Type:** Single choice
**Options:** A) Root package.json B) apps/web/package.json C) packages/ui/package.json D) Both root and web
**Answer:** B
**Why:** Dependencies belong in the package that uses them. Root deps are for workspace-level tooling only.

### Q8
**Question:** What is the purpose of `"private": true` in a package.json for an internal monorepo package?
**Type:** Single choice
**Options:** A) Prevents the package from being imported B) Prevents accidental publishing to npm C) Makes the package invisible to other workspaces D) Hides the package from git
**Answer:** B
**Why:** `"private": true` tells npm/pnpm to refuse `publish` commands. It's a safety net against accidentally publishing internal code.

### Q9
**Question:** True or False: You should install TypeScript in every package's devDependencies.
**Type:** True/False
**Answer:** It depends, but generally True for correctness.
**Why:** Each package should declare its own dependencies. However, in practice many monorepos install TypeScript at the root only and rely on hoisting. The strict-correct approach is per-package.

### Q10
**Question:** Match each term with its definition:
**Type:** Matching

| Term | Definition |
|------|-----------|
| A. Application | 1. A non-deployable reusable module |
| B. Library | 2. Package manager feature for linking packages |
| C. Workspace | 3. A deployable unit |
| D. Package | 4. Any folder with package.json |

**Answer:** A→3, B→1, C→2, D→4

### Q11
**Question:** What command runs the `dev` script in ALL workspace packages simultaneously?
**Type:** Single choice
**Options:** A) `pnpm dev` B) `pnpm --recursive dev` C) `turbo dev` D) `pnpm --filter "*" dev`
**Answer:** C
**Why:** `turbo dev` runs the dev task across all packages with `persistent: true`, handling parallelism. `pnpm --recursive` works but without orchestration.

### Q12
**Question:** You created a new `packages/utils` but `apps/web` can't import from it. What's the most likely issue?
**Type:** Scenario-based
**Answer:** `apps/web/package.json` is missing `"@acme/utils": "workspace:*"` in its dependencies.
**Why:** Workspace linking requires explicit dependency declarations. Just having the folder isn't enough.

### Q13
**Question:** What does `shamefully-hoist=false` do in `.npmrc`?
**Type:** Single choice
**Options:** A) Prevents installing dependencies B) Enables strict dependency isolation C) Disables the lockfile D) Removes node_modules
**Answer:** B
**Why:** It tells pnpm to NOT hoist packages to the root, enforcing that each package can only use its declared dependencies. Prevents phantom deps.

### Q14
**Question:** True or False: A shared ESLint config package needs to list `eslint` as a dependency.
**Type:** True/False
**Answer:** True (as a peer dependency)
**Why:** The config package expects `eslint` to be available. It should declare it as a `peerDependency` so the consuming package provides the actual version.

### Q15
**Question:** What is a "barrel export"?
**Type:** Fill in the blank
**Answer:** An `index.ts` file that re-exports everything from a package's modules, e.g., `export * from './Button'; export * from './Input';`
**Why:** Barrels simplify imports (`from '@acme/ui'` instead of `from '@acme/ui/Button'`) but can defeat tree-shaking and slow builds.

### Q16
**Question:** How do you extend a shared TypeScript config in a consuming package?
**Type:** Code
**Answer:** `{ "extends": "@acme/config-ts/tsconfig.base.json" }`
**Why:** TypeScript's `extends` field resolves the path through node_modules, finding the workspace-linked package.

### Q17
**Question:** True or False: Every internal package in a monorepo needs a build step.
**Type:** True/False
**Answer:** False
**Why:** Internal packages can export raw TypeScript source and let the consuming app's bundler (Next.js, Vite) compile them. This is the "Just-in-Time" pattern.

### Q18
**Question:** What is the `exports` field in package.json used for?
**Type:** Single choice
**Options:** A) Listing all source files B) Defining the public API entry points C) Exporting environment variables D) Publishing to npm
**Answer:** B
**Why:** `exports` defines what paths consumers can import from, providing encapsulation and enabling conditional exports (types, ESM, CJS).

### Q19
**Question:** You run `pnpm install` and get "ERR_PNPM_PEER_DEP_ISSUES". What does this mean?
**Type:** Scenario-based
**Answer:** A package requires a peer dependency that isn't installed or is at an incompatible version.
**Why:** Peer deps must be provided by the consumer. Check which peer dep is missing and add it to the consuming package.

### Q20
**Question:** What is the purpose of the root `package.json` in a monorepo?
**Type:** Multiple choice
**Options:** A) Define workspace scripts B) Declare workspace-level dev tools C) Mark as private D) Specify package manager E) All of the above
**Answer:** E
**Why:** Root package.json serves as the workspace coordinator: scripts, shared dev tools (turbo, prettier), `private: true`, and `packageManager` field.

---

## Junior (20 Questions)

### Q21
**Question:** What does `"dependsOn": ["^build"]` mean in turbo.json?
**Type:** Single choice
**Options:** A) Run build in the same package first B) Run build in dependency packages first C) Skip the build D) Run build in dependent packages first
**Answer:** B
**Why:** The caret `^` means "my dependencies" (upstream). So `^build` = "build my dependencies before building me." Without `^`, it would mean a self-dependency.

### Q22
**Question:** You have the dependency chain: `web → ui → utils → types`. You change `types/src/user.ts`. Which packages need to rebuild?
**Type:** Multiple choice
**Options:** A) types B) utils C) ui D) web E) All of the above
**Answer:** E
**Why:** Every package downstream of `types` in the dependency graph is affected. The build runs in topological order: types → utils → ui → web.

### Q23
**Question:** True or False: `turbo build --filter=web` only builds the `web` package, not its dependencies.
**Type:** True/False
**Answer:** False
**Why:** `--filter=web` builds `web` AND all its transitive dependencies (because of `"dependsOn": ["^build"]`). Use `--filter=web --no-deps` to build only web.

### Q24
**Question:** What is a circular dependency in a monorepo context?
**Type:** Fill in the blank
**Answer:** When package A depends on package B, and package B depends on package A (directly or transitively), creating a cycle in the dependency graph.
**Why:** Circular deps make topological sort impossible, causing build failures or infinite loops. The fix is extracting shared code into a third package.

### Q25
**Question:** How does Turborepo determine if a cached build is still valid?
**Type:** Single choice
**Options:** A) Checks file timestamps B) Hashes source files, deps, and config C) Compares git commits D) Checks package version numbers
**Answer:** B
**Why:** Turborepo creates a content hash from: source files, dependency outputs, environment variables, and configuration. If the hash matches a cached entry, it's a cache hit.

### Q26
**Question:** What is the "Just-in-Time" (JIT) internal package pattern?
**Type:** Single choice
**Options:** A) Building packages on demand in CI B) Exporting raw TypeScript source for consumer bundlers to compile C) Lazy-loading packages at runtime D) Publishing packages just before deployment
**Answer:** B
**Why:** JIT packages skip their own build step by pointing `exports` at `.ts` source files. The consumer's bundler (Next.js, Vite) handles compilation. Dramatically simplifies DX.

### Q27
**Question:** Your CI takes 20 minutes. All packages rebuild on every PR even though only `apps/web` changed. What's wrong?
**Type:** Scenario-based
**Answer:** CI is not using affected filtering. Add `--filter="...[origin/main]"` to only build/test packages changed since main.
**Why:** Without filtering, Turborepo builds everything. The `[origin/main]` comparator limits work to changed packages and their dependents.

### Q28
**Question:** What's the difference between `--filter=web...` and `--filter=...web` in Turborepo?
**Type:** Matching

| Filter | Meaning |
|--------|---------|
| `--filter=web...` | web + all its dependencies (upstream) |
| `--filter=...web` | web + all its dependents (downstream) |

**Answer:** `web...` = web + deps (things web needs). `...web` = web + dependents (things that need web).

### Q29
**Question:** You add `@acme/analytics` as a dependency to every app. Now every change to `analytics` rebuilds all apps. How do you minimize blast radius?
**Type:** Scenario-based
**Answer:** Make `analytics` as stable as possible. Consider: (1) separate its public API from implementation, (2) ensure good caching so rebuilds are cache hits, (3) consider lazy loading, (4) evaluate if all apps actually need it.
**Why:** A package depended on by everything becomes a "god package." Any change cascades through the entire graph.

### Q30
**Question:** True or False: `outputs` in turbo.json tells Turborepo which files to include in the input hash.
**Type:** True/False
**Answer:** False
**Why:** `outputs` specifies what files to CACHE (store and restore on hit). `inputs` (or the default — all files) controls the hash. They serve different purposes.

### Q31
**Question:** What is a task graph?
**Type:** Single choice
**Options:** A) A graph of npm packages B) A graph of tasks across packages respecting dependencies C) A visual diagram of the repo D) A dependency tree of node_modules
**Answer:** B
**Why:** The task graph maps every task (build, test, lint) across every package, with edges representing dependencies. Turborepo traverses this graph for execution.

### Q32
**Question:** How should React be declared in a shared UI library package?
**Type:** Single choice
**Options:** A) `dependencies` B) `devDependencies` C) `peerDependencies` D) `optionalDependencies`
**Answer:** C
**Why:** React should be a `peerDependency` so the consuming app provides a single React instance. Having React in `dependencies` would create multiple React instances, causing hooks to break.

### Q33
**Question:** What does `turbo prune --scope=web` produce?
**Type:** Single choice
**Options:** A) Deletes all packages except web B) Creates a sparse monorepo with web + its dependencies C) Removes unused dependencies D) Minifies the web app
**Answer:** B
**Why:** `turbo prune` creates an `out/` directory containing only the target package and its transitive dependencies. Essential for minimal Docker builds.

### Q34
**Question:** You want to share Zod validation schemas between your Next.js app and Express API. What's the recommended package structure?
**Type:** Scenario-based
**Answer:** Create `packages/validation` with Zod schemas. Both `apps/web` and `apps/api` depend on it. Use JIT pattern (export raw TS) since both consumers have TS compilation.
**Why:** Validation schemas are runtime code shared between frontend and backend. Zod schemas provide both types AND runtime validation, making them ideal for shared packages.

### Q35
**Question:** What is the `packageManager` field in root package.json?
**Type:** Fill in the blank
**Answer:** Declares which package manager and version the project uses (e.g., `"packageManager": "pnpm@9.0.0"`). Corepack uses this to auto-install the correct version.
**Why:** Ensures all developers and CI use the same package manager version, preventing "works on my machine" issues.

### Q36
**Question:** True or False: Turborepo can cache the `dev` task.
**Type:** True/False
**Answer:** False (and you shouldn't)
**Why:** `dev` is a long-running persistent process. Caching it makes no sense. In turbo.json, set `"cache": false, "persistent": true`.

### Q37
**Question:** What happens if two packages in a monorepo depend on different major versions of `lodash`?
**Type:** Scenario-based
**Answer:** pnpm will install both versions, isolating them. Each package gets its declared version. However, this increases `node_modules` size and can cause subtle issues if lodash instances are shared across package boundaries.
**Why:** pnpm's strict isolation handles this correctly, but it's a smell. Prefer a single version policy for shared dependencies.

### Q38
**Question:** What is "affected analysis" in monorepo CI?
**Type:** Single choice
**Options:** A) Analyzing code quality B) Determining which packages changed and their dependents C) Checking for security vulnerabilities D) Measuring build performance
**Answer:** B
**Why:** Affected analysis compares the current state with a baseline (e.g., main branch) to identify changed packages and everything downstream. Only those packages need building/testing.

### Q39
**Question:** How do you run a script in ALL packages matching a pattern?
**Type:** Code
**Answer:** `pnpm --filter "./packages/**" build` or `pnpm --filter "@acme/*" build`
**Why:** pnpm's `--filter` supports glob patterns for both directory paths and package names.

### Q40
**Question:** True or False: Internal packages with `"private": true` can still be imported by other workspace packages.
**Type:** True/False
**Answer:** True
**Why:** `"private": true` only prevents npm publish. Workspace linking works regardless. The package is accessible to any workspace package that declares it as a dependency.

---

## Senior / Expert (20 Questions)

### Q41
**Question:** Your Turborepo remote cache hit rate dropped from 85% to 30% after a CI change. What should you investigate?
**Type:** Scenario-based
**Answer:** Check: (1) `globalDependencies` in turbo.json — did a new file get added? (2) Environment variables included in hash — did CI environment change? (3) Node.js version change. (4) OS/architecture change in CI runners. (5) New `inputs` glob matching too many files.
**Why:** Cache keys include source hashes, env vars, and global deps. Any change to these invalidates caches. Use `turbo build --summarize` to compare cache keys between runs.

### Q42
**Question:** You have 200 packages. TypeScript language server is extremely slow. What architectural changes can improve IDE performance?
**Type:** Scenario-based
**Answer:** (1) Use TypeScript project references with composite builds. (2) Reduce unnecessary type-checking scope with `references` in tsconfig. (3) Use `"disableSourceOfProjectReferenceRedirect": true` for built packages. (4) Consider splitting the monorepo into multiple tsconfig solutions. (5) Exclude test files and build outputs from TS project scope.
**Why:** TS language server loads all referenced projects. Project references enable incremental type-checking and limit the scope of what the language server loads.

### Q43
**Question:** A team wants to extract their packages from the monorepo into a separate repo. How should you handle this?
**Type:** Scenario-based
**Answer:** (1) Identify all dependencies of the packages to extract. (2) Check if other packages depend on them. (3) If they have dependents, publish to a private registry first, then update consumers. (4) Use `git filter-repo` to preserve history. (5) Set up CI in the new repo. (6) Add the published packages to the monorepo's dependencies. (7) Gradual migration with a deprecation period.
**Why:** Extraction is expensive. Consider whether the pain of the monorepo is worse than the pain of cross-repo coordination. Often the answer is to fix governance, not split repos.

### Q44
**Question:** True or False: Fine-grained (file-level) caching is always better than coarse-grained (package-level) caching.
**Type:** True/False
**Answer:** False
**Why:** Fine-grained caching (Bazel-style) has higher cache management overhead and complexity. For most JS/TS monorepos, package-level caching (Turborepo/Nx) provides 80% of the benefit with 20% of the complexity. Fine-grained only pays off at massive scale (1000+ packages).

### Q45
**Question:** How does the "diamond dependency problem" manifest in monorepo builds?
**Type:** Fill in the blank
**Answer:** When package A depends on B and C, and both B and C depend on D, D might be built with different configurations or contexts for B vs C, causing inconsistencies.
**Why:** Build systems must ensure D is built once with consistent inputs. Turborepo handles this via content hashing — same inputs always produce the same hash, so D builds once.

### Q46
**Question:** Your monorepo has a `@acme/config` package that every package depends on. Changing one line in config rebuilds all 100 packages. How do you fix this?
**Type:** Scenario-based
**Answer:** (1) Split `@acme/config` into focused packages: `config-ts`, `config-eslint`, `config-prettier`, `config-test`. (2) Each package depends only on the configs it needs. (3) A TS change only rebuilds packages using TS config. (4) Consider making config packages have NO build step (JIT) so they don't create cache invalidation cascades.
**Why:** God packages are the #1 cause of poor cache hit rates. Splitting by concern reduces the blast radius of changes.

### Q47
**Question:** What's the difference between Turborepo's `inputs` and `globalDependencies`?
**Type:** Matching
**Answer:**
- `inputs`: Per-task file globs that determine the cache key for THAT task in THAT package
- `globalDependencies`: Files that, when changed, invalidate ALL task caches across ALL packages

**Why:** `globalDependencies` is for truly global config (root `.env`, `turbo.json`). Use `inputs` to narrow what each task considers, improving cache hit rates.

### Q48
**Question:** You need to deploy 5 apps from a monorepo. One app's deployment fails. What's your rollback strategy?
**Type:** Scenario-based
**Answer:** (1) Each app should be independently deployable with its own rollback. (2) Shared package versions should be pinned at build time, not runtime. (3) Use blue-green or canary deployments per app. (4) Never roll back a shared package version — roll forward with a fix. (5) Keep deployment artifacts (Docker images, build outputs) tagged with git SHA.
**Why:** Independent deployability is critical. If apps are coupled in deployment, a failure in one blocks all. Design for independent rollback from day one.

### Q49
**Question:** How do you handle non-deterministic builds that poison the remote cache?
**Type:** Scenario-based
**Answer:** (1) Identify non-determinism: timestamps in output, random hashes, environment-specific paths. (2) Strip timestamps from build outputs. (3) Use `outputs` in turbo.json to exclude non-deterministic files. (4) Ensure build tools produce deterministic output (e.g., sorted imports, stable chunk hashes). (5) Use `TURBO_HASH` env var for debugging.
**Why:** Non-deterministic builds produce different outputs for the same inputs, meaning cache hits restore incorrect artifacts. This causes subtle, hard-to-debug production bugs.

### Q50
**Question:** What is "remote execution" and how does it differ from "remote caching"?
**Type:** Single choice
**Options:** A) They're the same thing B) Remote caching stores results; remote execution runs builds on remote machines C) Remote execution is faster D) Remote caching requires Bazel
**Answer:** B
**Why:** Remote caching: "I've seen these inputs before, here's the output." Remote execution (Bazel RBE): "Run this build action on a remote machine, send back results." Remote execution enables true distributed builds; caching only skips already-done work.

### Q51
**Question:** You're setting up a monorepo with Next.js (Vercel), Astro (Cloudflare Pages), and a Cloudflare Worker. What are the deployment challenges?
**Type:** Scenario-based
**Answer:** (1) Each app deploys to a different platform with different build systems. (2) Vercel auto-detects Turborepo but builds from repo root. (3) Cloudflare Pages/Workers use `wrangler` with different build configs. (4) Shared packages must be built before each app's deployment build. (5) Need to configure each platform's root directory and build commands correctly. (6) Environment variables differ per platform.
**Why:** Multi-platform deployment is the hardest operational challenge in monorepos. Each platform has different assumptions about repo structure and build process.

### Q52
**Question:** True or False: TypeScript project references and Turborepo serve the same purpose and you only need one.
**Type:** True/False
**Answer:** False
**Why:** They complement each other. TS project references enable incremental TYPE-CHECKING (compile-time). Turborepo enables incremental TASK EXECUTION (build, test, lint). Use both: TS references for fast type-checking, Turborepo for fast builds.

### Q53
**Question:** How should you handle database migrations in a monorepo with multiple services sharing the same database?
**Type:** Scenario-based
**Answer:** (1) Create a dedicated `packages/db` or `packages/migrations` package. (2) Migrations run independently of app deployments. (3) Use forward-compatible migrations (additive only). (4) Never couple migration execution to app deployment. (5) Consider separate CI job for migrations with its own approval gate.
**Why:** Database migrations that are coupled to app deployments create tight coupling between services. A failed migration shouldn't prevent unrelated apps from deploying.

### Q54
**Question:** What is the "publish from source" pattern and when should you use it?
**Type:** Fill in the blank
**Answer:** Publishing npm packages with TypeScript source files instead of compiled JavaScript. Consumers compile the source themselves. Used for internal packages in monorepos where all consumers have TS compilation.
**Why:** Eliminates the build step for internal packages, dramatically simplifying the development workflow. Not suitable for packages published to public npm (consumers expect compiled JS).

### Q55
**Question:** Your monorepo's `pnpm-lock.yaml` has constant merge conflicts. What strategies can reduce this?
**Type:** Scenario-based
**Answer:** (1) Use `pnpm install --merge-git-branch-lockfiles` in CI. (2) Reduce frequency of dependency additions. (3) Batch dependency updates with Renovate grouping. (4) Use git rerere to auto-resolve repeated conflicts. (5) Consider lock file maintenance bot that auto-resolves conflicts.
**Why:** Lock file conflicts are the #1 git workflow pain in monorepos. They're auto-generated, so manual resolution is tedious and error-prone.

### Q56
**Question:** How do you implement "package graduation" — moving a package from internal to published?
**Type:** Scenario-based
**Answer:** (1) Add build step if using JIT pattern. (2) Add `exports` with compiled entry points. (3) Remove `"private": true`. (4) Set up Changesets for versioning. (5) Add publishing CI job. (6) Update internal consumers to use the published version OR keep `workspace:*` for internal and publish for external. (7) Add documentation, README, CHANGELOG.
**Why:** Graduation is a significant lifecycle event. The package now has external consumers and needs stability guarantees, versioning, and documentation.

### Q57
**Question:** What's the impact of having 50 internal packages with build steps vs 50 JIT packages on CI performance?
**Type:** Scenario-based
**Answer:** 50 built packages: CI must execute 50 build tasks in topological order. Even with caching, cache misses cascade. 50 JIT packages: Only app builds run (e.g., 3 apps). Dramatically fewer tasks. CI is 5-10x faster for the common case.
**Why:** JIT eliminates O(n) package builds. The trade-off is that app build times increase slightly (compiling more source), but this is usually dwarfed by the savings from eliminated package builds.

### Q58
**Question:** How should you implement feature flags in a monorepo with multiple apps?
**Type:** Scenario-based
**Answer:** Create `packages/feature-flags` with: (1) Type-safe flag definitions shared across apps. (2) Runtime evaluation (LaunchDarkly, Unleash, or custom). (3) Build-time flags via environment variables for dead code elimination. (4) Per-app flag overrides. (5) Flag cleanup process to remove stale flags.
**Why:** Feature flags in monorepos need to be shared (same flag in web + worker) but independently configurable (different defaults per environment/app).

### Q59
**Question:** At what scale would you recommend migrating from Turborepo to Nx, and from Nx to Bazel?
**Type:** Scenario-based
**Answer:** Turborepo → Nx: When you need module boundary enforcement, code generators, or dependency graph visualization (~30-50 packages, 10+ devs). Nx → Bazel: When you have multi-language builds, need hermetic reproducibility, or have 100+ engineers and 1000+ build targets. Most JS/TS monorepos never need Bazel.
**Why:** Each tool has a scaling sweet spot. Migrating too early adds unnecessary complexity. Migrating too late causes pain. Measure CI times and cache hit rates to know when you've outgrown a tool.

### Q60
**Question:** Design an internal developer platform for a 50-package monorepo. What components would it include?
**Type:** Open-ended
**Answer:** (1) CLI tool (`@acme/cli`): scaffold packages, run common workflows. (2) Package template generator: consistent new package structure. (3) Dependency graph dashboard: visualize and monitor. (4) Build performance tracker: CI times, cache hit rates over time. (5) Automated migration scripts: bulk codemod across packages. (6) Shared CI workflows: reusable GitHub Actions. (7) Documentation generator: auto-generate docs from TSDoc. (8) Health checks: lint for circular deps, unused packages, stale configs.
**Why:** At scale, the monorepo IS a product. DX engineers are product engineers whose users are other developers. The platform reduces friction and enforces consistency.

---

# 9. Personalized Recommendations

## For Your Stack: React + Next.js + Astro + TypeScript

### Most Useful Patterns

1. **Shared UI library** — Your #1 win. React components shared between Next.js and Astro.
2. **Shared types** — TypeScript types shared between frontend and any BFF/Worker.
3. **Shared config** — tsconfig, ESLint, Prettier configs shared across all packages.
4. **Shared hooks** — React hooks used in multiple apps.
5. **API client package** — Typed fetch wrappers shared between Next.js server components and Cloudflare Workers.

### Learn First

1. pnpm workspaces (day 1-3)
2. Internal packages with JIT pattern (day 4-7)
3. Turborepo basics (day 8-10)
4. Shared configs (day 11-14)
5. CI with affected builds (day 15-20)
6. Remote caching (day 21-25)
7. Docker integration with turbo prune (day 26-30)

### Best Tooling Fit

| Tool | Recommendation |
|------|---------------|
| **Package manager** | pnpm (strict, fast, disk-efficient) |
| **Build orchestrator** | Turborepo (simple, Vercel-native, Rust-fast) |
| **Bundler for packages** | tsup (when build step needed) or none (JIT) |
| **Framework** | Next.js + Astro (already your stack) |
| **Versioning** | Changesets (if publishing externally) |
| **CI** | GitHub Actions with turbo affected filtering |

### Common Mistakes Frontend Engineers Make

1. **Over-packaging** — Creating a package for every 3 functions. Package overhead is real.
2. **Ignoring the dependency graph** — Adding `@acme/utils` as a dep everywhere, creating a god package.
3. **Building internal packages unnecessarily** — JIT is simpler and faster for most cases.
4. **Not using `workspace:*`** — Hardcoding versions for internal packages.
5. **Sharing too much** — Not everything should be shared. Duplication is sometimes better than coupling.
6. **No CI optimization** — Running all tests on every PR in a 20-package monorepo.
7. **Mixing concerns in shared packages** — UI components + API logic + utils all in `@acme/shared`.

### 30-Day Learning Plan

| Week | Focus | Milestone |
|------|-------|-----------|
| **Week 1** | Setup pnpm workspace + 2 apps + 1 shared package. Configure Turborepo. | Working monorepo with `turbo build` and `turbo dev` |
| **Week 2** | Create shared `ui`, `utils`, `config-ts`, `config-eslint` packages. Use JIT pattern. | 4+ internal packages consumed by apps |
| **Week 3** | Set up CI with GitHub Actions. Implement affected builds. Enable remote caching. | CI under 3 minutes for typical PRs |
| **Week 4** | Docker builds with `turbo prune`. Add Cloudflare Worker sharing types with web. Deploy multi-app. | Full deployment pipeline for 2+ apps across 2+ platforms |

---

# 10. Official Documentation & Reference Links

## Beginner

- [Turborepo — Getting Started](https://turbo.build/repo/docs)
- [pnpm Workspaces](https://pnpm.io/workspaces)
- [Yarn Workspaces](https://yarnpkg.com/features/workspaces)
- [npm Workspaces](https://docs.npmjs.com/cli/using-npm/workspaces)
- [TypeScript Project References](https://www.typescriptlang.org/docs/handbook/project-references.html)

## Intermediate

- [Turborepo — Crafting Your Repository](https://turbo.build/repo/docs/crafting-your-repository)
- [Turborepo — Task Dependencies](https://turbo.build/repo/docs/crafting-your-repository/configuring-tasks)
- [Turborepo — Caching](https://turbo.build/repo/docs/crafting-your-repository/caching)
- [Nx — Getting Started](https://nx.dev/getting-started/intro)
- [Nx — Mental Model](https://nx.dev/concepts/mental-model)
- [Changesets Documentation](https://github.com/changesets/changesets)

## Advanced

- [Turborepo — Remote Caching](https://turbo.build/repo/docs/crafting-your-repository/remote-caching)
- [Turborepo — Deploying with Docker](https://turbo.build/repo/docs/guides/tools/docker)
- [Turborepo — GitHub Actions](https://turbo.build/repo/docs/guides/ci-vendors/github-actions)
- [Nx — CI Setup](https://nx.dev/ci/intro/ci-with-nx)
- [Nx — Module Boundary Rules](https://nx.dev/features/enforce-module-boundaries)
- [Rush — Getting Started](https://rushjs.io/pages/intro/welcome/)
- [Lage — Microsoft](https://github.com/microsoft/lage)

## Expert / Build Systems

- [Bazel — Getting Started](https://bazel.build/start)
- [Bazel — Remote Execution](https://bazel.build/remote/rbe)
- [Build Systems à la Carte (Paper)](https://www.microsoft.com/en-us/research/publication/build-systems-a-la-carte/)
- [Please Build System](https://please.build/)
- [Buck2 — Meta](https://buck2.build/)
- [Pants Build](https://www.pantsbuild.org/)
- [Turborepo Architecture Blog](https://turbo.build/blog)
- [Nx Blog — Enterprise Monorepos](https://blog.nrwl.io/)

## Engineering Blog Posts & Case Studies

- [Vercel — Why Turborepo](https://vercel.com/blog/turborepo)
- [Google — Why Google Stores Billions of Lines in a Single Repository](https://research.google/pubs/pub45424/)
- [Microsoft — Scaling Git at Microsoft](https://devblogs.microsoft.com/devops/the-largest-git-repo-on-the-planet/)
- [Airbnb — Monorepo Migration](https://medium.com/airbnb-engineering)
- [Shopify — Monorepo at Scale](https://shopify.engineering/)

## Open-Source Monorepo Examples

- [Turborepo Examples](https://github.com/vercel/turborepo/tree/main/examples)
- [Nx Examples](https://github.com/nrwl/nx-examples)
- [t3-oss/create-t3-turbo](https://github.com/t3-oss/create-t3-turbo)
- [shadcn/ui](https://github.com/shadcn-ui/ui) — Real-world monorepo with design system
- [Calcom](https://github.com/calcom/cal.com) — Production Next.js monorepo

---

# 11. Advanced Engineering Topics

## Build Graph Theory

A monorepo build is a computation over a **directed acyclic graph (DAG)**:
- **Nodes** = tasks (build:ui, test:web, lint:utils)
- **Edges** = dependencies between tasks
- **Execution** = topological sort with maximum parallelism

**Critical path** = the longest chain of sequential dependencies. This determines your minimum possible build time regardless of parallelism.

```
Critical path: types(2s) → utils(3s) → ui(5s) → web(8s) = 18s minimum
                                                 ↗
                            docs(4s) ────────────  (parallel, not on critical path)
```

**Optimization strategy:** Reduce the length of the critical path. Split large packages, cache aggressively, parallelize independent tasks.

## Incremental Computation

Build systems implement a form of **incremental computation** — only recompute what changed.

Three levels:
1. **Dirty bit** — Rebuild if any input changed (coarse, Turborepo default)
2. **Trace-based** — Track which inputs each output depends on, rebuild selectively (Nx)
3. **Demand-driven** — Only compute what's requested, memoize results (Bazel/Salsa)

## Distributed Caching

Cache storage options:
| Backend | Pros | Cons |
|---------|------|------|
| Vercel Remote Cache | Zero config with Turborepo | Vercel-only |
| Nx Cloud | Feature-rich, DTE | Nx ecosystem |
| S3/R2/GCS | Full control, cheap | Self-managed |
| GitHub Actions Cache | Free for GH users | Limited size (10GB) |

**Cache key design matters.** Include: source hash, dependency hashes, env vars, tool versions. Exclude: timestamps, absolute paths, non-deterministic values.

## Multi-Runtime Monorepos

Sharing code between Node.js, Cloudflare Workers, Deno, and browsers:

```
packages/
  core/           ← Pure functions, no runtime APIs
  node-utils/     ← Node.js-specific (fs, path, etc.)
  edge-utils/     ← Edge-runtime-specific (waitUntil, etc.)
  browser-utils/  ← Browser-specific (DOM, window, etc.)
```

**Rule:** Shared packages consumed by multiple runtimes MUST use only APIs available in ALL target runtimes. Use conditional exports for runtime-specific code:

```jsonc
{
  "exports": {
    ".": {
      "worker": "./src/edge.ts",
      "node": "./src/node.ts",
      "default": "./src/browser.ts"
    }
  }
}
```

## Hybrid Monorepo/Polyrepo Architecture

Not everything needs to be in the monorepo:

| In the monorepo | In separate repos |
|-----------------|------------------|
| Apps sharing significant code | Isolated microservices |
| Shared libraries | Third-party forks |
| Configs and tooling | Infrastructure (Terraform) |
| Design system | Mobile apps (different build system) |

**Pattern:** Monorepo publishes packages to private registry. Separate repos consume them as npm dependencies. Best of both worlds when organizations are too large for a single repo.

## DX Platform Engineering

The monorepo is a product. The DX team is the product team.

**Platform components:**
1. **Package scaffolder** — `pnpm create @acme/package` generates new packages with templates
2. **Migration runner** — Automated codemods for bulk changes (TS version upgrade, ESLint rule addition)
3. **Build dashboard** — Track CI times, cache hit rates, package count, dependency graph health
4. **Doctor CLI** — `pnpm acme doctor` checks for common issues: circular deps, phantom deps, stale configs
5. **Golden path docs** — "How to create a new app," "How to share code," "How to deploy"

---

# Summary

## Key Takeaways

1. A monorepo is a **structured, build-optimized** multi-project repository — not just "one repo."
2. The **dependency graph** is the foundation. Everything (builds, caching, CI) flows from it.
3. **Start simple:** pnpm workspaces + Turborepo + JIT internal packages.
4. **Cache aggressively:** Remote caching reduces CI by 40-80%.
5. **Filter ruthlessly:** Only build/test what's affected by changes.
6. **Package boundaries matter:** God packages destroy cache hit rates.
7. **JIT > built packages** for internal consumption in most cases.
8. **Governance scales with the org:** Process matters as much as tooling.

## Next Steps

1. Set up your first monorepo with pnpm + Turborepo
2. Create `@acme/ui` and share it between Next.js and Astro apps
3. Configure CI with affected builds and remote caching
4. Learn `turbo prune` for Docker deployments
5. Explore Nx when you need module boundary enforcement
6. Study Bazel when you're curious about build systems theory

## Advanced Topics to Continue

- Bazel and hermetic builds
- Module Federation with monorepos
- Micro-frontend architecture patterns
- Custom Turborepo transforms
- Build systems à la carte (academic foundations)
- Remote build execution
- Monorepo observability and metrics
- Internal developer platform design
