# GitLab Container Registry — Complete Deep-Dive Engineering Guide

> For a frontend engineer (React / Next.js / Astro / TypeScript) moving toward DevOps, Docker, release engineering, deployment, and platform engineering.

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

### 1.1 What GitLab Container Registry Is

GitLab Container Registry is a built-in Docker image storage service integrated directly into every GitLab project. It stores, manages, and distributes Docker (OCI) container images — the packaged, runnable snapshots of your application and its environment.

**The npm analogy:** If npm registry stores JavaScript packages (`react@18.2.0`), GitLab Container Registry stores Docker images (`my-app:v1.2.3`). Just as you `npm publish` a package and `npm install` it elsewhere, you `docker push` an image and `docker pull` it on a server. The registry is the warehouse in the middle.

### 1.2 Why a Container Registry Exists

Without a registry, you'd build a Docker image on your laptop and have no way to share it with a CI runner, a staging server, or a production cluster. A registry solves this:

1. **Central storage** — One place for all image versions.
2. **Distribution** — Any authorized machine can pull images.
3. **Versioning** — Tags and digests identify exact versions.
4. **Access control** — Private images, scoped tokens, audit logs.
5. **Integration** — CI/CD pipelines push images; deployments pull them.

### 1.3 How It Relates to Other Systems

#### Docker Image

A Docker image is a read-only, layered filesystem snapshot that contains your application code, runtime, dependencies, and OS libraries. The registry stores these images.

**Analogy:** An image is like a published npm package tarball — a self-contained, versioned artifact.

#### Docker Hub

Docker Hub is the default public registry (`docker pull nginx`). GitLab Container Registry is a private, project-scoped alternative. You use Docker Hub for public base images; you use GitLab's registry for your own application images.

**Analogy:** Docker Hub is like npmjs.com (public). GitLab Container Registry is like a private npm registry (Verdaccio, GitHub Packages) — same protocol, different access scope.

#### GitLab CI/CD

GitLab CI/CD pipelines build your code and push images to the registry. The registry is the handoff point between "code was built" and "code is deployed." CI pushes; deployment pulls.

#### Deployment Pipeline

The registry sits between build and deploy:

```text
Build stage → docker push → Registry → docker pull → Deploy stage
```

Without a registry, there's no clean way for the deploy step to get the built artifact.

#### Kubernetes / Docker Compose

Both pull images from registries:
- **Docker Compose:** `image: registry.gitlab.com/org/app:v1.2.0`
- **Kubernetes:** Pod spec references the same image URL, plus an `imagePullSecret` for authentication.

### 1.4 Core Terminology

| Term | Definition | npm Analogy |
|---|---|---|
| **Image** | A packaged, layered filesystem with your app and its runtime | An npm package tarball |
| **Tag** | A human-readable label pointing to a specific image version | A version string like `18.2.0` |
| **Registry** | The server that stores and serves images | `registry.npmjs.org` |
| **Repository** | A collection of related image tags under one name | A package name like `react` |
| **Digest** | A content-addressable SHA256 hash uniquely identifying an image | An npm integrity hash |
| **`latest` tag** | A mutable tag that conventionally points to the newest image | `@latest` dist-tag in npm |
| **Semantic version tag** | An immutable tag like `v1.2.3` following semver | `react@18.2.0` |

**Key insight:** A tag is a pointer that can be moved. A digest is permanent. `my-app:latest` might point to different images over time; `my-app@sha256:abc123...` always points to the same one.

**Analogy:** `latest` is like a symlink that gets repointed. A digest is like a commit SHA — immutable.

### 1.5 The Lifecycle

```text
┌──────────────────────────────────────────────────────────────┐
│ SOURCE CODE                                                  │
│                                                              │
│  src/  package.json  Dockerfile  .gitlab-ci.yml              │
│                                                              │
└────────────────────────┬─────────────────────────────────────┘
                         │ git push
                         ▼
┌──────────────────────────────────────────────────────────────┐
│ GITLAB CI/CD PIPELINE                                        │
│                                                              │
│  Stage: build                                                │
│  ┌────────────────────────────────────────────┐              │
│  │ docker build -t registry.gitlab.com/       │              │
│  │   org/app:v1.2.0 .                         │              │
│  │ docker push registry.gitlab.com/           │              │
│  │   org/app:v1.2.0                           │              │
│  └────────────────────────────────────────────┘              │
│                                                              │
└────────────────────────┬─────────────────────────────────────┘
                         │ push
                         ▼
┌──────────────────────────────────────────────────────────────┐
│ GITLAB CONTAINER REGISTRY                                    │
│                                                              │
│  registry.gitlab.com/org/app                                 │
│    ├── :v1.2.0   (sha256:abc123...)                         │
│    ├── :v1.1.0   (sha256:def456...)                         │
│    ├── :latest   → points to v1.2.0                         │
│    └── :feature-login  (branch preview)                      │
│                                                              │
└────────────────────────┬─────────────────────────────────────┘
                         │ pull
                         ▼
┌──────────────────────────────────────────────────────────────┐
│ DEPLOYMENT TARGET                                            │
│                                                              │
│  Kubernetes  /  Docker Compose  /  Cloud Run  /  ECS         │
│                                                              │
│  docker pull registry.gitlab.com/org/app:v1.2.0             │
│  → runs the container                                        │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

### 1.6 Comparison With Other Registries

| Dimension | GitLab Container Registry | Docker Hub | GitHub Container Registry (GHCR) | Amazon ECR | Google Artifact Registry | npm Registry |
|---|---|---|---|---|---|---|
| **Type** | Docker/OCI images | Docker/OCI images | Docker/OCI images | Docker/OCI images | Docker/OCI + others | JavaScript packages |
| **Integrated with** | GitLab projects | Standalone | GitHub repos | AWS ecosystem | GCP ecosystem | Node.js ecosystem |
| **Auth** | GitLab tokens, CI variables | Docker Hub account | GitHub tokens | IAM roles | Google IAM | npm tokens |
| **Private images** | Free (unlimited) | 1 free, then paid | Free (unlimited) | Free (with AWS) | Free tier then paid | Paid on npmjs |
| **CI integration** | Native (`$CI_REGISTRY_*` vars) | Manual config | Native (`GITHUB_TOKEN`) | AWS CLI setup | gcloud setup | `npm publish` |
| **Vulnerability scanning** | Built-in (GitLab Ultimate) | Docker Scout | Dependabot | Inspector | On-Demand Scanning | `npm audit` |
| **Best for** | GitLab-native teams | Public images, OSS | GitHub-native teams | AWS-deployed apps | GCP-deployed apps | JS packages |
| **Biggest advantage** | Zero-config with GitLab CI | Largest public catalog | GitHub ecosystem | IAM integration | Multi-format support | Huge JS ecosystem |
| **Biggest weakness** | GitLab-only ecosystem | Rate limits on free tier | GitHub-only ecosystem | AWS lock-in | GCP lock-in | Not for Docker images |

### 1.7 When GitLab Container Registry Is the Best Choice

**Choose GitLab Container Registry when:**
- Your source code lives on GitLab.
- You want zero-config CI integration (`$CI_REGISTRY` variables are auto-injected).
- You want private images at no extra cost.
- You want registry and CI/CD and source code in one platform.
- Your team doesn't use AWS/GCP as primary cloud (no lock-in).

**Choose something else when:**
- Your code is on GitHub → use GHCR.
- You deploy exclusively to AWS → ECR has tighter IAM integration.
- You deploy exclusively to GCP → Artifact Registry is native.
- You need a public image catalog → Docker Hub.
- You're distributing JavaScript, not Docker images → npm registry.

### 1.8 Mental Model Diagram

```text
┌─────────────────────────────────────────────────────────┐
│                 YOUR GITLAB PROJECT                      │
│                                                         │
│  Code (src/)  +  Dockerfile  +  .gitlab-ci.yml          │
│                                                         │
│  CI Pipeline:                                           │
│    build job → docker build → docker push               │
│                                                         │
└──────────────────┬──────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────┐
│            GITLAB CONTAINER REGISTRY                     │
│                                                         │
│  registry.gitlab.com/your-org/your-project              │
│                                                         │
│  Think of it as:                                        │
│    npm registry    →  but for Docker images              │
│    package.json    →  Dockerfile                         │
│    npm publish     →  docker push                        │
│    npm install     →  docker pull                        │
│    @18.2.0         →  :v1.2.0 (tag)                     │
│    integrity hash  →  sha256:abc... (digest)             │
│                                                         │
│  Images stored here are:                                │
│    ✓ Private by default                                 │
│    ✓ Versioned by tags                                  │
│    ✓ Pullable by any authorized machine                 │
│    ✓ Integrated with GitLab CI/CD                       │
│                                                         │
└──────────────────┬──────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────┐
│           DEPLOYMENT TARGETS                             │
│                                                         │
│  docker-compose pull  /  kubectl apply  /  cloud run     │
│                                                         │
│  All pull from: registry.gitlab.com/org/project:tag     │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

## 2. Learning Roadmap by Skill Level

### Level 1 — Newbie

**Goal:** Understand what a registry is, log in, push and pull your first image.

#### What a registry is

A container registry is a server that stores Docker images, just like npm's registry stores packages. When you `docker push`, the image is uploaded. When you `docker pull`, it's downloaded. GitLab gives every project its own registry at:

```
registry.gitlab.com/<namespace>/<project>
```

**Example:** If your GitLab project is `thaison/my-react-app`, your registry URL is:

```
registry.gitlab.com/thaison/my-react-app
```

#### Logging in to GitLab Container Registry

```bash
# Using a personal access token (PAT)
docker login registry.gitlab.com -u <your-username> -p <your-pat>

# Using CI job token (in .gitlab-ci.yml)
docker login -u $CI_REGISTRY_USER -p $CI_REGISTRY_PASSWORD $CI_REGISTRY
```

To create a PAT: **Settings → Access Tokens → New Token** with `read_registry` and `write_registry` scopes.

#### Pulling an image

```bash
# Pull a specific tag
docker pull registry.gitlab.com/thaison/my-react-app:v1.0.0

# Pull latest (defaults to :latest tag)
docker pull registry.gitlab.com/thaison/my-react-app
```

#### Tagging an image

```bash
# Tag a local image for the registry
docker tag my-react-app:local registry.gitlab.com/thaison/my-react-app:v1.0.0

# Tag with multiple tags
docker tag my-react-app:local registry.gitlab.com/thaison/my-react-app:latest
```

