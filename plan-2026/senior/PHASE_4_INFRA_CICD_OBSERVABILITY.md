# Phase 4 — Deep Dive: Infra, CI/CD + Observability

> **Duration:** 10–14 months (parallel tracks) **Goal:** Own a full deploy pipeline. Instrument it end-to-end. Drive technical decisions around deployment and flag strategy.

---

## Table of Contents

### Craft Track

1. [Docker + Container Basics](https://claude.ai/chat/66caa6a7-7c60-4209-93d6-c254a560cf68#1-docker--container-basics)
2. [GitHub Actions / CI Pipelines](https://claude.ai/chat/66caa6a7-7c60-4209-93d6-c254a560cf68#2-github-actions--ci-pipelines)
3. [Feature Flags — Deep Focus](https://claude.ai/chat/66caa6a7-7c60-4209-93d6-c254a560cf68#3-feature-flags--deep-focus)
4. [Deployment Strategies — Deep Focus](https://claude.ai/chat/66caa6a7-7c60-4209-93d6-c254a560cf68#4-deployment-strategies--deep-focus)
5. [Error Tracking — Sentry + RUM](https://claude.ai/chat/66caa6a7-7c60-4209-93d6-c254a560cf68#5-error-tracking--sentry--rum)
6. [Performance Budgets + Alerting](https://claude.ai/chat/66caa6a7-7c60-4209-93d6-c254a560cf68#6-performance-budgets--alerting)
7. [Security — CSP, XSS, CSRF, CORS](https://claude.ai/chat/66caa6a7-7c60-4209-93d6-c254a560cf68#7-security--csp-xss-csrf-cors)

### Interview Track

8. [Behavioral / Leadership — STAR Method](https://claude.ai/chat/66caa6a7-7c60-4209-93d6-c254a560cf68#8-behavioral--leadership--star-method)
9. [System Design — Feature Flag Service](https://claude.ai/chat/66caa6a7-7c60-4209-93d6-c254a560cf68#9-system-design--feature-flag-service)
10. [System Design — CI/CD Pipeline for a Frontend App](https://claude.ai/chat/66caa6a7-7c60-4209-93d6-c254a560cf68#10-system-design--cicd-pipeline-for-a-frontend-app)

---

# CRAFT TRACK

---

## 1. Docker + Container Basics

### Why a frontend engineer needs this

At FAANG, frontend engineers own their service end-to-end. You write the code, you define the container, you own the deploy. Not knowing Docker means you depend on a platform engineer for every environment change — a signal of limited scope.

---

### 1.1 The Mental Model

```
Physical machine
  └── OS (Linux)
        └── Docker Engine (runtime)
              ├── Container A (Node 20, your app)
              ├── Container B (Nginx, reverse proxy)
              └── Container C (Redis, cache)
```

A **container** is an isolated process with its own filesystem, network, and process space — but it shares the host OS kernel. Unlike a VM, no full OS is duplicated. This is why containers start in milliseconds and VMs take minutes.

An **image** is the blueprint. A **container** is the running instance. Same relationship as class → instance.

---

### 1.2 Dockerfile for a Next.js App

```dockerfile
# Stage 1: Install dependencies
FROM node:20-alpine AS deps
WORKDIR /app

# Copy only manifests first — layer caching
# If package.json doesn't change, this layer is cached
COPY package.json package-lock.json ./
RUN npm ci --frozen-lockfile

# Stage 2: Build
FROM node:20-alpine AS builder
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .

# Build args for environment — not secrets
ARG NEXT_PUBLIC_API_URL
ENV NEXT_PUBLIC_API_URL=$NEXT_PUBLIC_API_URL

RUN npm run build

# Stage 3: Production image (smallest possible)
FROM node:20-alpine AS runner
WORKDIR /app

ENV NODE_ENV=production

# Don't run as root — security best practice
RUN addgroup --system --gid 1001 nodejs
RUN adduser  --system --uid 1001 nextjs

# Copy only what's needed to run
COPY --from=builder /app/public ./public
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static

USER nextjs
EXPOSE 3000
ENV PORT 3000

CMD ["node", "server.js"]
```

**Multi-stage build rationale:**

- Stage 1 installs all deps (including devDependencies)
- Stage 2 builds the app
- Stage 3 copies only production artifacts — no `node_modules`, no source

Final image: ~150MB instead of ~1.5GB for a naive single-stage build.

---

### 1.3 Layer Caching — The Key Optimization

Docker rebuilds from the first changed instruction downward. Order instructions from least-to-most likely to change:

```dockerfile
# WRONG order — code change invalidates npm install
COPY . .                    # any source change = cache miss here
RUN npm ci                  # always re-runs even if package.json unchanged

# CORRECT order — code change doesn't invalidate npm install
COPY package.json package-lock.json ./   # only changes when deps change
RUN npm ci                               # cached unless deps change
COPY . .                                 # source changes here, after install
RUN npm run build
```

---

### 1.4 docker-compose for Local Dev

```yaml
# docker-compose.yml
version: '3.8'

services:
  app:
    build:
      context: .
      target: builder        # use builder stage for dev (has devDeps)
    ports:
      - "3000:3000"
    volumes:
      - .:/app               # mount source for hot reload
      - /app/node_modules    # anonymous volume — don't override container's node_modules
    environment:
      - NODE_ENV=development
      - API_URL=http://api:4000
    depends_on:
      - api
      - redis

  api:
    image: my-api:latest
    ports:
      - "4000:4000"

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
```

---

### 1.5 Interview Questions

**Q: What's the difference between a Docker image and a container?** A: Image is the immutable blueprint (filesystem layers). Container is a running instance of that image — an isolated process. Multiple containers can run from the same image simultaneously.

**Q: What is a multi-stage build and why use it?** A: Multiple `FROM` statements in one Dockerfile. Each stage can copy artifacts from previous stages. Lets you build with full tooling but ship only production artifacts — dramatically smaller final image, no source code or dev dependencies exposed.

**Q: Why does instruction order in a Dockerfile matter?** A: Docker caches each layer. A change invalidates that layer and all subsequent ones. Copy dependency manifests and install before copying source — so source changes don't trigger reinstalls.

---

## 2. GitHub Actions / CI Pipelines

### 2.1 Core Concepts

```
Workflow    — YAML file in .github/workflows/
  Job       — runs on a single machine (runner)
    Step    — individual command or action
```

Jobs run in **parallel** by default. Use `needs:` to sequence them. Steps within a job run **sequentially**.

---

### 2.2 Production-Grade Frontend CI Pipeline

```yaml
# .github/workflows/ci.yml
name: CI

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

env:
  NODE_VERSION: '20'
  TURBO_TOKEN: ${{ secrets.TURBO_TOKEN }}  # remote cache auth
  TURBO_TEAM:  ${{ vars.TURBO_TEAM }}

jobs:
  # ─── Fast checks first — fail fast ───────────────────────────────────────
  lint-typecheck:
    name: Lint + Typecheck
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0  # needed for Turbo affected computation

      - uses: actions/setup-node@v4
        with:
          node-version: ${{ env.NODE_VERSION }}
          cache: 'npm'

      - run: npm ci --frozen-lockfile

      - name: Lint
        run: npx turbo run lint --filter=[HEAD^1]  # only changed packages

      - name: Typecheck
        run: npx turbo run typecheck --filter=[HEAD^1]

  # ─── Tests ───────────────────────────────────────────────────────────────
  test:
    name: Test
    runs-on: ubuntu-latest
    needs: lint-typecheck  # only run if lint passes
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - uses: actions/setup-node@v4
        with:
          node-version: ${{ env.NODE_VERSION }}
          cache: 'npm'

      - run: npm ci --frozen-lockfile

      - name: Unit + Integration Tests
        run: npx turbo run test --filter=[HEAD^1]
        env:
          CI: true

      - name: Upload coverage
        uses: codecov/codecov-action@v4
        with:
          token: ${{ secrets.CODECOV_TOKEN }}

  # ─── Build ───────────────────────────────────────────────────────────────
  build:
    name: Build
    runs-on: ubuntu-latest
    needs: lint-typecheck
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: ${{ env.NODE_VERSION }}
          cache: 'npm'
      - run: npm ci --frozen-lockfile

      - name: Build
        run: npx turbo run build
        env:
          NEXT_PUBLIC_API_URL: ${{ vars.API_URL }}

      - name: Bundle size check
        run: npx bundlesize  # fails if bundles exceed budget

      - name: Upload build artifact
        uses: actions/upload-artifact@v4
        with:
          name: build-output
          path: apps/web/.next
          retention-days: 1

  # ─── E2E Tests ───────────────────────────────────────────────────────────
  e2e:
    name: E2E Tests
    runs-on: ubuntu-latest
    needs: build
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: ${{ env.NODE_VERSION }}
          cache: 'npm'
      - run: npm ci --frozen-lockfile

      - name: Download build
        uses: actions/download-artifact@v4
        with:
          name: build-output
          path: apps/web/.next

      - name: Install Playwright
        run: npx playwright install --with-deps chromium

      - name: Run E2E
        run: npx playwright test
        env:
          BASE_URL: http://localhost:3000

      - name: Upload Playwright report
        if: failure()
        uses: actions/upload-artifact@v4
        with:
          name: playwright-report
          path: playwright-report/

  # ─── Deploy (main branch only) ───────────────────────────────────────────
  deploy:
    name: Deploy to Production
    runs-on: ubuntu-latest
    needs: [test, e2e]
    if: github.ref == 'refs/heads/main'
    environment: production  # requires manual approval if configured
    steps:
      - uses: actions/checkout@v4
      - name: Deploy
        run: ./scripts/deploy.sh
        env:
          DEPLOY_TOKEN: ${{ secrets.DEPLOY_TOKEN }}
```

---

### 2.3 Reusable Workflows

```yaml
# .github/workflows/_setup.yml (reusable)
on:
  workflow_call:
    inputs:
      node-version:
        type: string
        default: '20'

jobs:
  setup:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: ${{ inputs.node-version }}
          cache: 'npm'
      - run: npm ci --frozen-lockfile

# Consumer workflow
jobs:
  test:
    uses: ./.github/workflows/_setup.yml
    with:
      node-version: '20'
```

---

### 2.4 Secrets vs Variables

```
secrets.*  — encrypted, never logged, not available in PRs from forks
             Use for: API keys, tokens, passwords

vars.*     — plaintext, logged, available everywhere
             Use for: URLs, feature names, non-sensitive config
```

---

### 2.5 Interview Questions

**Q: How do you prevent a slow E2E suite from blocking every PR?** A: Run E2E only on main branch merges or nightly, not on every PR. For PRs, run only tests affected by changed files (Turbo/Nx affected). Use sharding to parallelize across runners: `npx playwright test --shard=1/4`.

**Q: How do you handle secrets in CI without exposing them in logs?** A: GitHub Actions automatically masks `secrets.*` values in logs. Never echo secrets directly. Use environment variables passed to commands, not inline values. For third-party actions, pin to commit SHA (not tag) to prevent supply chain attacks.

**Q: What's the difference between `needs` and `if` in GitHub Actions?** A: `needs` defines job dependency (sequential execution — B runs after A). `if` is a condition expression (B only runs if condition is true). Combined: `needs: [build], if: github.ref == 'refs/heads/main'` means "run only on main, after build succeeds."

---

## 3. Feature Flags — Deep Focus

### What they are

Feature flags (also called feature toggles) decouple **code deployment** from **feature release**. Code ships to production behind a flag. The flag controls who sees what, without a new deployment.

```
Without flags:   deploy = release (coupled, risky)
With flags:      deploy ≠ release (decoupled, safe)
```

---

### 3.1 The Four Types of Feature Flags

```
Type            Lifespan    Purpose
─────────────────────────────────────────────────────────────────────
Release toggle  Short       Hide incomplete work. Merged to main, off in prod.
Experiment      Medium      A/B test — different variants for different users.
Ops toggle      Long        Kill switch. Turn off expensive feature under load.
Permission      Permanent   Gate features by user role/plan (free vs premium).
```

Each type has different lifecycle management needs:

- Release toggles → delete after feature is fully rolled out (technical debt if left)
- Ops toggles → keep long-term but document clearly
- Permission flags → never delete, evolve with product

---

### 3.2 Architecture: Evaluation Models

**Client-side evaluation (CDN-delivered flags):**

```
User browser
  → fetch flags from CDN (fast, cached)
    → evaluate locally (no network per check)
      → render correct variant

Latency:   ~0ms after initial load
Staleness: stale until next poll/push
Risk:      flag values visible in JS bundle or network response
```

**Server-side evaluation:**

```
User browser
  → request to your server
    → server evaluates flags for this user
      → sends rendered response with correct variant

Latency:   adds to server response time
Staleness: fresh on every request
Risk:      no client exposure of flag logic
```

**Edge evaluation (best of both):**

```
User browser
  → request to edge node (Cloudflare Worker, Vercel Edge)
    → edge evaluates flags (near user, low latency)
      → returns personalized response

Latency:   ~5–30ms (edge is geographically close)
Staleness: fresh per request
Risk:      flag logic at edge, not client
```

---

### 3.3 Flag Evaluation SDK — React Integration

```typescript
// Feature flag context — wraps app with flag values
interface FlagContext {
  flags: Record<string, boolean | string | number>;
  isLoading: boolean;
}

const FlagContext = React.createContext<FlagContext>({ flags: {}, isLoading: true });

// Provider — fetches and polls flags
function FlagProvider({ userId, children }: { userId: string; children: React.ReactNode }) {
  const [flags, setFlags]       = useState<Record<string, unknown>>({});
  const [isLoading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchFlags() {
      const response = await fetch(`/api/flags?userId=${userId}`);
      const data     = await response.json();
      setFlags(data);
      setLoading(false);
    }

    fetchFlags();

    // Poll every 30s for flag updates without full redeploy
    const interval = setInterval(fetchFlags, 30_000);
    return () => clearInterval(interval);
  }, [userId]);

  return (
    <FlagContext.Provider value={{ flags, isLoading }}>
      {children}
    </FlagContext.Provider>
  );
}

// Hook — type-safe flag access
function useFlag<T extends boolean | string | number>(
  key:          string,
  defaultValue: T
): T {
  const { flags } = useContext(FlagContext);
  return (flags[key] as T) ?? defaultValue;
}

// Usage
function CheckoutButton() {
  const newCheckoutEnabled = useFlag('checkout_v2', false);
  return newCheckoutEnabled ? <CheckoutV2 /> : <CheckoutV1 />;
}
```

---

### 3.4 Gradual Rollout — Percentage-Based Targeting

The core mechanism behind safe releases:

```typescript
// Deterministic hash — same user always gets same variant
function getUserBucket(userId: string, flagKey: string): number {
  // Combine userId + flagKey to avoid all flags rolling out to same users
  const input = `${userId}:${flagKey}`;
  let hash    = 0;
  for (let i = 0; i < input.length; i++) {
    hash = ((hash << 5) - hash) + input.charCodeAt(i);
    hash |= 0; // convert to 32-bit integer
  }
  // Return 0–99 bucket
  return Math.abs(hash) % 100;
}

interface RolloutRule {
  percentage:  number;              // 0–100
  targetGroups?: string[];          // optional: only beta users
  targetRegions?: string[];         // optional: only US users
}

function evaluateFlag(
  userId:    string,
  userGroups: string[],
  userRegion: string,
  flagKey:   string,
  rule:      RolloutRule
): boolean {
  // Check targeting rules first
  if (rule.targetGroups && !rule.targetGroups.some(g => userGroups.includes(g))) {
    return false;
  }
  if (rule.targetRegions && !rule.targetRegions.includes(userRegion)) {
    return false;
  }

  // Percentage rollout
  const bucket = getUserBucket(userId, flagKey);
  return bucket < rule.percentage;
}

// Examples:
// 0%   → nobody sees it (flag off)
// 5%   → internal testing (roughly 5% of users)
// 25%  → quarter rollout
// 100% → everyone (flag effectively on, cleanup time)
```

---

### 3.5 A/B Testing with Flags

```typescript
type Variant = 'control' | 'treatment_a' | 'treatment_b';

function getVariant(userId: string, experimentKey: string): Variant {
  const bucket = getUserBucket(userId, experimentKey);

  if (bucket < 33)  return 'control';
  if (bucket < 66)  return 'treatment_a';
  return 'treatment_b';
}

// React hook with analytics tracking
function useExperiment(experimentKey: string): Variant {
  const { userId } = useAuthStore();
  const variant    = getVariant(userId, experimentKey);

  useEffect(() => {
    // Track exposure — needed to calculate experiment results correctly
    analytics.track('experiment_exposure', {
      experiment: experimentKey,
      variant,
      userId,
    });
  }, [experimentKey, variant, userId]);

  return variant;
}

// Usage
function PricingPage() {
  const variant = useExperiment('pricing_layout_2024');

  return {
    control:     <PricingV1 />,
    treatment_a: <PricingV2Annual />,
    treatment_b: <PricingV2Monthly />,
  }[variant];
}
```

---

### 3.6 Ops Toggles — Kill Switches

The most critical flag type at FAANG scale. When a feature causes an incident, you kill it in seconds without a deploy:

```typescript
// Kill switch pattern — disable expensive feature under load
function useKillSwitch(featureKey: string) {
  const isKilled = useFlag(`kill_${featureKey}`, false);
  return isKilled;
}

function RecommendationEngine() {
  const isKilled = useKillSwitch('recommendations');

  if (isKilled) {
    // Fallback — simple chronological feed, no ML inference
    return <ChronologicalFeed />;
  }

  return <MLRecommendedFeed />;
}
```

**Ops toggle contract:**

- Flag name convention: `kill_<feature>` or `disable_<feature>`
- Default value: `false` (feature ON) — so flag service outage doesn't kill features
- On: feature disabled (kill switch activated)
- Document every ops toggle: who can toggle, what the fallback does, SLA

---

### 3.7 Flag Hygiene — Technical Debt Prevention

The biggest operational problem with feature flags is accumulation. Flags that stay in code after 100% rollout become dead branches — they confuse engineers and bloat code.

```typescript
// Track flag age in your flag service
interface FlagMetadata {
  key:         string;
  type:        'release' | 'experiment' | 'ops' | 'permission';
  owner:       string;    // team that owns this flag
  createdAt:   Date;
  expiresAt?:  Date;      // set for release flags — when to delete
  rollout:     number;    // 0–100 current percentage
  description: string;
}

// Flag cleanup checklist (run weekly):
// 1. Flags at 100% rollout for > 2 weeks → schedule deletion PR
// 2. Flags not evaluated in 30 days     → dead code, delete immediately
// 3. Flags older than expiry date        → alert owner
```

**Code pattern that makes cleanup easy:**

```typescript
// ❌ Hard to find and delete — flag check buried in component
function Product() {
  const flag = useFlag('new_images', false);
  return (
    <div>
      {flag ? <NewImageGallery /> : <OldImageGallery />}
    </div>
  );
}

// ✅ Flag clearly named and isolated — grep finds all usages easily
// When rolling out to 100%: delete flag + remove the `false` branch
const NEW_IMAGES_FLAG = 'product_image_gallery_v2';

function Product() {
  const showNewImages = useFlag(NEW_IMAGES_FLAG, false);
  return (
    <div>
      {showNewImages ? <ImageGalleryV2 /> : <ImageGalleryV1 />}
    </div>
  );
}
```

---

### 3.8 Flag Services — Build vs Buy

||LaunchDarkly|Unleash (OSS)|Growthbook|DIY (Redis/DB)|
|---|---|---|---|---|
|Evaluation|Client + server SDK|Client + server SDK|Client + server SDK|Your code|
|Targeting|Rich (segments, rules)|Rich|Rich + stats|You build|
|Analytics|Built-in|Basic|Built-in A/B stats|You build|
|Audit log|✅|✅|✅|You build|
|Edge eval|✅|❌|❌|You build|
|Cost|High ($)|Free (self-host)|Free tier|Infra cost|
|FAANG choice|Common|Common|Less common|Rare at scale|

**Recommendation for side projects:** Growthbook (free, has A/B stats). **Production at scale:** LaunchDarkly (ecosystem, SDKs, audit) or Unleash (self-hosted, no vendor lock-in).

---

### 3.9 Interview Questions

**Q: What is a feature flag and why use it instead of just deploying when ready?** A: Flags decouple deploy from release. Code merges continuously (reducing merge conflict debt), but features activate via configuration. Benefits: gradual rollout to catch bugs early, instant rollback without redeploy, A/B testing without separate deployments.

**Q: How do you ensure the same user always gets the same variant in an A/B test?** A: Deterministic hashing — hash the userId + experimentKey to a bucket (0–99). Same input always produces the same bucket. Including the experimentKey in the hash prevents all experiments from assigning the same users to treatment.

**Q: What is an ops toggle and what should its default value be?** A: A long-lived kill switch to disable a feature under incident conditions. Default must be `false` (feature ON) — if the flag service goes down, features stay on. The kill switch only activates when an engineer explicitly flips it.

**Q: How do you prevent feature flag technical debt from accumulating?** A: Set expiry dates on release flags at creation. Track flags by type (release, ops, experiment, permission). Alert owners when flags are at 100% rollout for more than N days. Use consistent naming conventions so flags are easy to grep and delete.

**Q: What is the risk of client-side flag evaluation?** A: Flag configuration is exposed in the browser — users can see all flag keys and values, including flags for unreleased features. Motivated users can flip flags manually. For experiments with business-sensitive targeting rules, evaluate server-side or at the edge.

**Q: How does percentage rollout work at the implementation level?** A: Hash the userId to a deterministic 0–99 bucket. If bucket < rolloutPercentage, the user is in. This is sticky (same user always same bucket), consistent across sessions, and requires no database — it's a pure function.

---

## 4. Deployment Strategies — Deep Focus

### The core problem

Every deployment carries risk. Deployment strategies are techniques to reduce blast radius — limiting how many users are affected if something goes wrong, and how quickly you can recover.

```
Risk formula:    Risk = Probability of failure × Number of affected users
Strategy goal:   Minimize both factors simultaneously
```

---

### 4.1 The Deployment Strategy Spectrum

```
←─────────────────────────────────────────────────────────────────►
Safest                                                         Fastest
(lowest blast radius)                                    (simplest to implement)

Blue/Green → Canary → Rolling → Feature Flag → Big Bang
```

---

### 4.2 Big Bang Deployment (Recreate)

The baseline — stop old version, start new version, everyone switches simultaneously.

```
v1 running (100% traffic)
  → v1 stopped
    → v2 started (100% traffic)

Downtime: YES (gap between stop and start)
Rollback: redeploy v1 (slow)
Use case: dev/staging environments, non-production
```

```yaml
# Kubernetes — Recreate strategy
spec:
  strategy:
    type: Recreate  # kill all v1 pods before starting v2
```

**Never use in production** unless downtime is acceptable (internal tools, batch jobs).

---

### 4.3 Rolling Deployment

Replace instances gradually. At any point, some instances run v1 and some run v2.

```
Start: [v1][v1][v1][v1]  (4 pods)
Step1: [v2][v1][v1][v1]  (1 updated, 3 old)
Step2: [v2][v2][v1][v1]  (2 updated, 2 old)
Step3: [v2][v2][v2][v1]  (3 updated, 1 old)
Done:  [v2][v2][v2][v2]  (all updated)
```

```yaml
# Kubernetes — Rolling strategy
spec:
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge:       1  # max pods above desired count during update
      maxUnavailable: 0  # min available pods (0 = no downtime)
```

**Implication for frontend apps:** During rollout, users may get v1 HTML but v2 JS bundle (or vice versa). Your API must be backward-compatible with both versions simultaneously — **never make breaking API changes without versioning first**.

```
Risk: mixed versions serving traffic simultaneously
Rollback: slow — roll forward (deploy v1 again as v3)
Use case: stateless services, APIs with backward compatibility
```

---

### 4.4 Blue/Green Deployment

Two identical environments. Switch traffic atomically from blue (current) to green (new).

```
Blue (v1):  LIVE — 100% traffic
Green (v2): IDLE — deploy and test here

After testing passes:
  Load balancer: route 100% → Green
  Blue stays running (instant rollback target)

Blue (v1):  IDLE (rollback target, keep for 24h)
Green (v2): LIVE — 100% traffic
```

```typescript
// Conceptual load balancer config switch
// AWS ALB target group swap
const albClient = new ElasticLoadBalancingV2Client({});

await albClient.send(new ModifyListenerCommand({
  ListenerArn: LISTENER_ARN,
  DefaultActions: [{
    Type: 'forward',
    TargetGroupArn: GREEN_TARGET_GROUP_ARN,  // switch here
  }],
}));
```

```
Risk:       100% of users hit new version at once — but environment tested first
Rollback:   instant (flip LB back to blue)
Cost:       double infrastructure during deployment
Use case:   databases, stateful services, when rollback speed is critical
```

**The DB migration problem with blue/green:**

```
Challenge: v2 requires a schema change (new column)

WRONG:
  1. Run migration (add column NOT NULL)
  2. Deploy v2
  → v1 still running during step 2 — breaks on new column

CORRECT (expand-contract pattern):
  Phase 1 — Expand:
    1. Add column as NULL (v1 ignores it, v2 writes to it)
    2. Deploy v2
  Phase 2 — Backfill:
    3. Backfill NULL values
  Phase 3 — Contract:
    4. Add NOT NULL constraint
    5. v1 can now be decommissioned
```

---

### 4.5 Canary Deployment — The FAANG Standard

Route a small percentage of real traffic to the new version. Monitor. Expand if metrics are healthy. Roll back if degraded.

```
                    ┌──────────────────┐
                    │   Load Balancer  │
                    └────────┬─────────┘
                             │
               ┌─────────────┴─────────────┐
               │ 95%                   5%   │
               ▼                           ▼
    ┌──────────────────┐       ┌──────────────────┐
    │   v1 (stable)    │       │   v2 (canary)    │
    │   many pods      │       │   1–2 pods       │
    └──────────────────┘       └──────────────────┘
```

**Canary progression:**

```
0% → 1% (internal traffic) → 5% → 10% → 25% → 50% → 100%

At each step:
  - Monitor error rate, latency p50/p95/p99, CPU, business metrics
  - Automatic rollback if thresholds breached
  - Dwell time at each step (e.g., 10 minutes before expanding)
```

**Kubernetes canary with Argo Rollouts:**

```yaml
apiVersion: argoproj.io/v1alpha1
kind: Rollout
metadata:
  name: web-app
spec:
  strategy:
    canary:
      steps:
        - setWeight: 5       # 5% canary
        - pause: { duration: 10m }  # observe 10 minutes
        - analysis:
            templates:
              - templateName: error-rate-check
        - setWeight: 25
        - pause: { duration: 10m }
        - setWeight: 50
        - pause: { duration: 10m }
        - setWeight: 100     # full rollout

      # Automatic rollback if analysis fails
      autoRollback:
        enabled: true
```

**Analysis template — automated gate:**

```yaml
apiVersion: argoproj.io/v1alpha1
kind: AnalysisTemplate
metadata:
  name: error-rate-check
spec:
  metrics:
    - name: error-rate
      interval: 1m
      failureLimit: 3
      provider:
        prometheus:
          address: http://prometheus:9090
          query: |
            sum(rate(http_requests_total{status=~"5..",version="v2"}[5m]))
            /
            sum(rate(http_requests_total{version="v2"}[5m]))
      successCondition: result[0] < 0.01  # < 1% error rate
```

---

### 4.6 Canary vs Feature Flags — The Critical Distinction

This is a common interview trap. They look similar but solve different problems:

```
                  Canary Deployment         Feature Flag
─────────────────────────────────────────────────────────────────────
What switches?    Infrastructure            Code path
Who controls?     Traffic percentage        User targeting rules
Granularity       All users at that %       Specific users/segments
Rollback          Re-route traffic          Flip flag value
Persistence       Temporary (during deploy) Permanent (until cleanup)
Use case          Deploy safety             Release control
Latency           Infrastructure change     Milliseconds
Can target user?  No (random 5%)           Yes (beta users, region, plan)
```

**The most powerful combination:**

```
1. Canary deployment: route 5% of traffic to new pods
2. Feature flag (inside those pods): only show new feature to beta users

Result: Only beta users on the canary get the new UI
        Everyone else on the canary still gets the old UI
```

---

### 4.7 Shadow Deployment

New version receives copies of production traffic but its responses are discarded. Used to test performance and correctness without user impact.

```
Request → Production (v1) → Response to user
        ↘ Shadow (v2)     → Response discarded, metrics captured
```

```
Use case:  Test a new ML model, a rewritten service, a new DB
Risk:      Zero to users (responses never shown)
Cost:      Double the compute during shadow period
Limitation: Side effects (writes) must be carefully managed
```

---

### 4.8 Immutable Deployments + Artifact Promotion

The modern standard: build once, promote the same artifact through environments.

```
Build → artifact:sha-abc123
          ↓
        dev (auto-promoted)
          ↓
        staging (auto-promoted after tests pass)
          ↓
        production (manual approval gate)
```

```
Why immutable?
  - What you tested in staging is exactly what ships to prod
  - No "it worked in staging because we rebuilt" bugs
  - Full audit trail (git SHA → artifact → deployed env)
```

```yaml
# GitHub Actions — promote existing artifact, don't rebuild
jobs:
  deploy-prod:
    environment:
      name: production
      url: https://app.example.com
    steps:
      - name: Promote artifact to prod
        run: |
          # Pull the exact image built in CI (by SHA)
          docker pull registry.example.com/app:${{ github.sha }}
          # Tag as production and push
          docker tag  registry.example.com/app:${{ github.sha }} \
                      registry.example.com/app:production
          docker push registry.example.com/app:production
```

---

### 4.9 Static Frontend Deployment — CDN Strategy

Frontend apps are different from services — they're static files. Deployment = invalidating CDN cache + uploading new files.

```
Deployment sequence (critical order):

1. Upload new JS/CSS (with content hashes in filenames)
   → app.abc123.js (new), app.xyz789.js (old, still there)
   → No cache invalidation needed — new filename = no conflict

2. Upload new HTML (no hash — must be invalidated)
   → index.html points to app.abc123.js
   → Invalidate CDN cache for index.html ONLY

3. Old users finish their sessions with old JS
   → Old JS files still on CDN (not deleted yet)
   → Delete old files after N hours (safe window)
```

```typescript
// AWS CloudFront invalidation after deploy
const client = new CloudFrontClient({});

await client.send(new CreateInvalidationCommand({
  DistributionId: DISTRIBUTION_ID,
  InvalidationBatch: {
    CallerReference: Date.now().toString(),
    Paths: {
      Quantity: 1,
      Items: ['/index.html'],  // only invalidate HTML, not hashed assets
    },
  },
}));
```

---

### 4.10 Rollback Strategies

```
Strategy          Speed     Risk
───────────────────────────────────────────────
LB flip (Blue/Green)  Instant  Near zero
Flag flip             Instant  Near zero (feature flag rollback)
Re-deploy previous    Minutes  Low (same code as before)
Canary halt           Seconds  Low (only canary users affected so far)
DB rollback           Hours    High (data loss risk)
```

**Rollback decision tree:**

```
Incident detected
  → Is it a feature flag? Flip the flag → done
  → Is it in canary? Halt canary → done (5% affected)
  → Is it fully deployed?
      → No DB changes? Re-deploy previous image → done
      → DB changes? Assess data impact → forward fix (usually safer than DB rollback)
```

---

### 4.11 Deployment Checklist (Senior-Level Ownership)

```
Pre-deploy:
  □ Feature flags in place for new features (can kill without redeploy)
  □ DB migrations are backward-compatible (expand-contract)
  □ Rollback plan documented and tested
  □ Monitoring dashboards ready
  □ Runbook written for known failure modes

During deploy:
  □ Canary metrics healthy (error rate, latency, business KPIs)
  □ On-call engineer aware and available
  □ Deployment window (avoid Friday afternoons)

Post-deploy:
  □ Monitor for 30 minutes minimum
  □ Check real user metrics (not just synthetic)
  □ Update flag rollout percentage systematically
  □ Schedule flag cleanup tickets
```

---

### 4.12 Interview Questions

**Q: What is a canary deployment and how does it reduce risk?** A: Route a small percentage (1–5%) of real traffic to the new version while most users stay on the stable version. Monitor error rates and latency. If metrics degrade, roll back instantly by re-routing traffic. Blast radius is limited to the canary percentage.

**Q: What's the difference between a canary deployment and a feature flag?** A: Canary operates at the infrastructure level — traffic routing. Feature flags operate at the code level — which code path executes. Canary can't target specific users. Feature flags can. They're complementary: canary for deployment safety, flags for controlled release to specific user segments.

**Q: How do you handle database migrations in a blue/green deployment?** A: Use the expand-contract pattern. Phase 1 (expand): add new columns as nullable — both v1 and v2 work. Phase 2: deploy v2, backfill data. Phase 3 (contract): add constraints, remove old columns. This ensures zero downtime and zero breaking changes across both versions.

**Q: Why should static assets use content hashing, and what should be invalidated on CDN?** A: Hashed filenames (`app.abc123.js`) are cache-safe forever — different content = different filename = no conflict. Only `index.html` needs CDN invalidation because it's the entry point that references hashed files. This means deploys don't invalidate cached JS/CSS, making them faster and safer.

**Q: What is immutable deployment and why is it preferred?** A: Build the artifact once (Docker image, JS bundle), promote the same artifact through environments. What you tested in staging is exactly what goes to production — eliminating "works in staging" bugs. Git SHA traceability: every production deployment maps to an exact commit.

**Q: When is a rolling deployment risky, and how do you mitigate it?** A: During rollout, v1 and v2 serve traffic simultaneously. If v2 makes a breaking API change, v1 clients break. Mitigation: always make API changes backward-compatible — add fields, don't rename or remove. Use API versioning for breaking changes. Never break the protocol between client versions.

**Q: What's the order of operations for a zero-downtime static frontend deploy?** A: Upload new hashed JS/CSS first (no conflict — new filenames). Then upload new index.html and invalidate only its CDN cache. The new HTML references new hashed files. Old JS/CSS stays on CDN for in-progress user sessions. Delete old assets after a safe window.

---

## 5. Error Tracking — Sentry + RUM

### 5.1 Sentry Integration

```typescript
// _app.tsx — initialize once at app root
import * as Sentry from '@sentry/nextjs';

Sentry.init({
  dsn:              process.env.NEXT_PUBLIC_SENTRY_DSN,
  environment:      process.env.NODE_ENV,
  release:          process.env.NEXT_PUBLIC_VERCEL_GIT_COMMIT_SHA,

  // Sample rates — don't send everything (cost + noise)
  tracesSampleRate: 0.1,   // 10% of transactions
  replaysOnErrorSampleRate: 1.0,  // 100% of sessions with errors

  // Filter noise
  ignoreErrors: [
    'ResizeObserver loop limit exceeded',
    'Non-Error promise rejection captured',
    /^Network Error/,
  ],

  beforeSend(event) {
    // Strip PII before sending
    if (event.user?.email) {
      event.user.email = '[redacted]';
    }
    return event;
  },
});
```

**Error boundary with Sentry:**

```typescript
import { ErrorBoundary } from '@sentry/react';

function App() {
  return (
    <ErrorBoundary
      fallback={({ error, resetError }) => (
        <ErrorPage
          message="Something went wrong"
          onRetry={resetError}
        />
      )}
      onError={(error, info) => {
        // Additional context
        Sentry.setContext('component', { componentStack: info.componentStack });
      }}
    >
      <Router />
    </ErrorBoundary>
  );
}
```

**Source maps — critical for readable stack traces:**

```javascript
// sentry.config.js
const { withSentryConfig } = require('@sentry/nextjs');

module.exports = withSentryConfig(nextConfig, {
  silent: true,
  widenClientFileUpload: true,
  hideSourceMaps: true,  // don't expose source maps to public
  // Upload maps to Sentry, delete from bundle
});
```

---

### 5.2 Real User Monitoring (RUM)

RUM captures performance data from real user sessions — not synthetic lab tests.

```typescript
// web-vitals → your analytics
import { onCLS, onINP, onLCP, onFCP, onTTFB } from 'web-vitals';

function sendToRUM(metric: Metric) {
  // Segment by page, device, connection type
  const payload = {
    name:       metric.name,
    value:      metric.value,
    rating:     metric.rating,  // 'good' | 'needs-improvement' | 'poor'
    page:       window.location.pathname,
    deviceType: navigator.userAgent.includes('Mobile') ? 'mobile' : 'desktop',
    connection: (navigator as any).connection?.effectiveType,
  };

  // Use sendBeacon — doesn't block page unload
  navigator.sendBeacon('/analytics/rum', JSON.stringify(payload));
}

onCLS(sendToRUM);
onINP(sendToRUM);
onLCP(sendToRUM);
onFCP(sendToRUM);
onTTFB(sendToRUM);
```

---

### 5.3 Interview Questions

**Q: Why do you need source maps in error tracking, and how do you prevent exposing them publicly?** A: Minified production JS has unreadable stack traces (a.b.c line 1 col 84729). Source maps map minified code back to original. Upload maps to Sentry server-side and set `hideSourceMaps: true` so they're not served in the public bundle — attackers can't reverse-engineer your source.

**Q: What's the difference between error monitoring and RUM?** A: Error monitoring (Sentry) captures exceptions — what broke and where. RUM captures performance metrics from real user sessions — how fast pages loaded for actual users. Both are needed: errors tell you something broke, RUM tells you the experience is degrading before it fully breaks.

---

## 6. Performance Budgets + Alerting

### 6.1 Defining a Budget

```json
// bundlesize config — enforced in CI
{
  "files": [
    {
      "path": "apps/web/.next/static/chunks/main-*.js",
      "maxSize": "80 kB"
    },
    {
      "path": "apps/web/.next/static/chunks/pages/index-*.js",
      "maxSize": "50 kB"
    }
  ]
}
```

**Lighthouse CI budget:**

```json
// lighthouserc.json
{
  "ci": {
    "assert": {
      "assertions": {
        "categories:performance":         ["error", { "minScore": 0.9 }],
        "first-contentful-paint":         ["error", { "maxNumericValue": 2000 }],
        "largest-contentful-paint":       ["error", { "maxNumericValue": 2500 }],
        "total-blocking-time":            ["error", { "maxNumericValue": 200 }],
        "cumulative-layout-shift":        ["error", { "maxNumericValue": 0.1 }]
      }
    }
  }
}
```

---

### 6.2 Performance Alerting

```typescript
// Alert when RUM metrics degrade beyond thresholds
function checkPerformanceBudget(metrics: RUMBatch) {
  const p75LCP = percentile(metrics.lcp, 75);

  if (p75LCP > 2500) {
    alerting.fire({
      severity: 'warning',
      title:    'LCP degraded',
      message:  `p75 LCP is ${p75LCP}ms (budget: 2500ms)`,
      runbook:  'https://wiki/runbook/lcp-degraded',
    });
  }
}
```

---

### 6.3 Interview Questions

**Q: What is a performance budget and how do you enforce it?** A: A hard limit on bundle size or Web Vitals scores. Enforced in CI — build fails if budget is exceeded. This prevents performance regressions from shipping. Common tools: bundlesize, Lighthouse CI, webpack performance hints.

---

## 7. Security — CSP, XSS, CSRF, CORS

### 7.1 XSS — Cross-Site Scripting

**The attack:** Injecting malicious scripts into a page that other users see.

```typescript
// Stored XSS: attacker saves script in DB
// Victim loads page → script runs as victim
// <script>document.cookie → attacker's server</script>

// React is safe by default — JSX auto-escapes
const userInput = '<script>alert("xss")</script>';
return <div>{userInput}</div>;  // rendered as text, not executed

// DANGER: dangerouslySetInnerHTML bypasses escaping
return <div dangerouslySetInnerHTML={{ __html: userInput }} />;  // XSS!

// If you must render HTML — sanitize first
import DOMPurify from 'dompurify';
return <div dangerouslySetInnerHTML={{ __html: DOMPurify.sanitize(userInput) }} />;
```

---

### 7.2 CSP — Content Security Policy

CSP is an HTTP header that tells the browser which sources are allowed to load scripts, styles, images, etc.

```
# Strict CSP header
Content-Security-Policy:
  default-src 'none';
  script-src  'self' 'nonce-{RANDOM_NONCE}';  # only scripts with correct nonce
  style-src   'self' 'nonce-{RANDOM_NONCE}';
  img-src     'self' data: https://cdn.example.com;
  connect-src 'self' https://api.example.com;
  font-src    'self';
  frame-src   'none';
  base-uri    'self';
  form-action 'self';
```

**Nonce-based CSP (most secure):**

```typescript
// Next.js middleware — generate nonce per request
import { NextResponse } from 'next/server';
import crypto from 'crypto';

export function middleware(request: NextRequest) {
  const nonce = crypto.randomBytes(16).toString('base64');
  const csp   = `script-src 'nonce-${nonce}' 'strict-dynamic'`;

  const response = NextResponse.next();
  response.headers.set('Content-Security-Policy', csp);
  response.headers.set('x-nonce', nonce); // pass to rendering

  return response;
}
```

---

### 7.3 CSRF — Cross-Site Request Forgery

**The attack:** Malicious site tricks authenticated user's browser into making requests to your API.

```html
<!-- On attacker's site — browser sends victim's cookies automatically -->
<form action="https://bank.com/transfer" method="POST">
  <input name="amount" value="1000" />
  <input name="to" value="attacker" />
</form>
<script>document.forms[0].submit()</script>
```

**Defenses:**

```typescript
// 1. SameSite cookie attribute (modern, primary defense)
Set-Cookie: session=abc123; SameSite=Strict; Secure; HttpOnly
// Strict: cookie only sent on same-site requests
// Lax:    cookie sent on top-level navigation (GET), not POST from other sites

// 2. CSRF token (for APIs that must support cross-origin forms)
// Server generates token, stores in session
// Client includes token in every mutating request header
// Server validates token matches session

// 3. Custom request header check
// Simple API check: if request has custom header (X-Requested-With: XMLHttpRequest)
// it must be from JS — browsers don't add custom headers to cross-origin form posts
```

---

### 7.4 CORS — Cross-Origin Resource Sharing

CORS is a browser security feature — not a server security feature. Servers declare who can access them. Browsers enforce it.

```
Origin: scheme + hostname + port
https://app.example.com ≠ https://api.example.com  (different subdomain)
https://example.com:443 ≠ https://example.com:3000 (different port)
```

```typescript
// Express CORS configuration
import cors from 'cors';

app.use(cors({
  origin: (origin, callback) => {
    const allowed = ['https://app.example.com', 'https://admin.example.com'];
    if (!origin || allowed.includes(origin)) {
      callback(null, true);
    } else {
      callback(new Error('Not allowed by CORS'));
    }
  },
  credentials:     true,           // allow cookies
  allowedHeaders:  ['Content-Type', 'Authorization', 'X-Request-ID'],
  methods:         ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
  maxAge:          86400,           // preflight cache: 24h
}));
```

**Preflight requests:**

```
Browser wants to: POST /api/data with Content-Type: application/json
Browser first sends: OPTIONS /api/data   ← preflight
Server responds:    200 + Access-Control-Allow-* headers
Browser proceeds:   POST /api/data       ← actual request
```

Simple requests (GET/POST with plain text) don't trigger preflight. Custom headers or JSON body do.

---

### 7.5 Interview Questions

**Q: Why is React safe from XSS by default, and what breaks that safety?** A: React escapes all values interpolated in JSX — `{userContent}` renders as text, never HTML. `dangerouslySetInnerHTML` bypasses this. Always sanitize with DOMPurify before using it.

**Q: What is CSP and how does a nonce-based policy work?** A: Content Security Policy is an HTTP header restricting which scripts the browser will execute. Nonce-based: server generates a random nonce per request, injects it into both the CSP header and inline `<script nonce="...">` tags. Browser only executes scripts with matching nonce — blocks injected scripts that have no nonce.

**Q: What is CORS and who enforces it?** A: Cross-Origin Resource Sharing — a browser mechanism that restricts cross-origin requests. The browser enforces it. The server declares allowed origins via response headers. CORS does not protect server-to-server requests — only browser-to-server. Setting `Access-Control-Allow-Origin: *` disables the protection.

**Q: What is the difference between CSRF and XSS?** A: XSS: attacker injects and runs code in your site's context (code injection). CSRF: attacker tricks the user's browser into making requests to your site using existing credentials (request forgery). XSS is a code problem; CSRF is an authentication/state problem. SameSite cookies prevent CSRF. Input sanitization + CSP prevent XSS.

---

---

# INTERVIEW TRACK

---

## 8. Behavioral / Leadership — STAR Method

### Why this matters at FAANG

At senior level, 30–40% of the interview loop is behavioral. FAANG uses structured behavioral interviews to assess leadership principles. Unlike coding rounds, these can't be crammed the night before — they require real stories and deliberate preparation.

---

### 8.1 The STAR Framework

```
Situation  — Context. When, where, what was happening. (1–2 sentences)
Task       — Your specific responsibility. What were YOU accountable for.
Action     — What YOU did. Specific, first-person. Not "we".
Result     — Quantified outcome. Business impact. What changed.
```

**Time allocation per answer:** 2 min total. Situation + Task = 30s. Action = 60–90s. Result = 30s.

---

### 8.2 Common Themes at FAANG

|Theme|What they're testing|
|---|---|
|Ownership|Did you go beyond your job description?|
|Bias for action|Did you move without perfect information?|
|Dive deep|Do you understand your systems at depth?|
|Disagree and commit|Can you push back, then fully commit when overruled?|
|Invent and simplify|Did you find a simpler solution?|
|Deliver results|Did you ship something that mattered?|

---

### 8.3 Story Bank Structure

Prepare 6–8 stories. Each story should flex to answer multiple question types.

**Story template:**

```
Project:      [name]
Context:      [team size, product, constraints]
My role:      [exact scope of ownership]
Challenge:    [technical or interpersonal obstacle]
Action:       [what I specifically did]
Result:       [metric: %, time saved, revenue, errors reduced]
Reusable for: [ownership, leadership, conflict, failure, innovation]
```

---

### 8.4 Key Behavioral Questions + Short Answers

**Q: Tell me about a time you disagreed with a technical decision.** A: Structure: what you disagreed with → how you raised it (data, not opinion) → what happened (overruled or convinced) → how you committed fully either way. Key: demonstrate you can advocate strongly AND commit without resentment.

**Q: Tell me about a time you failed.** A: Structure: what failed, why (your specific mistake, not team's), what you learned, what you changed. Key: don't minimize or deflect. Interviewers want ownership, not a perfect track record.

**Q: Describe a project where you had to learn something new quickly.** A: Structure: what the knowledge gap was, how you closed it (specific: read docs, built POC, found mentor), how it unblocked the project. Key: demonstrate learning velocity, not just that you learned.

**Q: Tell me about a time you improved a process.** A: Structure: what the pain point was (quantified if possible), what you changed, adoption result, ongoing impact. Key: unsolicited improvement — you saw a problem and fixed it without being asked.

**Q: How do you handle competing priorities?** A: Structure: specific example → how you evaluated priority (impact × urgency × dependencies) → what you deferred → what you shipped → outcome. Key: demonstrate structured thinking, not just "I worked harder."

---

## 9. System Design — Feature Flag Service

**Interviewer signal:** Can you design a system that is globally consistent, low-latency, and safely handles rollouts at FAANG scale?

---

### Requirements

**Functional:**

- Create, update, delete flags
- Target by user ID, group, percentage, region
- A/B variants with traffic splitting
- Flag evaluation in < 5ms p99

**Non-functional:**

- 1M+ flag evaluations/second
- 99.99% uptime (flag service outage ≠ product outage)
- Flag changes propagate globally in < 30 seconds

---

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                       Admin UI                              │
│              (create/update/delete flags)                   │
└──────────────────────┬──────────────────────────────────────┘
                       │ CRUD
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                    Flag Service API                         │
│           (validation, auth, audit log, publish)           │
└──────────────────────┬──────────────────────────────────────┘
                       │ write
                       ▼
┌──────────────────────────────┐     ┌──────────────────────┐
│      Postgres (source of     │────►│   Change stream /    │
│      truth for flag config)  │     │   Pub/Sub (Kafka)    │
└──────────────────────────────┘     └──────────┬───────────┘
                                                │ propagate
                                                ▼
                    ┌───────────────────────────────────────────┐
                    │            Redis Cluster                  │
                    │  (in-memory flag cache, global replica)   │
                    └────────────────┬──────────────────────────┘
                                     │ read (< 1ms)
         ┌───────────────────────────┼───────────────────────┐
         ▼                           ▼                       ▼
┌──────────────┐           ┌──────────────┐         ┌──────────────┐
│  SDK (server)│           │  SDK (edge)  │         │  SDK (client)│
│  evaluates   │           │  evaluates   │         │  evaluates   │
│  per request │           │  at CDN edge │         │  in browser  │
└──────────────┘           └──────────────┘         └──────────────┘
```

---

### Data Model

```typescript
interface Flag {
  key:         string;          // unique identifier
  type:        'boolean' | 'string' | 'number' | 'json';
  defaultValue: FlagValue;      // value when no rule matches (safe default)
  rules:       EvaluationRule[];
  status:      'active' | 'archived';
  metadata:    FlagMetadata;
}

interface EvaluationRule {
  id:       string;
  priority: number;             // lower = evaluated first
  conditions: Condition[];      // AND logic within rule
  value:    FlagValue;          // what to return if rule matches
  rollout?: RolloutConfig;      // percentage-based within matched segment
}

interface Condition {
  attribute: 'userId' | 'group' | 'region' | 'plan' | 'email';
  operator:  'in' | 'not_in' | 'equals' | 'contains' | 'matches_regex';
  values:    string[];
}

interface RolloutConfig {
  percentage: number;           // 0–100
  hashKey:    string;           // attribute to hash for bucketing (usually userId)
}
```

---

### Evaluation Algorithm

```typescript
function evaluateFlag(
  flag:    Flag,
  context: EvaluationContext   // { userId, groups, region, plan }
): FlagValue {
  // Rules evaluated in priority order (lower number first)
  const sortedRules = [...flag.rules].sort((a, b) => a.priority - b.priority);

  for (const rule of sortedRules) {
    if (matchesAllConditions(rule.conditions, context)) {
      if (rule.rollout) {
        const bucket = hashToBucket(context[rule.rollout.hashKey], flag.key);
        if (bucket >= rule.rollout.percentage) continue; // not in rollout
      }
      return rule.value;
    }
  }

  return flag.defaultValue; // no rule matched
}
```

---

### Propagation — Sub-30s Global Consistency

```
Flag updated in Postgres
  → Postgres change stream detected by flag service
    → Flag service publishes event to Kafka topic 'flag-changes'
      → Kafka consumers (one per region) receive event
        → Each consumer updates Redis in its region
          → SDKs polling Redis pick up change on next poll (max 10s interval)

Total propagation time: 5–30 seconds
```

**SDK fail-safe — never fail evaluation:**

```typescript
class FlagSDK {
  private localCache: Map<string, FlagConfig> = new Map();

  async evaluate(flagKey: string, context: EvaluationContext): Promise<FlagValue> {
    try {
      // Try Redis first
      const config = await redis.get(`flag:${flagKey}`);
      if (config) {
        this.localCache.set(flagKey, JSON.parse(config));
      }
    } catch {
      // Redis unavailable — fall through to local cache
    }

    const cached = this.localCache.get(flagKey);
    if (cached) return evaluateFlag(cached, context);

    // No cache at all — return safe default
    return SAFE_DEFAULTS[flagKey] ?? false;
  }
}
```

---

### Tradeoffs to Discuss in Interview

|Decision|Why|
|---|---|
|Redis as evaluation cache|Sub-millisecond reads, handles 1M+ RPS|
|Kafka for propagation|Durable, ordered, at-least-once delivery|
|Local in-memory fallback|Flag service outage doesn't affect product|
|Safe defaults in SDK|Network failure = feature off, not error|
|Postgres as source of truth|Durable, auditable, supports complex queries|

---

## 10. System Design — CI/CD Pipeline for a Frontend App

**Interviewer signal:** Can you design a pipeline that is fast, safe, and enables continuous deployment without fear?

---

### Requirements

- Build and test on every PR
- Deploy to staging on merge to main
- Deploy to production with canary + automatic rollback
- Total pipeline time < 10 minutes

---

### Full Pipeline Architecture

```
PR opened
  → Lint + Typecheck (parallel, 2 min)
  → Unit tests (parallel, 3 min) [affected packages only]
  → Build (3 min) [Turbo remote cache: often < 30s]
  → Bundle size check (fail if over budget)
  → Lighthouse CI on preview URL (score regression check)
  → E2E smoke tests (2 min, critical paths only on PR)

Merge to main
  → Full E2E suite (10 min, parallel shards)
  → Build production artifact (Docker image + static assets)
  → Tag image with git SHA
  → Push to container registry

  → Auto-deploy to staging
      → Smoke tests against staging
      → Auto-promote to canary (5%) if tests pass

  → Canary analysis (10 min dwell)
      → Error rate < 1% AND p95 latency < 500ms
        → Auto-expand to 25% → 50% → 100%
      → Threshold breached
        → Auto-rollback (route 100% to previous)
        → Alert on-call engineer
        → Create incident ticket

Production stable
  → CDN invalidation (index.html only)
  → Feature flag gradual rollout begins
  → Monitor RUM metrics for 30 min
```

---

### Speed Optimizations

```
1. Turbo remote cache  → build hits cache if inputs unchanged (< 30s)
2. Affected filtering  → only test changed packages on PR
3. Parallel jobs       → lint, test, build run simultaneously
4. E2E sharding        → 40 tests / 4 runners = 10 tests each
5. Playwright reuse    → cache browser binaries between runs
6. Docker layer cache  → package install cached if lockfile unchanged
```

---

### Automatic Rollback Implementation

```yaml
# Argo Rollouts analysis for automatic rollback
apiVersion: argoproj.io/v1alpha1
kind: AnalysisTemplate
metadata:
  name: frontend-health
spec:
  metrics:
    - name: error-rate
      interval: 1m
      failureLimit: 2        # fail after 2 consecutive bad readings
      provider:
        prometheus:
          query: |
            sum(rate(http_requests_total{status=~"5..",app="web"}[2m]))
            /
            sum(rate(http_requests_total{app="web"}[2m]))
      successCondition: result[0] < 0.005  # < 0.5% error rate

    - name: p95-latency
      interval: 1m
      failureLimit: 2
      provider:
        prometheus:
          query: |
            histogram_quantile(0.95,
              rate(http_request_duration_seconds_bucket{app="web"}[2m]))
      successCondition: result[0] < 0.5  # < 500ms
```

---

### Key Interview Tradeoffs

|Decision|Tradeoff|
|---|---|
|Remote build cache|Fast PRs vs cache invalidation complexity|
|Canary before full rollout|Slow deploy vs early error detection|
|Auto-rollback|Less manual intervention vs false positive rollbacks|
|Parallel pipeline jobs|Fast vs higher CI cost|
|Content-hash assets|Cache forever vs stale file accumulation|

---

## Phase 4 — Weekly Study Schedule

|Week|Craft Focus|Interview Focus|
|---|---|---|
|1|Docker: multi-stage builds, layer caching|STAR stories: write 3 ownership stories|
|2|GitHub Actions: build full CI pipeline|STAR stories: write 3 failure/conflict stories|
|3|Feature flags: SDK + percentage rollout + kill switch|System design: feature flag service (draft)|
|4|Feature flags: A/B testing + flag hygiene + tools|System design: feature flag service (refine tradeoffs)|
|5|Deployment: rolling + blue/green + canary|System design: CI/CD pipeline (draft)|
|6|Deployment: CDN strategy + immutable artifacts|System design: CI/CD pipeline (mock interview)|
|7|Sentry + RUM: integrate on a real project|Behavioral: mock behavioral interview (recorded)|
|8|Security: CSP + XSS + CSRF audit a real app|Mixed: full mock interview (coding + system design + behavioral)|

**Weekly habit:** Every flag you write in a real project — set an expiry date and open a cleanup ticket immediately. Build the discipline now.

---

## Primary Sources

|Topic|Source|
|---|---|
|Docker best practices|[docs.docker.com/develop/best-practices](https://docs.docker.com/develop/develop-images/dockerfile_best-practices/)|
|GitHub Actions docs|[docs.github.com/en/actions](https://docs.github.com/en/actions)|
|Feature flag patterns|[martinfowler.com/articles/feature-toggles](https://martinfowler.com/articles/feature-toggles.html)|
|LaunchDarkly flag best practices|[launchdarkly.com/blog](https://launchdarkly.com/blog/)|
|Deployment strategies|[kubernetes.io/docs/concepts/workloads/controllers/deployment](https://kubernetes.io/docs/concepts/workloads/controllers/deployment/)|
|Argo Rollouts|[argoproj.github.io/rollouts](https://argoproj.github.io/rollouts/)|
|Expand-contract migrations|[martinfowler.com/bliki/ParallelChange](https://martinfowler.com/bliki/ParallelChange.html)|
|OWASP Top 10|[owasp.org/www-project-top-ten](https://owasp.org/www-project-top-ten/)|
|CSP reference|[developer.mozilla.org/en-US/docs/Web/HTTP/CSP](https://developer.mozilla.org/en-US/docs/Web/HTTP/CSP)|
|Sentry Next.js|[docs.sentry.io/platforms/javascript/guides/nextjs](https://docs.sentry.io/platforms/javascript/guides/nextjs/)|
|web-vitals library|[github.com/GoogleChrome/web-vitals](https://github.com/GoogleChrome/web-vitals)|
|FAANG behavioral prep|[amazon.jobs/content/en/our-workplace/leadership-principles](https://www.amazon.jobs/content/en/our-workplace/leadership-principles)|