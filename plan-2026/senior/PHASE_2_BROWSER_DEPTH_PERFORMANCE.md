# Phase 2 — Deep Dive: Browser Depth + Performance

> **Duration:** 3–6 months (parallel tracks) **Goal:** Profile and fix real perf issues. Solve LC Medium/Hard (Meta/Google tagged). Explain the critical rendering path in an interview without hesitation.

---

## Table of Contents

### Craft Track

1. [Critical Rendering Path](https://claude.ai/chat/66caa6a7-7c60-4209-93d6-c254a560cf68#1-critical-rendering-path)
2. [Layout, Paint, Composite Layers](https://claude.ai/chat/66caa6a7-7c60-4209-93d6-c254a560cf68#2-layout-paint-composite-layers)
3. [Core Web Vitals — LCP, CLS, INP](https://claude.ai/chat/66caa6a7-7c60-4209-93d6-c254a560cf68#3-core-web-vitals--lcp-cls-inp)
4. [Chrome DevTools Profiling](https://claude.ai/chat/66caa6a7-7c60-4209-93d6-c254a560cf68#4-chrome-devtools-profiling)
5. [Bundle Analysis + Code Splitting](https://claude.ai/chat/66caa6a7-7c60-4209-93d6-c254a560cf68#5-bundle-analysis--code-splitting)

### Interview Track

6. [Graph Traversal — BFS / DFS](https://claude.ai/chat/66caa6a7-7c60-4209-93d6-c254a560cf68#6-graph-traversal--bfs--dfs)
7. [Dynamic Programming — Top-Down](https://claude.ai/chat/66caa6a7-7c60-4209-93d6-c254a560cf68#7-dynamic-programming--top-down)
8. [Stack, Queue, Heap Patterns](https://claude.ai/chat/66caa6a7-7c60-4209-93d6-c254a560cf68#8-stack-queue-heap-patterns)

---

# CRAFT TRACK

---

## 1. Critical Rendering Path

### What it is

The Critical Rendering Path (CRP) is the sequence of steps the browser must complete to convert HTML, CSS, and JavaScript into pixels on screen. Optimizing the CRP is the single most impactful category of frontend performance work.

---

### 1.1 The Full Sequence

```
Network request
  → HTML bytes received
    → Tokenization (bytes → tokens)
      → DOM construction (tokens → nodes → DOM tree)

  → CSS bytes received
    → CSSOM construction (parallel to DOM, but blocks rendering)

  → DOM + CSSOM merge
    → Render Tree (only visible nodes + computed styles)

  → Layout (Reflow) — compute geometry: size, position
  → Paint — fill pixels: color, text, images, shadows
  → Composite — assemble layers into final frame
```

Each arrow is a potential bottleneck. Understanding which step a resource blocks determines how you fix it.

---

### 1.2 DOM Construction

The browser parses HTML top-to-bottom and builds the DOM incrementally. The DOM represents the **structure and content** of the page, not how it looks.

```html
<!DOCTYPE html>
<html>
  <head>
    <link rel="stylesheet" href="styles.css" />   <!-- render-blocking -->
    <script src="app.js"></script>                 <!-- parser-blocking AND render-blocking -->
  </head>
  <body>
    <h1>Hello</h1>
  </body>
</html>
```

**Key:** The DOM can be built incrementally, but it cannot be rendered until the CSSOM is also complete. This is why CSS blocks rendering.

---

### 1.3 CSSOM Construction

CSS is **render-blocking by design**. The browser cannot render any content until it has a complete CSSOM — a partially styled page would shift visually as styles load, which is worse UX than waiting.

```
Bytes → Characters → Tokens → Nodes → CSSOM
```

The CSSOM is also **recalculation-heavy**. CSS rules cascade — a single rule can affect the entire subtree. This is why:

- Deep selector chains (`.a .b .c .d .e`) are expensive
- Adding/removing a class high in the tree triggers recalculation for all descendants

---

### 1.4 Render Tree

The Render Tree is the merge of DOM + CSSOM. It contains only **visible** nodes with their resolved styles.

What's excluded from the Render Tree:

- `<head>` elements (meta, scripts, links)
- `display: none` elements (not in tree — no space reserved)
- `visibility: hidden` elements **are** in the tree (space reserved, just invisible)
- `<script>` elements

```
DOM:                   CSSOM:              Render Tree:
html                   html → block        html
  head                 body → block        body
    link               h1   → block          h1 (with styles)
    script             span → inline          span (with styles)
  body                 .hidden → display:none
    h1
    span
    div.hidden          ← excluded (display:none)
```

---

### 1.5 Render-Blocking Resources

|Resource|Blocks rendering?|Blocks parsing?|Fix|
|---|---|---|---|
|CSS in `<head>`|Yes|No|Inline critical CSS, defer non-critical|
|`<script>` (default)|Yes|Yes|Add `defer` or `async`|
|`<script defer>`|No|No|Runs after DOM parsed, before DOMContentLoaded|
|`<script async>`|Yes (when it runs)|No|Runs as soon as downloaded — order not guaranteed|
|Web fonts|Yes (text invisible until loaded — FOIT)|No|`font-display: swap`, preload|

**`defer` vs `async` — the decision:**

```html
<!-- defer: safe for scripts that depend on DOM or each other -->
<script defer src="app.js"></script>

<!-- async: safe for independent scripts (analytics, ads) -->
<script async src="analytics.js"></script>
```

---

### 1.6 Preload, Prefetch, Preconnect

These hints let the browser start work before it would naturally discover the resource:

```html
<!-- preload: high priority, needed for current page, same origin -->
<link rel="preload" href="/fonts/Inter.woff2" as="font" crossorigin />

<!-- prefetch: low priority, likely needed for next navigation -->
<link rel="prefetch" href="/dashboard.js" />

<!-- preconnect: establish TCP + TLS with third-party origin early -->
<link rel="preconnect" href="https://api.example.com" />

<!-- dns-prefetch: just DNS lookup (lighter than preconnect) -->
<link rel="dns-prefetch" href="https://cdn.example.com" />
```

**Rule:** Only preload what's in the critical path. Preloading too much competes with resources the browser would have prioritized anyway.

---

### 1.7 Interview Questions

**Q: What is the critical rendering path and what are its main steps?** A: HTML → DOM, CSS → CSSOM, merge into Render Tree, Layout (compute geometry), Paint (fill pixels), Composite (assemble layers). CSS and synchronous scripts block this process.

**Q: Why does CSS block rendering?** A: The browser needs a complete CSSOM before building the Render Tree. Rendering with partial CSS would produce a flash of unstyled content that re-renders as styles arrive — worse UX than waiting.

**Q: What's the difference between `defer` and `async`?** A: `defer` delays script execution until after DOM is parsed, preserves order, and runs before DOMContentLoaded. `async` downloads in parallel and executes immediately when ready — order not guaranteed. Use `defer` for app scripts, `async` for independent third-party scripts.

**Q: What's the difference between `display:none` and `visibility:hidden`?** A: `display:none` removes the element from the Render Tree entirely — no space reserved, not painted. `visibility:hidden` keeps the element in the Render Tree and reserves its space, but makes it invisible.

**Q: What does `<link rel="preload">` do and when is it appropriate?** A: It tells the browser to fetch a resource at high priority before it would naturally discover it. Appropriate for late-discovered critical resources like fonts, hero images, or key CSS. Avoid preloading everything — it degrades prioritization.

---

## 2. Layout, Paint, Composite Layers

### What it is

After the Render Tree is built, the browser goes through three rendering stages: **Layout** (where and how big), **Paint** (what color and shape), and **Composite** (stack order). Triggering the wrong stage is the primary source of jank.

---

### 2.1 Layout (Reflow)

Layout computes the **geometry** of every element: position (x, y) and size (width, height). It reads the Render Tree and produces a Layout Tree with exact coordinates.

Layout is **expensive** because it's recursive — a size change to a parent cascades to all children.

**What triggers layout:**

```javascript
// Reading geometry properties FORCES synchronous layout
// (browser must calculate current layout to return accurate value)
const width  = element.offsetWidth;
const height = element.offsetHeight;
const rect   = element.getBoundingClientRect();
const scroll = element.scrollTop;

// Writing geometry properties invalidates layout (marks it dirty)
element.style.width = '200px';
element.style.margin = '10px';
```

**Layout thrashing** — the most common perf bug:

```javascript
// THRASHING: read → write → read → write in a loop
// Each read after a write forces a synchronous recalculation
for (const el of elements) {
  const width = el.offsetWidth;  // forced synchronous layout
  el.style.width = width + 10 + 'px'; // invalidates layout
}

// FIX: batch reads first, then writes
const widths = elements.map(el => el.offsetWidth);  // all reads
elements.forEach((el, i) => {
  el.style.width = widths[i] + 10 + 'px';  // all writes
});
```

---

### 2.2 Paint

Paint fills in the pixels: colors, text, images, borders, shadows, outlines. It operates on the Layout Tree and produces paint records.

**What triggers paint but NOT layout:**

```css
/* changes that require repaint but not reflow */
color, background-color, border-color,
box-shadow, outline, visibility, text-decoration
```

**What triggers both (layout → paint):**

```css
/* any geometry or structural change */
width, height, padding, margin, top, left,
font-size, border-width, display
```

**CSS Triggers reference:** `csstriggers.com` maps every CSS property to which pipeline stages it triggers.

---

### 2.3 Composite Layers

Compositing is the final step — the browser splits the page into **layers** and combines them on the GPU. Layer compositing is the cheapest rendering stage because the GPU handles it off the main thread.

**How layers are promoted:** The browser automatically promotes some elements to their own layer. You can force promotion:

```css
/* Explicit GPU layer promotion */
transform: translateZ(0);       /* legacy hack */
will-change: transform;         /* correct modern approach */
will-change: opacity;
```

**The two properties that only trigger compositing:**

```css
/* These two NEVER trigger layout or paint — GPU only */
transform: translate(x, y) scale(n) rotate(deg);
opacity: 0 to 1;
```

This is why you always animate with `transform` and `opacity`, never with `top/left` or `width/height`:

```css
/* SLOW — triggers layout + paint on every frame */
.box { transition: left 0.3s, top 0.3s; }

/* FAST — GPU compositing only, no layout/paint */
.box { transition: transform 0.3s; }
```

**Layer explosion:** Too many promoted layers consume GPU memory and can hurt performance. Only promote elements that genuinely benefit (animated elements, canvas, video, fixed headers).

---

### 2.4 The Rendering Pipeline Summary

```
JavaScript → Style → Layout → Paint → Composite
                        ↑           ↑          ↑
              All three stages  Only paint   Only composite
              (geometry change) (color change) (transform/opacity)
```

**The optimization rule:** Push animations and transitions as far right in this pipeline as possible — ideally to composite-only.

---

### 2.5 `requestAnimationFrame`

When you need to animate with JavaScript, use `requestAnimationFrame` (rAF) — it runs your callback at the right point in the rendering cycle, before the browser paints:

```javascript
// Wrong — may fire mid-frame, causing multiple layouts per frame
setInterval(() => {
  element.style.transform = `translateX(${x++}px)`;
}, 16);

// Correct — fires once per frame, synchronized with browser's rendering loop
function animate() {
  element.style.transform = `translateX(${x++}px)`;
  requestAnimationFrame(animate);
}
requestAnimationFrame(animate);
```

---

### 2.6 Interview Questions

**Q: What's the difference between layout, paint, and composite?** A: Layout computes geometry (position, size). Paint fills pixels (color, shadows, text). Composite assembles GPU layers into the final frame. Each is progressively cheaper. Skipping layout and paint by using transform/opacity keeps animations on the GPU.

**Q: What is layout thrashing?** A: Interleaving DOM reads that force synchronous layout (offsetWidth, getBoundingClientRect) with DOM writes that invalidate layout (style changes) inside a loop. Fix: batch all reads first, then all writes.

**Q: Why should you animate with `transform` instead of `top/left`?** A: `top/left` triggers layout + paint on every frame. `transform` only triggers compositing, which runs on the GPU off the main thread — no layout recalculation, no repaint. This is the difference between 60fps and jank.

**Q: What does `will-change` do?** A: It hints to the browser that an element will animate, triggering early GPU layer promotion. This avoids the cost of promoting the layer mid-animation. Overuse consumes GPU memory — only use on elements actively being animated.

**Q: What triggers a reflow?** A: Any change to geometry-affecting properties (width, height, padding, margin, font-size), or reading layout properties (offsetWidth, getBoundingClientRect) after a DOM write.

---

## 3. Core Web Vitals — LCP, CLS, INP

### What they are

Core Web Vitals are Google's standardized metrics for user-experienced performance. They directly affect SEO rankings and are the primary performance targets at FAANG-scale products.

---

### 3.1 LCP — Largest Contentful Paint

**What it measures:** Time from navigation start until the largest image or text block visible in the viewport is rendered.

**Target:** ≤ 2.5 seconds (good), 2.5–4s (needs improvement), > 4s (poor)

**What counts as the LCP element:**

- `<img>` elements
- `<image>` inside SVG
- `<video>` poster images
- Block-level elements with background images
- Block-level elements containing text

**Common LCP killers and fixes:**

```
Problem: Hero image is not preloaded
Fix: <link rel="preload" href="/hero.jpg" as="image" />

Problem: Hero image is lazy-loaded
Fix: Remove loading="lazy" from above-the-fold images
     <img src="/hero.jpg" loading="eager" fetchpriority="high" />

Problem: Render-blocking CSS delays when paint can start
Fix: Inline critical CSS, defer non-critical CSS

Problem: Server response is slow (high TTFB)
Fix: CDN, caching, reduce server-side computation

Problem: Client-side rendering — content arrives late
Fix: SSR or SSG for above-the-fold content
```

---

### 3.2 CLS — Cumulative Layout Shift

**What it measures:** Total unexpected visual shift of page content during the page's lifetime. Calculated as impact fraction × distance fraction for each shift.

**Target:** ≤ 0.1 (good), 0.1–0.25 (needs improvement), > 0.25 (poor)

**Common CLS causes and fixes:**

```
Problem: Images without explicit dimensions
Fix: Always set width + height (or aspect-ratio) on <img>

  <!-- Bad: browser doesn't know size, shifts when image loads -->
  <img src="/photo.jpg" />

  <!-- Good: browser reserves space before image loads -->
  <img src="/photo.jpg" width="800" height="600" />

Problem: Dynamically injected content above existing content
  (ads, banners, cookie notices pushing content down)
Fix: Reserve space with min-height, or inject at bottom

Problem: Web fonts causing FOUT (Flash of Unstyled Text)
Fix: font-display: swap + preload font
     or size-adjust CSS descriptor to match fallback metrics

Problem: Skeleton screens that differ from real content size
Fix: Match skeleton dimensions exactly to loaded content
```

---

### 3.3 INP — Interaction to Next Paint

**What it measures:** The latency of the worst (p98) interaction on the page — from user input (click, key, tap) to the next frame being painted. Replaced FID in March 2024.

**Target:** ≤ 200ms (good), 200–500ms (needs improvement), > 500ms (poor)

**Why INP > FID:** FID only measured the first interaction. INP measures all interactions across the page's lifetime, making it a much stronger signal of runtime responsiveness.

**INP = Input delay + Processing time + Presentation delay**

```
User clicks button
  → Input delay: event is queued (main thread busy?)
    → Processing time: event handler runs
      → Presentation delay: render, paint, composite
        → Next frame painted
```

**Common INP killers and fixes:**

```
Problem: Long tasks blocking the main thread
Fix: Break long tasks with scheduler.yield() or setTimeout(0)

  // Before: 500ms synchronous task blocks all input
  function processData(items) {
    items.forEach(item => heavyOperation(item));
  }

  // After: yield to browser between chunks
  async function processData(items) {
    for (const item of items) {
      heavyOperation(item);
      await scheduler.yield(); // let browser handle input between items
    }
  }

Problem: Expensive React re-renders on interaction
Fix: useDeferredValue, React.memo, useTransition for non-urgent updates

  function SearchResults({ query }) {
    const deferredQuery = useDeferredValue(query);
    // expensive filtering runs with deferred (lower priority) query
    const results = useMemo(() => filter(deferredQuery), [deferredQuery]);
    return <List items={results} />;
  }

Problem: Third-party scripts running on main thread
Fix: Move to Web Workers, load with async/defer, use Partytown
```

---

### 3.4 Supporting Metrics

|Metric|Measures|Target|
|---|---|---|
|TTFB|Server response time|< 800ms|
|FCP|First Contentful Paint — any content visible|< 1.8s|
|TBT|Total Blocking Time — main thread blocked > 50ms|< 200ms|
|TTI|Time to Interactive — fully interactive|< 3.8s|

**TBT** is the lab-equivalent of INP. Reduce long tasks → improve both.

---

### 3.5 Measuring Web Vitals

```javascript
// web-vitals library (Google's official package)
import { onLCP, onCLS, onINP } from 'web-vitals';

onLCP(metric => console.log('LCP:', metric.value));
onCLS(metric => console.log('CLS:', metric.value));
onINP(metric => console.log('INP:', metric.value));

// Send to analytics
function sendToAnalytics({ name, value, id }) {
  fetch('/analytics', {
    method: 'POST',
    body: JSON.stringify({ name, value, id }),
  });
}

onLCP(sendToAnalytics);
onCLS(sendToAnalytics);
onINP(sendToAnalytics);
```

---

### 3.6 Interview Questions

**Q: What are Core Web Vitals and why do they matter?** A: LCP (loading), CLS (visual stability), INP (responsiveness) — Google's metrics for user-experienced performance. They directly affect SEO rankings and reflect real user pain points, not synthetic benchmarks.

**Q: An image is your LCP element and it's slow. What do you check?** A: Is it preloaded? Is it lazy-loaded above the fold? Is it properly sized and in a modern format (WebP/AVIF)? Is the server TTFB fast? Is render-blocking CSS delaying when the browser can paint?

**Q: What causes CLS and how do you fix the most common case?** A: Most common: images without explicit width/height causing layout shifts when they load. Fix: always specify dimensions or use aspect-ratio CSS. Other causes: dynamically injected content, web fonts causing FOUT.

**Q: What is INP and what replaced it?** A: INP (Interaction to Next Paint) replaced FID in March 2024. FID only measured the first interaction's input delay. INP measures the worst interaction latency across the entire session, making it a stronger responsiveness signal.

**Q: How do you reduce INP on an interaction that triggers an expensive React re-render?** A: Use `useTransition` to mark the update as non-urgent (keeps the UI responsive during the render), `useDeferredValue` to defer the expensive computation, or `React.memo` to prevent unnecessary re-renders in the subtree.

---

## 4. Chrome DevTools Profiling

### What it is

Chrome DevTools is the primary tool for diagnosing frontend performance issues. Knowing how to read a flame chart, identify long tasks, and isolate rendering bottlenecks separates engineers who guess from engineers who measure.

---

### 4.1 Performance Panel Anatomy

Open: `F12 → Performance tab → Record → interact → Stop`

**Key sections in the timeline:**

```
┌─────────────────────────────────────────────────────┐
│ FPS chart    (green = good, red = jank)             │
│ CPU chart    (how busy the main thread is)          │
│ Network      (resource loading waterfall)           │
├─────────────────────────────────────────────────────┤
│ Main thread  (flame chart — call stacks over time)  │
│ Compositor   (GPU thread work)                      │
│ Raster       (tile rasterization)                   │
├─────────────────────────────────────────────────────┤
│ Timings      (FCP, LCP, DCL markers)                │
│ Long Tasks   (red triangles = tasks > 50ms)         │
└─────────────────────────────────────────────────────┘
```

---

### 4.2 Reading the Flame Chart

The flame chart shows the **call stack over time**. Each bar is a function call. Width = duration. Nesting = call depth.

```
┌──────────────────────────────── Task (120ms) ──────────────────────────────────┐
│  ┌────── onClick (80ms) ──────┐  ┌─── setState (30ms) ──────────────────────┐  │
│  │ ┌── processItems (70ms) ┐  │  │ ┌─── reconcile (20ms) ─────────────────┐ │  │
│  │ │ ┌─ loop(60ms) ───────┐│  │  │ │ ┌─ commitRoot (12ms) ──────────────┐ │ │  │
│  │ │ └───────────────────┘│  │  │ │ └─────────────────────────────────┘ │ │  │
│  │ └───────────────────────┘  │  │ └─────────────────────────────────────┘ │  │
│  └─────────────────────────────┘  └───────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────────────┘
```

**Long tasks (> 50ms)** are marked with a red triangle. These block the main thread and cause INP issues.

**How to identify the bottleneck:**

1. Find the widest bar in the flame chart
2. Look at its children — which child is widest?
3. Drill down until you find the leaf function consuming the most time
4. That function is your fix target

---

### 4.3 Memory Panel

**Heap snapshot:** Point-in-time view of all objects in memory. Use to find memory leaks — take a snapshot, interact with the page, take another, compare.

**Allocation timeline:** Records object allocations over time. Look for objects that are allocated but never garbage collected.

**Common leak patterns:**

```javascript
// Leak 1: event listeners not removed
function Component() {
  useEffect(() => {
    window.addEventListener('resize', handler);
    // missing: return () => window.removeEventListener('resize', handler);
  }, []);
}

// Leak 2: closures holding references to large objects
function createHandler(largeData) {
  return function handler() {
    // `largeData` is closed over — never GC'd while handler exists
    console.log(largeData.id);
  };
}

// Leak 3: timers not cleared
const id = setInterval(tick, 1000);
// missing: clearInterval(id) on cleanup
```

---

### 4.4 Network Panel Profiling

**Waterfall analysis:** Each row is a resource. The colored bars show:

- `Queueing` — waiting for a connection slot
- `Stall` — waiting for connection reuse
- `DNS lookup`
- `Initial connection` (TCP handshake)
- `SSL` (TLS handshake)
- `Request sent`
- `Waiting (TTFB)` — server response time
- `Content download`

**What to look for:**

- Large TTFB → server-side problem (slow DB, no caching)
- Many small sequential requests → waterfall anti-pattern (request chains)
- Large JS bundles → need code splitting
- No caching headers → repeated full downloads

**Coverage tab:** Shows exactly which bytes of each JS/CSS file were executed. High unused bytes = opportunity for code splitting.

---

### 4.5 Rendering Tab (Hidden but Critical)

Enable via: `⋮ → More tools → Rendering`

|Option|What it reveals|
|---|---|
|Paint flashing|Green overlay on every repaint — excess flashing = too many paints|
|Layout Shift Regions|Blue overlay on every layout shift — find CLS causes visually|
|FPS meter|Real-time frame rate overlay|
|Layer borders|Orange borders on composited layers — identify layer explosion|
|Scrolling performance issues|Highlights non-passive scroll listeners|

---

### 4.6 Interview Questions

**Q: How would you diagnose a janky animation using DevTools?** A: Record in Performance panel. Check FPS chart for drops. Find long tasks in the main thread flame chart. Identify if the animation triggers layout/paint (check for purple Layout and green Paint bars). If so, switch to transform/opacity. Use the Rendering tab to confirm paint flashing is eliminated.

**Q: What is a long task and why does it matter?** A: Any main thread task exceeding 50ms. During a long task the browser cannot respond to user input — clicks, scrolls, key presses queue up. This directly degrades INP and causes the perception of a "frozen" page.

**Q: How do you detect a memory leak?** A: Take a heap snapshot baseline, reproduce the suspected leak (navigate, interact, return), take a second snapshot. Use the comparison view to find objects that grew — specifically look for Detached DOM nodes and growing arrays/closures.

**Q: What does the Coverage tab show and how do you act on it?** A: Unused JavaScript and CSS bytes per file. High unused JS in a bundle means that code is loaded but not executed on the current page. Action: code-split at the route level so only the needed chunk is loaded.

---

## 5. Bundle Analysis + Code Splitting

### What it is

Bundle size directly determines parse and execution time — JavaScript is the most expensive byte-for-byte resource on the web (parse + compile + execute vs. images which only decode). Optimizing bundles is a primary FAANG frontend performance concern.

---

### 5.1 Why Bundle Size Matters

```
1MB of JPEG image: ~50ms to decode
1MB of JavaScript:
  → ~1000ms to parse + compile (low-end mobile)
  → + execution time
  → blocks main thread for all of it
```

JavaScript is **parse-compile-execute** heavy. Image bytes are decode-only. This is why a 200KB JS bundle hurts more than a 200KB image.

---

### 5.2 Analyzing Your Bundle

**Webpack Bundle Analyzer:**

```bash
npm install --save-dev webpack-bundle-analyzer

# In webpack config:
const { BundleAnalyzerPlugin } = require('webpack-bundle-analyzer');
module.exports = {
  plugins: [new BundleAnalyzerPlugin()]
};
```

**Vite / Rollup:**

```bash
npm install --save-dev rollup-plugin-visualizer

# vite.config.ts
import { visualizer } from 'rollup-plugin-visualizer';
export default {
  plugins: [visualizer({ open: true, gzipSize: true })]
};
```

**What to look for in the treemap:**

- Unexpectedly large dependencies (moment.js → replace with date-fns)
- Duplicate packages (two versions of lodash)
- Libraries included in full when only one function is used
- Polyfills for browsers you no longer support

---

### 5.3 Code Splitting Strategies

**Strategy 1: Route-based splitting (minimum bar)**

Every route gets its own chunk. Users only download the code for the page they're on.

```typescript
// React Router + React.lazy
import { lazy, Suspense } from 'react';
import { Routes, Route } from 'react-router-dom';

const Dashboard  = lazy(() => import('./pages/Dashboard'));
const Profile    = lazy(() => import('./pages/Profile'));
const Settings   = lazy(() => import('./pages/Settings'));

function App() {
  return (
    <Suspense fallback={<PageSpinner />}>
      <Routes>
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/profile"   element={<Profile />} />
        <Route path="/settings"  element={<Settings />} />
      </Routes>
    </Suspense>
  );
}
```

**Strategy 2: Component-based splitting (for heavy components)**

Split components that are heavy and not immediately visible:

```typescript
// Heavy chart only loaded when user navigates to analytics section
const AnalyticsChart = lazy(() => import('./components/AnalyticsChart'));

// Heavy modal only loaded when triggered
const VideoPlayer = lazy(() => import('./components/VideoPlayer'));

function Dashboard() {
  const [showVideo, setShowVideo] = useState(false);

  return (
    <>
      <button onClick={() => setShowVideo(true)}>Watch Tutorial</button>
      {showVideo && (
        <Suspense fallback={<Skeleton />}>
          <VideoPlayer />
        </Suspense>
      )}
    </>
  );
}
```

**Strategy 3: Library splitting (separate vendor chunk)**

Keep your app code and library code in separate chunks. Libraries change less frequently → better long-term caching:

```typescript
// vite.config.ts
export default {
  build: {
    rollupOptions: {
      output: {
        manualChunks: {
          'react-vendor': ['react', 'react-dom'],
          'router':       ['react-router-dom'],
          'charts':       ['recharts', 'd3'],
        }
      }
    }
  }
}
```

---

### 5.4 Tree Shaking

Tree shaking is dead code elimination — the bundler removes exported functions that are never imported.

**For tree shaking to work:**

1. Use ES Modules (`import/export`), not CommonJS (`require`)
2. Avoid side-effectful imports
3. Mark packages as side-effect-free in `package.json`

```json
// package.json
{ "sideEffects": false }

// or specify which files have side effects
{ "sideEffects": ["*.css", "polyfills.js"] }
```

**Named imports enable tree shaking; namespace imports don't:**

```javascript
// Good: bundler includes only the `format` function
import { format } from 'date-fns';

// Bad: bundler must include the entire lodash library
import _ from 'lodash';
// Better:
import debounce from 'lodash/debounce';
// Best: use lodash-es for full tree shaking
import { debounce } from 'lodash-es';
```

---

### 5.5 Preloading Split Chunks

Lazy chunks should be preloaded when it's likely the user will need them:

```typescript
// Prefetch: low priority, downloads when browser is idle
const Dashboard = lazy(() => import(/* webpackPrefetch: true */ './Dashboard'));

// Preload: high priority, downloads in parallel with current chunk
const Critical = lazy(() => import(/* webpackPreload: true */ './Critical'));

// Hover-based prefetch — preload on intent, not on page load
function NavLink({ to, children }) {
  const handleMouseEnter = () => {
    import(`./pages/${to}`); // trigger module load on hover
  };
  return <a href={to} onMouseEnter={handleMouseEnter}>{children}</a>;
}
```

---

### 5.6 Caching Strategy

Split bundles enable long-term caching. Each chunk gets a content hash in its filename:

```
app.[contenthash].js       ← changes every release
react-vendor.[contenthash].js  ← changes only when React version changes
```

When you ship a new feature:

- `app.[hash].js` → new hash → browser downloads it
- `react-vendor.[hash].js` → same hash → served from cache

Without splitting, any change invalidates the entire bundle.

---

### 5.7 Interview Questions

**Q: What is code splitting and why is it important?** A: Splitting a large JS bundle into smaller chunks so users only download the code needed for the current page/interaction. Reduces parse/compile/execute time, improves LCP and TTI, enables better caching.

**Q: What is tree shaking and what's required for it to work?** A: Dead code elimination — the bundler removes exported functions that are never imported. Requires ES Module syntax (import/export), not CommonJS (require), and packages marked with `sideEffects: false`.

**Q: Why is JavaScript more expensive than images of the same byte size?** A: Images only need to be decoded. JavaScript must be parsed (byte → AST), compiled (AST → bytecode), and executed — all on the main thread. A 200KB JS file typically costs 5–10× more CPU time than a 200KB image.

**Q: How do you split a vendor bundle and why?** A: Configure `manualChunks` in Rollup/Vite (or `splitChunks` in Webpack) to separate third-party dependencies into their own chunks. Libraries change less often than app code, so they get long-lived cache hits — users redownload only the changed app chunk, not React or router.

**Q: How would you prefetch a route before the user navigates to it?** A: Trigger `import('./Page')` dynamically — on hover, on idle (requestIdleCallback), or with Webpack's `webpackPrefetch` magic comment. The browser downloads the chunk in the background at low priority and serves it from cache when needed.

---

---

# INTERVIEW TRACK

---

## 6. Graph Traversal — BFS / DFS

### Mental model first

A graph is any structure where nodes connect to other nodes. This includes: social networks, file systems, dependency trees, web page links, React component trees, route graphs, DOM trees. Most real-world systems are graphs.

**BFS:** Explore level-by-level outward from source. Uses a queue. Finds shortest path in unweighted graphs.

**DFS:** Explore as deep as possible down one path before backtracking. Uses a stack (or recursion). Finds existence, connected components, cycles.

---

### 6.1 BFS — Breadth-First Search

```typescript
function bfs(graph: Map<number, number[]>, start: number): number[] {
  const visited = new Set<number>();
  const queue   = [start];
  const result  = [];

  visited.add(start);

  while (queue.length > 0) {
    const node = queue.shift()!;  // dequeue from front
    result.push(node);

    for (const neighbor of graph.get(node) ?? []) {
      if (!visited.has(neighbor)) {
        visited.add(neighbor);
        queue.push(neighbor);  // enqueue to back
      }
    }
  }

  return result;
}
```

**Time:** O(V + E) — visit every vertex and edge once **Space:** O(V) — queue holds at most one level

**BFS for shortest path (unweighted):**

```typescript
function shortestPath(
  graph: Map<number, number[]>,
  start: number,
  end: number
): number {
  const visited = new Set([start]);
  const queue   = [[start, 0]]; // [node, distance]

  while (queue.length > 0) {
    const [node, dist] = queue.shift()!;

    if (node === end) return dist;

    for (const neighbor of graph.get(node) ?? []) {
      if (!visited.has(neighbor)) {
        visited.add(neighbor);
        queue.push([neighbor, dist + 1]);
      }
    }
  }

  return -1; // unreachable
}
```

**Use BFS when:**

- Shortest path in unweighted graph
- Level-order traversal
- Finding all nodes within distance K

---

### 6.2 DFS — Depth-First Search

**Recursive (cleaner, risk of stack overflow on huge graphs):**

```typescript
function dfs(
  graph: Map<number, number[]>,
  node:  number,
  visited = new Set<number>()
): number[] {
  visited.add(node);
  const result = [node];

  for (const neighbor of graph.get(node) ?? []) {
    if (!visited.has(neighbor)) {
      result.push(...dfs(graph, neighbor, visited));
    }
  }

  return result;
}
```

**Iterative (stack-based, avoids recursion limit):**

```typescript
function dfsIterative(graph: Map<number, number[]>, start: number): number[] {
  const visited = new Set<number>();
  const stack   = [start];
  const result  = [];

  while (stack.length > 0) {
    const node = stack.pop()!;  // pop from top

    if (visited.has(node)) continue;
    visited.add(node);
    result.push(node);

    for (const neighbor of graph.get(node) ?? []) {
      if (!visited.has(neighbor)) {
        stack.push(neighbor);
      }
    }
  }

  return result;
}
```

**Use DFS when:**

- Detecting cycles
- Topological sort
- Connected components
- Maze/path existence problems
- Tree traversal (pre/in/post order)

---

### 6.3 Graph Representation

```typescript
// Adjacency list (most common — space efficient for sparse graphs)
const graph = new Map([
  [0, [1, 2]],
  [1, [0, 3]],
  [2, [0]],
  [3, [1]],
]);

// Build from edge list
function buildGraph(edges: [number, number][], n: number): Map<number, number[]> {
  const graph = new Map<number, number[]>();
  for (let i = 0; i < n; i++) graph.set(i, []);
  for (const [u, v] of edges) {
    graph.get(u)!.push(v);
    graph.get(v)!.push(u); // remove for directed graph
  }
  return graph;
}
```

---

### 6.4 Classic Problems

**Number of Islands (DFS on 2D grid):**

```typescript
function numIslands(grid: string[][]): number {
  const rows = grid.length, cols = grid[0].length;
  let count = 0;

  function dfs(r: number, c: number) {
    if (r < 0 || r >= rows || c < 0 || c >= cols || grid[r][c] !== '1') return;
    grid[r][c] = '0'; // mark visited by mutating
    dfs(r+1, c); dfs(r-1, c); dfs(r, c+1); dfs(r, c-1);
  }

  for (let r = 0; r < rows; r++) {
    for (let c = 0; c < cols; c++) {
      if (grid[r][c] === '1') {
        count++;
        dfs(r, c);
      }
    }
  }

  return count;
}
```

**Clone Graph:**

```typescript
function cloneGraph(node: GraphNode | null): GraphNode | null {
  if (!node) return null;
  const map = new Map<GraphNode, GraphNode>();

  function dfs(n: GraphNode): GraphNode {
    if (map.has(n)) return map.get(n)!;
    const clone = new GraphNode(n.val);
    map.set(n, clone);
    clone.neighbors = n.neighbors.map(dfs);
    return clone;
  }

  return dfs(node);
}
```

**Course Schedule (cycle detection → topological sort):**

```typescript
function canFinish(numCourses: number, prerequisites: number[][]): boolean {
  const graph = new Map<number, number[]>();
  for (let i = 0; i < numCourses; i++) graph.set(i, []);
  for (const [a, b] of prerequisites) graph.get(b)!.push(a);

  // 0 = unvisited, 1 = visiting (in current path), 2 = done
  const state = new Array(numCourses).fill(0);

  function hasCycle(node: number): boolean {
    if (state[node] === 1) return true;  // cycle detected
    if (state[node] === 2) return false; // already processed

    state[node] = 1; // mark as visiting
    for (const neighbor of graph.get(node)!) {
      if (hasCycle(neighbor)) return true;
    }
    state[node] = 2; // mark as done
    return false;
  }

  for (let i = 0; i < numCourses; i++) {
    if (hasCycle(i)) return false;
  }
  return true;
}
```

---

### 6.5 Interview Questions

**Q: When do you use BFS vs DFS?** A: BFS for shortest path in unweighted graphs, level-order problems, "minimum steps" questions. DFS for cycle detection, connected components, topological sort, and path existence. Both are O(V+E).

**Q: How do you handle cycles in graph traversal?** A: Maintain a `visited` set. For cycle detection specifically, use a three-state visited array: unvisited, in-current-path, completed.

**Q: What's the time and space complexity of BFS/DFS?** A: Both O(V+E) time — visit each vertex and edge once. Space: O(V) for the visited set + O(V) for the queue/stack. Recursive DFS also uses O(V) call stack space.

**Q: How do you detect a cycle in a directed graph?** A: DFS with a three-color marking: white (unvisited), gray (currently in DFS path), black (fully processed). A back edge to a gray node means a cycle exists.

---

## 7. Dynamic Programming — Top-Down

### Mental model first

DP solves problems with **overlapping subproblems** and **optimal substructure** by storing results of subproblems to avoid recomputation.

**Top-down (memoization):** Start from the original problem, recurse down, cache results. **Bottom-up (tabulation):** Start from base cases, build up to the answer iteratively.

Top-down is usually easier to derive — write the recursive solution first, then add a cache.

---

### 7.1 The Three-Step Framework

```
1. Define the subproblem: what does dp(i) or dp(i,j) represent?
2. Write the recurrence: how does dp(i) depend on smaller subproblems?
3. Identify the base case: what's the smallest subproblem with a known answer?
```

---

### 7.2 1D DP Patterns

**Fibonacci / Climbing Stairs:**

```typescript
function climbStairs(n: number): number {
  const memo = new Map<number, number>();

  function dp(i: number): number {
    if (i <= 1) return 1;           // base case
    if (memo.has(i)) return memo.get(i)!;
    const result = dp(i-1) + dp(i-2); // recurrence
    memo.set(i, result);
    return result;
  }

  return dp(n);
}
// Time: O(n) | Space: O(n)
```

**House Robber:**

```typescript
function rob(nums: number[]): number {
  const memo = new Map<number, number>();

  function dp(i: number): number {
    if (i >= nums.length) return 0;
    if (memo.has(i)) return memo.get(i)!;
    // at each house: rob it (skip next) or skip it
    const result = Math.max(
      nums[i] + dp(i + 2), // rob house i
      dp(i + 1)            // skip house i
    );
    memo.set(i, result);
    return result;
  }

  return dp(0);
}
```

**Word Break:**

```typescript
function wordBreak(s: string, wordDict: string[]): boolean {
  const words = new Set(wordDict);
  const memo  = new Map<number, boolean>();

  function dp(start: number): boolean {
    if (start === s.length) return true;
    if (memo.has(start)) return memo.get(start)!;

    for (let end = start + 1; end <= s.length; end++) {
      if (words.has(s.slice(start, end)) && dp(end)) {
        memo.set(start, true);
        return true;
      }
    }

    memo.set(start, false);
    return false;
  }

  return dp(0);
}
```

---

### 7.3 2D DP Patterns

**Unique Paths:**

```typescript
function uniquePaths(m: number, n: number): number {
  const memo = new Map<string, number>();

  function dp(r: number, c: number): number {
    if (r === m - 1 || c === n - 1) return 1; // base: edges have 1 path
    const key = `${r},${c}`;
    if (memo.has(key)) return memo.get(key)!;
    const result = dp(r+1, c) + dp(r, c+1);
    memo.set(key, result);
    return result;
  }

  return dp(0, 0);
}
```

**Longest Common Subsequence:**

```typescript
function longestCommonSubsequence(text1: string, text2: string): number {
  const memo = new Map<string, number>();

  function dp(i: number, j: number): number {
    if (i === text1.length || j === text2.length) return 0;
    const key = `${i},${j}`;
    if (memo.has(key)) return memo.get(key)!;

    let result: number;
    if (text1[i] === text2[j]) {
      result = 1 + dp(i+1, j+1); // characters match: include both
    } else {
      result = Math.max(dp(i+1, j), dp(i, j+1)); // skip one
    }

    memo.set(key, result);
    return result;
  }

  return dp(0, 0);
}
```

---

### 7.4 Identifying DP Problems

Ask these questions:

1. Can this be solved with "what's the best choice at each step"? → greedy or DP
2. Does the optimal answer depend on optimal answers to smaller versions? → DP
3. Do subproblems repeat? (Look for parameters that shrink toward a base case)

**Signals a problem is DP:**

- "Maximum/minimum" count/sum
- "Number of ways"
- "Can you achieve X?" (boolean)
- Array/string where you make choices at each index

---

### 7.5 Interview Questions

**Q: What's the difference between memoization and tabulation?** A: Memoization (top-down) adds a cache to a recursive solution — only computes subproblems that are actually needed. Tabulation (bottom-up) builds a table iteratively from base cases — avoids recursion overhead. Both achieve O(n) for 1D DP.

**Q: How do you recognize a DP problem?** A: Optimal substructure (optimal solution is built from optimal subsolutions) + overlapping subproblems (same subproblem computed multiple times). Common signals: "maximum/minimum", "number of ways", "can you reach", choices at each step.

**Q: What's the time and space complexity of a typical 2D DP solution?** A: O(m×n) time and O(m×n) space for the memo table. Space can often be reduced to O(min(m,n)) by only keeping one or two rows at a time (bottom-up tabulation).

**Q: Convert a naive recursive solution to memoized DP.** A: Identify the function parameters that define the subproblem state. Use a Map or array indexed by those parameters as the cache. At the start of each call, check the cache and return if found. At the end, store the result before returning.

---

## 8. Stack, Queue, Heap Patterns

### 8.1 Stack

LIFO (Last In, First Out). In JavaScript: use an array with `push`/`pop`.

**When to think stack:**

- Matching brackets / valid parentheses
- "Previous/next greater element"
- Undo/redo, backtracking
- DFS iterative implementation
- Monotonic stack problems

**Valid Parentheses:**

```typescript
function isValid(s: string): boolean {
  const stack: string[] = [];
  const pairs = { ')': '(', ']': '[', '}': '{' };

  for (const c of s) {
    if ('([{'.includes(c)) {
      stack.push(c);
    } else {
      if (stack.pop() !== pairs[c]) return false;
    }
  }

  return stack.length === 0;
}
```

**Monotonic Stack — Next Greater Element:**

```typescript
function nextGreaterElement(nums: number[]): number[] {
  const result = new Array(nums.length).fill(-1);
  const stack:  number[] = []; // stores indices

  for (let i = 0; i < nums.length; i++) {
    // pop elements smaller than current — current is their next greater
    while (stack.length > 0 && nums[i] > nums[stack.at(-1)!]) {
      const idx = stack.pop()!;
      result[idx] = nums[i];
    }
    stack.push(i);
  }

  return result;
}
```

**Min Stack:**

```typescript
class MinStack {
  private stack:    number[] = [];
  private minStack: number[] = [];

  push(val: number): void {
    this.stack.push(val);
    this.minStack.push(
      Math.min(val, this.minStack.at(-1) ?? Infinity)
    );
  }

  pop(): void {
    this.stack.pop();
    this.minStack.pop();
  }

  top():    number { return this.stack.at(-1)!; }
  getMin(): number { return this.minStack.at(-1)!; }
}
```

---

### 8.2 Queue

FIFO (First In, First Out). Use array with `push`/`shift` — but `shift` is O(n). For performance-critical code, implement a deque or use an index pointer.

```typescript
// Efficient queue using index pointer
class Queue<T> {
  private data: T[] = [];
  private head = 0;

  enqueue(val: T): void { this.data.push(val); }
  dequeue(): T | undefined {
    if (this.isEmpty()) return undefined;
    return this.data[this.head++];
  }
  isEmpty(): boolean { return this.head >= this.data.length; }
  size():    number  { return this.data.length - this.head; }
  peek():    T       { return this.data[this.head]; }
}
```

**When to think queue:**

- BFS
- Level-order tree traversal
- Sliding window problems with deque
- Rate limiting / task scheduling simulations

---

### 8.3 Heap (Priority Queue)

A heap is a complete binary tree where every parent is greater (max-heap) or smaller (min-heap) than its children. Access to the min/max element is O(1); insert and remove are O(log n).

**JavaScript doesn't have a built-in heap.** You need to implement one or use a library. Knowing this implementation is expected at FAANG:

```typescript
class MinHeap {
  private data: number[] = [];

  get size(): number { return this.data.length; }
  peek(): number     { return this.data[0]; }

  push(val: number): void {
    this.data.push(val);
    this._bubbleUp(this.data.length - 1);
  }

  pop(): number | undefined {
    if (this.size === 0) return undefined;
    const min = this.data[0];
    const last = this.data.pop()!;
    if (this.size > 0) {
      this.data[0] = last;
      this._sinkDown(0);
    }
    return min;
  }

  private _bubbleUp(i: number): void {
    while (i > 0) {
      const parent = (i - 1) >> 1;
      if (this.data[parent] <= this.data[i]) break;
      [this.data[parent], this.data[i]] = [this.data[i], this.data[parent]];
      i = parent;
    }
  }

  private _sinkDown(i: number): void {
    const n = this.size;
    while (true) {
      let smallest = i;
      const l = 2*i + 1, r = 2*i + 2;
      if (l < n && this.data[l] < this.data[smallest]) smallest = l;
      if (r < n && this.data[r] < this.data[smallest]) smallest = r;
      if (smallest === i) break;
      [this.data[smallest], this.data[i]] = [this.data[i], this.data[smallest]];
      i = smallest;
    }
  }
}
```

**When to think heap:**

- "K largest/smallest elements"
- "Kth largest element"
- Merge K sorted lists
- Median of a data stream
- Task scheduling by priority
- Dijkstra's shortest path

---

### 8.4 Classic Heap Problems

**K Closest Points to Origin:**

```typescript
function kClosest(points: number[][], k: number): number[][] {
  // Max-heap of size k: keep the k smallest distances
  const heap = new MaxHeap<[number, number[]]>(([d]) => d);

  for (const point of points) {
    const dist = point[0]**2 + point[1]**2;
    heap.push([dist, point]);
    if (heap.size > k) heap.pop(); // evict largest
  }

  return heap.toArray().map(([, point]) => point);
}
```

**Find Median from Data Stream:**

```typescript
class MedianFinder {
  private lo = new MaxHeap(); // lower half
  private hi = new MinHeap(); // upper half

  addNum(num: number): void {
    this.lo.push(num);
    this.hi.push(this.lo.pop()!); // balance: max of lower → upper

    if (this.hi.size > this.lo.size) {
      this.lo.push(this.hi.pop()!); // keep lo >= hi in size
    }
  }

  findMedian(): number {
    if (this.lo.size > this.hi.size) return this.lo.peek();
    return (this.lo.peek() + this.hi.peek()) / 2;
  }
}
```

**Merge K Sorted Lists:**

```typescript
function mergeKLists(lists: ListNode[][]): number[] {
  const heap = new MinHeap();
  const result: number[] = [];

  // Seed heap with first element of each list
  const ptrs = lists.map(() => 0);
  for (let i = 0; i < lists.length; i++) {
    if (lists[i].length > 0) {
      heap.push([lists[i][0], i, 0]); // [value, listIdx, elemIdx]
    }
  }

  while (heap.size > 0) {
    const [val, li, ei] = heap.pop()!;
    result.push(val);
    if (ei + 1 < lists[li].length) {
      heap.push([lists[li][ei + 1], li, ei + 1]);
    }
  }

  return result;
}
// Time: O(N log K) where N = total elements, K = number of lists
```

---

### 8.5 Complexity Reference

|Structure|Access|Search|Insert|Delete|Notes|
|---|---|---|---|---|---|
|Stack (array)|O(n)|O(n)|O(1)|O(1) top|push/pop|
|Queue (index ptr)|O(n)|O(n)|O(1)|O(1) front|enqueue/dequeue|
|Min/Max Heap|O(1) min/max|O(n)|O(log n)|O(log n)|peek O(1)|

---

### 8.6 Interview Questions

**Q: When would you use a monotonic stack?** A: When you need to find the next/previous greater or smaller element for each element in an array. The stack maintains elements in sorted order, so each element is pushed and popped at most once — O(n) total.

**Q: Why use a heap instead of sorting for "K largest elements"?** A: Sorting is O(n log n). A min-heap of size K gives O(n log K) — much better when K << n. You maintain a window of the K largest seen so far, evicting the smallest when the window overflows.

**Q: How does a heap differ from a BST for priority queue operations?** A: A heap guarantees O(1) peek at min/max and O(log n) insert/delete. A BST also gives O(log n) insert/delete but with more overhead per operation. Heaps are cache-friendlier (array-based). BSTs support O(log n) search and ordered traversal, which heaps don't.

**Q: How would you implement a queue using two stacks?** A: Push enqueues to stack1. Dequeue: if stack2 is empty, pop all from stack1 into stack2 (reversing order), then pop from stack2. Amortized O(1) dequeue because each element moves between stacks at most once.

**Q: Design a data structure that supports insert, delete, and getRandom in O(1).** A: HashMap (value → index) + dynamic array. Insert: append to array, add to map. Delete: swap with last element, update map, pop. getRandom: return array[random index]. All O(1) amortized.

---

## Phase 2 — Weekly Study Schedule

|Week|Craft Focus|Interview Focus|
|---|---|---|
|1|Critical Rendering Path — full sequence, render blocking|BFS fundamentals + LC: 102, 200, 994|
|2|Layout, Paint, Composite — animation correctness|DFS fundamentals + LC: 133, 207, 210|
|3|Core Web Vitals — LCP diagnosis and fixes|Graph hard problems + LC: 417, 130, 127|
|4|Core Web Vitals — CLS + INP + measurement|Stack patterns + LC: 20, 84, 739|
|5|Chrome DevTools — flame chart + memory profiling|DP top-down 1D + LC: 70, 198, 139|
|6|Bundle analysis + code splitting in a real project|DP top-down 2D + LC: 1143, 62, 72|
|7|Profiling + fixing a real perf issue end-to-end|Heap patterns + LC: 215, 973, 295|
|8|Review + build perf budget for a side project|Mixed hard problems — LC company-tagged Meta/Google|

**Daily commitment:**

- Craft: 45 min (read primary source + apply to real code)
- Interview: 1–2 LeetCode problems + review editorial for approach

---

## Primary Sources

|Topic|Source|
|---|---|
|Critical Rendering Path|[web.dev — Critical Rendering Path](https://web.dev/articles/critical-rendering-path)|
|Browser Rendering Pipeline|[Jake Archibald — In The Loop (JSConf 2018)](https://www.youtube.com/watch?v=cCOL7MC4Pl0)|
|Core Web Vitals|[web.dev/vitals](https://web.dev/vitals)|
|INP deep dive|[web.dev/articles/inp](https://web.dev/articles/inp)|
|CSS Triggers reference|[csstriggers.com](https://csstriggers.com/)|
|Chrome DevTools Performance|[developer.chrome.com/docs/devtools/performance](https://developer.chrome.com/docs/devtools/performance)|
|Webpack Bundle Analyzer|[github.com/webpack-contrib/webpack-bundle-analyzer](https://github.com/webpack-contrib/webpack-bundle-analyzer)|
|Graph patterns|[Neetcode — Graphs](https://neetcode.io/roadmap)|
|DP patterns|[Neetcode — 2D DP](https://neetcode.io/roadmap)|