**Analogy:** Tagging is like `npm version 1.0.0` — you're labeling a specific build with a version identifier.

#### Pushing an image

```bash
# Push a specific tag
docker push registry.gitlab.com/thaison/my-react-app:v1.0.0

# Push all tags for a repository
docker push --all-tags registry.gitlab.com/thaison/my-react-app
```

#### Understanding image naming format

```
registry.gitlab.com / <namespace> / <project> [/ <optional-path>] : <tag>
└── registry host ──┘ └─ group ──┘ └─ repo ─┘  └─ sub-image ──┘  └ tag ┘
```

**Examples:**

```
registry.gitlab.com/thaison/my-app:v1.0.0
registry.gitlab.com/thaison/my-app:latest
registry.gitlab.com/thaison/my-app/frontend:v1.0.0    ← sub-image for monorepo
registry.gitlab.com/thaison/my-app/backend:v1.0.0     ← another sub-image
```

#### Common Docker login mistakes

| Mistake | Symptom | Fix |
|---|---|---|
| Wrong registry URL | `unauthorized: authentication required` | Use `registry.gitlab.com` exactly |
| Expired token | `unauthorized` | Generate a new PAT |
| Wrong scopes on PAT | `denied: access forbidden` | Include `read_registry` and `write_registry` |
| Using password instead of PAT | Login fails | Use a PAT, not your GitLab password |
| Not logged in before push | `denied: requested access to the resource is denied` | Run `docker login` first |
| Typo in image name | `repository does not exist` | Match the exact GitLab namespace/project |

#### 5 beginner exercises

1. **Login:** Create a PAT with registry scopes and log in from your terminal.
2. **Build and tag:** Build a simple Dockerfile, tag it for your GitLab registry.
3. **Push:** Push the tagged image and verify it appears in GitLab UI (Packages & Registries → Container Registry).
4. **Pull on another machine:** Log in from a different terminal/machine and pull the image.
5. **Multiple tags:** Push the same image with both `:v1.0.0` and `:latest` tags.

#### Level 1 success criteria

- [ ] Can log in to GitLab Container Registry.
- [ ] Can build, tag, and push an image.
- [ ] Can pull an image on a different machine.
- [ ] Can explain image, tag, registry, and repository.

---

### Level 2 — Junior

**Goal:** Use the registry in team workflows — CI integration, branch tags, cleanup, and access control.

#### Multiple tags strategy

Every push to the registry can apply multiple tags to the same image:

```bash
# Same image, three tags
docker build -t registry.gitlab.com/org/app:v1.2.0 \
             -t registry.gitlab.com/org/app:latest \
             -t registry.gitlab.com/org/app:$CI_COMMIT_SHA .
docker push --all-tags registry.gitlab.com/org/app
```

**Why multiple tags?**
- `:v1.2.0` — human-readable release version.
- `:latest` — convenient default for development.
- `:<commit-sha>` — exact traceability to source code.

#### Branch-based image tags

```yaml
build:
  script:
    - docker build -t $CI_REGISTRY_IMAGE:$CI_COMMIT_REF_SLUG .
    - docker push $CI_REGISTRY_IMAGE:$CI_COMMIT_REF_SLUG
```

`$CI_COMMIT_REF_SLUG` converts branch names to URL-safe strings:
- `feature/login` → `feature-login`
- `main` → `main`

**Use case:** Preview deployments. Each branch gets its own image tag for isolated testing.

#### Version tags

```yaml
# On tagged commits (e.g., v1.2.0)
release:
  rules:
    - if: $CI_COMMIT_TAG =~ /^v\d+/
  script:
    - docker build -t $CI_REGISTRY_IMAGE:$CI_COMMIT_TAG .
    - docker push $CI_REGISTRY_IMAGE:$CI_COMMIT_TAG
```

#### Using registry in GitLab CI

```yaml
stages:
  - build
  - deploy

build:
  stage: build
  image: docker:24
  services:
    - docker:24-dind
  variables:
    DOCKER_TLS_CERTDIR: "/certs"
  script:
    - docker login -u $CI_REGISTRY_USER -p $CI_REGISTRY_PASSWORD $CI_REGISTRY
    - docker build -t $CI_REGISTRY_IMAGE:$CI_COMMIT_SHA .
    - docker push $CI_REGISTRY_IMAGE:$CI_COMMIT_SHA

deploy:
  stage: deploy
  script:
    - docker pull $CI_REGISTRY_IMAGE:$CI_COMMIT_SHA
    - echo "Deploying image $CI_REGISTRY_IMAGE:$CI_COMMIT_SHA"
```

**Key CI variables (auto-injected by GitLab):**

| Variable | Value | Example |
|---|---|---|
| `$CI_REGISTRY` | Registry hostname | `registry.gitlab.com` |
| `$CI_REGISTRY_IMAGE` | Project image path | `registry.gitlab.com/org/app` |
| `$CI_REGISTRY_USER` | CI user for auth | `gitlab-ci-token` |
| `$CI_REGISTRY_PASSWORD` | CI token for auth | (auto-generated) |

#### Pulling images in Docker Compose

```yaml
# docker-compose.yml
services:
  app:
    image: registry.gitlab.com/org/app:v1.2.0
    ports:
      - "3000:3000"
```

For private images, log in first:

```bash
docker login registry.gitlab.com -u <user> -p <token>
docker compose up
```

#### Image cleanup

Images accumulate quickly. Clean up with:

**Manual (UI):** Packages & Registries → Container Registry → Delete tags.

**Bulk cleanup policy (GitLab settings):**
Settings → Packages & Registries → Clean up image tags:
- Keep the most recent N tags.
- Remove tags older than N days.
- Match tags by regex pattern.

**CI-based cleanup:**

```yaml
cleanup:
  stage: cleanup
  image: registry.gitlab.com/gitlab-org/cli:latest
  script:
    - glab api --method DELETE "projects/$CI_PROJECT_ID/registry/repositories/$REPO_ID/tags/$TAG"
  rules:
    - if: $CI_PIPELINE_SOURCE == "schedule"
```

#### Registry permissions

| Role | Read (pull) | Write (push) | Delete |
|---|---|---|---|
| Guest | ❌ | ❌ | ❌ |
| Reporter | ✅ | ❌ | ❌ |
| Developer | ✅ | ✅ | ❌ |
| Maintainer | ✅ | ✅ | ✅ |
| Owner | ✅ | ✅ | ✅ |

#### Private vs. public images

| Setting | Who can pull | Use case |
|---|---|---|
| Private project | Only authenticated project members | Internal apps |
| Public project | Anyone | Open source |
| Deploy token (read-only) | Specific external systems | Production servers |

**Recommendation:** Keep images private. Use deploy tokens for production servers.

#### Common mistakes and anti-patterns

| Mistake | Why it's bad | Fix |
|---|---|---|
| Only using `:latest` | Can't trace which version is deployed | Always tag with SHA or semver |
| Never cleaning up images | Storage grows unbounded | Set cleanup policies |
| Hardcoding registry URL | Breaks on forks/moves | Use `$CI_REGISTRY_IMAGE` |
| Using personal PAT in CI | Tied to one person, security risk | Use `$CI_REGISTRY_PASSWORD` (CI job token) |
| No `.dockerignore` | Images contain `node_modules`, `.git`, etc. | Create `.dockerignore` |
| Building without `--no-cache` when debugging | Stale layers | Use `--no-cache` selectively |
| Pushing images on every branch | Storage waste | Only push on main/tags, or clean up branch images |

#### 5 mini project ideas

1. **React app with CI push:** Build a React Vite app, Dockerize it, push to GitLab registry on every push to main.
2. **Branch preview images:** Push branch-tagged images, use them in a Docker Compose preview environment.
3. **Multi-tag release:** On tag push, build image with `:v1.0.0`, `:latest`, and `:<sha>` tags.
4. **Image consumer project:** Create a second project that pulls from the first project's registry.
5. **Cleanup automation:** Create a scheduled pipeline that removes images older than 30 days.

#### Level 2 success criteria

- [ ] Can push images from GitLab CI using built-in variables.
- [ ] Can use branch-based and version-based tagging.
- [ ] Can pull private images in Docker Compose.
- [ ] Can set up image cleanup policies.

---

### Level 3 — Senior

**Goal:** Design production-grade image workflows — promotion, immutability, rollback, security, and optimization.

#### Production tagging strategy

| Strategy | Example tags | Traceability | Rollback | Complexity |
|---|---|---|---|---|
| SHA only | `:abc1234` | Excellent | By SHA | Low |
| Semver only | `:v1.2.3` | Good | By version | Medium |
| SHA + semver | `:abc1234`, `:v1.2.3` | Excellent | Both | Medium |
| SHA + semver + latest | `:abc1234`, `:v1.2.3`, `:latest` | Excellent | Both | Medium |
| Branch + SHA | `:main-abc1234` | Excellent | By SHA | Low |

**Senior recommendation:** SHA + semver for releases. SHA-only for non-release builds. Never rely solely on `:latest`.

```yaml
# In .gitlab-ci.yml
build:
  script:
    - |
      docker build \
        -t $CI_REGISTRY_IMAGE:$CI_COMMIT_SHA \
        -t $CI_REGISTRY_IMAGE:$CI_COMMIT_REF_SLUG \
        .
    - docker push $CI_REGISTRY_IMAGE:$CI_COMMIT_SHA
    - docker push $CI_REGISTRY_IMAGE:$CI_COMMIT_REF_SLUG

release:
  rules:
    - if: $CI_COMMIT_TAG =~ /^v\d+\.\d+\.\d+$/
  script:
    # Re-tag the already-built SHA image with the version
    - docker pull $CI_REGISTRY_IMAGE:$CI_COMMIT_SHA
    - docker tag $CI_REGISTRY_IMAGE:$CI_COMMIT_SHA $CI_REGISTRY_IMAGE:$CI_COMMIT_TAG
    - docker tag $CI_REGISTRY_IMAGE:$CI_COMMIT_SHA $CI_REGISTRY_IMAGE:latest
    - docker push $CI_REGISTRY_IMAGE:$CI_COMMIT_TAG
    - docker push $CI_REGISTRY_IMAGE:latest
```

#### Immutable image policy

**Problem:** Mutable tags (`:latest`, `:v1`) can point to different images over time. You lose reproducibility.

**Rule:** Once a versioned tag like `:v1.2.3` is pushed, it must never be overwritten.

