# GitLab CI/CD — Complete Deep-Dive Engineering Guide

> For a frontend engineer (React / Next.js / Astro / TypeScript) moving toward DevOps, CI/CD, release engineering, automation, and platform engineering.

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

### 1.1 What GitLab CI/CD Is

GitLab CI/CD is an automation engine built into the GitLab platform. It reads a `.gitlab-ci.yml` file at the root of your repository and executes pipelines — ordered sequences of jobs — in response to Git events such as pushes, merge requests, tags, and schedules.

Unlike GitHub Actions where automation is one feature among many, GitLab CI/CD is deeply integrated into the entire GitLab product — issues, merge requests, container registry, package registry, environments, and monitoring are all first-class citizens in the same platform. This means your pipeline doesn't just run tests; it can create releases, push container images to GitLab's built-in registry, manage environments, and report directly on merge requests — all without third-party integrations.

**The React/Next.js analogy:** If GitHub Actions is like assembling your build toolchain from npm packages (Webpack, Babel, ESLint, etc.), GitLab CI/CD is more like Next.js — an opinionated, batteries-included framework where routing, SSR, API routes, and optimization are all built in. You trade some flexibility for cohesion.

### 1.2 Core Concepts

#### GitLab Repository

The Git repository hosted on GitLab. It contains your source code and the `.gitlab-ci.yml` pipeline definition. GitLab reads this file from the root of the default branch (or the branch being pushed) to determine what to run.

#### GitLab Runner

The agent that executes your jobs. Runners can be:
- **Shared runners:** Provided by GitLab (SaaS) or your GitLab admin. Available to all projects.
- **Group runners:** Shared across all projects in a GitLab group.
- **Project runners:** Dedicated to a single project.

**Analogy:** Runners are like CI servers. In GitHub Actions terms, a runner is equivalent to the `runs-on` machine. The difference is that GitLab runners are a separate, installable component — you can host them yourself on any machine, VM, or Kubernetes cluster.

#### Pipeline

A complete execution of your `.gitlab-ci.yml` for a specific commit. A pipeline contains stages, and stages contain jobs.

**Analogy:** A pipeline is like a full `npm run build` cycle — but orchestrated across multiple machines with stages and parallelism.

#### Stage

A logical grouping of jobs that execute in sequence. All jobs in the same stage run in parallel. Stages execute one after another — the next stage only starts when all jobs in the previous stage succeed.

**Analogy:** Stages are like the phases of a build: first `lint`, then `test`, then `build`, then `deploy`. You wouldn't deploy before tests pass.

#### Job

The fundamental unit of work. A job runs on a single runner, executes scripts, and can produce artifacts, interact with caches, and report status.

**Analogy:** A job is like one script in `package.json` — `npm run lint` or `npm run test`. Each job runs independently on its own runner.

#### Artifact

A file or directory produced by a job that needs to be passed to later jobs or downloaded by a user. Artifacts are attached to the pipeline and available for a configurable retention period.

**Analogy:** Like the `dist/` folder from `npm run build` — the output you want to keep and use later.

**Key distinction from cache:** Artifacts are job outputs intended for downstream consumption. Caches are speed optimizations for repeated installs.

#### Cache

Stored data (typically `node_modules` or package manager caches) that persists across pipeline runs to speed up jobs. Caches are best-effort — they may not be available, and your job must work without them.

**Analogy:** Like `.next/cache` or the npm global cache — speeds things up but is not required for correctness.

#### Variable

A key-value pair available to jobs as environment variables. Variables can be:
- **Predefined:** `CI_COMMIT_SHA`, `CI_PIPELINE_ID`, `CI_MERGE_REQUEST_IID`, etc.
- **Custom:** Defined in `.gitlab-ci.yml`, project settings, group settings, or instance settings.
- **Protected:** Only available on protected branches/tags.
- **Masked:** Hidden in job logs.

**Analogy:** Like environment variables in Vercel or `.env` files — but with scope, protection, and masking controls.

#### Environment

A named deployment target (e.g., `staging`, `production`) tracked by GitLab. Environments have deployment history, rollback capability, and can be linked to external URLs.

**Analogy:** Like Vercel's Preview vs. Production, but you define and control the rules yourself.

#### Deployment

The act of releasing your application to an environment. GitLab tracks deployments per environment, providing a history and the ability to roll back.

### 1.3 The Lifecycle: git push → deployment

```text
┌─────────────────────────────────────────────────────────────────┐
│ DEVELOPER                                                       │
│                                                                 │
│  git add . → git commit → git push origin feature/login        │
│                                                                 │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│ GITLAB                                                          │
│                                                                 │
│  Receives push → reads .gitlab-ci.yml → creates pipeline       │
│                                                                 │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│ PIPELINE                                                        │
│                                                                 │
│  Stage: lint            Stage: test           Stage: build      │
│  ┌──────────┐           ┌──────────┐         ┌──────────┐     │
│  │ lint:js  │           │ test:unit│         │  build   │     │
│  └──────────┘           │ test:e2e │         └────┬─────┘     │
│       │                 └──────────┘              │           │
│       │                      │                    │           │
│       └──────────────────────┼────────────────────┘           │
│                              ▼                                 │
│                      Stage: deploy                             │
│                      ┌────────────┐                            │
│                      │  deploy    │  → environment: production │
│                      └────────────┘                            │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│ DEPLOYMENT TARGET                                               │
│                                                                 │
│  Vercel / Cloudflare / AWS / Docker registry / Kubernetes      │
│  Status reported back to GitLab merge request                  │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 1.4 Comparison With Other CI/CD Systems

| Dimension | GitLab CI/CD | GitHub Actions | Jenkins | CircleCI | Azure DevOps |
|---|---|---|---|---|---|
| **Config** | `.gitlab-ci.yml` | YAML per workflow | Jenkinsfile (Groovy) | `.circleci/config.yml` | `azure-pipelines.yml` |
| **Pipeline model** | Stage-based (sequential stages, parallel jobs within) | Job-based DAG with `needs` | Pipeline/stage/step | Workflow → jobs → steps | Stage → job → step |
| **Runner model** | Separate installable runner (gitlab-runner) | Built into platform or self-hosted | Always self-hosted | Cloud or self-hosted | Cloud or self-hosted |
| **Container registry** | Built-in | GitHub Packages (GHCR) | Plugin-based | None built-in | Azure Container Registry |
| **Environments** | First-class with deployment history and rollback | Environments with protection rules | Plugin-based | None built-in | Environments with approvals |
| **Marketplace/reuse** | CI/CD templates, `include` | 20,000+ actions marketplace | 1,800+ plugins | Orbs | Extensions |
| **Merge request integration** | Deep — CI status, test reports, security scans, code quality inline | PR checks and status | Via webhooks/plugins | PR checks | PR policies |
| **Best for** | GitLab-centric teams wanting all-in-one | GitHub-centric teams | Custom/legacy infra | Fast CI for product teams | Microsoft-centric enterprises |
| **Biggest weakness** | YAML complexity, less community reuse than Actions | Less integrated platform | Maintenance burden | Separate platform | Heavier UX |

### 1.5 When GitLab CI/CD Is a Better Choice

**Choose GitLab CI/CD when:**
- Your team already uses GitLab for source code.
- You want an all-in-one platform (SCM + CI/CD + registry + environments + monitoring).
- You need strong self-hosted/on-premise support.
- You want built-in container registry and package registry.
- You need dynamic child pipelines for complex monorepo orchestration.
- Your organization requires strong compliance and audit features.

**Choose something else when:**
- Your code lives on GitHub (use GitHub Actions).
- You need a massive ecosystem of community-maintained actions (GitHub Actions wins here).
- You want zero-config deployment for Next.js/frontend (Vercel is better DX).
- You have deep Jenkins investment and migration cost is too high.

### 1.6 Mental Model Diagram

```text
┌──────────────────────────────────────────────────────┐
│                 YOUR REPOSITORY                       │
│                                                      │
│  src/  package.json  .gitlab-ci.yml                  │
│                                                      │
└────────────────────┬─────────────────────────────────┘
                     │ git push / MR / tag / schedule
                     ▼
┌──────────────────────────────────────────────────────┐
│               GITLAB PLATFORM                         │
│                                                      │
│  Reads .gitlab-ci.yml → creates pipeline             │
│                                                      │
│  Pipeline:                                           │
│    Stage 1: lint     ──► all jobs run in parallel     │
│    Stage 2: test     ──► all jobs run in parallel     │
│    Stage 3: build    ──► all jobs run in parallel     │
│    Stage 4: deploy   ──► deploy to environment        │
│                                                      │
│  Each job → dispatched to a Runner                   │
│  Artifacts flow downstream between stages            │
│  Cache shared across pipelines for speed             │
│                                                      │
└──────────────────────────────────────────────────────┘
```

---

## 2. Learning Roadmap by Skill Level

### Level 1 — Newbie

**Goal:** Create your first pipeline, understand the file format, and debug basic failures.

#### What `.gitlab-ci.yml` is

A YAML file at the root of your repository that defines your entire pipeline — stages, jobs, scripts, artifacts, caching, deployment rules, and more. GitLab reads it on every push and creates a pipeline accordingly.

**Analogy:** It's like `package.json` for your CI/CD — a single declarative file that tells the system what to do.

#### YAML basics for GitLab CI

```yaml
# Stages define the order of execution
stages:
  - lint
  - test
  - build

# A job definition
lint:
  stage: lint
  image: node:20-alpine
  script:
    - npm ci
    - npm run lint

# Another job
test:
  stage: test
  image: node:20-alpine
  script:
    - npm ci
    - npm test
```

**Key YAML rules:**
- Indentation: spaces only (2-space recommended), never tabs.
- Job names cannot be GitLab reserved keywords (`stages`, `variables`, `include`, `default`, `workflow`, etc.).
- Each job must have a `script` keyword.

#### First pipeline

```yaml
stages:
  - check
  - build

lint:
  stage: check
  image: node:20-alpine
  script:
    - npm ci
    - npm run lint

test:
  stage: check
  image: node:20-alpine
  script:
    - npm ci
    - npm test

