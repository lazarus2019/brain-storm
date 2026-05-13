# Critical Rendering Path (CRP) — Ultimate Deep-Dive Guide

## Table of Contents

1. [Big Picture](#1-big-picture)
2. [Browser Rendering Pipeline Deep Dive](#2-browser-rendering-pipeline-deep-dive)
3. [Core Web Vitals & Metrics](#3-core-web-vitals--metrics)
4. [Learning Roadmap by Skill Level](#4-learning-roadmap-by-skill-level)
5. [React / Next.js / Astro Rendering Performance](#5-react--nextjs--astro-rendering-performance)
6. [Setup Guide](#6-setup-guide)
7. [Performance Tooling Comparison](#7-performance-tooling-comparison)
8. [Cheatsheet](#8-cheatsheet)
9. [Real-World Engineering Mindset](#9-real-world-engineering-mindset)
10. [Brainstorm / Open Questions](#10-brainstorm--open-questions)
11. [Practice Questions](#11-practice-questions)
12. [Personalized Recommendations](#12-personalized-recommendations)
13. [Official Documentation & Reference Links](#13-official-documentation--reference-links)
14. [Advanced Engineering Topics](#14-advanced-engineering-topics)

---

## 1. Big Picture

### What Is the Critical Rendering Path?

The Critical Rendering Path (CRP) is the sequence of steps a browser must complete to convert HTML, CSS, and JavaScript into pixels on screen. It represents the minimum work required to render the **first frame** of a page.

**WHY it matters:** Every millisecond spent in the CRP delays the user seeing content. On mobile devices with constrained CPU/GPU/network, CRP inefficiency compounds into seconds of blank screen.

**Problems CRP optimization solves:**
- Blank white screens on initial load
- Slow First Contentful Paint (FCP)
- Poor Largest Contentful Paint (LCP)
- Unnecessary render-blocking resources
- Hydration delays in SSR apps
- Layout shifts from late-loading resources
- Poor mobile performance on 3G/4G networks

### Key Concepts Differentiated

| Concept | What It Is | When It Happens |
|---------|------------|-----------------|
| **Parsing** | Converting raw bytes (HTML/CSS/JS) into structured trees (DOM/CSSOM/AST) | Network → Parser |
| **Rendering** | The full pipeline from DOM+CSSOM → pixels on screen | After parse, before display |
| **Style Recalculation** | Recomputing which CSS rules apply to which DOM nodes | After DOM/CSS changes |
| **Layout (Reflow)** | Computing geometry (position, size) of every visible element | After style recalc, on geometry changes |
| **Paint** | Filling in pixels (colors, text, images, borders) into paint records | After layout |
| **Compositing** | Combining painted layers into final screen image (GPU-accelerated) | After paint |
| **Hydration** | Attaching JS event handlers to server-rendered HTML | Client-side, after SSR HTML arrives |
| **Reflow** | Re-running layout due to geometry changes (expensive) | DOM mutation, style change, resize |
| **Repaint** | Re-painting without layout change (e.g., color change) | Visual-only property changes |

### The Full Rendering Lifecycle

```
Network Request
    │
    ▼
┌─────────────────────────────────────────────────────┐
│  HTML Parser (incremental, byte-stream)             │
│  ├── Builds DOM tree                                │
│  ├── Preload Scanner (speculative fetches)          │
│  └── Encounters <link>, <script>, <style>           │
└─────────────────────────────────────────────────────┘
    │                    │                    │
    ▼                    ▼                    ▼
┌──────────┐      ┌──────────┐      ┌──────────────┐
│ CSS Parse │      │ JS Exec  │      │ Subresource  │
│ → CSSOM   │      │ (blocks  │      │ Fetches      │
│           │      │  parser) │      │ (preloaded)  │
└──────────┘      └──────────┘      └──────────────┘
    │                    │
    ▼                    ▼
┌─────────────────────────────────────────────────────┐
│  Render Tree Construction                           │
│  DOM + CSSOM → only visible nodes                   │
│  (display:none excluded, ::before included)         │
└─────────────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────────────┐
│  Layout (Reflow)                                    │
│  Compute exact position & size of every element     │
│  Box model, flexbox, grid calculations              │
└─────────────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────────────┐
│  Paint                                              │
│  Generate paint records (draw commands)             │
│  Per-layer painting                                 │
└─────────────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────────────┐
│  Compositing                                        │
│  Layers → GPU tiles → rasterize → composite        │
│  Final pixels on screen                             │
└─────────────────────────────────────────────────────┘
    │
    ▼
  FIRST RENDER (First Contentful Paint)
```

### Rendering Approaches Compared

| Approach | HTML Source | JS Bundle | Time to First Paint | Interactivity | CRP Impact |
|----------|-----------|-----------|--------------------:|---------------|------------|
| **CSR** | Empty shell | Full app | Slow (wait for JS) | After JS parse+exec | Heavy — entire app is CRP-blocking |
| **SSR** | Full HTML | Full app | Fast (HTML arrives) | After hydration | Medium — HTML fast, hydration costly |
| **SSG** | Full HTML (pre-built) | Minimal | Very fast (CDN) | After hydration | Light — static HTML + minimal JS |
| **Streaming SSR** | Chunks arrive progressively | Selective | Progressive | Progressive hydration | Optimized — unblocks rendering early |
| **Islands** | Full HTML | Per-island | Very fast | Per-island hydration | Minimal — only interactive islands load JS |
| **Partial Hydration** | Full HTML | Subset | Very fast | Selective | Minimal — hydrate only what needs it |

### When CRP Optimization Matters Most

- **Mobile users on slow networks** — every render-blocking resource adds seconds
- **Landing pages** — bounce rate directly correlates with load time
- **E-commerce** — 100ms delay = measurable revenue loss
- **SEO** — Core Web Vitals are ranking factors
- **Low-end devices** — CPU-constrained, layout/paint are expensive

### When Over-Optimization Becomes Harmful

- Inlining ALL CSS creates large HTML documents that can't be cached
- Aggressive code splitting creates waterfall chains
- Too many layers cause GPU memory pressure on mobile
- Premature optimization obscures code maintainability
- Over-lazy-loading causes content to pop in, hurting CLS

---

## 2. Browser Rendering Pipeline Deep Dive

### HTML Parser Internals

The HTML parser is **incremental** — it processes bytes as they arrive from the network. It does NOT wait for the full document.

**Key behaviors:**
- Tokenizer converts bytes → tokens (start tags, end tags, text, comments)
- Tree constructor builds DOM from tokens
- Parser is **reentrant** — can be paused/resumed
- Synchronous `<script>` blocks the parser completely
- Parser maintains an **insertion mode** state machine (in body, in head, in table, etc.)

**Speculative Parsing (Preload Scanner):**
When the main parser is blocked by a synchronous script, a **secondary parser** (preload scanner) continues scanning ahead to discover resources to fetch:
- Images
- Stylesheets
- Scripts
- Fonts (via CSS)

This is why resources are fetched even when scripts block — the preload scanner is doing speculative work. **This is one of the most impactful browser optimizations.**

### CSS Blocking Behavior

**CSS is render-blocking, NOT parser-blocking.**

- The HTML parser continues building the DOM while CSS loads
- But the browser will NOT render anything until CSSOM is complete for all render-blocking stylesheets
- WHY: Rendering without CSS would cause a flash of unstyled content (FOUC)

```
DOM ready ────────────────────→ (waiting for CSSOM)
CSSOM ready ──────────────────→ 
                                 ↓
                            Render Tree Construction
```

**Implications:**
- Large CSS files directly delay first paint
- CSS in `<head>` blocks rendering of everything below
- Media-specific stylesheets (`media="print"`) don't block rendering for screen

### JavaScript Execution & Blocking

| Script Type | Parser Blocking | Execution Timing | Order Preserved |
|-------------|:-:|----------------|:-:|
| `<script>` (inline) | ✅ Yes | Immediately | ✅ |
| `<script src>` (no attr) | ✅ Yes | After download | ✅ |
| `<script async>` | ❌ No | ASAP after download | ❌ |
| `<script defer>` | ❌ No | After DOM parsed, before DOMContentLoaded | ✅ |
| `<script type="module">` | ❌ No (deferred by default) | After DOM parsed | ✅ |
| `<script type="module" async>` | ❌ No | ASAP after download | ❌ |

**WHY synchronous scripts block:**
The script might call `document.write()` which modifies the token stream. The parser cannot continue safely without knowing if the document will be modified.

### Layout Thrashing

Layout thrashing occurs when JavaScript repeatedly reads layout properties and then writes to the DOM, forcing the browser to recalculate layout synchronously multiple times in a single frame.

```javascript
// BAD — forces layout recalculation on every iteration
for (let i = 0; i < elements.length; i++) {
  const height = elements[i].offsetHeight; // READ → forces layout
  elements[i].style.height = height * 2 + 'px'; // WRITE → invalidates layout
}

// GOOD — batch reads, then batch writes
const heights = elements.map(el => el.offsetHeight); // All reads first
elements.forEach((el, i) => {
  el.style.height = heights[i] * 2 + 'px'; // All writes after
});
```

**Properties that trigger forced synchronous layout:**
- `offsetTop/Left/Width/Height`
- `clientTop/Left/Width/Height`
- `scrollTop/Left/Width/Height`
- `getComputedStyle()`
- `getBoundingClientRect()`
- `innerText` (requires layout to compute)

### Compositor Thread & GPU Acceleration

The browser has multiple threads:

```
┌────────────────────────────────────────────────┐
│  Main Thread                                   │
│  - JavaScript execution                        │
│  - Style calculation                           │
│  - Layout                                      │
│  - Paint (generate display list)               │
└────────────────────────────────────────────────┘
         │ (paint records)
         ▼
┌────────────────────────────────────────────────┐
│  Compositor Thread                             │
│  - Layer management                            │
│  - Scroll handling (without main thread)       │
│  - CSS animations (transform, opacity)         │
│  - Commit layers to GPU                        │
└────────────────────────────────────────────────┘
         │ (tiles)
         ▼
┌────────────────────────────────────────────────┐
│  Raster Threads (GPU Process)                  │
│  - Rasterize tiles into bitmaps                │
│  - GPU texture upload                          │
│  - Final compositing                           │
└────────────────────────────────────────────────┘
```

**WHY this matters:**
- Animations using `transform` and `opacity` run on the compositor thread — they don't block the main thread
- Animations using `width`, `height`, `top`, `left` require layout → paint → composite on the main thread
- Scroll is handled by compositor — that's why scroll is usually smooth even when main thread is busy

### Frame Budget

At 60fps, each frame has **16.67ms** budget:

```
16.67ms per frame
├── JavaScript: ~10ms max recommended
├── Style recalculation: ~1-2ms
├── Layout: ~1-2ms
├── Paint: ~1-2ms
└── Composite: ~1ms
    (+ overhead)
```

**Long tasks** (>50ms) cause jank. The browser cannot update the screen during a long task.

### Browser Engine Differences

| Feature | Blink (Chrome) | WebKit (Safari) | Gecko (Firefox) |
|---------|---------------|-----------------|-----------------|
| Layer promotion | Aggressive (will-change) | Conservative | Moderate |
| Compositor | Threaded compositor | Single-process compositor | WebRender (GPU-first) |
| Rasterization | GPU rasterization (default) | CPU rasterization (mostly) | GPU via WebRender |
| Font rendering | Skia | Core Text | FreeType |
| Scheduling | RendererScheduler | RunLoop | Task controller |
| Paint | Skia → GPU | Core Graphics | WebRender |

**Mobile differences:**
- GPU memory is shared with system — excessive layers cause OOM crashes
- CPU thermal throttling reduces performance over time
- Touch event handling can block compositor if not passive
- Safari has unique compositing behavior with `overflow: scroll`

---

## 3. Core Web Vitals & Metrics

### Largest Contentful Paint (LCP)

| Aspect | Detail |
|--------|--------|
| **What it measures** | Time until the largest visible content element is rendered |
| **Good threshold** | ≤ 2.5s |
| **Poor threshold** | > 4.0s |
| **Elements considered** | `<img>`, `<video>`, background-image, block-level text |
| **Browser-level meaning** | Render tree painted the largest element to screen |

**Common causes of poor LCP:**
1. Render-blocking CSS/JS delays render tree construction
2. Large hero images without preload
3. Web fonts blocking text paint (FOIT)
4. Server response time (TTFB)
5. Client-side rendering (no HTML content until JS executes)
6. Third-party scripts competing for bandwidth/CPU

**Optimization strategies:**
- Preload LCP image: `<link rel="preload" as="image" href="hero.webp">`
- Inline critical CSS
- Use `fetchpriority="high"` on LCP image
- Eliminate render-blocking resources
- Use SSR/SSG for above-the-fold content
- Optimize TTFB via CDN/edge

**React implications:** Hydration delays LCP when the LCP element depends on client-side state or dynamic rendering.

### Cumulative Layout Shift (CLS)

| Aspect | Detail |
|--------|--------|
| **What it measures** | Total unexpected layout shifts during page lifetime |
| **Good threshold** | ≤ 0.1 |
| **Poor threshold** | > 0.25 |
| **Calculation** | impact fraction × distance fraction |
| **Browser-level meaning** | Layout recalculation moved visible elements after paint |

**Common causes:**
1. Images/iframes without explicit dimensions
2. Dynamically injected content above viewport
3. Web fonts causing text reflow (FOUT)
4. Ads/embeds without reserved space
5. Late-loading CSS changing layout
6. React hydration mismatch causing re-render

**Optimization:**
- Always set `width`/`height` or `aspect-ratio` on images/videos
- Reserve space for dynamic content
- Use `font-display: optional` or size-adjusted fallback fonts
- Avoid inserting content above existing content
- Use CSS `contain` for isolated components

### Interaction to Next Paint (INP)

| Aspect | Detail |
|--------|--------|
| **What it measures** | Responsiveness — time from user interaction to next visual update |
| **Good threshold** | ≤ 200ms |
| **Poor threshold** | > 500ms |
| **Interactions** | click, tap, keypress (NOT scroll, hover) |
| **Browser-level meaning** | Main thread processing time + rendering time for response |

**Common causes of poor INP:**
1. Long tasks blocking main thread
2. Heavy React re-renders on interaction
3. Synchronous layout calculations in event handlers
4. Large DOM trees (slow style recalculation)
5. Excessive third-party scripts

**Optimization:**
- Break long tasks with `scheduler.yield()` or `setTimeout`
- Use `startTransition` in React for non-urgent updates
- Minimize DOM size
- Debounce/throttle expensive handlers
- Use web workers for heavy computation
- Virtualize long lists

### Other Key Metrics

| Metric | What | Good | Browser Meaning |
|--------|------|------|-----------------|
| **FCP** | First Contentful Paint | ≤ 1.8s | First DOM content painted (text, image, canvas) |
| **TTFB** | Time to First Byte | ≤ 0.8s | Server processing + network latency |
| **TBT** | Total Blocking Time | ≤ 200ms | Sum of time tasks exceed 50ms (between FCP and TTI) |
| **Speed Index** | Visual completeness over time | ≤ 3.4s | How quickly viewport is visually populated |

### Lab Data vs Field Data

| Aspect | Lab (Synthetic) | Field (RUM) |
|--------|----------------|-------------|
| **Source** | Controlled environment | Real users |
| **Tools** | Lighthouse, WebPageTest | CrUX, Analytics RUM |
| **Consistency** | Reproducible | Variable |
| **Coverage** | Single device/network | All devices/networks |
| **Use case** | Debugging, CI/CD | Real-world impact |
| **Metrics** | All metrics | CWV subset |
| **Mobile testing** | Simulated throttling | Actual devices |

**RUM Architecture:**
```
User Browser
    │
    ├── PerformanceObserver (LCP, CLS, INP)
    ├── Navigation Timing API
    ├── Resource Timing API
    └── Long Task API
         │
         ▼
    Beacon/fetch → Analytics Endpoint → Dashboard
```

---

## 4. Learning Roadmap by Skill Level

### Level 1 — Newbie

**Core concepts:**
- HTML is parsed top-to-bottom, building a DOM tree
- CSS creates a CSSOM — both DOM + CSSOM needed before rendering
- Scripts without `defer`/`async` block HTML parsing
- Images don't block rendering but cause layout shifts without dimensions
- Fonts can block text painting (FOIT/FOUT)

**Common beginner mistakes:**
1. Placing `<script>` in `<head>` without defer/async
2. Loading unused CSS for the page
3. Using enormous unoptimized images
4. Not specifying image dimensions
5. Loading all JavaScript upfront
6. Using custom fonts without fallback strategy
7. Not understanding why pages show blank before content appears
8. Ignoring mobile network constraints
9. Adding too many third-party scripts
10. Not using browser DevTools Network tab

**Exercises:**
1. Open DevTools Network tab → identify render-blocking resources on any site
2. Add `defer` to a script and observe DOMContentLoaded timing change
3. Remove a CSS file and observe FOUC behavior
4. Add `width`/`height` to all images on a page and measure CLS
5. Use Lighthouse on a personal project and fix one red metric
6. Compare page load with/without a large synchronous script
7. Implement lazy loading for below-fold images
8. Move a CSS `<link>` from `<body>` to `<head>` and observe rendering difference
9. Use `font-display: swap` and observe text visibility during font load
10. Throttle network to Slow 3G in DevTools and experience a typical user's load

### Level 2 — Junior

**Core concepts:**
- `<link rel="preload">` — tell browser to fetch resource early
- `<link rel="prefetch">` — hint for next navigation
- Lazy loading with `loading="lazy"` (images, iframes)
- Code splitting — load only what's needed for current route
- Critical CSS — inline above-fold CSS, defer the rest
- Hydration — attaching event handlers to server-rendered HTML
- Layout shifts from dynamic content insertion
- Network waterfall — serial dependency chains

**Anti-patterns:**
- Preloading everything (wastes bandwidth, no prioritization)
- Lazy loading above-fold images (delays LCP)
- Code splitting too aggressively (waterfall chains)
- Not measuring before optimizing
- Ignoring third-party script impact

**Mini project ideas:**
1. Build a landing page scoring 100 on Lighthouse Performance
2. Implement critical CSS extraction for a multi-page site
3. Set up route-based code splitting in a React app
4. Create a font loading strategy with size-adjusted fallbacks
5. Build an image component with responsive srcset and lazy loading
6. Analyze and fix a waterfall chain in a Next.js app
7. Implement a performance budget in CI (fail build if bundle > X KB)
8. Build a skeleton loading UI that prevents layout shifts
9. Compare SSR vs CSR load performance with WebPageTest
10. Create a resource hints strategy (`preload`, `preconnect`, `dns-prefetch`)

### Level 3 — Senior

**Core concepts:**
- Rendering pipeline debugging via Performance tab
- Compositing optimization — promote animation layers with `will-change`
- Layer strategy — balance layer count vs memory
- React rendering performance — memo, useMemo, useCallback trade-offs
- Streaming SSR with React 18 `renderToPipeableStream`
- Partial/selective hydration
- Island architecture (Astro)
- Advanced caching (stale-while-revalidate, cache partitioning)
- CDN strategy (edge rendering, cache keys, invalidation)
- Long task breaking with `scheduler.yield()`

**Production-grade project examples:**
1. Implement streaming SSR with selective hydration in Next.js
2. Build a virtualized list handling 100k items with stable scroll performance
3. Create a performance monitoring dashboard with RUM data
4. Architect an island-based page with Astro mixing React/Svelte
5. Build CI/CD pipeline with Lighthouse CI and performance regression alerts
6. Implement image optimization pipeline (responsive, WebP/AVIF, CDN)
7. Create a font subsetting and loading pipeline for multi-brand site
8. Build a React app with zero layout shifts (CLS = 0)
9. Implement resource prioritization strategy for an e-commerce PDP
10. Architect a dashboard with virtualization, web workers, and compositor animations

### Level 4 — Expert

**Core concepts:**
- Browser scheduling: how the event loop prioritizes tasks
- Rendering invalidation: what triggers style/layout/paint and at what cost
- Compositor thread: what CAN and CANNOT run off main thread
- GPU pipeline: texture upload, tile management, memory pressure
- Memory implications: layer count, bitmap cache, DOM size
- Advanced profiling: Chrome tracing, Perfetto, `performance.mark/measure`

**What experts care about that juniors miss:**
- Layout containment (`contain: layout`) to prevent cascading invalidation
- Font metric overrides to eliminate CLS from font swap
- Third-party script isolation (iframe sandboxing, Partytown)
- Rendering cost of large DOM trees (>1500 nodes)
- Animation jank from GC pauses
- HTTP/2 push vs preload trade-offs (push is deprecated)
- Priority Hints API (`fetchpriority`)
- Speculative loading (`Speculation-Rules` API)
- View Transitions API for smoother navigation
- Scheduler API for task prioritization

**Advanced discussion topics:**
1. When does promoting a layer hurt more than help?
2. How does `content-visibility: auto` affect rendering cost?
3. What's the actual cost of React reconciliation vs DOM mutation?
4. How does streaming SSR interact with browser progressive rendering?
5. When should you use web workers vs main thread?
6. How does HTTP/3 change resource loading strategy?
7. What's the memory cost of will-change on mobile?
8. How does CSS containment affect layout invalidation scope?
9. When is `requestAnimationFrame` not enough?
10. How do you architect performance governance for a 50-engineer team?
11. What's the performance cost of CSS-in-JS at scale?
12. How do you handle performance on low-end Android (2GB RAM)?
13. What's the rendering cost of shadow DOM?
14. How does edge rendering change CRP optimization?
15. When should you pre-render vs server-render vs client-render?

### Level 5 — Browser / Rendering Engineer Mindset

**Blink rendering architecture:**
```
                   Blink
                     │
    ┌────────────────┼────────────────┐
    │                │                │
 DOM/Style       Layout Engine     Paint
 (StyleEngine)   (LayoutNG)       (Paint → DisplayList)
    │                │                │
    └────────────────┼────────────────┘
                     │
              Compositor (cc/)
                     │
              ┌──────┴──────┐
              │             │
         Tile Manager   GPU Process
              │             │
              └──────┬──────┘
                     │
                  Display
```

**Threading model:**
- **Main thread (Renderer):** DOM, Style, Layout, Paint, JS
- **Compositor thread:** Scrolling, CSS transform/opacity animations, layer tree management
- **Raster threads:** Tile rasterization (can use GPU)
- **GPU process:** Shared across all renderer processes, handles actual GPU commands

**Scheduler internals:**
- Tasks are prioritized: User-blocking > User-visible > Background
- Rendering is interleaved with JS via `requestAnimationFrame`
- Input events get highest priority
- Long tasks (>50ms) delay rendering frames

**Future browser rendering directions:**
- WebGPU for compute-heavy rendering
- View Transitions API for app-like navigation
- Speculation Rules for instant navigation
- CSS `@scope` for style containment
- Scroll-driven animations (off main thread)
- `content-visibility` for rendering on demand
- MathML Core re-implementation
- Better font rendering with font metric overrides

---

## 5. React / Next.js / Astro Rendering Performance

### WHY React Apps Often Become CRP-Heavy

1. **Bundle size:** React + ReactDOM ≈ 45KB gzipped — must download, parse, execute before anything interactive
2. **CSR by default:** Without SSR, browser sees empty `<div id="root">` — CRP produces blank screen
3. **Hydration cost:** Server-rendered HTML still needs full JS to become interactive
4. **Component tree depth:** Deep trees mean expensive reconciliation
5. **State-driven re-renders:** Unoptimized state causes cascade re-renders
6. **CSS-in-JS runtime:** Styled-components/Emotion inject styles at runtime, blocking paint

### WHY Hydration Becomes Expensive

```
Server HTML arrives (fast FCP)
    │
    ▼
Browser must:
1. Download entire JS bundle
2. Parse JavaScript
3. Execute React
4. React walks entire tree comparing server HTML to virtual DOM
5. Attach event handlers
    │
    ▼
Page is interactive (slow TTI)
```

On low-end mobile: Steps 1-5 can take **3-10 seconds**. During this time, the page LOOKS interactive but clicking does nothing.

### React Optimization Patterns

```jsx
// Streaming SSR (React 18)
import { renderToPipeableStream } from 'react-dom/server';

const { pipe } = renderToPipeableStream(<App />, {
  bootstrapScripts: ['/main.js'],
  onShellReady() {
    // Shell (layout + loading states) rendered
    response.statusCode = 200;
    pipe(response);
  },
});

// Selective hydration with Suspense
function Page() {
  return (
    <Layout>
      <Header /> {/* Hydrates immediately */}
      <Suspense fallback={<Skeleton />}>
        <HeavyContent /> {/* Hydrates when ready */}
      </Suspense>
      <Suspense fallback={<Skeleton />}>
        <Comments /> {/* Hydrates last, or on interaction */}
      </Suspense>
    </Layout>
  );
}
```

### Next.js Rendering Strategies

| Strategy | Use When | CRP Impact |
|----------|----------|------------|
| Static (SSG) | Content doesn't change per-request | Minimal — served from CDN |
| ISR | Content changes occasionally | Low — cached + background regen |
| Server Components | Component doesn't need interactivity | Low — zero client JS |
| Streaming SSR | Dynamic content, fast TTFB needed | Optimized — progressive rendering |
| Client Component | Needs browser APIs, interactivity | Higher — requires hydration |

```tsx
// Next.js App Router — Server Component (zero client JS)
async function ProductPage({ id }: { id: string }) {
  const product = await getProduct(id); // Runs on server only
  return (
    <div>
      <h1>{product.name}</h1>
      <Image
        src={product.image}
        width={800}
        height={600}
        priority // Preloads LCP image
        fetchPriority="high"
      />
      <AddToCartButton product={product} /> {/* Client Component */}
    </div>
  );
}
```

### Astro Islands Architecture

```astro
---
// This runs at build time / server time — zero client JS
import Header from '../components/Header.astro';
import ProductCard from '../components/ProductCard.astro';
import CartWidget from '../components/CartWidget.tsx';
---

<Header /> <!-- Static HTML, no JS -->
<ProductCard /> <!-- Static HTML, no JS -->

<!-- Only this island ships JS to the client -->
<CartWidget client:visible />
<!-- Hydrates only when scrolled into view -->
```

**Astro hydration directives:**
| Directive | When It Hydrates | Use Case |
|-----------|-----------------|----------|
| `client:load` | Immediately on page load | Critical interactive UI |
| `client:idle` | After page is idle (requestIdleCallback) | Non-urgent interactivity |
| `client:visible` | When scrolled into viewport | Below-fold components |
| `client:media` | When media query matches | Mobile-only components |
| `client:only` | Client-only (no SSR) | Browser-API-dependent |

### WHY SSR Can Still Feel Slow

1. **TTFB latency:** Server computation + database queries delay first byte
2. **Large HTML payload:** Full HTML document takes time to download
3. **Hydration gap:** Page looks ready but isn't interactive
4. **Blocking hydration:** Entire tree must hydrate before any interaction works
5. **JavaScript parse cost:** Even with HTML present, JS must be parsed/compiled

**Solution: Streaming + Selective Hydration + Islands**

---

## 6. Setup Guide

### Performance Workflow for React/Next.js/Astro/Vite Stack

```
1. Measure (Lighthouse + RUM)
    │
2. Identify bottleneck (Network? JS? Layout? Paint?)
    │
3. Fix highest-impact issue
    │
4. Verify fix (re-measure)
    │
5. Automate (CI/CD budget)
    │
6. Monitor (RUM alerts)
```

### Lighthouse Setup

```bash
# CLI
npm install -g lighthouse
lighthouse https://example.com --output=html --output-path=./report.html

# CI with Lighthouse CI
npm install -g @lhci/cli
lhci autorun --config=lighthouserc.json
```

```json
// lighthouserc.json
{
  "ci": {
    "collect": {
      "url": ["http://localhost:3000"],
      "numberOfRuns": 3
    },
    "assert": {
      "assertions": {
        "categories:performance": ["error", { "minScore": 0.9 }],
        "largest-contentful-paint": ["error", { "maxNumericValue": 2500 }],
        "cumulative-layout-shift": ["error", { "maxNumericValue": 0.1 }],
        "interactive": ["error", { "maxNumericValue": 3800 }]
      }
    },
    "upload": {
      "target": "temporary-public-storage"
    }
  }
}
```

### Chrome DevTools Performance Profiling

1. **Performance tab:** Record → interact → stop → analyze flame chart
2. **Key things to look for:**
   - Long tasks (red corners)
   - Layout recalculations (purple bars)
   - Paint events (green bars)
   - Idle time (gray)
3. **Network tab:** Waterfall view → identify blocking chains
4. **Rendering tab:** Enable "Paint flashing", "Layout shift regions"
5. **Layers tab:** Inspect compositing layers and memory

### Bundle Analysis Setup (Vite)

```bash
# vite-plugin-bundle-analyzer
npm install -D rollup-plugin-visualizer

# vite.config.ts
import { visualizer } from 'rollup-plugin-visualizer';

export default defineConfig({
  plugins: [
    visualizer({
      open: true,
      gzipSize: true,
      brotliSize: true,
    }),
  ],
});
```

### Next.js Optimization Setup

```tsx
// next.config.js
module.exports = {
  images: {
    formats: ['image/avif', 'image/webp'],
    deviceSizes: [640, 750, 828, 1080, 1200, 1920],
  },
  experimental: {
    optimizeCss: true, // Critical CSS extraction
  },
};
```

### Image Optimization

```html
<!-- Responsive images with modern formats -->
<picture>
  <source srcset="hero.avif" type="image/avif">
  <source srcset="hero.webp" type="image/webp">
  <img
    src="hero.jpg"
    alt="Hero"
    width="1200"
    height="600"
    loading="eager"
    fetchpriority="high"
    decoding="async"
  >
</picture>
```

### Font Optimization

```html
<!-- Preload critical font -->
<link rel="preload" href="/fonts/Inter-var.woff2" as="font" type="font/woff2" crossorigin>

<style>
@font-face {
  font-family: 'Inter';
  src: url('/fonts/Inter-var.woff2') format('woff2');
  font-display: optional; /* Best for CLS — no layout shift */
  /* Size-adjusted fallback for zero CLS */
  size-adjust: 107%;
  ascent-override: 90%;
  descent-override: 22%;
  line-gap-override: 0%;
}
</style>
```

### Performance Budget in CI/CD

```yaml
# GitHub Actions example
- name: Bundle size check
  run: |
    npm run build
    MAX_SIZE=200000  # 200KB
    ACTUAL=$(stat -f%z dist/assets/index-*.js 2>/dev/null || stat --printf="%s" dist/assets/index-*.js)
    if [ "$ACTUAL" -gt "$MAX_SIZE" ]; then
      echo "❌ Bundle too large: ${ACTUAL} bytes (max: ${MAX_SIZE})"
      exit 1
    fi
```

### Real-User Monitoring Setup

```typescript
// Lightweight RUM with web-vitals library
import { onLCP, onCLS, onINP } from 'web-vitals';

function sendMetric(metric: { name: string; value: number; id: string }) {
  navigator.sendBeacon('/api/metrics', JSON.stringify(metric));
}

onLCP(sendMetric);
onCLS(sendMetric);
onINP(sendMetric);
```

---

## 7. Performance Tooling Comparison

| Tool | Purpose | Pros | Cons | CI/CD | Learning Curve |
|------|---------|------|------|:-----:|:-:|
| **Lighthouse** | Audit overall performance | Free, comprehensive, actionable | Lab only, simulated throttling | ✅ | Low |
| **WebPageTest** | Deep waterfall & video analysis | Real devices, multi-location, filmstrip | Complex UI, slower | ✅ | Medium |
| **Chrome DevTools** | Real-time debugging | Live profiling, flame chart, layers | Manual, not automated | ❌ | Medium |
| **PageSpeed Insights** | Quick CWV check (lab + field) | Includes CrUX data, free | Limited detail | ❌ | Low |
| **Calibre** | Continuous monitoring | Alerting, budgets, trends | Paid | ✅ | Medium |
| **SpeedCurve** | Performance visualization | Beautiful dashboards, competitive analysis | Paid, expensive | ✅ | Medium |
| **Bundle Analyzer** | JS bundle composition | Visual treemap, find bloat | Build-time only | ✅ | Low |
| **React Profiler** | React render performance | Component-level timing | React-only, dev mode | ❌ | Medium |
| **Perfetto** | Low-level browser tracing | Chrome internals, thread-level | Very complex | ❌ | High |
| **Chrome Tracing** | Browser process tracing | Full rendering pipeline | Expert-level | ❌ | High |

### When to Use What

| Scenario | Best Tool |
|----------|-----------|
| Quick performance check | PageSpeed Insights |
| Debug specific rendering issue | Chrome DevTools Performance tab |
| CI/CD performance gate | Lighthouse CI |
| Understand load waterfall | WebPageTest |
| React re-render debugging | React Profiler |
| Bundle size monitoring | Bundle Analyzer in CI |
| Browser internals debugging | Perfetto / Chrome Tracing |
| Continuous monitoring | Calibre / SpeedCurve |
| Real-user impact | RUM (web-vitals + analytics) |

---

## 8. Cheatsheet

### Script Loading Patterns

```html
<!-- Critical inline script (rare) -->
<script>/* only for critical above-fold logic */</script>

<!-- Standard deferred (most scripts) -->
<script defer src="/main.js"></script>

<!-- Async for independent scripts (analytics) -->
<script async src="/analytics.js"></script>

<!-- Module (deferred by default) -->
<script type="module" src="/app.js"></script>

<!-- Preload critical script -->
<link rel="preload" as="script" href="/critical.js">

<!-- Prefetch for next page -->
<link rel="prefetch" as="script" href="/next-page.js">
```

### Critical CSS Pattern

```html
<head>
  <!-- Inline critical CSS -->
  <style>
    /* Above-fold styles only */
    .header { ... }
    .hero { ... }
  </style>

  <!-- Defer full CSS -->
  <link rel="preload" href="/styles.css" as="style" onload="this.onload=null;this.rel='stylesheet'">
  <noscript><link rel="stylesheet" href="/styles.css"></noscript>
</head>
```

### Image Optimization Patterns

```html
<!-- LCP image: eager + high priority -->
<img src="hero.webp" fetchpriority="high" loading="eager" decoding="async" width="1200" height="600" alt="">

<!-- Below-fold: lazy -->
<img src="card.webp" loading="lazy" decoding="async" width="400" height="300" alt="">

<!-- Responsive -->
<img srcset="img-400.webp 400w, img-800.webp 800w, img-1200.webp 1200w"
     sizes="(max-width: 600px) 400px, (max-width: 1000px) 800px, 1200px"
     src="img-800.webp" alt="">
```

### Layout Thrashing Fixes

```javascript
// ❌ Read-write-read-write
elements.forEach(el => {
  el.style.width = el.offsetWidth + 10 + 'px';
});

// ✅ Batch reads, then batch writes
const widths = elements.map(el => el.offsetWidth);
elements.forEach((el, i) => {
  el.style.width = widths[i] + 10 + 'px';
});

// ✅ Use requestAnimationFrame
requestAnimationFrame(() => {
  // All DOM writes here
});
```

### GPU Optimization Patterns

```css
/* ✅ Compositor-only animation (smooth, off main thread) */
.animate {
  will-change: transform;
  transform: translateX(0);
  transition: transform 0.3s ease;
}
.animate:hover {
  transform: translateX(100px);
}

/* ❌ Main-thread animation (causes layout + paint) */
.animate-bad {
  transition: left 0.3s ease;
  left: 0;
}
.animate-bad:hover {
  left: 100px;
}

/* Promote to own layer (use sparingly) */
.layer {
  will-change: transform;
  /* or: transform: translateZ(0); — hack, less ideal */
}

/* Content visibility for off-screen content */
.below-fold {
  content-visibility: auto;
  contain-intrinsic-size: 0 500px;
}
```

### React Optimization Patterns

```tsx
// ✅ Lazy load routes
const Dashboard = lazy(() => import('./Dashboard'));

// ✅ Use startTransition for non-urgent updates
function Search() {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState([]);

  function handleChange(e) {
    setQuery(e.target.value); // Urgent: update input
    startTransition(() => {
      setResults(search(e.target.value)); // Non-urgent: can be interrupted
    });
  }
}

// ✅ Virtualize long lists
import { useVirtualizer } from '@tanstack/react-virtual';
```

### Performance Debugging Checklist

- [ ] Check TTFB (server/CDN issue?)
- [ ] Check render-blocking resources (Network tab, coverage)
- [ ] Check LCP element (is it preloaded? fetchpriority?)
- [ ] Check JS bundle size (too large? code split?)
- [ ] Check long tasks (Performance tab → Main thread)
- [ ] Check layout shifts (Rendering tab → Layout Shift Regions)
- [ ] Check font loading (FOIT/FOUT?)
- [ ] Check third-party scripts (blocking main thread?)
- [ ] Check image optimization (format, size, lazy/eager)
- [ ] Check hydration cost (React Profiler)
- [ ] Check compositor layers (Layers tab — too many?)
- [ ] Check mobile performance (throttle CPU 4x + Slow 3G)

### Mobile Optimization Checklist

- [ ] Test on real low-end device (not just throttled Chrome)
- [ ] JS bundle < 100KB gzipped for critical path
- [ ] Images in WebP/AVIF with responsive srcset
- [ ] Fonts: < 2 font files, `font-display: optional`
- [ ] Touch handlers are `{ passive: true }`
- [ ] No layout thrashing in scroll handlers
- [ ] Virtualize lists > 50 items
- [ ] Use `content-visibility: auto` for long pages
- [ ] Service worker for repeat visits
- [ ] Minimize layers (GPU memory limited on mobile)

---

## 9. Real-World Engineering Mindset

### Landing Pages

**Problem:** Must render meaningful content ASAP. Every ms of delay = bounce.

| Strategy | Best For | Trade-off |
|----------|----------|-----------|
| SSG + CDN | Static content | Can't personalize |
| Edge SSR | Personalized landing | More complex infra |
| Critical CSS inline | Fast first paint | Larger HTML, harder to maintain |
| Preload hero image | Fast LCP | One extra resource hint to manage |

**Senior choice:** SSG with edge middleware for personalization. Inline critical CSS. Preload LCP image with `fetchpriority="high"`. Ship < 50KB JS total.

### Dashboard Apps

**Problem:** Large component trees, frequent updates, heavy data.

| Strategy | Approach |
|----------|----------|
| **Rendering** | CSR is fine (authenticated, no SEO needed) |
| **Bundle** | Route-based code splitting, lazy load panels |
| **Lists** | Virtualize tables/lists with >50 rows |
| **Updates** | Use `useDeferredValue` / `startTransition` for filters |
| **Workers** | Offload data processing to web worker |
| **Animations** | Compositor-only transitions for panels |

### E-commerce Product Pages

**Problem:** LCP is hero image. Revenue depends on speed. SEO matters.

**Senior architecture:**
1. Server Components for product data (zero client JS)
2. Streaming SSR for dynamic content (reviews, recommendations)
3. `<Image priority fetchPriority="high">` for hero
4. Preconnect to image CDN
5. Skeleton UI for below-fold (no CLS)
6. Client islands only for Add to Cart, size selector

### Heavy Animations

**Problem:** 60fps while animating complex UI.

**Rules:**
1. Only animate `transform` and `opacity` (compositor thread)
2. Promote animated elements to own layer (`will-change: transform`)
3. Avoid animating `width/height/top/left` (triggers layout)
4. Use CSS animations over JS when possible (declarative, optimizable)
5. For complex sequences: Web Animations API or GSAP (batches DOM)
6. Monitor frame drops in Performance tab
7. Test on throttled CPU (4x slowdown)

**Mobile constraint:** Each layer = GPU texture = memory. On a phone with 3GB RAM shared between system and browser, 50+ layers can cause crashes.

### Infinite Scrolling

**Problem:** DOM grows unbounded → layout becomes expensive → scroll janks.

**Solution architecture:**
```
Viewport (visible)
├── Render only visible items (virtualization)
├── Buffer zone above/below (prevent flicker)
├── Recycle DOM nodes (not create new ones)
├── IntersectionObserver for trigger (no scroll listener)
└── Placeholder height for scroll position
```

Use `@tanstack/react-virtual` or `react-window`. Keep DOM node count < 500.

---

## 10. Brainstorm / Open Questions

### Rendering Pipeline (12)
1. Why does CSS block rendering but not HTML parsing?
2. What happens if CSSOM isn't ready when DOM finishes parsing?
3. How does the browser decide which elements get their own compositing layer?
4. What's the rendering cost difference between `visibility: hidden` and `display: none`?
5. When does `content-visibility: auto` skip rendering work vs just paint?
6. How does the render tree differ from the DOM tree?
7. What triggers a full layout vs partial layout?
8. Why can't the browser just skip layout for unchanged elements?
9. What's the difference between paint invalidation and layout invalidation?
10. How does the browser prioritize which layers to rasterize first?
11. What happens to rendering when main thread is blocked by JS for 500ms?
12. How does `contain: strict` actually limit rendering scope?

### Browser Behavior (12)
13. Why did browsers implement a preload scanner?
14. How does speculative parsing differ between Chrome, Safari, and Firefox?
15. What's the actual cost of `document.write()` in modern browsers?
16. How does the browser decide request priority for subresources?
17. Why does Safari handle back/forward cache differently than Chrome?
18. How does the browser's task scheduler prioritize rendering vs input?
19. What happens when you have 100 `<link rel="preload">` tags?
20. How does HTTP/3 change how browsers handle resource loading?
21. Why do browsers limit concurrent connections per origin in HTTP/1.1?
22. How does the browser decide when to show a loading indicator?
23. What triggers a browser repaint without relayout?
24. How do passive event listeners affect compositor performance?

### Networking (12)
25. When is TTFB more important than total download time?
26. How does streaming HTML change the browser's parsing behavior?
27. What's the performance cost of too many preconnect hints?
28. When does server push (HTTP/2) hurt more than help?
29. How does DNS prefetch priority compare to preconnect?
30. What's the cost of a redirect chain on mobile?
31. How does CDN cache partitioning affect CRP?
32. When should you inline resources vs use cache?
33. How does 103 Early Hints change CRP optimization?
34. What's the bandwidth cost of over-preloading?
35. How does network priority work across multiple iframes?
36. When does a Service Worker hurt first-load performance?

### Hydration (12)
37. Why does React hydration walk the entire DOM tree?
38. How does selective hydration in React 18 actually work?
39. What causes hydration mismatch and what's the rendering cost?
40. When is progressive hydration better than islands?
41. How does Astro's `client:visible` actually implement deferred hydration?
42. What's the CPU cost of hydration on a budget Android phone?
43. Can you hydrate only event handlers without full reconciliation?
44. How does React Server Components eliminate hydration cost?
45. What's the memory overhead of keeping both server HTML and virtual DOM?
46. When does hydration ordering matter for user experience?
47. How does streaming SSR interact with hydration timing?
48. What if the user interacts before hydration completes?

### GPU/Compositing (12)
49. When does layer promotion increase memory pressure beyond benefit?
50. How does `will-change` actually work at the GPU level?
51. What's the memory cost per compositing layer on mobile?
52. How does the GPU handle transparent overlapping layers?
53. What happens when GPU memory is exhausted?
54. How does `transform: translateZ(0)` differ from `will-change: transform`?
55. When do CSS animations run on compositor vs main thread?
56. What forces a CSS animation to fall back to main thread?
57. How does the browser decide tile sizes for rasterization?
58. What's the rendering cost of `backdrop-filter: blur()`?
59. How does `isolation: isolate` affect compositing?
60. When does GPU rasterization outperform CPU rasterization?

### React Architecture (12)
61. Why do React re-renders cascade down the tree?
62. When does `React.memo` hurt performance instead of helping?
63. How does Suspense boundaries affect streaming SSR chunks?
64. What's the rendering cost of context changes vs prop drilling?
65. How does React's batching prevent layout thrashing?
66. When should you split a Client Component into Server + Client?
67. How does `useTransition` actually defer rendering work?
68. What's the compositing impact of React-driven animations?
69. How does React's synthetic event system affect INP?
70. What's the paint cost of conditional rendering vs CSS display toggle?
71. How does React's reconciler interact with requestIdleCallback?
72. When does component code splitting help vs hurt hydration?

### Mobile Performance (12)
73. Why does the same page perform differently on iOS vs Android?
74. How does thermal throttling affect rendering over time?
75. What's the impact of 120Hz displays on frame budgets?
76. How does mobile Safari's "click delay" affect INP?
77. What's the network variability on 4G that lab testing misses?
78. How does low memory affect compositing on Android?
79. When should you serve different JS bundles for mobile vs desktop?
80. How does the virtual keyboard appearance affect layout?
81. What's the GPU difference between a flagship and budget phone?
82. How does iOS WKWebView handle rendering differently than Safari?
83. Why are touch handlers more costly than mouse handlers?
84. How does viewport meta tag affect initial rendering?

### CI/CD Performance (12)
85. How do you prevent performance regression in a monorepo?
86. What's a meaningful performance budget for a React SPA?
87. When does Lighthouse CI give misleading results?
88. How do you track performance across feature branches?
89. What's the right p75 threshold for RUM alerting?
90. How do you isolate third-party script impact in CI?
91. When should performance gates block deployment?
92. How do you test rendering performance in CI (no GPU)?
93. What's the cost of running WebPageTest in CI for every PR?
94. How do you measure the performance impact of a design system change?
95. When does bundle size not correlate with runtime performance?
96. How do you handle performance in preview deployments?

### Product Trade-offs (11)
97. When should you prioritize fast first load vs fast interactions?
98. How do you justify performance work to product managers?
99. When does A/B testing infrastructure hurt performance?
100. Should above-fold priority always override below-fold?
101. How do you balance developer experience with performance?
102. When is progressive enhancement impractical?
103. How do you handle performance on feature-flag-heavy apps?
104. When should you serve a lighter experience to slow connections?
105. How do you measure the revenue impact of performance improvements?
106. When is "good enough" performance acceptable?
107. How do you handle third-party marketing scripts that tank performance?

---

## 11. Practice Questions

### Beginner (30)

**Q1.** What does the browser need before it can render the first pixel?
- **Type:** Short answer
- **Answer:** A complete DOM tree AND complete CSSOM tree to construct the render tree.
- **Why:** The render tree combines DOM structure with computed styles — without either, the browser can't determine what to show or how to show it.

**Q2.** True or False: Images block the Critical Rendering Path.
- **Type:** True/False
- **Answer:** False
- **Why:** Images are not render-blocking. The browser renders the page without waiting for images to download. However, images without dimensions cause layout shifts when they load.

**Q3.** What's the difference between `<script defer>` and `<script async>`?
- **Type:** Short answer
- **Answer:** `defer` downloads in parallel and executes after DOM parsing (in order). `async` downloads in parallel and executes immediately when ready (no order guarantee).
- **Why:** `defer` preserves execution order and waits for parser. `async` fires as soon as downloaded, which can interrupt parsing.

**Q4.** Why does a `<link rel="stylesheet">` in the `<head>` delay first paint?
- **Type:** Explanation
- **Answer:** CSS is render-blocking. The browser must build the complete CSSOM before constructing the render tree. Until the stylesheet is downloaded and parsed, no rendering occurs.
- **Why:** Without complete styles, rendering would produce FOUC (Flash of Unstyled Content).

**Q5.** Which loads faster — an image with `loading="lazy"` or `loading="eager"`?
- **Type:** Single choice
- **Answer:** `eager` loads immediately (faster for above-fold). `lazy` defers until near viewport (saves bandwidth for below-fold).
- **Why other is wrong:** `lazy` is NOT faster for above-fold content — it actually delays the image by waiting for IntersectionObserver to trigger.

**Q6.** What is FOUC?
- **Type:** Short answer
- **Answer:** Flash of Unstyled Content — when HTML renders before CSS is loaded/applied, showing raw unstyled content briefly.
- **Why:** This is why CSS is render-blocking: browsers intentionally wait for CSS to avoid FOUC.

**Q7.** What does `font-display: swap` do?
- **Type:** Short answer
- **Answer:** Shows text immediately using a fallback font, then swaps to the custom font when it loads.
- **Why:** Eliminates invisible text (FOIT) but can cause a layout shift (CLS) when fonts swap.

**Q8.** What is the DOM tree?
- **Type:** Short answer
- **Answer:** A tree data structure representing the hierarchical structure of HTML elements, built by the HTML parser from the document's bytes.

**Q9.** True or False: CSS is parser-blocking.
- **Type:** True/False
- **Answer:** False
- **Why:** CSS is render-blocking (prevents rendering) but NOT parser-blocking (HTML parsing continues while CSS loads). However, CSS blocks execution of subsequent inline scripts.

**Q10.** What happens when you put a `<script>` tag in the middle of `<body>` without defer/async?
- **Type:** Explanation
- **Answer:** HTML parsing pauses, the script is downloaded (if external) and executed, then parsing resumes. Content below the script is invisible until the script completes.

**Q11.** What is the CSSOM?
- **Type:** Short answer
- **Answer:** CSS Object Model — a tree structure representing all CSS rules with computed specificity and cascade, analogous to DOM but for styles.

**Q12.** Why should images have `width` and `height` attributes?
- **Type:** Explanation
- **Answer:** They let the browser calculate the aspect ratio before the image loads, reserving the correct space and preventing layout shifts (CLS).

**Q13.** What is render-blocking?
- **Type:** Short answer
- **Answer:** A resource that prevents the browser from rendering any content until it's fully loaded and processed. Default CSS and synchronous JS are render-blocking.

**Q14.** True or False: `<script type="module">` is deferred by default.
- **Type:** True/False
- **Answer:** True
- **Why:** ES modules have `defer` behavior built-in — they don't block HTML parsing and execute after DOM is ready.

**Q15.** What does the preload scanner do?
- **Type:** Short answer
- **Answer:** A secondary parser that scans ahead in HTML while the main parser is blocked (by JS), discovering and initiating fetches for resources early.

**Q16.** Which image format should you prefer for photos on the web?
- **Type:** Single choice — (a) PNG (b) WebP (c) AVIF (d) GIF
- **Answer:** (c) AVIF — best compression for photos. Fallback: WebP. PNG for transparency, GIF never for photos.
- **Why:** AVIF achieves 50% smaller files than JPEG with better quality.

**Q17.** What's the purpose of `<link rel="preconnect">`?
- **Type:** Short answer
- **Answer:** Establishes early connection (DNS + TCP + TLS) to a third-party origin, saving 100-300ms when the resource is eventually requested.

**Q18.** True or False: The browser can render a page with only the DOM tree (no CSSOM).
- **Type:** True/False
- **Answer:** False
- **Why:** The render tree requires both DOM and CSSOM. Without CSSOM, the browser doesn't know which elements are visible or how they're styled.

**Q19.** What does `decoding="async"` do on an `<img>` tag?
- **Type:** Short answer
- **Answer:** Hints to the browser that image decoding can happen off the main thread, avoiding blocking rendering for other content.

**Q20.** What's the difference between DOMContentLoaded and load events?
- **Type:** Short answer
- **Answer:** `DOMContentLoaded` fires when HTML is fully parsed (DOM ready). `load` fires when ALL resources (images, stylesheets, iframes) finish loading.

**Q21.** Why is a white screen shown before content appears?
- **Type:** Explanation
- **Answer:** The browser hasn't completed the CRP — either waiting for render-blocking CSS, executing blocking JS, or still building the render tree.

**Q22.** What does `fetchpriority="high"` do?
- **Type:** Short answer
- **Answer:** Tells the browser to prioritize this resource's network fetch above others of the same type. Critical for LCP images.

**Q23.** True or False: Inline styles are render-blocking.
- **Type:** True/False
- **Answer:** False (technically) — inline `<style>` blocks are parsed synchronously with HTML but don't require a network fetch, so they don't add blocking latency.

**Q24.** What happens if CSS fails to load?
- **Type:** Explanation
- **Answer:** After a timeout, the browser renders without that CSS. Content appears unstyled (FOUC). Some browsers may show content sooner than others.

**Q25.** What is a long task?
- **Type:** Short answer
- **Answer:** Any task on the main thread that takes longer than 50ms, blocking rendering and input handling during its execution.

**Q26.** What property triggers layout when read?
- **Type:** Multiple choice — (a) `innerHTML` (b) `offsetHeight` (c) `className` (d) `textContent`
- **Answer:** (b) `offsetHeight` — reading geometric properties forces synchronous layout if DOM is dirty.

**Q27.** What is the purpose of `<link rel="dns-prefetch">`?
- **Type:** Short answer
- **Answer:** Resolves DNS for a third-party domain early, saving ~20-100ms on first request to that origin.

**Q28.** True or False: `display: none` elements are included in the render tree.
- **Type:** True/False
- **Answer:** False
- **Why:** Elements with `display: none` are in the DOM but excluded from the render tree — they don't go through layout or paint.

**Q29.** Why shouldn't you lazy-load the hero image?
- **Type:** Explanation
- **Answer:** The hero image is typically the LCP element. `loading="lazy"` delays its fetch until it's near the viewport, but for above-fold content it's already visible, causing unnecessary delay.

**Q30.** What is the render tree?
- **Type:** Short answer
- **Answer:** A tree combining DOM nodes with their computed styles, excluding invisible nodes (`display: none`, `<head>`, `<script>`). Used as input for layout.

---

### Junior (30)

**Q31.** Your page has good TTFB but poor FCP. What should you investigate?
- **Type:** Scenario
- **Answer:** Render-blocking resources (large CSS files, synchronous JS in head), large JS bundles blocking rendering, missing preload for critical resources.
- **Why:** Good TTFB means server is fast. The bottleneck is between receiving bytes and first render — that's CRP blocking.

**Q32.** What's the difference between `preload` and `prefetch`?
- **Type:** Short answer
- **Answer:** `preload` = high-priority fetch for current page. `prefetch` = low-priority fetch for likely next navigation.

**Q33.** A page has CLS of 0.35. Which of these is most likely the cause?
- (a) Slow server response
- (b) Images without dimensions
- (c) Large JS bundle
- (d) Unoptimized fonts
- **Type:** Single choice
- **Answer:** (b) Images without dimensions — they cause layout shifts when loaded. (d) is also possible via font swap.
- **Why:** CLS measures layout instability, not speed. Images without reserved space are the #1 cause.

**Q34.** How does code splitting improve CRP?
- **Type:** Explanation
- **Answer:** Reduces the initial JS bundle to only what's needed for the current route. Less JS = faster parse/execute = faster interactivity. The CRP completes with less work.

**Q35.** What is the "hydration gap" in SSR?
- **Type:** Short answer
- **Answer:** The time between when server-rendered HTML appears (looks interactive) and when JS hydration completes (actually interactive). Users can see but not interact.

**Q36.** Your Lighthouse score shows "Eliminate render-blocking resources." What are likely culprits?
- **Type:** Scenario
- **Answer:** CSS `<link>` in head without media query, synchronous `<script>` without defer/async, non-critical CSS loaded in head.

**Q37.** When should you use `<link rel="preload" as="image">`?
- **Type:** Short answer
- **Answer:** For the LCP image that the browser can't discover early (e.g., CSS background-image, dynamically rendered `<img>`). NOT for all images.

**Q38.** What causes a network waterfall and how do you fix it?
- **Type:** Explanation
- **Answer:** Serial dependency chains (A loads B loads C). Fix: flatten dependencies, preload critical resources, use HTTP/2 multiplexing, parallel fetch.

**Q39.** True or False: `loading="lazy"` works on all browsers for iframes.
- **Type:** True/False
- **Answer:** True (in modern browsers) — `loading="lazy"` is supported for both `<img>` and `<iframe>` in all modern browsers.

**Q40.** What is critical CSS and when should you use it?
- **Type:** Explanation
- **Answer:** The minimum CSS needed to render above-fold content, inlined in `<style>` to eliminate the render-blocking stylesheet fetch. Use for landing pages, marketing sites where FCP matters critically.

**Q41.** A React app has good TTFB (SSR) but poor LCP. What's happening?
- **Type:** Scenario
- **Answer:** LCP image isn't preloaded, image is rendered client-side after hydration, or large CSS file blocks rendering of the HTML content.

**Q42.** What does `<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>` do?
- **Type:** Short answer
- **Answer:** Establishes DNS + TCP + TLS connection to fonts.gstatic.com early, so when Google Fonts CSS requests the actual font file, the connection is already ready.

**Q43.** How does `font-display: optional` differ from `swap`?
- **Type:** Comparison
- **Answer:** `optional`: uses fallback if font hasn't loaded within ~100ms, never swaps later (no CLS, but might not show custom font). `swap`: shows fallback then swaps when ready (FOUT, possible CLS).

**Q44.** What's the performance impact of CSS `@import`?
- **Type:** Short answer
- **Answer:** Creates a waterfall: browser must download and parse the first CSS file before discovering the `@import`, then fetch the second file serially. Use `<link>` tags instead for parallel downloads.

**Q45.** How does the Coverage tab in DevTools help with CRP?
- **Type:** Explanation
- **Answer:** Shows what percentage of CSS/JS is actually used on the current page. Unused code is downloaded, parsed, and (for CSS) potentially blocking rendering unnecessarily.

**Q46.** A site loads 2MB of JavaScript. What's the mobile rendering impact?
- **Type:** Scenario
- **Answer:** On mid-range mobile (150ms/MB parse time), that's ~300ms just to parse + ~200ms to compile + execution time. Main thread is blocked, delaying interactivity by potentially 1-3 seconds.

**Q47.** When should you use `srcset` vs `<picture>`?
- **Type:** Comparison
- **Answer:** `srcset` + `sizes`: same image, different resolutions (browser picks best). `<picture>`: different images for different conditions (art direction, format negotiation).

**Q48.** What is the Speculation Rules API?
- **Type:** Short answer
- **Answer:** Allows declaring which URLs the browser should prefetch or prerender for instant future navigation. Replaces `<link rel="prefetch">` with more control.

**Q49.** True or False: HTTP/2 eliminates the need for bundling JavaScript.
- **Type:** True/False
- **Answer:** False
- **Why:** While HTTP/2 multiplexing removes the connection limit, compression efficiency, caching granularity, and parse overhead still make bundling beneficial (just less aggressive).

**Q50.** How do you measure layout shifts in DevTools?
- **Type:** Short answer
- **Answer:** Performance tab → enable "Layout Shift" in settings. Rendering tab → check "Layout Shift Regions" for visual highlighting. Console: `PerformanceObserver` with `type: 'layout-shift'`.

**Q51.** What is "Total Blocking Time" and how does it relate to CRP?
- **Type:** Explanation
- **Answer:** TBT measures total time that tasks exceed 50ms between FCP and TTI. High TBT means the main thread is busy with JS after first render, delaying interactivity. Correlates with INP.

**Q52.** How does Next.js `<Image>` component optimize CRP?
- **Type:** Explanation
- **Answer:** Auto-generates responsive srcset, lazy loads by default, reserves space with width/height (prevents CLS), supports priority prop for LCP images, optimizes format (WebP/AVIF).

**Q53.** What's a performance budget and how should you set one?
- **Type:** Short answer
- **Answer:** A limit on metrics (bundle size < 170KB JS, LCP < 2.5s, CLS < 0.1). Set based on competitor analysis, target devices, and business goals. Enforce in CI.

**Q54.** How does `<link rel="modulepreload">` differ from `<link rel="preload" as="script">`?
- **Type:** Comparison
- **Answer:** `modulepreload` not only fetches but also parses and compiles the module (and its static imports), making execution instant. Regular preload only fetches.

**Q55.** A user reports "the page loads but nothing happens when I click buttons." What's the diagnosis?
- **Type:** Scenario
- **Answer:** Classic hydration gap. SSR HTML is visible but JS hasn't finished downloading/parsing/hydrating. The page looks interactive but event handlers aren't attached yet.

**Q56.** How does `<script>` placement affect perceived performance?
- **Type:** Explanation
- **Answer:** `<script>` in `<head>` without defer blocks rendering of entire `<body>`. At end of `<body>` lets HTML render first. With `defer` in `<head>` is optimal: early fetch + late execution.

**Q57.** What causes "layout shift from web fonts"?
- **Type:** Explanation
- **Answer:** When fallback font metrics differ from custom font, text reflows on swap (line heights, widths change). Fix: use size-adjusted fallback or `font-display: optional`.

**Q58.** How do you preload a font correctly?
- **Type:** Code
- **Answer:** `<link rel="preload" href="/font.woff2" as="font" type="font/woff2" crossorigin>` — `crossorigin` is required even for same-origin fonts (font spec requirement).

**Q59.** What's the difference between First Paint and First Contentful Paint?
- **Type:** Short answer
- **Answer:** First Paint: any pixel change (could be background color). FCP: meaningful content rendered (text, image, SVG, canvas). FCP is always ≥ First Paint.

**Q60.** How does `<link rel="preload">` differ from putting the resource in HTML?
- **Type:** Explanation
- **Answer:** Preload elevates fetch priority and starts download earlier (before parser reaches it). Useful for resources discovered late (CSS background-images, JS-loaded images, fonts).

---

### Senior (30)

**Q61.** Your React app has INP of 350ms on interaction. The Performance trace shows a 200ms "Recalculate Style" event. What's causing this?
- **Type:** Debugging
- **Answer:** Large DOM tree (>1500 nodes) combined with a broad style change. When React re-renders and changes classes/styles, the browser must recalculate styles for all affected nodes. Fix: reduce DOM size, use CSS containment, virtualize.

**Q62.** Explain how streaming SSR interacts with the browser's incremental rendering.
- **Type:** Explanation
- **Answer:** Streaming sends HTML chunks progressively. The browser's HTML parser is incremental — it processes each chunk as it arrives, building DOM and triggering renders. With Suspense boundaries, React sends shells first (fast FCP) then fills in chunks (progressive LCP). Browser can paint after each chunk.

**Q63.** When does `will-change` hurt performance?
- **Type:** Explanation
- **Answer:** `will-change` promotes elements to their own compositing layer. Each layer consumes GPU memory (roughly width × height × 4 bytes). On mobile with limited GPU memory, excessive layers cause: more memory pressure, longer composite time, potential fallback to software rendering, or OOM crashes. Apply only to elements that will actually animate, remove after animation ends.

**Q64.** A Next.js page has LCP of 4.2s despite fast TTFB (200ms). The LCP element is a hero image. What's your debugging approach?
- **Type:** Scenario
- **Answer:**
  1. Check if image has `priority` / `fetchpriority="high"` — if not, browser deprioritizes it
  2. Check if image is rendered client-side (after hydration) — won't be in initial HTML
  3. Check render-blocking CSS — image can't paint until CSS loads
  4. Check image format/size — large unoptimized image
  5. Check if image is behind responsive/conditional render
  6. Check network waterfall — is image request chained behind other resources?
  7. Fix: Add `priority`, preload, use proper format, ensure it's in SSR HTML

**Q65.** How does `content-visibility: auto` actually reduce rendering work?
- **Type:** Deep explanation
- **Answer:** Elements with `content-visibility: auto` that are off-screen skip:
  - Style calculation for children
  - Layout for children
  - Paint for children
  Only the element itself is laid out (using `contain-intrinsic-size` as placeholder). When scrolled into view, the browser renders the subtree. This can save hundreds of ms on long pages with many complex sections.

**Q66.** True or False: React's `useMemo` reduces rendering pipeline cost.
- **Type:** True/False
- **Answer:** Partially true — `useMemo` reduces React reconciliation work (fewer virtual DOM diffs), which reduces DOM mutations, which reduces style/layout/paint work. But `useMemo` itself has overhead (comparison cost + memory). Net benefit depends on component complexity.

**Q67.** How would you architect a performance monitoring system for a 50-person frontend team?
- **Type:** Architecture
- **Answer:**
  1. **RUM collection**: web-vitals library → beacon to analytics endpoint
  2. **Dashboards**: Per-route CWV scores, p75 trends, regression detection
  3. **CI gates**: Lighthouse CI with budgets per route, bundle size checks
  4. **Alerting**: p75 CWV regression > 10% triggers Slack alert
  5. **Attribution**: Link performance to PRs via deploy markers
  6. **Education**: Performance review in code review checklist
  7. **Ownership**: Each team owns their routes' performance budgets

**Q68.** What's the difference between layout containment and size containment?
- **Type:** Comparison
- **Answer:** `contain: layout` — element's internal layout doesn't affect outside (and vice versa), but element's size still depends on content. `contain: size` — element's size is independent of content (must set explicit dimensions). Combined with `contain: strict` (= size + layout + paint + style) for maximum isolation.

**Q69.** A virtualized list janks when scrolling fast. What's happening?
- **Type:** Debugging
- **Answer:** Likely causes:
  1. Items are complex (expensive to render on mount/unmount during scroll)
  2. Style recalculation cascade when new items mount
  3. Layout thrashing in scroll handler
  4. Overscan buffer too small (blank flashes trigger urgent rendering)
  5. GC pauses from rapid allocation/deallocation
  Fix: increase overscan, simplify item rendering, recycle DOM nodes, use `contain: strict` on items.

**Q70.** How does React Server Components eliminate CRP cost compared to regular SSR?
- **Type:** Explanation
- **Answer:** Regular SSR: Server renders HTML → client downloads full component JS → hydration walks entire tree. RSC: Server components never ship to client — zero JS for those components. Only Client Components ship JS and hydrate. The CRP cost (JS download, parse, execute, hydrate) is only paid for interactive components.

**Q71.** Explain the performance trade-offs of CSS-in-JS at scale.
- **Type:** Analysis
- **Answer:**
  - **Runtime (styled-components):** Generates CSS during render → blocks paint. Extra JS bundle size. Style injection causes style recalculation.
  - **Build-time (vanilla-extract, Linaria):** Zero runtime cost. CSS extracted at build. Behaves like regular CSS.
  - **Atomic (Tailwind):** Tiny CSS file (reused classes), zero runtime, but HTML is larger.
  - At scale (1000+ components): Runtime CSS-in-JS adds 20-50KB JS + per-render overhead. Build-time extraction is the performance-optimal choice.

**Q72.** When should you use web workers for rendering performance?
- **Type:** Explanation
- **Answer:** Move computation OFF main thread when:
  - Data processing > 16ms (blocks rendering frame)
  - Search/filter over large datasets
  - JSON parsing of large payloads
  - Image processing / canvas manipulation
  - Complex calculations (sorting, graph algorithms)
  Don't use for: DOM manipulation (workers can't access DOM), small computations (postMessage overhead > computation).

**Q73.** How does the Scheduler API (`scheduler.postTask`) improve rendering?
- **Type:** Explanation
- **Answer:** Allows prioritizing tasks: `user-blocking` > `user-visible` > `background`. Browser can interleave rendering between tasks. Unlike `setTimeout(0)` which has minimum 4ms delay and no priority, `scheduler.postTask` gives fine-grained control over yielding to rendering.

**Q74.** A page has 200 compositing layers shown in DevTools Layers panel. Is this a problem?
- **Type:** Scenario
- **Answer:** Yes, likely. Each layer needs GPU memory (bitmap = width × height × 4 bytes). 200 layers on mobile could consume 50-100MB+ GPU memory. Composite time increases. Fix: audit why layers are created (unnecessary `will-change`, `z-index` stacking, `position: fixed`, overlapping with animated elements). Reduce to <30 layers.

**Q75.** How do you implement zero-CLS font loading?
- **Type:** Implementation
- **Answer:**
  1. Use `font-display: optional` (renders fallback, never swaps = no shift)
  2. OR use `@font-face` `size-adjust`, `ascent-override`, `descent-override` to match fallback metrics to custom font exactly
  3. Preload the font file
  4. Subset the font (only needed characters)
  5. Use `woff2` format exclusively
  Result: Text renders immediately with fallback that matches custom font metrics → no visible shift.

**Q76.** Explain the rendering cost of a large DOM tree (5000+ nodes).
- **Type:** Explanation
- **Answer:** Cost scales with DOM size:
  - Style recalculation: O(n) elements × applicable rules
  - Layout: Complex tree means more boxes to calculate
  - Paint: More elements = more draw commands
  - Memory: Each node = ~0.5-1KB in memory
  - Selector matching: More nodes to match against
  - `querySelectorAll`: Linear scan
  A 5000-node DOM can make single style recalc take 50-100ms. Fix: virtualize, lazy render, simplify tree.

**Q77.** How does HTTP/3 (QUIC) change CRP optimization strategy?
- **Type:** Analysis
- **Answer:**
  - **0-RTT connection:** Eliminates TLS handshake on repeat visits (faster TTFB)
  - **No head-of-line blocking:** One lost packet doesn't block other streams
  - **Better multiplexing:** Less need for domain sharding or bundling
  - Strategy shifts: Slightly less aggressive bundling is OK, preconnect less critical for known origins, but image optimization and render-blocking resources still matter equally.

**Q78.** What forces a CSS animation to fall back from compositor to main thread?
- **Type:** List
- **Answer:** Animation falls back to main thread if it animates:
  - Any property other than `transform`, `opacity`, `filter`
  - A property that affects layout (`width`, `height`, `margin`, `padding`, `top`, `left`)
  - Element isn't in its own layer
  - Animation uses `calc()` with layout-dependent values
  - Element has complex clip-path or mask

**Q79.** How would you diagnose why React hydration takes 800ms on a product page?
- **Type:** Debugging
- **Answer:**
  1. React Profiler: Find which components are expensive to hydrate
  2. Performance trace: Look for long "Evaluate Script" + "Function Call" blocks
  3. Check component count in hydrated tree
  4. Check if data fetching happens during hydration
  5. Check for hydration mismatches (expensive recovery path)
  6. Fix: Move components to Server Components, add Suspense boundaries, lazy load below-fold, reduce component tree depth.

**Q80.** True or False: `requestAnimationFrame` guarantees your callback runs before the next paint.
- **Type:** True/False
- **Answer:** True (per spec) — rAF callbacks run as the last step before style/layout/paint in the rendering pipeline. However, if the callback takes too long, it will delay that frame's paint (causing jank).

**Q81.** What's the difference between `paint` and `composite` in terms of cost?
- **Type:** Comparison
- **Answer:** **Paint**: Generates draw commands for a layer (fills, strokes, text, images) — runs on main thread, can be expensive for complex visuals. **Composite**: Combines pre-painted layers into final image — runs on compositor/GPU thread, very fast (just matrix transforms and alpha blending). This is WHY compositor-only animations are smooth.

**Q82.** How does `<link rel="preload" as="fetch">` differ from `<link rel="preload" as="script">`?
- **Type:** Comparison
- **Answer:** Different `as` values set different request priorities and CORS modes. `as="script"` gets high priority, `as="fetch"` gets high priority but expects CORS response. Wrong `as` value = wrong priority or double-fetch (browser won't match the preloaded resource to the actual request).

**Q83.** How does the View Transitions API improve perceived performance?
- **Type:** Explanation
- **Answer:** Captures a screenshot of the old state, immediately shows the new state, then animates between them. The transition runs on compositor thread (smooth 60fps) regardless of how long the new page takes to render. Gives perception of instant navigation while actual rendering happens behind the transition.

**Q84.** What's the rendering cost of `backdrop-filter: blur(10px)` and how do you mitigate it?
- **Type:** Analysis
- **Answer:** Extremely expensive: browser must capture everything behind the element, apply Gaussian blur (O(n²) per pixel), then composite. On mobile, this can drop to <30fps. Mitigations: reduce blur radius, minimize blurred area size, use `will-change: backdrop-filter` to hint compositing, consider pre-blurred background image as alternative.

**Q85.** How do you implement performance regression detection in CI for a monorepo?
- **Type:** Architecture
- **Answer:**
  1. Run Lighthouse CI on affected routes (determine from changed files)
  2. Compare against baseline (main branch scores)
  3. Use bundlesize/size-limit for bundle checks per package
  4. Run on consistent hardware (dedicated CI runner)
  5. Statistical comparison (3+ runs, median)
  6. Alert on p75 regression > threshold
  7. Store historical data for trend analysis
  8. Fail PR if budget exceeded

**Q86.** Explain how `contain: paint` affects the rendering pipeline.
- **Type:** Explanation
- **Answer:** `contain: paint` tells the browser that this element's descendants won't paint outside its bounds. Effects: the element creates a new stacking context, clips overflow, and can be used as a containing block for fixed/absolute positioning. Rendering benefit: browser can skip painting this subtree if it's entirely off-screen.

**Q87.** What's the performance difference between CSS Grid and Flexbox for layout computation?
- **Type:** Analysis
- **Answer:** Both are fast for typical use cases. Grid can be slightly more expensive for dynamic sizing (auto-placement algorithm), but the difference is negligible for <100 items. The real cost comes from layout invalidation frequency, not algorithm choice. A flexbox container that re-layouts 60 times per second is worse than a complex grid that layouts once.

**Q88.** A user on a budget Android phone reports 3-second INP. Your analytics show p75 INP is 180ms. How do you investigate?
- **Type:** Scenario
- **Answer:**
  1. Segment RUM data by device class → confirm budget devices are disproportionately affected
  2. Use DevTools with 6x CPU throttle to simulate
  3. Profile interactions → find long tasks
  4. Common culprits: heavy React re-renders, large DOM trees, unoptimized event handlers, no `startTransition`
  5. Consider serving lighter experience to low-end devices (via `navigator.deviceMemory` or `navigator.hardwareConcurrency`)

**Q89.** How does `fetchpriority` actually work at the browser scheduling level?
- **Type:** Deep explanation
- **Answer:** Browser assigns 5 internal priority levels (Highest, High, Medium, Low, Lowest). `fetchpriority` overrides the default for that resource type. For images: default is Low (during initial load), `fetchpriority="high"` bumps to High. This affects: queue ordering in the network stack, bandwidth allocation under contention, and whether the resource can delay other fetches.

**Q90.** What architectural patterns prevent performance degradation as a React app scales to 200+ routes?
- **Type:** Architecture
- **Answer:**
  1. Route-based code splitting (each route = separate chunk)
  2. Shared vendor chunk (React, common libs)
  3. Server Components for data-heavy routes
  4. Performance budgets per route in CI
  5. Lazy load modals/dialogs
  6. Design system with tree-shaking
  7. Remove unused dependencies (bundlephobia check)
  8. Monitor bundle growth per PR
  9. Consider micro-frontends for independent teams
  10. RUM monitoring per route with regression alerts

---

### Expert / Browser Engineer (30)

**Q91.** How does Blink's LayoutNG differ from the legacy layout engine in terms of rendering performance?
- **Type:** Deep explanation
- **Answer:** LayoutNG introduced immutable fragment trees — layout results are cached and reused when inputs haven't changed. Legacy layout mutated a single tree, requiring full re-layout more often. LayoutNG enables better incremental layout (only recompute changed subtrees), parallel layout for independent subtrees, and simpler invalidation logic. This means fewer forced layouts and faster style recalculation recovery.

**Q92.** Explain how Chrome's compositor thread handles scroll without involving the main thread.
- **Type:** Deep explanation
- **Answer:** The compositor has a copy of the layer tree with pre-rasterized tiles. On scroll input, the compositor simply adjusts the scroll offset and composites existing tiles at new positions — pure GPU operation (matrix transform). No style, layout, or paint needed. If new tiles are needed (scroll into unrasterized area), the compositor requests rasterization asynchronously. This is WHY scroll is usually smooth even when main thread is busy (unless scroll handlers are non-passive).

**Q93.** What causes "checkerboarding" during fast scroll and how do browsers mitigate it?
- **Type:** Explanation
- **Answer:** Checkerboarding = scrolling faster than tiles can be rasterized, showing blank (checker-patterned) areas. Mitigations: larger tile buffer (pre-rasterize tiles outside viewport), priority rasterization in scroll direction, GPU rasterization (faster than CPU), predictive rasterization based on scroll velocity. Trade-off: more tiles = more GPU memory.

**Q94.** How does React's fiber architecture interact with browser rendering frames?
- **Type:** Deep explanation
- **Answer:** Fiber makes React work interruptible. React works in units (fibers), and after each unit, it checks if the frame deadline is approaching (via `shouldYield()`). If yes, it yields to the browser to render a frame, then resumes. This prevents React from monopolizing the main thread for an entire reconciliation pass. In concurrent mode, React can pause low-priority work to handle user input, maintaining responsiveness.

**Q95.** True or False: GPU rasterization is always faster than CPU rasterization.
- **Type:** True/False
- **Answer:** False
- **Why:** GPU rasterization has overhead (texture upload, shader compilation). For simple/small layers, CPU rasterization can be faster. For complex layers with many draw operations, gradients, or large areas, GPU excels. Chrome uses heuristics to decide per-layer.

**Q96.** How does the browser's task scheduler decide between running JavaScript vs rendering?
- **Type:** Deep explanation
- **Answer:** The event loop: run one macrotask → run all microtasks → check if rendering needed (16.67ms since last frame?) → if yes: run rAF callbacks → style → layout → paint → composite. The scheduler doesn't interrupt JS mid-task. If a task takes 100ms, rendering is delayed 100ms (6 dropped frames). This is why `scheduler.yield()` and task splitting are critical.

**Q97.** Explain the performance implications of style engine's selector matching strategy.
- **Type:** Deep explanation
- **Answer:** Browsers match selectors RIGHT-TO-LEFT. `.nav > .item > a` starts by finding all `a` tags, then checking parent is `.item`, then grandparent is `.nav`. This is efficient because most elements DON'T match (early termination). Expensive selectors: universal selectors `*`, deep descendant selectors, selectors with many components. At 10,000 DOM nodes × 10,000 CSS rules, selector matching cost becomes measurable.

**Q98.** How does WebRender (Firefox/Gecko) differ architecturally from Chrome's compositor?
- **Type:** Comparison
- **Answer:** WebRender uses a GPU-first approach: the entire page is treated as a GPU scene graph, rasterized directly on GPU (like a game engine). Chrome's approach: CPU paints to bitmaps, uploads textures to GPU for compositing. WebRender advantage: better handling of complex effects (filters, masks, clips). Trade-off: requires modern GPU, higher GPU memory usage, shader compilation stalls.

**Q99.** What happens at the rendering level when you call `element.style.transform = ...` in a loop 1000 times synchronously?
- **Type:** Deep explanation
- **Answer:** Style is marked dirty but NOT recalculated until needed (lazy evaluation). Only ONE style recalculation happens before the next frame. The 1000 assignments just overwrite the inline style property. HOWEVER, if you READ a layout property between writes, you force synchronous style recalculation on each read. Without reads: 1000 writes = 1 recalc. With interleaved reads: 1000 writes = up to 1000 recalcs.

**Q100.** How does the browser's pre-paint phase work in the modern rendering pipeline?
- **Type:** Deep explanation
- **Answer:** Pre-paint (after layout, before paint): resolves paint properties that depend on layout (like `background-attachment: fixed` needing scroll position, or `clip-path` needing element bounds), builds the paint property tree (transform tree, clip tree, effect tree), and determines which layers need repainting. This phase decides WHAT to paint without actually doing the painting work.

**Q101.** Explain how IntersectionObserver is more efficient than scroll event + getBoundingClientRect.
- **Type:** Comparison
- **Answer:** Scroll events fire on main thread at high frequency, and `getBoundingClientRect()` forces synchronous layout. IntersectionObserver is implemented in the browser's compositor/off-main-thread and batches callbacks asynchronously. It uses cached geometry, doesn't force layout, and only fires when threshold crossings occur. At scale (100 observed elements), the performance difference is dramatic.

**Q102.** What's the memory architecture of compositing layers and how does it affect mobile?
- **Type:** Deep explanation
- **Answer:** Each layer = bitmap in GPU memory: width × height × 4 bytes (RGBA). A full-screen layer on a 1080p phone = 1920×1080×4 = ~8MB. With 2x DPR: ~32MB per full-screen layer. 10 full-screen layers = 320MB GPU memory on a device with maybe 1-2GB total GPU memory shared with system. This is why layer count must be minimized on mobile.

**Q103.** How does `scheduler.yield()` differ from `setTimeout(0)` for breaking up long tasks?
- **Type:** Comparison
- **Answer:** `setTimeout(0)` has minimum 4ms delay (per spec), drops to end of task queue, loses priority context. `scheduler.yield()` (Scheduler API): yields immediately, retains current priority level, continuation runs as next task at same priority. This means user-blocking work resumes before background work, preventing priority inversion.

**Q104.** Explain how the browser handles `position: fixed` elements in the compositing pipeline.
- **Type:** Deep explanation
- **Answer:** Fixed elements are promoted to their own compositing layer because they must stay in viewport during scroll without re-layout. The compositor handles their positioning (viewport-relative) while scrolling other layers. This is efficient for scroll but costs a layer. If a fixed element is large or has many descendants, the layer cost is significant.

**Q105.** What causes "jank" during CSS transitions that should be compositor-accelerated?
- **Type:** Debugging
- **Answer:** Even compositor animations can jank if:
  1. Main thread is blocked (GC pause delays compositor commit)
  2. Layer is too large to rasterize in time
  3. GPU is overwhelmed (too many layers animating)
  4. Animation triggers paint (not just transform/opacity)
  5. `will-change` was set too late (layer promotion has setup cost)
  6. Implicit layer creation from z-index stacking

**Q106.** How does Chrome's renderer process architecture (site isolation) affect CRP?
- **Type:** Deep explanation
- **Answer:** Each site gets its own renderer process (security). Cross-origin iframes run in separate processes. CRP implications: each process has its own main thread, style engine, layout engine. Cross-origin iframes don't block parent's CRP. But: more processes = more memory. `<iframe>` heavy pages consume significantly more resources than single-origin pages.

**Q107.** What is "rendering starvation" and when does it occur?
- **Type:** Explanation
- **Answer:** When the main thread is continuously busy with JavaScript tasks, preventing the browser from performing rendering updates. The event loop never reaches the "render" step because there's always another microtask or macrotask queued. Symptoms: frozen UI, scroll jank, input delay. Common cause: tight loops, unthrottled processing, recursive microtasks.

**Q108.** How do passive event listeners actually improve compositor performance?
- **Type:** Deep explanation
- **Answer:** Without `passive`, the compositor must wait for the main thread to run the touch/wheel handler to check if it calls `preventDefault()`. This adds one frame of latency to scroll. With `passive: true`, the compositor knows scrolling won't be cancelled and scrolls immediately, in parallel with main thread running the handler. This is why Chrome defaults touchstart/wheel to passive on document.

**Q109.** Explain the rendering implications of the `content-visibility: auto` with `contain-intrinsic-size`.
- **Type:** Deep explanation
- **Answer:** `content-visibility: auto` tells the browser: "skip rendering this subtree when off-screen." `contain-intrinsic-size` provides a placeholder size so the page's total height is correct for scrollbar calculations. When the element enters viewport: browser renders the subtree (may cause a frame drop for complex content). Trade-off: reduces initial render cost but may cause jank on scroll into view. Mitigation: browser pre-renders slightly ahead of viewport.

**Q110.** How does the browser decide the order of resource loading for a page with 50+ resources?
- **Type:** Deep explanation
- **Answer:** Priority assignment (Chromium):
  - HTML: Highest
  - CSS (in head): Highest (render-blocking)
  - Preloaded resources: depends on `as` type
  - Fonts: High (during blocking period)
  - Scripts (sync): High, (async): Low, (defer): Low
  - Images: Low (initially), bumped to Medium when in viewport
  - `fetchpriority` overrides defaults
  Network stack has limited concurrent requests per priority band. Higher priority resources get bandwidth first. Late-discovered resources compete with already-in-flight requests.

**Q111.** What's the cost model of forced style recalculation (invalidation) in browser engines?
- **Type:** Deep explanation
- **Answer:** Style invalidation is NOT always O(n):
  - **Descendant invalidation**: Class change on parent → recalc all descendants (O(subtree))
  - **Sibling invalidation**: `:nth-child` rules → changing one sibling recalcs all siblings
  - **Self-only**: Changing element's own style → recalc just that element (O(1))
  - Blink uses "invalidation sets" to minimize work: tracks which style changes affect which selectors
  - The most expensive case: changing a class on `<body>` with broad selectors

**Q112.** How does `isolation: isolate` create a new stacking context and what are the compositing implications?
- **Type:** Deep explanation
- **Answer:** `isolation: isolate` creates a new stacking context, which means the element and its descendants are composited as a group before being blended with the rest. This prevents `mix-blend-mode` from reaching outside the isolated element. Compositing implication: may create a new layer (or require the element to be painted as a single unit), slightly increasing composite cost but enabling optimization for its subtree.

**Q113.** Explain how Chrome's speculative loading (Speculation Rules API) affects the rendering pipeline.
- **Type:** Deep explanation
- **Answer:** Speculation Rules tell Chrome to pre-render entire pages in hidden renderer processes. When user navigates, the pre-rendered page is instantly swapped in — no CRP delay at all. Costs: extra CPU/memory for rendering pages user might not visit, network bandwidth for prefetch. The browser limits active speculations and cancels them under memory pressure. This is the most aggressive CRP optimization possible — eliminate it entirely for predicted navigations.

**Q114.** What's the rendering difference between `opacity: 0`, `visibility: hidden`, and `display: none`?
- **Type:** Comparison
- **Answer:**
  - `display: none`: Excluded from render tree. No layout, paint, or composite cost. Not accessible.
  - `visibility: hidden`: In render tree, takes layout space, painted (as invisible), composited. Accessible to screen readers.
  - `opacity: 0`: In render tree, takes layout space, painted, composited (own layer if animated). Still interactive (receives clicks). Full rendering cost minus visual output.

**Q115.** How does the browser handle rendering for a `<canvas>` element with frequent updates?
- **Type:** Deep explanation
- **Answer:** `<canvas>` with frequent updates: element gets its own compositing layer. Each frame, the canvas bitmap is updated and the texture re-uploaded to GPU. The compositor composites this layer with the rest. Hardware-accelerated canvas (WebGL/WebGPU) renders directly to a GPU texture, avoiding main thread entirely. 2D canvas: depends on whether GPU-accelerated (Chrome does for most 2D canvas). Key: canvas doesn't participate in DOM layout/style, making it ideal for high-frequency visual updates.

**Q116.** What are the performance implications of CSS `@layer` for the style engine?
- **Type:** Analysis
- **Answer:** `@layer` changes cascade ordering but doesn't fundamentally change style engine cost. The engine still matches selectors against all rules; layers only affect which rule wins. However, layers can improve developer workflows that previously used `!important` or overly-specific selectors, leading to simpler selectors overall — which improves selector matching performance indirectly.

**Q117.** How does a browser's GPU process handle texture memory limits?
- **Type:** Deep explanation
- **Answer:** GPU process manages a texture budget. When layers exceed budget: evicts least-recently-used tiles (checkerboarding on scroll), reduces tile resolution (blurry then sharp), or falls back to CPU compositing. On mobile: system can kill the GPU process under memory pressure (Android low-memory killer). Browser signals include: slow rasterization, missing tiles, resolution drops on zoom.

**Q118.** Explain the performance characteristics of `requestIdleCallback` vs `scheduler.postTask({priority: 'background'})`.
- **Type:** Comparison
- **Answer:** `requestIdleCallback`: fires during idle periods, gets a deadline object (typically 50ms max). Not guaranteed to fire (busy pages may never be idle). `scheduler.postTask({priority: 'background'})`: guaranteed to eventually run, browser schedules around higher-priority work, integrates with overall task prioritization. rIC is better for truly optional work; postTask is better for work that must complete but isn't urgent.

**Q119.** What's the rendering cost of a large `box-shadow` vs `filter: drop-shadow()`?
- **Type:** Comparison
- **Answer:** `box-shadow`: Painted as part of the element's paint phase. Cost proportional to blur radius and element size. Stays on same layer. `filter: drop-shadow()`: Creates an offscreen buffer, renders element, applies shadow to the alpha channel. Often promotes to own layer. More expensive per-element but can be composited (animated without repaint). For static shadows, `box-shadow` is cheaper.

**Q120.** How would you use Perfetto/Chrome Tracing to diagnose a 200ms input delay?
- **Type:** Debugging workflow
- **Answer:**
  1. Record trace with categories: `blink`, `cc`, `viz`, `input`, `v8`
  2. Find the input event in the `InputLatency` track
  3. Follow the flow: input received → dispatched to renderer → event handler → rAF → style → layout → paint → composite → display
  4. Identify which phase took longest
  5. Common findings: long JS handler, forced layout in handler, expensive style recalc, slow paint
  6. Look at main thread task that contains the handler — what else is in that task?
  7. Check if input was delayed by a preceding long task (queuing delay)

---

## 12. Personalized Recommendations

### For Your Stack (React + Next.js + Astro + Vite + TypeScript)

**Priority CRP concepts:**
1. **React hydration cost** — this is your #1 CRP bottleneck in Next.js apps
2. **Server Components** — eliminate client JS for data-heavy components
3. **Streaming SSR** — unblock first paint with progressive rendering
4. **Image optimization** — Next.js Image + fetchpriority for LCP
5. **Bundle architecture** — Vite's code splitting + tree shaking
6. **Island architecture** — Astro for content-heavy sites
7. **Font loading** — zero-CLS font strategy
8. **Core Web Vitals monitoring** — RUM in production

### Common Mistakes Frontend Engineers Make

1. Using CSR when SSR/SSG would be better (React SPA habit)
2. Not preloading LCP images
3. Over-hydrating (sending JS for static content)
4. Ignoring mobile performance (testing only on fast laptops)
5. Bundle size creep without monitoring
6. Layout thrashing in animation/scroll handlers
7. CSS-in-JS runtime overhead at scale
8. Not using `fetchpriority` on critical resources
9. Lazy loading above-fold content
10. Not measuring before and after optimization

### 60-Day Learning Plan

**Week 1-2: Foundations**
- Study this guide sections 1-3
- Run Lighthouse on 5 of your projects, note scores
- Learn Chrome DevTools Performance tab workflow
- Identify LCP elements on your pages

**Week 3-4: React Performance**
- Profile hydration cost of your Next.js apps
- Implement Server Components for 3 data-heavy pages
- Set up streaming SSR with Suspense boundaries
- Measure before/after with Lighthouse

**Week 5-6: Advanced Optimization**
- Implement zero-CLS font loading
- Set up image optimization pipeline (AVIF/WebP + fetchpriority)
- Add `content-visibility: auto` to long pages
- Break long tasks with `startTransition` / `scheduler.yield()`

**Week 7-8: Tooling & CI**
- Set up Lighthouse CI in your pipeline
- Add bundle size budgets (size-limit)
- Implement RUM with web-vitals library
- Create performance dashboard

**Week 9-10: Deep Rendering**
- Study compositing with Layers panel
- Profile animations (ensure compositor-only)
- Learn Perfetto basics
- Optimize one page to score 100 on mobile Lighthouse

**Week 11-12: Architecture**
- Design performance governance for your team
- Create performance review checklist
- Document optimization patterns for your codebase
- Build an Astro island architecture prototype

**Milestone targets:**
- Day 14: Can explain CRP pipeline from memory
- Day 28: All project LCP < 2.5s
- Day 42: Zero CLS on main pages
- Day 56: CI performance gates active, RUM monitoring live

---

## 13. Official Documentation & Reference Links

### Beginner

| Topic | Link |
|-------|------|
| Critical Rendering Path | https://web.dev/articles/critical-rendering-path |
| How Browsers Work | https://developer.chrome.com/blog/inside-browser-part1/ |
| Render-blocking resources | https://web.dev/articles/render-blocking-resources |
| Core Web Vitals | https://web.dev/articles/vitals |
| DOM Construction | https://web.dev/articles/critical-rendering-path/constructing-the-object-model |
| Render Tree | https://web.dev/articles/critical-rendering-path/render-tree-construction |
| MDN: Critical Rendering Path | https://developer.mozilla.org/en-US/docs/Web/Performance/Critical_rendering_path |
| Loading Performance | https://web.dev/learn/performance |

### Intermediate

| Topic | Link |
|-------|------|
| LCP | https://web.dev/articles/lcp |
| CLS | https://web.dev/articles/cls |
| INP | https://web.dev/articles/inp |
| Optimize LCP | https://web.dev/articles/optimize-lcp |
| Resource Hints | https://web.dev/articles/preload-critical-assets |
| Font Best Practices | https://web.dev/articles/font-best-practices |
| Image Optimization | https://web.dev/articles/choose-the-right-image-format |
| Lighthouse | https://developer.chrome.com/docs/lighthouse |
| Patterns.dev | https://www.patterns.dev |

### Advanced

| Topic | Link |
|-------|------|
| Rendering Performance | https://web.dev/articles/rendering-performance |
| Compositor Animations | https://web.dev/articles/animations-guide |
| Layout Thrashing | https://web.dev/articles/avoid-large-complex-layouts-and-layout-thrashing |
| content-visibility | https://web.dev/articles/content-visibility |
| Speculation Rules | https://developer.chrome.com/docs/web-platform/prerender-pages |
| View Transitions | https://developer.chrome.com/docs/web-platform/view-transitions |
| Scheduler API | https://developer.chrome.com/blog/introducing-scheduler-yield |
| fetchpriority | https://web.dev/articles/fetch-priority |
| Performance Calendar | https://calendar.perfplanet.com |
| React Server Components | https://react.dev/reference/rsc/server-components |

### Expert / Browser Internals

| Topic | Link |
|-------|------|
| Blink Rendering Architecture | https://chromium.googlesource.com/chromium/src/+/main/third_party/blink/renderer/README.md |
| How Blink Works | https://docs.google.com/document/d/1aitSOucL0VHZa9Z2vbRJSyAIsAz24kX8LFByQ5xQnUg |
| Chromium Compositor | https://chromium.googlesource.com/chromium/src/+/main/cc/README.md |
| RenderingNG Architecture | https://developer.chrome.com/articles/renderingng-architecture |
| LayoutNG | https://chromium.googlesource.com/chromium/src/+/main/third_party/blink/renderer/core/layout/ng/README.md |
| Perfetto | https://perfetto.dev |
| Chrome Tracing | https://www.chromium.org/developers/how-tos/trace-event-profiling-tool/ |
| Life of a Pixel (video) | https://www.youtube.com/watch?v=K2QHdgAKP-s |
| WebRender (Firefox) | https://hacks.mozilla.org/2017/10/the-whole-web-at-maximum-fps-how-webrender-gets-rid-of-jank/ |

### React / Next.js / Astro

| Topic | Link |
|-------|------|
| React Hydration | https://react.dev/reference/react-dom/client/hydrateRoot |
| React Suspense (Streaming) | https://react.dev/reference/react/Suspense |
| Next.js Performance | https://nextjs.org/docs/app/building-your-application/optimizing |
| Next.js Image | https://nextjs.org/docs/app/api-reference/components/image |
| Astro Islands | https://docs.astro.build/en/concepts/islands/ |
| Vercel Blog (Performance) | https://vercel.com/blog |

---

## 14. Advanced Engineering Topics

### Browser Rendering Internals — Deeper

**RenderingNG (Chrome's modern pipeline):**
```
Content (DOM + Style)
    │
    ▼
┌─────────────────┐
│  Main Thread    │
│  - Animate      │
│  - Style        │
│  - Layout       │
│  - Pre-paint    │
│  - Paint        │
│  - Commit       │
└────────┬────────┘
         │ (commit)
         ▼
┌─────────────────┐
│  Compositor     │
│  - Tiling       │
│  - Raster       │
│  - Activate     │
│  - Draw         │
│  - Submit       │
└────────┬────────┘
         │ (submit)
         ▼
┌─────────────────┐
│  Viz (Display)  │
│  - Aggregate    │
│  - Display      │
└─────────────────┘
```

### Frame Budget Engineering

For 60fps on a page with animations:
- **JS budget:** ≤ 8ms (leave room for rendering)
- **Style:** ≤ 2ms (keep selectors simple, limit DOM size)
- **Layout:** ≤ 2ms (avoid thrashing, use containment)
- **Paint:** ≤ 2ms (minimize paint area, use layers)
- **Composite:** ≤ 1ms (limit layer count)
- **Overhead:** ~2ms (GC, browser internal work)
- **Total:** ≤ 16.67ms

### Hydration Architecture Patterns

| Pattern | How | Best For |
|---------|-----|----------|
| Full hydration | React hydrates entire tree | Small apps |
| Progressive hydration | Hydrate in priority order | Medium apps with clear priority |
| Selective hydration (React 18) | Suspense boundaries hydrate independently | Large apps |
| Islands (Astro) | Only interactive components hydrate | Content-heavy sites |
| Resumability (Qwik) | Serialize execution state, resume on interaction | Maximum performance |
| Partial hydration | Only hydrate components that need interactivity | Mixed static/dynamic |

### Performance Budgets at Scale

```
Per-route budget (example):
├── HTML: < 50KB (gzipped)
├── CSS: < 30KB (critical) + lazy rest
├── JS: < 100KB (initial) + lazy chunks
├── Images: < 200KB above-fold
├── Fonts: < 50KB (2 weights max)
├── LCP: < 2.5s (p75)
├── CLS: < 0.1
├── INP: < 200ms
└── TBT: < 200ms
```

### Future Browser Rendering Directions

1. **WebGPU Compute:** Offload complex rendering/data processing to GPU compute shaders
2. **Scroll-driven Animations:** Declarative animations tied to scroll position, run on compositor
3. **View Transitions Level 2:** Cross-document transitions without SPA
4. **CSS `@scope`:** Style containment without specificity hacks
5. **Popover API:** Native popover with compositor-optimized positioning
6. **Anchor Positioning:** Layout-engine-optimized tooltip/popover positioning
7. **Navigation API:** Fine-grained control over navigation for SPA performance
8. **Shared Element Transitions:** Native element morphing between states

---

## Summary

The Critical Rendering Path is the foundation of web performance. Understanding it deeply means understanding:
- **How browsers convert bytes to pixels** (parsing → style → layout → paint → composite)
- **What blocks rendering** (CSS, synchronous JS) and how to unblock it
- **How to measure real impact** (Core Web Vitals, RUM, lab testing)
- **How to optimize for your stack** (Server Components, streaming, islands)
- **How to think like a browser** (main thread budget, compositor, GPU constraints)

## Next Steps

1. Profile your most important page with Chrome DevTools Performance tab
2. Identify your LCP element and ensure it's preloaded with high priority
3. Set up Lighthouse CI in your deployment pipeline
4. Convert one data-heavy page to Server Components
5. Implement RUM with web-vitals library

## Advanced Topics to Continue

- WebGPU and compute-based rendering
- Speculation Rules API for instant navigation
- Scroll-driven animations (CSS)
- View Transitions API (cross-document)
- Resumability (Qwik-style approach)
- Browser scheduler API evolution
- Edge computing and rendering at the edge
- Performance isolation with `<fencedframe>`
- Soft navigation performance measurement
- Long Animation Frames API