**Enforcement:**
1. CI validation — check if tag exists before pushing:
   ```bash
   if docker manifest inspect $CI_REGISTRY_IMAGE:$CI_COMMIT_TAG > /dev/null 2>&1; then
     echo "ERROR: Tag $CI_COMMIT_TAG already exists. Cannot overwrite."
     exit 1
   fi
   ```
2. Convention — only mutable tags are `:latest` and branch slugs. Version tags are sacred.
3. Digests — reference images by digest in production: `image: registry.gitlab.com/org/app@sha256:abc123...`

#### Semantic versioning for images

```text
v<major>.<minor>.<patch>

v1.0.0  → initial release
v1.1.0  → new feature, backward compatible
v1.1.1  → bug fix
v2.0.0  → breaking change
```

**Floating tags for convenience (mutable):**
- `:v1` → latest `v1.x.x`
- `:v1.2` → latest `v1.2.x`
- `:v1.2.3` → immutable, specific

**Analogy:** Like npm's `^1.2.3` (allow minor/patch updates) vs `1.2.3` (exact).

#### Image promotion strategy

**Problem:** Should you rebuild the image for production, or promote the same image from staging?

**Answer:** Promote, don't rebuild. The image tested in staging should be the exact same image deployed to production. Rebuilding introduces risk (different dependencies, build-time variance).

```text
Build (CI) → :sha-abc123
                 ↓ deploy to staging
Staging → registry.gitlab.com/org/app:sha-abc123
                 ↓ manual approval → re-tag
Production → registry.gitlab.com/org/app:v1.2.0 (same digest!)
```

```yaml
promote-to-production:
  stage: promote
  rules:
    - if: $CI_COMMIT_TAG =~ /^v\d+/
      when: manual
  script:
    - docker pull $CI_REGISTRY_IMAGE:$CI_COMMIT_SHA
    - docker tag $CI_REGISTRY_IMAGE:$CI_COMMIT_SHA $CI_REGISTRY_IMAGE:$CI_COMMIT_TAG
    - docker push $CI_REGISTRY_IMAGE:$CI_COMMIT_TAG
```

#### Multi-environment image flow

```text
Feature branch → :feature-xyz (preview)
           ↓ merge
main → :sha-abc123 → deploy to staging
           ↓ manual gate
Tag v1.2.0 → :v1.2.0 (re-tag same SHA image) → deploy to production
```

**Key principle:** Build once, deploy many. The image is built once from the commit SHA. Environments pull the same image by different tags.

#### Secure authentication

| Method | Use case | Security |
|---|---|---|
| CI job token (`$CI_REGISTRY_PASSWORD`) | GitLab CI jobs | Auto-scoped, short-lived ✅ |
| Deploy token | Production servers pulling images | Read-only, long-lived, auditable ✅ |
| Personal access token (PAT) | Local development | Personal, should not be shared ⚠️ |
| Group access token | Cross-project automation | Scoped to group ✅ |
| OIDC | Cloud platforms (K8s, AWS) | No static secrets ✅✅ |

**Senior recommendation:** CI job tokens for pipelines. Deploy tokens for servers. Never embed PATs in scripts or Dockerfiles.

#### Registry cleanup automation

```yaml
# Scheduled weekly cleanup
cleanup-old-images:
  stage: cleanup
  image: registry.gitlab.com/gitlab-org/cli:latest
  rules:
    - if: $CI_PIPELINE_SOURCE == "schedule"
  script:
    - |
      # Delete branch tags older than 30 days
      # Keep all semver tags
      # Keep latest 10 SHA tags on main
      glab api "projects/$CI_PROJECT_ID/registry/repositories" \
        | jq -r '.[].id' \
        | while read repo_id; do
            glab api "projects/$CI_PROJECT_ID/registry/repositories/$repo_id/tags" \
              | jq -r '.[] | select(.created_at < (now - 2592000 | todate)) | select(.name | test("^v\\d") | not) | .name' \
              | while read tag; do
                  glab api --method DELETE "projects/$CI_PROJECT_ID/registry/repositories/$repo_id/tags/$tag"
                done
          done
```

**GitLab built-in cleanup policy (recommended):**
Settings → Packages & Registries → Clean up image tags:
- Regex for tags to remove: `.*` (match all)
- Regex for tags to keep: `^v\d+\.\d+\.\d+$` (keep semver)
- Keep the most recent: 10 tags
- Remove tags older than: 30 days

#### Large monorepo image strategy

```text
registry.gitlab.com/org/monorepo/frontend:v1.2.0
registry.gitlab.com/org/monorepo/backend:v3.1.0
registry.gitlab.com/org/monorepo/worker:v2.0.1
registry.gitlab.com/org/monorepo/nginx:v1.0.0
```

Each service gets its own sub-path in the registry. Tags are independent per service.

```yaml
# .gitlab-ci.yml
build-frontend:
  script:
    - docker build -t $CI_REGISTRY_IMAGE/frontend:$CI_COMMIT_SHA -f frontend/Dockerfile .
    - docker push $CI_REGISTRY_IMAGE/frontend:$CI_COMMIT_SHA
  rules:
    - changes: [frontend/**, packages/shared/**]

build-backend:
  script:
    - docker build -t $CI_REGISTRY_IMAGE/backend:$CI_COMMIT_SHA -f backend/Dockerfile .
    - docker push $CI_REGISTRY_IMAGE/backend:$CI_COMMIT_SHA
  rules:
    - changes: [backend/**, packages/shared/**]
```

#### Multi-service architecture

```yaml
# docker-compose.yml
services:
  frontend:
    image: registry.gitlab.com/org/app/frontend:v1.2.0
    ports: ["3000:3000"]

  backend:
    image: registry.gitlab.com/org/app/backend:v3.1.0
    ports: ["8080:8080"]

  worker:
    image: registry.gitlab.com/org/app/worker:v2.0.1
```

Each service is versioned independently. You can update the backend without touching the frontend image.

#### Release rollback strategy

```text
Current production:  app:v1.3.0 (sha256:broken...)
Previous version:    app:v1.2.0 (sha256:works...)

Rollback: redeploy app:v1.2.0
```

**Strategies:**

| Strategy | Speed | Risk |
|---|---|---|
| Re-deploy previous tag | Fast (minutes) | Low — same tested image |
| Re-deploy by digest | Fast | Lowest — immutable reference |
| Git revert + rebuild | Slow (5-15 min) | Medium — new build |
| Feature flag disable | Instant | Low — no deployment needed |

**Senior recommendation:** Always keep the last N version tags. Rollback = re-deploy the previous tag. Use digests in production manifests for maximum safety.

#### Cost optimization

| Technique | Impact |
|---|---|
| Multi-stage Docker builds | Smaller images (100MB vs 1GB) |
| `.dockerignore` | Exclude `node_modules`, `.git`, test files |
| Alpine-based images | 5-50MB vs 200MB+ |
| Layer caching in CI | Faster builds |
| Cleanup old images | Reduce storage cost |
| Don't push branch images for every commit | Reduce storage and transfer |
| Compress layers | Smaller push/pull |

#### Observability

- **GitLab UI:** View all tags, sizes, and push dates in Container Registry page.
- **CI logs:** Log the exact tag and digest pushed.
- **Deployment tracking:** GitLab Environments show which image tag is deployed.
- **Alerts:** Pipeline failure notification if push fails.

```yaml
# Log the digest after push for traceability
build:
  script:
    - docker push $CI_REGISTRY_IMAGE:$CI_COMMIT_SHA
    - docker inspect --format='{{index .RepoDigests 0}}' $CI_REGISTRY_IMAGE:$CI_COMMIT_SHA
```

#### 5 production-grade project examples

1. **Next.js with multi-stage build:** Dockerfile with build + runtime stages, SHA + semver tags, promotion from staging to production.
2. **Monorepo with per-service images:** Frontend, backend, and worker each have their own Dockerfile and registry path, built only when changed.
3. **Automated cleanup pipeline:** Scheduled weekly job that removes branch tags older than 14 days, keeping all semver tags.
4. **Cross-project image sharing:** Shared base image project that other projects pull from using deploy tokens.
5. **Blue-green deployment with rollback:** Two production slots, switch traffic between images, instant rollback to previous digest.

#### Level 3 success criteria

- [ ] Can design a production tagging strategy with immutable versions.
- [ ] Can implement image promotion (build once, deploy many).
- [ ] Can set up automated cleanup policies.
- [ ] Can design multi-service registry architecture.
- [ ] Can implement instant rollback by re-deploying a previous tag.

---

### Level 4 — Expert

**Goal:** Architect organization-wide registry strategy — governance, security, supply chain, and disaster recovery.

#### Organization-wide registry architecture

```text
org/base-images/
├── node:20-alpine-custom    ← hardened base images maintained by platform team
├── nginx:stable-custom
└── python:3.12-custom

org/frontend-app/
├── /frontend:v1.2.0         ← built FROM org/base-images/node
└── /storybook:v1.2.0

org/backend-api/
├── /api:v3.0.0              ← built FROM org/base-images/node
└── /worker:v2.1.0

org/infrastructure/
├── /nginx-proxy:v1.0.0
└── /monitoring:v1.0.0
```

**Key patterns:**
- **Shared base images:** Platform team maintains hardened, scanned base images. All teams build FROM these.
- **Per-project registries:** Each project owns its images.
- **Naming convention:** Enforced by CI templates.

#### Multi-project registry strategy

```yaml
# Project A builds and pushes
build:
  script:
    - docker push registry.gitlab.com/org/shared-lib:$CI_COMMIT_TAG

# Project B pulls from Project A's registry
deploy:
  image: registry.gitlab.com/org/shared-lib:v1.2.0
  script:
    - echo "Using shared image"
```

**Authentication for cross-project pulls:**
- Use deploy tokens scoped to the source project.
- Use group access tokens for intra-group access.

#### Supply chain security

| Threat | Mitigation |
|---|---|
| Compromised base image | Pin base images by digest, scan regularly |
| Malicious layer injection | Review Dockerfile changes in MR |
| Dependency vulnerability | SAST + dependency scanning in CI |
| Unauthorized push | Protected branches + protected tags |
| Image tampering in transit | Docker Content Trust (DCT) / Cosign signing |
| Unknown image provenance | SLSA provenance attestation |

#### Image signing and verification

```yaml
# Sign with Cosign (Sigstore)
sign:
  stage: sign
  image: bitnami/cosign:latest
  script:
    - cosign sign --key $COSIGN_KEY $CI_REGISTRY_IMAGE:$CI_COMMIT_SHA
  rules:
    - if: $CI_COMMIT_TAG =~ /^v\d+/

# Verify before deployment
verify:
  stage: verify
  image: bitnami/cosign:latest
  script:
    - cosign verify --key $COSIGN_PUB_KEY $CI_REGISTRY_IMAGE:$CI_COMMIT_TAG
```

