# Docker & Docker Compose — Complete Deep-Dive Engineering Guide

> For a frontend engineer (React / Next.js / Astro / TypeScript) moving toward backend, DevOps, infrastructure, deployment, and platform engineering.

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

### 1.1 What Docker Is

Docker is a platform for building, shipping, and running applications inside **containers** — lightweight, isolated environments that package your code together with everything it needs to run: runtime, libraries, system tools, and configuration.

**The React analogy:** Think of a React component as a self-contained unit — it declares its own props, state, and rendering logic. A Docker container is the same idea applied to an entire application: it declares its own OS dependencies, runtime, files, and network ports. Just as you can render the same React component anywhere (browser, SSR, tests), you can run the same Docker container anywhere (your laptop, CI, staging, production).

### 1.2 Why Containers Exist

Before containers, deploying software meant:
- "It works on my machine" — different Node versions, missing system libraries, OS differences.
- Slow, fragile provisioning — manually installing dependencies on servers.
- Environment drift — staging doesn't match production.
- Resource waste — each app gets a full VM.

Containers solve all of this. A container is a promise: **"This application will run identically everywhere."**

**Frontend analogy:** You already understand this problem. When a teammate clones your repo and `npm install` gives different results because of OS differences or Node version mismatches — that's the problem containers solve at the infrastructure level. Docker is like `nix develop` or a lockfile for your entire operating environment, not just your npm packages.

### 1.3 Key Distinctions

| Concept | What it is | Analogy |
|---|---|---|
| **Process** | A running program on your OS | A single function executing |
| **Container** | An isolated process with its own filesystem, network, and resource limits | A sandboxed iframe — isolated from the host but sharing the kernel |
| **Virtual Machine** | A full OS running on emulated hardware | A completely separate computer inside your computer |
| **Docker Engine** | The daemon (background service) that builds and runs containers | Like the Node.js runtime — it interprets and executes |
| **Docker Desktop** | GUI + Docker Engine + extras (VM on Mac/Windows) | Like VS Code wrapping a language server |
| **Docker Compose** | A tool for defining and running multi-container apps from a YAML file | Like `package.json` scripts but for containers — declares which services to run together |
| **Kubernetes** | A container orchestration platform for running containers at scale across many machines | Like Vercel's infrastructure — manages scaling, routing, and failover, but you control it |

**Container vs. VM — the critical difference:**

```text
Virtual Machine:                    Container:
┌─────────────────────┐            ┌─────────────────────┐
│     Your App        │            │     Your App        │
│     Libraries       │            │     Libraries       │
│     Guest OS        │  ← full OS │     (no guest OS)   │
│     Hypervisor      │            │     Docker Engine    │
│     Host OS         │            │     Host OS         │
│     Hardware        │            │     Hardware        │
└─────────────────────┘            └─────────────────────┘

VMs: heavy, slow to start, full isolation
Containers: lightweight, instant start, process-level isolation
```

### 1.4 Core Concepts

#### Image

A read-only template containing the application code, runtime, libraries, and filesystem. Images are built from a Dockerfile and stored in registries.

**Analogy:** An image is like a built `dist/` folder from `npm run build` — it's the immutable artifact. You don't modify it; you create a new build.

#### Container

A running instance of an image. You can run multiple containers from the same image.

**Analogy:** An image is the class; a container is the instance. Or: the image is the Docker equivalent of your built Next.js app, and the container is that app actually running on a server.

#### Volume

Persistent storage that survives container restarts and removal. Used for databases, uploads, and any data that must persist.

**Analogy:** Like `localStorage` in the browser — the container (page) can be refreshed or destroyed, but the volume (localStorage) persists.

#### Network

Docker creates isolated networks for containers to communicate. Containers on the same network can reach each other by service name.

**Analogy:** Like a private LAN — containers on the same Docker network can talk to each other using hostnames, but they're isolated from the outside by default.

#### Layer

Each instruction in a Dockerfile creates a filesystem layer. Layers are cached and shared between images, making builds fast and storage efficient.

**Analogy:** Like Git commits — each layer is a diff on top of the previous one. Docker caches unchanged layers so rebuilds only reprocess what changed.

#### Registry

A storage and distribution service for Docker images. Docker Hub is the public default. GitHub Container Registry (ghcr.io), AWS ECR, and Google Artifact Registry are common alternatives.

**Analogy:** Like npm registry for packages, but for container images.

#### Dockerfile

A text file with instructions to build an image. Each instruction (FROM, COPY, RUN, etc.) creates a layer.

**Analogy:** Like a `next.config.js` + build script — it declares how to construct the application artifact.

#### Build Context

The set of files sent to the Docker daemon when building an image. Controlled by what you pass to `docker build` and filtered by `.dockerignore`.

**Analogy:** Like the files Webpack/Vite processes — everything in the build context is available during the build. A `.dockerignore` is like a `.gitignore` for builds.

### 1.5 The Lifecycle: Source Code → Deployment

```text
┌──────────────────────────────────────────────────────────────┐
│  SOURCE CODE                                                  │
│                                                              │
│  src/  package.json  Dockerfile  docker-compose.yml          │
│                                                              │
└──────────────────────────┬───────────────────────────────────┘
                           │ docker build
                           ▼
┌──────────────────────────────────────────────────────────────┐
│  IMAGE                                                        │
│                                                              │
│  Immutable artifact containing app + runtime + dependencies  │
│  Tagged: myapp:1.0.0  myapp:latest                           │
│                                                              │
└──────────────────────────┬───────────────────────────────────┘
                           │ docker push
                           ▼
┌──────────────────────────────────────────────────────────────┐
│  REGISTRY                                                     │
│                                                              │
│  Docker Hub / GHCR / ECR / Artifact Registry                 │
│  Stores and distributes images                               │
│                                                              │
└──────────────────────────┬───────────────────────────────────┘
                           │ docker pull + docker run
                           ▼
┌──────────────────────────────────────────────────────────────┐
│  CONTAINER(S)                                                 │
│                                                              │
│  Running instance(s) of the image                            │
│  Mapped ports, mounted volumes, connected networks           │
│  On: local machine / CI / staging / production               │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

### 1.6 Docker vs. Your Current Local Setup

| Dimension | Local Node.js | Docker |
|---|---|---|
| Runtime | Whatever Node version is installed | Exact Node version declared in Dockerfile |
| Dependencies | `node_modules` on your filesystem | Isolated inside the container |
| OS libraries | Whatever your OS has | Declared and installed in the image |
| Database | Install PostgreSQL/Redis locally | Run as a container alongside your app |
| Sharing setup | README with "install these things" | `docker compose up` — done |
| Reproducibility | "Works on my machine" | Guaranteed identical everywhere |
| Cleanup | Leftover processes, global installs | `docker compose down` — everything gone |

### 1.7 Why Docker Is Useful for React / Next.js / Astro

| Scenario | Without Docker | With Docker |
|---|---|---|
| **Local development** | Install Node, npm, DB, Redis, etc. | `docker compose up` |
| **Team onboarding** | 2-hour setup guide | `git clone && docker compose up` |
| **CI/CD** | Configure runner with exact toolchain | Build image, run tests inside it |
| **Staging/production** | Configure server, install deps, pray | Deploy the same image you tested |
| **Running Next.js SSR** | Install Node on server, manage process | Container with Node + Next.js, portable |
| **Full-stack local** | Frontend + API + DB + Redis all manual | One `docker-compose.yml` defines everything |

### 1.8 Mental Model Diagram

```text
┌─────────────────────────────────────────────────┐
│               YOUR PROJECT                       │
│                                                 │
│  Dockerfile          docker-compose.yml         │
│  .dockerignore       .env                       │
│  src/  package.json  ...                        │
│                                                 │
└──────────────┬──────────────────────────────────┘
               │
               │ docker compose up
               ▼
┌─────────────────────────────────────────────────┐
│           DOCKER ENGINE                          │
│                                                 │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐     │
│  │ frontend │  │   api    │  │ postgres │     │
│  │ :3000    │  │ :4000    │  │ :5432    │     │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘     │
│       │              │              │           │
│       └──────────────┼──────────────┘           │
│                      │                          │
│              Docker Network                     │
│              (services find each other by name) │
│                                                 │
│  ┌──────────────────────────┐                   │
│  │    Volumes               │                   │
│  │    (persistent data)     │                   │
│  └──────────────────────────┘                   │
│                                                 │
└─────────────────────────────────────────────────┘
```

---

## 2. Learning Roadmap by Skill Level

### Level 1 — Newbie

**Goal:** Run your first container, write your first Dockerfile, understand the basics.

#### Installing Docker

- **macOS / Windows:** Install Docker Desktop from https://docker.com. It includes Docker Engine, Docker CLI, Docker Compose, and a GUI.
- **Linux:** Install Docker Engine directly via your package manager. Docker Compose v2 is included as a plugin.

Verify installation:

```bash
docker --version
docker compose version
docker run hello-world
```

#### Understanding image vs. container

| Image | Container |
|---|---|
| Blueprint / recipe | Running instance |
| Read-only | Read-write layer on top |
| Built from Dockerfile | Created from image |
| Stored on disk | Running as a process |
| Can exist without running | Exists only while alive (or stopped) |

#### Basic Docker commands

```bash
# Run a container
docker run -it node:20-alpine node -e "console.log('Hello')"

# Run and expose a port
docker run -p 3000:3000 my-app

# List running containers
docker ps

# List all containers (including stopped)
docker ps -a

# Stop a container
docker stop <container-id>

# Remove a container
docker rm <container-id>

# List images
docker images

# Remove an image
docker rmi <image-id>

# Build an image
docker build -t my-app .

# View logs
docker logs <container-id>

# Execute a command inside a running container
docker exec -it <container-id> sh
```

#### Your first Dockerfile — a Node.js app

```dockerfile
# Use an official Node.js runtime as the base image
FROM node:20-alpine

# Set the working directory inside the container
WORKDIR /app

# Copy package files first (for layer caching)
COPY package.json package-lock.json ./

# Install dependencies
RUN npm ci

# Copy the rest of the source code
COPY . .

# Expose the port the app runs on
EXPOSE 3000

# Define the command to run the app
CMD ["node", "server.js"]
```

**Build and run it:**

```bash
docker build -t my-node-app .
docker run -p 3000:3000 my-node-app
```

#### Exposing ports

```bash
# Map host port 8080 to container port 3000
docker run -p 8080:3000 my-app

# Map multiple ports
docker run -p 3000:3000 -p 9229:9229 my-app
```

**The rule:** `-p HOST:CONTAINER`. The left side is your machine, the right side is inside the container.

#### Mounting files (bind mounts)

```bash
# Mount current directory into the container
docker run -v $(pwd):/app -p 3000:3000 my-app

