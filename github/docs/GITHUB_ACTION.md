# GitHub Actions — Complete Deep-Dive Engineering Guide

> For a frontend engineer (React / Next.js / Astro / TypeScript) moving toward DevOps, CI/CD, automation, release engineering, and platform engineering.

---

## Table of Contents

- [1. Big Picture](#1-big-picture)
- [2. Learning Roadmap by Skill Level](#2-learning-roadmap-by-skill-level)
- [3. Setup Guide](#3-setup-guide)
- [4. Cheatsheet](#4-cheatsheet)
- [5. Real-World Engineering Mindset](#5-real-world-engineering-mindset)
- [6. Brainstorm / Open Questions](#6-brainstorm--open-questions)
- [7. Practice Questions](#7-practice-questions)
- [8. Personalized Recommendations](#8-personalized-recommendations)
- [Summary, Next Steps, and Advanced Topics](#summary-next-steps-and-advanced-topics)

---

## 1. Big Picture

### 1.1 What GitHub Actions Are

GitHub Actions is an event-driven automation engine built directly into GitHub. It executes arbitrary code — your code, community-maintained actions, or shell scripts — in response to events that happen inside or around a repository.

You already know this pattern. When you run `npm run dev`, Vite watches files and re-renders on change. GitHub Actions does the same thing, but the "watcher" is GitHub itself, the "files" are Git events (pushes, PRs, tags, schedules, manual triggers), and the "render" is a pipeline of jobs that lint, test, build, deploy, notify, scan, release, or do anything a shell can do.

It is **not** just CI. It is a general-purpose workflow automation platform that happens to be excellent at CI/CD.

### 1.2 How GitHub Actions Differ From Things You Already Know

| Tool / Pattern | What it does | Where it runs | Key difference from GitHub Actions |
|---|---|---|---|
| **Local scripts** (`./deploy.sh`) | One-off automation | Your laptop | Not shared, not auditable, not triggered by Git events, not reproducible across machines |
| **npm scripts** (`npm run build`) | Project commands | Wherever you run them | Single-process, single-machine; Actions orchestrates many jobs across isolated VMs |
| **Husky** (Git hooks) | Pre-commit / pre-push checks | Developer machine | Runs *before* push on *your* machine; Actions runs *after* push on *GitHub's* machines; Husky can be skipped with `--no-verify` |
| **CI/CD tools** (Jenkins, CircleCI) | Automated pipelines | Their own infrastructure | Actions is natively integrated into GitHub — no separate platform to manage, no webhook glue |
| **Cron jobs** | Time-based scheduling | A server you maintain | Actions supports `schedule` triggers, but also reacts to every Git event; no server to maintain |
| **Traditional deployment pipelines** | Stage-gated release flows | Centralized infra | Actions is decentralized (per-repo YAML), composable (reusable workflows), and version-controlled alongside code |

**The React/Next.js analogy:**

Think of your local `npm run dev` → `npm run build` → `npm run start` cycle. Now imagine GitHub automatically runs that cycle every time anyone on your team pushes code, but on a fresh clean machine, with results posted to the PR, and the build output deployed to a URL — all without you touching a terminal. That is GitHub Actions.

### 1.3 Core Concepts

#### Workflow

A YAML file in `.github/workflows/` that defines an automation pipeline. One repository can have many workflows. Each workflow responds to one or more events.

**Analogy:** A workflow is like a `next.config.js` — it declares how the system should behave, and the platform interprets it.

#### Event

Something that triggers a workflow. Examples: `push`, `pull_request`, `release`, `schedule`, `workflow_dispatch` (manual button), `workflow_call` (called by another workflow).

**Analogy:** Events are like DOM events. A `push` is like an `onClick` — when it fires, registered handlers (workflows) run.

#### Job

A unit of work that runs on a single runner. Jobs within a workflow run in parallel by default, unless you declare dependencies with `needs`.

**Analogy:** Jobs are like independent React components — they render (execute) independently, but can pass data to each other.

#### Step

A single command or action within a job. Steps run sequentially, top to bottom.

**Analogy:** Steps are like lines inside a `useEffect` — they execute in order, sharing the same context (the runner's filesystem and environment).

#### Runner

The machine (VM) that executes a job. GitHub provides hosted runners (Ubuntu, Windows, macOS) or you can use self-hosted runners.

**Analogy:** A runner is like a fresh `npx create-next-app` environment — clean, isolated, and disposable. Every job starts on a blank machine.

#### Action

A reusable, parameterized unit of workflow logic. Published to the GitHub Marketplace or defined locally. Called with `uses:`.

**Analogy:** An action is like an npm package for your pipeline — someone else wrote and tested it, you import it and pass props (inputs).

#### Matrix

A strategy that fans a single job definition into many parallel runs by varying parameters (Node versions, OS, config flags).

**Analogy:** Like rendering a component list with `.map()` — same template, different data per instance.

#### Artifact

A file or directory produced by a workflow run that you want to persist — build outputs, test reports, binaries. Uploaded with `actions/upload-artifact`, downloaded with `actions/download-artifact`.

**Analogy:** Like the `out/` or `dist/` directory from `next build`, but stored on GitHub for later jobs or manual download.

#### Cache

Stored dependency data (like `node_modules` or the pnpm store) that is restored on subsequent runs to skip expensive installs. Keyed by a hash of the lockfile.

**Analogy:** Like the `.next/cache` folder that makes rebuilds faster — but across CI runs.

#### Environment

A named deployment target (e.g., `staging`, `production`) with configurable protection rules — required reviewers, wait timers, branch restrictions, scoped secrets.

**Analogy:** Like Vercel's "Preview" vs. "Production" distinction, but you define the rules yourself.

#### Secret

An encrypted value stored at the repository, environment, or organization level. Accessed via `${{ secrets.NAME }}`. Masked in logs automatically.

**Analogy:** Like environment variables in Vercel or Cloudflare dashboards, but scoped to your pipeline.

### 1.4 The Lifecycle: git push → deployment

```text
┌─────────────────────────────────────────────────────────────────────────┐
│ DEVELOPER                                                               │
│                                                                         │
│  git add . → git commit → git push origin main                         │
│                                                                         │
└────────────────────────────┬────────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ GITHUB EVENT SYSTEM                                                     │
│                                                                         │
│  Event emitted: push (ref: refs/heads/main)                            │
│  GitHub scans .github/workflows/*.yml for matching triggers            │
│                                                                         │
└────────────────────────────┬────────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ WORKFLOW EXECUTION                                                      │
│                                                                         │
│  ci.yml matched on: push.branches: [main]                              │
│                                                                         │
│  ┌──────────┐   ┌──────────┐                                           │
│  │ Job: lint │   │ Job: test │  ← parallel by default                  │
│  └─────┬────┘   └─────┬────┘                                           │
│        │               │                                                │
│        └───────┬───────┘                                                │
│                ▼                                                        │
│        ┌──────────────┐                                                 │
│        │  Job: build   │  ← needs: [lint, test]                        │
│        └──────┬───────┘                                                 │
│               ▼                                                        │
│        ┌──────────────┐                                                 │
│        │  Job: deploy  │  ← needs: build, environment: production      │
│        └──────────────┘                                                 │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ DEPLOYMENT TARGET                                                       │
│                                                                         │
│  Vercel / Cloudflare Pages / AWS S3 / Docker registry / etc.           │
│  Status check reported back to GitHub                                  │
│  Deployment URL linked in PR or commit                                 │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### 1.5 Comparison With Other CI/CD Systems

| Dimension | GitHub Actions | GitLab CI/CD | Jenkins | CircleCI | Azure DevOps | Vercel deployment |
|---|---|---|---|---|---|---|
| **Config format** | YAML per repo | `.gitlab-ci.yml` | Jenkinsfile (Groovy) or UI | `.circleci/config.yml` | `azure-pipelines.yml` | Zero-config / `vercel.json` |
| **Where it runs** | GitHub-hosted VMs or self-hosted | GitLab runners | Self-hosted (always) | CircleCI cloud or self-hosted | Azure-hosted or self-hosted | Vercel's edge infra |
| **Native SCM** | GitHub | GitLab | Any (via plugins) | GitHub, Bitbucket | Azure Repos, GitHub | GitHub, GitLab, Bitbucket |
| **Marketplace** | 20,000+ actions | Templates | 1,800+ plugins | Orbs | Extensions | N/A |
| **Pricing model** | Free minutes + per-minute overage | Free tier + per-minute | Free (self-host cost) | Free tier + per-minute | Free tier + per-minute | Free tier + per-seat |
| **Best for** | GitHub-centric teams of any size | GitLab-centric teams | Heavy customization / legacy | Fast CI for product teams | Microsoft-centric enterprise | Frontend-first apps |
| **Biggest weakness** | YAML complexity at scale | Ecosystem size | Maintenance burden | Separate platform | Heavier UX | Not general-purpose |
| **Learning curve** | Moderate | Moderate | High | Moderate | Moderate-High | Very Low |

**Key insight for a frontend engineer:** Vercel gives you the *best DX* for deploying Next.js — zero config, instant previews, automatic production. GitHub Actions gives you the *most control* — you decide every step, can add security scanning, multi-platform testing, release gating, and deployment to any target. Most real teams use both: Vercel for deployment, Actions for everything else (lint, test, release, automation).

### 1.6 Mental Model Diagram

```text
┌────────────────────────────────────────────────────┐
│                  YOUR REPOSITORY                    │
│                                                    │
│  src/  package.json  .github/workflows/ci.yml      │
│                                                    │
└────────────────────────┬───────────────────────────┘
                         │ git push / PR / tag / schedule / manual
                         ▼
┌────────────────────────────────────────────────────┐
│              GITHUB EVENT SYSTEM                    │
│                                                    │
│  Matches event → selects workflow(s)               │
│                                                    │
└────────────────────────┬───────────────────────────┘
                         │
           ┌─────────────┼─────────────┐
           ▼             ▼             ▼
      ┌─────────┐  ┌─────────┐  ┌─────────┐
      │ Job A   │  │ Job B   │  │ Job C   │   ← each on its own runner
      │ (lint)  │  │ (test)  │  │ (types) │
      └────┬────┘  └────┬────┘  └────┬────┘
           │             │             │
           └──────┬──────┘─────────────┘
                  ▼
            ┌───────────┐
            │  Job D    │   ← needs: [A, B, C]
            │  (build)  │
            └─────┬─────┘
                  │ upload artifact
                  ▼
            ┌───────────┐
            │  Job E    │   ← needs: D, environment: production
            │  (deploy) │
            └───────────┘
                  │
                  ▼
         Deploy to target
```

---

## 2. Learning Roadmap by Skill Level

### Level 1 — Newbie

**Goal:** Create your first working workflow and understand every part of it.

#### What a workflow file is

A workflow file is a YAML document that lives in `.github/workflows/`. It tells GitHub: "When *this event* happens, run *these jobs* on *these machines*."

You already manage config files — `next.config.js`, `tsconfig.json`, `tailwind.config.ts`. A workflow file is another config file, but for your automation pipeline instead of your app.

#### YAML basics you need

```yaml
# Scalars (strings, numbers, booleans)
name: CI
timeout-minutes: 10

# Mappings (key-value pairs — like JS objects)
env:
  NODE_ENV: production
  CI: true

# Sequences (lists — like JS arrays)
branches:
  - main
  - develop

# Multi-line strings
run: |
  echo "Line 1"
  echo "Line 2"

# Inline flow syntax
branches: [main, develop]
```

**Critical YAML rules:**
- Indentation is **spaces only** — never tabs.
- Indentation level defines structure (like Python).
- Colons need a space after them: `key: value` not `key:value`.
- The values `true`, `false`, `on`, `off`, `yes`, `no` are booleans in YAML — quote them if you mean strings.

#### Where workflows live

```text
your-repo/
└── .github/
    └── workflows/
        ├── ci.yml          ← runs on push and PR
        ├── deploy.yml      ← runs on merge to main
        └── nightly.yml     ← runs on schedule
```

GitHub only reads workflow files from `.github/workflows/`. The filenames can be anything ending in `.yml` or `.yaml`.

#### First workflow — the complete "Hello World"

```yaml
# .github/workflows/hello.yml
name: Hello World

on:
  push:
    branches: [main]

jobs:
  greet:
    runs-on: ubuntu-latest
    steps:
      - name: Say hello
        run: echo "Hello from GitHub Actions!"

      - name: Show environment
        run: |
          echo "Runner OS: ${{ runner.os }}"
          echo "Event: ${{ github.event_name }}"
          echo "Branch: ${{ github.ref }}"
          echo "SHA: ${{ github.sha }}"
```

#### First real workflow — lint + test + build

```yaml
# .github/workflows/ci.yml
name: CI

on:
  push:
    branches: [main]
  pull_request:

jobs:
  ci:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: 20
          cache: npm

      - name: Install dependencies
        run: npm ci

      - name: Lint
        run: npm run lint

      - name: Type check
        run: npm run typecheck

      - name: Test
        run: npm test

      - name: Build
        run: npm run build
```

**Why `npm ci` instead of `npm install`?**

`npm ci` does a clean install from the lockfile — faster, deterministic, and will fail if `package-lock.json` is out of sync. This is what you always want in CI. `npm install` can modify the lockfile, introducing drift.

#### How to debug failures

1. **Read the failing step's logs.** Click the red X → click the failing job → expand the failing step. The error message is usually right there.
2. **Check the YAML syntax.** GitHub shows a parse error banner if your YAML is malformed. Use a local YAML linter or VS Code's YAML extension.
3. **Reproduce locally.** Run the exact same commands on your machine. If it works locally but fails in CI, the difference is usually: Node version, missing dependency, environment variable, or file path.
4. **Add debug output.**
   ```yaml
   - name: Debug info
     run: |
       node --version
       npm --version
       ls -la
       cat package.json
       echo "Event: ${{ toJSON(github.event) }}"
   ```
5. **Enable debug logging.** Re-run the workflow with "Enable debug logging" checked, or set the repository secret `ACTIONS_STEP_DEBUG` to `true`.
6. **Check the event payload.** Use `${{ toJSON(github.event) }}` to see exactly what data GitHub sent.

#### Common mistakes at this level

| Mistake | What happens | Fix |
|---|---|---|
| Tabs in YAML | Parse error | Use spaces (2-space indent recommended) |
| Missing `actions/checkout` | Commands fail — no source code | Always checkout first |
| Using `npm install` | Lockfile may change, non-deterministic | Use `npm ci` |
| Wrong Node version | Package incompatibilities | Match your local version |
| Typo in branch name | Workflow never triggers | Check `on.push.branches` carefully |
| Running in wrong directory | `command not found` or missing files | Use `working-directory:` if needed |
| Assuming env vars exist | Undefined variables, empty strings | Explicitly set `env:` or use `secrets` |

#### 5 small practice exercises

1. **Print your toolchain:** Create a workflow that prints the Node.js version, npm version, and Git version on every push.
2. **Lint on PR:** Create a workflow that runs `npm run lint` only on pull requests.
3. **Multi-step build:** Create a workflow with separate steps for install, lint, test, and build.
4. **Break it intentionally:** Introduce a lint error, push it, and study the failure logs. Then fix it.
5. **Branch filtering:** Create a workflow that runs on pushes to `main` and `develop` but not other branches.

#### Level 1 success criteria

- [ ] Can create a `.github/workflows/ci.yml` from scratch.
- [ ] Can explain trigger, job, step, runner, and action.
- [ ] Can read failure logs and fix basic errors.
- [ ] Can explain why `npm ci` is used instead of `npm install`.

---

### Level 2 — Junior

**Goal:** Build workflows a team actually uses — multi-job, cached, conditional, with deployments.

#### Multiple jobs and dependencies

```yaml
name: CI

on:
  pull_request:
  push:
    branches: [main]

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: 20
          cache: npm
      - run: npm ci
      - run: npm run lint

  typecheck:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: 20
          cache: npm
      - run: npm ci
      - run: npm run typecheck

  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: 20
          cache: npm
      - run: npm ci
      - run: npm test -- --ci

  build:
    runs-on: ubuntu-latest
    needs: [lint, typecheck, test]    # ← waits for all three
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: 20
          cache: npm
      - run: npm ci
      - run: npm run build
      - uses: actions/upload-artifact@v4
        with:
          name: build-output
          path: dist/
          retention-days: 7
```

**Why separate jobs?** Faster feedback. If lint fails in 20 seconds, you know immediately — even if tests take 5 minutes. Each job runs on its own runner in parallel unless constrained by `needs`.

**Trade-off:** Each job does a fresh checkout and install. This costs time. Caching mitigates it. For very small projects, a single job may be faster end-to-end.

#### Matrix builds

```yaml
jobs:
  test:
    runs-on: ${{ matrix.os }}
    strategy:
      fail-fast: false          # ← don't cancel others if one fails
      matrix:
        os: [ubuntu-latest, macos-latest, windows-latest]
        node-version: [18, 20, 22]
        exclude:
          - os: macos-latest
            node-version: 18    # ← skip this combination
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: ${{ matrix.node-version }}
          cache: npm
      - run: npm ci
      - run: npm test
```

**When to use a matrix:** When you genuinely need cross-platform or cross-version confidence. For most frontend apps, a single OS and Node version is enough. Save matrices for libraries, packages, and tools.

#### Caching — npm, pnpm, and yarn

The `actions/setup-node` action has built-in caching:

```yaml
# npm
- uses: actions/setup-node@v4
  with:
    node-version: 20
    cache: npm           # ← caches based on package-lock.json hash

# pnpm
- uses: pnpm/action-setup@v4
  with:
    version: 9
- uses: actions/setup-node@v4
  with:
    node-version: 20
    cache: pnpm          # ← caches based on pnpm-lock.yaml hash

# yarn
- uses: actions/setup-node@v4
  with:
    node-version: 20
    cache: yarn           # ← caches based on yarn.lock hash
```

**What gets cached?** Not `node_modules` itself — the package manager's global cache directory. On cache hit, `npm ci` / `pnpm install` still runs but reads from local cache instead of the network.

**Advanced: manual caching with `actions/cache`:**

```yaml
- uses: actions/cache@v4
  with:
    path: |
      ~/.npm
      .next/cache
    key: ${{ runner.os }}-nextjs-${{ hashFiles('package-lock.json') }}-${{ hashFiles('**/*.ts', '**/*.tsx') }}
    restore-keys: |
      ${{ runner.os }}-nextjs-${{ hashFiles('package-lock.json') }}-
      ${{ runner.os }}-nextjs-
```

#### Environment variables and secrets

```yaml
# Workflow-level env
env:
  CI: true
  NODE_ENV: production

jobs:
  deploy:
    runs-on: ubuntu-latest
    env:
      DEPLOY_TARGET: staging       # ← job-level env
    steps:
      - name: Deploy
        env:
          API_TOKEN: ${{ secrets.API_TOKEN }}    # ← step-level, from secrets
          DEPLOY_URL: ${{ vars.DEPLOY_URL }}     # ← from repository variables
        run: |
          echo "Deploying to $DEPLOY_TARGET"
          ./deploy.sh
```

**Secret rules:**
- Secrets are encrypted at rest and masked in logs.
- They cannot be read back from the UI after creation.
- Use environment-scoped secrets for production credentials.
- Never echo secrets directly — GitHub masks them, but be careful with encoded/transformed values.

#### Conditional execution

```yaml
# Run only on main branch
- name: Deploy
  if: github.ref == 'refs/heads/main'
  run: npm run deploy

# Run only on PRs
- name: Preview
  if: github.event_name == 'pull_request'
  run: npm run build:preview

# Run only when a specific label is present
- name: Full test
  if: contains(github.event.pull_request.labels.*.name, 'full-test')
  run: npm run test:e2e

# Run even if a previous step failed
- name: Cleanup
  if: always()
  run: ./cleanup.sh

# Run only if previous steps succeeded (default behavior)
- name: Deploy
  if: success()
  run: npm run deploy

# Run only if a previous step failed
- name: Notify failure
  if: failure()
  run: curl -X POST $SLACK_WEBHOOK -d '{"text":"CI failed!"}'
```

#### Pull request workflows

PR workflows are your primary quality gate:

```yaml
name: PR Checks

on:
  pull_request:
    types: [opened, synchronize, reopened]

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: 20
          cache: npm
      - run: npm ci
      - run: npm run lint
      - run: npm run typecheck
      - run: npm test -- --ci
      - run: npm run build

  # Post build size as a PR comment
  bundle-size:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: 20
          cache: npm
      - run: npm ci
      - run: npm run build
      - uses: andresz1/size-limit-action@v1
        with:
          github_token: ${{ secrets.GITHUB_TOKEN }}
```

#### Deployment basics

```yaml
deploy:
  runs-on: ubuntu-latest
  needs: build
  if: github.ref == 'refs/heads/main'
  environment:
    name: production
    url: https://myapp.com
  steps:
    - uses: actions/download-artifact@v4
      with:
        name: build-output
    - name: Deploy to hosting
      env:
        DEPLOY_TOKEN: ${{ secrets.DEPLOY_TOKEN }}
      run: |
        npx wrangler pages deploy dist/ --project-name=my-site
```

#### 5 mini project ideas

1. **React CI with bundle size tracking:** Lint, test, build, and post bundle size diff as a PR comment.
2. **Next.js preview deployment:** On PR, build and deploy a preview to Vercel or Cloudflare Pages.
3. **Astro static site deployment:** Build and deploy Astro output to GitHub Pages on merge to main.
4. **Matrix test across Node versions:** Test a shared utility library across Node 18, 20, and 22.
5. **Automated dependency updates:** Configure Dependabot + auto-merge for patch updates that pass CI.

#### Common mistakes and anti-patterns

| Anti-pattern | Why it is bad | Better approach |
|---|---|---|
| One giant workflow for everything | Hard to read, slow feedback, hard to maintain | Split into focused workflows (ci.yml, deploy.yml, release.yml) |
| Duplicating YAML across repos | Drift, inconsistency, maintenance pain | Use reusable workflows or composite actions |
| Not caching dependencies | Slow installs on every run | Use built-in cache in `actions/setup-node` |
| Deploying from every branch | Broken previews, wasted resources | Deploy only from main or tagged releases |
| Hardcoding secrets in YAML | Security disaster | Use `secrets` context |
| Ignoring `needs` graph | Jobs run in wrong order or waste time | Design explicit dependency chains |
| Using `npm install` | Non-deterministic, modifies lockfile | Use `npm ci` |
| Not requiring CI checks for merge | Broken code lands in main | Set up branch protection with required status checks |

#### Level 2 success criteria

- [ ] Can structure multi-job workflows with `needs`.
- [ ] Can explain and configure caching.
- [ ] Can use matrix builds purposefully.
- [ ] Can use secrets and environment variables correctly.
- [ ] Can build a basic deploy pipeline with conditions.

---

### Level 3 — Senior

**Goal:** Build production-ready CI/CD — fast, secure, maintainable, with deployment safety.

#### Branch strategy integration

Map workflows to your Git strategy:

```text
Feature branch  → PR workflow: lint, test, typecheck, build, preview deploy
Main branch     → CI + deploy to staging (automatic)
Release tag     → Deploy to production (with approval)
Hotfix branch   → Fast-track CI + deploy to production
```

```yaml
on:
  pull_request:         # ← feature branches
  push:
    branches: [main]    # ← staging deploy trigger
    tags: ['v*']        # ← production deploy trigger
```

#### Monorepo workflows with path filters

```yaml
name: Frontend CI

on:
  push:
    paths:
      - 'packages/web/**'
      - 'packages/shared/**'
      - 'package.json'
      - 'pnpm-lock.yaml'
  pull_request:
    paths:
      - 'packages/web/**'
      - 'packages/shared/**'

jobs:
  web-ci:
    runs-on: ubuntu-latest
    defaults:
      run:
        working-directory: packages/web
    steps:
      - uses: actions/checkout@v4
      - uses: pnpm/action-setup@v4
        with:
          version: 9
      - uses: actions/setup-node@v4
        with:
          node-version: 20
          cache: pnpm
      - run: pnpm install --frozen-lockfile
      - run: pnpm run lint
      - run: pnpm run test
      - run: pnpm run build
```

**Advanced change detection:** For complex monorepos, path filters are too coarse. Use a change detection step:

```yaml
- uses: dorny/paths-filter@v3
  id: changes
  with:
    filters: |
      web:
        - 'packages/web/**'
        - 'packages/shared/**'
      api:
        - 'packages/api/**'
        - 'packages/shared/**'

- name: Run web tests
  if: steps.changes.outputs.web == 'true'
  run: pnpm --filter web test
```

#### Reusable workflows

Define once, call from many repos:

```yaml
# .github/workflows/reusable-ci.yml (in a shared repo)
name: Reusable CI

on:
  workflow_call:
    inputs:
      node-version:
        type: string
        default: '20'
      working-directory:
        type: string
        default: '.'
      package-manager:
        type: string
        default: 'npm'
    secrets:
      deploy-token:
        required: false

jobs:
  ci:
    runs-on: ubuntu-latest
    defaults:
      run:
        working-directory: ${{ inputs.working-directory }}
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: ${{ inputs.node-version }}
          cache: ${{ inputs.package-manager }}
      - run: npm ci
      - run: npm run lint
      - run: npm test
      - run: npm run build
```

```yaml
# .github/workflows/ci.yml (in a consuming repo)
name: CI

on:
  pull_request:
  push:
    branches: [main]

jobs:
  ci:
    uses: my-org/shared-workflows/.github/workflows/reusable-ci.yml@main
    with:
      node-version: '20'
      package-manager: npm
    secrets:
      deploy-token: ${{ secrets.DEPLOY_TOKEN }}
```

#### Composite actions

Reusable step-level logic (not full jobs):

```yaml
# .github/actions/setup-project/action.yml
name: Setup Project
description: Checkout, install Node, install dependencies

inputs:
  node-version:
    description: Node.js version
    default: '20'

runs:
  using: composite
  steps:
    - uses: actions/checkout@v4
    - uses: actions/setup-node@v4
      with:
        node-version: ${{ inputs.node-version }}
        cache: npm
    - run: npm ci
      shell: bash
```

```yaml
# Usage in a workflow
steps:
  - uses: ./.github/actions/setup-project
    with:
      node-version: '20'
  - run: npm run lint
  - run: npm test
```

#### Reusable workflow vs composite action — decision table

| Question | Reusable workflow | Composite action |
|---|---|---|
| Can define multiple jobs? | Yes | No |
| Can define triggers? | Yes (`workflow_call`) | No |
| Can be called cross-repo? | Yes | Yes (with checkout or reference) |
| Can share step-level logic? | Indirectly | Yes — this is the purpose |
| Can define `environment:`? | Yes | No |
| Can use `secrets:`? | Yes (declared) | No (pass via inputs) |
| Best for | Full pipeline patterns | Shared setup / utility steps |

#### Self-hosted runners

Use them when you need:
- Private network access (VPN, internal APIs)
- Heavy compute (large Docker builds, ML jobs)
- Specialized hardware (GPU, ARM)
- Large artifact handling
- Cost control at scale

**Runner management rules:**
- Use ephemeral runners when possible (fresh VM per job).
- Never store long-lived secrets on runner machines.
- Patch and update regularly.
- Isolate by trust boundary — don't share runners between public and private repos.
- Monitor runner health and queue depth.

#### Secure secret management

| Practice | Why | Priority |
|---|---|---|
| Use OIDC for cloud access | Short-lived tokens, no static keys | High |
| Scope secrets to environments | Production creds only available in production jobs | High |
| Use environment protection rules | Require approval before production deploy | High |
| Audit secret access | Know who can read what | Medium |
| Rotate secrets regularly | Limit blast radius | Medium |
| Never echo secrets | Even masked, transformed values can leak | Critical |
| Pin third-party actions | Prevents supply chain injection | High |

**OIDC example — deploying to AWS without static keys:**

```yaml
permissions:
  id-token: write
  contents: read

steps:
  - uses: aws-actions/configure-aws-credentials@v4
    with:
      role-to-assume: arn:aws:iam::123456789:role/github-actions
      aws-region: us-east-1
  - run: aws s3 sync dist/ s3://my-bucket/
```

#### Deployment strategies

| Strategy | How it works | When to use | Risk | Cost |
|---|---|---|---|---|
| **Direct deploy** | Replace current version immediately | Small apps, static sites | Instant rollback needed | Low |
| **Rolling** | Replace instances gradually | Stateless services | Slow convergence | Low |
| **Blue-green** | Run two environments, switch traffic | Critical apps needing instant rollback | Double infrastructure during deploy | Medium |
| **Canary** | Route small % of traffic to new version | Risk-sensitive releases | Complex routing setup | Medium |
| **Feature flags** | Deploy code dark, enable via flag | Product experimentation | Flag governance overhead | Low |

#### Release automation

```yaml
name: Release

on:
  push:
    tags: ['v*']

jobs:
  release:
    runs-on: ubuntu-latest
    permissions:
      contents: write
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0
      - uses: actions/setup-node@v4
        with:
          node-version: 20
          cache: npm
      - run: npm ci
      - run: npm run build
      - name: Create GitHub Release
        uses: softprops/action-gh-release@v2
        with:
          generate_release_notes: true
          files: dist/**
```

**Semantic release automation:**

```yaml
- uses: cycjimmy/semantic-release-action@v4
  with:
    branches: |
      ['main']
  env:
    GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
    NPM_TOKEN: ${{ secrets.NPM_TOKEN }}
```

#### Rollback strategy

**Rule:** Define rollback *before* you define deploy. If you cannot answer "how do I undo this?", you are not ready to ship.

Approaches:

1. **Re-deploy previous artifact:** Keep artifacts with `retention-days`. On failure, re-run the deploy job pointing at the last good artifact.
2. **Git revert + re-deploy:** Create a revert commit, push, and let the pipeline deploy the reverted code.
3. **Traffic switch:** With blue-green or canary, route traffic back to the old version instantly.
4. **Feature flag disable:** If the new code is behind a flag, turn it off.

```yaml
# Manual rollback workflow
name: Rollback

on:
  workflow_dispatch:
    inputs:
      version:
        description: 'Version to rollback to (e.g., v1.2.3)'
        required: true

jobs:
  rollback:
    runs-on: ubuntu-latest
    environment: production
    steps:
      - uses: actions/checkout@v4
        with:
          ref: ${{ github.event.inputs.version }}
      - uses: actions/setup-node@v4
        with:
          node-version: 20
          cache: npm
      - run: npm ci
      - run: npm run build
      - run: npm run deploy
        env:
          DEPLOY_TOKEN: ${{ secrets.DEPLOY_TOKEN }}
```

#### CI optimization

| Technique | Impact | Effort |
|---|---|---|
| Cache dependencies | 30-60% faster installs | Low |
| Parallel jobs | Faster overall pipeline | Low |
| Path filters | Skip unchanged packages | Medium |
| Skip CI on docs changes | Save minutes | Low |
| Smaller Docker base images | Faster pulls | Medium |
| Incremental builds (`.next/cache`) | Faster builds | Medium |
| Fan out with matrix only where needed | Right-sized coverage | Low |
| Combine small steps | Reduce overhead | Low |

#### Notifications and incident handling

```yaml
# Slack notification on failure
- name: Notify Slack
  if: failure()
  uses: slackapi/slack-github-action@v2
  with:
    webhook: ${{ secrets.SLACK_WEBHOOK }}
    webhook-type: incoming-webhook
    payload: |
      {
        "text": "❌ CI failed on ${{ github.ref }} — ${{ github.server_url }}/${{ github.repository }}/actions/runs/${{ github.run_id }}"
      }
```

#### 5 production-grade project examples

1. **Next.js monorepo CI/CD:** Path-filtered CI, parallel lint/test/build, artifact-based deploy to Vercel with preview environments for PRs and production deployment on tag.
2. **Astro static site with Cloudflare Pages:** Build on PR for preview, deploy to production on main, with cache warming and bundle size tracking.
3. **Automated release pipeline:** Semantic versioning from commit messages, auto-generated changelog, GitHub Release creation, and deployment trigger.
4. **Docker image build and publish:** Multi-platform Docker build with caching, vulnerability scanning, image signing, and push to GHCR (GitHub Container Registry).
5. **Organization-wide shared CI:** Reusable workflows for lint/test/build/deploy consumed by 20+ repos, with centralized updates and version pinning.

#### Level 3 success criteria

- [ ] Can design a maintainable multi-job pipeline for a real team.
- [ ] Can implement reusable workflows and composite actions.
- [ ] Can reduce CI cost and duration measurably.
- [ ] Can explain deployment safety, rollback, and environment protection.
- [ ] Can secure secrets with OIDC and environment scoping.

---

### Level 4 — Expert

**Goal:** Design and operate a CI/CD platform at organization scale.

At this level you are not writing one workflow — you are designing the system that all workflows run inside. You think about governance, cost, reliability, security, and developer experience across hundreds of repositories.

#### Building an internal CI/CD platform

Your platform provides:
- Standardized reusable workflows for every language and framework.
- Opinionated defaults (Node version, package manager, test framework, deploy target).
- Escape hatches for teams that need customization.
- Observability — dashboards for CI cost, duration, flakiness, and failure rates.
- Guardrails — policies that prevent insecure or wasteful patterns.

#### Organization-wide reusable workflows

Structure:

```text
my-org/ci-workflows/
├── .github/workflows/
│   ├── frontend-ci.yml          ← called by all frontend repos
│   ├── backend-ci.yml           ← called by all backend repos
│   ├── docker-build.yml         ← called by all containerized services
│   ├── deploy-preview.yml       ← shared preview deploy logic
│   ├── deploy-production.yml    ← shared production deploy with approval
│   ├── release.yml              ← shared release automation
│   └── security-scan.yml        ← shared security scanning
└── README.md
```

**Versioning strategy:** Use tagged releases of the shared workflow repo. Consuming repos pin to a version:

```yaml
uses: my-org/ci-workflows/.github/workflows/frontend-ci.yml@v2.1.0
```

This prevents breaking changes from propagating instantly.

#### Governance and policy enforcement

| Policy | Implementation |
|---|---|
| All repos must run CI before merge | Branch protection rules with required status checks |
| Workflow files cannot be modified without review | CODEOWNERS file protecting `.github/` |
| Third-party actions must be audited | Organization-level allow list for actions |
| Production secrets only available with approval | Environment protection rules |
| All deployments must be traceable | Require deployment environments with history |
| Security scans must run on all PRs | Organization-level required workflow |

#### Multi-repository automation

Use `workflow_dispatch` with API calls to trigger workflows across repos:

```yaml
# Trigger a deploy in another repo
- name: Trigger deploy
  uses: peter-evans/repository-dispatch@v3
  with:
    token: ${{ secrets.CROSS_REPO_TOKEN }}
    repository: my-org/production-deploy
    event-type: deploy-frontend
    client-payload: '{"version": "${{ github.sha }}", "repo": "${{ github.repository }}"}'
```

#### Multi-environment promotion pipeline

```text
PR → preview (automatic)
     ↓ merge
main → staging (automatic)
     ↓ manual approval
staging → production (protected environment)
     ↓ monitor
production → rollback (manual dispatch)
```

```yaml
deploy-staging:
  needs: build
  if: github.ref == 'refs/heads/main'
  environment:
    name: staging
    url: https://staging.myapp.com
  # ...

deploy-production:
  needs: deploy-staging
  environment:
    name: production
    url: https://myapp.com
  # ← requires manual approval via environment protection rules
  # ...
```

#### Advanced self-hosted runner architecture

```text
┌─────────────────────────────────────────────────┐
│ RUNNER FLEET                                     │
│                                                 │
│  Pool: general-purpose (auto-scaled)            │
│    ├── ubuntu-latest × N (ephemeral)            │
│    └── scale-to-zero when idle                  │
│                                                 │
│  Pool: docker-builds (large instances)          │
│    ├── 8 CPU / 32 GB RAM                        │
│    └── Docker layer cache on persistent volume  │
│                                                 │
│  Pool: trusted (for production deploys)         │
│    ├── Network access to production             │
│    ├── Strict access controls                   │
│    └── Separate from CI pool                    │
│                                                 │
└─────────────────────────────────────────────────┘
```

**Key architectural decisions:**
- Ephemeral runners for isolation (no state between jobs).
- Separate pools by trust boundary.
- Autoscale based on queue depth.
- Use `actions/runner-controller` (ARC) for Kubernetes-based scaling.
- Monitor runner utilization and queue wait times.

#### Security hardening

| Threat | Mitigation |
|---|---|
| Compromised third-party action | Pin actions to commit SHA, audit on update |
| Secret exfiltration via logs | Mask secrets, avoid echoing transformed values |
| PR from fork running dangerous code | Use `pull_request_target` carefully, limit permissions |
| Runner compromise | Ephemeral runners, least-privilege, network segmentation |
| Supply chain attack | Sign artifacts, verify provenance, scan dependencies |
| Credential theft | OIDC for cloud access, short-lived tokens, environment scoping |
| Workflow injection | Validate inputs, avoid `${{ github.event.*.body }}` in `run:` |

**Action pinning — SHA vs. tag:**

```yaml
# Tag — convenient, but mutable:
uses: actions/checkout@v4

# SHA — immutable, auditable:
uses: actions/checkout@b4ffde65f46336ab88eb53be808477a3936bae11 # v4.1.1
```

For critical production workflows, SHA pinning with Dependabot updates is the gold standard.

#### Supply chain security

- Use `actions/attest-build-provenance` for artifact attestation.
- Sign container images with `cosign`.
- Scan dependencies with `github/codeql-action` and `ossf/scorecard-action`.
- Generate SBOMs (Software Bill of Materials) for releases.
- Enforce lockfile integrity — fail CI if lockfile is missing or outdated.

#### OIDC and cloud credentials

**Problem:** Static cloud access keys (AWS, GCP, Azure) stored as secrets are long-lived and risky.

**Solution:** OIDC (OpenID Connect) federated identity — GitHub mints a short-lived JWT, your cloud provider exchanges it for temporary credentials.

```yaml
permissions:
  id-token: write
  contents: read

steps:
  # AWS
  - uses: aws-actions/configure-aws-credentials@v4
    with:
      role-to-assume: arn:aws:iam::123456789:role/deploy
      aws-region: us-east-1

  # GCP
  - uses: google-github-actions/auth@v2
    with:
      workload_identity_provider: projects/123/locations/global/workloadIdentityPools/gh/providers/gh
      service_account: deploy@my-project.iam.gserviceaccount.com

  # Azure
  - uses: azure/login@v2
    with:
      client-id: ${{ secrets.AZURE_CLIENT_ID }}
      tenant-id: ${{ secrets.AZURE_TENANT_ID }}
      subscription-id: ${{ secrets.AZURE_SUBSCRIPTION_ID }}
```

#### Disaster recovery for CI/CD systems

| Risk | Mitigation |
|---|---|
| GitHub outage | Document manual deploy procedure, keep deployment scripts runnable locally |
| Lost workflow definitions | Version control (they are in the repo), backup org-level configs |
| Runner fleet failure | Autoscaling with health checks, fallback to GitHub-hosted runners |
| Secret rotation failure | Documented rotation procedure, monitoring for expiring credentials |
| Broken shared workflow | Version pinning, canary rollout of shared workflow updates |

#### Architecture review checklist

Use this when reviewing any production workflow:

- [ ] Is the pipeline idempotent? (Re-running produces the same result)
- [ ] Are secrets minimized and scoped?
- [ ] Are jobs parallelized where useful?
- [ ] Can we rollback safely?
- [ ] Are workflows reusable and DRY?
- [ ] Are logs and artifacts sufficient for incident response?
- [ ] Are runner permissions appropriate?
- [ ] Are external actions trusted and pinned?
- [ ] Is the pipeline cost-efficient?
- [ ] Are environments protected appropriately?
- [ ] Is there a documented failure recovery path?
- [ ] Are notifications configured for failures?

#### What expert engineers care about that juniors miss

| Expert concern | Why it matters | Junior blind spot |
|---|---|---|
| Drift between workflow intent and runtime | Workflows silently change behavior | "It passed, ship it" |
| Secret sprawl | Unused secrets accumulate, increasing risk | "Just add another secret" |
| Auditability | Who deployed what, when, and why | No deployment logs |
| Recovery time objectives | How fast can we fix a bad deploy? | No rollback plan |
| Reproducible builds | Same code should produce same artifact | Node version drift, unpinned deps |
| Policy as code | Governance should be automated, not manual | "Trust the team" |
| Supply chain integrity | Every action/dependency is an attack surface | "It's from the marketplace, it's fine" |
| Cost per deployment | CI minutes add up at scale | "It's free" |
| Fleet management | Runners need ops like any infrastructure | "GitHub hosts it" |
| Organizational consistency | Teams should not reinvent basic CI | "Each team owns their workflow" |

#### 10 advanced engineering discussion topics

1. **Runner economics:** At what scale do self-hosted runners become cheaper than GitHub-hosted? Include maintenance, networking, security, and ops cost.
2. **Workflow as product:** Should the platform team treat reusable workflows as internal products with SLOs, changelogs, and migration guides?
3. **Multi-tenancy:** How do you isolate CI for different teams in a single GitHub organization while sharing common infrastructure?
4. **Pipeline observability:** What metrics should you track? Propose a dashboard for CI health across 100+ repos.
5. **Action supply chain:** Design a policy for evaluating, approving, and monitoring third-party actions.
6. **Migration strategy:** How would you migrate 50 repos from Jenkins to GitHub Actions without disrupting teams?
7. **Secrets at scale:** Design a secrets management architecture for an org with 200 repos, 10 environments, and 5 cloud providers.
8. **Monorepo CI scaling:** At 500 packages, path filters break down. What architectural patterns handle this?
9. **Incident response:** A compromised action was used in production workflows. Design the response playbook.
10. **Cost allocation:** How do you attribute CI costs to teams, projects, or products for budget planning?

---

## 3. Setup Guide

### Step 1: Create the workflows directory

```bash
mkdir -p .github/workflows
```

### Step 2: Use clear naming conventions

| File | Purpose |
|---|---|
| `ci.yml` | Main CI pipeline (lint, test, typecheck, build) |
| `deploy-preview.yml` | Preview deployment on PRs |
| `deploy-production.yml` | Production deployment on merge/tag |
| `release.yml` | Automated release and changelog |
| `nightly.yml` | Scheduled nightly builds or checks |
| `security.yml` | Security scanning workflow |
| `dependabot-merge.yml` | Auto-merge safe dependency updates |

**Convention:** Name files by *intent* (what they do), not by *implementation* (how they do it).

### Step 3: Basic workflow structure

Every workflow has three parts:

```yaml
# 1. NAME — human-readable label
name: CI

# 2. TRIGGERS — when does this run?
on:
  push:
    branches: [main]
  pull_request:

# 3. JOBS — what does this do?
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: echo "Hello"
```

### Step 4: Complete example workflows

#### Lint workflow

```yaml
name: Lint

on:
  pull_request:

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: 20
          cache: npm
      - run: npm ci
      - run: npm run lint
```

#### Test workflow

```yaml
name: Test

on:
  pull_request:
  push:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: 20
          cache: npm
      - run: npm ci
      - run: npm test -- --ci --coverage
      - uses: actions/upload-artifact@v4
        if: always()
        with:
          name: coverage-report
          path: coverage/
```

#### Build workflow

```yaml
name: Build

on:
  push:
    branches: [main]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: 20
          cache: npm
      - run: npm ci
      - run: npm run build
      - uses: actions/upload-artifact@v4
        with:
          name: build-output
          path: dist/
          retention-days: 14
```

#### Deploy workflow

```yaml
name: Deploy

on:
  push:
    branches: [main]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: 20
          cache: npm
      - run: npm ci
      - run: npm run build
      - uses: actions/upload-artifact@v4
        with:
          name: build-output
          path: dist/

  deploy:
    needs: build
    runs-on: ubuntu-latest
    environment:
      name: production
      url: https://myapp.com
    steps:
      - uses: actions/download-artifact@v4
        with:
          name: build-output
          path: dist/
      - name: Deploy
        env:
          DEPLOY_TOKEN: ${{ secrets.DEPLOY_TOKEN }}
        run: echo "Deploy dist/ to production"
```

### Step 5: Framework-specific examples

#### React app with Vite

```yaml
name: React CI

on:
  pull_request:
  push:
    branches: [main]

jobs:
  ci:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: 20
          cache: npm
      - run: npm ci
      - run: npm run lint
      - run: npm run typecheck
      - run: npm test -- --ci
      - run: npm run build
      - uses: actions/upload-artifact@v4
        with:
          name: react-build
          path: dist/
```

#### Next.js app

```yaml
name: Next.js CI

on:
  pull_request:
  push:
    branches: [main]

jobs:
  ci:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: 20
          cache: npm
      - uses: actions/cache@v4
        with:
          path: .next/cache
          key: ${{ runner.os }}-nextjs-${{ hashFiles('package-lock.json') }}-${{ hashFiles('**/*.ts', '**/*.tsx') }}
          restore-keys: |
            ${{ runner.os }}-nextjs-${{ hashFiles('package-lock.json') }}-
            ${{ runner.os }}-nextjs-
      - run: npm ci
      - run: npm run lint
      - run: npm run typecheck
      - run: npm test
      - run: npm run build

  deploy-preview:
    needs: ci
    if: github.event_name == 'pull_request'
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Deploy preview to Vercel
        uses: amondnet/vercel-action@v25
        with:
          vercel-token: ${{ secrets.VERCEL_TOKEN }}
          vercel-org-id: ${{ secrets.VERCEL_ORG_ID }}
          vercel-project-id: ${{ secrets.VERCEL_PROJECT_ID }}

  deploy-production:
    needs: ci
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    environment:
      name: production
      url: https://myapp.com
    steps:
      - uses: actions/checkout@v4
      - name: Deploy to Vercel (production)
        uses: amondnet/vercel-action@v25
        with:
          vercel-token: ${{ secrets.VERCEL_TOKEN }}
          vercel-org-id: ${{ secrets.VERCEL_ORG_ID }}
          vercel-project-id: ${{ secrets.VERCEL_PROJECT_ID }}
          vercel-args: '--prod'
```

#### Astro static site

```yaml
name: Astro CI

on:
  pull_request:
  push:
    branches: [main]

jobs:
  ci:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: 20
          cache: npm
      - run: npm ci
      - run: npm run lint
      - run: npm run build
      - uses: actions/upload-artifact@v4
        with:
          name: astro-site
          path: dist/

  deploy:
    needs: ci
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    environment:
      name: production
    permissions:
      pages: write
      id-token: write
    steps:
      - uses: actions/download-artifact@v4
        with:
          name: astro-site
          path: dist/
      - uses: actions/configure-pages@v5
      - uses: actions/upload-pages-artifact@v3
        with:
          path: dist/
      - uses: actions/deploy-pages@v4
```

#### pnpm setup (shared pattern)

```yaml
steps:
  - uses: actions/checkout@v4
  - uses: pnpm/action-setup@v4
    with:
      version: 9
  - uses: actions/setup-node@v4
    with:
      node-version: 20
      cache: pnpm
  - run: pnpm install --frozen-lockfile
```

#### yarn setup (shared pattern)

```yaml
steps:
  - uses: actions/checkout@v4
  - uses: actions/setup-node@v4
    with:
      node-version: 20
      cache: yarn
  - run: yarn install --frozen-lockfile
```

### Step 6: Caching strategy

| What to cache | How | Key strategy |
|---|---|---|
| npm global cache | `actions/setup-node` with `cache: npm` | Based on `package-lock.json` hash |
| pnpm store | `actions/setup-node` with `cache: pnpm` | Based on `pnpm-lock.yaml` hash |
| Next.js build cache | `actions/cache` targeting `.next/cache` | Based on lockfile + source hash |
| Playwright browsers | `actions/cache` targeting `~/.cache/ms-playwright` | Based on Playwright version |
| Docker layers | Docker buildx cache | Based on Dockerfile + source hash |

**Cache key design:**

```yaml
key: ${{ runner.os }}-${{ inputs.package-manager }}-${{ hashFiles('**/lockfile') }}
restore-keys: |
  ${{ runner.os }}-${{ inputs.package-manager }}-
```

The `restore-keys` enable partial cache hits — better than no cache, even if not exact.

### Step 7: Secret setup

1. Go to **Settings → Secrets and variables → Actions** in your repository.
2. Add repository secrets for project-specific values.
3. Create environments (staging, production) and add environment-specific secrets there.
4. For organization-wide secrets, use organization-level settings.

**Common secrets:**

| Secret | Purpose |
|---|---|
| `VERCEL_TOKEN` | Deploy to Vercel |
| `CLOUDFLARE_API_TOKEN` | Deploy to Cloudflare |
| `DEPLOY_TOKEN` | General deployment credential |
| `SLACK_WEBHOOK` | Failure notifications |
| `NPM_TOKEN` | Publish to npm |
| `CODECOV_TOKEN` | Coverage reporting |

### Step 8: Environment setup

1. Go to **Settings → Environments**.
2. Create environments: `preview`, `staging`, `production`.
3. Configure protection rules for production:
   - Required reviewers (at least 1-2 people)
   - Wait timer (optional — e.g., 5 minutes)
   - Restrict to specific branches (only `main` or `release/*`)
4. Add environment-specific secrets and variables.

### Step 9: Branch protection integration

1. Go to **Settings → Branches → Branch protection rules**.
2. Add a rule for `main`:
   - Require a pull request before merging
   - Require status checks to pass (select your CI job names)
   - Require branches to be up to date
   - Require review from code owners (optional)
3. Your CI workflow job names become the required status checks.

### Example repository structure

```text
my-project/
├── .github/
│   ├── workflows/
│   │   ├── ci.yml                 ← lint, typecheck, test, build
│   │   ├── deploy-preview.yml     ← preview on PR
│   │   ├── deploy-production.yml  ← deploy on merge to main
│   │   ├── release.yml            ← tag-based release
│   │   └── nightly.yml            ← scheduled checks
│   ├── actions/
│   │   └── setup-project/
│   │       └── action.yml         ← composite action for shared setup
│   ├── CODEOWNERS                 ← protect .github/ changes
│   └── dependabot.yml             ← automated dependency updates
├── src/
├── tests/
├── public/
├── package.json
├── package-lock.json              ← or pnpm-lock.yaml
├── tsconfig.json
└── README.md
```

---

## 4. Cheatsheet

### Workflow syntax quick reference

```yaml
name: string                          # Human-readable name
on: event | [events] | {event: config}  # Triggers
permissions: {scope: level}           # Token permissions
env: {KEY: value}                     # Workflow-level env vars
concurrency:                          # Prevent duplicate runs
  group: string
  cancel-in-progress: boolean
jobs:
  job-id:
    runs-on: runner-label
    needs: [job-ids]                  # Dependencies
    if: expression                    # Condition
    environment: name | {name, url}   # Deployment target
    timeout-minutes: number           # Job timeout
    strategy:
      matrix: {key: [values]}
      fail-fast: boolean
    defaults:
      run:
        working-directory: path
    steps:
      - name: string                  # Step label
        uses: owner/action@ref        # Use an action
        with: {input: value}          # Action inputs
        run: command                   # Shell command
        env: {KEY: value}             # Step-level env vars
        if: expression                # Step condition
        id: step-id                   # Reference this step
        working-directory: path
        shell: bash | pwsh | python
        continue-on-error: boolean
```

### Triggers (events)

| Trigger | Syntax | Use case |
|---|---|---|
| Push | `on: push` | CI on every commit |
| Push to branch | `on: push: branches: [main]` | CI on specific branches |
| Push with path filter | `on: push: paths: ['src/**']` | Monorepo selective CI |
| Pull request | `on: pull_request` | PR validation |
| PR types | `on: pull_request: types: [opened, synchronize]` | Specific PR events |
| Manual | `on: workflow_dispatch` | Manual trigger with inputs |
| Schedule | `on: schedule: - cron: '0 2 * * *'` | Nightly builds |
| Tag | `on: push: tags: ['v*']` | Release automation |
| Release | `on: release: types: [published]` | Post-release actions |
| Workflow call | `on: workflow_call` | Reusable workflow |
| Repository dispatch | `on: repository_dispatch` | External/cross-repo trigger |
| Workflow run | `on: workflow_run` | Chain after another workflow |

### Expressions

```yaml
# Context variables
${{ github.ref }}                          # refs/heads/main
${{ github.sha }}                          # full commit SHA
${{ github.event_name }}                   # push, pull_request, etc.
${{ github.actor }}                        # who triggered
${{ github.repository }}                   # owner/repo
${{ github.run_id }}                       # unique run ID
${{ github.run_number }}                   # incrementing run number
${{ runner.os }}                           # Linux, Windows, macOS
${{ matrix.node-version }}                 # current matrix value
${{ secrets.MY_SECRET }}                   # secret value
${{ vars.MY_VAR }}                         # repository/org variable
${{ steps.step-id.outputs.key }}           # step output
${{ needs.job-id.outputs.key }}            # job output
${{ env.MY_VAR }}                          # environment variable

# Functions
${{ hashFiles('**/package-lock.json') }}   # file hash for cache keys
${{ toJSON(github.event) }}                # JSON dump for debugging
${{ contains(github.ref, 'release') }}     # string contains
${{ startsWith(github.ref, 'refs/tags') }} # string starts with
${{ format('Hello {0}', github.actor) }}   # string format
${{ fromJSON(steps.id.outputs.json) }}     # parse JSON
```

### Conditions

```yaml
# Branch conditions
if: github.ref == 'refs/heads/main'
if: github.ref != 'refs/heads/main'
if: startsWith(github.ref, 'refs/tags/v')

# Event conditions
if: github.event_name == 'pull_request'
if: github.event_name == 'push'
if: github.event_name == 'workflow_dispatch'

# Label conditions
if: contains(github.event.pull_request.labels.*.name, 'deploy')

# Status conditions
if: success()          # all previous steps succeeded (default)
if: failure()          # any previous step failed
if: always()           # run regardless
if: cancelled()        # run was cancelled

# Combining conditions
if: github.ref == 'refs/heads/main' && github.event_name == 'push'
if: github.event_name == 'pull_request' || github.event_name == 'push'
```

### Matrix patterns

```yaml
# Basic matrix
strategy:
  matrix:
    node: [18, 20, 22]

# Multi-dimensional
strategy:
  matrix:
    node: [18, 20]
    os: [ubuntu-latest, macos-latest]

# With exclusions
strategy:
  matrix:
    node: [18, 20]
    os: [ubuntu-latest, macos-latest]
    exclude:
      - node: 18
        os: macos-latest

# With inclusions (add specific combos)
strategy:
  matrix:
    node: [18, 20]
    include:
      - node: 22
        os: ubuntu-latest
        experimental: true

# Don't cancel others on failure
strategy:
  fail-fast: false
  matrix:
    node: [18, 20, 22]
```

### Cache patterns

```yaml
# Built-in (simplest)
- uses: actions/setup-node@v4
  with:
    node-version: 20
    cache: npm       # or pnpm, yarn

# Manual cache
- uses: actions/cache@v4
  with:
    path: ~/.npm
    key: ${{ runner.os }}-npm-${{ hashFiles('package-lock.json') }}
    restore-keys: ${{ runner.os }}-npm-

# Next.js build cache
- uses: actions/cache@v4
  with:
    path: .next/cache
    key: nextjs-${{ runner.os }}-${{ hashFiles('package-lock.json') }}-${{ hashFiles('src/**') }}
    restore-keys: |
      nextjs-${{ runner.os }}-${{ hashFiles('package-lock.json') }}-
      nextjs-${{ runner.os }}-
```

### Artifact patterns

```yaml
# Upload
- uses: actions/upload-artifact@v4
  with:
    name: build-output
    path: dist/
    retention-days: 7
    if-no-files-found: error    # fail if nothing to upload

# Download (in a later job)
- uses: actions/download-artifact@v4
  with:
    name: build-output
    path: dist/

# Upload multiple
- uses: actions/upload-artifact@v4
  with:
    name: test-results
    path: |
      coverage/
      test-results/
```

### Concurrency control

```yaml
# Cancel previous runs on same branch
concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true

# Don't cancel production deploys
concurrency:
  group: deploy-production
  cancel-in-progress: false
```

### Job outputs

```yaml
jobs:
  detect:
    runs-on: ubuntu-latest
    outputs:
      should-deploy: ${{ steps.check.outputs.deploy }}
    steps:
      - id: check
        run: echo "deploy=true" >> "$GITHUB_OUTPUT"

  deploy:
    needs: detect
    if: needs.detect.outputs.should-deploy == 'true'
    runs-on: ubuntu-latest
    steps:
      - run: echo "Deploying..."
```

### Common marketplace actions

| Action | Version | Purpose |
|---|---|---|
| `actions/checkout` | `@v4` | Clone repository |
| `actions/setup-node` | `@v4` | Install Node.js + cache |
| `actions/cache` | `@v4` | Manual cache control |
| `actions/upload-artifact` | `@v4` | Persist build outputs |
| `actions/download-artifact` | `@v4` | Retrieve artifacts |
| `actions/upload-pages-artifact` | `@v3` | GitHub Pages deploy artifact |
| `actions/deploy-pages` | `@v4` | Deploy to GitHub Pages |
| `actions/configure-pages` | `@v5` | Configure GitHub Pages |
| `pnpm/action-setup` | `@v4` | Install pnpm |
| `softprops/action-gh-release` | `@v2` | Create GitHub Releases |
| `slackapi/slack-github-action` | `@v2` | Slack notifications |
| `dorny/paths-filter` | `@v3` | Detect changed paths |
| `peter-evans/create-pull-request` | `@v7` | Auto-create PRs |
| `github/codeql-action` | `@v3` | Security analysis |
| `aws-actions/configure-aws-credentials` | `@v4` | AWS OIDC auth |
| `google-github-actions/auth` | `@v2` | GCP OIDC auth |

### Debugging tips

| Technique | How |
|---|---|
| Print context | `echo "${{ toJSON(github) }}"` |
| Print env vars | `env \| sort` |
| List files | `ls -la` or `find . -type f` |
| Check Node/npm | `node --version && npm --version` |
| Enable debug logs | Re-run with "Enable debug logging" or set `ACTIONS_STEP_DEBUG: true` |
| Inspect event payload | `cat $GITHUB_EVENT_PATH \| jq .` |
| SSH into runner | Use `mxschmitt/action-tmate` for interactive debugging |
| Test locally | Use `act` (https://github.com/nektos/act) to run workflows locally |

### Common errors and fixes

| Error message | Cause | Fix |
|---|---|---|
| `unexpected value 'workflow_call'` | Wrong event type or indentation | Check `on:` syntax |
| `No hosted provisioner` | Invalid `runs-on` label | Use `ubuntu-latest`, `macos-latest`, or `windows-latest` |
| `Resource not accessible by integration` | Insufficient token permissions | Add `permissions:` block |
| `Process completed with exit code 1` | Command failed | Read the output above this line |
| `npm ERR! could not determine executable to run` | Wrong npx/package setup | Check package.json scripts |
| `Error: No files were found with the provided path` | Upload artifact path wrong | Verify build output directory |
| `The workflow is not valid` | YAML syntax error | Use YAML linter, check indentation |
| Cache not restoring | Key mismatch | Check `hashFiles()` patterns and key format |

### YAML pitfalls

| Pitfall | Example | Fix |
|---|---|---|
| `on` is a boolean | `on:` becomes `true:` | Always quote: `'on':` or use full form |
| Tabs vs spaces | Mix of indent types | Use only spaces (2-space recommended) |
| Unquoted special values | `version: 3.10` → `3.1` | Quote: `version: '3.10'` |
| Multi-line gotcha | `run: echo "hello\nworld"` | Use `run: \|` for multi-line |
| Boolean strings | `yes`, `no`, `true`, `false` | Quote if you mean strings |

### Performance optimization

| Optimization | Expected impact | Effort |
|---|---|---|
| Enable dependency caching | 30–60% faster installs | Trivial |
| Parallel jobs for lint/test/build | 2–3× faster pipeline | Low |
| Path filters for monorepos | Skip 50–80% of runs | Low |
| Concurrency cancellation | Stop redundant runs | Trivial |
| Skip CI on docs changes | Save all minutes for non-code PRs | Low |
| Cache `.next/cache` | 20–40% faster Next.js builds | Low |
| Use `actions/upload-artifact` + `download-artifact` instead of rebuilding | Avoid double builds | Medium |
| Smaller runner images | Faster boot | Medium |

### Security best practices

| Practice | Priority |
|---|---|
| Minimize `permissions:` to what is needed | Critical |
| Use OIDC for cloud access instead of static keys | High |
| Pin critical actions to commit SHA | High |
| Use environment protection for production | High |
| Never echo or transform secrets | Critical |
| Protect `.github/` with CODEOWNERS | High |
| Audit third-party actions before use | Medium |
| Rotate secrets on a schedule | Medium |
| Use `pull_request` (not `pull_request_target`) unless you need write access | High |
| Set `concurrency` to prevent abuse | Medium |

---

## 5. Real-World Engineering Mindset

### CI for React / Next.js / Astro

**Problem:** Every PR needs fast, reliable feedback on code quality and correctness.

**Strategies:**

| Strategy | Description | Pros | Cons |
|---|---|---|---|
| **Single job** | lint → typecheck → test → build in sequence | Simple, minimal YAML | Slower total time, no parallel feedback |
| **Parallel jobs** | lint, typecheck, test run in parallel; build depends on all | Faster feedback on each dimension | More YAML, repeated installs |
| **Parallel + shared setup** | Composite action for checkout/install; parallel validation | Best balance | Slightly more setup |

**By team size:**
- **Small (1–3):** Single job is fine. Simplicity wins.
- **Medium (4–15):** Parallel jobs with caching. Speed matters now.
- **Large (15+):** Reusable workflows, shared composite actions, path filters.

**Hidden pitfalls:**
- Tests that pass locally but fail in CI due to timezone, locale, or font issues.
- Flaky tests eroding team trust in CI.
- Build cache invalidation causing stale behavior.

**Cost:** Free tier gives 2,000 minutes/month for private repos. A 4-job pipeline running 3 minutes each, 20 times/day = 240 minutes/day = 7,200 minutes/month → you will exceed free tier quickly. Cache everything.

**Senior choice:** Parallel jobs (lint, typecheck, test), cached installs, build only after all pass. Add concurrency cancellation to avoid wasting minutes on superseded pushes.

---

### Deploying static sites

**Problem:** Ship built HTML/CSS/JS to a CDN reliably.

**Strategies:**

| Strategy | Pros | Cons |
|---|---|---|
| **GitHub Pages** (via `actions/deploy-pages`) | Free, integrated, simple | Limited to static, no server-side |
| **Cloudflare Pages** (via `cloudflare/pages-action`) | Edge CDN, fast, generous free tier | Cloudflare-specific |
| **Vercel** (native or via action) | Great DX, instant previews | Less control over pipeline |
| **AWS S3 + CloudFront** | Full control, scalable | More setup, more ops |
| **Netlify** (via action) | Good DX, form handling | Platform lock-in |

**Senior choice:** For simple static sites (Astro, Vite), Cloudflare Pages or GitHub Pages. For Next.js with server-side features, Vercel. For maximum control, S3 + CloudFront with OIDC auth.

---

### Deploying to Vercel

**Problem:** You want preview deployments on PRs and production deploys on merge.

**Strategies:**

| Strategy | Pros | Cons |
|---|---|---|
| **Let Vercel handle it natively** | Zero config, automatic previews, instant rollback | Less control, harder to add custom steps |
| **Use GitHub Actions + Vercel CLI** | Full pipeline control, add scans/checks before deploy | More setup, you manage the integration |
| **Hybrid: Vercel for deploy, Actions for CI** | Best of both — Actions validates, Vercel deploys | Two systems to understand |

**Hidden pitfalls:**
- Vercel auto-deploys on push. If you also deploy from Actions, you get double deployments.
- To use Actions-only, disable Vercel's GitHub integration and use the CLI.

**Senior choice:** Hybrid. Let Vercel handle deployment (its DX is superior), use Actions for lint/test/typecheck/security. This is the most common pattern in production Next.js teams.

---

### Deploying to Cloudflare Pages / Workers

**Problem:** Publish edge content or Worker code with consistent validation.

**Strategies:**

| Strategy | Pros | Cons |
|---|---|---|
| **Cloudflare native Git integration** | Simple, automatic previews | Less pipeline customization |
| **Actions + Wrangler CLI** | Full control, multi-step validation | More YAML to maintain |

```yaml
# Deploy Astro to Cloudflare Pages
- name: Deploy to Cloudflare Pages
  uses: cloudflare/pages-action@v1
  with:
    apiToken: ${{ secrets.CLOUDFLARE_API_TOKEN }}
    accountId: ${{ secrets.CLOUDFLARE_ACCOUNT_ID }}
    projectName: my-site
    directory: dist/
```

**Senior choice:** For static sites, Cloudflare's native integration is excellent. For Workers with complex build steps, use Actions + Wrangler.

---

### Docker build and deployment

**Problem:** Build container images reproducibly, scan them, and push to a registry.

```yaml
name: Docker Build

on:
  push:
    branches: [main]

jobs:
  build:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      packages: write
    steps:
      - uses: actions/checkout@v4

      - uses: docker/setup-buildx-action@v3

      - uses: docker/login-action@v3
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}

      - uses: docker/build-push-action@v6
        with:
          context: .
          push: true
          tags: ghcr.io/${{ github.repository }}:${{ github.sha }}
          cache-from: type=gha
          cache-to: type=gha,mode=max
```

**Strategies:**

| Strategy | Pros | Cons |
|---|---|---|
| **GitHub-hosted runner + buildx cache** | Simple, good caching | Slow for very large images |
| **Self-hosted runner + persistent cache** | Fastest builds | Runner maintenance |
| **Multi-stage Dockerfile** | Smaller images, faster deploys | Dockerfile complexity |

**Senior choice:** GitHub-hosted runner with `docker/build-push-action` and `cache-from: type=gha` for most teams. Move to self-hosted when build times exceed 10 minutes.

---

### Preview deployments

**Problem:** Reviewers want to see and interact with changes before merge.

**Strategies:**

| Strategy | Pros | Cons |
|---|---|---|
| **Platform-native** (Vercel/Cloudflare) | Zero config, automatic | Platform-specific |
| **GitHub Pages per branch** | Free | Only static, complex setup |
| **Ephemeral environment per PR** | Full runtime fidelity | Expensive, complex teardown |

**Senior choice:** Use platform-native previews (Vercel, Cloudflare). For full-stack apps, spin up ephemeral environments only for critical PRs.

---

### Monorepo selective builds

**Problem:** Running all CI for all packages on every change is wasteful.

**Strategies:**

| Strategy | Pros | Cons |
|---|---|---|
| **Path filters** (`on.push.paths`) | Simple | Misses shared dependency changes |
| **Change detection** (`dorny/paths-filter`) | More precise, can detect transitive deps | More setup |
| **Turborepo/Nx integration** | Build-tool aware, understands dependency graph | Tool-specific |

```yaml
# Using dorny/paths-filter
- uses: dorny/paths-filter@v3
  id: filter
  with:
    filters: |
      web:
        - 'apps/web/**'
        - 'packages/ui/**'
        - 'packages/utils/**'
      api:
        - 'apps/api/**'
        - 'packages/db/**'

- name: Web CI
  if: steps.filter.outputs.web == 'true'
  run: pnpm --filter web test && pnpm --filter web build
```

**Senior choice:** Change detection + Turborepo for large monorepos. Simple path filters for small ones.

---

### Versioning and release automation

**Problem:** Releases need consistency, traceability, and should not depend on human memory.

**Strategies:**

| Strategy | Pros | Cons |
|---|---|---|
| **Manual tags** | Simple, explicit | Error-prone, easy to forget |
| **Semantic release** | Fully automated from commit messages | Requires conventional commit discipline |
| **Release PRs** (e.g., `release-please`) | Auditable, reviewable release process | Extra step in the flow |
| **Tag + GitHub Release** | Good for libraries | Less structured |

```yaml
# Using Google's release-please
name: Release

on:
  push:
    branches: [main]

jobs:
  release:
    runs-on: ubuntu-latest
    steps:
      - uses: googleapis/release-please-action@v4
        with:
          release-type: node
```

**Senior choice:** `release-please` for apps (structured, auditable). `semantic-release` for libraries (fully automated). Both require commit message discipline.

---

### Running database migrations

**Problem:** If deploy succeeds but migration fails, the app may be broken.

**Strategies:**

| Strategy | How it works | Risk |
|---|---|---|
| **Migrate before deploy** | Run migrations first, then deploy new code | If deploy fails, migration is already applied |
| **Deploy then migrate** | Deploy new code, then run migrations | App may error if it expects new schema |
| **Expand/contract** | Backward-compatible schema changes in two phases | Safest but requires discipline |

**Senior choice:** Expand/contract migrations. Make schema changes backward-compatible so old and new code can coexist. Deploy code first, then apply schema changes. This is the only safe approach for zero-downtime systems.

---

### Dependabot automation

**Problem:** Dependabot creates many PRs that need review.

```yaml
# .github/dependabot.yml
version: 2
updates:
  - package-ecosystem: npm
    directory: /
    schedule:
      interval: weekly
    groups:
      minor-and-patch:
        update-types: [minor, patch]
    open-pull-requests-limit: 10
```

```yaml
# .github/workflows/dependabot-merge.yml
name: Dependabot Auto-merge

on:
  pull_request:

permissions:
  contents: write
  pull-requests: write

jobs:
  auto-merge:
    if: github.actor == 'dependabot[bot]'
    runs-on: ubuntu-latest
    steps:
      - uses: dependabot/fetch-metadata@v2
        id: metadata
      - if: steps.metadata.outputs.update-type == 'version-update:semver-patch'
        run: gh pr merge "${{ github.event.pull_request.number }}" --auto --squash
        env:
          GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

**Senior choice:** Group minor/patch updates, auto-merge patches that pass CI, manually review major updates.

---

### Security scanning

```yaml
name: Security

on:
  pull_request:
  schedule:
    - cron: '0 6 * * 1'   # weekly Monday 6 AM

jobs:
  codeql:
    runs-on: ubuntu-latest
    permissions:
      security-events: write
    steps:
      - uses: actions/checkout@v4
      - uses: github/codeql-action/init@v3
        with:
          languages: javascript-typescript
      - uses: github/codeql-action/analyze@v3

  dependency-review:
    if: github.event_name == 'pull_request'
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/dependency-review-action@v4
```

**Senior choice:** Run CodeQL on PRs and weekly. Add dependency review on PRs. Use OSSF Scorecard for supply chain assessment.

---

### Auto-labeling PRs

```yaml
# .github/labeler.yml
frontend:
  - changed-files:
    - any-glob-to-any-file: ['src/components/**', 'src/pages/**']

docs:
  - changed-files:
    - any-glob-to-any-file: ['docs/**', '*.md']

ci:
  - changed-files:
    - any-glob-to-any-file: ['.github/**']
```

```yaml
name: Label PR

on:
  pull_request:
    types: [opened, synchronize]

jobs:
  label:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      pull-requests: write
    steps:
      - uses: actions/labeler@v5
```

---

### Generating changelogs

**Strategies:**

| Strategy | Tool | Pros | Cons |
|---|---|---|---|
| Manual | None | Accurate | Time-consuming, inconsistent |
| From PR labels | `release-please` | Auditable | Requires label discipline |
| From conventional commits | `semantic-release` | Fully automated | Requires commit message discipline |
| GitHub auto-generated | Built-in release notes | Zero config | Less structured |

**Senior choice:** Conventional commits + automated generation for mature teams. GitHub auto-generated release notes for small teams.

---

### Multi-environment deployment

```yaml
name: Deploy

on:
  push:
    branches: [main]
    tags: ['v*']

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: 20
          cache: npm
      - run: npm ci && npm run build
      - uses: actions/upload-artifact@v4
        with:
          name: build
          path: dist/

  deploy-staging:
    needs: build
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    environment:
      name: staging
      url: https://staging.myapp.com
    steps:
      - uses: actions/download-artifact@v4
        with:
          name: build
          path: dist/
      - run: echo "Deploy to staging"

  deploy-production:
    needs: deploy-staging
    if: startsWith(github.ref, 'refs/tags/v')
    runs-on: ubuntu-latest
    environment:
      name: production
      url: https://myapp.com
    steps:
      - uses: actions/download-artifact@v4
        with:
          name: build
          path: dist/
      - run: echo "Deploy to production"
```

**Senior choice:** Reusable deploy workflow called with different environment inputs. Build once, deploy many times.

---

### Rollback after failed deployment

**Problem:** Production is broken after a deploy. How fast can you recover?

**Strategies:**

| Strategy | Recovery time | Requirement |
|---|---|---|
| **Re-deploy previous artifact** | 2–5 minutes | Artifact retention |
| **Traffic switch** (blue-green) | Seconds | Two environments running |
| **Git revert + pipeline** | 5–10 minutes | Fast CI pipeline |
| **Feature flag disable** | Seconds | Flag infrastructure |

```yaml
# Manual rollback trigger
name: Rollback Production

on:
  workflow_dispatch:
    inputs:
      version:
        description: 'Git tag or SHA to rollback to'
        required: true

jobs:
  rollback:
    runs-on: ubuntu-latest
    environment: production
    steps:
      - uses: actions/checkout@v4
        with:
          ref: ${{ github.event.inputs.version }}
      - uses: actions/setup-node@v4
        with:
          node-version: 20
          cache: npm
      - run: npm ci
      - run: npm run build
      - name: Deploy
        env:
          DEPLOY_TOKEN: ${{ secrets.DEPLOY_TOKEN }}
        run: echo "Rolling back to ${{ github.event.inputs.version }}"
```

**Senior choice:** Make rollback a first-class workflow with manual dispatch. Test it regularly. Know your RTO (Recovery Time Objective).

---

### Scheduled workflows

```yaml
name: Nightly

on:
  schedule:
    - cron: '0 2 * * *'    # 2 AM UTC daily

jobs:
  nightly:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: 20
          cache: npm
      - run: npm ci
      - run: npm run test:e2e
      - run: npm audit
      - name: Notify on failure
        if: failure()
        run: |
          curl -X POST "${{ secrets.SLACK_WEBHOOK }}" \
            -H 'Content-type: application/json' \
            -d '{"text":"🌙 Nightly build failed: ${{ github.server_url }}/${{ github.repository }}/actions/runs/${{ github.run_id }}"}'
```

**Cron syntax quick reference:**

| Schedule | Cron | Notes |
|---|---|---|
| Every day at 2 AM UTC | `0 2 * * *` | Common for nightly builds |
| Every Monday at 6 AM UTC | `0 6 * * 1` | Weekly security scans |
| Every 6 hours | `0 */6 * * *` | Frequent checks |
| First of every month | `0 0 1 * *` | Monthly maintenance |

**Pitfall:** Scheduled workflows only run on the default branch. If your workflow is on a feature branch, it won't trigger on schedule.

---

### Nightly builds

**Problem:** PR-time CI might not catch issues that appear only with full test suites, integration tests, or across platforms.

**Strategies:**

| Strategy | Pros | Cons |
|---|---|---|
| **Nightly full matrix** | Maximum coverage | Expensive |
| **Nightly smoke tests** | Cheap, fast | Lower coverage |
| **Nightly release candidate** | Tests the release process | Needs release infrastructure |

**Senior choice:** Run the broadest matrix nightly. Run the focused matrix on PRs. Alert the team on Slack/email if the nightly fails.

---

## 6. Brainstorm / Open Questions

### Architecture

1. What should be standardized in shared workflows vs. left to each repo?
2. When should a workflow be split into multiple workflows?
3. When should a workflow become a reusable workflow?
4. When should a reusable workflow become a platform service?
5. What does the ideal pipeline DAG (directed acyclic graph) look like for your organization?
6. Which parts of CI should be event-driven and which should be scheduled?
7. How much conditional logic is acceptable before a workflow becomes unmaintainable?
8. Should workflows define their own Node version, or should that be centralized?

### Scaling

9. What happens if this workflow takes 30 minutes instead of 3?
10. How many parallel jobs can your runner fleet actually support at peak?
11. What workflows become too expensive to run on every PR?
12. How do you handle bursts when 20 teams push simultaneously?
13. How do you detect and reduce redundant workflow executions?
14. What is the right level of workflow reuse across 50 repos? 500 repos?
15. How do you prevent duplicated YAML logic across repositories?
16. At what point should you invest in self-hosted runners?

### Security

17. How do you avoid leaking secrets in logs — even transformed or base64-encoded ones?
18. Which jobs should never have access to production secrets?
19. Should third-party actions be pinned to commit SHAs or version tags?
20. Where should OIDC replace static cloud credentials?
21. How do you review workflow file changes with the same rigor as application code?
22. What should happen if a workflow file is compromised via a supply chain attack?
23. How do you segment trusted and untrusted runners?
24. What is your process for vetting a new action from the marketplace?
25. How do you detect if a previously-trusted action changes behavior silently?

### DX / Maintainability

26. Can a new engineer understand the pipeline in under 10 minutes?
27. Which steps are noisy or flaky enough to degrade trust in CI?
28. Where is caching helpful vs. where does it cause confusion?
29. How do you surface the real failure instead of a cascade of follow-on errors?
30. What should be reusable, and what should remain explicit for readability?
31. How do you keep YAML complexity from becoming tribal knowledge?
32. What is the best default workflow template for your team?
33. How do you test workflow changes safely before merging?

### Cost

34. Which jobs cost the most minutes without proportional value?
35. Can you skip the entire pipeline for docs-only or README changes?
36. Should you run full matrix tests on every commit, or only on specific triggers?
37. How much does artifact retention cost over time?
38. Are self-hosted runners actually cheaper after including maintenance and ops?
39. Are your caches helping enough to justify their complexity?
40. What is the cost of a slow pipeline in developer time and context switching?

### Reliability

41. What should happen if deployment succeeds but the database migration fails?
42. How do you design for re-runs after flaky infrastructure outages?
43. How do you ensure artifacts are reproducible and traceable?
44. What should be automatically retried vs. manually investigated?
45. How do you detect partial failures that look successful at first glance?
46. What is your rollback RTO (Recovery Time Objective)?
47. How do you keep scheduled workflows trustworthy over months?

### Release Strategy

48. When should you release on merge vs. on tag?
49. Should production deployment be gated by manual approval?
50. How should preview deployments map to release confidence?
51. What release process works best for a monorepo with multiple products?
52. When should database migrations be decoupled from app deployment?
53. What does a safe canary look like for your technology stack?
54. How do you reconcile fast shipping with controlled, safe releases?
55. What is the right balance between release automation and human judgment?

---

## 7. Practice Questions

### Beginner (Level 1)

**Q1. Multiple choice:** Where do GitHub Actions workflow files live?

- A. `src/workflows/`
- B. `.github/workflows/`
- C. `.vscode/tasks/`
- D. `actions/`

<details><summary>Answer</summary>B. <code>.github/workflows/</code></details>

---

**Q2. True/False:** A job runs on a runner.

<details><summary>Answer</summary>True. Every job is assigned to a runner (a VM or container) that executes its steps.</details>

---

**Q3. Fill in the blank:** The command `npm ___` should be used instead of `npm install` in CI for deterministic builds.

<details><summary>Answer</summary><code>ci</code> — <code>npm ci</code> does a clean install strictly from the lockfile.</details>

---

**Q4. Single choice:** Which step must usually come first in a GitHub Actions job?

- A. `npm run build`
- B. `npm test`
- C. `actions/checkout@v4`
- D. `npm run deploy`

<details><summary>Answer</summary>C. <code>actions/checkout@v4</code> — without checkout, there is no source code on the runner.</details>

---

**Q5. Debugging:** Your workflow says `command not found: eslint`. Name three likely causes.

<details><summary>Answer</summary>
1. <code>npm ci</code> or dependency install step is missing.<br>
2. eslint is a devDependency but dependencies were installed with <code>--production</code>.<br>
3. The working directory is wrong — the job is running in a folder without <code>node_modules</code>.
</details>

---

**Q6. Scenario:** Your YAML file fails to parse. The error says "mapping values are not allowed here." What do you check first?

<details><summary>Answer</summary>Indentation. This error almost always means inconsistent indentation — a value is at the wrong level, or tabs are mixed with spaces.</details>

---

**Q7. Matching:** Match each concept to its meaning.

| Concept | Meaning |
|---|---|
| A. workflow | 1. A reusable unit of pipeline logic |
| B. step | 2. A file or directory persisted from a run |
| C. action | 3. A single command or action invocation |
| D. artifact | 4. The full automation definition in YAML |

<details><summary>Answer</summary>A→4, B→3, C→1, D→2</details>

---

**Q8. True/False:** Tabs are acceptable in YAML workflow files.

<details><summary>Answer</summary>False. YAML requires spaces for indentation. Tabs cause parse errors.</details>

---

**Q9. Scenario:** You push to a branch called `feature/login`, but your workflow only triggers on `push: branches: [main]`. Will the workflow run?

<details><summary>Answer</summary>No. The branch filter only matches <code>main</code>. The push to <code>feature/login</code> does not match.</details>

---

**Q10. Fill in the blank:** To trigger a workflow on every pull request, use `on: _______`.

<details><summary>Answer</summary><code>pull_request</code></details>

---

### Junior (Level 2)

**Q11. Multiple choice:** Why use a matrix strategy?

- A. To hide secrets
- B. To run the same job across multiple versions or platforms
- C. To make logs shorter
- D. To replace caching

<details><summary>Answer</summary>B. Matrices fan out a job across combinations of parameters.</details>

---

**Q12. True/False:** The `needs` keyword can control the execution order of jobs.

<details><summary>Answer</summary>True. <code>needs: [lint, test]</code> means this job waits for both lint and test to complete.</details>

---

**Q13. Fill in the blank:** The cache key should usually be tied to the ________.

<details><summary>Answer</summary>Lockfile hash — e.g., <code>hashFiles('package-lock.json')</code>. This ensures the cache is invalidated when dependencies change.</details>

---

**Q14. Scenario:** A pull request workflow should NOT deploy to production. Write the condition.

<details><summary>Answer</summary><code>if: github.ref == 'refs/heads/main' && github.event_name == 'push'</code> — this ensures the deploy step only runs on pushes to main, not on PRs.</details>

---

**Q15. Debugging:** A job passes locally but fails in CI with missing peer dependencies. What should you inspect?

<details><summary>Answer</summary>
1. Node version mismatch between local and CI.<br>
2. npm version difference (npm 7+ auto-installs peer deps, older versions don't).<br>
3. Missing lockfile or stale lockfile.<br>
4. Different package manager (local uses pnpm, CI uses npm).
</details>

---

**Q16. Matching:** Match the package manager to its lockfile and cache mode.

| Package manager | Lockfile | Setup-node cache value |
|---|---|---|
| A. npm | 1. `yarn.lock` | X. `pnpm` |
| B. pnpm | 2. `pnpm-lock.yaml` | Y. `npm` |
| C. yarn | 3. `package-lock.json` | Z. `yarn` |

<details><summary>Answer</summary>A→3,Y | B→2,X | C→1,Z</details>

---

**Q17. Single choice:** Which is a common anti-pattern?

- A. Parallel jobs for lint and test
- B. Reusable workflows
- C. Duplicating nearly identical YAML in every repository
- D. Protected environments

<details><summary>Answer</summary>C. Duplicating YAML causes drift and maintenance pain. Use reusable workflows instead.</details>

---

**Q18. Scenario:** Your team wants preview deployments for every PR. What trade-offs should be discussed?

<details><summary>Answer</summary>
1. <strong>Cost:</strong> Each preview uses CI minutes and possibly hosting resources.<br>
2. <strong>Cleanup:</strong> Preview environments need to be torn down when the PR is closed.<br>
3. <strong>Security:</strong> Preview environments may expose features before they're ready.<br>
4. <strong>Parity:</strong> Previews may not match production behavior (different env vars, API endpoints).<br>
5. <strong>Value:</strong> Previews are most valuable for UI changes — skip them for backend-only PRs.
</details>

---

**Q19. True/False:** `actions/setup-node` with `cache: npm` caches the `node_modules` directory.

<details><summary>Answer</summary>False. It caches npm's global cache directory (<code>~/.npm</code>), not <code>node_modules</code>. You still need <code>npm ci</code> to install from the cache into <code>node_modules</code>.</details>

---

**Q20. Fill in the blank:** To access a secret named `DEPLOY_KEY` in a step, use `${{ secrets.________ }}`.

<details><summary>Answer</summary><code>DEPLOY_KEY</code></details>

---

### Senior / Expert (Level 3–4)

**Q21. Multiple choice:** What is the biggest advantage of OIDC over long-lived cloud access keys?

- A. Faster YAML parsing
- B. Short-lived, federated credential exchange — no static keys to leak
- C. Better log formatting
- D. More matrix options

<details><summary>Answer</summary>B. OIDC uses short-lived tokens generated per workflow run, eliminating the risk of leaked static credentials.</details>

---

**Q22. True/False:** Blue-green deployment always uses less infrastructure than rolling deployment.

<details><summary>Answer</summary>False. Blue-green requires two full environments running simultaneously during the switch, which uses <em>more</em> infrastructure than rolling.</details>

---

**Q23. Fill in the blank:** A workflow reused across repositories via `workflow_call` is called a ________ workflow.

<details><summary>Answer</summary>Reusable</details>

---

**Q24. Scenario:** Your monorepo has 150 packages. Path filters in `on.push.paths` miss changes to shared packages. What strategy would you use?

<details><summary>Answer</summary>Use a change detection tool that understands the dependency graph — <code>dorny/paths-filter</code> with explicit shared package paths, or integrate with Turborepo/Nx which know the package dependency tree and can determine affected packages transitively.</details>

---

**Q25. Debugging:** Deployment succeeded, but the app is broken because a database migration failed halfway. What design mistake likely occurred?

<details><summary>Answer</summary>
1. Migration was not wrapped in a transaction.<br>
2. Migration was not backward-compatible (expand/contract pattern was not used).<br>
3. There was no health check after migration to gate the deploy.<br>
4. Rollback strategy for the migration was not defined.
</details>

---

**Q26. Single choice:** Which is most appropriate for sharing step-level logic (like checkout + install + setup)?

- A. Composite action
- B. Release tag
- C. Pull request template
- D. Artifact retention policy

<details><summary>Answer</summary>A. Composite actions encapsulate reusable step logic.</details>

---

**Q27. Multiple choice:** Which is a good reason to use self-hosted runners? (Select all)

- A. No maintenance required ever
- B. Private network access and custom tooling
- C. Avoid writing workflows
- D. Cost control at scale

<details><summary>Answer</summary>B and D. Self-hosted runners require maintenance but provide network access and can be cheaper at high scale.</details>

---

**Q28. Matching:** Match each deployment strategy to its description.

| Strategy | Description |
|---|---|
| A. Rolling | 1. Route a small % of traffic to the new version first |
| B. Blue-green | 2. Gradually replace instances one by one |
| C. Canary | 3. Maintain two full environments, switch traffic instantly |

<details><summary>Answer</summary>A→2, B→3, C→1</details>

---

**Q29. Scenario:** An action from the marketplace (`cool-deploy@latest`) suddenly starts exfiltrating secrets. What policy would have prevented this?

<details><summary>Answer</summary>
1. Pin actions to commit SHA (<code>cool-deploy@abc123</code>) instead of mutable tags.<br>
2. Use Dependabot to update action versions with review.<br>
3. Restrict allowed actions at the organization level.<br>
4. Review action source code before adoption.
</details>

---

**Q30. Real-world pain:** CI costs have doubled after adding matrix tests across 3 OS × 3 Node versions (9 combinations). How would you evaluate whether the extra coverage is worth the cost?

<details><summary>Answer</summary>
1. Check if any real bugs were caught by non-primary OS/Node combos.<br>
2. Run the full matrix on nightly, not on every PR.<br>
3. Run only the primary combo (ubuntu + current LTS Node) on PRs.<br>
4. Use <code>fail-fast: true</code> to stop early on failure.<br>
5. Calculate cost: 9 × avg_minutes × runs_per_day × cost_per_minute.
</details>

---

**Q31. True/False:** Scheduled workflows can trigger on any branch.

<details><summary>Answer</summary>False. Scheduled workflows only run on the default branch (usually <code>main</code>).</details>

---

**Q32. Fill in the blank:** Production secrets should be stored in a GitHub ________ with protection rules.

<details><summary>Answer</summary>Environment</details>

---

**Q33. Design question:** How would you design rollback for a system that uses feature flags AND database migrations?

<details><summary>Answer</summary>
1. Feature flags: disable the flag immediately — fastest rollback.<br>
2. Database: use expand/contract migrations so old code works with new schema.<br>
3. If a migration cannot be backward-compatible, ensure the flag is turned off before the migration runs.<br>
4. Keep a manual dispatch rollback workflow that redeploys the previous version.<br>
5. Document the rollback decision tree for on-call engineers.
</details>

---

**Q34. Debugging:** A workflow that depends on an environment secret works in staging but fails in production with "secret not found." What should you inspect?

<details><summary>Answer</summary>
1. The secret exists in the <code>production</code> environment (not just <code>staging</code>).<br>
2. The job references <code>environment: production</code>.<br>
3. The branch is allowed by the environment's branch protection rules.<br>
4. The person/workflow has approval to access the production environment.
</details>

---

**Q35. Design question:** When should a team move from per-repo YAML files to organization-wide reusable workflows?

<details><summary>Answer</summary>
When you observe:<br>
1. The same YAML is copy-pasted across 5+ repos.<br>
2. A change to the standard pipeline requires updating every repo.<br>
3. Teams are making inconsistent CI decisions (different Node versions, missing steps).<br>
4. Security or compliance requires standardized scanning and deployment.
</details>

---

## 8. Personalized Recommendations

### Based on your stack: React, Next.js, Astro, TypeScript, static files

#### Patterns most useful for you

1. **PR validation workflow:** lint + typecheck + test + build on every PR. This is your #1 quality gate.
2. **Dependency caching:** `actions/setup-node` with `cache: npm` (or pnpm). Essential for speed.
3. **Preview deployments:** Automatic preview URLs for every PR (via Vercel or Cloudflare).
4. **Production deployment with environment protection:** Deploy on merge to main, with approval for production.
5. **Path filters:** For monorepos or multi-package setups, skip CI for unrelated changes.
6. **Concurrency cancellation:** Cancel in-progress runs when you push again to the same PR.
7. **Dependabot auto-merge:** Automatically merge safe patch updates that pass CI.
8. **Release automation:** Automated versioning and changelog generation on merge.

#### What to learn first (priority order)

1. Basic workflow syntax and structure.
2. Triggers: `push`, `pull_request`, `workflow_dispatch`.
3. `actions/checkout` + `actions/setup-node` + `npm ci`.
4. Multi-job pipelines with `needs`.
5. Caching.
6. Secrets and environments.
7. Conditional logic with `if:`.
8. Artifacts.
9. Reusable workflows.
10. OIDC and security hardening.

#### Which workflows to build first

| Order | Workflow | Why |
|---|---|---|
| 1st | `ci.yml` — lint, typecheck, test, build | Your foundation — everything else depends on this |
| 2nd | `deploy.yml` — deploy to staging/production | Close the loop — code changes reach users |
| 3rd | `preview.yml` — preview deployment on PR | Better code review — reviewers can see the change |
| 4th | `dependabot-merge.yml` — auto-merge patches | Reduce dependency noise |
| 5th | `release.yml` — automated versioning | Professional release process |
| 6th | `nightly.yml` — scheduled full test suite | Catch issues PR-CI misses |
| 7th | `security.yml` — CodeQL + dependency review | Security posture |

#### Mistakes frontend engineers commonly make in CI/CD

| Mistake | Why it happens | Better approach |
|---|---|---|
| Treating CI as "just run my local scripts" | Mental model from `npm run dev` | Design CI as a production system with isolation, reproducibility, and failure handling |
| No caching | "It works without it" | Always cache — the speed difference compounds |
| Deploying from every branch | Copy-paste from a tutorial | Deploy only from `main` or tags |
| Mixing preview and production deploys | Not understanding environments | Use separate jobs with `environment:` and conditions |
| Ignoring rollback | "We'll fix forward" | Define rollback before you define deploy |
| Using `npm install` | Habit | `npm ci` is always correct in CI |
| Hardcoding values | Quick and dirty | Use secrets, variables, and inputs |
| Not setting up branch protection | "We trust the team" | Branch protection catches mistakes trust cannot |
| Ignoring CI speed | "It only takes 5 minutes" | Slow CI kills iteration speed; optimize early |
| Not testing the workflow | "YAML is just config" | Workflow code is production code — test it |

#### How to evolve from simple to production-grade

```text
Phase 1: Single-job CI
  └── lint + test + build in one job

Phase 2: Multi-job CI
  └── parallel lint/typecheck/test → build

Phase 3: Deployment
  └── CI → staging deploy → production deploy

Phase 4: Safety
  └── environment protection, secrets, branch rules

Phase 5: Speed
  └── caching, concurrency, path filters

Phase 6: Automation
  └── Dependabot, release automation, auto-labeling

Phase 7: Reuse
  └── composite actions, reusable workflows

Phase 8: Security
  └── OIDC, action pinning, CodeQL, dependency review

Phase 9: Observability
  └── notifications, failure alerts, cost tracking

Phase 10: Platform
  └── org-wide shared workflows, governance, runner fleet
```

#### 30-day learning plan

**Week 1: Foundations (Days 1–7)**

| Day | Task | Deliverable |
|---|---|---|
| 1 | Read this guide sections 1–2 Level 1 | Mental model of concepts |
| 2 | Create first `ci.yml`: print Node version, run lint | Working workflow |
| 3 | Add test and build steps | Complete single-job CI |
| 4 | Break the workflow intentionally, study logs | Debugging confidence |
| 5 | Split into parallel jobs (lint, test, build) | Multi-job workflow |
| 6 | Add `actions/setup-node` with caching | Faster installs |
| 7 | Add trigger for `pull_request` and push to `main` | Proper trigger config |

**Week 2: Team workflows (Days 8–14)**

| Day | Task | Deliverable |
|---|---|---|
| 8 | Add typecheck job | Full validation pipeline |
| 9 | Configure secrets and environment variables | Secure config |
| 10 | Add a deployment job (Vercel or Cloudflare) | Working deployment |
| 11 | Add environment protection for production | Safe production deploy |
| 12 | Set up branch protection requiring CI | Enforced quality gate |
| 13 | Add concurrency cancellation | No wasted runs |
| 14 | Add Dependabot config + auto-merge workflow | Dependency automation |

**Week 3: Production readiness (Days 15–21)**

| Day | Task | Deliverable |
|---|---|---|
| 15 | Create a preview deployment workflow for PRs | Preview URLs on PRs |
| 16 | Add `.next/cache` or build cache | Faster builds |
| 17 | Add release automation (release-please or manual) | Versioned releases |
| 18 | Add Slack/Discord notification on failure | Team awareness |
| 19 | Create a composite action for project setup | Reusable setup logic |
| 20 | Add CodeQL or dependency review | Security scanning |
| 21 | Review and document your workflows | Maintainable system |

**Week 4: Advanced patterns (Days 22–30)**

| Day | Task | Deliverable |
|---|---|---|
| 22 | Study reusable workflows; convert CI to reusable | Shareable pipeline |
| 23 | Add path filters for a monorepo setup | Selective CI |
| 24 | Create a rollback workflow with `workflow_dispatch` | Recovery mechanism |
| 25 | Study OIDC; replace a static key with OIDC | Better security |
| 26 | Add a nightly workflow with broader testing | Extended coverage |
| 27 | Study self-hosted runners conceptually | Architecture knowledge |
| 28 | Audit all workflows against the security checklist | Security hardening |
| 29 | Review cost — minutes used, cache efficiency | Cost awareness |
| 30 | Write an architecture decision record for your CI/CD | Documentation |

---

## Summary, Next Steps, and Advanced Topics

### Concise summary

GitHub Actions is an event-driven automation platform integrated into GitHub. For a frontend engineer, the fastest path to mastery is:

1. **Start** with a simple CI workflow (lint, test, build).
2. **Evolve** to parallel jobs, caching, and deployment with environments.
3. **Mature** into reusable workflows, security hardening, and release automation.
4. **Scale** toward organization-wide platform engineering with governance.

The key mindset shift: your pipeline is production infrastructure. Treat it with the same rigor as your application code — version it, test it, monitor it, and design for failure.

### Next steps

1. Create your first `ci.yml` for a real project today.
2. Add caching and branch protection this week.
3. Set up a preview deployment workflow for PRs.
4. Add environment protection for production deployments.
5. Study reusable workflows and OIDC within the next two weeks.
6. Build a rollback workflow and test it.

### Suggested advanced topics to continue learning

| Topic | Why it matters |
|---|---|
| Reusable workflows at organization scale | Consistency and governance across many repos |
| OIDC-based cloud authentication | Eliminate static cloud credentials |
| Ephemeral self-hosted runners (ARC) | Cost-effective, secure runner infrastructure |
| Release automation with semantic versioning | Professional, traceable releases |
| Supply chain security and action pinning | Protect against compromised dependencies |
| Monorepo pipeline orchestration | Efficient CI for large codebases |
| Canary and blue-green deployment design | Safe production releases |
| CI/CD observability and failure analytics | Data-driven pipeline improvement |
| Artifact provenance and signing | Build integrity and compliance |
| Internal developer platform design | CI/CD as a product for your organization |
| GitHub Actions + Terraform/Pulumi | Infrastructure as code in your pipeline |
| Multi-cloud deployment strategies | Deploy to AWS, GCP, Azure from one pipeline |
| Performance testing in CI | Catch regressions before production |
| E2E testing with Playwright in Actions | Full browser testing in CI |
| Custom GitHub Actions development | Build and publish your own actions |