**Kubernetes admission control:** Use a policy engine (Kyverno, OPA Gatekeeper) to reject unsigned images in production clusters.

#### SBOM strategy

Software Bill of Materials — a manifest of everything inside an image.

```yaml
generate-sbom:
  stage: scan
  image: anchore/syft:latest
  script:
    - syft $CI_REGISTRY_IMAGE:$CI_COMMIT_SHA -o spdx-json > sbom.json
  artifacts:
    paths: [sbom.json]
    expire_in: 1 year
```

**Why:** Compliance requirements, vulnerability response ("are we affected by CVE-X?"), and auditing.

#### Vulnerability scanning

```yaml
# GitLab built-in container scanning
include:
  - template: Security/Container-Scanning.gitlab-ci.yml

container_scanning:
  variables:
    CS_IMAGE: $CI_REGISTRY_IMAGE:$CI_COMMIT_SHA
```

**Manual scanning with Trivy:**

```yaml
scan:
  image:
    name: aquasec/trivy:latest
    entrypoint: [""]
  script:
    - trivy image --severity HIGH,CRITICAL --exit-code 1 $CI_REGISTRY_IMAGE:$CI_COMMIT_SHA
```

**Policy:** Block deployment if HIGH or CRITICAL vulnerabilities are found. Allow MEDIUM with a review process.

#### Multi-region registry replication

GitLab SaaS stores images in a single region. For multi-region needs:

| Strategy | Complexity | Latency improvement |
|---|---|---|
| GitLab Geo (self-managed) | High | Automatic replication |
| Push to multiple registries | Medium | Manual in CI |
| Cloud-native registry with replication (ECR, GAR) | Medium | Cloud-native |
| Pull-through cache (Harbor) | Medium | Transparent caching |

```yaml
# Push to GitLab + ECR for multi-region
build:
  script:
    - docker push $CI_REGISTRY_IMAGE:$CI_COMMIT_SHA
    - docker tag $CI_REGISTRY_IMAGE:$CI_COMMIT_SHA $ECR_REPO:$CI_COMMIT_SHA
    - aws ecr get-login-password | docker login --username AWS --password-stdin $ECR_URL
    - docker push $ECR_REPO:$CI_COMMIT_SHA
```

#### Disaster recovery

| Risk | Mitigation |
|---|---|
| Registry outage | Mirror critical images to a secondary registry |
| Accidental tag deletion | Protect semver tags, backup digests |
| Corrupted image | Verify digests, sign images |
| Lost registry credentials | Document rotation procedure, store securely |
| Need to rebuild old version | Keep Dockerfile + lockfile in source control |

**Recovery strategy:** Store a manifest of production image digests in version control. If the registry fails, rebuild from source using pinned dependency lockfiles.

#### Advanced governance

| Policy | Implementation |
|---|---|
| All images must be scanned | Include container scanning template at group level |
| Only signed images in production | Kubernetes admission controller |
| Base images approved by platform team | Shared base image project, enforce in Dockerfiles |
| Tags follow naming convention | CI validation step |
| Images cleaned up after N days | Cleanup policy per project |
| No `latest` in production manifests | Linting in CI |
| Cross-project access audited | Deploy token audit log |

#### Lifecycle policy architecture

```text
Branch image (:feature-xyz)
  → Created on MR open
  → Deleted 7 days after MR merge
  → Auto-cleaned by scheduled pipeline

SHA image (:abc1234)
  → Created on every main push
  → Kept for 30 days
  → Last 20 retained regardless of age

Release image (:v1.2.3)
  → Created on tag push
  → Never auto-deleted
  → Manually archived after EOL

Latest image (:latest)
  → Updated on every main push
  → Points to newest main build
  → Never used in production manifests
```

#### Architecture review checklist

- [ ] Are all images tagged with commit SHA for traceability?
- [ ] Are release images tagged with semver?
- [ ] Is `:latest` banned from production deployments?
- [ ] Are base images pinned by digest?
- [ ] Is there a cleanup policy for branch and old SHA tags?
- [ ] Are images scanned for vulnerabilities before deployment?
- [ ] Is cross-project access authenticated with deploy tokens (not PATs)?
- [ ] Are production images signed?
- [ ] Is there a documented rollback procedure?
- [ ] Is there a disaster recovery plan for registry failure?
- [ ] Are SBOMs generated for compliance?
- [ ] Is image size optimized (multi-stage builds, Alpine)?
- [ ] Are `.dockerignore` files maintained?
- [ ] Is there observability on push/pull failures?

#### What expert engineers care about that juniors miss

| Expert concern | Junior blind spot |
|---|---|
| Image immutability | "Just overwrite the tag" |
| Digest-based references | "Tags are fine" |
| Build reproducibility | "Just rebuild it" |
| Supply chain security | "Docker Hub images are safe" |
| Registry storage costs | "Storage is cheap" |
| Base image hygiene | "Use whatever FROM image" |
| Cleanup automation | "We'll clean up later" |
| Cross-project auth model | "Use my personal token" |
| Provenance and signing | "Who would tamper with our images?" |
| Multi-region availability | "One registry is enough" |

#### 10 advanced engineering discussion topics

1. **Build vs. promote:** Should a production image be rebuilt from source or promoted from staging? What are the security trade-offs of each?
2. **Digest pinning at scale:** How do you manage digest references across 50 Kubernetes manifests when base images update?
3. **Base image update propagation:** When the platform team updates `node:20-alpine-custom`, how should downstream projects discover and adopt the change?
4. **Registry as single point of failure:** If your registry is down, production can't scale. How do you design for this?
5. **Image sprawl economics:** At 500 pushes/week, how much registry storage do you consume yearly? What's the cost-optimal retention policy?
6. **Signing key management:** Who holds the Cosign signing keys? How do you rotate them without breaking verification?
7. **Multi-tenant registry isolation:** In a shared GitLab instance, how do you ensure Team A can't pull Team B's images?
8. **Compliance automation:** How would you prove to an auditor that every production image was scanned and signed?
9. **Zero-trust image policy:** Design a system where Kubernetes rejects any image that isn't from an approved registry, signed, scanned, and built by CI.
10. **Migration strategy:** You're moving from Docker Hub to GitLab Container Registry for 200 images. How do you plan the migration without downtime?

---

## 3. Setup Guide

### Step 1: Enable GitLab Container Registry

GitLab Container Registry is enabled by default on GitLab.com. For self-managed instances, confirm with your admin.

Verify: Go to your project → **Packages & Registries → Container Registry**. If you see the registry page, it's enabled.

### Step 2: Log in from terminal

```bash
# Create a Personal Access Token (PAT):
# Settings → Access Tokens → New Token
# Scopes: read_registry, write_registry

docker login registry.gitlab.com -u <your-username> -p <your-pat>
```

Verify:

```bash
cat ~/.docker/config.json | grep registry.gitlab.com
# Should show an auth entry
```

### Step 3: Build and push your first image

Create a minimal Dockerfile:

```dockerfile
# Dockerfile
FROM node:20-alpine AS build
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
EXPOSE 80
```

Create `.dockerignore`:

```
node_modules
.git
.next
dist
*.md
.env*
```

Build, tag, and push:

```bash
# Build
docker build -t registry.gitlab.com/your-org/your-project:v1.0.0 .

# Push
docker push registry.gitlab.com/your-org/your-project:v1.0.0
```

### Step 4: Recommended image naming strategy

```text
# Single app
registry.gitlab.com/<namespace>/<project>:<tag>

# Monorepo
registry.gitlab.com/<namespace>/<project>/<service>:<tag>

# Examples
registry.gitlab.com/thaison/my-app:v1.2.0
registry.gitlab.com/thaison/my-app:abc1234
registry.gitlab.com/thaison/monorepo/frontend:v1.2.0
registry.gitlab.com/thaison/monorepo/backend:v3.0.0
```

### Step 5: Recommended tag naming conventions

| Context | Tag format | Example |
|---|---|---|
| Every CI build | Commit SHA | `:abc1234def` |
| Main branch | Branch slug | `:main` |
| Feature branch | Branch slug | `:feature-login` |
| Release | Semver | `:v1.2.0` |
| Latest stable | Mutable | `:latest` |
| Production (manifests) | Digest or semver | `:v1.2.0` or `@sha256:...` |

### Step 6: Example commands

#### Local development

```bash
# Build locally
docker build -t my-app:dev .

# Run locally
docker run -p 3000:80 my-app:dev

# Tag for registry
docker tag my-app:dev registry.gitlab.com/org/app:dev

# Push (optional, for sharing)
docker push registry.gitlab.com/org/app:dev
```

#### CI/CD pipeline

```yaml
stages:
  - build
  - scan
  - deploy

variables:
  DOCKER_TLS_CERTDIR: "/certs"

build:
  stage: build
  image: docker:24
  services:
    - docker:24-dind
  script:
    - docker login -u $CI_REGISTRY_USER -p $CI_REGISTRY_PASSWORD $CI_REGISTRY
    - |
      docker build \
        --cache-from $CI_REGISTRY_IMAGE:latest \
        -t $CI_REGISTRY_IMAGE:$CI_COMMIT_SHA \
        -t $CI_REGISTRY_IMAGE:$CI_COMMIT_REF_SLUG \
        .
    - docker push $CI_REGISTRY_IMAGE:$CI_COMMIT_SHA
    - docker push $CI_REGISTRY_IMAGE:$CI_COMMIT_REF_SLUG

scan:
  stage: scan
  image:
    name: aquasec/trivy:latest
    entrypoint: [""]
  script:
    - trivy image --severity HIGH,CRITICAL $CI_REGISTRY_IMAGE:$CI_COMMIT_SHA

deploy:
  stage: deploy
  script:
    - echo "Deploying $CI_REGISTRY_IMAGE:$CI_COMMIT_SHA"
  environment:
    name: production
  rules:
    - if: $CI_COMMIT_TAG =~ /^v\d+/
      when: manual
```

#### Production deployment

```bash
# On production server
docker login registry.gitlab.com -u <deploy-token-user> -p <deploy-token>
docker pull registry.gitlab.com/org/app:v1.2.0
docker stop app && docker rm app
docker run -d --name app -p 80:80 registry.gitlab.com/org/app:v1.2.0
```

### Step 7: Framework-specific Dockerfiles