build:
  stage: build
  image: node:20-alpine
  script:
    - npm ci
    - npm run build
```

`lint` and `test` are both in the `check` stage — they run **in parallel**. `build` is in the next stage — it runs **after** both `lint` and `test` succeed.

#### Understanding GitLab Runner

Runners execute your jobs. Every job runs inside a Docker container (by default) pulled from the `image` you specify.

```yaml
# This job runs inside a node:20-alpine container
build:
  image: node:20-alpine
  script:
    - node --version
    - npm ci
    - npm run build
```

If you don't specify `image`, the runner uses its default image (often `ruby:latest` — you almost always want to specify your own).

#### Debugging pipeline failures

1. **Click the failed job** in the pipeline view. The log shows exactly which script line failed.
2. **Check the exit code.** A non-zero exit code fails the job.
3. **Reproduce locally.** Run the same commands on your machine in the same Node version.
4. **Add debug output:**
   ```yaml
   script:
     - node --version
     - npm --version
     - ls -la
     - npm ci
     - npm run lint
   ```
5. **Check variables.** Use `echo $CI_COMMIT_BRANCH` to verify context.
6. **Enable debug logging.** Set the variable `CI_DEBUG_TRACE: "true"` (verbose — use sparingly).

#### Common mistakes

| Mistake | What happens | Fix |
|---|---|---|
| No `stages` definition | Jobs may run in unexpected order | Always define `stages` explicitly |
| Missing `image` | Uses runner default (often wrong) | Always specify `image: node:20-alpine` |
| `npm install` instead of `npm ci` | Non-deterministic builds | Use `npm ci` for lockfile-based installs |
| Wrong indentation | YAML parse error | Use spaces (2-space), never tabs |
| Job name is a reserved keyword | Confusing errors | Avoid `stages`, `variables`, `include`, `default` as job names |
| Not specifying `stage` | Job goes to `test` stage by default | Assign every job to a stage |

#### 5 beginner exercises

1. **Hello pipeline:** Create a pipeline with one job that prints "Hello from GitLab CI."
2. **Lint on push:** Create a pipeline that runs `npm run lint` on every push.
3. **Two stages:** Create a pipeline with `check` and `build` stages — lint + test in check, build in build.
4. **Break it:** Introduce a lint error, push, and study the failure log.
5. **Node version:** Print the Node.js version and npm version in a job.

#### Level 1 success criteria

- [ ] Can create a `.gitlab-ci.yml` from scratch.
- [ ] Can explain pipeline, stage, job, and runner.
- [ ] Can read failure logs and fix basic errors.
- [ ] Can explain why `npm ci` is used in CI.

---

### Level 2 — Junior

**Goal:** Build practical team pipelines — multi-stage, cached, conditional, with artifacts and MR integration.

#### Multiple stages and job dependencies

```yaml
stages:
  - validate
  - build
  - deploy

lint:
  stage: validate
  image: node:20-alpine
  script:
    - npm ci
    - npm run lint

typecheck:
  stage: validate
  image: node:20-alpine
  script:
    - npm ci
    - npm run typecheck

test:
  stage: validate
  image: node:20-alpine
  script:
    - npm ci
    - npm test

build:
  stage: build
  image: node:20-alpine
  script:
    - npm ci
    - npm run build
  artifacts:
    paths:
      - dist/
    expire_in: 1 week

deploy:
  stage: deploy
  script:
    - echo "Deploying dist/"
  environment:
    name: production
    url: https://myapp.com
  rules:
    - if: $CI_COMMIT_BRANCH == "main"
```

#### Job dependencies with `needs`

By default, a job waits for the entire previous stage. `needs` lets you skip the stage barrier:

```yaml
stages:
  - validate
  - build
  - deploy

lint:
  stage: validate
  script: npm run lint

test:
  stage: validate
  script: npm test

build:
  stage: build
  needs: [lint, test]    # ← starts as soon as lint AND test finish
  script: npm run build
  artifacts:
    paths: [dist/]

deploy:
  stage: deploy
  needs: [build]         # ← doesn't wait for entire build stage
  script: echo "Deploy"
```

**`needs` creates a DAG** (directed acyclic graph) — jobs can start earlier, making the pipeline faster.

#### Artifacts vs. cache

| Feature | Artifacts | Cache |
|---|---|---|
| Purpose | Pass files between jobs/stages | Speed up repeated installs |
| Reliability | Guaranteed (stored by GitLab) | Best-effort (may be missing) |
| Scope | Within one pipeline (or downloadable) | Across pipelines |
| Example | `dist/`, test reports | `node_modules/`, `.npm/` |
| Keyword | `artifacts:` | `cache:` |

#### Cache configuration

```yaml
# Global cache for all jobs
default:
  cache:
    key:
      files:
        - package-lock.json     # Cache key based on lockfile hash
    paths:
      - node_modules/
    policy: pull-push            # pull on start, push on success

# Job that only reads cache (faster)
deploy:
  cache:
    key:
      files:
        - package-lock.json
    paths:
      - node_modules/
    policy: pull                 # Don't update the cache
```

**pnpm cache:**

```yaml
default:
  cache:
    key:
      files:
        - pnpm-lock.yaml
    paths:
      - .pnpm-store/
    policy: pull-push

.pnpm-setup:
  before_script:
    - corepack enable
    - corepack prepare pnpm@9 --activate
    - pnpm config set store-dir .pnpm-store
    - pnpm install --frozen-lockfile
```

#### Variables and secrets

```yaml
# In .gitlab-ci.yml
variables:
  NODE_ENV: production
  CI: "true"

# Use predefined variables
build:
  script:
    - echo "Branch: $CI_COMMIT_BRANCH"
    - echo "SHA: $CI_COMMIT_SHA"
    - echo "MR: $CI_MERGE_REQUEST_IID"
    - echo "Pipeline: $CI_PIPELINE_ID"
```

**Secret variables:** Set in GitLab UI under **Settings → CI/CD → Variables**.
- Mark as **Protected** → only available on protected branches.
- Mark as **Masked** → hidden in logs.

#### Conditional rules

```yaml
# Modern approach: use rules (not only/except)
deploy-staging:
  stage: deploy
  script: echo "Deploy to staging"
  rules:
    - if: $CI_COMMIT_BRANCH == "main"

deploy-production:
  stage: deploy
  script: echo "Deploy to production"
  rules:
    - if: $CI_COMMIT_TAG =~ /^v\d+\.\d+\.\d+$/
  environment:
    name: production

# MR-only job
preview:
  stage: deploy
  script: echo "Build preview"
  rules:
    - if: $CI_PIPELINE_SOURCE == "merge_request_event"

# Manual trigger
deploy-manual:
  stage: deploy
  script: echo "Manual deploy"
  rules:
    - if: $CI_COMMIT_BRANCH == "main"
      when: manual
```

#### Merge request pipelines

```yaml
workflow:
  rules:
    - if: $CI_PIPELINE_SOURCE == "merge_request_event"
    - if: $CI_COMMIT_BRANCH == "main"
    - if: $CI_COMMIT_TAG

# Now the pipeline runs on:
# - Every merge request
# - Pushes to main
# - Tags
```

**Why use merge request pipelines?** They prevent duplicate pipelines (one for the push, one for the MR) and give you access to MR-specific variables like `$CI_MERGE_REQUEST_IID`.

#### Reusable job templates

```yaml
# Template (starts with a dot — not executed as a job)
.node-setup:
  image: node:20-alpine
  before_script:
    - npm ci
  cache:
    key:
      files: [package-lock.json]
    paths: [node_modules/]

# Extend the template
lint:
  extends: .node-setup
  stage: validate
  script:
    - npm run lint

test:
  extends: .node-setup
  stage: validate
  script:
    - npm test

build:
  extends: .node-setup
  stage: build
  script:
    - npm run build
  artifacts:
    paths: [dist/]
```

**`extends` is like component composition in React** — you define a base, then extend it with specifics.

#### Running Docker in GitLab CI

```yaml
build-image:
  image: docker:24
  services:
    - docker:24-dind
  variables:
    DOCKER_TLS_CERTDIR: "/certs"
  script:
    - docker login -u $CI_REGISTRY_USER -p $CI_REGISTRY_PASSWORD $CI_REGISTRY
    - docker build -t $CI_REGISTRY_IMAGE:$CI_COMMIT_SHA .
    - docker push $CI_REGISTRY_IMAGE:$CI_COMMIT_SHA