# Read-only mount
docker run -v $(pwd)/config:/app/config:ro my-app
```

#### Common mistakes at this level

| Mistake | What happens | Fix |
|---|---|---|
| Forgetting to expose ports | App runs but you can't reach it | Add `-p` flag or `EXPOSE` + `-p` |
| Not using `.dockerignore` | `node_modules` copied into image, slow build, huge image | Create `.dockerignore` with `node_modules`, `.git`, `dist` |
| Using `npm install` instead of `npm ci` | Non-deterministic installs, lockfile drift | Always use `npm ci` in Dockerfiles |
| `COPY . .` before `npm ci` | Breaks layer cache — every code change reinstalls deps | Copy `package.json` + lockfile first, then `npm ci`, then `COPY . .` |
| Running as root | Security risk | Add `USER node` (or create a non-root user) |
| Using `node:20` instead of `node:20-alpine` | Image is 1GB+ instead of ~180MB | Use alpine or slim variants |

#### 5 beginner exercises

1. **Run a container:** Pull and run `nginx:alpine`, visit it in your browser on port 8080.
2. **Build a Dockerfile:** Create a simple Express server, Dockerize it, and run it.
3. **Layer caching:** Build an image twice without changing code. Observe "CACHED" in the output. Then change one source file and rebuild — see which layers rebuild.
4. **Inspect a container:** Run a container, use `docker exec -it <id> sh` to explore the filesystem inside it.
5. **Clean up:** List all containers and images, stop everything, remove everything. (`docker system prune`)

#### Level 1 success criteria

- [ ] Can build an image from a Dockerfile.
- [ ] Can run a container with port mapping.
- [ ] Can explain the difference between image and container.
- [ ] Can use `.dockerignore` and explain why layer order matters.

---

### Level 2 — Junior

**Goal:** Build multi-container applications, use Docker Compose, and optimize images.

#### Multi-stage Dockerfile

Multi-stage builds let you use one stage for building and another for running. This drastically reduces image size.

```dockerfile
# Stage 1: Build
FROM node:20-alpine AS builder

WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci
COPY . .
RUN npm run build

# Stage 2: Production
FROM node:20-alpine AS runner

WORKDIR /app
ENV NODE_ENV=production

# Copy only what's needed from the builder
COPY --from=builder /app/package.json /app/package-lock.json ./
RUN npm ci --omit=dev
COPY --from=builder /app/dist ./dist

EXPOSE 3000
USER node
CMD ["node", "dist/server.js"]
```

**Why multi-stage?**
- Builder stage has devDependencies, source code, build tools — large.
- Runner stage has only production deps and built output — small.
- Final image doesn't contain TypeScript, Webpack, test files, etc.

#### Environment variables

```dockerfile
# In Dockerfile
ENV NODE_ENV=production
ENV PORT=3000

# Override at runtime
docker run -e PORT=8080 -e DATABASE_URL=postgres://... my-app
```

```yaml
# In docker-compose.yml
services:
  api:
    environment:
      - NODE_ENV=production
      - DATABASE_URL=postgres://db:5432/mydb
    env_file:
      - .env
```

#### Volumes

| Type | Syntax | Use case |
|---|---|---|
| **Named volume** | `my-data:/var/lib/postgresql/data` | Database persistence |
| **Bind mount** | `./src:/app/src` | Local development — code syncing |
| **tmpfs** | `tmpfs: /tmp` | Temporary data that shouldn't persist |

```yaml
# docker-compose.yml
services:
  db:
    image: postgres:16-alpine
    volumes:
      - pgdata:/var/lib/postgresql/data    # Named volume — persists
    environment:
      POSTGRES_PASSWORD: secret

volumes:
  pgdata:    # Declare the named volume
```

#### Networks

Docker Compose creates a default network for all services. Services can reach each other by name.

```yaml
services:
  web:
    build: ./frontend
    ports:
      - "3000:3000"
    depends_on:
      - api

  api:
    build: ./backend
    ports:
      - "4000:4000"
    environment:
      DATABASE_URL: postgres://db:5432/mydb    # ← "db" is the service name
    depends_on:
      - db

  db:
    image: postgres:16-alpine
    environment:
      POSTGRES_PASSWORD: secret
```

**Key insight:** Inside the Docker network, `db` resolves to the PostgreSQL container's IP. You never use `localhost` to reach another container — you use the service name.

#### Docker Compose basics

```yaml
# docker-compose.yml
services:
  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    ports:
      - "3000:3000"
    volumes:
      - ./frontend/src:/app/src    # Hot reload
    environment:
      - NEXT_PUBLIC_API_URL=http://localhost:4000

  api:
    build: ./api
    ports:
      - "4000:4000"
    environment:
      - DATABASE_URL=postgres://postgres:secret@db:5432/mydb
    depends_on:
      db:
        condition: service_healthy

  db:
    image: postgres:16-alpine
    ports:
      - "5432:5432"
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: secret
      POSTGRES_DB: mydb
    volumes:
      - pgdata:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 5s
      timeout: 5s
      retries: 5

volumes:
  pgdata:
```

**Commands:**

```bash
# Start all services
docker compose up

# Start in background
docker compose up -d

# Rebuild images and start
docker compose up --build

# Stop all services
docker compose down

# Stop and remove volumes (careful — deletes data!)
docker compose down -v

# View logs
docker compose logs -f api

# Run a one-off command
docker compose exec api sh

# Restart a single service
docker compose restart api
```

#### Debugging containers

```bash
# View logs
docker compose logs -f <service>

# Shell into a running container
docker compose exec <service> sh

# Inspect a container
docker inspect <container-id>

# Check resource usage
docker stats

# View networks
docker network ls
docker network inspect <network>

# Check if a port is actually exposed
docker port <container-id>
```

#### Optimizing image size

| Technique | Impact | Example |
|---|---|---|
| Use alpine base | ~900MB → ~180MB | `FROM node:20-alpine` |
| Multi-stage builds | Remove build tools from final image | See multi-stage example above |
| `.dockerignore` | Exclude unnecessary files from build context | See .dockerignore section |
| `npm ci --omit=dev` | Skip devDependencies in production | `RUN npm ci --omit=dev` |
| Minimize layers | Fewer layers = smaller image | Combine RUN commands with `&&` |
| Use specific tags | Avoid pulling unexpected updates | `node:20.11-alpine` not `node:latest` |

#### 5 mini project ideas

1. **React + Express + PostgreSQL:** Full-stack app with Docker Compose. Frontend proxies to API, API talks to DB.
2. **Next.js with hot reload:** Development Compose file with bind mounts for instant feedback.
3. **Multi-stage React build:** Build React app, serve with Nginx in a tiny production image.
4. **API with Redis cache:** Express API + Redis container, cached responses.
5. **Database migration workflow:** Run migrations as a one-off command in Compose before starting the app.

#### Common mistakes and anti-patterns

| Anti-pattern | Why it's bad | Better approach |
|---|---|---|
| One giant container for everything | Hard to scale, debug, and update | One process per container |
| Not using multi-stage builds | Images are 1GB+ with dev tools | Separate build and runtime stages |
| Bind-mounting `node_modules` | Overwrites container's `node_modules` with host's (OS mismatch) | Use anonymous volume: `- /app/node_modules` |
| Hardcoding secrets in Dockerfile | Secrets baked into image layers permanently | Use env vars or secrets at runtime |
| Using `latest` tag | Non-reproducible — image changes silently | Pin to specific version tags |
| No `.dockerignore` | Slow builds, bloated context, accidental secret inclusion | Always create `.dockerignore` |
| `depends_on` without health check | Service starts before dependency is ready | Use `condition: service_healthy` |
| Storing data inside containers | Data lost on container removal | Use volumes for persistence |

#### Level 2 success criteria

- [ ] Can write a multi-stage Dockerfile.
- [ ] Can use Docker Compose to run frontend + API + DB.
- [ ] Can explain volumes, networks, and environment variables.
- [ ] Can debug a container that isn't working.

---

### Level 3 — Senior

**Goal:** Build production-ready Docker setups — secure, optimized, observable, and integrated with CI/CD.

#### Production Dockerfile strategy

```dockerfile
# ============================================
# Production Dockerfile for Next.js
# ============================================

# Stage 1: Dependencies
FROM node:20-alpine AS deps
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci

# Stage 2: Build
FROM node:20-alpine AS builder
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .
ENV NEXT_TELEMETRY_DISABLED=1
RUN npm run build

# Stage 3: Production runtime
FROM node:20-alpine AS runner
WORKDIR /app

ENV NODE_ENV=production
ENV NEXT_TELEMETRY_DISABLED=1

# Create non-root user
RUN addgroup --system --gid 1001 nodejs && \
    adduser --system --uid 1001 nextjs

# Copy only production artifacts
COPY --from=builder /app/public ./public
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static

USER nextjs

EXPOSE 3000
ENV PORT=3000
ENV HOSTNAME="0.0.0.0"

HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD wget --no-verbose --tries=1 --spider http://localhost:3000/api/health || exit 1

CMD ["node", "server.js"]
```

**Next.js `standalone` output** requires `output: 'standalone'` in `next.config.js`. This produces a minimal server without `node_modules` — image size drops dramatically.

#### Security hardening

| Practice | Why | How |
|---|---|---|
| Non-root user | Prevent container escape escalation | `USER node` or create a custom user |
| Read-only filesystem | Prevent runtime modification | `read_only: true` in Compose |
| No secrets in image | Secrets persist in layers forever | Use runtime env vars or Docker secrets |
| Minimal base image | Fewer packages = fewer vulnerabilities | Use `alpine` or `distroless` |
| Pin image digests | Prevent supply chain attacks | `FROM node:20-alpine@sha256:abc123...` |
| Scan images | Detect known CVEs | `docker scout`, `trivy`, `snyk container` |
| Drop capabilities | Reduce kernel surface | `cap_drop: [ALL]` in Compose |
| No package managers in production | Prevent installing malware at runtime | Remove `apk`/`apt` in final stage or use distroless |

```yaml
# Security-hardened Compose service
services:
  api:
    build: .
    read_only: true
    tmpfs:
      - /tmp
    cap_drop:
      - ALL
    security_opt:
      - no-new-privileges:true
    user: "1001:1001"
```

#### Build cache optimization

Layer order matters enormously:

```dockerfile
# ❌ BAD: Any source change invalidates npm ci cache
COPY . .
RUN npm ci