#### React (Vite)

```dockerfile
FROM node:20-alpine AS build
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
```

```nginx
# nginx.conf
server {
    listen 80;
    root /usr/share/nginx/html;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }
}
```

#### Next.js (standalone)

```dockerfile
FROM node:20-alpine AS deps
WORKDIR /app
COPY package*.json ./
RUN npm ci

FROM node:20-alpine AS build
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .
RUN npm run build

FROM node:20-alpine AS runner
WORKDIR /app
ENV NODE_ENV=production
COPY --from=build /app/.next/standalone ./
COPY --from=build /app/.next/static ./.next/static
COPY --from=build /app/public ./public
EXPOSE 3000
CMD ["node", "server.js"]
```

**Requires** in `next.config.js`:
```javascript
module.exports = {
  output: 'standalone',
};
```

#### Astro (static)

```dockerfile
FROM node:20-alpine AS build
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
EXPOSE 80
```

### Step 8: Docker Compose example using registry image

```yaml
# docker-compose.yml
services:
  frontend:
    image: registry.gitlab.com/org/app/frontend:v1.2.0
    ports:
      - "3000:80"
    restart: unless-stopped

  backend:
    image: registry.gitlab.com/org/app/backend:v3.0.0
    ports:
      - "8080:8080"
    environment:
      - DATABASE_URL=postgres://db:5432/app
    restart: unless-stopped

  db:
    image: postgres:16-alpine
    volumes:
      - pgdata:/var/lib/postgresql/data
    environment:
      POSTGRES_DB: app
      POSTGRES_PASSWORD: secret

volumes:
  pgdata:
```

```bash
# Login first, then compose
docker login registry.gitlab.com -u <user> -p <token>
docker compose pull
docker compose up -d
```

### Step 9: Kubernetes example pulling from registry

```yaml
# Create pull secret
# kubectl create secret docker-registry gitlab-registry \
#   --docker-server=registry.gitlab.com \
#   --docker-username=<deploy-token-user> \
#   --docker-password=<deploy-token>

apiVersion: apps/v1
kind: Deployment
metadata:
  name: frontend
spec:
  replicas: 3
  selector:
    matchLabels:
      app: frontend
  template:
    metadata:
      labels:
        app: frontend
    spec:
      imagePullSecrets:
        - name: gitlab-registry
      containers:
        - name: frontend
          image: registry.gitlab.com/org/app/frontend:v1.2.0
          ports:
            - containerPort: 80
```

### Step 10: Private registry authentication

| Method | Command / Config |
|---|---|
| **Terminal (PAT)** | `docker login registry.gitlab.com -u user -p pat` |
| **CI (auto)** | `docker login -u $CI_REGISTRY_USER -p $CI_REGISTRY_PASSWORD $CI_REGISTRY` |
| **Deploy token** | Create in Settings → Repository → Deploy Tokens (read_registry) |
| **Docker Compose** | `docker login` before `docker compose pull` |
| **Kubernetes** | `kubectl create secret docker-registry` + `imagePullSecrets` |

### Step 11: Cleanup strategy

**Recommended policy:**

| Image type | Retention | Method |
|---|---|---|
| Branch tags | 14 days after MR merge | GitLab cleanup policy |
| SHA tags on main | Last 20 | GitLab cleanup policy |
| Semver release tags | Forever (or until EOL) | Manual |
| `:latest` | Always exists, overwritten | N/A |

**Setup:** Settings → Packages & Registries → Clean up image tags:
- Remove tags matching: `.*`
- Keep tags matching: `^v\d+\.\d+\.\d+$`
- Keep N most recent: 20
- Remove older than: 30 days

### Recommended starter workflow

For someone with a React/Next.js/Astro background:

1. **Week 1:** Dockerize your app with a multi-stage Dockerfile. Build and run locally.
2. **Week 2:** Push to GitLab Container Registry manually. Verify in GitLab UI.
3. **Week 3:** Automate with `.gitlab-ci.yml`. Push on every main commit with SHA tag.
4. **Week 4:** Add semver tags on git tags. Set up cleanup policy. Pull in Docker Compose.

---

## 4. Cheatsheet

### Docker login / build / tag / push / pull

```bash
# Login
docker login registry.gitlab.com -u $USER -p $TOKEN

# Build
docker build -t registry.gitlab.com/org/app:tag .

# Build with multiple tags
docker build \
  -t registry.gitlab.com/org/app:v1.2.0 \
  -t registry.gitlab.com/org/app:latest \
  .

# Build with cache from registry
docker build --cache-from registry.gitlab.com/org/app:latest \
  -t registry.gitlab.com/org/app:new .

# Tag existing image
docker tag local-image:dev registry.gitlab.com/org/app:v1.0.0

# Push
docker push registry.gitlab.com/org/app:v1.0.0
docker push --all-tags registry.gitlab.com/org/app

# Pull
docker pull registry.gitlab.com/org/app:v1.0.0

# Inspect (check digest, layers)
docker inspect registry.gitlab.com/org/app:v1.0.0
docker manifest inspect registry.gitlab.com/org/app:v1.0.0
```

### GitLab CI variables

| Variable | Value | Use |
|---|---|---|
| `$CI_REGISTRY` | `registry.gitlab.com` | Docker login host |
| `$CI_REGISTRY_IMAGE` | `registry.gitlab.com/org/app` | Image base path |
| `$CI_REGISTRY_USER` | `gitlab-ci-token` | Login username |
| `$CI_REGISTRY_PASSWORD` | Auto-generated job token | Login password |
| `$CI_COMMIT_SHA` | Full commit hash | Traceable image tag |
| `$CI_COMMIT_SHORT_SHA` | Short commit hash (8 chars) | Shorter image tag |
| `$CI_COMMIT_REF_SLUG` | Branch name (URL-safe) | Branch-based tag |
| `$CI_COMMIT_TAG` | Git tag name | Release tag |

### Common tag strategies

| Strategy | Tag format | When to use |
|---|---|---|
| SHA | `:abc1234def` | Every build (traceability) |
| Branch | `:main`, `:feature-login` | Branch previews |
| Semver | `:v1.2.0` | Releases |
| Latest | `:latest` | Development convenience |
| Date | `:2026-04-16` | Nightly builds |
| SHA + semver | Both on release | Production (best) |

### Common registry naming patterns

```text
# Single project
registry.gitlab.com/org/app:tag

# Monorepo services
registry.gitlab.com/org/app/frontend:tag
registry.gitlab.com/org/app/backend:tag
registry.gitlab.com/org/app/worker:tag

# Shared base images
registry.gitlab.com/org/base-images/node:20-custom
registry.gitlab.com/org/base-images/nginx:stable

# Environment-specific (anti-pattern — prefer promotion)
# ❌ registry.gitlab.com/org/app:staging-v1.0.0
# ✅ registry.gitlab.com/org/app:v1.0.0 (same image, different env)
```

### Cleanup commands

```bash
# Delete a tag via API
curl --request DELETE \
  --header "PRIVATE-TOKEN: $TOKEN" \
  "https://gitlab.com/api/v4/projects/$PROJECT_ID/registry/repositories/$REPO_ID/tags/old-tag"

# Bulk delete tags matching regex via API
curl --request DELETE \
  --header "PRIVATE-TOKEN: $TOKEN" \
  "https://gitlab.com/api/v4/projects/$PROJECT_ID/registry/repositories/$REPO_ID/tags?name_regex_delete=feature-.*&older_than=14d"

# Local cleanup
docker image prune -a           # Remove unused images
docker system prune -a --volumes # Remove everything unused
```

### Common error messages

| Error | Cause | Fix |
|---|---|---|
| `unauthorized: authentication required` | Not logged in or wrong credentials | `docker login` with correct token |
| `denied: requested access to the resource is denied` | Wrong scope or no push permission | Check PAT scopes and project role |
| `manifest unknown` | Tag doesn't exist | Verify tag name, check registry UI |
| `name unknown: repository name not known` | Wrong image path | Match exact namespace/project path |
| `error parsing HTTP 413 response body` | Image too large for proxy/gateway | Check max upload size settings |
| `toomanyrequests` | Rate limit hit (Docker Hub) | Use GitLab registry or authenticate |
| `denied: access forbidden` | IP restriction or project visibility | Check project settings and network |

### Security tips

| Tip | Priority |
|---|---|
| Use `$CI_REGISTRY_PASSWORD`, not personal tokens, in CI | Critical |
| Create deploy tokens with minimal scope (read-only) | Critical |
| Pin base images by digest in Dockerfiles | High |
| Scan images with Trivy or GitLab container scanning | High |
| Never put secrets in Dockerfiles or image layers | Critical |
| Use multi-stage builds to exclude build tools from final image | High |
| Sign production images with Cosign | Medium |
| Review Dockerfile changes in MRs | High |

### Performance tips

| Tip | Impact |
|---|---|
| Use multi-stage builds | 50-90% smaller images |
| Order Dockerfile layers by change frequency | Better cache hits |
| Use `--cache-from` in CI | Faster builds |
| Use `.dockerignore` | Smaller build context |
| Use Alpine-based images | 5-50MB vs 200MB+ |
| Build with Kaniko or Buildx | No DinD overhead |
| Pull only needed layers | Faster deployments |

### Cost optimization tips

| Tip | Savings |
|---|---|
| Cleanup policy for old tags | Reduce storage 50-80% |
| Don't push branch images for every commit | Reduce push volume |
| Multi-stage builds (smaller images) | Less storage and transfer |
| Clean up untagged manifests | Remove orphaned layers |
| Limit artifact retention | Reduce GitLab storage |
| Monitor registry usage | Visibility into growth |

---

## 5. Real-World Engineering Mindset

### Tagging strategy

**Problem:** Without a strategy, you end up with hundreds of randomly named tags and no way to know what's deployed.

| Strategy | Traceability | Rollback | Simplicity | Best for |
|---|---|---|---|---|
| `:latest` only | ❌ None | ❌ Impossible | ✅ Simple | Hobby projects |
| Branch slug | ⚠️ Weak | ⚠️ Hard | ✅ Simple | Preview environments |
| Commit SHA | ✅ Excellent | ✅ Easy | ⚠️ Not human-readable | CI builds |
| Semver | ✅ Good | ✅ Easy | ✅ Readable | Releases |
| SHA + semver | ✅ Excellent | ✅ Easy | ⚠️ Two tags | Production (best) |

**Senior choice:** Commit SHA for every CI build. Add semver tag on release. Keep `:latest` as a convenience pointer but never reference it in production manifests.