```

GitLab provides built-in variables for its container registry (`$CI_REGISTRY`, `$CI_REGISTRY_IMAGE`, etc.).

#### 5 mini project ideas

1. **React CI with MR pipeline:** Lint, test, build on MRs; deploy on main.
2. **Next.js with artifacts:** Build, upload artifact, deploy artifact to hosting.
3. **Docker build and push:** Build a Docker image, push to GitLab Container Registry.
4. **Multi-stage with caching:** Separate validate/build/deploy stages with npm cache.
5. **Scheduled dependency check:** Weekly pipeline that runs `npm audit`.

#### Common mistakes and anti-patterns

| Anti-pattern | Why it's bad | Better approach |
|---|---|---|
| Using `only/except` | Deprecated, confusing precedence | Use `rules` |
| No caching | Every job reinstalls dependencies | Cache `node_modules` or package store |
| Artifacts without `expire_in` | Storage bloat | Set `expire_in: 1 week` or appropriate duration |
| One massive job | Slow feedback, hard to debug | Split into stages and jobs |
| Duplicating job config | Drift, maintenance pain | Use `.templates` and `extends` |
| No `workflow:rules` | Duplicate pipelines on MRs | Define `workflow:rules` to control pipeline creation |
| Secrets in `.gitlab-ci.yml` | Committed to repo history | Use CI/CD variables in project settings |

#### Level 2 success criteria

- [ ] Can build multi-stage pipelines with artifacts and cache.
- [ ] Can use `rules` for conditional execution.
- [ ] Can use `extends` for DRY job definitions.
- [ ] Can explain MR pipelines and prevent duplicates.

---

### Level 3 — Senior

**Goal:** Build production-ready CI/CD — fast, secure, maintainable, with deployment safety and monorepo support.

#### Monorepo pipelines with `changes`

```yaml
frontend:
  stage: build
  script:
    - cd frontend && npm ci && npm run build
  rules:
    - changes:
        - frontend/**
        - packages/shared/**

backend:
  stage: build
  script:
    - cd backend && npm ci && npm run build
  rules:
    - changes:
        - backend/**
        - packages/shared/**
```

**Limitation:** `changes` only works for push and MR pipelines, not schedules or triggers. For complex monorepos, use dynamic child pipelines.

#### Dynamic child pipelines

Generate pipeline YAML dynamically, then trigger it:

```yaml
# Parent pipeline
generate-pipeline:
  stage: prepare
  image: node:20-alpine
  script:
    - node scripts/generate-pipeline.js > child-pipeline.yml
  artifacts:
    paths:
      - child-pipeline.yml

trigger-child:
  stage: execute
  trigger:
    include:
      - artifact: child-pipeline.yml
        job: generate-pipeline
    strategy: depend    # Parent waits for child to finish
```

```javascript
// scripts/generate-pipeline.js
// Detect changed packages and generate jobs only for them
const changedPackages = detectChanges();
const jobs = changedPackages.map(pkg => ({
  [`build-${pkg}`]: {
    stage: 'build',
    script: [`cd packages/${pkg}`, 'npm ci', 'npm run build'],
    rules: [{ when: 'always' }],
  }
}));

const pipeline = {
  stages: ['build', 'test', 'deploy'],
  ...Object.assign({}, ...jobs),
};

console.log(YAML.stringify(pipeline));
```

**This is extremely powerful for monorepos** — you can generate exactly the jobs you need based on what changed, avoiding wasted compute.

#### Reusable pipeline templates with `include`

```yaml
# In a shared templates repository: templates/frontend-ci.yml
.frontend-ci:
  image: node:20-alpine
  cache:
    key:
      files: [package-lock.json]
    paths: [node_modules/]
  before_script:
    - npm ci

lint:
  extends: .frontend-ci
  stage: validate
  script: npm run lint

test:
  extends: .frontend-ci
  stage: validate
  script: npm test

build:
  extends: .frontend-ci
  stage: build
  script: npm run build
  artifacts:
    paths: [dist/]
    expire_in: 1 week
```

```yaml
# In consuming project: .gitlab-ci.yml
include:
  - project: 'my-org/ci-templates'
    ref: v2.0.0
    file: '/templates/frontend-ci.yml'

stages:
  - validate
  - build
  - deploy

deploy:
  stage: deploy
  script: echo "Deploy"
  rules:
    - if: $CI_COMMIT_BRANCH == "main"
```

**`include` sources:**

| Source | Syntax | Use case |
|---|---|---|
| Local file | `include: local: '/path.yml'` | Split large pipelines |
| Another project | `include: project: 'org/repo'` | Shared templates across repos |
| Remote URL | `include: remote: 'https://...'` | External templates |
| Template | `include: template: 'name.yml'` | GitLab-provided templates |

#### Deployment strategy

```yaml
deploy-staging:
  stage: deploy
  script:
    - ./deploy.sh staging
  environment:
    name: staging
    url: https://staging.myapp.com
  rules:
    - if: $CI_COMMIT_BRANCH == "main"

deploy-production:
  stage: deploy
  script:
    - ./deploy.sh production
  environment:
    name: production
    url: https://myapp.com
  rules:
    - if: $CI_COMMIT_TAG =~ /^v\d+/
      when: manual
      allow_failure: false    # Pipeline waits for manual approval
```

#### Environment promotion

```text
MR → preview (automatic)
  ↓ merge
main → staging (automatic)
  ↓ manual approval
staging → production (manual trigger, protected environment)
  ↓ monitor
production → rollback (re-deploy previous successful deployment)
```

#### Release pipelines

```yaml
release:
  stage: release
  image: registry.gitlab.com/gitlab-org/release-cli:latest
  rules:
    - if: $CI_COMMIT_TAG =~ /^v\d+\.\d+\.\d+$/
  script:
    - echo "Creating release for $CI_COMMIT_TAG"
  release:
    tag_name: $CI_COMMIT_TAG
    name: "Release $CI_COMMIT_TAG"
    description: "Automated release"
```

#### CI optimization

| Technique | Impact | How |
|---|---|---|
| Cache dependencies | 30-60% faster installs | `cache:` with lockfile key |
| Use `needs` (DAG) | Skip stage barriers | `needs: [job-name]` |
| Parallel keyword | Split test suites | `parallel: 4` |
| Interruptible jobs | Cancel on new push | `interruptible: true` |
| `changes` rules | Skip unchanged packages | `rules: changes:` |
| Smaller Docker images | Faster pull times | Use `alpine` variants |
| Artifacts only what's needed | Less upload/download | Precise `paths:` |

#### Parallel and matrix-like patterns

```yaml
# Parallel test splitting
test:
  stage: test
  image: node:20-alpine
  parallel: 4
  script:
    - npm ci
    - npm test -- --shard=$CI_NODE_INDEX/$CI_NODE_TOTAL

# Matrix-like pattern with parallel:matrix
test:
  stage: test
  parallel:
    matrix:
      - NODE_VERSION: ["18", "20", "22"]
        OS_IMAGE: ["node:${NODE_VERSION}-alpine"]
  image: $OS_IMAGE
  script:
    - node --version
    - npm ci
    - npm test
```

#### Docker build and deployment

```yaml
variables:
  DOCKER_TLS_CERTDIR: "/certs"

build-image:
  stage: build
  image: docker:24
  services:
    - docker:24-dind
  script:
    - docker login -u $CI_REGISTRY_USER -p $CI_REGISTRY_PASSWORD $CI_REGISTRY
    - |
      docker build \
        --cache-from $CI_REGISTRY_IMAGE:latest \
        --tag $CI_REGISTRY_IMAGE:$CI_COMMIT_SHA \
        --tag $CI_REGISTRY_IMAGE:latest \
        .
    - docker push $CI_REGISTRY_IMAGE:$CI_COMMIT_SHA
    - docker push $CI_REGISTRY_IMAGE:latest
```

#### Secure secrets management

| Practice | Priority |
|---|---|
| Use protected variables for production secrets | Critical |
| Mask variables in logs | High |
| Limit variable scope to environments | High |
| Use OIDC for cloud access (no static keys) | High |
| Rotate secrets regularly | Medium |
| Audit variable access | Medium |

#### Self-hosted runners

Use when you need:
- Private network access
- Custom hardware (GPU, ARM)
- Cost control at high scale
- Regulatory compliance (data locality)

**Runner executors:**

| Executor | Use case | Isolation |
|---|---|---|
| Docker | Most common — each job in a container | Container-level |
| Kubernetes | Auto-scaling on K8s | Pod-level |
| Shell | Direct on host (avoid for shared runners) | None |
| Docker Machine | Auto-scale VMs (legacy) | VM-level |

#### Rollback strategy

GitLab environments support one-click rollback:

```yaml
deploy:
  environment:
    name: production
    url: https://myapp.com
    on_stop: stop-production
```

GitLab tracks every deployment per environment. You can re-deploy any previous successful deployment from the Environments UI.

**Additional strategies:**
- Re-deploy previous image tag.
- Git revert + push → pipeline re-deploys.
- Feature flag disable.
- Traffic switch (blue-green).

#### Observability and notifications

```yaml
# Slack notification on failure
notify-failure:
  stage: .post
  script:
    - |
      curl -X POST "$SLACK_WEBHOOK" \
        -H 'Content-type: application/json' \
        -d "{\"text\":\"❌ Pipeline failed: $CI_PROJECT_URL/-/pipelines/$CI_PIPELINE_ID\"}"
  rules:
    - if: $CI_COMMIT_BRANCH == "main"
      when: on_failure
```

#### 5 production-grade project examples

1. **Next.js monorepo CI/CD:** Child pipelines for changed packages, artifact-based deploy, environment promotion from staging to production.
2. **Astro static site:** Build, push to GitLab Pages or Cloudflare, preview on MR, production on tag.
3. **Docker microservice:** Build image, scan for vulnerabilities, push to GitLab registry, deploy to Kubernetes.
4. **Automated releases:** Conventional commit parsing, changelog generation, GitLab Release creation on tag.
5. **Multi-environment pipeline:** dev/staging/production with progressive deployment and manual gates.

#### Level 3 success criteria

- [ ] Can design maintainable multi-stage pipelines for real teams.
- [ ] Can use child pipelines for monorepo optimization.
- [ ] Can implement environment promotion with rollback.
- [ ] Can optimize pipeline speed with caching, DAGs, and parallelism.

---

### Level 4 — Expert

**Goal:** Design and operate CI/CD at organization scale — governance, multi-project, security, and cost optimization.

#### Organization-wide pipeline architecture

```text
org/ci-templates/
├── templates/
│   ├── frontend-ci.yml
│   ├── backend-ci.yml
│   ├── docker-build.yml
│   ├── deploy-static.yml
│   ├── deploy-k8s.yml
│   ├── security-scan.yml
│   └── release.yml
└── README.md
```

All projects include from this repo:

```yaml
include:
  - project: 'org/ci-templates'
    ref: v3.0.0
    file: '/templates/frontend-ci.yml'
```

**Version pinning** (`ref: v3.0.0`) prevents breaking changes from propagating instantly.

#### Pipeline governance

| Policy | Implementation |
|---|---|
| All repos must run CI | Enforce via group-level compliance pipelines |
| Templates cannot be modified locally | Use `include` with strict overrides |
| Production deploys require approval | Protected environments with required approvers |
| Secrets scoped to protected branches | Protected variables |
| Pipeline changes reviewed | Require MR approval for `.gitlab-ci.yml` |
| Security scans mandatory | Include security templates at group level |

**Compliance pipelines** (GitLab Premium+): Force specific jobs to run regardless of what the project defines.

#### Multi-project pipelines

```yaml
# Trigger pipeline in another project
trigger-deploy:
  stage: deploy
  trigger:
    project: org/infrastructure
    branch: main
    strategy: depend
  variables:
    DEPLOY_VERSION: $CI_COMMIT_SHA
    DEPLOY_APP: frontend
```

#### Multi-environment deployment architecture

```yaml
.deploy-template:
  image: alpine:latest
  script:
    - ./deploy.sh $DEPLOY_ENV
  rules:
    - when: manual
      allow_failure: false

deploy-staging:
  extends: .deploy-template
  stage: deploy
  variables:
    DEPLOY_ENV: staging
  environment:
    name: staging
    url: https://staging.myapp.com
  rules:
    - if: $CI_COMMIT_BRANCH == "main"

deploy-production:
  extends: .deploy-template
  stage: deploy
  variables:
    DEPLOY_ENV: production
  environment:
    name: production
    url: https://myapp.com
  rules:
    - if: $CI_COMMIT_TAG =~ /^v\d+/
      when: manual
      allow_failure: false
```

#### Security hardening

| Threat | Mitigation |
|---|---|
| Secret leakage in logs | Mask all sensitive variables |
| Compromised dependency | SAST, dependency scanning, container scanning |
| Unauthorized production deploy | Protected environments with required approvers |
| Runner compromise | Use ephemeral runners, least-privilege |
| Pipeline injection | Validate all external inputs, avoid `eval` |
| Supply chain attack | Pin dependencies, sign images, verify provenance |

**GitLab built-in security scanning:**

```yaml
include:
  - template: Security/SAST.gitlab-ci.yml
  - template: Security/Dependency-Scanning.gitlab-ci.yml
  - template: Security/Container-Scanning.gitlab-ci.yml
  - template: Security/Secret-Detection.gitlab-ci.yml
```

#### OIDC and cloud authentication

```yaml
deploy-aws:
  stage: deploy
  image: amazon/aws-cli:latest
  id_tokens:
    AWS_TOKEN:
      aud: https://gitlab.com
  script:
    - >
      export $(printf "AWS_ACCESS_KEY_ID=%s AWS_SECRET_ACCESS_KEY=%s AWS_SESSION_TOKEN=%s"
      $(aws sts assume-role-with-web-identity
      --role-arn $AWS_ROLE_ARN
      --role-session-name "gitlab-ci-$CI_JOB_ID"
      --web-identity-token $AWS_TOKEN
      --duration-seconds 3600
      --query 'Credentials.[AccessKeyId,SecretAccessKey,SessionToken]'
      --output text))
    - aws s3 sync dist/ s3://my-bucket/
```

#### Scaling runners

| Strategy | Pros | Cons |
|---|---|---|
| GitLab SaaS shared runners | Zero maintenance | Cost at scale, shared resources |
| Self-hosted on VMs | Control, private network | Manual scaling and patching |
| Kubernetes executor | Auto-scaling pods | K8s complexity |
| Docker Machine (legacy) | Auto-scale VMs | Being deprecated |
| Fleeting plugin | Modern auto-scaling for cloud VMs | Newer, less battle-tested |

#### Cost optimization

| Technique | Savings |
|---|---|
| Cache dependencies | Reduce install time 30-60% |
| Use `needs` (DAG) | Reduce total pipeline time |
| `interruptible: true` | Cancel superseded pipelines |
| Skip jobs on unchanged paths | Reduce unnecessary jobs |
| Use smaller runner instance types | Lower per-minute cost |
| Right-size parallelism | Avoid over-provisioning |
| Artifact retention policies | Reduce storage cost |

#### Disaster recovery for CI/CD

| Risk | Mitigation |
|---|---|
| GitLab outage | Document manual deploy procedure |
| Lost pipeline config | `.gitlab-ci.yml` is in version control |
| Runner fleet failure | Multi-provider runner fleet, fallback to shared |
| Secret rotation failure | Documented rotation procedure, monitoring |
| Broken shared template | Version pinning, canary rollout of template updates |

#### Architecture review checklist

- [ ] Are stages and job dependencies designed for speed?
- [ ] Are artifacts scoped and expired appropriately?
- [ ] Is caching effective and key-based?
- [ ] Are secrets protected, masked, and environment-scoped?
- [ ] Are templates versioned and included from a shared project?
- [ ] Are environments protected with required approvers?
- [ ] Is there a rollback strategy?
- [ ] Are security scans included?
- [ ] Is the pipeline cost-efficient?
- [ ] Can a new engineer understand the pipeline quickly?
- [ ] Is there notification on failure?
- [ ] Are child pipelines used where appropriate for monorepos?

#### What expert engineers care about that juniors miss

| Expert concern | Junior blind spot |
|---|---|
| Pipeline cost per deployment | "CI is free" |
| Template versioning and migration | Copy-paste YAML everywhere |
| Compliance enforcement | "Trust the team" |
| Secret sprawl and rotation | "Just add another variable" |
| Runner security boundaries | "Shared runners are fine" |
| Artifact storage growth | No expiration set |
| Pipeline observability | No alerts on failure |
| Reproducible builds | Version drift across runs |
| Recovery time for CI/CD failures | No disaster recovery plan |
| Policy as code | Manual enforcement |

#### 10 advanced engineering discussion topics

1. **Template economics:** Should the platform team maintain CI templates as internal products with SLOs, changelogs, and migration guides?
2. **Runner fleet design:** At what scale do self-hosted runners justify their maintenance cost? How do you measure?
3. **Child pipeline limits:** What complexity threshold makes child pipelines essential for a monorepo?
4. **Multi-project cascading:** How do you prevent cascading failures when one project's pipeline triggers five others?
5. **Compliance pipelines:** How do you balance governance with team autonomy?
6. **Migration strategy:** How would you migrate 100 repos from Jenkins to GitLab CI without disrupting teams?
7. **Secret architecture:** Design secrets management for an org with 200 projects, 10 environments, and 3 cloud providers.
8. **Cost allocation:** How do you attribute CI costs to teams for budget planning?
9. **Incident response:** A malicious commit modifies `.gitlab-ci.yml` to exfiltrate secrets. Design the detection and response playbook.
10. **Pipeline SLOs:** What pipeline reliability and duration SLOs should you define, and how do you measure them?

---

## 3. Setup Guide

### Step 1: Create `.gitlab-ci.yml`

Create the file at the root of your repository:

```yaml
stages:
  - validate
  - build
  - deploy

default:
  image: node:20-alpine
  cache:
    key:
      files:
        - package-lock.json
    paths:
      - node_modules/
```

### Step 2: Recommended pipeline structure

```text
.gitlab-ci.yml          ← main pipeline file
ci/
├── templates/
│   ├── node-setup.yml  ← reusable setup template
│   └── deploy.yml      ← reusable deploy template
└── scripts/
    ├── deploy.sh
    └── generate-pipeline.js
```

```yaml
# .gitlab-ci.yml
include:
  - local: 'ci/templates/node-setup.yml'
  - local: 'ci/templates/deploy.yml'
```

### Step 3: Example pipelines

#### Lint + test + build + deploy

```yaml
stages:
  - validate
  - build
  - deploy

default:
  image: node:20-alpine

.node-cache:
  cache:
    key:
      files: [package-lock.json]
    paths: [node_modules/]

lint:
  extends: .node-cache
  stage: validate
  script:
    - npm ci
    - npm run lint

typecheck:
  extends: .node-cache
  stage: validate
  script:
    - npm ci
    - npm run typecheck

test:
  extends: .node-cache
  stage: validate
  script:
    - npm ci
    - npm test -- --ci
  artifacts:
    when: always
    reports:
      junit: junit.xml
    expire_in: 1 week

build:
  extends: .node-cache
  stage: build
  needs: [lint, typecheck, test]
  script:
    - npm ci
    - npm run build
  artifacts:
    paths: [dist/]
    expire_in: 1 week

deploy-staging:
  stage: deploy
  needs: [build]
  script:
    - echo "Deploy to staging"
  environment:
    name: staging
    url: https://staging.myapp.com
  rules:
    - if: $CI_COMMIT_BRANCH == "main"

deploy-production:
  stage: deploy
  needs: [build]
  script:
    - echo "Deploy to production"
  environment:
    name: production
    url: https://myapp.com
  rules:
    - if: $CI_COMMIT_TAG =~ /^v\d+/
      when: manual
```

### Step 4: Framework-specific examples

#### React app (Vite)

```yaml
stages:
  - validate
  - build
  - deploy

default:
  image: node:20-alpine
  cache:
    key:
      files: [package-lock.json]
    paths: [node_modules/]

lint:
  stage: validate
  script:
    - npm ci
    - npm run lint

test:
  stage: validate
  script:
    - npm ci
    - npm test -- --ci

build:
  stage: build
  needs: [lint, test]
  script:
    - npm ci
    - npm run build
  artifacts:
    paths: [dist/]
    expire_in: 1 week

pages:
  stage: deploy
  needs: [build]
  script:
    - mv dist/ public/
  artifacts:
    paths: [public/]
  rules:
    - if: $CI_COMMIT_BRANCH == "main"
```

#### Next.js app

```yaml
stages:
  - validate
  - build
  - deploy

default:
  image: node:20-alpine
  cache:
    key:
      files: [package-lock.json]
    paths:
      - node_modules/
      - .next/cache/

lint:
  stage: validate
  script:
    - npm ci
    - npm run lint

typecheck:
  stage: validate
  script:
    - npm ci
    - npm run typecheck

test:
  stage: validate
  script:
    - npm ci
    - npm test

build:
  stage: build
  needs: [lint, typecheck, test]
  script:
    - npm ci
    - npm run build
  artifacts:
    paths:
      - .next/
      - public/
    expire_in: 1 week

deploy:
  stage: deploy
  needs: [build]
  image: node:20-alpine
  script:
    - npx vercel deploy --prod --token=$VERCEL_TOKEN
  environment:
    name: production
    url: https://myapp.com
  rules:
    - if: $CI_COMMIT_BRANCH == "main"
```

#### Astro static site

```yaml
stages:
  - validate
  - build
  - deploy

default:
  image: node:20-alpine
  cache:
    key:
      files: [package-lock.json]
    paths: [node_modules/]

lint:
  stage: validate
  script:
    - npm ci
    - npm run lint

build:
  stage: build
  needs: [lint]
  script:
    - npm ci
    - npm run build
  artifacts:
    paths: [dist/]
    expire_in: 1 week

pages:
  stage: deploy
  needs: [build]
  script:
    - mv dist/ public/
  artifacts:
    paths: [public/]
  rules:
    - if: $CI_COMMIT_BRANCH == "main"
```

### Step 5: pnpm / yarn examples

#### pnpm

```yaml
default:
  image: node:20-alpine
  before_script:
    - corepack enable
    - corepack prepare pnpm@9 --activate
    - pnpm config set store-dir .pnpm-store
    - pnpm install --frozen-lockfile
  cache:
    key:
      files: [pnpm-lock.yaml]
    paths: [.pnpm-store/]
```

#### yarn

```yaml
default:
  image: node:20-alpine
  before_script:
    - yarn install --frozen-lockfile
  cache:
    key:
      files: [yarn.lock]
    paths: [node_modules/]
```

### Step 6: Cache strategy

| What to cache | Cache key | Path |
|---|---|---|
| npm | `package-lock.json` hash | `node_modules/` |
| pnpm | `pnpm-lock.yaml` hash | `.pnpm-store/` |
| yarn | `yarn.lock` hash | `node_modules/` |
| Next.js build | lockfile + source hash | `.next/cache/` |

**Cache policies:**
- `pull-push` (default): Restore and update cache.
- `pull`: Only restore (for jobs that shouldn't update).
- `push`: Only update (for a dedicated cache-warming job).

### Step 7: Variables and secrets

1. Go to **Settings → CI/CD → Variables**.
2. Add variables:
   - `VERCEL_TOKEN` — masked, protected.
   - `CLOUDFLARE_API_TOKEN` — masked, protected.
   - `DEPLOY_KEY` — masked, protected.
3. Use `protected` for production secrets (available only on protected branches).
4. Use `masked` to hide values in job logs.

### Step 8: Protected branches and environments

1. **Protected branches:** Settings → Repository → Protected Branches. Protect `main` — require MR, require CI to pass.
2. **Protected environments:** Settings → CI/CD → Environments. Mark `production` as protected, add required approvers.

### Step 9: Docker integration

GitLab provides a built-in container registry at `registry.gitlab.com/<namespace>/<project>`.

```yaml
build-and-push:
  image: docker:24
  services:
    - docker:24-dind
  variables:
    DOCKER_TLS_CERTDIR: "/certs"
  script:
    - docker login -u $CI_REGISTRY_USER -p $CI_REGISTRY_PASSWORD $CI_REGISTRY
    - docker build -t $CI_REGISTRY_IMAGE:$CI_COMMIT_SHA .
    - docker push $CI_REGISTRY_IMAGE:$CI_COMMIT_SHA
  rules:
    - if: $CI_COMMIT_BRANCH == "main"
```

### Step 10: Example project structure

```text
my-project/
├── .gitlab-ci.yml
├── ci/
│   ├── templates/
│   │   └── node-setup.yml
│   └── scripts/
│       └── deploy.sh
├── src/
├── tests/
├── public/
├── package.json
├── package-lock.json
├── Dockerfile
├── .dockerignore
└── README.md
```

### Starter templates by project size

#### Small project (single app)

```yaml
stages:
  - check
  - build

default:
  image: node:20-alpine
  cache:
    key:
      files: [package-lock.json]
    paths: [node_modules/]

lint:
  stage: check
  script:
    - npm ci
    - npm run lint

test:
  stage: check
  script:
    - npm ci
    - npm test

build:
  stage: build
  needs: [lint, test]
  script:
    - npm ci
    - npm run build
  artifacts:
    paths: [dist/]
    expire_in: 1 week
```

#### Medium project (app + deploy)

The full lint/typecheck/test/build/deploy example from Step 3.

#### Large project (monorepo + multi-env)

```yaml
stages:
  - prepare
  - validate
  - build
  - deploy

include:
  - local: 'ci/templates/node-setup.yml'

workflow:
  rules:
    - if: $CI_PIPELINE_SOURCE == "merge_request_event"
    - if: $CI_COMMIT_BRANCH == "main"
    - if: $CI_COMMIT_TAG

generate-pipeline:
  stage: prepare
  image: node:20-alpine
  script:
    - node ci/scripts/generate-pipeline.js > child-pipeline.yml
  artifacts:
    paths: [child-pipeline.yml]
  rules:
    - if: $CI_PIPELINE_SOURCE == "merge_request_event"
      changes:
        - packages/**

trigger-child:
  stage: validate
  trigger:
    include:
      - artifact: child-pipeline.yml
        job: generate-pipeline
    strategy: depend

deploy-staging:
  stage: deploy
  script: ./ci/scripts/deploy.sh staging
  environment:
    name: staging
  rules:
    - if: $CI_COMMIT_BRANCH == "main"

deploy-production:
  stage: deploy
  script: ./ci/scripts/deploy.sh production
  environment:
    name: production
  rules:
    - if: $CI_COMMIT_TAG =~ /^v\d+/
      when: manual
```

---

## 4. Cheatsheet

### Common `.gitlab-ci.yml` syntax

```yaml
stages:              # Define execution order
  - validate
  - build
  - deploy

default:             # Defaults for all jobs
  image: node:20-alpine
  before_script:
    - npm ci

variables:           # Global variables
  NODE_ENV: production

workflow:            # Control when pipelines run
  rules:
    - if: $CI_PIPELINE_SOURCE == "merge_request_event"
    - if: $CI_COMMIT_BRANCH == "main"

include:             # Import external configs
  - local: '/ci/templates.yml'
  - project: 'org/templates'
    ref: v1.0
    file: '/frontend.yml'
```

### Keyword reference

| Keyword | Purpose | Example |
|---|---|---|
| `stages` | Define stage order | `stages: [lint, test, build]` |
| `image` | Docker image for the job | `image: node:20-alpine` |
| `script` | Commands to run | `script: [npm ci, npm test]` |
| `before_script` | Commands before `script` | `before_script: [npm ci]` |
| `after_script` | Commands after `script` (always runs) | `after_script: [echo "done"]` |
| `stage` | Assign job to stage | `stage: build` |
| `rules` | Conditional execution | See rules section |
| `needs` | DAG dependencies | `needs: [lint, test]` |
| `dependencies` | Which artifacts to download | `dependencies: [build]` |
| `artifacts` | Files to preserve | `artifacts: paths: [dist/]` |
| `cache` | Files to cache across runs | See cache section |
| `variables` | Job-level variables | `variables: NODE_ENV: test` |
| `environment` | Deployment target | `environment: name: staging` |
| `extends` | Inherit from template | `extends: .node-setup` |
| `include` | Import external YAML | See include section |
| `trigger` | Trigger child/downstream pipeline | `trigger: project: org/repo` |
| `parallel` | Split job into parallel instances | `parallel: 4` |
| `interruptible` | Allow cancellation on new push | `interruptible: true` |
| `retry` | Retry on failure | `retry: max: 2` |
| `timeout` | Job timeout | `timeout: 10 minutes` |
| `allow_failure` | Don't fail pipeline if this fails | `allow_failure: true` |
| `when` | When to run | `when: manual`, `on_success`, `on_failure`, `always` |
| `resource_group` | Prevent concurrent deploys | `resource_group: production` |
| `services` | Sidecar containers | `services: [docker:24-dind]` |
| `tags` | Select specific runners | `tags: [docker, linux]` |

### Rules syntax

```yaml
rules:
  # Branch condition
  - if: $CI_COMMIT_BRANCH == "main"

  # Tag condition
  - if: $CI_COMMIT_TAG =~ /^v\d+\.\d+\.\d+$/

  # MR pipeline
  - if: $CI_PIPELINE_SOURCE == "merge_request_event"

  # Manual trigger
  - if: $CI_COMMIT_BRANCH == "main"
    when: manual

  # Path changes
  - changes:
      - src/**
      - package.json

  # Never run
  - when: never

  # Combine conditions
  - if: $CI_COMMIT_BRANCH == "main"
    changes:
      - src/**
```

### Artifacts patterns

```yaml
artifacts:
  paths:
    - dist/
    - coverage/
  expire_in: 1 week
  when: always              # Upload even on failure

# JUnit test reports (shown in MR)
artifacts:
  reports:
    junit: junit.xml
    coverage_report:
      coverage_format: cobertura
      path: coverage/cobertura.xml
```

### Cache patterns

```yaml
# npm
cache:
  key:
    files: [package-lock.json]
  paths: [node_modules/]

# pnpm
cache:
  key:
    files: [pnpm-lock.yaml]
  paths: [.pnpm-store/]

# Multiple caches
cache:
  - key:
      files: [package-lock.json]
    paths: [node_modules/]
  - key: next-cache-$CI_COMMIT_REF_SLUG
    paths: [.next/cache/]
```

### Docker in GitLab CI

```yaml
# Build and push to GitLab Container Registry
build-image:
  image: docker:24
  services:
    - docker:24-dind
  variables:
    DOCKER_TLS_CERTDIR: "/certs"
  script:
    - docker login -u $CI_REGISTRY_USER -p $CI_REGISTRY_PASSWORD $CI_REGISTRY
    - docker build -t $CI_REGISTRY_IMAGE:$CI_COMMIT_SHA .
    - docker push $CI_REGISTRY_IMAGE:$CI_COMMIT_SHA

# Using Kaniko (no Docker daemon needed)
build-image-kaniko:
  image:
    name: gcr.io/kaniko-project/executor:v1.21.0-debug
    entrypoint: [""]
  script:
    - |
      /kaniko/executor \
        --context $CI_PROJECT_DIR \
        --dockerfile $CI_PROJECT_DIR/Dockerfile \
        --destination $CI_REGISTRY_IMAGE:$CI_COMMIT_SHA
```

### Common deployment patterns

```yaml
# Deploy to GitLab Pages
pages:
  stage: deploy
  script:
    - mv dist/ public/
  artifacts:
    paths: [public/]
  rules:
    - if: $CI_COMMIT_BRANCH == "main"

# Deploy to Cloudflare Pages
deploy-cloudflare:
  stage: deploy
  image: node:20-alpine
  script:
    - npx wrangler pages deploy dist/ --project-name=my-site
  environment:
    name: production
    url: https://myapp.com
  variables:
    CLOUDFLARE_API_TOKEN: $CLOUDFLARE_API_TOKEN

# Deploy via SSH
deploy-ssh:
  stage: deploy
  script:
    - apt-get update && apt-get install -y openssh-client
    - eval $(ssh-agent -s)
    - echo "$SSH_PRIVATE_KEY" | ssh-add -
    - scp -r dist/ deploy@server:/var/www/app/
```

### Debugging commands

```bash
# In a job script
- echo "Branch: $CI_COMMIT_BRANCH"
- echo "SHA: $CI_COMMIT_SHA"
- echo "Source: $CI_PIPELINE_SOURCE"
- echo "MR: $CI_MERGE_REQUEST_IID"
- node --version
- npm --version
- ls -la
- env | sort | grep CI_
```

### Common pipeline failures

| Error | Cause | Fix |
|---|---|---|
| YAML syntax error | Indentation or structure issue | Use GitLab CI Lint (CI/CD → Editor → Lint) |
| `job: script not found` | Missing `script` keyword | Every job needs `script:` |
| Job stuck / pending | No runner available with matching tags | Check runner tags and availability |
| `npm ERR! could not determine executable` | Wrong image or missing deps | Verify `image:` and `before_script` |
| Artifact not found in downstream job | Wrong `dependencies` or `needs` | Verify artifact paths and job references |
| Cache not restoring | Key mismatch or cache expired | Verify `cache:key` matches across jobs |
| Protected variable missing | Job running on unprotected branch | Use protected branches or unprotect the variable |
| Docker build fails | DinD not configured | Add `services: [docker:24-dind]` and TLS cert dir |

### Performance optimization

| Technique | Impact |
|---|---|
| Cache with lockfile key | 30-60% faster installs |
| `needs` (DAG mode) | Jobs start sooner |
| `interruptible: true` | Cancel old pipelines |
| `parallel:` | Split tests across runners |
| `changes:` rules | Skip unchanged packages |
| Smaller images | Faster container pull |
| `expire_in` on artifacts | Reduce storage |
| `policy: pull` on deploy jobs | Don't re-upload cache |

### Security best practices

| Practice | Priority |
|---|---|
| Use `rules` not `only/except` | High |
| Mask and protect sensitive variables | Critical |
| Pin Docker image versions | High |
| Use protected environments for production | Critical |
| Enable SAST and dependency scanning | High |
| Use OIDC for cloud access | High |
| Audit variable access regularly | Medium |
| Use `resource_group` for deploy jobs | Medium |
| Review `.gitlab-ci.yml` changes in MRs | High |

---

## 5. Real-World Engineering Mindset

### CI for React / Next.js / Astro

**Problem:** Every MR needs fast, reliable feedback on code quality.

**Strategies:**

| Strategy | Pros | Cons |
|---|---|---|
| Single job: lint → test → build | Simple | Slower, sequential feedback |
| Parallel jobs with `needs` | Fast feedback per check | More YAML, repeated installs |
| Template-based with `extends` | DRY, maintainable | Slight learning curve |

**By team size:**
- **Small:** Single job or two stages (validate + build).
- **Medium:** Parallel validation jobs, shared template, cache.
- **Large:** Reusable templates from shared project, child pipelines for monorepo.

**Senior choice:** Parallel lint/typecheck/test in `validate` stage, build in `build` stage with `needs`, cache on lockfile hash. Add `interruptible: true` to save minutes.

---

### Deploying static sites

**Problem:** Ship HTML/CSS/JS reliably to a CDN.

**Strategies:**

| Strategy | Pros | Cons |
|---|---|---|
| GitLab Pages | Free, integrated, zero config | GitLab-hosted only |
| Cloudflare Pages (via CLI) | Edge CDN, fast | Requires API token |
| AWS S3 + CloudFront | Full control | More setup |
| Vercel (via CLI) | Great DX | External platform |

**Senior choice:** GitLab Pages for simple static sites (Astro, Vite React). Cloudflare Pages for edge performance. Vercel for Next.js with SSR.

---

### Deploying Docker containers

**Problem:** Build images reproducibly, scan, and push to registry.

**Strategies:**

| Strategy | Pros | Cons |
|---|---|---|
| Docker-in-Docker (DinD) | Standard, well-documented | Privileged mode needed |
| Kaniko | No privileged mode, more secure | Slightly different build behavior |
| Buildah | Rootless, OCI-compliant | Less common in GitLab CI |

```yaml
# Kaniko — no DinD required
build:
  image:
    name: gcr.io/kaniko-project/executor:v1.21.0-debug
    entrypoint: [""]
  script:
    - |
      /kaniko/executor \
        --context $CI_PROJECT_DIR \
        --dockerfile Dockerfile \
        --destination $CI_REGISTRY_IMAGE:$CI_COMMIT_SHA \
        --cache=true \
        --cache-repo=$CI_REGISTRY_IMAGE/cache
```

**Senior choice:** Kaniko for security-conscious teams (no privileged containers). DinD for simplicity when privileged is acceptable.

---

### Monorepo selective pipelines

**Problem:** Don't rebuild everything when only one package changed.

**Strategies:**

| Strategy | Pros | Cons |
|---|---|---|
| `rules: changes:` | Simple | Doesn't handle transitive deps |
| Dynamic child pipelines | Most flexible | More complex setup |
| Turborepo/Nx integration | Build-tool aware | Tool-specific |

**Senior choice:** `rules: changes:` for simple monorepos. Dynamic child pipelines with change detection scripts for complex ones.

---

### Merge request preview deployment

**Problem:** Reviewers want to see changes live before approving.

```yaml
deploy-preview:
  stage: deploy
  script:
    - npx wrangler pages deploy dist/ --project-name=myapp --branch=$CI_MERGE_REQUEST_SOURCE_BRANCH_NAME
  environment:
    name: preview/$CI_MERGE_REQUEST_IID
    url: https://$CI_MERGE_REQUEST_SOURCE_BRANCH_NAME.myapp.pages.dev
    on_stop: stop-preview
  rules:
    - if: $CI_PIPELINE_SOURCE == "merge_request_event"

stop-preview:
  stage: deploy
  script:
    - echo "Cleanup preview"
  environment:
    name: preview/$CI_MERGE_REQUEST_IID
    action: stop
  rules:
    - if: $CI_PIPELINE_SOURCE == "merge_request_event"
      when: manual
```

**Senior choice:** Use platform-native previews (Vercel, Cloudflare) for the best DX. Use GitLab environments with `on_stop` for cleanup.

---

### Environment promotion

**Problem:** Code should flow through dev → staging → production safely.

**Senior choice:** Auto-deploy to staging on main. Manual gate for production with protected environment. Track all deployments in GitLab Environments for rollback.

---

### Database migration during deployment

**Problem:** Migration failure can break the app.

**Strategies:**

| Strategy | Risk level | Trade-off |
|---|---|---|
| Migrate before deploy | Medium | Migration applied even if deploy fails |
| Deploy then migrate | Medium | App may error if schema mismatch |
| Expand/contract (backward-compatible) | Low | Requires discipline |

**Senior choice:** Expand/contract. Make migrations backward-compatible so old and new code coexist. Always test migrations in staging first.

---

### Release automation

```yaml
release:
  stage: release
  image: registry.gitlab.com/gitlab-org/release-cli:latest
  rules:
    - if: $CI_COMMIT_TAG =~ /^v\d+/
  script:
    - echo "Creating release"
  release:
    tag_name: $CI_COMMIT_TAG
    name: "Release $CI_COMMIT_TAG"
    description: "Automated release for $CI_COMMIT_TAG"
```

**Senior choice:** Tag-based releases with automated changelog from conventional commits.

---

### Canary deployment

**Problem:** Reduce risk by releasing to a subset of users first.

**Senior choice:** Use feature flags or traffic splitting. GitLab's incremental rollout is available for Kubernetes deployments.

---

### Blue/Green deployment

**Problem:** Need instant rollback capability.

**Senior choice:** Maintain two environments. Deploy to the inactive one, verify, then switch traffic. Requires infrastructure support.

---

### Rollback after failed release

**Problem:** Production is broken after deploy.

**Strategies:**

| Strategy | Recovery time |
|---|---|
| GitLab environment rollback | Minutes |
| Re-deploy previous image tag | Minutes |
| Git revert + pipeline | 5-10 minutes |
| Feature flag disable | Seconds |

**Senior choice:** Use GitLab's built-in environment rollback for immediate recovery. Test rollback procedures regularly.

---

### Scheduled jobs

```yaml
nightly-tests:
  stage: test
  script:
    - npm ci
    - npm run test:e2e
  rules:
    - if: $CI_PIPELINE_SOURCE == "schedule"
```

Set up in **CI/CD → Schedules**. Common patterns: nightly E2E tests, weekly dependency audits, monthly security scans.

---

### Nightly testing

**Senior choice:** Run the broadest test suite nightly — E2E, full matrix, integration tests. Run focused tests on MRs. Alert the team on failure.

---

### Security scanning

```yaml
include:
  - template: Security/SAST.gitlab-ci.yml
  - template: Security/Dependency-Scanning.gitlab-ci.yml
  - template: Security/Secret-Detection.gitlab-ci.yml
```

**Senior choice:** Include GitLab security templates. Run SAST and dependency scanning on MRs. Review vulnerability reports in merge request widgets.

---

### Dependency updates

**Senior choice:** Use GitLab's Dependency Bot or Renovate Bot. Auto-merge patches that pass CI. Manually review major updates. Group minor updates.

---

## 6. Brainstorm / Open Questions

### Architecture

1. Should this be one pipeline or multiple pipelines?
2. When should you use child pipelines vs. multi-project pipelines?
3. At what complexity should you extract templates to a shared project?
4. Should every service have its own `.gitlab-ci.yml` or share one?
5. How do you balance standardization with team autonomy?
6. When should a child pipeline be introduced for a monorepo?
7. What is the right granularity for stages?

### Scaling

8. What happens when your pipeline takes 30 minutes instead of 3?
9. How many concurrent jobs can your runner fleet handle at peak?
10. When should you move from shared runners to self-hosted?
11. How do you handle 20 teams pushing simultaneously?
12. How do you prevent one team's heavy pipeline from starving others?
13. What is the right level of parallelism for test suites?
14. How do you measure and reduce pipeline queue time?

### Security

15. How can secrets leak in CI logs even when masked?
16. Which jobs should never have access to production secrets?
17. Should all pipeline config changes require MR approval?
18. How do you detect if a `.gitlab-ci.yml` change is malicious?
19. What happens if a runner is compromised?
20. How do you handle secrets rotation across 100 projects?
21. When should OIDC replace static cloud credentials?

### DX / Maintainability

22. Can a new engineer understand the pipeline in 10 minutes?
23. How do you prevent "YAML sprawl" across teams?
24. What should be in shared templates vs. project-specific config?
25. How do you test pipeline changes safely?
26. How do you version and migrate shared templates?
27. How should a monorepo detect which apps changed?
28. What is the right level of abstraction for CI templates?

### Cost

29. Which jobs cost the most without proportional value?
30. Should full test suites run on every MR or only on main?
31. Are caches actually saving you time? How do you measure?
32. When do self-hosted runners become cheaper than shared?
33. How much does artifact storage cost at your scale?
34. What is the developer productivity cost of slow pipelines?

### Reliability

35. What happens if deployment succeeds but migration fails?
36. How do you design for pipeline re-runs after flaky failures?
37. How do you ensure artifacts are traceable and reproducible?
38. What should be retried automatically vs. investigated manually?
39. How do you detect partial failures that look successful?
40. What is your rollback RTO (Recovery Time Objective)?

### Release Strategy

41. When should you release on merge vs. on tag?
42. Should production deploy require manual approval?
43. How do you coordinate releases across dependent services?
44. What does a safe canary look like for your stack?
45. How do you reconcile fast shipping with deployment safety?

---

## 7. Practice Questions

### Beginner (Level 1)

**Q1. Single choice:** Where does the GitLab CI/CD configuration file live?

- A. `src/.ci.yml`
- B. `.gitlab-ci.yml` at the repository root
- C. `.github/workflows/ci.yml`
- D. `ci/config.yml`

<details><summary>Answer</summary>B. GitLab reads <code>.gitlab-ci.yml</code> from the repository root.</details>

---

**Q2. True/False:** Jobs in the same stage run sequentially.

<details><summary>Answer</summary>False. Jobs in the same stage run <strong>in parallel</strong>. Stages execute sequentially — the next stage starts only after all jobs in the current stage succeed.</details>

---

**Q3. Fill in the blank:** Every job must have a `_______` keyword.

<details><summary>Answer</summary><code>script</code>. Without <code>script</code>, GitLab doesn't know what commands to run.</details>

---

**Q4. Single choice:** What command should you use instead of `npm install` in CI?

- A. `npm update`
- B. `npm ci`
- C. `npm start`
- D. `npm init`

<details><summary>Answer</summary>B. <code>npm ci</code> performs a clean, deterministic install from the lockfile.</details>

---

**Q5. Debugging:** Your pipeline shows "Job is stuck." What should you check?

<details><summary>Answer</summary>
1. Check if any runners are available for the project.<br>
2. Check if the job requires specific runner <code>tags:</code> that no runner matches.<br>
3. Check if runners are online in Settings → CI/CD → Runners.
</details>

---

**Q6. Multiple choice:** What does the `image` keyword specify?

- A. The Git branch to use
- B. The Docker image the job runs inside
- C. The artifact format
- D. The environment name

<details><summary>Answer</summary>B. <code>image</code> specifies the Docker image used as the execution environment for the job.</details>

---

**Q7. Matching:** Match each concept to its meaning.

| Concept | Meaning |
|---|---|
| A. Pipeline | 1. A file produced by a job for downstream use |
| B. Stage | 2. The agent that executes jobs |
| C. Runner | 3. A logical grouping of parallel jobs |
| D. Artifact | 4. The full execution of .gitlab-ci.yml for a commit |

<details><summary>Answer</summary>A→4, B→3, C→2, D→1</details>

---

**Q8. True/False:** If you don't specify `stage:` for a job, it defaults to the `test` stage.

<details><summary>Answer</summary>True. Jobs without an explicit <code>stage:</code> are assigned to the <code>test</code> stage by default.</details>

---

**Q9. Scenario:** You push to a branch. The pipeline runs but no jobs execute. The pipeline is empty. What is likely wrong?

<details><summary>Answer</summary>
Your <code>workflow:rules</code> or job <code>rules</code> are filtering out the current pipeline source/branch. Check that your rules match the branch or event type being triggered.
</details>

---

**Q10. Fill in the blank:** To specify which Docker image a job runs in, use the `_______` keyword.

<details><summary>Answer</summary><code>image</code></details>

---

### Junior (Level 2)

**Q11. Single choice:** What is the difference between `cache` and `artifacts`?

- A. They are the same thing
- B. Cache persists across pipelines for speed; artifacts pass files between jobs
- C. Artifacts persist across pipelines; cache passes files between jobs
- D. Cache is for Docker images; artifacts are for code

<details><summary>Answer</summary>B. Cache is best-effort and speeds up repeated installs across pipelines. Artifacts are guaranteed and pass files between jobs within (or across) pipelines.</details>

---

**Q12. True/False:** `needs: [build]` means the job waits for the entire previous stage to complete.

<details><summary>Answer</summary>False. <code>needs</code> creates a DAG dependency — the job starts as soon as the specified jobs finish, regardless of stage completion.</details>

---

**Q13. Debugging:** A job can't find `$DEPLOY_TOKEN`, but you set it as a protected variable. The pipeline runs on a feature branch. Why?

<details><summary>Answer</summary>Protected variables are only available on protected branches and protected tags. A feature branch is not protected, so the variable is unavailable. Either unprotect the variable or run the job only on protected branches.</details>

---

**Q14. Fill in the blank:** To prevent duplicate pipelines for push and MR events, define `workflow: _______`.

<details><summary>Answer</summary><code>rules</code>. Define <code>workflow:rules</code> to control when pipelines are created (e.g., only for MR events and pushes to main).</details>

---

**Q15. Scenario:** You want to pass the `dist/` folder from a `build` job to a `deploy` job. Which keyword do you use?

<details><summary>Answer</summary><code>artifacts</code>. Define <code>artifacts: paths: [dist/]</code> in the build job. The deploy job (in a later stage or with <code>needs: [build]</code>) will automatically download it.</details>

---

**Q16. Multiple choice:** Which `rules` condition runs a job only on merge requests?

- A. `if: $CI_COMMIT_BRANCH == "merge_request"`
- B. `if: $CI_PIPELINE_SOURCE == "merge_request_event"`
- C. `if: $CI_MERGE_REQUEST == "true"`
- D. `only: merge_requests`

<details><summary>Answer</summary>B. <code>$CI_PIPELINE_SOURCE == "merge_request_event"</code> is the correct rules-based approach. D (<code>only:</code>) works but is deprecated in favor of <code>rules:</code>.</details>

---

**Q17. Matching:** Match the cache policy to its behavior.

| Policy | Behavior |
|---|---|
| A. `pull-push` | 1. Only upload cache at end |
| B. `pull` | 2. Download at start, upload at end |
| C. `push` | 3. Only download cache at start |

<details><summary>Answer</summary>A→2, B→3, C→1</details>

---

**Q18. True/False:** `extends: .template` works like class inheritance — child overrides parent values.

<details><summary>Answer</summary>True. Properties defined in the job override the template's values. Arrays and mappings are merged or overridden depending on the key.</details>

---

**Q19. Scenario:** Your cache key is `default`. Every branch shares the same cache. Sometimes the cache is corrupted, causing failures. What should you fix?

<details><summary>Answer</summary>Use a file-based cache key: <code>key: files: [package-lock.json]</code>. This ties the cache to the lockfile hash, so different dependency versions get different caches.</details>

---

**Q20. Single choice:** To run a job only when files in `src/` changed, use:

- A. `rules: - changes: [src/**]`
- B. `rules: - if: src changed`
- C. `only: changes: [src/]`
- D. `when: src_changed`

<details><summary>Answer</summary>A. <code>rules: - changes: [src/**]</code> is the correct syntax. C uses the deprecated <code>only:</code> syntax.</details>

---

### Senior / Expert (Level 3–4)

**Q21. Scenario:** You have a monorepo with 20 packages. `rules: changes:` misses changes in shared dependencies. What approach do you use?

<details><summary>Answer</summary>Dynamic child pipelines. Write a script that analyzes the dependency graph, detects affected packages from changed files, generates a <code>.yml</code> with only the needed jobs, and triggers it as a child pipeline.</details>

---

**Q22. True/False:** Protected variables are available in pipelines triggered by unprotected branches.

<details><summary>Answer</summary>False. Protected variables are only available in pipelines running on protected branches or protected tags.</details>

---

**Q23. Design question:** Deployment succeeded, but the database migration failed midway. Users see errors. What went wrong and how do you prevent it?

<details><summary>Answer</summary>
1. The migration wasn't wrapped in a transaction.<br>
2. The migration wasn't backward-compatible (expand/contract pattern not used).<br>
3. There was no health check after migration to gate the traffic switch.<br>
Prevention: Use backward-compatible migrations, test in staging, gate deployment on health checks, and have a rollback plan.
</details>

---

**Q24. Single choice:** Which is more secure for building Docker images in GitLab CI?

- A. Docker-in-Docker (DinD) with privileged mode
- B. Kaniko (no privileged mode)
- C. Running Docker on the host shell executor
- D. They are all equally secure

<details><summary>Answer</summary>B. Kaniko runs without privileged mode and without a Docker daemon, reducing the attack surface. DinD requires privileged mode which is a security risk. Shell executor has no isolation.</details>

---

**Q25. Scenario:** A team pushes to main 50 times a day. Each pipeline takes 15 minutes and costs $0.10/minute on shared runners. Estimate the monthly CI cost and propose optimizations.

<details><summary>Answer</summary>
Cost: 50 pushes × 15 min × $0.10 × 30 days = $2,250/month.<br>
Optimizations:<br>
1. <code>interruptible: true</code> — cancel superseded pipelines (could save 30-50%).<br>
2. Caching — reduce install time by 30-60%.<br>
3. <code>needs</code> DAG — reduce total pipeline time.<br>
4. <code>changes:</code> rules — skip unchanged packages.<br>
5. Self-hosted runners at this scale would likely be cheaper.
</details>

---

**Q26. Fill in the blank:** To prevent two deploy jobs from running concurrently, use `resource_group: _______`.

<details><summary>Answer</summary>A meaningful group name like <code>production</code>. <code>resource_group: production</code> ensures only one deploy to production runs at a time.</details>

---

**Q27. Design question:** You need to migrate 50 projects from Jenkins to GitLab CI. How do you plan it?

<details><summary>Answer</summary>
1. Create shared CI templates for common patterns (frontend, backend, Docker).<br>
2. Start with low-risk, small projects to validate templates.<br>
3. Run Jenkins and GitLab CI in parallel for a transition period.<br>
4. Provide team-by-team migration support and documentation.<br>
5. Track migration progress and collect feedback.<br>
6. Decommission Jenkins only after all projects pass validation.
</details>

---

**Q28. Multiple choice:** Which features make GitLab CI/CD better for monorepos than GitHub Actions? (Select all)

- A. Dynamic child pipelines
- B. `rules: changes:` at job level
- C. Multi-project pipelines
- D. Built-in marketplace with 20,000+ actions

<details><summary>Answer</summary>A, B, and C. Dynamic child pipelines and job-level <code>changes:</code> rules are strong monorepo features. Multi-project pipelines coordinate across repos. D is a GitHub Actions advantage, not GitLab.</details>

---

**Q29. Debugging:** A deploy to production ran without the required manual approval. How could this happen?

<details><summary>Answer</summary>
1. The environment is not configured as protected.<br>
2. The user has the right role to bypass protection.<br>
3. The <code>rules:</code> don't include <code>when: manual</code>.<br>
4. The pipeline was triggered via API with sufficient permissions.<br>
Check environment protection settings and job rules.
</details>

---

**Q30. Design question:** Design an incident response plan for when a CI template update breaks pipelines across 100 projects.

<details><summary>Answer</summary>
1. <strong>Detection:</strong> Monitor pipeline failure rate. Alert on sudden spike.<br>
2. <strong>Containment:</strong> Projects pin to template version — unaffected until they update. For those affected, revert the template change immediately.<br>
3. <strong>Recovery:</strong> Push a fix to the template repo. Projects re-run pipelines.<br>
4. <strong>Prevention:</strong> Version pin all template references. Test template changes in a canary project first. Require MR review for template changes. Maintain a changelog.
</details>

---

## 8. Personalized Recommendations

### GitLab CI/CD patterns most useful for your stack

1. **MR pipelines:** Lint + typecheck + test + build on every merge request.
2. **Lockfile-based caching:** Speed up installs with `cache: key: files:`.
3. **Artifacts for build output:** Pass `dist/` between stages.
4. **GitLab Pages deployment:** Free static hosting for Astro/React.
5. **Environment promotion:** Auto-staging on main, manual production on tag.
6. **`extends` templates:** DRY job definitions across similar jobs.
7. **`needs` DAG:** Faster pipelines by skipping stage barriers.
8. **Interruptible jobs:** Cancel superseded pipelines on rapid pushes.

### What to learn first

| Priority | Topic |
|---|---|
| 1 | Basic `.gitlab-ci.yml` structure, stages, jobs |
| 2 | Cache and artifacts |
| 3 | `rules` for conditional execution |
| 4 | `extends` for DRY templates |
| 5 | `needs` for DAG mode |
| 6 | MR pipelines (`workflow:rules`) |
| 7 | Environments and deployment |
| 8 | Variables and secrets |
| 9 | Docker integration |
| 10 | `include` for shared templates |

### Which pipelines to build first

| Order | Pipeline | Why |
|---|---|---|
| 1st | Basic CI: lint + test + build | Foundation |
| 2nd | MR pipeline with `workflow:rules` | Prevent duplicates, MR integration |
| 3rd | Deploy to staging on main | Close the loop |
| 4th | Deploy to production on tag | Release process |
| 5th | Preview deployment on MR | Better code review |
| 6th | Nightly/scheduled security scan | Security posture |
| 7th | Release automation | Professional releases |

### Common mistakes frontend engineers make

| Mistake | Why it happens | Fix |
|---|---|---|
| Not defining `stages` | Seems optional | Always define stages explicitly |
| Using `only/except` | Found in old tutorials | Use `rules` instead |
| No `workflow:rules` | Don't know about duplicate pipelines | Define workflow rules |
| Not caching | "It works without it" | Cache on lockfile hash |
| No `expire_in` on artifacts | Seems harmless | Set expiration to avoid storage bloat |
| Using `npm install` | Habit | Use `npm ci` |
| Secrets in YAML | Quick and dirty | Use CI/CD variables in settings |
| Ignoring MR pipeline features | Not aware | Use test reports, code quality integration |

### How to evolve from simple to production-grade

```text
Phase 1: Basic CI
  └── lint + test + build in stages

Phase 2: Optimized CI
  └── cache, needs (DAG), interruptible, MR pipelines

Phase 3: Deployment
  └── staging auto-deploy, production manual gate

Phase 4: Templates
  └── extends, include from shared project

Phase 5: Security
  └── protected environments, masked variables, SAST scanning

Phase 6: Automation
  └── release automation, scheduled scans, dependency updates

Phase 7: Monorepo
  └── changes rules, child pipelines

Phase 8: Platform
  └── org-wide templates, compliance pipelines, runner fleet
```

### 30-day learning plan

#### Week 1: Foundations (Days 1–7)

| Day | Task | Deliverable |
|---|---|---|
| 1 | Read Big Picture section, understand concepts | Mental model |
| 2 | Create first `.gitlab-ci.yml` with one job | Working pipeline |
| 3 | Add lint, test, and build in separate stages | Multi-stage pipeline |
| 4 | Add caching on lockfile hash | Faster installs |
| 5 | Add `needs` to skip stage barriers | DAG pipeline |
| 6 | Break a job intentionally, study failure logs | Debugging confidence |
| 7 | Add `extends` for shared setup template | DRY pipeline |

#### Week 2: Team workflows (Days 8–14)

| Day | Task | Deliverable |
|---|---|---|
| 8 | Add `workflow:rules` for MR pipelines | No duplicate pipelines |
| 9 | Add `rules` for conditional execution | Branch/event-based jobs |
| 10 | Set up CI/CD variables (secrets) | Secure config |
| 11 | Add artifacts for build output | Build passed between stages |
| 12 | Add test reports (JUnit format) | Reports in MR widget |
| 13 | Add `interruptible: true` | Cancel old pipelines |
| 14 | Review and document your pipeline | Maintainable system |

#### Week 3: Deployment (Days 15–21)

| Day | Task | Deliverable |
|---|---|---|
| 15 | Deploy to GitLab Pages (Astro/React) | Working deployment |
| 16 | Add staging environment on main | Environment tracking |
| 17 | Add production environment with manual gate | Safe production deploy |
| 18 | Add Slack/notification on failure | Team awareness |
| 19 | Add Docker image build and push | Container pipeline |
| 20 | Add scheduled pipeline for security scan | Nightly scans |
| 21 | Add release automation on tag | Versioned releases |

#### Week 4: Advanced (Days 22–30)

| Day | Task | Deliverable |
|---|---|---|
| 22 | Study `include` from shared templates | Reusable patterns |
| 23 | Create a shared template project | Org-wide reuse |
| 24 | Add `rules: changes:` for monorepo | Selective CI |
| 25 | Study child pipelines | Dynamic pipeline generation |
| 26 | Study self-hosted runners | Architecture knowledge |
| 27 | Add OIDC for cloud authentication | Better security |
| 28 | Audit pipeline for security checklist | Hardened pipeline |
| 29 | Calculate and optimize pipeline cost | Cost awareness |
| 30 | Write architecture decision record | Documentation |

---

## Summary, Next Steps, and Advanced Topics

### Concise Summary

GitLab CI/CD is a batteries-included automation platform deeply integrated with the GitLab ecosystem. For a frontend engineer, the key path to mastery is:

1. **Start** with a simple pipeline: lint, test, build in stages.
2. **Optimize** with caching, DAG (`needs`), and `interruptible`.
3. **Deploy** with environments, protection rules, and artifacts.
4. **Scale** with `extends`, `include`, and shared templates.
5. **Harden** with protected variables, OIDC, and security scanning.
6. **Govern** with compliance pipelines and org-wide templates.

The key mindset: your pipeline is production infrastructure. Treat `.gitlab-ci.yml` with the same rigor as application code.

### Next Steps

1. Create a `.gitlab-ci.yml` for your current project today.
2. Add caching and `workflow:rules`.
3. Add a deployment to staging with an environment.
4. Set up protected environment for production.
5. Study `include` and build shared templates.
6. Add security scanning and scheduled pipelines.

### Suggested Advanced Topics

| Topic | Why it matters |
|---|---|
| Dynamic child pipelines for monorepos | Scale CI for large codebases |
| GitLab compliance pipelines | Enforce standards across projects |
| Multi-project pipeline orchestration | Coordinate dependent services |
| OIDC-based cloud authentication | Eliminate static credentials |
| Kubernetes executor for runners | Auto-scaling runner fleet |
| GitLab Container Registry integration | Built-in image management |
| Review Apps with dynamic environments | Per-MR preview environments |
| Merge trains | Safe continuous delivery to main |
| Feature flags (GitLab) | Decouple deployment from release |
| Pipeline analytics and insights | Data-driven pipeline optimization |
| Kaniko and rootless image builds | Secure container builds |
| GitLab Pages advanced usage | Custom domains, redirects, SPA routing |
| Vault integration for secrets | Enterprise secret management |
| Auto DevOps | Zero-config CI/CD for standard apps |
| Pipeline efficiency dashboard | Monitor cost and duration trends |