# ✅ GOOD: npm ci only reruns when package files change
COPY package.json package-lock.json ./
RUN npm ci
COPY . .
```

**Advanced: BuildKit cache mounts:**

```dockerfile
# syntax=docker/dockerfile:1
FROM node:20-alpine
WORKDIR /app
COPY package.json package-lock.json ./
RUN --mount=type=cache,target=/root/.npm npm ci
COPY . .
RUN npm run build
```

This keeps the npm cache across builds even when the layer is invalidated.

#### Docker Compose for production-like environments

```yaml
# docker-compose.prod.yml
services:
  web:
    build:
      context: .
      dockerfile: Dockerfile
      target: runner
    ports:
      - "3000:3000"
    environment:
      - NODE_ENV=production
    restart: unless-stopped
    deploy:
      resources:
        limits:
          cpus: '1.0'
          memory: 512M
    healthcheck:
      test: ["CMD", "wget", "--spider", "-q", "http://localhost:3000/api/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 10s
    logging:
      driver: json-file
      options:
        max-size: "10m"
        max-file: "3"
```

#### Monorepo Docker strategy

```text
monorepo/
├── apps/
│   ├── web/
│   │   └── Dockerfile
│   └── api/
│       └── Dockerfile
├── packages/
│   ├── ui/
│   └── shared/
├── package.json
├── pnpm-lock.yaml
├── pnpm-workspace.yaml
└── docker-compose.yml
```

```dockerfile
# apps/web/Dockerfile (monorepo-aware)
FROM node:20-alpine AS builder
WORKDIR /app

# Install pnpm
RUN corepack enable && corepack prepare pnpm@9 --activate

# Copy workspace config
COPY pnpm-lock.yaml pnpm-workspace.yaml package.json ./
COPY apps/web/package.json ./apps/web/
COPY packages/ui/package.json ./packages/ui/
COPY packages/shared/package.json ./packages/shared/

# Install all workspace dependencies
RUN pnpm install --frozen-lockfile

# Copy source
COPY apps/web ./apps/web
COPY packages/ui ./packages/ui
COPY packages/shared ./packages/shared

# Build
RUN pnpm --filter web build

# Production stage
FROM node:20-alpine AS runner
WORKDIR /app
COPY --from=builder /app/apps/web/.next/standalone ./
COPY --from=builder /app/apps/web/.next/static ./.next/static
COPY --from=builder /app/apps/web/public ./public

USER node
EXPOSE 3000
CMD ["node", "server.js"]
```

#### CI/CD integration

```yaml
# GitHub Actions: Build and push Docker image
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
          tags: |
            ghcr.io/${{ github.repository }}:${{ github.sha }}
            ghcr.io/${{ github.repository }}:latest
          cache-from: type=gha
          cache-to: type=gha,mode=max
```

#### Health checks

```dockerfile
# In Dockerfile
HEALTHCHECK --interval=30s --timeout=3s --start-period=10s --retries=3 \
  CMD wget --no-verbose --tries=1 --spider http://localhost:3000/api/health || exit 1
```

```yaml
# In docker-compose.yml
services:
  api:
    healthcheck:
      test: ["CMD-SHELL", "curl -f http://localhost:4000/health || exit 1"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 15s

  db:
    image: postgres:16-alpine
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 5s
      timeout: 5s
      retries: 5
```

#### Logging and observability

```yaml
services:
  api:
    logging:
      driver: json-file
      options:
        max-size: "10m"     # Rotate at 10MB
        max-file: "3"       # Keep 3 files

    # Alternatively, use a logging driver for centralized logging
    # logging:
    #   driver: fluentd
    #   options:
    #     fluentd-address: localhost:24224
```

**Structured logging inside your app** is critical:

```typescript
// Use JSON logging in production
console.log(JSON.stringify({
  level: 'info',
  message: 'Request handled',
  method: 'GET',
  path: '/api/users',
  duration_ms: 42,
  timestamp: new Date().toISOString(),
}));
```

#### Secret management

| Method | Security level | Use case |
|---|---|---|
| Environment variables | Low-Medium | Non-sensitive config, development |
| `.env` file | Low | Local development only |
| Docker secrets (Compose) | Medium | Production Compose deployments |
| External secrets manager | High | Production (Vault, AWS Secrets Manager) |

```yaml
# Docker Compose secrets
services:
  api:
    secrets:
      - db_password
    environment:
      DB_PASSWORD_FILE: /run/secrets/db_password

secrets:
  db_password:
    file: ./secrets/db_password.txt    # Development
    # external: true                   # Production (pre-created)
```

#### Reverse proxy with Nginx / Traefik

```yaml
# Nginx reverse proxy
services:
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
      - ./certs:/etc/nginx/certs:ro
    depends_on:
      - web
      - api

  web:
    build: ./frontend
    expose:
      - "3000"      # Not published to host — only accessible via nginx

  api:
    build: ./backend
    expose:
      - "4000"
```

```nginx
# nginx/nginx.conf
events {}

http {
    upstream frontend {
        server web:3000;
    }

    upstream backend {
        server api:4000;
    }

    server {
        listen 80;

        location / {
            proxy_pass http://frontend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
        }

        location /api/ {
            proxy_pass http://backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
        }
    }
}
```

**Traefik alternative** (auto-discovers services via labels):

```yaml
services:
  traefik:
    image: traefik:v3.0
    command:
      - "--providers.docker=true"
      - "--entrypoints.web.address=:80"
    ports:
      - "80:80"
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock:ro

  web:
    build: ./frontend
    labels:
      - "traefik.http.routers.web.rule=Host(`myapp.localhost`)"
      - "traefik.http.services.web.loadbalancer.server.port=3000"
```

#### 5 production-grade project examples

1. **Next.js SSR + PostgreSQL + Redis:** Three-stage Dockerfile for Next.js standalone, health checks, volume persistence, Nginx reverse proxy.
2. **Monorepo with pnpm:** Workspace-aware Dockerfiles for multiple apps sharing packages, CI/CD pipeline building only changed services.
3. **Full-stack with background workers:** Web app + API + database + worker service for async jobs (e.g., email sending, image processing).
4. **Multi-environment Compose:** `docker-compose.yml` (base) + `docker-compose.dev.yml` (overrides for local dev) + `docker-compose.prod.yml` (production settings).
5. **Automated image pipeline:** GitHub Actions builds, scans for vulnerabilities, pushes to GHCR, deploys to a VPS with docker compose pull + up.

#### Level 3 success criteria

- [ ] Can write a production-grade multi-stage Dockerfile.
- [ ] Can harden an image (non-root user, minimal base, no secrets in layers).
- [ ] Can set up a reverse proxy with Nginx or Traefik.
- [ ] Can integrate Docker builds into CI/CD.
- [ ] Can explain health checks, logging, and secret management.

---

### Level 4 — Expert

**Goal:** Design container strategy at platform scale — reusable base images, orchestration decisions, supply chain security, multi-architecture, disaster recovery.

#### Designing reusable base images

Create organization-wide base images that embed your standards:

```dockerfile
# base-images/node-base/Dockerfile
FROM node:20-alpine

# Security: non-root user
RUN addgroup --system --gid 1001 appgroup && \
    adduser --system --uid 1001 appuser

# Standard tools
RUN apk add --no-cache tini wget

# Healthcheck utility
COPY healthcheck.sh /usr/local/bin/healthcheck
RUN chmod +x /usr/local/bin/healthcheck

# Use tini as init system (proper signal handling)
ENTRYPOINT ["/sbin/tini", "--"]

USER appuser
WORKDIR /app
```

Teams then use:

```dockerfile
FROM ghcr.io/my-org/node-base:20-1.0.0

COPY --chown=appuser:appgroup package.json package-lock.json ./
RUN npm ci --omit=dev
COPY --chown=appuser:appgroup . .
CMD ["node", "server.js"]
```

**Benefits:**
- Consistent security posture across all services.
- Centralized patching — update the base image, all child images inherit fixes.
- Reduced Dockerfile boilerplate.

#### Docker vs. Kubernetes — decision strategy

| Dimension | Docker Compose | Kubernetes |
|---|---|---|
| Complexity | Low | High |
| Learning curve | Days | Weeks to months |
| Best for | Single host, small teams, dev environments | Multi-host, auto-scaling, large teams |
| Scaling | Manual (add replicas) | Automatic (HPA) |
| Networking | Simple service discovery | Complex but powerful (ingress, service mesh) |
| State management | Volumes on one host | Persistent Volume Claims across nodes |
| CI/CD | Simple (compose up) | Complex (Helm, ArgoCD, etc.) |
| When to use | < 10 services, < 5 nodes, < 20 engineers | > 10 services, multi-node, auto-scaling needed |

**Rule of thumb:** Start with Docker Compose. Move to Kubernetes when you need multi-node scaling, auto-healing, or complex service mesh. Many production workloads never need Kubernetes.

#### Image lifecycle management

```text
Build → Tag → Scan → Push → Deploy → Monitor → Rotate

Tag strategy:
  - git SHA: myapp:abc1234 (immutable, traceable)
  - semver: myapp:1.2.3 (release versions)
  - latest: myapp:latest (convenience, mutable — avoid in production)
  - branch: myapp:main (for staging, mutable)
```

**Retention policy:** Delete images older than N days, keep last N tagged releases. Use registry garbage collection.

#### Supply chain security

| Threat | Mitigation |
|---|---|
| Compromised base image | Pin to digest, scan regularly, use official images |
| Malicious layer injection | Verify image provenance, sign images with `cosign` |
| Secrets in image layers | Never `COPY .env`, use runtime secrets |
| Unpatched vulnerabilities | Automate scanning in CI, rebuild on base image updates |
| Untrusted registries | Pull only from approved registries |

```bash
# Scan an image for vulnerabilities
docker scout cves myapp:latest

# Sign an image
cosign sign ghcr.io/my-org/myapp:1.0.0

# Verify a signature
cosign verify ghcr.io/my-org/myapp:1.0.0
```

#### Multi-architecture builds

```bash
# Build for multiple architectures
docker buildx build \
  --platform linux/amd64,linux/arm64 \
  --tag ghcr.io/my-org/myapp:1.0.0 \
  --push .
```

This is essential for teams with mixed hardware (Intel Macs, Apple Silicon, ARM servers like AWS Graviton).

#### Advanced networking

```yaml
services:
  web:
    networks:
      - frontend

  api:
    networks:
      - frontend
      - backend

  db:
    networks:
      - backend    # ← web cannot reach db directly

networks:
  frontend:
  backend:
```

**Network segmentation:** The frontend can reach the API, the API can reach the database, but the frontend cannot reach the database directly. This is defense in depth.

#### Disaster recovery and rollback

| Scenario | Recovery strategy |
|---|---|
| Bad image deployed | Redeploy previous image tag |
| Database corruption | Restore from volume backup |
| Registry outage | Keep local image cache, mirror critical images |
| Secret compromise | Rotate secrets, redeploy all affected services |
| Host failure | Run on multiple hosts, use orchestration |

**Rollback pattern:**

```bash
# Rollback to previous version
docker compose pull        # gets latest tags
# OR specify the old version:
IMAGE_TAG=1.2.2 docker compose up -d

# Verify health
docker compose ps
docker compose logs --tail 50 api
```

#### Architecture review checklist

- [ ] Is each service in its own container?
- [ ] Are images built with multi-stage Dockerfiles?
- [ ] Are images scanned for vulnerabilities?
- [ ] Are containers running as non-root?
- [ ] Is the filesystem read-only where possible?
- [ ] Are health checks defined for all services?
- [ ] Are logs structured and rotated?
- [ ] Are secrets managed properly (not in images)?
- [ ] Is data persistence handled with named volumes?
- [ ] Are networks segmented appropriately?
- [ ] Is there a rollback strategy?
- [ ] Are images tagged immutably (SHA or semver)?
- [ ] Are base images pinned and regularly updated?
- [ ] Is `.dockerignore` comprehensive?
- [ ] Are resource limits set?

#### What expert engineers worry about that juniors miss

| Expert concern | Junior blind spot |
|---|---|
| Image provenance and signing | "I just pull from Docker Hub" |
| Layer cache invalidation in CI | "Why is the CI build so slow?" |
| Container resource limits | "It works on my machine (with 32GB RAM)" |
| Log rotation and storage | Logs fill disk, container crashes |
| Init system (tini/dumb-init) | Zombie processes, signal handling bugs |
| DNS caching in containers | Stale DNS when a service restarts |
| `node_modules` platform mismatch | macOS bind mount + Linux container = broken native deps |
| Graceful shutdown | App doesn't handle SIGTERM, connections drop |
| Image size drift | Image grows from 200MB to 2GB over months |
| Volume backup strategy | "We'll deal with backups later" |

#### 10 advanced engineering discussion topics

1. **Init systems:** Why should every container use `tini` or `dumb-init`? What happens to orphan processes without one?
2. **Distroless images:** When should you use Google's distroless images vs. Alpine? What do you lose?
3. **BuildKit secrets:** How do you safely use secrets during build time (e.g., private npm registry tokens) without them persisting in layers?
4. **Container-native CI:** Should your CI run inside containers, or should it build containers? What are the trade-offs?
5. **Sidecar pattern:** When should you run a helper process in the same container vs. a separate sidecar container?
6. **Image promotion:** Design a pipeline where an image is built once and promoted through dev → staging → production without rebuilding.
7. **Docker socket security:** Why is mounting `/var/run/docker.sock` dangerous? When is it acceptable?
8. **Rootless Docker:** What is rootless mode, and when should you use it?
9. **Container density:** How many containers can you run on a single host before performance degrades? What are the limiting factors?
10. **Migration from Compose to Kubernetes:** What signals indicate it's time to migrate? What does the migration path look like?

---

## 3. Setup Guide

### Step 1: Install Docker and Docker Compose

**macOS:**
```bash
# Install Docker Desktop (includes Docker Engine + Compose)
brew install --cask docker
# OR download from https://docker.com/products/docker-desktop
```

**Linux (Ubuntu/Debian):**
```bash
# Install Docker Engine
curl -fsSL https://get.docker.com | sh

# Add your user to the docker group (log out/in after)
sudo usermod -aG docker $USER

# Docker Compose v2 is included as a plugin
docker compose version
```

**Verify:**
```bash
docker --version          # Docker version 27.x
docker compose version    # Docker Compose version v2.x
docker run hello-world    # Should print a success message
```

### Step 2: Recommended folder structure

#### Small project (single app)

```text
my-app/
├── Dockerfile
├── .dockerignore
├── docker-compose.yml
├── docker-compose.dev.yml       # Development overrides
├── .env.example
├── src/
├── public/
├── package.json
└── package-lock.json
```

#### Medium project (frontend + backend)

```text
my-project/
├── docker-compose.yml
├── docker-compose.dev.yml
├── .env.example
├── frontend/
│   ├── Dockerfile
│   ├── .dockerignore
│   ├── src/
│   ├── package.json
│   └── ...
├── backend/
│   ├── Dockerfile
│   ├── .dockerignore
│   ├── src/
│   ├── package.json
│   └── ...
└── nginx/
    └── nginx.conf
```

#### Large project (monorepo)

```text
monorepo/
├── docker-compose.yml
├── docker-compose.dev.yml
├── docker-compose.prod.yml
├── .env.example
├── apps/
│   ├── web/
│   │   ├── Dockerfile
│   │   └── ...
│   ├── api/
│   │   ├── Dockerfile
│   │   └── ...
│   └── worker/
│       ├── Dockerfile
│       └── ...
├── packages/
│   ├── shared/
│   └── ui/
├── infra/
│   ├── nginx/
│   │   └── nginx.conf
│   └── postgres/
│       └── init.sql
├── package.json
└── pnpm-lock.yaml
```

### Step 3: Example Dockerfiles

#### React app (Vite) — production

```dockerfile
# Stage 1: Build
FROM node:20-alpine AS builder
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci
COPY . .
RUN npm run build

# Stage 2: Serve with Nginx
FROM nginx:alpine AS runner
COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

```nginx
# nginx.conf for SPA
server {
    listen 80;
    root /usr/share/nginx/html;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }

    location /assets {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
```

**Image size comparison:**

| Approach | Image size |
|---|---|
| `node:20` + serve | ~1.1 GB |
| `node:20-alpine` + serve | ~190 MB |
| Multi-stage + Nginx | ~25 MB |

#### Next.js app — production

```dockerfile
FROM node:20-alpine AS deps
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci

FROM node:20-alpine AS builder
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .
ENV NEXT_TELEMETRY_DISABLED=1
RUN npm run build

FROM node:20-alpine AS runner
WORKDIR /app
ENV NODE_ENV=production
ENV NEXT_TELEMETRY_DISABLED=1

RUN addgroup --system --gid 1001 nodejs && \
    adduser --system --uid 1001 nextjs

COPY --from=builder /app/public ./public
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static

USER nextjs
EXPOSE 3000
ENV PORT=3000
ENV HOSTNAME="0.0.0.0"
CMD ["node", "server.js"]
```

**Requires in `next.config.js`:**

```js
/** @type {import('next').NextConfig} */
const nextConfig = {
  output: 'standalone',
};
module.exports = nextConfig;
```

#### Astro app — production (static)

```dockerfile
FROM node:20-alpine AS builder
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM nginx:alpine AS runner
COPY --from=builder /app/dist /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

#### Node.js API — production

```dockerfile
FROM node:20-alpine AS builder
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM node:20-alpine AS runner
WORKDIR /app
ENV NODE_ENV=production

RUN addgroup --system --gid 1001 appgroup && \
    adduser --system --uid 1001 appuser

COPY --from=builder --chown=appuser:appgroup /app/package.json /app/package-lock.json ./
RUN npm ci --omit=dev
COPY --from=builder --chown=appuser:appgroup /app/dist ./dist

USER appuser
EXPOSE 4000

HEALTHCHECK --interval=30s --timeout=3s --retries=3 \
  CMD wget --no-verbose --tries=1 --spider http://localhost:4000/health || exit 1

CMD ["node", "dist/server.js"]
```

### Step 4: Example docker-compose.yml files

#### Frontend + Backend

```yaml
services:
  frontend:
    build: ./frontend
    ports:
      - "3000:80"
    depends_on:
      - api

  api:
    build: ./backend
    ports:
      - "4000:4000"
    environment:
      - NODE_ENV=production
```

#### Frontend + Backend + Database

```yaml
services:
  frontend:
    build: ./frontend
    ports:
      - "3000:80"
    depends_on:
      - api

  api:
    build: ./backend
    ports:
      - "4000:4000"
    environment:
      - DATABASE_URL=postgres://postgres:secret@db:5432/mydb
      - NODE_ENV=production
    depends_on:
      db:
        condition: service_healthy

  db:
    image: postgres:16-alpine
    ports:
      - "5432:5432"
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: secret
      POSTGRES_DB: mydb
    volumes:
      - pgdata:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 5s
      timeout: 5s
      retries: 5

volumes:
  pgdata:
```

#### Next.js + PostgreSQL + Redis

```yaml
services:
  web:
    build: .
    ports:
      - "3000:3000"
    environment:
      - DATABASE_URL=postgres://postgres:secret@db:5432/mydb
      - REDIS_URL=redis://redis:6379
      - NODE_ENV=production
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_healthy

  db:
    image: postgres:16-alpine
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: secret
      POSTGRES_DB: mydb
    volumes:
      - pgdata:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 5s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    volumes:
      - redisdata:/data
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 5s
      timeout: 5s
      retries: 5

volumes:
  pgdata:
  redisdata:
```

### Step 5: Development vs. production strategy

Use Compose overrides:

```yaml
# docker-compose.yml (base — shared config)
services:
  web:
    build: .
    ports:
      - "3000:3000"
    depends_on:
      - db

  db:
    image: postgres:16-alpine
    environment:
      POSTGRES_PASSWORD: secret
    volumes:
      - pgdata:/var/lib/postgresql/data

volumes:
  pgdata:
```

```yaml
# docker-compose.dev.yml (development overrides)
services:
  web:
    build:
      target: deps       # Use early stage with all deps
    volumes:
      - ./src:/app/src   # Hot reload via bind mount
      - /app/node_modules  # Anonymous volume — don't overwrite
    environment:
      - NODE_ENV=development
    command: npm run dev

  db:
    ports:
      - "5432:5432"      # Expose DB port for local tools
```

```yaml
# docker-compose.prod.yml (production overrides)
services:
  web:
    build:
      target: runner     # Use final minimal stage
    environment:
      - NODE_ENV=production
    restart: unless-stopped
    deploy:
      resources:
        limits:
          cpus: '1.0'
          memory: 512M
```

**Usage:**

```bash
# Development
docker compose -f docker-compose.yml -f docker-compose.dev.yml up

# Production
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

### Step 6: .dockerignore

```text
# Dependencies
node_modules
.pnpm-store

# Build output
dist
.next
out
build

# Git
.git
.gitignore

# Docker
Dockerfile*
docker-compose*
.dockerignore

# IDE
.vscode
.idea
*.swp
*.swo

# Environment
.env
.env.local
.env*.local

# Tests (if not needed in image)
__tests__
*.test.ts
*.spec.ts
coverage
jest.config.*

# Misc
README.md
LICENSE
*.md
```

### Step 7: Common scripts in package.json

```json
{
  "scripts": {
    "docker:dev": "docker compose -f docker-compose.yml -f docker-compose.dev.yml up",
    "docker:dev:build": "docker compose -f docker-compose.yml -f docker-compose.dev.yml up --build",
    "docker:prod": "docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d",
    "docker:down": "docker compose down",
    "docker:clean": "docker compose down -v --rmi local",
    "docker:logs": "docker compose logs -f",
    "docker:shell": "docker compose exec web sh",
    "docker:db:shell": "docker compose exec db psql -U postgres"
  }
}
```

---

## 4. Cheatsheet

### Docker commands

| Command | Purpose |
|---|---|
| `docker build -t name .` | Build image from Dockerfile |
| `docker build -t name --target stage .` | Build specific stage |
| `docker run -p 3000:3000 name` | Run container with port mapping |
| `docker run -d name` | Run in background (detached) |
| `docker run -it name sh` | Run interactive shell |
| `docker run -v $(pwd):/app name` | Run with bind mount |
| `docker run -e KEY=val name` | Run with environment variable |
| `docker run --rm name` | Remove container after exit |
| `docker ps` | List running containers |
| `docker ps -a` | List all containers |
| `docker stop <id>` | Stop container |
| `docker rm <id>` | Remove container |
| `docker images` | List images |
| `docker rmi <id>` | Remove image |
| `docker logs <id>` | View container logs |
| `docker logs -f <id>` | Follow logs (tail) |
| `docker exec -it <id> sh` | Shell into running container |
| `docker inspect <id>` | Detailed container info |
| `docker stats` | Live resource usage |
| `docker system prune` | Remove unused data |
| `docker system prune -a` | Remove all unused images too |
| `docker system df` | Show disk usage |

### Docker Compose commands

| Command | Purpose |
|---|---|
| `docker compose up` | Start all services |
| `docker compose up -d` | Start in background |
| `docker compose up --build` | Rebuild images then start |
| `docker compose down` | Stop and remove |
| `docker compose down -v` | Also remove volumes |
| `docker compose ps` | List services |
| `docker compose logs -f` | Follow all logs |
| `docker compose logs -f api` | Follow specific service |
| `docker compose exec api sh` | Shell into service |
| `docker compose run api npm test` | Run one-off command |
| `docker compose restart api` | Restart a service |
| `docker compose pull` | Pull latest images |
| `docker compose build` | Build all images |
| `docker compose config` | Validate and display config |
| `docker compose top` | Show running processes |

### Dockerfile syntax

| Instruction | Purpose | Example |
|---|---|---|
| `FROM` | Base image | `FROM node:20-alpine` |
| `WORKDIR` | Set working directory | `WORKDIR /app` |
| `COPY` | Copy files from context | `COPY package.json ./` |
| `RUN` | Execute a command during build | `RUN npm ci` |
| `ENV` | Set environment variable | `ENV NODE_ENV=production` |
| `ARG` | Build-time variable | `ARG NODE_VERSION=20` |
| `EXPOSE` | Document the port | `EXPOSE 3000` |
| `CMD` | Default command when container starts | `CMD ["node", "server.js"]` |
| `ENTRYPOINT` | Main executable (harder to override) | `ENTRYPOINT ["/sbin/tini", "--"]` |
| `USER` | Set the user | `USER node` |
| `HEALTHCHECK` | Define health check | See health check section |
| `LABEL` | Add metadata | `LABEL version="1.0"` |

### Compose syntax

```yaml
services:
  name:
    image: image:tag             # Use existing image
    build:                        # OR build from Dockerfile
      context: .
      dockerfile: Dockerfile
      target: stage              # Multi-stage target
      args:
        NODE_VERSION: 20
    ports:
      - "host:container"
    expose:
      - "3000"                   # Internal only
    volumes:
      - ./src:/app/src           # Bind mount
      - data:/app/data           # Named volume
      - /app/node_modules        # Anonymous volume
    environment:
      KEY: value
    env_file:
      - .env
    depends_on:
      db:
        condition: service_healthy
    restart: unless-stopped       # Restart policy
    command: npm run dev          # Override CMD
    working_dir: /app
    user: "1001:1001"
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:3000"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 10s
    deploy:
      resources:
        limits:
          cpus: '1.0'
          memory: 512M
    networks:
      - frontend
    logging:
      driver: json-file
      options:
        max-size: "10m"
        max-file: "3"

volumes:
  data:

networks:
  frontend:
```

### Environment variable patterns

```yaml
# Inline
environment:
  - NODE_ENV=production
  - DATABASE_URL=postgres://db:5432/mydb

# Map syntax
environment:
  NODE_ENV: production
  DATABASE_URL: postgres://db:5432/mydb

# From file
env_file:
  - .env
  - .env.production

# Build args
build:
  args:
    NODE_VERSION: 20
```

### Volume patterns

```yaml
volumes:
  # Named volume (persistent, Docker-managed)
  - pgdata:/var/lib/postgresql/data

  # Bind mount (host directory)
  - ./src:/app/src

  # Bind mount read-only
  - ./config:/app/config:ro

  # Anonymous volume (prevent overwrite from bind mount)
  - /app/node_modules

  # tmpfs (in-memory, not persistent)
  # tmpfs:
  #   - /tmp
```

### Network patterns

```yaml
# Default — all services on one network
# (automatic, no config needed)

# Custom networks for isolation
services:
  web:
    networks: [frontend]
  api:
    networks: [frontend, backend]
  db:
    networks: [backend]

networks:
  frontend:
  backend:
```

### Debugging commands

```bash
# Why won't my container start?
docker compose logs <service>

# What's inside the container?
docker compose exec <service> sh
docker compose exec <service> ls -la /app

# Is the port actually open?
docker compose exec <service> wget -qO- http://localhost:3000

# What environment variables are set?
docker compose exec <service> env

# Check container health
docker inspect --format='{{.State.Health.Status}}' <container-id>

# Check network connectivity
docker compose exec api ping db

# See what's using disk space
docker system df
docker system df -v
```

### Common error messages

| Error | Cause | Fix |
|---|---|---|
| `port is already allocated` | Another process uses the port | Change the host port or stop the conflicting process |
| `no space left on device` | Docker disk full | `docker system prune -a` |
| `COPY failed: file not found` | File not in build context | Check path relative to Dockerfile, check `.dockerignore` |
| `npm ERR! could not determine executable` | Wrong `WORKDIR` or missing deps | Verify `WORKDIR` and that `npm ci` ran |
| `ECONNREFUSED localhost` | Container trying to reach another via localhost | Use the service name instead (`db`, `api`, etc.) |
| `permission denied` | Non-root user can't access files | `chown` in Dockerfile or adjust permissions |
| `exec format error` | Image built for wrong architecture | Rebuild for the correct platform |
| `OCI runtime create failed` | Corrupt image or incompatible base | Rebuild the image, check base image |

### Performance tips

| Tip | Impact |
|---|---|
| Order Dockerfile layers by change frequency | Maximize cache hits |
| Use `.dockerignore` | Smaller build context, faster builds |
| Use multi-stage builds | Smaller production images |
| Use Alpine base images | ~900MB → ~180MB |
| Use BuildKit (`DOCKER_BUILDKIT=1`) | Parallel stage building, cache mounts |
| Combine `RUN` commands | Fewer layers |
| Use `npm ci --omit=dev` | Exclude devDependencies |
| Cache mount for npm | Persist npm cache across builds |

### Security tips

| Tip | Priority |
|---|---|
| Run as non-root user | Critical |
| Use minimal base images | High |
| Pin image versions | High |
| Scan images for CVEs | High |
| Never put secrets in Dockerfile | Critical |
| Use `.dockerignore` (exclude `.env`) | High |
| Make filesystem read-only | Medium |
| Drop all capabilities | Medium |
| Use `no-new-privileges` | Medium |
| Set resource limits | Medium |

---

## 5. Real-World Engineering Mindset

### Local development environment

**Problem:** "It takes a new engineer half a day to set up the project."

**Strategies:**

| Strategy | Pros | Cons |
|---|---|---|
| README with manual steps | Simple, no Docker knowledge needed | Fragile, OS-dependent, drift |
| Docker Compose for everything | One command, identical everywhere | Slower feedback loop (build time), Docker knowledge needed |
| Docker for services only (DB, Redis) | Best of both worlds — native Node.js speed + containerized infrastructure | Slightly more setup |
| Nix/devbox for toolchain + Docker for services | Reproducible toolchain + containerized services | Higher learning curve |

**Senior choice:** Docker for infrastructure (database, Redis, message queue), native Node.js for the application. This gives you hot reload speed while ensuring everyone has identical backing services. Use `docker compose up db redis` alongside `npm run dev`.

---

### Sharing the same environment across team members

**Problem:** "It works on my machine but not on yours."

**Strategies:**

| Strategy | Pros | Cons |
|---|---|---|
| Docker Compose for dev | Identical environment, one command | Slower than native for some workflows |
| Docker for infra only | Fast dev loop, consistent services | App-level differences still possible |
| Dev containers (VS Code) | Full IDE + container integration | VS Code-specific, heavier |

**Senior choice:** Commit `docker-compose.dev.yml` to the repo. New engineers run `docker compose -f docker-compose.yml -f docker-compose.dev.yml up` and have a working environment in minutes.

---

### Running React + API + DB together

**Problem:** Frontend needs a backend and database running locally.

```yaml
services:
  frontend:
    build:
      context: ./frontend
      target: deps
    volumes:
      - ./frontend/src:/app/src
      - /app/node_modules
    ports:
      - "3000:3000"
    command: npm run dev
    environment:
      - VITE_API_URL=http://localhost:4000

  api:
    build:
      context: ./backend
      target: deps
    volumes:
      - ./backend/src:/app/src
      - /app/node_modules
    ports:
      - "4000:4000"
    command: npm run dev
    environment:
      - DATABASE_URL=postgres://postgres:secret@db:5432/mydb
    depends_on:
      db:
        condition: service_healthy

  db:
    image: postgres:16-alpine
    ports:
      - "5432:5432"
    environment:
      POSTGRES_PASSWORD: secret
      POSTGRES_DB: mydb
    volumes:
      - pgdata:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 5s
      timeout: 5s
      retries: 5

volumes:
  pgdata:
```

**Key patterns:**
- Bind mount `src/` for hot reload.
- Anonymous volume for `node_modules` to avoid host/container mismatch.
- `depends_on` with health check condition.
- Service names as hostnames (`db`, not `localhost`).

---

### Optimizing frontend image size

**Problem:** Your React image is 1.2 GB.

**Strategies:**

| Technique | Before | After |
|---|---|---|
| Switch from `node` to `node:alpine` | 1.1 GB | 190 MB |
| Multi-stage: build in Node, serve with Nginx | 190 MB | 25 MB |
| Add `.dockerignore` | Slow build, bloated context | Fast build |
| `npm ci --omit=dev` | All deps in image | Only prod deps |

**Senior choice:** Multi-stage build. Build with Node, copy `dist/` into Nginx. Result: ~25 MB image that serves static files with proper caching headers.

---

### Running Next.js SSR in Docker

**Problem:** Next.js needs a Node.js runtime, not just a static file server.

**Strategy:** Use Next.js `standalone` output mode.

```js
// next.config.js
module.exports = { output: 'standalone' };
```

This produces a self-contained `server.js` with bundled dependencies. The Docker image only needs Node.js + this output — no `node_modules` directory.

**Result:** ~120 MB image (vs. 800 MB+ without standalone).

**Hidden pitfall:** Static assets (`.next/static` and `public/`) are NOT included in the standalone output. You must copy them separately in the Dockerfile.

---

### Hot reload in Docker

**Problem:** You change a file, but the app inside Docker doesn't update.

**Strategies:**

| Strategy | Pros | Cons |
|---|---|---|
| Bind mount `src/` | Simple, works with Vite/Next.js | File watching can be slow on macOS |
| Use polling | Works on all OS | CPU overhead |
| Docker for infra only, app runs natively | Best hot reload performance | Less "containerized" |

```yaml
# docker-compose.dev.yml
services:
  web:
    volumes:
      - ./src:/app/src
      - /app/node_modules    # ← prevent host node_modules from overwriting
    environment:
      - WATCHPACK_POLLING=true   # For Next.js on macOS
      - CHOKIDAR_USEPOLLING=true # For Vite/CRA on macOS
    command: npm run dev
```

**Senior choice:** For development, run Node.js natively and only containerize infrastructure. Reserve full containerization for CI and production.

---

### Database persistence

**Problem:** You run `docker compose down` and your database is empty.

**Solution:** Named volumes.

```yaml
services:
  db:
    image: postgres:16-alpine
    volumes:
      - pgdata:/var/lib/postgresql/data

volumes:
  pgdata:
```

**Rules:**
- `docker compose down` — data persists in the volume.
- `docker compose down -v` — **deletes the volume** — data is gone.
- Named volumes survive container recreation.
- Bind mounts to host directories also work but are less portable.

**Backup:**

```bash
# Backup
docker compose exec db pg_dump -U postgres mydb > backup.sql

# Restore
docker compose exec -T db psql -U postgres mydb < backup.sql
```

---

### Reverse proxy setup

**Problem:** Multiple services on one host, need routing by domain or path.

| Solution | Pros | Cons |
|---|---|---|
| Nginx (manual config) | Full control, well understood | Manual config for each service |
| Traefik (auto-discovery) | Automatic via Docker labels | More complex initial setup |
| Caddy (auto-HTTPS) | Simple config, auto TLS | Less ecosystem |

**Senior choice:** Traefik for development and small production. Nginx for high-traffic production where you need fine-grained control.

---

### Background workers

**Problem:** You need async job processing alongside your web app.

```yaml
services:
  web:
    build: .
    command: node dist/server.js
    ports:
      - "3000:3000"

  worker:
    build: .                    # Same image!
    command: node dist/worker.js  # Different entrypoint
    environment:
      - REDIS_URL=redis://redis:6379

  redis:
    image: redis:7-alpine
```

**Key insight:** The web and worker services use the **same image** but different commands. This is a common pattern — build once, run with different entrypoints.

---

### Deploying containers

**Strategies:**

| Strategy | Complexity | Best for |
|---|---|---|
| `docker compose up` on VPS | Low | Small projects, personal apps |
| Docker Swarm | Medium | Small-medium production |
| Kubernetes | High | Large-scale, auto-scaling |
| Cloud container services (ECS, Cloud Run, Fly.io) | Medium | Managed infrastructure |
| Coolify / CapRover | Low-Medium | Self-hosted PaaS |

**Senior choice for a small team:** VPS + Docker Compose + GitHub Actions. Simple, cheap, and sufficient for most apps.

**Deployment script pattern:**

```bash
#!/bin/bash
# deploy.sh — run on the server
cd /opt/myapp
docker compose pull
docker compose up -d --remove-orphans
docker image prune -f
```

---

### CI/CD pipeline with Docker

```yaml
# GitHub Actions
name: Build and Deploy

on:
  push:
    branches: [main]

jobs:
  build:
    runs-on: ubuntu-latest
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

  deploy:
    needs: build
    runs-on: ubuntu-latest
    steps:
      - name: Deploy via SSH
        uses: appleboy/ssh-action@v1
        with:
          host: ${{ secrets.SERVER_HOST }}
          username: deploy
          key: ${{ secrets.SSH_KEY }}
          script: |
            cd /opt/myapp
            export IMAGE_TAG=${{ github.sha }}
            docker compose pull
            docker compose up -d --remove-orphans
```

---

### Monorepo strategy

**Problem:** Multiple apps share packages; you don't want to rebuild everything on every change.

**Strategies:**

| Strategy | Pros | Cons |
|---|---|---|
| One Dockerfile per app, copy workspace | Simple | Large build context |
| Turbo prune + Docker | Only includes needed packages | Turborepo-specific |
| Shared base image + app layers | Reuses common deps | More complex image management |

**Turborepo prune pattern:**

```dockerfile
FROM node:20-alpine AS pruner
WORKDIR /app
RUN npm install -g turbo
COPY . .
RUN turbo prune --scope=web --docker

FROM node:20-alpine AS builder
WORKDIR /app
COPY --from=pruner /app/out/json/ .
COPY --from=pruner /app/out/package-lock.json ./
RUN npm ci
COPY --from=pruner /app/out/full/ .
RUN npx turbo build --filter=web

FROM node:20-alpine AS runner
WORKDIR /app
COPY --from=builder /app/apps/web/.next/standalone ./
COPY --from=builder /app/apps/web/.next/static ./.next/static
COPY --from=builder /app/apps/web/public ./public
CMD ["node", "server.js"]
```

---

### Multi-environment setup

**Problem:** Dev, staging, and production need different configurations.

**Strategy:** Compose file layering.

```bash
# Development
docker compose -f docker-compose.yml -f docker-compose.dev.yml up

# Staging
docker compose -f docker-compose.yml -f docker-compose.staging.yml up -d

# Production
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

Or use `.env` files:

```bash
# .env.staging
IMAGE_TAG=staging
NODE_ENV=staging
DATABASE_URL=postgres://...

# .env.production
IMAGE_TAG=v1.2.3
NODE_ENV=production
DATABASE_URL=postgres://...
```

```bash
docker compose --env-file .env.production up -d
```

---

### Secret management

**Problem:** Database passwords, API keys, tokens — where do they go?

| Method | Security | Use case |
|---|---|---|
| `.env` file | Low | Local development only |
| Environment variables | Medium | Simple production |
| Docker secrets | Medium-High | Docker Swarm / Compose |
| External manager (Vault, AWS SM) | High | Enterprise production |

**Senior choice:** `.env` for local dev (gitignored), environment variables from CI/CD secrets for production, external secrets manager for sensitive production systems.

---

### Scaling containers

**Problem:** One container can't handle the load.

```yaml
services:
  api:
    build: .
    deploy:
      replicas: 3
    expose:
      - "4000"

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
    depends_on:
      - api
```

```bash
# Scale manually
docker compose up -d --scale api=3
```

**For real scaling**, move to Kubernetes, Docker Swarm, or a managed container platform (ECS, Cloud Run, Fly.io).

---

## 6. Brainstorm / Open Questions

### Architecture

1. Should this service live in the same container or a different one?
2. When does a monolith in one container make more sense than microservices?
3. How do you decide which services need their own Dockerfile vs. using off-the-shelf images?
4. Should your development container match your production container exactly?
5. When should you use a sidecar container vs. adding functionality to the main container?
6. How should shared libraries in a monorepo be handled in Docker builds?
7. What is the right boundary between "Docker Compose is enough" and "we need Kubernetes"?

### Scaling

8. How would this architecture change if traffic increased 100×?
9. At what point should you move from `docker compose --scale` to a proper orchestrator?
10. How do you handle database connection pooling when scaling app containers?
11. What is the cost difference between scaling with bigger containers vs. more containers?
12. How do you handle sessions and state when running multiple container instances?
13. What happens when your build takes 15 minutes? How do you reduce it?
14. How many containers can you realistically run on a single VPS?

### Security

15. What data should never be stored inside a container?
16. How do you handle secrets that are needed at build time (e.g., private npm registry tokens)?
17. What happens if a container is compromised — what can the attacker reach?
18. How do you ensure your base images don't have known vulnerabilities?
19. When should you use image signing and verification?
20. How do you prevent a container from accessing other containers' data?
21. What is the risk of running Docker as root on the host?
22. How do you audit what containers are running and what they can access?

### DX / Maintainability

23. Can a new engineer get the project running in under 10 minutes?
24. How do you prevent "Dockerfile rot" — Dockerfiles that gradually become outdated?
25. When should you use a bind mount vs. a volume vs. rebuilding the image?
26. How do you handle `node_modules` platform differences between macOS and Linux?
27. What is the best strategy for hot reload in Docker?
28. How do you keep Docker Compose files DRY across multiple environments?
29. Should Dockerfile and docker-compose.yml live in the app repo or a separate infra repo?
30. How do you debug a container that starts and immediately crashes?

### Cost

31. How much does a container-based VPS deployment cost compared to Vercel?
32. When does the complexity of Docker outweigh its benefits?
33. Is there a project size below which Docker is not worth it?
34. How do you reduce Docker image storage costs in registries?
35. What is the cost of slow Docker builds in developer productivity?

### Reliability

36. What happens when a container runs out of memory?
37. How do you handle database migrations during container deployment?
38. What is your rollback strategy if a new container version is broken?
39. How do you ensure containers restart after a host reboot?
40. What happens if the Docker daemon itself crashes?
41. How do you monitor container health in production?
42. What is the blast radius if your container registry goes down?

### Deployment Strategy

43. When should you use `docker compose` in production vs. a managed container service?
44. How do you handle zero-downtime deployments with Docker Compose?
45. Should you deploy the same image to all environments or build per-environment?
46. How do you handle database schema changes during container updates?
47. What is the right tagging strategy for production images?
48. When should you use rolling updates vs. blue-green deployments?
49. How do you coordinate deployments across multiple dependent services?

---

## 7. Practice Questions

### Beginner (Level 1)

**Q1. True/False:** A Docker image is a running instance of a container.

<details><summary>Answer</summary>False. A Docker <strong>container</strong> is a running instance of an <strong>image</strong>. The image is the blueprint; the container is the running process.</details>

---

**Q2. Single choice:** What does `docker run -p 8080:3000 myapp` do?

- A. Exposes port 3000 on the host
- B. Maps host port 8080 to container port 3000
- C. Maps container port 8080 to host port 3000
- D. Opens port 8080 inside the container

<details><summary>Answer</summary>B. The format is <code>-p HOST:CONTAINER</code>. Host port 8080 is mapped to container port 3000.</details>

---

**Q3. Fill in the blank:** The file that tells Docker which files to exclude from the build context is called `._________`.

<details><summary>Answer</summary><code>dockerignore</code> — The file is <code>.dockerignore</code>.</details>

---

**Q4. Multiple choice:** Which base image will give you the smallest Node.js image?

- A. `node:20`
- B. `node:20-slim`
- C. `node:20-alpine`
- D. `node:20-bookworm`

<details><summary>Answer</summary>C. <code>node:20-alpine</code> is ~180 MB. <code>node:20</code> and <code>node:20-bookworm</code> are ~1.1 GB. <code>node:20-slim</code> is ~250 MB.</details>

---

**Q5. Debugging:** You build a Dockerfile but your app says "Cannot find module 'express'." What is the most likely cause?

<details><summary>Answer</summary>The <code>npm ci</code> or <code>npm install</code> step is missing, or it ran before <code>COPY package.json</code>, or <code>.dockerignore</code> excludes <code>package.json</code> or <code>package-lock.json</code>.</details>

---

**Q6. Single choice:** Why should you `COPY package.json` and `npm ci` BEFORE `COPY . .`?

- A. Docker requires this order
- B. It makes the image smaller
- C. It enables layer caching — dependencies only reinstall when package.json changes
- D. It prevents security issues

<details><summary>Answer</summary>C. Docker caches layers. If <code>package.json</code> hasn't changed, <code>npm ci</code> uses the cached layer. If you <code>COPY . .</code> first, any source code change invalidates the cache for all subsequent layers.</details>

---

**Q7. Matching:** Match the Dockerfile instruction to its purpose.

| Instruction | Purpose |
|---|---|
| A. `FROM` | 1. Run a command during build |
| B. `COPY` | 2. Set the base image |
| C. `RUN` | 3. Default command when container starts |
| D. `CMD` | 4. Add files from build context |

<details><summary>Answer</summary>A→2, B→4, C→1, D→3</details>

---

**Q8. True/False:** `EXPOSE 3000` in a Dockerfile automatically makes the container accessible on port 3000 from the host.

<details><summary>Answer</summary>False. <code>EXPOSE</code> is documentation only. You must use <code>-p 3000:3000</code> when running the container to actually publish the port.</details>

---

**Q9. Scenario:** You run `docker build -t myapp .` and it takes 10 minutes because it reinstalls node_modules every time. Nothing in `package.json` changed. What is wrong?

<details><summary>Answer</summary>The Dockerfile likely has <code>COPY . .</code> before <code>RUN npm ci</code>. Any source code change invalidates the layer cache for the COPY, which invalidates all subsequent layers including <code>npm ci</code>. Fix: copy <code>package.json</code> and lockfile first, run <code>npm ci</code>, then <code>COPY . .</code>.</details>

---

**Q10. Fill in the blank:** To use `npm ci` instead of `npm install` in a Dockerfile, you must have a _________ file committed.

<details><summary>Answer</summary><code>package-lock.json</code> (or equivalent lockfile). <code>npm ci</code> requires a lockfile to perform a deterministic install.</details>

---

### Junior (Level 2)

**Q11. True/False:** A container can access another container on the same Docker Compose network using `localhost`.

<details><summary>Answer</summary>False. Containers on the same Docker network reach each other by <strong>service name</strong>, not <code>localhost</code>. <code>localhost</code> inside a container refers to the container itself.</details>

---

**Q12. Single choice:** What is the purpose of a multi-stage Docker build?

- A. Run multiple containers from one Dockerfile
- B. Build the app in one stage and copy only needed files to a minimal runtime stage
- C. Automatically scale containers
- D. Enable hot reload

<details><summary>Answer</summary>B. Multi-stage builds separate the build environment (with dev tools, source code) from the runtime environment (minimal, production-only files). This dramatically reduces image size.</details>

---

**Q13. Debugging:** Your Docker Compose app's API says "ECONNREFUSED 127.0.0.1:5432" when trying to reach PostgreSQL. PostgreSQL is running. What is wrong?

<details><summary>Answer</summary>The API is trying to connect to <code>localhost</code> (127.0.0.1) instead of the service name. In Docker Compose, containers reach each other by service name. Change the connection string from <code>localhost:5432</code> to <code>db:5432</code> (or whatever the Postgres service name is).</details>

---

**Q14. Matching:** Match the volume type to its use case.

| Type | Use case |
|---|---|
| A. Named volume | 1. Temporary data that shouldn't persist |
| B. Bind mount | 2. Database persistence across restarts |
| C. tmpfs | 3. Syncing source code for hot reload |

<details><summary>Answer</summary>A→2, B→3, C→1</details>

---

**Q15. Fill in the blank:** To prevent the host's `node_modules` from overwriting the container's when using a bind mount, add an _________ volume for `/app/node_modules`.

<details><summary>Answer</summary>Anonymous. Adding <code>- /app/node_modules</code> as a volume (without a host path) creates an anonymous volume that preserves the container's <code>node_modules</code>.</details>

---

**Q16. Scenario:** You add `depends_on: [db]` but your API crashes on startup because the database isn't ready yet. Why?

<details><summary>Answer</summary><code>depends_on</code> only waits for the container to <strong>start</strong>, not for the service inside to be <strong>ready</strong>. PostgreSQL may take seconds to initialize. Use <code>depends_on</code> with <code>condition: service_healthy</code> and define a healthcheck on the database service.</details>

---

**Q17. Multiple choice:** Which of these should be in `.dockerignore`? (Select all)

- A. `node_modules`
- B. `.git`
- C. `.env`
- D. `src/`
- E. `Dockerfile`

<details><summary>Answer</summary>A, B, C, and E. <code>node_modules</code> is rebuilt inside the container. <code>.git</code> is unnecessary and large. <code>.env</code> may contain secrets. <code>Dockerfile</code> isn't needed inside the image. <code>src/</code> is usually needed for the build.</details>

---

**Q18. Single choice:** What does `docker compose down -v` do that `docker compose down` does not?

- A. Removes images
- B. Removes networks
- C. Removes named volumes (deletes persistent data)
- D. Stops containers faster

<details><summary>Answer</summary>C. The <code>-v</code> flag removes named volumes. This deletes persistent data like database contents. Use with caution.</details>

---

**Q19. True/False:** Using the `latest` tag for base images in production Dockerfiles is a best practice.

<details><summary>Answer</summary>False. <code>latest</code> is mutable — it changes when a new version is published. This makes builds non-reproducible. Pin to specific versions like <code>node:20.11-alpine</code>.</details>

---

**Q20. Scenario:** You want to run `npx prisma migrate deploy` once before your API starts, but only in Docker Compose. How would you approach this?

<details><summary>Answer</summary>
Options:<br>
1. Add a <code>migrate</code> service in Compose with <code>command: npx prisma migrate deploy</code> and make the API <code>depends_on</code> the migrate service.<br>
2. Use a startup script that runs migrations then starts the app.<br>
3. Run <code>docker compose run api npx prisma migrate deploy</code> as a separate step before <code>docker compose up</code>.<br>
Option 1 is cleanest for automation.
</details>

---

### Senior / Expert (Level 3–4)

**Q21. Scenario:** Your production Docker image is 2 GB and builds take 15 minutes. What should you investigate first?

<details><summary>Answer</summary>
1. <strong>Base image:</strong> Switch from <code>node:20</code> (1.1 GB) to <code>node:20-alpine</code> (~180 MB).<br>
2. <strong>Multi-stage build:</strong> Are dev dependencies and build tools in the final image?<br>
3. <strong>.dockerignore:</strong> Is <code>node_modules</code>, <code>.git</code>, or test files being copied?<br>
4. <strong>Layer order:</strong> Is <code>npm ci</code> being invalidated on every code change?<br>
5. <strong>BuildKit cache:</strong> Are you using <code>--mount=type=cache</code> for npm?
</details>

---

**Q22. True/False:** Running a container as root inside the container also gives it root access to the host.

<details><summary>Answer</summary>False — by default, container namespaces isolate root inside the container from the host. However, running as root inside the container increases the blast radius if a container escape vulnerability exists. Always use a non-root user for defense in depth.</details>

---

**Q23. Design question:** You have a Next.js app, a Node.js API, a PostgreSQL database, and a Redis cache. Design the Docker networking so the frontend cannot directly access the database.

<details><summary>Answer</summary>
Use two networks:<br>
<code>frontend-net</code>: web + api<br>
<code>backend-net</code>: api + db + redis<br>
The API is on both networks. The web service can reach the API but not the database or Redis directly. This is network segmentation / defense in depth.
</details>

---

**Q24. Single choice:** Your container starts, passes health checks, but users report slow responses. `docker stats` shows the container using 490 MB of a 512 MB memory limit. What is happening?

- A. The container is healthy
- B. The container is likely experiencing memory pressure and GC thrashing
- C. The memory limit is being ignored
- D. Docker stats is wrong

<details><summary>Answer</summary>B. The container is running near its memory limit. Node.js garbage collection becomes aggressive and frequent, causing latency spikes. Increase the memory limit or optimize the app's memory usage. Also consider setting Node's <code>--max-old-space-size</code>.</details>

---

**Q25. Scenario:** A developer accidentally committed a `.env` file with database credentials to the Docker image three months ago. They removed it in a later commit. Is the secret safe?

<details><summary>Answer</summary>No. Docker image layers are additive. The <code>.env</code> file exists in an earlier layer even though it was removed in a later one. Anyone with access to the image can extract it with <code>docker history</code> or layer inspection tools. The image must be rebuilt from scratch, the secret must be rotated, and <code>.env</code> must be in <code>.dockerignore</code>.</details>

---

**Q26. Fill in the blank:** To handle SIGTERM properly in a Docker container (for graceful shutdown), you should use an _________ system like `tini` or `dumb-init` as the `ENTRYPOINT`.

<details><summary>Answer</summary>Init. Docker sends SIGTERM to PID 1 when stopping a container. If PID 1 is your Node.js app, it may not handle signals correctly (especially if started via npm scripts). An init system like <code>tini</code> forwards signals properly and reaps zombie processes.</details>

---

**Q27. Debugging:** You deploy a new container version. The old container stops. The new container starts but fails its health check. Now no containers are serving traffic. What went wrong?

<details><summary>Answer</summary>
The deployment strategy lacks overlap. Options to fix:<br>
1. <strong>Blue-green:</strong> Start the new container, verify health, then stop the old one.<br>
2. <strong>Rolling update:</strong> Only remove old instances as new ones pass health checks.<br>
3. <strong>Health check start period:</strong> Allow the new container time to initialize before checking health.<br>
4. <strong>Rollback automation:</strong> Automatically redeploy the old image if the new one fails health checks.
</details>

---

**Q28. Multiple choice:** Which are valid reasons to pin a Docker base image to a digest (SHA) instead of a tag? (Select all)

- A. Tags are mutable — the image behind `:alpine` can change
- B. Digests are faster to pull
- C. Prevents supply chain attacks via tag hijacking
- D. Ensures bit-for-bit reproducible builds

<details><summary>Answer</summary>A, C, and D. Tags can be moved to point to different images. Digests are immutable references. They don't affect pull speed (B is incorrect).</details>

---

**Q29. Scenario:** You need a private npm token during `docker build` to install private packages, but you don't want the token in any image layer. How do you solve this?

<details><summary>Answer</summary>
Use BuildKit secret mounts:<br>
<pre>
# syntax=docker/dockerfile:1
RUN --mount=type=secret,id=npmrc,target=/app/.npmrc npm ci
</pre>
Build with:<br>
<pre>
docker build --secret id=npmrc,src=$HOME/.npmrc .
</pre>
The secret is mounted during the RUN command but never persisted in any layer.
</details>

---

**Q30. Design question:** Your team has 15 microservices in a monorepo. CI builds all 15 images on every commit. Builds take 45 minutes. How would you redesign this?

<details><summary>Answer</summary>
1. <strong>Change detection:</strong> Only build images for services affected by the commit (path filters + dependency analysis).<br>
2. <strong>Shared base image:</strong> Common dependencies in a base image, service-specific layers on top.<br>
3. <strong>BuildKit cache:</strong> Use GitHub Actions cache (<code>cache-from: type=gha</code>) to reuse layers across builds.<br>
4. <strong>Parallel builds:</strong> Build independent services concurrently.<br>
5. <strong>Turbo prune:</strong> Use Turborepo to create minimal build contexts per service.<br>
Combined: 45 minutes → 5-10 minutes for most commits.
</details>

---

## 8. Personalized Recommendations

### Docker patterns most useful for your stack

Based on React, Next.js, Astro, TypeScript, and static files:

1. **Multi-stage builds** — Build with Node, serve with Nginx (React/Astro) or standalone Node (Next.js). This is your most important pattern.
2. **Docker Compose for local infrastructure** — Run PostgreSQL, Redis, and other services with one command while developing natively.
3. **Next.js standalone output** — Use `output: 'standalone'` for minimal Docker images with SSR.
4. **Development Compose overrides** — Bind mounts for hot reload, separate from production config.
5. **CI/CD image pipeline** — Build, scan, tag, push to registry in GitHub Actions.
6. **`.dockerignore`** — Essential for every project to keep builds fast and images clean.

### What to learn first (priority order)

| Priority | Topic | Why |
|---|---|---|
| 1 | Dockerfile basics + `docker build` + `docker run` | Foundation of everything |
| 2 | `.dockerignore` + layer caching | Prevent pain early |
| 3 | Multi-stage builds | Image size is the #1 frontend Docker problem |
| 4 | Docker Compose for local dev (DB, Redis) | Practical daily use |
| 5 | Environment variables + secrets | Configuration management |
| 6 | Volumes (named + bind mount) | Data persistence + hot reload |
| 7 | Networks + service communication | Multi-service architecture |
| 8 | Health checks | Production readiness |
| 9 | CI/CD integration (build + push) | Deployment pipeline |
| 10 | Security hardening | Production safety |

### Best practice projects

| Project | What you learn |
|---|---|
| Dockerize a React app (Vite) | Dockerfile, multi-stage, Nginx serving |
| Dockerize a Next.js app | Standalone output, SSR in container |
| Docker Compose: Next.js + PostgreSQL | Compose, volumes, networking, health checks |
| Full stack: React + Express + Postgres + Redis | Multi-service architecture |
| CI/CD: Build image in GitHub Actions, deploy to VPS | End-to-end pipeline |

### Common mistakes frontend engineers make with Docker

| Mistake | Why it happens | Fix |
|---|---|---|
| 1 GB+ images | Using `node:20` base | Use `node:20-alpine` + multi-stage |
| Slow builds every time | Wrong layer order | Copy lockfile first, then source |
| "Works in Docker but not locally" (or vice versa) | Different Node versions, env vars | Match versions, use `.env` consistently |
| Using `localhost` between containers | Frontend mental model | Use service names in Docker networks |
| Bind-mounting `node_modules` | Habit from local dev | Use anonymous volume to prevent overwrite |
| Putting secrets in Dockerfile | Quick and dirty | Use env vars, secrets, or BuildKit mounts |
| No `.dockerignore` | Didn't know it exists | Always create one with `node_modules`, `.git`, `.env` |
| Ignoring image scanning | "I trust the base image" | Scan regularly — images have CVEs |
| No health checks | "It starts, it works" | Add health checks for reliable orchestration |
| Running as root | Default behavior | Add `USER node` or create a non-root user |

### 30-day learning plan

#### Week 1: Foundations (Days 1–7)

| Day | Task | Deliverable |
|---|---|---|
| 1 | Install Docker, run `hello-world`, explore Docker Desktop | Working installation |
| 2 | Learn basic commands: `run`, `ps`, `stop`, `rm`, `images`, `logs`, `exec` | Command fluency |
| 3 | Write first Dockerfile for a simple Express server | Working Dockerfile |
| 4 | Learn `.dockerignore` and layer caching | Optimized build |
| 5 | Dockerize a React (Vite) app with multi-stage build + Nginx | ~25 MB production image |
| 6 | Dockerize a Next.js app with standalone output | Working Next.js container |
| 7 | Learn port mapping, environment variables, bind mounts | Configuration control |

#### Week 2: Docker Compose (Days 8–14)

| Day | Task | Deliverable |
|---|---|---|
| 8 | Write first `docker-compose.yml` — app + PostgreSQL | Multi-container setup |
| 9 | Learn volumes — persist database data | Data survives restarts |
| 10 | Learn networks — service-to-service communication | API connects to DB by name |
| 11 | Add Redis as a third service | Three-service architecture |
| 12 | Set up development overrides with bind mounts for hot reload | Fast dev feedback |
| 13 | Learn `depends_on` with health checks | Reliable service ordering |
| 14 | Debug a broken Compose setup — practice logs, exec, inspect | Debugging confidence |

#### Week 3: Production readiness (Days 15–21)

| Day | Task | Deliverable |
|---|---|---|
| 15 | Security: non-root user, minimal base, read-only filesystem | Hardened Dockerfile |
| 16 | Add health checks to all services | Observable containers |
| 17 | Set up Nginx reverse proxy | Production-like routing |
| 18 | Environment management: `.env` files, Compose overrides | Multi-environment config |
| 19 | Build and push image in GitHub Actions | CI/CD pipeline |
| 20 | Deploy to a VPS with `docker compose pull && up` | End-to-end deployment |
| 21 | Learn image scanning (`docker scout`) | Security awareness |

#### Week 4: Advanced patterns (Days 22–30)

| Day | Task | Deliverable |
|---|---|---|
| 22 | Set up a full-stack project: Next.js + API + Postgres + Redis | Complex architecture |
| 23 | Optimize build times with BuildKit cache mounts | Faster CI builds |
| 24 | Study monorepo Docker strategy | Scalable structure |
| 25 | Add background worker service (same image, different command) | Worker pattern |
| 26 | Set up logging and resource limits | Production observability |
| 27 | Study Docker vs. Kubernetes decision criteria | Architecture knowledge |
| 28 | Design a rollback strategy | Recovery mechanism |
| 29 | Review all Dockerfiles against the security checklist | Hardening pass |
| 30 | Write an architecture decision record for your Docker setup | Documentation |

---

## Summary, Next Steps, and Advanced Topics

### Concise Summary

Docker packages applications into portable, reproducible containers. Docker Compose orchestrates multiple containers on a single host. For a frontend engineer, the key insight is:

1. **Images are immutable artifacts** — like `dist/` from a build.
2. **Containers are running instances** — like a server process.
3. **Multi-stage builds** are essential — build big, run small.
4. **Compose** replaces the "install all dependencies" README with one command.
5. **Treat containers like cattle, not pets** — disposable, replaceable, stateless (data goes in volumes).

### Next Steps

1. Dockerize your current project today — start with a multi-stage Dockerfile.
2. Add Docker Compose for local infrastructure (database, cache).
3. Create `.dockerignore` and optimize layer caching.
4. Set up a CI/CD pipeline that builds and pushes images.
5. Harden your images: non-root user, alpine base, health checks.
6. Deploy a containerized app to a VPS or cloud service.

### Suggested Advanced Topics

| Topic | Why it matters |
|---|---|
| Kubernetes basics | Next step after outgrowing Docker Compose |
| Helm charts | Package and version Kubernetes deployments |
| Service mesh (Istio, Linkerd) | Observability and security between services |
| Container security scanning (Trivy, Snyk) | Automated vulnerability detection |
| Image signing and verification (cosign) | Supply chain integrity |
| Multi-architecture builds (buildx) | ARM support (Apple Silicon, AWS Graviton) |
| Rootless Docker | Enhanced host security |
| Distroless images | Absolute minimal attack surface |
| BuildKit advanced features | Secrets, SSH forwarding, cache mounts |
| Container observability (Prometheus, Grafana) | Production monitoring and alerting |
| Docker-in-Docker (DinD) vs. Docker-out-of-Docker | CI/CD container build strategies |
| Init systems (tini, dumb-init) | Proper signal handling and zombie reaping |
| Container runtime alternatives (Podman, containerd) | Broader ecosystem understanding |
| GitOps with containers (ArgoCD, Flux) | Declarative deployment management |
| Fly.io / Railway / Render | Managed container platforms for small teams |