---

### Branch preview images

**Problem:** Reviewers want to run the MR's Docker image locally or in a preview environment.

| Strategy | Cleanup | Storage | DX |
|---|---|---|---|
| Don't push branch images | N/A | None | ❌ No preview |
| Push with branch slug tag | Need cleanup policy | Medium | ✅ Good |
| Push only on MR label/comment | On demand | Low | ✅ Good |

**Senior choice:** Push `:$CI_COMMIT_REF_SLUG` on MR pipelines. Auto-delete branch tags 7 days after MR merge. Use GitLab's environment cleanup with `on_stop`.

---

### Production release image

**Problem:** The image deployed to production must be traceable, immutable, and tested.

**Senior choice:** Build once from commit SHA. Test in staging. Promote to production by re-tagging with semver — same digest, new tag. Never rebuild for production.

```yaml
promote:
  stage: release
  script:
    - docker pull $CI_REGISTRY_IMAGE:$CI_COMMIT_SHA
    - docker tag $CI_REGISTRY_IMAGE:$CI_COMMIT_SHA $CI_REGISTRY_IMAGE:$CI_COMMIT_TAG
    - docker push $CI_REGISTRY_IMAGE:$CI_COMMIT_TAG
  rules:
    - if: $CI_COMMIT_TAG =~ /^v\d+/
```

---

### Rollback strategy

**Problem:** Production is broken after deploying `:v1.3.0`. You need to go back to `:v1.2.0` immediately.

| Strategy | Speed | Reliability |
|---|---|---|
| Re-deploy previous semver tag | Minutes | High — tested image |
| Re-deploy by digest | Minutes | Highest — immutable |
| Git revert + rebuild | 5-15 minutes | Medium — new build |
| Feature flag | Seconds | High — no redeployment |

**Senior choice:** Re-deploy the previous tag. Keep a manifest of `{ environment: tag, digest }` in version control or deployment tool. Test rollback procedures quarterly.

---

### Sharing images across projects

**Problem:** Project B needs to use an image built by Project A.

| Strategy | Auth | Complexity |
|---|---|---|
| Deploy token on source project | Read-only token | Low |
| Group access token | Group-scoped | Medium |
| Public project | No auth needed | Low (but public) |
| Mirror to external registry | Depends | High |

**Senior choice:** Deploy token with `read_registry` scope. Created in the source project, used by consumers. Rotate annually.

---

### Monorepo image organization

**Problem:** A monorepo has 5 services. Each needs its own image.

```text
registry.gitlab.com/org/monorepo/frontend:v1.2.0
registry.gitlab.com/org/monorepo/backend:v3.0.0
registry.gitlab.com/org/monorepo/worker:v2.1.0
registry.gitlab.com/org/monorepo/nginx:v1.0.0
registry.gitlab.com/org/monorepo/cron:v1.0.0
```

**Senior choice:** Each service gets a sub-path. Each is versioned independently. Only build what changed using `rules: changes:`. Use a shared base image for common dependencies.

---

### Multi-environment deployment

**Problem:** The same app runs in dev, staging, and production. Should each environment have its own image?

**Answer:** No. One image, multiple environments. Configuration comes from environment variables, not baked into the image.

```text
Build: app:sha-abc123
  → Deploy to dev   (env vars for dev)
  → Deploy to staging (env vars for staging)
  → Promote to app:v1.2.0
  → Deploy to production (env vars for production)
```

**Anti-pattern:** `app:staging-v1.2.0` and `app:production-v1.2.0` — different builds means different behavior.

---

### Private vs. public images

| Factor | Private | Public |
|---|---|---|
| Access | Auth required | Anyone can pull |
| Use case | Internal apps | OSS, public tools |
| Cost | Free on GitLab | Free on GitLab |
| DX | Need login/tokens | Just `docker pull` |

**Senior choice:** Private by default. Public only for open-source projects. Use deploy tokens for external access.

---

### Registry cleanup

**Problem:** After 6 months, you have 2,000 tags consuming 50GB.

**Senior choice:** Automated cleanup policy:
- Branch tags: delete 14 days after merge.
- SHA tags: keep last 20.
- Semver tags: keep forever (or until EOL).
- Schedule a weekly cleanup pipeline.

---

### Versioning

**Senior choice:** Follow semver for releases. Use commit SHA for CI traceability. Never rely on mutable tags for production.

---

### Using `:latest` vs. immutable tag

| Factor | `:latest` | `:v1.2.0` | `@sha256:...` |
|---|---|---|---|
| Mutability | Mutable (changes) | Should be immutable | Immutable (guaranteed) |
| Debugging | "Which version is latest?" | Clear | Exact |
| Rollback | Impossible | Easy | Easiest |
| Caching | Unpredictable | Predictable | Predictable |

**Senior choice:** Use `:latest` for local development only. Use semver or digest for staging and production.

---

### Security scanning

**Problem:** Your image contains a vulnerable version of OpenSSL. You deploy to production without knowing.

**Senior choice:** Scan every image in CI. Block deployment on CRITICAL findings. Report vulnerabilities in MR widget. Schedule weekly full scans.

```yaml
include:
  - template: Security/Container-Scanning.gitlab-ci.yml
```

---

### Large image management

**Problem:** Your Node.js image is 1.2GB. Pulls take 60 seconds. Storage costs add up.

| Technique | Before | After |
|---|---|---|
| Multi-stage build | 1.2GB | 150MB |
| Alpine base | 200MB | 50MB |
| `.dockerignore` | +200MB junk | Clean context |
| Fewer layers | Many small layers | Consolidated |

**Senior choice:** Multi-stage build with Alpine. Measure image size in CI. Alert if image exceeds threshold.

```yaml
check-size:
  script:
    - SIZE=$(docker image inspect $CI_REGISTRY_IMAGE:$CI_COMMIT_SHA --format='{{.Size}}')
    - |
      if [ $SIZE -gt 200000000 ]; then
        echo "WARNING: Image size is $(($SIZE / 1000000))MB — exceeds 200MB threshold"
        exit 1
      fi
```

---

## 6. Brainstorm / Open Questions

### Architecture

1. Should each microservice have its own GitLab project (and registry), or should they share a monorepo registry with sub-paths?
2. When should you create a dedicated base-images project vs. using public base images?
3. How should your registry naming convention evolve as the org grows from 5 to 50 to 500 services?
4. Should CI/CD images (like custom runners or tool images) live in the same registry as application images?
5. How do you handle diamond dependency problems when multiple services share a base image that updates?
6. Should infrastructure (Terraform, Helm) have its own image registry path?
7. When is a pull-through cache (Harbor) justified over direct GitLab registry access?

### Scaling

8. At what image count does registry performance degrade noticeably?
9. How do you handle 100 concurrent pushes during a monorepo CI spike?
10. When should you replicate your registry to a second region?
11. How do you shard registry storage across backends?
12. What is the pull latency impact of a 500MB image vs. 50MB in a Kubernetes pod startup?
13. How many tags per repository before cleanup becomes mandatory for performance?
14. How do you measure registry I/O impact on CI pipeline duration?

### Security

15. If a developer pushes a malicious layer to an image, how would you detect it?
16. How do you prevent secret leakage in Docker image layers?
17. Should `docker build --secret` replace `ARG` for build-time secrets?
18. How do you verify that the image in production is exactly what CI built?
19. What happens if a base image on Docker Hub is compromised after you've built FROM it?
20. How should signing keys be rotated without breaking existing verification?
21. Should vulnerability scanning block MR merge or only production deployment?

### DX / Maintainability

22. How do you make it easy for a new engineer to find the right image for their service?
23. Should there be a central "image catalog" with descriptions and owners?
24. How do you enforce Dockerfile best practices across 50 projects?
25. How do you test a Dockerfile change without pushing to the registry?
26. Should multi-stage Dockerfiles be split into multiple files for readability?
27. How do you document which services use which base images?
28. What is the right level of abstraction for shared Dockerfile fragments?

### Cost

29. How much does your registry storage cost per GB per month?
30. What's the cost difference between storing 200 images at 1GB vs. 50MB each?
31. When do cleanup policies pay for themselves in storage savings?
32. Should you pay for a premium registry (Harbor, JFrog) or use GitLab's built-in?
33. How do you attribute registry costs to specific teams or projects?
34. What is the bandwidth cost of pulling images across regions?

### Reliability

35. What happens if the registry is down during a Kubernetes rolling update?
36. How do you ensure image availability if GitLab has an outage?
37. Should you mirror critical production images to a backup registry?
38. What is your recovery plan if a production image tag is accidentally deleted?
39. How do you detect silent image corruption?
40. What SLA should the registry have for production deployments?

### Release Strategy

41. Should the same image be promoted from staging to production, or rebuilt?
42. When should a branch image be deleted — on MR merge, on schedule, or never?
43. What happens if `:latest` points to the wrong image?
44. How should tags be designed for monorepo microservices with independent release cycles?
45. Should you maintain floating minor version tags (`:v1.2`) or only exact (`:v1.2.3`)?
46. How do you coordinate image updates when Service A depends on Service B's image?
47. What is the rollback procedure when the previous image also has a bug?

---

## 7. Practice Questions

### Beginner (Level 1)

**Q1. Single choice:** What is the correct URL format for a GitLab Container Registry image?

- A. `docker.io/org/app:v1.0.0`
- B. `registry.gitlab.com/org/app:v1.0.0`
- C. `gitlab.com/registry/org/app:v1.0.0`
- D. `hub.gitlab.com/org/app:v1.0.0`

<details><summary>Answer</summary>B. The format is <code>registry.gitlab.com/&lt;namespace&gt;/&lt;project&gt;:&lt;tag&gt;</code>. A is Docker Hub. C and D are incorrect URLs.</details>

---

**Q2. Fill in the blank:** To log in to GitLab Container Registry, run `docker login _______`.

<details><summary>Answer</summary><code>registry.gitlab.com</code>. You must specify the registry hostname, not just <code>gitlab.com</code>.</details>

---

**Q3. True/False:** `docker push my-app:v1.0.0` will push the image to GitLab Container Registry.

<details><summary>Answer</summary>False. The image must be tagged with the full registry path: <code>registry.gitlab.com/org/app:v1.0.0</code>. Without the registry prefix, Docker tries to push to Docker Hub.</details>

---

**Q4. Single choice:** What is the difference between an image tag and a digest?

- A. Tags are immutable; digests are mutable
- B. Tags are human-readable labels; digests are SHA256 hashes
- C. Tags identify registries; digests identify repositories
- D. They are the same thing

