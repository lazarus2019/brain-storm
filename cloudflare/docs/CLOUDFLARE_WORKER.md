# Cloudflare Workers — Complete Deep-Dive Engineering Guide

> **Audience:** Frontend engineer (React / Next.js / Astro) moving toward backend, edge computing, and platform engineering.
> **Goal:** Go from zero to expert-level Cloudflare Worker engineer.

---

# Table of Contents

1. [Big Picture](#1-big-picture)
2. [Learning Roadmap by Skill Level](#2-learning-roadmap-by-skill-level)
3. [Setup Guide](#3-setup-guide)
4. [Cheatsheet](#4-cheatsheet)
5. [Real-World Engineering Mindset](#5-real-world-engineering-mindset)
6. [Brainstorm / Open Questions](#6-brainstorm--open-questions)
7. [Personalized Recommendations](#7-personalized-recommendations)
8. [Summary & Next Steps](#8-summary--next-steps)

---

# 1. Big Picture

## 1.1 What Are Cloudflare Workers?

Cloudflare Workers are **serverless functions that run on Cloudflare's global edge network** — over 300 data centers worldwide. Unlike traditional serverless (AWS Lambda, Vercel Functions) that run in a few regions, Workers execute **at the data center closest to the user**.

**Key mental shift from frontend:**
- In React/Next.js, you think: "code runs in the browser or on a server."
- In Workers, think: "code runs **between** the browser and the server, at the edge, globally."

Workers use the **V8 isolate model** — not Node.js, not a browser. They spin up in **under 5ms** (vs. Lambda cold starts of 100ms–several seconds). Each request gets its own lightweight isolate (not a container, not a VM).

## 1.2 Edge Runtime vs. Everything Else

```
┌─────────────────────────────────────────────────────────────────────────┐
│                       Runtime Comparison Matrix                         │
├──────────────────┬──────────┬──────────┬──────────┬──────────┬─────────┤
│ Feature          │ Browser  │ Node.js  │ Lambda   │ Workers  │ CDN     │
├──────────────────┼──────────┼──────────┼──────────┼──────────┼─────────┤
│ Location         │ Client   │ Server   │ Region   │ Edge     │ Edge    │
│ Cold start       │ N/A      │ N/A      │ 100ms+   │ <5ms     │ N/A     │
│ Full Node API    │ No       │ Yes      │ Yes      │ Partial  │ No      │
│ DOM APIs         │ Yes      │ No       │ No       │ No       │ No      │
│ Web Standard APIs│ Yes      │ Partial  │ Partial  │ Yes      │ No      │
│ File system      │ No       │ Yes      │ Yes      │ No       │ No      │
│ Long-running     │ Yes      │ Yes      │ 15min    │ 30s*     │ No      │
│ Global by default│ No       │ No       │ No       │ Yes      │ Yes     │
│ Persistent state │ No       │ Yes      │ No       │ KV/DO/R2 │ Cache   │
│ Cost at idle     │ Free     │ $$       │ Free     │ Free     │ Free    │
│ Max memory       │ Varies   │ Varies   │ 10GB     │ 128MB    │ N/A     │
└──────────────────┴──────────┴──────────┴──────────┴──────────┴─────────┘
* Workers can run up to 30s CPU time (or 15 min with Cron Triggers)
```

### What Workers Have (Web Standard APIs)

- `fetch()`, `Request`, `Response`, `Headers`, `URL`
- `crypto`, `TextEncoder` / `TextDecoder`
- `setTimeout` / `setInterval` (limited)
- `ReadableStream` / `WritableStream`
- `WebSocket`
- `structuredClone`, `atob`, `btoa`
- `AbortController` / `AbortSignal`

### What Workers Do NOT Have

- No `fs` (no file system)
- No native `require()` (use ES modules)
- No `process` / `process.env` (use `env` parameter)
- No full Node.js APIs (though `nodejs_compat` flag enables many)
- No DOM, `window`, `document`
- No long-running connections beyond WebSocket

## 1.3 When Workers Are a Good Fit

| ✅ Good Fit | ❌ Bad Fit |
|---|---|
| API proxying / gateway | Heavy computation (ML inference, video encoding) |
| Authentication / session validation | Long-running background jobs > 30s CPU |
| Request rewriting / routing | Apps needing full Node.js ecosystem |
| A/B testing, feature flags | Relational DB heavy operations (use D1 or external) |
| Edge-side personalization | Apps needing >128MB memory |
| Rate limiting | Apps requiring filesystem access |
| Image/content transformation | Stateful WebSocket servers (use Durable Objects) |
| Webhook processing | Monolithic applications |
| Cache management | |
| Static site enhancement | |
| Geolocation-based routing | |

## 1.4 Workers vs. Your Current Stack

```
┌───────────────────────────────────────────────────────────────────────────┐
│                     Workers vs. Frameworks You Know                       │
├─────────────────────┬────────────────────────────────────────────────────┤
│ Next.js API Routes  │ Similar concept, but Workers run at edge globally. │
│                     │ Next.js API routes run in one region (or edge if   │
│                     │ you opt in). Workers have no cold start.           │
│                     │ Workers can't use full Node.js by default.         │
├─────────────────────┼────────────────────────────────────────────────────┤
│ Next.js Edge Runtime│ VERY similar. Next.js Edge Runtime IS a V8 isolate │
│                     │ on Vercel. Workers are the same concept on         │
│                     │ Cloudflare. Same API constraints. Cloudflare has   │
│                     │ KV, DO, R2 — Vercel has KV, Blob.                 │
├─────────────────────┼────────────────────────────────────────────────────┤
│ Astro SSR           │ Astro can deploy TO Workers (adapter). The Worker  │
│                     │ becomes Astro's runtime. Think of Workers as the   │
│                     │ "engine" Astro SSR runs on when deployed to CF.    │
├─────────────────────┼────────────────────────────────────────────────────┤
│ Vercel Functions    │ Vercel serverless = AWS Lambda under the hood.     │
│                     │ Workers = V8 isolates. Workers are faster to cold  │
│                     │ start, cheaper at scale, but more constrained.     │
├─────────────────────┼────────────────────────────────────────────────────┤
│ Express / NestJS    │ Traditional server: one region, full Node.js,      │
│                     │ persistent connections, unlimited memory.          │
│                     │ Workers: global, constrained, stateless per request│
│                     │ (state via bindings). Hono is the "Express for     │
│                     │ Workers."                                          │
└─────────────────────┴────────────────────────────────────────────────────┘
```

## 1.5 Mental Model — Request Lifecycle

```
Browser (User)
    │
    ▼
┌─────────────────────────┐
│   Cloudflare Edge Node  │  ← Closest to user (any of 300+ cities)
│   (CDN + Worker Runtime)│
│                         │
│  1. DNS resolved to CF  │
│  2. TLS terminated      │
│  3. Cache checked        │
│     ├─ HIT → respond    │
│     └─ MISS ↓           │
│  4. Worker executes     │
│     ├─ KV read          │
│     ├─ DO interaction   │
│     ├─ fetch() origin   │
│     └─ R2 read/write    │
│  5. Response built      │
│  6. Cache stored (opt)  │
│  7. Response sent       │
└─────────────────────────┘
    │
    ▼
┌───────────────────┐
│  Origin Server    │  ← Your backend (optional — Workers can BE the backend)
│  (API, DB, etc.)  │
└───────────────────┘
```

**Key insight for frontend engineers:** A Worker sits WHERE a CDN sits. It's a CDN that can run code. You're not "calling a server" — you're "programming the network."

## 1.6 Cloudflare Primitives Ecosystem

```
┌─────────────────────────────────────────────────────────────────┐
│                    Cloudflare Developer Platform                  │
├──────────────┬──────────────────────────────────────────────────┤
│ Compute      │ Workers (stateless), Durable Objects (stateful), │
│              │ Workflows, Cron Triggers, Queues (consumers)     │
├──────────────┼──────────────────────────────────────────────────┤
│ Storage      │ KV (key-value, eventually consistent),           │
│              │ R2 (S3-compatible object storage),               │
│              │ D1 (SQLite at edge),                             │
│              │ Durable Object Storage (strongly consistent),    │
│              │ Hyperdrive (DB connection pooling)               │
├──────────────┼──────────────────────────────────────────────────┤
│ Messaging    │ Queues (pub/sub), Pub/Sub, Email Routing         │
├──────────────┼──────────────────────────────────────────────────┤
│ AI           │ Workers AI, Vectorize, AI Gateway                │
├──────────────┼──────────────────────────────────────────────────┤
│ Media        │ Images, Stream (video)                           │
├──────────────┼──────────────────────────────────────────────────┤
│ Security     │ WAF, Bot Management, Rate Limiting, mTLS         │
├──────────────┼──────────────────────────────────────────────────┤
│ Networking   │ Custom Domains, DNS, Tunnels, VPC               │
└──────────────┴──────────────────────────────────────────────────┘
```

---

# 2. Learning Roadmap by Skill Level

---

## Level 1 — Newbie

> "I've never touched Workers. I want to understand the fundamentals."

### Core Concepts to Memorize

1. **Workers execute on every request** — there's no server to manage
2. **No `process.env`** — environment is passed as `env` parameter
3. **No file system** — everything is in-memory or via bindings (KV, R2, DO)
4. **ES modules only** — use `export default { fetch() {} }`
5. **`fetch` handler is your entry point** — equivalent to Express `app.get('*', ...)`
6. **Bindings are your "dependencies"** — KV, DO, R2, secrets are injected via `env`
7. **CPU time ≠ wall clock time** — you get 10ms CPU (free) / 30s CPU (paid), but awaiting I/O doesn't count
8. **Everything is a `Request` in, `Response` out** — Web Standard APIs

### Minimum Setup

```bash
# Install Wrangler (Cloudflare's CLI — think of it as `next` CLI for Workers)
npm install -g wrangler

# Authenticate
wrangler login

# Create a project
npm create cloudflare@latest my-first-worker
# Select: "Hello World" Worker → TypeScript

# Navigate
cd my-first-worker

# Run locally
wrangler dev

# Deploy
wrangler deploy
```

### Project Structure (Hello World)

```
my-first-worker/
├── src/
│   └── index.ts          ← Your Worker entry point
├── wrangler.jsonc         ← Config (like next.config.js)
├── package.json
└── tsconfig.json
```

### First Worker — Hello World

```typescript
// src/index.ts
export default {
  async fetch(request: Request, env: Env, ctx: ExecutionContext): Promise<Response> {
    const url = new URL(request.url);

    if (url.pathname === "/") {
      return new Response("Hello from Cloudflare Workers!", {
        headers: { "content-type": "text/plain" },
      });
    }

    if (url.pathname === "/json") {
      return Response.json({
        message: "Hello!",
        timestamp: Date.now(),
        cf: request.cf, // Cloudflare-specific request metadata (country, colo, etc.)
      });
    }

    return new Response("Not Found", { status: 404 });
  },
} satisfies ExportedHandler<Env>;
```

### Common Mistakes (Newbie)

1. **Using `process.env`** — Use `env` parameter instead
2. **Importing Node.js modules** — Most don't work without `nodejs_compat` flag
3. **Not returning a `Response`** — Every `fetch` MUST return a `Response`
4. **Mutating global state** — Isolates are reused; global vars persist between requests unpredictably
5. **Forgetting `await`** — Async operations need `await` or `ctx.waitUntil()`
6. **Using `console.log` expecting persistent logs** — Logs are ephemeral (use `wrangler tail` to stream)

### 5 Practice Exercises

| # | Exercise | What You Learn |
|---|---|---|
| 1 | Return different responses based on URL path (`/hello`, `/time`, `/404`) | Routing fundamentals |
| 2 | Return the user's country from `request.cf.country` | CF request metadata |
| 3 | Proxy a request to `https://jsonplaceholder.typicode.com/posts` | `fetch()` from a Worker |
| 4 | Set a custom header `X-Powered-By: my-worker` on the response | Header manipulation |
| 5 | Return HTML with inline CSS that shows "Hello, {country}!" | HTML responses |

---

## Level 2 — Junior

> "I can make Workers. Now I want to build real things."

### Routing

Workers don't have a built-in router. You have three options:

**Option A: Manual routing (small projects)**
```typescript
export default {
  async fetch(request: Request, env: Env): Promise<Response> {
    const url = new URL(request.url);
    const { pathname } = url;

    if (pathname === "/api/users" && request.method === "GET") {
      return handleGetUsers(env);
    }
    if (pathname === "/api/users" && request.method === "POST") {
      return handleCreateUser(request, env);
    }
    return new Response("Not Found", { status: 404 });
  },
};
```

**Option B: Hono framework (recommended for most projects)**
```typescript
import { Hono } from "hono";
import { cors } from "hono/cors";
import { logger } from "hono/logger";

type Bindings = {
  MY_KV: KVNamespace;
  DB: D1Database;
};

const app = new Hono<{ Bindings: Bindings }>();

app.use("*", logger());
app.use("/api/*", cors());

app.get("/api/users", async (c) => {
  const users = await c.env.DB.prepare("SELECT * FROM users").all();
  return c.json(users.results);
});

app.post("/api/users", async (c) => {
  const body = await c.req.json();
  // ... handle creation
  return c.json({ success: true }, 201);
});

export default app;
```

**Option C: itty-router (ultra-lightweight)**
```typescript
import { Router } from "itty-router";
const router = Router();
router.get("/api/health", () => new Response("OK"));
export default { fetch: router.handle };
```

### KV (Key-Value Store)

KV is **eventually consistent**, high-read, low-write storage. Think of it as a global Redis with ~60s replication lag.

```typescript
// Write
await env.MY_KV.put("user:123", JSON.stringify({ name: "Thai Son" }));
await env.MY_KV.put("session:abc", "data", { expirationTtl: 3600 }); // TTL in seconds

// Read
const value = await env.MY_KV.get("user:123", "json"); // auto-parse JSON
const raw = await env.MY_KV.get("config", "text");

// Delete
await env.MY_KV.delete("user:123");

// List keys
const keys = await env.MY_KV.list({ prefix: "user:" });
```

**When to use KV:** Configuration, feature flags, session tokens, cached API responses, A/B test configs.

**When NOT to use KV:** Anything needing strong consistency, counters, frequently-written data.

### Durable Objects (Basics)

Durable Objects provide **strongly consistent, single-threaded, stateful** compute. Each DO instance has a unique ID and handles requests serially.

```typescript
import { DurableObject } from "cloudflare:workers";

export class Counter extends DurableObject {
  async fetch(request: Request): Promise<Response> {
    let count = (await this.ctx.storage.get<number>("count")) || 0;
    count++;
    await this.ctx.storage.put("count", count);
    return Response.json({ count });
  }
}

// In your main Worker:
export default {
  async fetch(request: Request, env: Env): Promise<Response> {
    const id = env.COUNTER.idFromName("global-counter");
    const stub = env.COUNTER.get(id);
    return stub.fetch(request);
  },
};
```

**Mental model:** A DO is like a single-threaded microservice with its own private database, pinned to one location.

### Environment Variables & Secrets

```jsonc
// wrangler.jsonc
{
  "vars": {
    "API_URL": "https://api.example.com",
    "ENVIRONMENT": "production"
  }
}
```

```bash
# Secrets (encrypted, not in config file)
wrangler secret put API_KEY
# Then type or paste the value

# Access in code:
env.API_KEY  // the secret value
env.API_URL  // the plain variable
```

### Error Handling Pattern

```typescript
export default {
  async fetch(request: Request, env: Env, ctx: ExecutionContext): Promise<Response> {
    try {
      return await handleRequest(request, env, ctx);
    } catch (error) {
      console.error("Unhandled error:", error);

      if (error instanceof HttpError) {
        return Response.json(
          { error: error.message },
          { status: error.status }
        );
      }

      return Response.json(
        { error: "Internal Server Error" },
        { status: 500 }
      );
    }
  },
};

class HttpError extends Error {
  constructor(public status: number, message: string) {
    super(message);
  }
}
```

### Middleware Pattern (without framework)

```typescript
type Middleware = (
  request: Request,
  env: Env,
  ctx: ExecutionContext,
  next: () => Promise<Response>
) => Promise<Response>;

const withCors: Middleware = async (req, env, ctx, next) => {
  if (req.method === "OPTIONS") {
    return new Response(null, {
      headers: {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE",
        "Access-Control-Allow-Headers": "Content-Type, Authorization",
      },
    });
  }
  const response = await next();
  response.headers.set("Access-Control-Allow-Origin", "*");
  return response;
};

const withAuth: Middleware = async (req, env, ctx, next) => {
  const token = req.headers.get("Authorization")?.replace("Bearer ", "");
  if (!token || token !== env.API_TOKEN) {
    return Response.json({ error: "Unauthorized" }, { status: 401 });
  }
  return next();
};
```

### 5 Mini Project Ideas

| # | Project | Bindings Used | Skills Practiced |
|---|---|---|---|
| 1 | URL shortener (create + redirect) | KV | CRUD, routing, redirects |
| 2 | API proxy with caching + rate limiting | KV, Cache API | fetch, cache, headers |
| 3 | Markdown pastebin | KV or R2 | File storage, content types |
| 4 | Webhook receiver that logs to R2 | R2, Queue | Async processing, storage |
| 5 | Simple auth API (register/login/verify) | KV, Secrets | Crypto, JWT, sessions |

### Common Architecture Mistakes (Junior)

1. **Using KV for counters** — KV is eventually consistent; use Durable Objects for counters
2. **Fetching your own Worker** — Causes infinite loops; use Service Bindings instead
3. **Not using `ctx.waitUntil()`** — For fire-and-forget tasks (logging, analytics), use `ctx.waitUntil(promise)` so they complete after the response is sent
4. **Storing large blobs in KV** — KV values max 25MB; use R2 for files
5. **Hardcoding secrets** — Use `wrangler secret put` and `env.SECRET_NAME`
6. **Not setting `compatibility_date`** — Always pin this to avoid breaking changes

---

## Level 3 — Senior

> "I can build things. Now I want to build production systems."

### Scalable Architecture Patterns

**Pattern 1: API Gateway**
```
                    ┌─────────────┐
Browser ──────────► │   Gateway   │ ──────► Auth Worker (Service Binding)
                    │   Worker    │ ──────► Users Worker (Service Binding)
                    │             │ ──────► Orders Worker (Service Binding)
                    └─────────────┘
```

**Pattern 2: Worker + Static Assets (SPA)**
```jsonc
// wrangler.jsonc
{
  "name": "my-app",
  "main": "./src/worker.ts",
  "assets": {
    "directory": "./dist",
    "not_found_handling": "single-page-application",
    "run_worker_first": ["/api/*"]
  }
}
```

**Pattern 3: Event-Driven Pipeline**
```
Request → Worker → Queue → Consumer Worker → R2 / D1 / External API
                                     ↓
                              Dead Letter Queue → Alert Worker
```

### Multi-Worker Architecture

```jsonc
// gateway/wrangler.jsonc
{
  "name": "gateway",
  "main": "src/index.ts",
  "services": [
    { "binding": "AUTH_SERVICE", "service": "auth-worker" },
    { "binding": "USER_SERVICE", "service": "user-worker" }
  ]
}
```

```typescript
// gateway/src/index.ts — Service Bindings (RPC, not HTTP)
export default {
  async fetch(request: Request, env: Env): Promise<Response> {
    const url = new URL(request.url);
    if (url.pathname.startsWith("/api/auth")) {
      return env.AUTH_SERVICE.fetch(request);
    }
    if (url.pathname.startsWith("/api/users")) {
      return env.USER_SERVICE.fetch(request);
    }
    return new Response("Not Found", { status: 404 });
  },
};
```

### Worker + KV + DO + R2 Strategy (Decision Matrix)

| Need | Use | Why |
|---|---|---|
| Configuration / feature flags | **KV** | Read-heavy, rarely written, eventually consistent is fine |
| User sessions / tokens | **KV** with TTL | Expiration built-in, global reads |
| Counters / rate limiting | **Durable Objects** | Strong consistency, atomic operations |
| Real-time collaboration | **Durable Objects** with WebSocket | Stateful, single-threaded coordination |
| File storage | **R2** | S3-compatible, no egress fees, up to 5TB per object |
| Relational data | **D1** | SQLite at the edge, SQL queries |
| Caching API responses | **Cache API** | Free, automatic, respects headers |
| Job queues | **Queues** | Guaranteed delivery, retries, dead-letter |
| Transactional state | **Durable Object Storage** | ACID-like within a single DO |

### Rate Limiting with Durable Objects

```typescript
export class RateLimiter extends DurableObject {
  async fetch(request: Request): Promise<Response> {
    const ip = request.headers.get("CF-Connecting-IP") || "unknown";
    const now = Date.now();
    const windowMs = 60_000; // 1 minute
    const maxRequests = 100;

    const key = `rate:${ip}`;
    const data = (await this.ctx.storage.get<{ count: number; resetAt: number }>(key)) || {
      count: 0,
      resetAt: now + windowMs,
    };

    if (now > data.resetAt) {
      data.count = 0;
      data.resetAt = now + windowMs;
    }

    data.count++;
    await this.ctx.storage.put(key, data);

    if (data.count > maxRequests) {
      return new Response("Too Many Requests", {
        status: 429,
        headers: { "Retry-After": String(Math.ceil((data.resetAt - now) / 1000)) },
      });
    }

    return new Response("OK");
  }
}
```

### CI/CD Pipeline

```yaml
# .github/workflows/deploy.yml
name: Deploy Worker
on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: "20"
      - run: npm ci
      - run: npm test
      - run: npx wrangler deploy
        env:
          CLOUDFLARE_API_TOKEN: ${{ secrets.CLOUDFLARE_API_TOKEN }}
          CLOUDFLARE_ACCOUNT_ID: ${{ secrets.CLOUDFLARE_ACCOUNT_ID }}
```

**Multi-environment deployment:**
```bash
# Deploy to staging
wrangler deploy --env staging

# Deploy to production
wrangler deploy --env production
```

### Monitoring & Observability

```jsonc
// wrangler.jsonc
{
  "observability": {
    "enabled": true,
    "logs": {
      "invocation_logs": true,
      "head_sampling_rate": 1  // 1 = 100%, 0.01 = 1%
    },
    "traces": {
      "enabled": true,
      "head_sampling_rate": 0.01  // Sample 1% for high-traffic
    }
  }
}
```

```bash
# Live tail logs
wrangler tail

# Filter by status
wrangler tail --status error

# Filter by search string
wrangler tail --search "timeout"
```

### Performance Optimization

1. **Use Cache API aggressively**
   ```typescript
   const cache = caches.default;
   const cached = await cache.match(request);
   if (cached) return cached;

   const response = await fetch(origin);
   const resp = new Response(response.body, response);
   resp.headers.set("Cache-Control", "s-maxage=3600");
   ctx.waitUntil(cache.put(request, resp.clone()));
   return resp;
   ```

2. **Stream responses** — Don't buffer entire responses in memory
3. **Use `ctx.waitUntil()`** for non-critical async work
4. **Minimize KV reads** — Cache hot keys in global variables (with TTL awareness)
5. **Use Smart Placement** for Workers that call a specific origin frequently

### Cost Optimization

| Tier | Requests | CPU Time | KV Reads | KV Writes |
|---|---|---|---|---|
| Free | 100K/day | 10ms/req | 100K/day | 1K/day |
| Paid ($5/mo) | 10M included | 30s/req | 10M incl. | 1M incl. |
| Over | $0.30/M | $0.02/M ms | $0.50/M | $5.00/M |

**Tips:**
- Cache API is **free** — use it to reduce KV reads
- Queue batching reduces consumer invocations
- Use `head_sampling_rate` for logs on high-traffic Workers
- R2 has **zero egress fees** — prefer over S3

### Migration Strategy from React/Next.js/Astro

| From | To | Strategy |
|---|---|---|
| Next.js API Routes | Worker with Hono | Port route handlers; replace `process.env` with `env`; replace Node APIs with Web APIs |
| Next.js Edge Runtime | Worker | Nearly 1:1; remove Next.js-specific imports |
| Astro SSR | Astro + CF adapter | `@astrojs/cloudflare` adapter; SSR pages become Worker-rendered |
| Static site | Workers Static Assets | Set `assets.directory` in wrangler config; add Worker for dynamic routes |
| Express middleware | Hono middleware | Replace `req`/`res` with `c` (context); replace `next()` pattern |

### 5 Production-Grade Project Examples

| # | Project | Architecture |
|---|---|---|
| 1 | Multi-tenant SaaS API | Gateway Worker → Service Workers → D1 per tenant |
| 2 | Image processing pipeline | Upload Worker → Queue → Consumer → R2 + Images API |
| 3 | Real-time collaborative editor | Durable Objects with WebSocket + R2 for persistence |
| 4 | API gateway with auth + rate limiting | Gateway Worker + DO (rate limit) + KV (sessions) |
| 5 | E-commerce storefront | Astro SSR on Workers + D1 + R2 + Queue (order processing) |

---

## Level 4 — Expert

> "I can build production systems. Now I want to design platforms."

### Designing Reusable Edge Platforms

Build **Worker libraries** that other teams compose:

```typescript
// packages/edge-auth/src/index.ts
export function createAuthMiddleware(config: AuthConfig) {
  return async (c: Context, next: Next) => {
    const token = c.req.header("Authorization")?.slice(7);
    const session = await c.env[config.kvBinding].get(`session:${token}`, "json");
    if (!session) return c.json({ error: "Unauthorized" }, 401);
    c.set("user", session);
    return next();
  };
}
```

### Multi-Tenant Architecture

```
┌───────────────────────────────────────────────────────────────┐
│                        Gateway Worker                          │
│  1. Extract tenant from subdomain / header / JWT               │
│  2. Route to tenant-specific Durable Object                    │
│  3. Each DO has its own SQLite (D1-like) storage               │
└─────────┬─────────────────────────────────────────────────────┘
          │
    ┌─────┴─────┐
    ▼           ▼
┌────────┐  ┌────────┐
│ DO:    │  │ DO:    │
│ tenant │  │ tenant │   Each tenant = isolated state
│ -acme  │  │ -corp  │   Strong consistency within tenant
└────────┘  └────────┘
```

### Global Consistency vs. Latency Trade-offs

| Storage | Consistency | Read Latency | Write Latency | Use When |
|---|---|---|---|---|
| KV | Eventual (~60s) | <10ms global | <50ms | Read-heavy, stale OK |
| DO Storage | Strong | <1ms (colocated) | <1ms (colocated) | Must be correct |
| D1 | Strong (per DB) | <10ms (nearest) | <50ms | Relational queries |
| R2 | Strong (per object) | <50ms | <100ms | Large objects |
| Cache API | Best-effort | <1ms | <1ms | Ephemeral, CDN-local |

**The Expert Question:** "If I need strong consistency AND low latency globally, what do I do?"

**Answer:** You can't have both (CAP theorem). Strategies:
1. **Accept eventual consistency** — KV + conflict resolution
2. **Route to single DO** — Strong consistency, but latency for users far from DO location
3. **CRDT-based DO** — Distribute state, merge conflicts automatically
4. **Read replicas** — Write to DO, fan-out to KV for reads

### Queue + Cron + Durable Object Coordination

```typescript
// Cron Trigger → checks for stale data
export default {
  async scheduled(event: ScheduledEvent, env: Env, ctx: ExecutionContext) {
    // Run every hour
    const staleKeys = await env.MY_KV.list({ prefix: "cache:" });
    for (const key of staleKeys.keys) {
      await env.REFRESH_QUEUE.send({ key: key.name });
    }
  },

  async queue(batch: MessageBatch, env: Env) {
    for (const msg of batch.messages) {
      const { key } = msg.body as { key: string };
      try {
        const fresh = await fetch(`https://api.example.com/data/${key}`);
        await env.MY_KV.put(key, await fresh.text(), { expirationTtl: 7200 });
        msg.ack();
      } catch {
        msg.retry();
      }
    }
  },
};
```

### Failure Scenarios and Recovery

| Scenario | Impact | Recovery Strategy |
|---|---|---|
| Worker throws unhandled exception | 500 to that request | Global error handler + alerting via tail workers |
| KV read returns stale data | User sees old data | TTL + cache busting + fallback to origin |
| Durable Object is unavailable | Requests to that DO fail | Retry with backoff; consider DO alarm for self-healing |
| Queue consumer fails | Message retried | Dead-letter queue + monitoring |
| R2 write fails | Data loss risk | Retry in `waitUntil`; idempotency keys |
| Deploy introduces bug | All traffic affected | Gradual rollouts; `wrangler versions deploy` with traffic splitting |
| Memory limit exceeded | Worker killed | Stream instead of buffer; split work across multiple Workers |

### Architecture Review Checklist

- [ ] Is every secret stored via `wrangler secret`?
- [ ] Are all bindings typed (run `wrangler types`)?
- [ ] Is error handling consistent with proper status codes?
- [ ] Are cache headers set correctly?
- [ ] Is there a dead-letter queue for failed async operations?
- [ ] Are Durable Object migrations versioned?
- [ ] Is observability enabled with appropriate sampling?
- [ ] Can the Worker be tested locally with `wrangler dev`?
- [ ] Is there a CI/CD pipeline with staging → production?
- [ ] Are rate limits in place for public endpoints?
- [ ] Is CORS configured correctly?
- [ ] Are large responses streamed (not buffered)?
- [ ] Is `ctx.waitUntil()` used for non-critical work?
- [ ] Is there a rollback strategy?

### What Experts Worry About That Juniors Miss

1. **Global state mutation** — V8 isolates reuse globals. A global `let counter = 0` will increment across requests unpredictably.
2. **Tail latency** — P50 is 5ms, but P99 might be 200ms due to KV cache misses.
3. **Billing surprises** — One hot loop = CPU time spike = cost spike.
4. **Durable Object location** — DOs get pinned to a region. If your users are global, DO access adds latency.
5. **Subrequest limits** — Free: 50 fetches/request. Paid: 1000 fetches/request.
6. **Bundle size** — Max 10MB compressed. Large dependencies bloat this fast.
7. **Migration safety** — Renaming a DO class without migration config = data loss.
8. **Poison messages** — A malformed queue message that always fails can block the queue.
9. **Cache stampede** — When cache expires, 1000 concurrent requests all hit origin.
10. **Dependency on Cloudflare** — Lock-in is real. KV, DO, R2 APIs are proprietary.

### 10 Advanced Engineering Discussion Topics

1. How would you design a distributed rate limiter that works across multiple Workers with sub-second accuracy?
2. What's the optimal strategy for migrating a 100-table PostgreSQL database to D1 + R2 + DO?
3. How do you implement CRDT-based conflict resolution in Durable Objects for a collaborative editor?
4. Design a multi-region failover system where Workers detect origin health and reroute automatically.
5. How would you build a Cloudflare-native event sourcing system using Queues + DO + D1?
6. What's the cost model for serving 1 billion requests/month, and where are the optimization leverage points?
7. How do you implement distributed tracing across 5 Workers connected via Service Bindings?
8. Design a zero-downtime migration from AWS Lambda + DynamoDB to Workers + KV + D1.
9. How would you build a multi-tenant platform where each tenant gets isolated compute AND storage?
10. What's the right testing strategy for a Worker system with 10 Service Bindings, 3 DOs, and 2 Queues?

---

# 3. Setup Guide

## 3.1 Installing Wrangler

```bash
# Global install (convenient)
npm install -g wrangler

# Per-project install (recommended for teams)
npm install --save-dev wrangler

# Verify
npx wrangler --version

# Login to Cloudflare
npx wrangler login
```

## 3.2 Creating a Project

```bash
# Interactive scaffolding (recommended)
npm create cloudflare@latest my-worker

# Manual init
mkdir my-worker && cd my-worker
npm init -y
npm install --save-dev wrangler typescript @cloudflare/workers-types
```

## 3.3 Recommended TypeScript Setup

```jsonc
// tsconfig.json
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "ES2022",
    "moduleResolution": "bundler",
    "lib": ["ES2022"],
    "types": ["@cloudflare/workers-types/2023-07-01"],
    "strict": true,
    "noEmit": true,
    "skipLibCheck": true,
    "forceConsistentCasingInFileNames": true,
    "resolveJsonModule": true,
    "isolatedModules": true,
    "jsx": "react-jsx"
  },
  "include": ["src/**/*"],
  "exclude": ["node_modules"]
}
```

```bash
# Generate types from your wrangler config (auto-types your Env)
npx wrangler types
```

## 3.4 Folder Structures

### Small Project (1–3 routes)

```
my-worker/
├── src/
│   └── index.ts           ← Single entry point with all logic
├── wrangler.jsonc
├── package.json
└── tsconfig.json
```

### Medium Project (5–20 routes)

```
my-worker/
├── src/
│   ├── index.ts            ← Entry point, registers routes
│   ├── routes/
│   │   ├── users.ts
│   │   ├── auth.ts
│   │   └── health.ts
│   ├── services/
│   │   ├── user-service.ts
│   │   └── auth-service.ts
│   ├── middleware/
│   │   ├── cors.ts
│   │   ├── auth.ts
│   │   └── error-handler.ts
│   ├── utils/
│   │   ├── response.ts
│   │   └── validation.ts
│   └── types.ts
├── test/
│   ├── routes/
│   └── services/
├── wrangler.jsonc
├── vitest.config.ts
├── package.json
└── tsconfig.json
```

### Large Project (monorepo, multi-worker)

```
my-platform/
├── packages/
│   ├── shared/              ← Shared types, utils, middleware
│   │   ├── src/
│   │   └── package.json
│   ├── edge-auth/           ← Reusable auth library
│   │   ├── src/
│   │   └── package.json
│   └── edge-logger/         ← Reusable logging
│       ├── src/
│       └── package.json
├── workers/
│   ├── gateway/             ← API gateway Worker
│   │   ├── src/
│   │   │   ├── index.ts
│   │   │   ├── routes/
│   │   │   └── middleware/
│   │   ├── wrangler.jsonc
│   │   └── package.json
│   ├── auth/                ← Auth microservice Worker
│   │   ├── src/
│   │   ├── wrangler.jsonc
│   │   └── package.json
│   ├── users/               ← Users microservice Worker
│   │   ├── src/
│   │   ├── wrangler.jsonc
│   │   └── package.json
│   └── jobs/                ← Queue consumer Worker
│       ├── src/
│       ├── wrangler.jsonc
│       └── package.json
├── infrastructure/
│   ├── terraform/           ← Optional IaC
│   └── scripts/
├── turbo.json               ← Turborepo config
├── package.json
└── pnpm-workspace.yaml
```

## 3.5 Example wrangler.jsonc (Production-Ready)

```jsonc
{
  "$schema": "./node_modules/wrangler/config-schema.json",
  "name": "my-api",
  "main": "src/index.ts",
  "compatibility_date": "2026-04-15",
  "compatibility_flags": ["nodejs_compat"],

  // Environment variables (non-secret)
  "vars": {
    "ENVIRONMENT": "development",
    "API_VERSION": "v1",
    "LOG_LEVEL": "debug"
  },

  // KV Namespaces
  "kv_namespaces": [
    { "binding": "CACHE", "id": "dev-kv-id" }
  ],

  // R2 Buckets
  "r2_buckets": [
    { "binding": "UPLOADS", "bucket_name": "my-uploads-dev" }
  ],

  // Durable Objects
  "durable_objects": {
    "bindings": [
      { "name": "RATE_LIMITER", "class_name": "RateLimiter" }
    ]
  },
  "migrations": [
    { "tag": "v1", "new_sqlite_classes": ["RateLimiter"] }
  ],

  // Queues
  "queues": {
    "producers": [
      { "binding": "JOB_QUEUE", "queue": "my-jobs" }
    ],
    "consumers": [
      {
        "queue": "my-jobs",
        "max_batch_size": 10,
        "max_batch_timeout": 30,
        "max_retries": 3,
        "dead_letter_queue": "my-jobs-dlq"
      }
    ]
  },

  // Cron Triggers
  "triggers": {
    "crons": ["0 * * * *"]  // Every hour
  },

  // Observability
  "observability": {
    "enabled": true,
    "logs": { "invocation_logs": true, "head_sampling_rate": 1 }
  },

  // Service Bindings
  "services": [
    { "binding": "AUTH_SERVICE", "service": "auth-worker" }
  ],

  // Production environment
  "env": {
    "production": {
      "vars": {
        "ENVIRONMENT": "production",
        "LOG_LEVEL": "warn"
      },
      "kv_namespaces": [
        { "binding": "CACHE", "id": "prod-kv-id" }
      ],
      "r2_buckets": [
        { "binding": "UPLOADS", "bucket_name": "my-uploads-prod" }
      ],
      "routes": [
        { "pattern": "api.example.com/*", "zone_name": "example.com" }
      ],
      "observability": {
        "enabled": true,
        "logs": { "head_sampling_rate": 0.1 },
        "traces": { "enabled": true, "head_sampling_rate": 0.01 }
      }
    },
    "staging": {
      "vars": {
        "ENVIRONMENT": "staging",
        "LOG_LEVEL": "info"
      },
      "kv_namespaces": [
        { "binding": "CACHE", "id": "staging-kv-id" }
      ],
      "workers_dev": true
    }
  }
}
```

## 3.6 Example package.json

```jsonc
{
  "name": "my-worker",
  "version": "1.0.0",
  "private": true,
  "scripts": {
    "dev": "wrangler dev",
    "dev:remote": "wrangler dev --remote",
    "deploy": "wrangler deploy",
    "deploy:staging": "wrangler deploy --env staging",
    "deploy:production": "wrangler deploy --env production",
    "types": "wrangler types",
    "test": "vitest run",
    "test:watch": "vitest",
    "lint": "eslint src/",
    "tail": "wrangler tail",
    "tail:production": "wrangler tail --env production"
  },
  "dependencies": {
    "hono": "^4.0.0"
  },
  "devDependencies": {
    "@cloudflare/vitest-pool-workers": "^0.5.0",
    "@cloudflare/workers-types": "^4.0.0",
    "typescript": "^5.5.0",
    "vitest": "^2.0.0",
    "wrangler": "^4.0.0"
  }
}
```

## 3.7 Recommended Starter Template

For someone with your React/Next.js/Astro background, here's the fastest path:

```bash
# Option A: API Worker with Hono (recommended — feels like Express)
npm create cloudflare@latest my-api -- --template https://github.com/honojs/starter

# Option B: Full-stack with Astro + Workers
npm create cloudflare@latest my-site -- --framework astro

# Option C: SPA (React/Vite) + Worker API
npm create cloudflare@latest my-app -- --framework react

# Option D: Bare Worker + Static Assets (most control)
npm create cloudflare@latest my-app
# Select "Hello World" Worker + Assets
```

**My recommendation:** Start with **Hono on Workers**. It's the closest mental model to Express/Next.js API routes, has excellent TypeScript support, and is built specifically for edge runtimes.

---

# 4. Cheatsheet

## 4.1 Wrangler CLI Commands

| Command | What It Does |
|---|---|
| `wrangler dev` | Start local dev server (hot reload) |
| `wrangler dev --remote` | Dev server running on Cloudflare (real bindings) |
| `wrangler deploy` | Deploy to production |
| `wrangler deploy --env staging` | Deploy to specific environment |
| `wrangler tail` | Live stream logs from deployed Worker |
| `wrangler tail --status error` | Stream only error logs |
| `wrangler types` | Generate TypeScript types from config |
| `wrangler secret put SECRET_NAME` | Set an encrypted secret |
| `wrangler secret list` | List all secrets |
| `wrangler kv namespace create NS` | Create a KV namespace |
| `wrangler kv key put --binding KV "key" "value"` | Put a KV key |
| `wrangler kv key get --binding KV "key"` | Get a KV value |
| `wrangler r2 bucket create my-bucket` | Create an R2 bucket |
| `wrangler r2 object put bucket/key --file ./f` | Upload to R2 |
| `wrangler d1 create my-db` | Create a D1 database |
| `wrangler d1 execute my-db --file schema.sql` | Run SQL on D1 |
| `wrangler queues create my-queue` | Create a queue |
| `wrangler login` | Authenticate with Cloudflare |
| `wrangler whoami` | Check current auth |
| `wrangler deployments list` | List recent deployments |
| `wrangler versions deploy` | Gradual rollout / traffic splitting |

## 4.2 Worker Entry Points

```typescript
// Standard fetch handler
export default {
  async fetch(request: Request, env: Env, ctx: ExecutionContext): Promise<Response> {
    return new Response("Hello");
  },
} satisfies ExportedHandler<Env>;
```

```typescript
// Cron handler
export default {
  async scheduled(event: ScheduledEvent, env: Env, ctx: ExecutionContext) {
    ctx.waitUntil(doCleanup(env));
  },
};
```

```typescript
// Queue consumer
export default {
  async queue(batch: MessageBatch, env: Env) {
    for (const msg of batch.messages) {
      console.log(msg.body);
      msg.ack();
    }
  },
};
```

```typescript
// Email handler
export default {
  async email(message: EmailMessage, env: Env, ctx: ExecutionContext) {
    await message.forward("admin@example.com");
  },
};
```

## 4.3 Request / Response Patterns

```typescript
// Parse URL
const url = new URL(request.url);
const path = url.pathname;           // "/api/users"
const query = url.searchParams;      // ?page=2
const page = query.get("page");      // "2"

// Read body
const json = await request.json();
const text = await request.text();
const form = await request.formData();
const buffer = await request.arrayBuffer();

// Read headers
const auth = request.headers.get("Authorization");
const contentType = request.headers.get("Content-Type");

// Cloudflare-specific metadata
const country = request.cf?.country;     // "US"
const city = request.cf?.city;           // "San Francisco"
const colo = request.cf?.colo;           // "SFO"
const tlsVersion = request.cf?.tlsVersion;

// Create responses
return new Response("text", { status: 200 });
return Response.json({ data: [] });
return Response.json({ error: "Not found" }, { status: 404 });
return Response.redirect("https://example.com", 301);
return new Response(null, { status: 204 });
return new Response(readableStream, {
  headers: { "Content-Type": "application/octet-stream" },
});
```

## 4.4 Cache API

```typescript
// Read from cache
const cache = caches.default;
const cacheKey = new Request(url.toString(), request);
const cached = await cache.match(cacheKey);
if (cached) return cached;

// Fetch and cache
const response = await fetch(request);
const resp = new Response(response.body, response);
resp.headers.set("Cache-Control", "s-maxage=3600");
ctx.waitUntil(cache.put(cacheKey, resp.clone()));
return resp;

// Delete from cache
await cache.delete(cacheKey);

// Named cache
const namedCache = await caches.open("my-cache");
```

## 4.5 KV Snippets

```typescript
// String operations
await env.KV.put("key", "value");
await env.KV.put("key", "value", { expirationTtl: 3600 });
await env.KV.put("key", "value", { expiration: Math.floor(Date.now()/1000) + 3600 });
await env.KV.put("key", "value", { metadata: { created: Date.now() } });

const val = await env.KV.get("key");                 // string | null
const json = await env.KV.get("key", "json");         // parsed JSON | null
const buf = await env.KV.get("key", "arrayBuffer");   // ArrayBuffer | null
const stream = await env.KV.get("key", "stream");     // ReadableStream | null

// With metadata
const { value, metadata } = await env.KV.getWithMetadata("key", "json");

// Delete
await env.KV.delete("key");

// List keys (paginated)
const list = await env.KV.list({ prefix: "user:", limit: 100 });
for (const key of list.keys) {
  console.log(key.name, key.metadata);
}
if (!list.list_complete) {
  const more = await env.KV.list({ prefix: "user:", cursor: list.cursor });
}
```

## 4.6 Durable Object Snippets

```typescript
// Define a Durable Object
import { DurableObject } from "cloudflare:workers";

export class MyDO extends DurableObject {
  async fetch(request: Request): Promise<Response> {
    // Storage API
    await this.ctx.storage.put("key", "value");
    const val = await this.ctx.storage.get("key");
    await this.ctx.storage.delete("key");

    // Atomic transaction
    await this.ctx.storage.transaction(async (txn) => {
      const current = await txn.get<number>("counter") || 0;
      await txn.put("counter", current + 1);
    });

    // Alarm (scheduled callback)
    await this.ctx.storage.setAlarm(Date.now() + 60_000);

    return Response.json({ val });
  }

  async alarm() {
    // Called when alarm fires
    console.log("Alarm fired!");
    // Optionally re-schedule
    await this.ctx.storage.setAlarm(Date.now() + 60_000);
  }
}

// Access from Worker
const id = env.MY_DO.idFromName("unique-name");
// or: const id = env.MY_DO.newUniqueId();
const stub = env.MY_DO.get(id);
const response = await stub.fetch(request);
```

## 4.7 R2 Snippets

```typescript
// Upload
await env.BUCKET.put("path/file.png", request.body, {
  httpMetadata: { contentType: "image/png" },
  customMetadata: { uploadedBy: "user-123" },
});

// Download
const object = await env.BUCKET.get("path/file.png");
if (!object) return new Response("Not Found", { status: 404 });
const headers = new Headers();
object.writeHttpMetadata(headers);
headers.set("etag", object.httpEtag);
return new Response(object.body, { headers });

// Delete
await env.BUCKET.delete("path/file.png");

// List objects
const listed = await env.BUCKET.list({ prefix: "uploads/", limit: 100 });
for (const obj of listed.objects) {
  console.log(obj.key, obj.size);
}

// Head (metadata only)
const head = await env.BUCKET.head("path/file.png");
```

## 4.8 Queue Snippets

```typescript
// Producer: Send messages
await env.MY_QUEUE.send({ type: "email", to: "user@example.com" });
await env.MY_QUEUE.send("simple string message");
await env.MY_QUEUE.sendBatch([
  { body: { id: 1 } },
  { body: { id: 2 } },
  { body: { id: 3 }, delaySeconds: 60 },  // Delay delivery
]);

// Consumer: Process messages
export default {
  async queue(batch: MessageBatch, env: Env): Promise<void> {
    for (const msg of batch.messages) {
      try {
        await processMessage(msg.body, env);
        msg.ack();       // Success
      } catch (error) {
        msg.retry();     // Will be retried
      }
    }
  },
};
```

## 4.9 Cron Snippets

```jsonc
// wrangler.jsonc
{ "triggers": { "crons": ["*/5 * * * *", "0 0 * * *"] } }
```

```typescript
export default {
  async scheduled(event: ScheduledEvent, env: Env, ctx: ExecutionContext) {
    switch (event.cron) {
      case "*/5 * * * *":
        ctx.waitUntil(refreshCache(env));
        break;
      case "0 0 * * *":
        ctx.waitUntil(dailyCleanup(env));
        break;
    }
  },
};
```

## 4.10 Environment Variable Patterns

```typescript
// In wrangler.jsonc:     "vars": { "API_URL": "https://..." }
// Secrets:               wrangler secret put API_KEY
// In code:               env.API_URL, env.API_KEY

// Type your Env (auto-generated by `wrangler types`)
interface Env {
  // Vars
  API_URL: string;
  ENVIRONMENT: string;
  // Secrets
  API_KEY: string;
  // Bindings
  MY_KV: KVNamespace;
  MY_BUCKET: R2Bucket;
  MY_DO: DurableObjectNamespace;
  MY_QUEUE: Queue;
  MY_DB: D1Database;
  // Service Bindings
  AUTH_SERVICE: Service;
}
```

## 4.11 Common Error Messages

| Error | Cause | Fix |
|---|---|---|
| `Error: No matching export` | Missing `export default` | Add `export default { fetch() {} }` |
| `Error: Script startup exceeded CPU limit` | Top-level code too heavy | Move init logic into handler |
| `Error: Subrequest depth limit` | Worker calling itself | Use Service Bindings instead |
| `Error: Memory limit exceeded` | Buffering too much data | Stream responses |
| `NetworkError: connection refused` | `wrangler dev` port conflict | Change port: `wrangler dev --port 8788` |
| `Error 10021: too many KV operations` | KV rate limit hit | Batch operations, add caching layer |
| `TypeError: Cannot read properties of undefined` | Accessing binding that isn't configured | Check wrangler.jsonc binding names |
| `Error: Durable Object migration needed` | New DO class without migration | Add migration tag in config |

## 4.12 Performance Tips

1. **Cache aggressively** — Cache API is free, reduce origin fetches
2. **Stream, don't buffer** — Use `ReadableStream` for large payloads
3. **Minimize KV reads** — Global variable cache with TTL check
4. **Use Smart Placement** — For Workers that call a specific backend region
5. **Batch Queue sends** — `sendBatch()` is cheaper than individual `send()`
6. **Reuse connections** — `fetch()` connection pooling is automatic
7. **Use `waitUntil()`** — For async non-critical work after response
8. **Minimize bundle size** — Tree-shake, avoid large libraries

## 4.13 Security Tips

1. **Never hardcode secrets** — Use `wrangler secret put`
2. **Validate all input** — Use Zod or similar for request validation
3. **Rate limit public endpoints** — Durable Objects or CF Rate Limiting rules
4. **Set CORS correctly** — Don't use `*` in production
5. **Use `CF-Connecting-IP`** — Cloudflare provides the real client IP
6. **Enable Bot Management** — If on Business/Enterprise plan
7. **Sanitize HTML output** — Prevent XSS in HTML responses
8. **Use mTLS** — For Worker-to-Worker or Worker-to-origin auth
9. **Pin `compatibility_date`** — Prevents surprise API changes
10. **Audit `wrangler secret list`** — Know what secrets are deployed

---

# 5. Real-World Engineering Mindset

For each use case: **problem → strategies → trade-offs → recommendation.**

---

## 5.1 API Proxy

**Problem:** Frontend needs to call a third-party API, but CORS, auth keys, or rate limits prevent direct browser calls.

| Strategy | Pros | Cons | Scale |
|---|---|---|---|
| Worker as simple proxy | Zero cold start, global, hides API keys | Single point of failure for proxy | Small–Large |
| Worker + Cache API | Reduces origin calls, fast | Cache invalidation complexity | Medium–Large |
| Worker + KV cache | Longer TTL, global cache | Eventually consistent | Large |
| Worker + Queue for writes | Decouples write latency | Complexity, eventual | Large |

**Senior choice:** Worker + Cache API for reads, Queue for writes. Cache API is free and fast. KV only if you need custom TTL or need to cache across subrequests.

**Hidden pitfall:** If the third-party API goes down, your Worker still processes requests. Implement circuit breaker pattern or fallback.

---

## 5.2 Authentication Session Storage

**Problem:** Store user sessions after login, validate on every request.

| Strategy | Pros | Cons |
|---|---|---|
| KV with TTL | Simple, global reads, auto-expiry | Eventually consistent (60s replication) |
| Durable Object | Strongly consistent, instant invalidation | Higher latency for distant users |
| JWT (stateless) | No storage needed, instant validation | Can't revoke without blocklist |
| JWT + KV blocklist | Best of both worlds | Extra KV read per request |

**Senior choice:** JWT for auth + KV for revocation blocklist. The blocklist is small and rarely changes, perfect for KV.

**Cost:** KV reads are $0.50/M after free tier. At 10M requests/day = $5/day. Consider caching JWT validation result briefly.

---

## 5.3 Rate Limiting

**Problem:** Prevent abuse of public APIs.

| Strategy | Pros | Cons |
|---|---|---|
| CF Rate Limiting rules (dashboard) | Zero code, managed | Less flexible, costs per rule |
| Durable Object per IP | Precise, strongly consistent | One DO per IP = lots of DOs |
| KV-based sliding window | Global, simple | Eventually consistent = imprecise |
| DO per endpoint + sliding window | Balanced precision | Medium complexity |

**Senior choice:** CF Rate Limiting rules for broad protection + DO-based limiter for sensitive endpoints (login, payment). KV for non-critical soft limits.

---

## 5.4 Image Optimization

**Problem:** Serve optimized images based on device, format, and size.

| Strategy | Pros | Cons |
|---|---|---|
| Cloudflare Images API | Managed, auto-format (WebP/AVIF) | $5/month + per-image cost |
| Worker + R2 + CF Image Resizing | Full control, no egress on R2 | More code to maintain |
| External (Imgix, Cloudinary) | Feature-rich | Egress costs, another vendor |

**Senior choice:** Worker + R2 + CF Image Resizing. Store originals in R2 (zero egress), use Image Resizing via `fetch()` with `cf.image` options. Cache transformed images.

```typescript
const imageUrl = new URL(request.url);
const response = await fetch(imageUrl, {
  cf: {
    image: {
      width: 400,
      height: 300,
      fit: "cover",
      format: "auto", // auto-selects WebP/AVIF based on Accept header
    },
  },
});
```

---

## 5.5 Feature Flags

**Problem:** Control feature rollout without deploying.

| Strategy | Pros | Cons |
|---|---|---|
| KV-stored flags | Global, fast reads, update via API | Eventually consistent (60s lag) |
| Worker environment variables | Instant, no read cost | Requires redeploy to change |
| External service (LaunchDarkly) | Full featured | Extra latency, cost, dependency |
| D1-stored flags with KV cache | Queryable + fast | More complex |

**Senior choice:** KV for flags. Read once per request (or cache in global with 30s TTL). Update via Cloudflare API or admin Worker. The 60s eventual consistency is fine for feature flags.

```typescript
async function getFlag(env: Env, flag: string): Promise<boolean> {
  const value = await env.FLAGS_KV.get(`flag:${flag}`, "json");
  return value?.enabled ?? false;
}
```

---

## 5.6 A/B Testing

**Problem:** Route users to different experiences and track results.

| Strategy | Pros | Cons |
|---|---|---|
| Worker + KV (experiment config) | Full control, edge-fast | Build your own analytics |
| Worker + cookie-based bucketing | Sticky sessions, simple | Cookie management |
| Third-party (Optimizely, etc.) | Feature-rich | Latency, cost |

**Senior choice:** Worker assigns bucket via hash of user ID → stores in cookie → reads experiment config from KV → modifies response. Track events via Queue → external analytics.

---

## 5.7 Analytics Collection

**Problem:** Collect user analytics without blocking the response.

| Strategy | Pros | Cons |
|---|---|---|
| `ctx.waitUntil()` + fetch to analytics API | Simple, non-blocking | If the analytics API is slow, context held open |
| Queue → Consumer Worker → external API | Decoupled, batched, reliable | More infra |
| Queue → Consumer → R2 (batch files) | Zero vendor lock-in, cheap storage | Need to process R2 files later |

**Senior choice:** Queue for important events (conversions), `waitUntil` + direct fetch for lightweight pageview tracking. R2 archival for compliance.

---

## 5.8 Realtime Chat

**Problem:** Low-latency, multi-user chat.

| Strategy | Pros | Cons |
|---|---|---|
| Durable Object + WebSocket | Native CF, strongly consistent | DO pinned to one region |
| External WebSocket (Pusher, Ably) | Battle-tested, global | Cost, latency, dependency |
| DO per chat room | Room-level isolation | Hot rooms = single DO bottleneck |

**Senior choice:** Durable Object per chat room with WebSocket Hibernation API. This lets the DO sleep when idle (no cost) and wake on message. For truly global chat, consider DO per region + eventual sync.

---

## 5.9 Notification System

**Problem:** Send notifications (email, push, SMS) reliably.

```
Request → Worker → Queue (notifications) → Consumer Worker → External APIs
                                                    ↓ (on failure)
                                              Dead Letter Queue → Alert
```

**Senior choice:** Always use Queues for notifications. Never send directly from the request handler. Queue gives you retries, dead-letter, and batching. Consumer Worker calls SendGrid/Twilio/FCM.

---

## 5.10 Static Site with Dynamic Personalization

**Problem:** Your Astro/React site is static, but you want personalized content.

| Strategy | Pros | Cons |
|---|---|---|
| Worker intercepts HTML, injects data | No client JS needed, SEO-friendly | HTML parsing complexity |
| Worker sets cookies, client JS reads | Simple Worker logic | Requires client JS, FOUC |
| Edge-side includes (ESI) | Standard pattern | Limited support |
| `HTMLRewriter` API | Stream-based HTML transform, fast | Learning curve |

**Senior choice:** `HTMLRewriter` — Cloudflare's stream-based HTML transformation API. Transforms HTML on the fly without buffering.

```typescript
return new HTMLRewriter()
  .on("#user-name", {
    element(el) {
      el.setInnerContent(userName);
    },
  })
  .on("#user-country", {
    element(el) {
      el.setInnerContent(request.cf?.country || "Unknown");
    },
  })
  .transform(await fetch(request));
```

---

## 5.11 File Upload

**Problem:** Accept file uploads from users.

| Strategy | Pros | Cons |
|---|---|---|
| Worker → R2 (direct) | Simple, zero egress | 128MB Worker memory limit |
| Presigned URL (R2 → client) | Bypasses Worker memory limit | More complex client |
| Worker → R2 multipart | Large files, resumable | Complex implementation |

**Senior choice:** For files <100MB, direct Worker → R2. For larger files, generate presigned URLs and let the client upload directly to R2. For very large files, multipart upload API.

---

## 5.12 Cache Invalidation

**Problem:** When data changes, cached responses are stale.

| Strategy | Pros | Cons |
|---|---|---|
| TTL-based (set short cache times) | Simple | Stale window exists |
| Purge via API on write | Immediate invalidation | Purge API has rate limits |
| Cache tags + tag-based purge | Granular | Enterprise feature |
| KV as cache (manual control) | Full control | More code, KV cost |

**Senior choice:** Short TTL (30–60s) + `stale-while-revalidate` for most cases. Cache tag purge for enterprise. KV + custom invalidation for critical data.

---

## 5.13 Multi-Region Data

**Problem:** Your data needs to be close to users globally.

| Strategy | Pros | Cons |
|---|---|---|
| KV (global replication) | Auto-replicated, fast reads | Eventually consistent |
| DO per region | Strong consistency per region | Manual routing |
| D1 (single primary) | SQL queries, replicas coming | Write latency for distant users |
| Hyperdrive + external DB | Use existing Postgres | Depends on DB location |

**Senior choice:** KV for read-heavy global data. D1 for relational. Hyperdrive for existing databases. DO only for coordination that MUST be consistent.

---

## 5.14 Webhook Processing

**Problem:** Receive webhooks from external services reliably.

```typescript
export default {
  async fetch(request: Request, env: Env, ctx: ExecutionContext): Promise<Response> {
    // Validate webhook signature (important!)
    const signature = request.headers.get("X-Webhook-Signature");
    const body = await request.text();
    if (!verifySignature(body, signature, env.WEBHOOK_SECRET)) {
      return new Response("Invalid signature", { status: 401 });
    }

    // Queue for reliable processing (respond 200 immediately)
    ctx.waitUntil(env.WEBHOOK_QUEUE.send({ payload: JSON.parse(body) }));

    return new Response("OK", { status: 200 });
  },
};
```

**Key principle:** Respond 200 immediately, process asynchronously via Queue. External services have short timeout windows.

---

## 5.15 Background Jobs

**Problem:** Process tasks that take longer than a request cycle.

| Strategy | Pros | Cons |
|---|---|---|
| `ctx.waitUntil()` | Simple, extends request | Still limited to 30s CPU |
| Queues | Reliable, retries, batching | Async, can't return result to user |
| Workflows | Multi-step, durable, resumable | Newer API, more complex |
| DO Alarms | Scheduled, per-entity | Tied to a DO instance |
| Cron Triggers | Periodic, reliable | Fixed schedule, not on-demand |

**Senior choice:** Queues for most background work. Workflows for multi-step processes. DO Alarms for per-entity scheduled tasks (e.g., "send reminder 24h after signup").

---

# 6. Brainstorm / Open Questions

## Architecture

1. If your Worker receives 100x more traffic tomorrow, what breaks first?
2. Should you use one Worker with routing or many Workers with Service Bindings? At what scale does this matter?
3. How would you design a Worker architecture where a single bug in one feature doesn't take down the whole API?
4. When should you use Cloudflare Pages vs. Workers Static Assets vs. Workers alone?
5. How would you architect a system that needs both strong consistency (Durable Objects) and global low-latency reads (KV)?
6. If you need to process 10,000 webhook events per second, what's your architecture?
7. How would you design a Worker-based system that handles both synchronous HTTP responses and asynchronous background jobs?

## Scaling

8. At what point does a Durable Object become a bottleneck, and how do you shard it?
9. What happens to your KV-cached data if Cloudflare has a regional outage?
10. How do you handle Queue consumer backpressure when messages arrive faster than they can be processed?
11. If your R2 bucket reaches 1 billion objects, how does that affect list operations?
12. What's the maximum realistic throughput of a single Durable Object?
13. How would you distribute writes across DO instances for a high-write workload?
14. What's the cost breakdown for serving 100M requests/month across Workers + KV + R2 + Queues?

## Security

15. How do you prevent SSRF attacks in a Worker that makes `fetch()` calls based on user input?
16. What's your strategy for rotating secrets across 50 Workers without downtime?
17. How do you implement end-to-end encryption for data stored in KV or R2?
18. If a Worker is compromised, what's the blast radius? How do you limit it?
19. How do you audit and log all access to sensitive KV keys?
20. What's the risk of storing JWT secrets in Workers environment, and how do you mitigate?
21. How would you implement IP allowlisting that updates dynamically?

## DX / Maintainability

22. How do you write tests for a Worker that depends on KV, DO, R2, and Queue bindings?
23. What's your strategy for sharing code between 10 Workers in a monorepo?
24. How do you debug a production issue when `console.log` is ephemeral?
25. What's the ideal branching and deployment strategy for Workers?
26. How do you manage Durable Object migrations without losing data?
27. What's the best way to handle breaking API changes in a deployed Worker?
28. How do you ensure TypeScript types stay in sync with wrangler.jsonc bindings?

## Cost

29. At what request volume does Workers become cheaper than AWS Lambda? Than a VPS?
30. Which operations are "free" and which cost money? How do you minimize paid operations?
31. If you accidentally deploy a Worker with an infinite loop, what's the financial impact?
32. What's cheaper: caching in KV or caching via Cache API? When does each make sense?
33. How do you set up billing alerts for unexpected traffic spikes?
34. What's the true cost of Durable Objects at scale (1M DOs, each with 10KB storage)?

## Reliability

35. What happens to in-flight requests during a Worker deployment?
36. If a Queue consumer Worker fails, what happens to the messages?
37. How do you implement graceful degradation when KV is slower than expected?
38. What's your monitoring strategy to catch 99th percentile latency spikes?
39. How do you implement a health check endpoint that validates all bindings?
40. What data should NOT live in a Durable Object?

## Product Trade-offs

41. When should you use Workers AI vs. calling OpenAI directly?
42. At what point should you move logic out of Workers into a traditional backend?
43. How do you decide between Cloudflare's D1 vs. Neon Postgres vs. PlanetScale?
44. Should you use Cloudflare's ecosystem exclusively, or mix with AWS/GCP?
45. When is it worth paying for Cloudflare Enterprise features vs. building yourself?
46. How do you evaluate the risk of vendor lock-in with Durable Objects?
47. When should you choose Queues vs. external Kafka/SQS vs. simple `waitUntil()`?

---

# 7. Personalized Recommendations

## 7.1 Most Useful Patterns for Your Stack

Given your React / Next.js / Astro / static files background:

| Pattern | Why It's Useful for You |
|---|---|
| **Worker + Static Assets (SPA)** | Deploy your React app as static files + Worker for API — replaces Vercel |
| **API proxy with caching** | Replace Next.js API routes that proxy third-party APIs |
| **HTMLRewriter for personalization** | Add dynamic content to your static Astro/Next.js pages at the edge |
| **Hono-based API** | Feels like Express/Next.js API routes — lowest learning curve |
| **KV for feature flags** | Replace LaunchDarkly / PostHog feature flag with zero-latency edge reads |
| **Queue for async processing** | Webhook handlers, email sending, analytics — offload from response path |
| **R2 for file storage** | Replace S3 with zero egress fees — perfect for user uploads, assets |

## 7.2 Learning Priority Order

1. **Week 1:** Basic Worker (fetch handler, routing, responses)
2. **Week 1:** `wrangler dev` + deploy workflow
3. **Week 2:** Hono framework (your Express replacement)
4. **Week 2:** Environment variables + secrets
5. **Week 3:** KV (sessions, caching, feature flags)
6. **Week 3:** Cache API
7. **Week 4:** R2 (file storage)
8. **Month 2:** Durable Objects
9. **Month 2:** Queues
10. **Month 2:** D1
11. **Month 3:** Multi-worker architecture + Service Bindings
12. **Month 3:** CI/CD, monitoring, production hardening

## 7.3 Ideal Practice Projects

| Week | Project | Skills |
|---|---|---|
| 1 | URL shortener | KV, routing, redirects |
| 2 | Personal API (portfolio data + GitHub proxy) | Hono, fetch, Cache API |
| 3 | Blog with Astro + CF Workers adapter | Astro SSR on Workers, KV |
| 4 | File sharing app | R2, presigned URLs, auth |
| 5-6 | Real-time poll/voting app | Durable Objects, WebSocket |
| 7-8 | Webhook processing pipeline | Queues, R2, error handling |

## 7.4 Common Mistakes Frontend Engineers Make

1. **Thinking in client-server, not edge** — Workers run BETWEEN client and server. You're programming the network, not a server.

2. **Trying to use npm packages that need Node.js** — Many npm packages use `fs`, `path`, `net`, etc. Check compatibility or use `nodejs_compat` flag.

3. **Buffering entire responses in memory** — In React you think in objects. Workers think in streams. A 50MB response will kill your Worker.

4. **Overusing global state** — Unlike a React component that re-renders, Worker globals persist across requests in the same isolate. This causes subtle bugs.

5. **Not understanding eventual consistency** — KV is eventually consistent. If you write then immediately read in another region, you might get stale data. This doesn't happen in traditional backends.

6. **Building everything in one Worker** — Coming from Next.js where everything is in one app. Workers should be small and composed via Service Bindings.

7. **Ignoring `waitUntil()`** — Coming from Express where you just `res.send()` and keep processing. In Workers, once you return a Response, the isolate may be killed. Use `ctx.waitUntil()` for fire-and-forget tasks.

8. **Using `process.env` out of habit** — There is no `process` in Workers. Environment is injected via the `env` parameter.

## 7.5 30-Day Learning Plan

### Week 1: Foundations
| Day | Task | Deliverable |
|---|---|---|
| 1 | Install Wrangler, create Hello World, deploy | Live Worker on workers.dev |
| 2 | Explore `request.cf`, URL routing, response types | Worker that responds differently per path |
| 3 | Build a JSON API proxy (fetch external API) | Working proxy Worker |
| 4 | Learn Cache API, add caching to proxy | Cached proxy with headers |
| 5 | Learn environment variables + secrets | Configured Worker with secrets |
| 6 | Build URL shortener with KV | Working URL shortener |
| 7 | Review, refactor, read Cloudflare docs on limits | Clean code, notes on gotchas |

### Week 2: Real Framework
| Day | Task | Deliverable |
|---|---|---|
| 8 | Set up Hono, recreate all routes | Hono-based Worker |
| 9 | Add middleware (CORS, auth, logging) | Production-like middleware stack |
| 10 | Build CRUD API with KV as storage | Working REST API |
| 11 | Add input validation (Zod) + error handling | Robust error responses |
| 12 | Write tests with Vitest + Workers pool | Test suite passing |
| 13 | Set up CI/CD with GitHub Actions | Auto-deploy on push |
| 14 | Deploy with staging + production environments | Multi-env setup |

### Week 3: Storage Deep-Dive
| Day | Task | Deliverable |
|---|---|---|
| 15 | R2: Build a file upload/download API | Working file storage |
| 16 | R2: Add presigned URLs for large uploads | Client-side upload flow |
| 17 | D1: Create a database, run SQL queries | Working D1 queries |
| 18 | D1: Build a simple blog API (CRUD posts) | Blog API with SQL |
| 19 | Durable Objects: Build a counter | First DO working |
| 20 | Durable Objects: Build a rate limiter | DO-based rate limiting |
| 21 | Compare all storage options, write decision guide | Personal cheatsheet |

### Week 4: Advanced Patterns
| Day | Task | Deliverable |
|---|---|---|
| 22 | Queues: Build a webhook receiver → processor | Queue pipeline working |
| 23 | Queues: Add dead-letter queue + monitoring | Reliable queue system |
| 24 | Deploy Astro site on Workers | Astro SSR on CF |
| 25 | Add HTMLRewriter personalization to static site | Dynamic edge content |
| 26 | Multi-Worker: Build gateway + 2 service Workers | Service Bindings working |
| 27 | Add observability (logs, traces, tail) | Monitoring setup |
| 28 | Cron Triggers: Build a scheduled cleanup job | Cron Worker running |
| 29 | Performance audit: measure latency, optimize | P50/P99 benchmarks |
| 30 | Write architecture doc for a real project idea | Architecture diagram + plan |

---

# 8. Summary & Next Steps

## Summary

- **Workers are edge-first serverless functions** running on V8 isolates across 300+ global locations.
- **They are NOT Node.js** — they use Web Standard APIs with optional `nodejs_compat`.
- **Core primitives:** KV (cache), R2 (files), D1 (SQL), DO (state), Queues (async), Cron (scheduled).
- **Best mental model for you:** Think of Workers as **Next.js Edge Runtime, detached from Next.js**, with access to Cloudflare's storage/compute primitives.
- **Start with Hono** — it gives you the Express/Next.js API route ergonomics on Workers.
- **Think in streams, not buffers.** Think in eventual consistency, not immediate.
- **Use the right storage for the job** — KV for reads, DO for consistency, R2 for files, D1 for queries.

## Next Steps (After 30 Days)

1. **Build a real project** — Take something you'd normally build with Next.js and build it purely on Workers
2. **Explore Workflows** — Cloudflare's durable execution for multi-step background jobs
3. **Try Workers AI** — Run ML models at the edge
4. **Explore Hyperdrive** — Connection pooling for your existing Postgres/MySQL
5. **Learn Terraform/Pulumi for CF** — Infrastructure as code for complex deployments
6. **Study the Cloudflare blog** — Engineering posts explain real-world patterns
7. **Join the Cloudflare Discord** — Active community for Workers questions

## Advanced Topics to Continue Learning

| Topic | Why |
|---|---|
| **WebSocket Hibernation** | Build efficient real-time apps without DO cost when idle |
| **Workers for Platforms** | Build platforms where YOUR users deploy Workers (like Shopify) |
| **Smart Placement** | Optimize Worker location relative to your backend |
| **Cloudflare Containers** | Run containers at the edge for heavier workloads |
| **Vectorize + Workers AI** | Build RAG/AI search at the edge |
| **mTLS + Access** | Zero-trust security between Workers and origins |
| **Tail Workers** | Process logs from other Workers (observability pipeline) |
| **Trace Workers** | Custom tracing across Service Bindings |
| **DO WebSocket + SQLite** | Each DO instance gets its own SQLite database |
| **Gradual Deployments** | `wrangler versions deploy` for canary/blue-green releases |

---

> **Remember:** The best way to learn Workers is to replace one thing you currently do in Next.js/Astro with a Worker. Start small, ship often, and expand from there.