<details><summary>Answer</summary>B. A tag like <code>:v1.0.0</code> is a human-readable label that <em>can</em> be moved. A digest like <code>sha256:abc123...</code> is a content hash that uniquely and immutably identifies an image.</details>

---

**Q5. Matching:** Match each command to its purpose.

| Command | Purpose |
|---|---|
| A. `docker build` | 1. Download image from registry |
| B. `docker tag` | 2. Upload image to registry |
| C. `docker push` | 3. Create image from Dockerfile |
| D. `docker pull` | 4. Label an image with a new name |

<details><summary>Answer</summary>A→3, B→4, C→2, D→1</details>

---

**Q6. Debugging:** You run `docker push registry.gitlab.com/org/app:v1` and get `denied: requested access to the resource is denied`. What should you check?

<details><summary>Answer</summary>
1. Have you run <code>docker login registry.gitlab.com</code>?<br>
2. Does your token have the <code>write_registry</code> scope?<br>
3. Do you have Developer (or higher) role on the project?<br>
4. Is the image path exactly matching your GitLab namespace/project?
</details>

---

**Q7. Single choice:** What does `:latest` mean in Docker?

- A. The most recently built image, guaranteed by Docker
- B. A conventional tag that may or may not point to the newest image
- C. A special immutable reference to the stable release
- D. An automatically generated tag by GitLab

<details><summary>Answer</summary>B. <code>:latest</code> is just a convention. It's a mutable tag that someone must explicitly update. It could point to any image, and there's no guarantee it's the newest.</details>

---

**Q8. Fill in the blank:** The command to give a local image a registry-compatible name is `docker _______ local-name registry.gitlab.com/org/app:tag`.

<details><summary>Answer</summary><code>tag</code>. <code>docker tag</code> creates a new name (reference) pointing to the same image.</details>

---

**Q9. True/False:** You need to create the container registry repository manually in GitLab before pushing.

<details><summary>Answer</summary>False. GitLab automatically creates the repository on first push. No manual setup needed.</details>

---

**Q10. Scenario:** You pushed `:v1.0.0` yesterday and `:v1.0.0` again today with different code. A colleague pulls `:v1.0.0`. Which version do they get?

<details><summary>Answer</summary>They get today's version — the second push overwrote the tag. This is why tags should be treated as immutable for releases. To prevent this, check if the tag exists before pushing, or use digests for critical references.</details>

---

### Junior (Level 2)

**Q11. Single choice:** In GitLab CI, what does `$CI_REGISTRY_IMAGE` resolve to?

- A. `registry.gitlab.com`
- B. `registry.gitlab.com/org/app`
- C. `gitlab-ci-token`
- D. The Docker image used by the job

<details><summary>Answer</summary>B. <code>$CI_REGISTRY_IMAGE</code> is the full image path for the project: <code>registry.gitlab.com/&lt;namespace&gt;/&lt;project&gt;</code>. A is <code>$CI_REGISTRY</code>. C is <code>$CI_REGISTRY_USER</code>.</details>

---

**Q12. Debugging:** Your CI job runs `docker push $CI_REGISTRY_IMAGE:$CI_COMMIT_SHA` but fails with `unauthorized`. The pipeline runs on a merge request. What's wrong?

<details><summary>Answer</summary>Check that the job runs <code>docker login -u $CI_REGISTRY_USER -p $CI_REGISTRY_PASSWORD $CI_REGISTRY</code> before pushing. The CI job token is available but you must explicitly log in. Also verify the MR source branch has permission to push.</details>

---

**Q13. Fill in the blank:** To convert a branch name like `feature/user-auth` to a safe Docker tag, GitLab provides the variable `$CI_COMMIT_REF_______`.

<details><summary>Answer</summary><code>SLUG</code>. <code>$CI_COMMIT_REF_SLUG</code> converts <code>feature/user-auth</code> to <code>feature-user-auth</code> (lowercase, URL-safe).</details>

---

**Q14. True/False:** Cache and registry images serve the same purpose in GitLab CI.

<details><summary>Answer</summary>False. Cache speeds up dependency installation across pipelines (e.g., <code>node_modules</code>). Registry images are built application artifacts intended for deployment. They serve completely different purposes.</details>

---

**Q15. Multiple choice:** Which approaches help reduce Docker image size? (Select all)

- A. Multi-stage builds
- B. Using Alpine base images
- C. Adding a `.dockerignore` file
- D. Using `:latest` tag

<details><summary>Answer</summary>A, B, and C. Multi-stage builds exclude build tools from the final image. Alpine is much smaller than Debian/Ubuntu. <code>.dockerignore</code> prevents unnecessary files from entering the build context. D (the tag name) has no effect on image size.</details>

---

**Q16. Scenario:** Your Docker Compose file references `image: registry.gitlab.com/org/app:v1.2.0`. Running `docker compose up` fails with `unauthorized`. What should you do?

<details><summary>Answer</summary>Run <code>docker login registry.gitlab.com</code> with a valid token before <code>docker compose up</code>. For automated servers, create a deploy token with <code>read_registry</code> scope and use it for login.</details>

---

**Q17. Single choice:** You want to delete old branch images automatically. What's the recommended approach?

- A. Manually delete from GitLab UI weekly
- B. Use GitLab's built-in cleanup policy in project settings
- C. Never delete images
- D. Delete the entire registry and start over

<details><summary>Answer</summary>B. GitLab's cleanup policy (Settings → Packages & Registries → Clean up image tags) lets you define retention rules by regex, age, and count. A doesn't scale. C wastes storage. D is destructive.</details>

---

**Q18. Matching:** Match the CI variable to its value.

| Variable | Value |
|---|---|
| A. `$CI_REGISTRY` | 1. `gitlab-ci-token` |
| B. `$CI_REGISTRY_IMAGE` | 2. Auto-generated job token |
| C. `$CI_REGISTRY_USER` | 3. `registry.gitlab.com` |
| D. `$CI_REGISTRY_PASSWORD` | 4. `registry.gitlab.com/org/app` |

<details><summary>Answer</summary>A→3, B→4, C→1, D→2</details>

---

**Q19. True/False:** You should use your personal access token in `.gitlab-ci.yml` for Docker registry authentication.

<details><summary>Answer</summary>False. Use the built-in <code>$CI_REGISTRY_USER</code> and <code>$CI_REGISTRY_PASSWORD</code> which are auto-injected CI job tokens. Personal tokens are tied to individuals, can't be rotated easily, and are a security risk if committed.</details>

---

**Q20. Scenario:** You have a monorepo with `frontend/` and `backend/` directories. How do you organize images in the registry?

<details><summary>Answer</summary>Use sub-paths: <code>$CI_REGISTRY_IMAGE/frontend:tag</code> and <code>$CI_REGISTRY_IMAGE/backend:tag</code>. GitLab supports nested repository paths. Build and push each service independently using <code>rules: changes:</code> to only build what changed.</details>

---

### Senior / Expert (Level 3–4)

**Q21. Scenario:** Your team deploys `:latest` to production. One morning, a dev pushes a broken build that updates `:latest`. Production auto-scales and pulls the broken image. What went wrong and how do you prevent it?

<details><summary>Answer</summary>
1. <strong>Problem:</strong> <code>:latest</code> is mutable. New pushes change what it points to. Auto-scaling pods pull the new (broken) version.<br>
2. <strong>Prevention:</strong> Never use <code>:latest</code> in production manifests. Use immutable semver tags (<code>:v1.2.0</code>) or digests (<code>@sha256:...</code>). Pin the exact version in deployment configs.
</details>

---

**Q22. True/False:** Rebuilding the same Dockerfile with the same source code always produces the exact same image digest.

<details><summary>Answer</summary>False. Docker builds are not reproducible by default. Timestamps, non-pinned dependencies (<code>apt-get update</code>, <code>npm install</code> without lockfile), and layer metadata can change. To improve reproducibility: pin all dependencies, use lockfiles, and pin base images by digest.</details>

---

**Q23. Design question:** Your organization has 200 microservices across 30 teams. Design the registry architecture.

<details><summary>Answer</summary>
1. <strong>Base images:</strong> Platform team maintains <code>org/base-images/</code> with hardened, scanned images.<br>
2. <strong>Per-team projects:</strong> Each team owns their project registries.<br>
3. <strong>Naming convention:</strong> <code>registry.gitlab.com/org/team-name/service:tag</code>.<br>
4. <strong>Tagging:</strong> SHA for builds, semver for releases, enforced by shared CI templates.<br>
5. <strong>Cleanup:</strong> Organization-wide cleanup policy. Branch tags: 14 days. SHA tags: last 20. Semver: kept.<br>
6. <strong>Security:</strong> Container scanning in all pipelines. Signed images for production. Admission controller rejecting unsigned images.<br>
7. <strong>Access:</strong> Deploy tokens for cross-project pulls. No personal tokens in automation.
</details>

---

**Q24. Single choice:** Which approach is most secure for production image references?

- A. `image: registry.gitlab.com/org/app:latest`
- B. `image: registry.gitlab.com/org/app:v1.2.0`
- C. `image: registry.gitlab.com/org/app@sha256:abc123...`
- D. `image: org/app`

<details><summary>Answer</summary>C. A digest reference is immutable and cannot be tampered with (tag rewriting, registry compromise). B is good but tags can theoretically be overwritten. A is mutable and unpredictable. D pulls from Docker Hub, not your private registry.</details>

---

**Q25. Debugging:** A Kubernetes deployment is stuck in `ImagePullBackOff`. The image exists in GitLab Container Registry. What should you investigate?

<details><summary>Answer</summary>
1. Does the K8s cluster have an <code>imagePullSecret</code> configured for <code>registry.gitlab.com</code>?<br>
2. Is the deploy token valid and not expired?<br>
3. Is the image path and tag exact (case-sensitive)?<br>
4. Can the cluster reach <code>registry.gitlab.com</code> (network/firewall)?<br>
5. Run <code>kubectl describe pod</code> and check the Events section for the exact error.
</details>

---

**Q26. Scenario:** You promote an image from staging to production by re-tagging `:sha-abc123` as `:v1.2.0`. A week later, you need to audit what exactly was in that image. How do you trace it?

<details><summary>Answer</summary>
1. The semver tag <code>:v1.2.0</code> has a digest (visible in registry UI or via <code>docker manifest inspect</code>).<br>
2. The SHA tag <code>:sha-abc123</code> points to the same digest — verify they match.<br>
3. The commit <code>abc123</code> is the source code that built the image.<br>
4. The CI pipeline for that commit has the build logs, Dockerfile, and lockfile.<br>
5. If you generate SBOMs, the artifact from that pipeline lists every dependency.
</details>

---

**Q27. Fill in the blank:** To verify an image hasn't been tampered with after build, you can sign it with _______ and verify at deployment time.

<details><summary>Answer</summary><code>Cosign</code> (from Sigstore). Cosign generates a cryptographic signature tied to the image digest. Kubernetes admission controllers (Kyverno, OPA) can verify signatures before allowing pods to run.</details>

---

**Q28. Design question:** Your registry contains 10TB of images. Storage costs are growing 20% monthly. Design a cost reduction plan.

<details><summary>Answer</summary>
1. <strong>Audit:</strong> Identify largest images and most prolific pushers.<br>
2. <strong>Multi-stage builds:</strong> Reduce image sizes from 1GB to 100-200MB.<br>
3. <strong>Cleanup policy:</strong> Delete branch tags after 7 days. Keep last 10 SHA tags. Keep semver tags for 1 year.<br>
4. <strong>Delete untagged manifests:</strong> Orphaned layers consume storage.<br>
5. <strong>Push less:</strong> Only push on main and tags, not every feature branch commit.<br>
6. <strong>Alpine migration:</strong> Move base images to Alpine variants.<br>
7. <strong>Monitor:</strong> Dashboard tracking weekly storage growth by project.
</details>

---

**Q29. True/False:** A deploy token with `read_registry` scope can push images to the registry.

<details><summary>Answer</summary>False. <code>read_registry</code> only allows pulling. To push, you need <code>write_registry</code> scope. Deploy tokens for production servers should be read-only (principle of least privilege).</details>

---

**Q30. Scenario:** Your CI builds an image and pushes it. Minutes later, you scan it and find a CRITICAL vulnerability in the base image. The image is already deployed to staging. What's your incident response?

<details><summary>Answer</summary>
1. <strong>Assess:</strong> Is the vulnerability exploitable in your context? Check the CVE details.<br>
2. <strong>Contain:</strong> If critical, stop the staging deployment from promoting to production.<br>
3. <strong>Fix:</strong> Update the base image (rebuild with patched base), push new image.<br>
4. <strong>Verify:</strong> Re-scan. Confirm vulnerability is resolved.<br>
5. <strong>Deploy:</strong> Roll out the fixed image to staging, then production.<br>
6. <strong>Prevent:</strong> Pin base images by digest. Scan before deploy, not after. Add scanning as a pipeline gate.
</details>

---

## 8. Personalized Recommendations

### GitLab Container Registry patterns most useful for your stack

As a React/Next.js/Astro developer, your primary container use cases are:

1. **Static site images:** Nginx serving built HTML/CSS/JS (React, Astro). Multi-stage Dockerfile: build with Node, serve with Nginx.
2. **Next.js standalone images:** Server-side rendering containers using Next.js standalone output.
3. **Preview deployments:** Branch-tagged images for reviewer previews.
4. **CI integration:** Auto-push on main, semver tag on release.
5. **Docker Compose for local dev:** Pull images from registry to replicate staging locally.

### What to learn first

| Priority | Topic |
|---|---|
| 1 | Docker basics: build, tag, push, pull |
| 2 | Multi-stage Dockerfiles for frontend apps |
| 3 | GitLab CI variables ($CI_REGISTRY_*) |
| 4 | Pushing images from CI pipeline |
| 5 | Tag strategies: SHA + semver |
| 6 | .dockerignore for clean builds |
| 7 | Image size optimization |
| 8 | Cleanup policies |
| 9 | Deploy tokens for server pulls |
| 10 | Security scanning (Trivy) |

### Which image/tagging workflows to build first

| Order | Workflow | Why |
|---|---|---|
| 1st | Build + push on main (SHA tag) | Foundation |
| 2nd | Semver tag on git tag | Release process |
| 3rd | Cleanup policy | Prevent storage bloat |
| 4th | Branch preview images | Better code review |
| 5th | Docker Compose with registry images | Local dev parity |
| 6th | Vulnerability scanning in CI | Security baseline |
| 7th | Image promotion (staging → production) | Production safety |

### Common mistakes frontend engineers make with registries

| Mistake | Why it happens | Fix |
|---|---|---|
| Shipping `node_modules` in image | No `.dockerignore` | Create `.dockerignore`, use multi-stage |
| 1GB+ images | Single-stage build | Multi-stage: build stage + tiny runtime stage |
| Using `:latest` everywhere | "It's the default" | Use SHA/semver tags |
| Secrets in Dockerfile | `ARG API_KEY=...` | Use build secrets or runtime env vars |
| Not caching Docker layers | Copies everything before `npm ci` | Order: COPY lockfile → install → COPY source |
| Never cleaning up | "Storage is cheap" | Set cleanup policies from day 1 |
| Using personal token in CI | Quick and dirty | Use `$CI_REGISTRY_PASSWORD` |
| Rebuilding for each environment | "Staging and production are different" | Build once, configure with env vars |

### How to evolve from local Docker to production-grade registry

```text
Phase 1: Local Docker
  └── Dockerfile + docker build + docker run locally

Phase 2: Registry basics
  └── Push to GitLab registry manually, verify in UI

Phase 3: CI integration
  └── Auto-push on main with SHA tag

Phase 4: Release workflow
  └── Semver tags on git tags, cleanup policy

Phase 5: Multi-stage builds
  └── Optimized images (50-150MB), .dockerignore

Phase 6: Security
  └── Vulnerability scanning, deploy tokens, no personal tokens

Phase 7: Promotion
  └── Build once, promote staging → production (same digest)

Phase 8: Advanced
  └── Image signing, SBOM, monorepo sub-paths, shared base images
```

### 30-day learning plan

#### Week 1: Docker Foundations (Days 1–7)

| Day | Task | Deliverable |
|---|---|---|
| 1 | Write a Dockerfile for your React/Astro app | Working Dockerfile |
| 2 | Build and run the image locally | Container running on localhost |
| 3 | Create multi-stage Dockerfile (build + nginx) | Image under 100MB |
| 4 | Create `.dockerignore`, measure size difference | Optimized build context |
| 5 | Log in to GitLab registry, push manually | Image visible in GitLab UI |
| 6 | Tag with multiple tags (`:v1.0.0`, `:latest`) | Multi-tag push |
| 7 | Pull on a different machine or clean Docker | Verify registry works end-to-end |

#### Week 2: CI Integration (Days 8–14)

| Day | Task | Deliverable |
|---|---|---|
| 8 | Add Docker build+push to `.gitlab-ci.yml` | CI pushes image on main |
| 9 | Use `$CI_REGISTRY_*` variables | No hardcoded paths |
| 10 | Add commit SHA tagging | Traceable builds |
| 11 | Add semver tag on git tag push | Release workflow |
| 12 | Set up GitLab cleanup policy | Auto-cleanup old tags |
| 13 | Add `--cache-from` for faster CI builds | Faster pipelines |
| 14 | Review and document your image workflow | Clear team documentation |

#### Week 3: Deployment (Days 15–21)

| Day | Task | Deliverable |
|---|---|---|
| 15 | Create Docker Compose file using registry images | Local dev from registry |
| 16 | Create a deploy token for server access | Secure server pulls |
| 17 | Deploy image to a staging environment | Staging running from registry |
| 18 | Implement image promotion (staging → production tag) | Build once, deploy many |
| 19 | Add branch preview images on MR | Reviewer previews |
| 20 | Add environment tracking in GitLab | Deployment history |
| 21 | Practice rollback by re-deploying previous tag | Rollback confidence |

#### Week 4: Security & Advanced (Days 22–30)

| Day | Task | Deliverable |
|---|---|---|
| 22 | Add Trivy or GitLab container scanning | Vulnerability reports |
| 23 | Pin base image by digest | Reproducible builds |
| 24 | Add image size check in CI | Size gate |
| 25 | Study monorepo sub-path image organization | Architecture knowledge |
| 26 | Study Cosign image signing | Security knowledge |
| 27 | Study SBOM generation with Syft | Compliance knowledge |
| 28 | Audit your registry for unused images | Storage optimization |
| 29 | Create a shared base image project | Org-wide reuse |
| 30 | Write architecture decision record for your registry strategy | Documentation |

---

## Summary, Next Steps, and Advanced Topics

### Concise Summary

GitLab Container Registry is a built-in image store integrated into every GitLab project. For a frontend engineer, the key path to mastery is:

1. **Start** with a multi-stage Dockerfile (build with Node, serve with Nginx/standalone).
2. **Automate** with CI: push SHA-tagged images on main, semver on tags.
3. **Optimize** with `.dockerignore`, Alpine bases, layer caching.
4. **Secure** with deploy tokens (not PATs), vulnerability scanning, cleanup policies.
5. **Mature** with image promotion (build once, deploy many), signed images, and SBOM.
6. **Scale** with monorepo sub-paths, shared base images, and governance policies.

The key mindset: **an image tag is a deployment contract.** Treat it with the same rigor as a release version.

### Next Steps

1. Dockerize your current project with a multi-stage build today.
2. Push to GitLab Container Registry from CI with SHA tagging.
3. Add semver tagging on git tag pushes.
4. Set up a cleanup policy immediately (before storage grows).
5. Add vulnerability scanning to your pipeline.
6. Create deploy tokens for any server that needs to pull images.

### Suggested Advanced Topics

| Topic | Why it matters |
|---|---|
| OCI image specification | Understand what images actually are |
| Buildx and multi-platform builds | ARM support (Apple Silicon, AWS Graviton) |
| Cosign and Sigstore | Supply chain security standard |
| SLSA provenance | Build attestation for compliance |
| Harbor as a registry proxy | Caching, replication, scanning |
| Kubernetes admission controllers | Enforce image policies at deploy time |
| Distroless images | Minimal attack surface (no shell, no package manager) |
| Docker layer analysis (dive) | Inspect and optimize layers |
| GitLab Dependency Proxy | Cache Docker Hub images to avoid rate limits |
| OCI artifacts (Helm, WASM) | Registries for non-Docker artifacts |
| Image attestation and SBOM | Full software supply chain visibility |
| Registry migration strategies | Moving between registry providers |
| Ephemeral build environments | Hermetic builds for reproducibility |
| GitLab Geo for registry replication | Self-managed multi-region |
| Policy-as-code for registries | OPA/Kyverno for enforcement |
