---
title: Content Security Policy (CSP)
description: Complete CSP deep-dive guide covering browser execution internals, directives,
  nonce/hash strategies, Trusted Types, React/Next.js/Astro integration, enterprise
  rollout, reporting, and frontend AppSec governance
slug: csp
modifiedDate: '2026-05-21'
draft: false
featured: true
tags:
- security
- csp
- trusted-types
- browser-security
- frontend-security
- xss-prevention
categories:
- security
seo:
  title: Content Security Policy (CSP) — Ultimate Deep-Dive Guide
  description: Complete CSP engineering guide covering browser execution internals,
    directives, nonce/hash strategies, Trusted Types, React/Next.js/Astro patterns,
    enterprise rollout, and frontend AppSec governance
  canonical: https://feel-free.com/blogs/csp
  keywords:
  - csp
  - content security policy
  - security
  - trusted types
  - nonce
  - strict-dynamic
  - browser security
  - xss prevention
author: lazarus2019
lang: en
relatedPosts:
- cors-and-proxy
- cors-and-proxy-quizs
- csrf
- xss
---

# Content Security Policy (CSP) — Ultimate Deep-Dive Guide

A complete engineering guide from beginner concepts to browser-enforcement-engine-level mental models and enterprise-scale secure frontend architecture.

---

## Table of Contents

1. [Big Picture](#1-big-picture)
2. [Browser Security & CSP Internals](#2-browser-security--csp-internals)
3. [CSP Directives Deep Dive](#3-csp-directives-deep-dive)
4. [Nonce, Hash & Strict CSP Deep Dive](#4-nonce-hash--strict-csp-deep-dive)
5. [Trusted Types & CSP Integration](#5-trusted-types--csp-integration)
6. [React / Next.js / Astro CSP Deep Dive](#6-react--nextjs--astro-csp-deep-dive)
7. [Advanced Browser Security Concepts](#7-advanced-browser-security-concepts)
8. [Secure Architecture & Enterprise CSP Strategy](#8-secure-architecture--enterprise-csp-strategy)
9. [CSP Reporting & Observability](#9-csp-reporting--observability)
10. [Setup Guide](#10-setup-guide)
11. [Security Tooling Comparison](#11-security-tooling-comparison)
12. [Cheatsheet](#12-cheatsheet)
13. [Real-World Engineering Mindset](#13-real-world-engineering-mindset)
14. [Brainstorm / Open Questions](#14-brainstorm--open-questions)
15. [Practice Questions](#15-practice-questions)
16. [Personalized Recommendations](#16-personalized-recommendations)
17. [Official Documentation & Reference Links](#17-official-documentation--reference-links)
18. [Advanced Engineering Topics](#18-advanced-engineering-topics)

---

## 1. Big Picture

### What CSP Actually Is

Content Security Policy (CSP) is a **browser-enforced security layer** delivered via HTTP header (or `<meta>` tag) that declares which resources are allowed to load and execute on a page. It acts as a whitelist for content sources — anything not explicitly permitted is blocked by the browser.

**The core insight:** CSP doesn't prevent injection — it prevents **execution** of injected code. Even if an attacker successfully injects a `<script>` tag via XSS, CSP can prevent that script from running.

### Why CSP Exists

CSP exists because:

1. **XSS is pervasive** — Despite decades of escaping/sanitization, XSS remains in the OWASP Top 10
2. **Defense-in-depth** — Even perfect code can have bugs; CSP is a safety net
3. **The web mixes data and code** — HTML documents contain both content and executable scripts
4. **Third-party script governance** — Modern pages load dozens of external scripts
5. **Browser needs explicit permission model** — Without CSP, browsers execute anything that looks like code

```
┌──────────────────────────────────────────────────────────────┐
│                    CSP Mental Model                            │
├──────────────────────────────────────────────────────────────┤
│                                                                │
│  WITHOUT CSP:                                                 │
│    Any script in the document executes                        │
│    Any resource from any origin loads                         │
│    Injected code runs with full privileges                   │
│                                                                │
│  WITH CSP:                                                    │
│    Browser checks EVERY resource against policy              │
│    Inline scripts blocked unless explicitly allowed           │
│    Only approved origins can serve resources                  │
│    Violations reported to security team                       │
│                                                                │
│  CSP = "Here's what my page SHOULD load.                     │
│         Block everything else."                               │
│                                                                │
└──────────────────────────────────────────────────────────────┘
```

### CSP vs Related Security Mechanisms

| Mechanism | What it does | Relationship to CSP |
|-----------|-------------|-------------------|
| **CSP** | Controls what resources can load/execute | The policy itself |
| **XSS protection** | Prevents script injection | CSP mitigates XSS impact |
| **Trusted Types** | Controls DOM sink assignments | Works WITH CSP (`require-trusted-types-for`) |
| **Sandboxing** | Restricts page capabilities | CSP `sandbox` directive |
| **Same-Origin Policy** | Isolates origins from each other | CSP adds intra-origin control |
| **iframe isolation** | Restricts embedded content | CSP `frame-src` + `frame-ancestors` |

### Browser Trust & Script Execution Model

```
┌──────────────────────────────────────────────────────────────┐
│          Browser Script Execution Decision Tree               │
├──────────────────────────────────────────────────────────────┤
│                                                                │
│  Script encountered during parsing                           │
│       │                                                       │
│       ├── Is there a CSP policy?                             │
│       │     NO → Execute (legacy behavior)                   │
│       │     YES ↓                                            │
│       │                                                       │
│       ├── Is it an inline script?                            │
│       │     ├── Has valid nonce? → Execute                   │
│       │     ├── Has valid hash? → Execute                    │
│       │     ├── 'unsafe-inline' allowed? → Execute           │
│       │     └── Otherwise → BLOCK + report violation         │
│       │                                                       │
│       ├── Is it an external script?                          │
│       │     ├── Source matches script-src? → Execute         │
│       │     ├── 'strict-dynamic' + trusted parent? → Execute │
│       │     └── Otherwise → BLOCK + report violation         │
│       │                                                       │
│       └── Is it eval/Function/setTimeout(string)?            │
│             ├── 'unsafe-eval' allowed? → Execute             │
│             └── Otherwise → BLOCK + report violation         │
│                                                                │
└──────────────────────────────────────────────────────────────┘
```

### CSP Lifecycle

```
1. BROWSER LOADS DOCUMENT
   Receives HTTP response with CSP header

2. CSP POLICY PARSED
   Browser builds internal policy representation
   Multiple policies: intersection (all must allow)

3. RESOURCE REQUEST OCCURS
   Script, style, image, font, fetch, frame, etc.

4. POLICY VALIDATION
   Browser checks resource against relevant directive
   Falls back to default-src if specific directive absent

5. ALLOW/BLOCK DECISION
   Allowed → resource loads normally
   Blocked → resource not loaded, error in console

6. VIOLATION REPORTING
   If report-uri/report-to configured → sends JSON report
   Includes: violated directive, blocked URI, document URI
```

### Weak vs Strict CSP

| Approach | Example | Security Level | Bypass Risk |
|----------|---------|---------------|-------------|
| **No CSP** | (none) | ❌ None | Trivial |
| **Weak CSP** | `script-src 'self' *.cdn.com 'unsafe-inline'` | ⚠️ Low | Many bypasses |
| **Moderate CSP** | `script-src 'self' https://trusted.cdn.com` | ⚠️ Medium | JSONP/redirect bypasses |
| **Strict nonce** | `script-src 'nonce-{random}' 'strict-dynamic'` | ✅ High | Very few bypasses |
| **Strict hash** | `script-src 'sha256-{hash}' 'strict-dynamic'` | ✅ High | Very few bypasses |

### Why CSP Is Not a Silver Bullet

- **Doesn't prevent injection** — only prevents execution
- **DOM XSS via allowed scripts** — if your own scripts have DOM XSS, CSP doesn't help
- **Bypass via allowed domains** — JSONP endpoints, open redirects on allowed origins
- **`strict-dynamic` limitations** — trusted scripts can load anything
- **Browser extensions can bypass** — extensions inject scripts outside CSP
- **`<meta>` CSP limitations** — can't set `frame-ancestors`, `report-uri`, `sandbox`

### Real-World Impact

- **Google** deployed strict CSP across all properties — dramatically reduced XSS impact
- **GitHub** uses nonce-based CSP — catches injection attempts in CI
- **Dropbox** published detailed CSP deployment case study
- **Twitter/X** CSP prevented multiple stored XSS from executing
- Companies report **60-80% reduction** in exploitable XSS after strict CSP deployment

---

## 2. Browser Security & CSP Internals

### How Browsers Evaluate CSP

```
┌──────────────────────────────────────────────────────────────┐
│           CSP Evaluation Internal Flow                         │
├──────────────────────────────────────────────────────────────┤
│                                                                │
│  1. HTTP Response received                                   │
│     → Parse Content-Security-Policy header                   │
│     → Parse Content-Security-Policy-Report-Only header       │
│     → Parse <meta http-equiv="Content-Security-Policy">      │
│                                                                │
│  2. Policy stored per document                               │
│     → Multiple policies = ALL must allow (intersection)      │
│     → Report-Only policies evaluated but don't block         │
│                                                                │
│  3. For each resource load:                                  │
│     → Determine resource type (script, style, img, etc.)     │
│     → Find matching directive (script-src, style-src, etc.)  │
│     → If no matching directive → fall back to default-src    │
│     → If no default-src → browser default (allow all)        │
│                                                                │
│  4. Source matching:                                         │
│     → Check against each source expression in directive      │
│     → Nonce match: script nonce == policy nonce?            │
│     → Hash match: SHA of content matches policy hash?       │
│     → Host match: origin matches allowed pattern?           │
│     → Keyword match: 'self', 'unsafe-inline', etc.?        │
│                                                                │
│  5. Decision:                                                │
│     → ANY source matches → ALLOW                            │
│     → NO source matches → BLOCK                            │
│     → Generate violation report                              │
│                                                                │
└──────────────────────────────────────────────────────────────┘
```

### Why Inline Scripts Are Dangerous

```html
<!-- Inline script: no external origin to validate -->
<script>doSomething();</script>

<!-- Event handler: inline JavaScript in attribute -->
<div onclick="handleClick()">Click</div>

<!-- javascript: URL -->
<a href="javascript:void(0)">Link</a>

<!-- WHY they're dangerous: -->
<!-- If attacker achieves HTML injection, they can add: -->
<script>stealCookies()</script>
<img onerror="stealCookies()">
<a href="javascript:stealCookies()">

<!-- Without CSP: browser executes ALL of these -->
<!-- With CSP (no unsafe-inline): NONE execute -->
```

### Why eval() Is Dangerous

```javascript
// eval executes arbitrary strings as code
eval(userInput); // Direct code execution

// These are also eval-like:
new Function("return " + userInput)(); // Dynamic function creation
setTimeout(userInput, 0); // String-form setTimeout
setInterval(userInput, 0); // String-form setInterval

// WHY CSP blocks these:
// If attacker controls ANY string that reaches eval → code execution
// Even without HTML injection, data injection → eval → XSS

// CSP directive: script-src without 'unsafe-eval'
// Blocks: eval, Function, setTimeout(string), setInterval(string)
```

### CSP and Dynamic Script Injection

```javascript
// Creating scripts dynamically:
const script = document.createElement("script");
script.src = "https://cdn.example.com/lib.js";
document.head.appendChild(script);

// WITHOUT strict-dynamic: checked against script-src source list
// WITH strict-dynamic: automatically trusted IF parent script was trusted

// This is why strict-dynamic is important for modern apps:
// Module loaders, lazy loading, and bundler code splitting
// all create scripts dynamically
```

### Browser Engine Differences

| Behavior | Chromium | Firefox | Safari |
|----------|----------|---------|--------|
| CSP3 support | Full | Full | Partial |
| Trusted Types | Supported | Not yet | Not yet |
| `strict-dynamic` | Full | Full | Full |
| `script-src-elem` | Supported | Supported | Limited |
| Report-To API | Supported | Partial | Not yet |
| `wasm-unsafe-eval` | Supported | Supported | Supported |
| Multiple policies | Intersection | Intersection | Intersection |

---

## 3. CSP Directives Deep Dive

### Core Directives Reference

#### script-src (Most Important for XSS)

```http
# Controls JavaScript execution
script-src 'nonce-abc123' 'strict-dynamic';

# Sub-directives (CSP3):
script-src-elem 'nonce-abc123';  # <script> elements only
script-src-attr 'unsafe-inline'; # Inline event handlers only (e.g., onclick)
```

| Source Value | Meaning | Security |
|-------------|---------|----------|
| `'none'` | Block all scripts | Maximum (breaks everything) |
| `'self'` | Same origin only | Good baseline |
| `'nonce-{random}'` | Match nonce attribute | ✅ Recommended |
| `'sha256-{hash}'` | Match content hash | ✅ Recommended (static) |
| `'strict-dynamic'` | Trust propagation from nonced scripts | ✅ Recommended |
| `'unsafe-inline'` | Allow all inline scripts | ❌ Defeats CSP purpose |
| `'unsafe-eval'` | Allow eval() | ❌ Dangerous |
| `'wasm-unsafe-eval'` | Allow WebAssembly compilation | ⚠️ Targeted |
| `https://cdn.com` | Allow from specific origin | ⚠️ Bypass risk |
| `https:` | Allow from any HTTPS | ❌ Too broad |
| `*` | Allow everything | ❌ No protection |

#### default-src

```http
# Fallback for all fetch directives that aren't explicitly set
default-src 'none';  # Deny everything by default, then allow specifically

# IMPORTANT: default-src does NOT apply to:
# - base-uri
# - form-action
# - frame-ancestors
# - sandbox
# These must be set independently
```

#### style-src

```http
style-src 'self' 'nonce-abc123';
# Or for CSS-in-JS (common in React):
style-src 'self' 'unsafe-inline';  # Often necessary trade-off
```

#### connect-src

```http
# Controls fetch, XHR, WebSocket, EventSource
connect-src 'self' https://api.example.com wss://ws.example.com;
```

#### img-src

```http
img-src 'self' https: data:;  # Allow HTTPS images + data URIs
# data: needed for inline images (Base64)
# Be careful: data: in script-src is dangerous (not img-src though)
```

#### frame-src & frame-ancestors

```http
# frame-src: what THIS page can embed
frame-src https://youtube.com https://player.vimeo.com;

# frame-ancestors: who can embed THIS page (clickjacking defense)
frame-ancestors 'none';  # No one can iframe this page
frame-ancestors 'self';  # Only same origin can iframe
```

#### base-uri

```http
# Prevents <base> tag injection (relative URL hijacking)
base-uri 'none';  # Always set this — no legitimate reason for dynamic base
```

#### form-action

```http
# Controls where forms can submit
form-action 'self';  # Forms can only submit to same origin
# Prevents credential phishing via injected forms
```

#### object-src

```http
# Controls Flash, Java, other plugins
object-src 'none';  # Always set to 'none' — plugins are deprecated
```

#### worker-src

```http
# Controls Web Worker, Shared Worker, Service Worker origins
worker-src 'self';
# Falls back to child-src → script-src → default-src
```

#### sandbox

```http
# Applies iframe sandbox restrictions to the page itself
sandbox allow-scripts allow-same-origin;
# WARNING: allow-scripts + allow-same-origin together = can remove sandbox
```

#### upgrade-insecure-requests

```http
# Automatically upgrades HTTP → HTTPS for all requests
upgrade-insecure-requests;
```

---

## 4. Nonce, Hash & Strict CSP Deep Dive

### Nonce-Based CSP (Recommended for Dynamic Apps)

```http
Content-Security-Policy: script-src 'nonce-a1b2c3d4e5f6' 'strict-dynamic'; object-src 'none'; base-uri 'none';
```

```html
<!-- Only scripts with matching nonce execute -->
<script nonce="a1b2c3d4e5f6">
  // This executes ✅
  console.log("Trusted script");
</script>

<script>
  // This is BLOCKED ❌ (no nonce)
  alert("Injected!");
</script>

<script nonce="a1b2c3d4e5f6" src="/bundle.js"></script> <!-- ✅ -->
<script src="/evil.js"></script> <!-- ❌ -->
```

**Critical requirements:**
1. **Nonce must be cryptographically random** — at least 128 bits
2. **Nonce must be unique per response** — never reuse across requests
3. **Nonce must be unguessable** — use `crypto.randomBytes(16).toString('base64')`
4. **Nonce must not appear in any cacheable response** — breaks if CDN caches

```typescript
// Secure nonce generation
import crypto from "crypto";

function generateNonce(): string {
  return crypto.randomBytes(16).toString("base64");
}
// Produces: "dGhpcyBpcyBhIHRlc3Q=" (example)
```

### Hash-Based CSP (For Static Content)

```http
Content-Security-Policy: script-src 'sha256-RFWPLDbv2BY+rCkDzsE+0fr8ylGr2R2faWMhq4lfEQc=';
```

```html
<!-- Script content must EXACTLY match the hash (including whitespace) -->
<script>console.log("Hello");</script>
<!-- SHA-256 of 'console.log("Hello");' must match policy hash -->
```

**When to use hashes:**
- Static pages (no server-side rendering per request)
- Known inline scripts that don't change
- CDN-cached pages where nonces can't be per-request

**Limitations:**
- Any change to script content requires updating the hash
- Whitespace-sensitive
- Can't be used with dynamically generated scripts
- Management at scale is difficult

### strict-dynamic

```http
# strict-dynamic: Scripts loaded BY trusted scripts are also trusted
script-src 'nonce-abc123' 'strict-dynamic';
```

```javascript
// This script is trusted (has nonce)
// <script nonce="abc123">

// It dynamically loads another script:
const s = document.createElement("script");
s.src = "https://any-cdn.com/lib.js";
document.head.appendChild(s);
// With strict-dynamic: lib.js is TRUSTED (loaded by trusted parent)
// Without strict-dynamic: lib.js checked against source list
```

**Why strict-dynamic matters:**
- Modern bundlers use dynamic `import()`
- Libraries lazy-load dependencies
- Module loaders create scripts dynamically
- Without `strict-dynamic`, you'd need to list every CDN URL

**Important:** When `strict-dynamic` is present:
- Host-based allowlist entries are IGNORED (`https://cdn.com` has no effect)
- `'self'` is IGNORED
- `'unsafe-inline'` is IGNORED (for scripts with nonces/hashes)
- Only nonces and hashes determine initial trust

### unsafe-inline vs Nonces

```
┌──────────────────────────────────────────────────────────────┐
│       unsafe-inline vs Nonce comparison                       │
├──────────────────────────────────────────────────────────────┤
│                                                                │
│  'unsafe-inline':                                            │
│    - Allows ALL inline scripts                               │
│    - Injected <script> tags execute → XSS works             │
│    - Injected event handlers execute → XSS works            │
│    - Completely negates CSP's XSS protection                │
│    - ❌ NEVER use in production                              │
│                                                                │
│  'nonce-{random}':                                           │
│    - Only scripts with matching nonce execute                │
│    - Attacker can't guess the nonce (cryptographic random)  │
│    - Injected scripts don't have nonce → blocked            │
│    - ✅ Maintains full XSS protection                        │
│                                                                │
│  KEY: If nonce or hash is present, 'unsafe-inline' is       │
│  IGNORED for scripts (CSP3 behavior)                        │
│                                                                │
└──────────────────────────────────────────────────────────────┘
```

### unsafe-eval Implications

```http
# What unsafe-eval allows:
# eval("code")
# new Function("code")
# setTimeout("code", delay)  ← string form only
# setInterval("code", delay) ← string form only

# Libraries that commonly require unsafe-eval:
# - Template engines (Handlebars, EJS client-side)
# - Some older Angular versions
# - Some charting libraries
# - Expression parsers

# Alternative: wasm-unsafe-eval
# Allows WebAssembly.compile() without allowing eval()
script-src 'nonce-xxx' 'wasm-unsafe-eval';
```

### React/Next.js Nonce Strategy

```typescript
// Next.js App Router: middleware.ts
import { NextResponse } from "next/server";
import crypto from "crypto";

export function middleware(request) {
  const nonce = crypto.randomBytes(16).toString("base64");
  
  const csp = [
    `default-src 'none'`,
    `script-src 'nonce-${nonce}' 'strict-dynamic'`,
    `style-src 'self' 'nonce-${nonce}'`,
    `img-src 'self' https: data:`,
    `font-src 'self'`,
    `connect-src 'self' ${process.env.API_URL || ""}`,
    `frame-ancestors 'none'`,
    `base-uri 'none'`,
    `form-action 'self'`,
    `object-src 'none'`,
  ].join("; ");

  const response = NextResponse.next();
  response.headers.set("Content-Security-Policy", csp);
  // Pass nonce to server components
  response.headers.set("x-nonce", nonce);
  return response;
}
```

```tsx
// app/layout.tsx — Passing nonce to scripts
import { headers } from "next/headers";

export default function RootLayout({ children }) {
  const nonce = headers().get("x-nonce") || "";
  
  return (
    <html>
      <head>
        {/* Next.js internal scripts get nonce automatically in App Router */}
      </head>
      <body>
        {children}
        <script nonce={nonce} src="/analytics.js" />
      </body>
    </html>
  );
}
```

### Astro Nonce Strategy

```typescript
// src/middleware.ts (Astro middleware)
import { defineMiddleware } from "astro:middleware";
import crypto from "crypto";

export const onRequest = defineMiddleware(async (context, next) => {
  const nonce = crypto.randomBytes(16).toString("base64");
  context.locals.nonce = nonce;
  
  const response = await next();
  
  response.headers.set("Content-Security-Policy", [
    `default-src 'none'`,
    `script-src 'nonce-${nonce}' 'strict-dynamic'`,
    `style-src 'self' 'unsafe-inline'`,
    `img-src 'self' https: data:`,
    `font-src 'self'`,
    `connect-src 'self'`,
    `frame-ancestors 'none'`,
    `base-uri 'none'`,
    `form-action 'self'`,
    `object-src 'none'`,
  ].join("; "));
  
  return response;
});
```

```astro
---
// src/layouts/Base.astro
const nonce = Astro.locals.nonce;
---
<html>
<head>
  <script nonce={nonce} src="/app.js"></script>
</head>
<body>
  <slot />
</body>
</html>
```

---

## 5. Trusted Types & CSP Integration

### What Trusted Types Solve

```
┌──────────────────────────────────────────────────────────────┐
│           CSP vs Trusted Types                                │
├──────────────────────────────────────────────────────────────┤
│                                                                │
│  CSP prevents:                                               │
│    ✓ Inline script execution (injection via HTML)            │
│    ✓ Unauthorized external script loading                    │
│    ✗ DOM XSS in YOUR OWN scripts                            │
│                                                                │
│  Trusted Types prevents:                                     │
│    ✓ DOM XSS via innerHTML, eval, etc.                      │
│    ✓ Unsafe string → DOM sink assignments                   │
│    ✓ Third-party library DOM XSS                            │
│                                                                │
│  Together: comprehensive XSS defense                         │
│    CSP blocks injected scripts from running                  │
│    Trusted Types blocks injected strings from DOM sinks      │
│                                                                │
└──────────────────────────────────────────────────────────────┘
```

### Enabling Trusted Types via CSP

```http
# Require Trusted Types for all DOM sinks
Content-Security-Policy: require-trusted-types-for 'script';

# Named policies allowed
Content-Security-Policy: trusted-types myPolicy dompurify;

# Combined with script CSP
Content-Security-Policy: 
  script-src 'nonce-abc' 'strict-dynamic';
  require-trusted-types-for 'script';
  trusted-types default dompurify;
```

### Creating Trusted Types Policies

```typescript
// Initialize Trusted Types policy
const sanitizerPolicy = trustedTypes.createPolicy("dompurify", {
  createHTML: (input: string) => DOMPurify.sanitize(input),
  createScriptURL: (input: string) => {
    const url = new URL(input, location.origin);
    if (url.origin === location.origin) return url.toString();
    throw new Error(`Blocked script URL: ${input}`);
  },
  createScript: () => {
    throw new Error("Dynamic script creation blocked");
  },
});

// Usage
element.innerHTML = sanitizerPolicy.createHTML(userContent); // ✅
element.innerHTML = userContent; // ❌ TypeError: not a TrustedHTML
```

### Migration Strategy

```
Phase 1: Report-Only
  Content-Security-Policy-Report-Only: require-trusted-types-for 'script';
  → Collect violations, identify all DOM sinks in codebase
  
Phase 2: Default Policy (Safety Net)
  Create 'default' policy that sanitizes + logs
  → Catches violations without breaking functionality
  
Phase 3: Named Policies
  Create specific policies for known use cases:
  - 'dompurify' for rich text rendering
  - 'script-loader' for dynamic scripts
  
Phase 4: Enforce
  Content-Security-Policy: require-trusted-types-for 'script'; trusted-types dompurify script-loader;
  → Block any policy not in allowlist
```

---

## 6. React / Next.js / Astro CSP Deep Dive

### Why React Makes CSP Complicated

1. **Hydration scripts** — React injects inline scripts for hydration data
2. **CSS-in-JS** — styled-components/emotion create inline `<style>` tags
3. **Dynamic imports** — Code splitting creates runtime script loading
4. **Development mode** — Hot reload requires `eval` and dynamic scripts
5. **Third-party integration** — Analytics, chat widgets need inline scripts

### Next.js App Router CSP (Complete Setup)

```typescript
// middleware.ts
import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";

export function middleware(request: NextRequest) {
  const nonce = Buffer.from(crypto.randomUUID()).toString("base64");
  
  // Different CSP for development vs production
  const isDev = process.env.NODE_ENV === "development";
  
  const scriptSrc = isDev
    ? `'self' 'unsafe-eval' 'unsafe-inline'` // Dev needs eval for HMR
    : `'nonce-${nonce}' 'strict-dynamic'`;
  
  const styleSrc = isDev
    ? `'self' 'unsafe-inline'`
    : `'self' 'unsafe-inline'`; // CSS-in-JS often needs this
  
  const csp = [
    `default-src 'none'`,
    `script-src ${scriptSrc}`,
    `style-src ${styleSrc}`,
    `img-src 'self' https: data: blob:`,
    `font-src 'self' https:`,
    `connect-src 'self' ${process.env.NEXT_PUBLIC_API_URL || ""} ${isDev ? "ws:" : ""}`,
    `media-src 'self'`,
    `frame-src 'none'`,
    `frame-ancestors 'none'`,
    `base-uri 'none'`,
    `form-action 'self'`,
    `object-src 'none'`,
    `manifest-src 'self'`,
    isDev ? "" : `upgrade-insecure-requests`,
  ].filter(Boolean).join("; ");

  const requestHeaders = new Headers(request.headers);
  requestHeaders.set("x-nonce", nonce);

  const response = NextResponse.next({ request: { headers: requestHeaders } });
  response.headers.set("Content-Security-Policy", csp);
  response.headers.set("X-Content-Type-Options", "nosniff");
  response.headers.set("X-Frame-Options", "DENY");
  response.headers.set("Referrer-Policy", "strict-origin-when-cross-origin");
  
  return response;
}

export const config = { matcher: "/((?!_next/static|_next/image|favicon.ico).*)" };
```

```tsx
// app/layout.tsx
import { headers } from "next/headers";
import Script from "next/script";

export default async function RootLayout({ children }: { children: React.ReactNode }) {
  const headersList = await headers();
  const nonce = headersList.get("x-nonce") ?? "";

  return (
    <html lang="en">
      <body>
        {children}
        {/* Third-party scripts with nonce */}
        <Script
          nonce={nonce}
          strategy="afterInteractive"
          src="https://www.googletagmanager.com/gtag/js?id=G-XXXXX"
        />
        <Script nonce={nonce} id="gtag-init" strategy="afterInteractive">
          {`window.dataLayer = window.dataLayer || [];
            function gtag(){dataLayer.push(arguments);}
            gtag('js', new Date());
            gtag('config', 'G-XXXXX');`}
        </Script>
      </body>
    </html>
  );
}
```

### Astro CSP (Complete Setup)

```typescript
// src/middleware.ts
import { defineMiddleware } from "astro:middleware";

export const onRequest = defineMiddleware(async (context, next) => {
  const nonce = Buffer.from(crypto.randomUUID()).toString("base64");
  context.locals.nonce = nonce;
  
  const response = await next();
  
  // Only set CSP for HTML responses
  const contentType = response.headers.get("content-type") || "";
  if (contentType.includes("text/html")) {
    const csp = [
      `default-src 'none'`,
      `script-src 'nonce-${nonce}' 'strict-dynamic'`,
      `style-src 'self' 'unsafe-inline'`, // Astro inlines critical CSS
      `img-src 'self' https: data:`,
      `font-src 'self'`,
      `connect-src 'self'`,
      `frame-ancestors 'none'`,
      `base-uri 'none'`,
      `form-action 'self'`,
      `object-src 'none'`,
    ].join("; ");
    
    response.headers.set("Content-Security-Policy", csp);
  }
  
  return response;
});
```

### Vite Dev Server CSP Issues

```typescript
// vite.config.ts — CSP considerations for development
import { defineConfig } from "vite";

export default defineConfig({
  server: {
    // Vite HMR uses WebSocket + dynamic script injection
    // Strict CSP breaks dev mode
    // Solution: separate CSP for dev vs prod
  },
  // For production builds, inject nonce into script tags:
  html: {
    cspNonce: "{{CSP_NONCE}}", // Placeholder replaced at serve time
  },
});
```

### Third-Party Script Integration with CSP

```typescript
// Strategy: Load third-party scripts with nonce + strict-dynamic

// Google Tag Manager (challenge: it loads many sub-scripts)
// strict-dynamic allows GTM's dynamically loaded scripts
<script nonce={nonce}>
  {`(function(w,d,s,l,i){w[l]=w[l]||[];w[l].push({'gtm.start':
  new Date().getTime(),event:'gtm.js'});var f=d.getElementsByTagName(s)[0],
  j=d.createElement(s),dl=l!='dataLayer'?'&l='+l:'';j.async=true;j.src=
  'https://www.googletagmanager.com/gtm.js?id='+i+dl;f.parentNode.insertBefore(j,f);
  })(window,document,'script','dataLayer','GTM-XXXXX');`}
</script>

// With strict-dynamic: GTM's dynamically created scripts are trusted
// because they're created by a nonced (trusted) parent script
```

---

## 7. Advanced Browser Security Concepts

### CSP Bypasses

| Bypass | How | Prevention |
|--------|-----|-----------|
| **JSONP endpoints** | Allowed origin has JSONP: `callback=alert(1)` | Don't use domain allowlists; use nonces |
| **Open redirects** | Allowed origin redirects to attacker | Use nonces, not domain allowlists |
| **Angular template injection** | CSP allows Angular CDN + `ng-app` | strict-dynamic (ignores domain allowlists) |
| **base-uri injection** | `<base href="evil.com">` hijacks relative URLs | Always set `base-uri 'none'` |
| **Script gadgets** | Existing code in allowed scripts has DOM XSS | Trusted Types + code audit |
| **CSS exfiltration** | `style-src 'unsafe-inline'` + attribute selectors | Strict style-src |
| **Object/embed** | Flash/plugin-based execution | `object-src 'none'` |

### Browser Isolation & COOP/COEP

```http
# Cross-Origin Opener Policy (COOP)
Cross-Origin-Opener-Policy: same-origin
# Isolates browsing context group → prevents cross-window attacks

# Cross-Origin Embedder Policy (COEP)
Cross-Origin-Embedder-Policy: require-corp
# Requires all resources to explicitly opt-in to being loaded

# Cross-Origin Resource Policy (CORP)
Cross-Origin-Resource-Policy: same-origin
# Resource can only be loaded by same-origin pages

# Together: enables SharedArrayBuffer, high-resolution timers
# Security benefit: complete process isolation
```

### Supply Chain & CSP

```
Third-party script compromise:
  1. Attacker compromises CDN or package
  2. Malicious code injected into trusted script
  3. CSP allows the script (trusted source)
  4. Attack executes with full origin access

Defense layers:
  1. Subresource Integrity (SRI)
     <script src="https://cdn.com/lib.js" 
             integrity="sha384-{hash}" crossorigin="anonymous">
     → If CDN content changes, browser blocks it

  2. CSP with strict-dynamic + nonces
     → At least inline injection is blocked

  3. Trusted Types
     → Limits what even compromised scripts can do to DOM

  4. Monitoring
     → SRI failures, CSP violations, behavioral anomalies
```

---

## 8. Secure Architecture & Enterprise CSP Strategy

### Enterprise CSP Rollout Strategy

```
┌──────────────────────────────────────────────────────────────┐
│         Enterprise CSP Deployment Phases                       │
├──────────────────────────────────────────────────────────────┤
│                                                                │
│  Phase 0: Assessment (2-4 weeks)                             │
│    - Audit all inline scripts                                │
│    - Identify third-party script dependencies                │
│    - Map dynamic script creation patterns                    │
│    - Document eval() usage                                   │
│                                                                │
│  Phase 1: Report-Only (4-8 weeks)                            │
│    - Deploy CSP-Report-Only with strict policy               │
│    - Set up reporting endpoint + dashboard                   │
│    - Analyze violations: legitimate vs concerning            │
│    - Fix obvious violations (inline scripts → nonced)       │
│                                                                │
│  Phase 2: Enforce — Non-Critical Pages (2-4 weeks)           │
│    - Enforce on marketing pages, docs, blogs                 │
│    - Monitor for breakage                                    │
│    - Build confidence + fix patterns                         │
│                                                                │
│  Phase 3: Enforce — Application (4-8 weeks)                  │
│    - Enforce on main application                             │
│    - Maintain report-only on most strict policy              │
│    - Gradual tightening                                      │
│                                                                │
│  Phase 4: Strict + Trusted Types (ongoing)                   │
│    - Move to nonce-only (drop domain allowlists)            │
│    - Add Trusted Types (report-only → enforce)              │
│    - Continuous monitoring + governance                       │
│                                                                │
└──────────────────────────────────────────────────────────────┘
```

### Multi-Team CSP Governance

```
Central Platform Team owns:
  - CSP header generation (middleware)
  - Nonce propagation infrastructure
  - Reporting pipeline
  - Policy baseline
  - Exception process

Product Teams own:
  - Ensuring their features work with CSP
  - Requesting exceptions with justification
  - Migrating away from unsafe patterns
  - Testing CSP compliance in CI

Security Team owns:
  - Policy strictness decisions
  - Violation triage
  - Exception approval
  - Incident response for CSP bypasses
```

### CSP for Different Application Types

| App Type | Recommended Policy | Key Challenges |
|----------|-------------------|----------------|
| Static marketing site | Hash-based (no server) | Third-party analytics |
| SSR app (Next.js) | Nonce + strict-dynamic | Hydration scripts, per-request nonce |
| SPA (Vite/React) | Hash-based or meta tag | No server for nonces |
| Admin dashboard | Strict nonce + no third-party | Rich text editors |
| Multi-tenant SaaS | Per-tenant CSP | Tenant customization |
| CMS-driven | Nonce + sanitized content | User HTML rendering |
| Edge-rendered | Nonce at edge | Worker-based nonce generation |

---

## 9. CSP Reporting & Observability

### Report Endpoint Setup

```typescript
// /api/csp-report (Next.js API route)
import { NextRequest, NextResponse } from "next/server";

export async function POST(req: NextRequest) {
  const report = await req.json();
  
  // CSP report structure:
  // {
  //   "csp-report": {
  //     "document-uri": "https://example.com/page",
  //     "violated-directive": "script-src-elem",
  //     "effective-directive": "script-src-elem",
  //     "original-policy": "script-src 'nonce-xxx' 'strict-dynamic'",
  //     "blocked-uri": "inline",
  //     "status-code": 200,
  //     "source-file": "https://example.com/app.js",
  //     "line-number": 42,
  //     "column-number": 15
  //   }
  // }
  
  // Filter noise (browser extensions, etc.)
  const violation = report["csp-report"];
  if (shouldIgnore(violation)) return NextResponse.json({ ok: true });
  
  // Log to monitoring system
  await logToSIEM({
    type: "csp-violation",
    directive: violation["violated-directive"],
    blockedUri: violation["blocked-uri"],
    documentUri: violation["document-uri"],
    sourceFile: violation["source-file"],
    timestamp: Date.now(),
  });
  
  return NextResponse.json({ ok: true });
}

function shouldIgnore(violation: any): boolean {
  const ignoredSources = [
    "moz-extension://",    // Firefox extensions
    "chrome-extension://", // Chrome extensions
    "safari-extension://", // Safari extensions
    "about:",
    "blob:",
  ];
  return ignoredSources.some(s => 
    violation["blocked-uri"]?.startsWith(s) ||
    violation["source-file"]?.startsWith(s)
  );
}
```

### CSP Header with Reporting

```http
# Enforce + report
Content-Security-Policy: 
  script-src 'nonce-abc' 'strict-dynamic';
  object-src 'none';
  base-uri 'none';
  report-uri /api/csp-report;

# Report-only (for testing)
Content-Security-Policy-Report-Only:
  script-src 'nonce-abc' 'strict-dynamic';
  require-trusted-types-for 'script';
  report-uri /api/csp-report;
```

### Monitoring Dashboard Metrics

| Metric | What to track | Alert threshold |
|--------|---------------|-----------------|
| Violation rate | Violations per minute | Sudden spike (5x baseline) |
| Unique violations | Distinct violated-directive + blocked-uri pairs | New unique patterns |
| script-src violations | Blocked script attempts | Any in production |
| Top blocked URIs | Most frequently blocked resources | Unknown domains |
| Source file patterns | Where violations originate | Non-extension sources |

---

## 10. Setup Guide

### Complete CSP Setup (Step by Step)

#### Step 1: Baseline Strict Policy

```http
# Start with the strictest reasonable policy
Content-Security-Policy:
  default-src 'none';
  script-src 'nonce-{PER_REQUEST_RANDOM}' 'strict-dynamic';
  style-src 'self' 'nonce-{PER_REQUEST_RANDOM}';
  img-src 'self' https: data:;
  font-src 'self';
  connect-src 'self';
  frame-src 'none';
  frame-ancestors 'none';
  base-uri 'none';
  form-action 'self';
  object-src 'none';
  upgrade-insecure-requests;
  report-uri /api/csp-report;
```

#### Step 2: Nonce Generation (Node.js)

```typescript
// lib/csp.ts
import crypto from "crypto";

export function generateNonce(): string {
  return crypto.randomBytes(16).toString("base64");
}

export function buildCSP(nonce: string, options?: { reportOnly?: boolean }): string {
  const directives = [
    `default-src 'none'`,
    `script-src 'nonce-${nonce}' 'strict-dynamic'`,
    `style-src 'self' 'nonce-${nonce}'`,
    `img-src 'self' https: data:`,
    `font-src 'self'`,
    `connect-src 'self' ${process.env.API_URL || ""}`.trim(),
    `frame-src 'none'`,
    `frame-ancestors 'none'`,
    `base-uri 'none'`,
    `form-action 'self'`,
    `object-src 'none'`,
    `report-uri /api/csp-report`,
  ];
  
  return directives.join("; ");
}
```

#### Step 3: Nginx CSP Header

```nginx
# nginx.conf
server {
    # For static sites (hash-based)
    add_header Content-Security-Policy "default-src 'none'; script-src 'sha256-xxxx' 'strict-dynamic'; style-src 'self'; img-src 'self' https: data:; font-src 'self'; frame-ancestors 'none'; base-uri 'none'; form-action 'self'; object-src 'none';" always;
    
    # For dynamic sites, use a reverse proxy that adds nonce
    # or handle in application layer
}
```

#### Step 4: Cloudflare Workers CSP

```typescript
// Cloudflare Worker: add CSP with nonce
export default {
  async fetch(request: Request): Promise<Response> {
    const response = await fetch(request);
    const nonce = crypto.randomUUID().replace(/-/g, "").substring(0, 24);
    
    const csp = `script-src 'nonce-${nonce}' 'strict-dynamic'; object-src 'none'; base-uri 'none';`;
    
    // Inject nonce into HTML
    const html = await response.text();
    const nonced = html.replace(/<script/g, `<script nonce="${nonce}"`);
    
    return new Response(nonced, {
      headers: {
        ...Object.fromEntries(response.headers),
        "Content-Security-Policy": csp,
      },
    });
  },
};
```

#### Step 5: CI/CD CSP Validation

```yaml
# .github/workflows/csp-check.yml
name: CSP Validation
on: [push, pull_request]

jobs:
  csp:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: npm ci && npm run build && npm run start &
      - run: sleep 5
      - name: Check CSP headers
        run: |
          CSP=$(curl -sI http://localhost:3000 | grep -i "content-security-policy:")
          echo "CSP: $CSP"
          
          # Fail if unsafe-inline in script-src
          if echo "$CSP" | grep -qi "script-src.*unsafe-inline"; then
            echo "❌ FAIL: unsafe-inline in script-src"
            exit 1
          fi
          
          # Fail if no nonce or hash in script-src
          if ! echo "$CSP" | grep -qiE "script-src.*(nonce-|sha256-|sha384-)"; then
            echo "❌ FAIL: No nonce/hash in script-src"
            exit 1
          fi
          
          # Ensure base-uri is restricted
          if ! echo "$CSP" | grep -qi "base-uri"; then
            echo "⚠️ WARNING: base-uri not set"
          fi
          
          echo "✅ CSP validation passed"
```

---

## 11. Security Tooling Comparison

| Tool | Type | CSP Relevance | CI/CD | Enterprise |
|------|------|---------------|-------|------------|
| **CSP Evaluator (Google)** | Online analyzer | Evaluates policy strength | ❌ | ✅ |
| **csp-header (npm)** | Policy builder | Generates CSP programmatically | ✅ | ✅ |
| **helmet.js** | Express middleware | Sets security headers including CSP | ✅ | ✅ |
| **Trusted Types** | Browser API | DOM XSS prevention with CSP | N/A | ✅ |
| **DOMPurify** | Sanitization | Trusted Types compatible | N/A | ✅ |
| **Semgrep** | SAST | Finds unsafe-inline, missing CSP | ✅ | ✅ |
| **OWASP ZAP** | DAST | Tests CSP effectiveness | ✅ | ✅ |
| **Snyk** | SCA | Vulnerable dependency detection | ✅ | ✅ |
| **Report URI** | SaaS | CSP violation collection/analysis | ✅ | ✅ |
| **Sentry** | Monitoring | CSP report collection | ✅ | ✅ |

---

## 12. Cheatsheet

### Strict CSP Template (Copy-Paste)

```http
# For SSR apps (Next.js, Astro, Remix)
Content-Security-Policy:
  default-src 'none';
  script-src 'nonce-{RANDOM}' 'strict-dynamic';
  style-src 'self' 'nonce-{RANDOM}';
  img-src 'self' https: data:;
  font-src 'self';
  connect-src 'self';
  frame-ancestors 'none';
  base-uri 'none';
  form-action 'self';
  object-src 'none';
  upgrade-insecure-requests;

# For static sites (hash-based)
Content-Security-Policy:
  default-src 'none';
  script-src 'sha256-{HASH}' 'strict-dynamic';
  style-src 'self';
  img-src 'self' https: data:;
  font-src 'self';
  connect-src 'self';
  frame-ancestors 'none';
  base-uri 'none';
  form-action 'self';
  object-src 'none';
```

### Dangerous Anti-Patterns

| Anti-Pattern | Why It's Bad | Fix |
|-------------|-------------|-----|
| `script-src 'unsafe-inline'` | Allows ALL inline scripts → XSS works | Use nonces |
| `script-src 'unsafe-eval'` | Allows eval() → code injection | Refactor away from eval |
| `script-src *` | Allows any source | Use nonces + strict-dynamic |
| `script-src https:` | Any HTTPS site = too broad | Use nonces |
| `script-src 'self' *.cdn.com` | CDN JSONP bypass possible | Nonces + strict-dynamic |
| `default-src 'self'` alone | Missing many directives | Explicit per-type directives |
| No `base-uri` | `<base>` injection hijacks URLs | `base-uri 'none'` |
| No `object-src` | Plugin-based execution | `object-src 'none'` |
| No `frame-ancestors` | Clickjacking possible | `frame-ancestors 'none'` |

### Quick Debugging Workflow

```
1. Open DevTools → Console
   - Look for "[Report Only]" or blocked resource messages
   
2. Check Network tab
   - Failed requests with "(blocked:csp)" status
   
3. Read the violation message:
   "Refused to execute inline script because it violates CSP directive: 'script-src'"
   → Need nonce on that script, or move to external file
   
4. Common fixes:
   - Inline script blocked → Add nonce attribute
   - External script blocked → Add to connect-src or use strict-dynamic
   - Inline style blocked → Add nonce or use 'unsafe-inline' for styles
   - eval() blocked → Refactor code, or add 'unsafe-eval' (last resort)
   - Image blocked → Add source to img-src
```

---

## 13. Real-World Engineering Mindset

### Analytics Integration (Google Analytics, Segment, etc.)

**Problem:** Analytics scripts inject multiple sub-scripts dynamically.

**Strategies:**

| Strategy | How | Pros | Cons |
|----------|-----|------|------|
| Nonce + strict-dynamic | Nonce on loader, dynamic scripts auto-trusted | Secure + functional | Need per-request nonce |
| Proxy analytics | Self-host analytics JS | Full control, CSP-friendly | Maintenance burden |
| Server-side analytics | Send events from server | No client scripts needed | Lose some client data |
| Tag Manager sandbox | Load GTM in sandboxed iframe | Isolated execution | Limited data access |

**Senior engineer's choice:** Nonce + strict-dynamic for most cases. Proxy for privacy-critical apps. Server-side for maximum security.

### CMS Platforms (Contentful, Sanity, Strapi)

**Problem:** CMS content may contain rich HTML including embeds, scripts, iframes.

**Strategy:**
1. Sanitize CMS output server-side (DOMPurify)
2. Render in components that escape by default (React JSX)
3. For embeds: explicit allowlist in `frame-src`
4. Never render raw CMS HTML without sanitization
5. CSP blocks any injected scripts even if sanitization misses something

### Multi-Tenant SaaS

**Problem:** Tenants want custom scripts/widgets, but shared infrastructure.

**Strategy:**
1. Tenant customization rendered in sandboxed iframe
2. Main app has strict CSP
3. Tenant iframe has permissive CSP (isolated origin)
4. Communication via postMessage (validated)
5. Tenant scripts can't access main app cookies/DOM

---

## 14. Brainstorm / Open Questions

### Browser Execution (15 questions)
1. Should this script execute inline or be externalized?
2. What happens when a nonced script creates another script dynamically?
3. How does strict-dynamic change the trust model for dynamically loaded modules?
4. What's the execution order when CSP blocks a critical script?
5. How does the browser handle CSP for scripts in Shadow DOM?
6. What happens to event handlers (onclick) when script-src-attr isn't set?
7. How do module scripts (`type="module"`) interact with CSP nonces?
8. What's the behavior when multiple CSP headers are present?
9. How does CSP affect `importScripts()` in Web Workers?
10. What happens when a Service Worker's CSP differs from the page's?
11. How does CSP evaluate `blob:` and `data:` URLs for scripts?
12. What's the security implication of `'wasm-unsafe-eval'`?
13. How do browsers handle CSP for dynamically inserted `<style>` tags?
14. What happens to `javascript:` URLs under strict CSP?
15. How does CSP interact with browser back-forward cache?

### CSP Architecture (15 questions)
16. What CSP strategy scales across hundreds of microservices?
17. How should nonce propagation work in streaming SSR?
18. Should CSP differ between authenticated and unauthenticated pages?
19. How do you handle CSP for A/B testing scripts?
20. What's the right CSP for a page that embeds third-party payment forms?
21. How should CSP work for progressive web apps with service workers?
22. Should each micro-frontend have its own CSP?
23. How do you handle CSP when migrating from legacy to modern architecture?
24. What's the organizational ownership model for CSP?
25. How should CSP handle dynamic content from CMS?
26. What's the right CSP for server-sent HTML fragments (HTMX)?
27. How do you test CSP effectiveness in CI/CD?
28. Should staging and production have the same CSP?
29. How should CSP handle feature flags that add/remove scripts?
30. What's the recovery plan when CSP breaks production?

### Trusted Types (15 questions)
31. How should Trusted Types migration work for a 5-year-old React app?
32. What's the interaction between Trusted Types and `dangerouslySetInnerHTML`?
33. Should the default Trusted Types policy sanitize or throw?
34. How do third-party libraries interact with Trusted Types?
35. What's the performance overhead of Trusted Types policies?
36. How should teams share Trusted Types policies in a monorepo?
37. What DOM sinks are NOT covered by Trusted Types?
38. How does Trusted Types affect server-side rendering?
39. Should Trusted Types enforcement differ between development and production?
40. What's the testing strategy for Trusted Types policies?
41. How do you debug Trusted Types violations in production?
42. What's the browser support strategy for Trusted Types?
43. How should Trusted Types handle dynamic content from APIs?
44. What's the right granularity for Trusted Types policies?
45. How do Trusted Types interact with Web Components?

### SSR Security (15 questions)
46. How should nonces work with edge caching?
47. What's the CSP implication of partial prerendering?
48. How does streaming SSR affect nonce delivery?
49. Should React Server Components have different CSP considerations?
50. How does ISR (Incremental Static Regeneration) interact with nonce-based CSP?
51. What's the CSP strategy for hybrid static/dynamic pages?
52. How should CSP handle hydration data in `<script>` tags?
53. What's the security model for server-side component streaming?
54. How do you ensure nonce consistency across chunked responses?
55. What's the CSP implication of React Suspense boundaries?
56. How should CSP work with Astro's partial hydration?
57. What's the right CSP for pages with both static and dynamic islands?
58. How does next/font affect style-src CSP?
59. What's the CSP strategy for preview/draft mode in CMS?
60. How should error pages handle CSP (error boundary rendering)?

### Third-Party Scripts (15 questions)
61. Should analytics scripts be loaded via strict-dynamic or explicit source?
62. How do you audit third-party scripts for CSP compatibility?
63. What's the risk of strict-dynamic with compromised third-party?
64. Should Google Tag Manager be loaded inside a sandbox?
65. How do you handle consent management platforms and CSP?
66. What's the CSP strategy for embedded payment forms (Stripe)?
67. How should live chat widgets work with strict CSP?
68. What's the impact of blocking a third-party script in production?
69. How do you roll back CSP when it breaks third-party functionality?
70. Should third-party scripts ever be self-hosted?
71. How do you monitor third-party script changes?
72. What's the SRI strategy for third-party scripts?
73. How should CSP handle social media embeds?
74. What's the security model for third-party iframes?
75. How do you handle third-party scripts that use eval()?

### Enterprise AppSec (15 questions)
76. How should CSP governance work across 50+ frontend apps?
77. What metrics should security teams track for CSP?
78. How do you handle CSP exceptions (unsafe-inline) in specific services?
79. What's the rollback strategy for CSP deployment failures?
80. How should CSP fit into the SDLC?
81. What's the cost-benefit of Trusted Types deployment at scale?
82. How do you train 200+ developers on CSP best practices?
83. What's the incident response plan for CSP-bypass XSS?
84. How should CSP maturity be measured across an organization?
85. What automated checks should run on every deployment?
86. How do you handle legacy applications that can't support strict CSP?
87. What's the CSP strategy for acquired companies/products?
88. How should CSP violations feed into threat intelligence?
89. What's the ROI model for CSP investment?
90. How do you prioritize CSP improvements across services?

### Framework Integration (15 questions)
91. How does Next.js App Router handle nonce propagation differently than Pages Router?
92. What CSP challenges does React's streaming SSR introduce?
93. How should Astro islands handle per-island CSP needs?
94. What's the CSP strategy for Remix's nested routes?
95. How does Vite's dev server interact with CSP during development?
96. What CSP challenges do CSS-in-JS libraries create?
97. How should Web Components handle CSP for their shadow DOM scripts?
98. What's the CSP strategy for Svelte's compile-time approach?
99. How do React Server Components change CSP needs?
100. What CSP challenges does Qwik's resumability model create?

### Browser Isolation (10 questions)
101. How does COOP/COEP interact with CSP?
102. What's the security model for cross-origin isolated pages?
103. How does process isolation change the XSS threat model?
104. Should CSP differ for cross-origin isolated contexts?
105. How does browser Site Isolation affect CSP enforcement?
106. What's the relationship between CSP sandbox and iframe sandbox?
107. How should CSP handle fenced frames?
108. What's the CSP model for Shared Workers across origins?
109. How does speculation rules API interact with CSP?
110. What's the future of CSP with browser partition (privacy sandbox)?

### Security Governance (10+ questions)
111. How should security champions program integrate CSP education?
112. What's the maturity model for CSP deployment?
113. How should security design reviews evaluate CSP?
114. What's the feedback loop between violations and engineering?
115. How should CSP fit into compliance requirements (SOC2, etc.)?
116. What's the relationship between CSP and bug bounty programs?
117. How should CSP evolution track browser spec changes?
118. What's the deprecation strategy for weakened CSP exceptions?
119. How should CSP documentation be maintained?
120. What's the knowledge sharing model for CSP across teams?

---

## 15. Practice Questions

### Beginner (35 questions)

**Q1.** What does CSP stand for?
- **Type:** Fill in the blank
- **Answer:** Content Security Policy

**Q2.** True or False: CSP prevents XSS by stopping injection.
- **Type:** True/False
- **Answer:** False
- **Why:** CSP doesn't prevent injection — it prevents EXECUTION of injected code. The injection still occurs, but the browser refuses to run the injected script.

**Q3.** Which HTTP header delivers CSP?
- A) X-Content-Security-Policy
- B) Content-Security-Policy
- C) X-CSP-Policy
- D) Security-Policy
- **Type:** Single choice
- **Answer:** B) Content-Security-Policy

**Q4.** What does `script-src 'self'` mean?
- **Type:** Short answer
- **Answer:** Only scripts from the same origin (same scheme + host + port) are allowed to execute. External scripts from other domains and inline scripts are blocked.

**Q5.** True or False: `'unsafe-inline'` in script-src is recommended for production.
- **Type:** True/False
- **Answer:** False
- **Why:** `'unsafe-inline'` allows ANY inline script to execute, which means injected `<script>` tags will run — completely negating CSP's XSS protection.

**Q6.** What happens when a script violates CSP?
- A) Browser shows a warning but executes it
- B) Browser blocks execution and may send a report
- C) Server rejects the request
- D) The page is redirected
- **Type:** Single choice
- **Answer:** B) Browser blocks execution and may send a report

**Q7.** What is the `default-src` directive?
- **Type:** Short answer
- **Answer:** A fallback directive that applies to any resource type that doesn't have its own specific directive set. If `img-src` isn't specified but `default-src 'self'` is, images follow the `default-src` policy.

**Q8.** True or False: CSP can be set via a `<meta>` tag.
- **Type:** True/False
- **Answer:** True — via `<meta http-equiv="Content-Security-Policy" content="...">`. However, some directives (`frame-ancestors`, `report-uri`, `sandbox`) cannot be set this way.

**Q9.** What does `object-src 'none'` do?
- **Type:** Short answer
- **Answer:** Blocks all `<object>`, `<embed>`, and `<applet>` elements from loading any content. This prevents Flash/plugin-based attacks.

**Q10.** Which directive prevents clickjacking?
- A) script-src
- B) frame-src
- C) frame-ancestors
- D) default-src
- **Type:** Single choice
- **Answer:** C) frame-ancestors
- **Why:** `frame-ancestors` controls who can embed this page in an iframe. Setting it to `'none'` prevents all framing (like X-Frame-Options: DENY).

**Q11-Q35:** *(Additional beginner questions covering basic directives, CSP delivery methods, violation behavior, and common misconfigurations)*

**Q11.** What does `base-uri 'none'` prevent?
- **Answer:** Prevents `<base href="...">` injection that could hijack all relative URLs on the page to point to an attacker-controlled domain.

**Q12.** True or False: CSP blocks all cross-origin requests.
- **Answer:** False — CSP only blocks resources that don't match the policy. If `img-src https:` is set, any HTTPS image loads fine. CSP is an allowlist, not a blanket block.

**Q13.** What is `report-uri` used for?
- **Answer:** Specifies a URL where the browser sends JSON violation reports when resources are blocked by CSP. Enables monitoring of CSP effectiveness and attempted attacks.

---

### Junior (35 questions)

**Q36.** What is a CSP nonce and why must it be random?
- **Type:** Short answer
- **Answer:** A nonce is a cryptographically random value added to the CSP header and matching `<script nonce="...">` attributes. It must be random (unguessable) so attackers can't predict it and add it to injected scripts. Must be unique per response.

**Q37.** Your Next.js app has CSP violations from inline styles created by styled-components. What's the fix?
- **Type:** Scenario-based
- **Answer:** Options: 1) Add nonce to style tags (styled-components supports `__webpack_nonce__`), 2) Use `style-src 'unsafe-inline'` (acceptable trade-off since CSS injection is less severe than script injection), 3) Extract styles to external CSS at build time. Most teams choose option 2 for CSS-in-JS.

**Q38.** True or False: When `strict-dynamic` is present, host-based allowlists in script-src are ignored.
- **Type:** True/False
- **Answer:** True — `strict-dynamic` tells the browser to ignore host allowlists and `'self'`, relying only on nonces/hashes for initial trust and propagating trust to dynamically loaded scripts.

**Q39.** What's the difference between `script-src-elem` and `script-src-attr`?
- **Type:** Short answer
- **Answer:** `script-src-elem` controls `<script>` elements (both inline and external). `script-src-attr` controls inline event handlers (onclick, onerror, etc.). They allow more granular control — you can block event handlers while allowing nonced script elements.

**Q40.** A CSP violation report shows `blocked-uri: "inline"`. What does this mean?
- **Type:** Debugging
- **Answer:** An inline script (or event handler) was blocked. Could be: a `<script>` tag without a nonce, an event handler like `onclick="..."`, or a `javascript:` URL. Check the `source-file` and `line-number` fields to find the specific code.

**Q41.** How do multiple CSP policies interact?
- **Type:** Short answer
- **Answer:** When multiple CSP policies are present (multiple headers or header + meta), ALL policies must allow a resource. It's an intersection — the most restrictive wins. You can't make policy more permissive by adding another header.

---

### Senior (35 questions)

**Q71.** Design a CSP strategy for a Next.js App Router application with Google Analytics, Stripe payments, and a rich text editor.
- **Type:** Architecture challenge
- **Answer:** Nonce-based with strict-dynamic via middleware. GA: nonced loader script, strict-dynamic propagates trust to GA's sub-scripts. Stripe: add `frame-src https://js.stripe.com; connect-src https://api.stripe.com`. Rich text editor: if it needs innerHTML, use Trusted Types policy with DOMPurify. Style: `'self' 'unsafe-inline'` for editor CSS. Add `report-uri` for monitoring. Deploy report-only first for 2 weeks.

**Q72.** Your CSP report dashboard shows 10,000 violations per hour after deployment. 90% are from browser extensions. How do you handle this?
- **Type:** Incident response
- **Answer:** 1) Filter extension violations server-side (chrome-extension://, moz-extension://, safari-extension:// in blocked-uri or source-file), 2) Don't alert on these, 3) Create separate dashboard for legitimate violations, 4) Focus on violations from your own domain or unknown sources, 5) Set up rate limiting on report endpoint.

**Q73.** How should nonce propagation work in a streaming SSR response (React 18+ with Suspense)?
- **Type:** Architecture
- **Answer:** Generate nonce before streaming starts (in middleware). Include CSP header with nonce (headers are sent before body). All script tags throughout the stream use the same nonce. Challenge: if using HTTP/2 server push or early hints, nonce must be decided at connection time. For chunked HTML with Suspense, nonce is available in the request context throughout the render.

---

### Expert / Browser Security Engineer (35 questions)

**Q106.** Explain how a JSONP endpoint on an allowed origin can bypass CSP and how strict-dynamic prevents this.
- **Type:** Deep analysis
- **Answer:** If CSP is `script-src https://trusted-api.com`, and that API has a JSONP endpoint (`/jsonp?callback=alert`), attacker injects: `<script src="https://trusted-api.com/jsonp?callback=alert(document.cookie)//"></script>`. The response is valid JS that executes `alert(document.cookie)`. With `strict-dynamic`: domain allowlists are ignored; only nonced scripts are trusted. Even if the JSONP URL is loaded, it lacks a nonce → blocked.

**Q107.** A researcher reports a CSP bypass using a script gadget in React's error overlay in development. Is this a real vulnerability?
- **Type:** Scenario-based
- **Answer:** No — development mode should have relaxed CSP (with `unsafe-eval` for HMR). The real question is: does production have strict CSP? Development CSP bypasses are expected and acceptable. If React's error overlay is present in production builds → that's a different bug (dev code in production).

**Q108.** Design a Trusted Types + CSP architecture for an enterprise with React microfrontends, a shared component library, and third-party analytics.
- **Type:** Architecture
- **Answer:** Shell app sets CSP + Trusted Types enforcement. Shared library provides pre-built policies: 'sanitizer' (DOMPurify-backed) and 'safe-url' (protocol validation). Each MFE uses these named policies — can't create arbitrary policies. Third-party analytics loaded via nonced script in shell. Default policy in report mode catches any missed sinks. Monthly review of violation reports → migrate remaining sinks to typed policies. CI checks: no `innerHTML` without policy, no `eval`, no `unsafe-inline`.

---

## 16. Personalized Recommendations

### For Your Stack (React + Next.js + Astro + Vite + TypeScript)

#### Priority CSP Concepts

1. **Immediate:** Deploy nonce-based CSP in Next.js middleware
2. **Immediate:** Set `base-uri 'none'`, `object-src 'none'`, `frame-ancestors 'none'`
3. **High:** Understand strict-dynamic for code splitting/dynamic imports
4. **High:** Handle CSS-in-JS (accept `style-src 'unsafe-inline'` or use nonces)
5. **Medium:** Set up CSP reporting endpoint + dashboard
6. **Medium:** Trusted Types in report-only mode
7. **Advanced:** Per-page CSP tuning for different security profiles
8. **Advanced:** Auditing third-party scripts for CSP compatibility

#### 60-Day Learning Plan

**Week 1-2: Foundations**
- [ ] Understand all CSP directives and what they control
- [ ] Deploy report-only CSP on your Next.js app
- [ ] Set up CSP violation reporting endpoint
- [ ] Analyze violations — understand what's breaking and why

**Week 3-4: Implementation**
- [ ] Implement nonce generation in Next.js middleware
- [ ] Add nonces to all `<script>` tags
- [ ] Configure strict-dynamic for dynamic imports
- [ ] Handle CSS-in-JS compatibility (style-src decision)
- [ ] Move from report-only to enforcing on non-critical pages

**Week 5-6: Production Hardening**
- [ ] Enforce CSP on all pages
- [ ] Set up violation alerting (spike detection)
- [ ] Implement Trusted Types in report-only
- [ ] Add CSP validation to CI/CD pipeline
- [ ] Document CSP exception process for team

**Week 7-8: Advanced**
- [ ] Implement Trusted Types enforcement
- [ ] Audit third-party scripts for compatibility
- [ ] Set up SRI for external scripts
- [ ] Build CSP dashboard with violation analytics
- [ ] Study CSP bypasses and harden configuration
- [ ] Plan organizational CSP governance

---

## 17. Official Documentation & Reference Links

### Beginner

| Resource | URL |
|----------|-----|
| MDN: Content Security Policy | https://developer.mozilla.org/en-US/docs/Web/HTTP/CSP |
| CSP Reference (all directives) | https://content-security-policy.com |
| OWASP CSP Cheat Sheet | https://cheatsheetseries.owasp.org/cheatsheets/Content_Security_Policy_Cheat_Sheet.html |
| Google: CSP Overview | https://developers.google.com/web/fundamentals/security/csp |
| MDN: Web Security | https://developer.mozilla.org/en-US/docs/Web/Security |

### Intermediate

| Resource | URL |
|----------|-----|
| Google: Strict CSP | https://csp.withgoogle.com/docs/strict-csp.html |
| Chrome: CSP XSS Prevention | https://developer.chrome.com/docs/lighthouse/best-practices/csp-xss/ |
| Next.js CSP Guide | https://nextjs.org/docs/app/building-your-application/configuring/content-security-policy |
| web.dev: Trusted Types | https://web.dev/trusted-types/ |
| PortSwigger: CSP | https://portswigger.net/web-security/cross-site-scripting/content-security-policy |
| Google CSP Evaluator | https://csp-evaluator.withgoogle.com |

### Advanced

| Resource | URL |
|----------|-----|
| W3C CSP Level 3 Spec | https://w3c.github.io/webappsec-csp/ |
| Trusted Types Spec | https://w3c.github.io/trusted-types/dist/spec/ |
| OWASP Secure Headers | https://owasp.org/www-project-secure-headers/ |
| Google: Deploying Strict CSP | https://web.dev/strict-csp/ |
| CSP bypass techniques | https://book.hacktricks.xyz/pentesting-web/content-security-policy-csp-bypass |

### Expert / Browser Internals

| Resource | URL |
|----------|-----|
| Chromium CSP Implementation | https://source.chromium.org/chromium/chromium/src/+/main:third_party/blink/renderer/core/frame/csp/ |
| HTML Spec: CSP Integration | https://html.spec.whatwg.org/multipage/origin.html |
| Fetch Spec: CSP Check | https://fetch.spec.whatwg.org/#should-response-to-request-be-blocked-by-content-security-policy |
| Chromium Security Architecture | https://www.chromium.org/Home/chromium-security/ |
| CSP Research Papers | https://research.google/pubs/ (search "CSP") |

---

## 18. Advanced Engineering Topics

### CSP Enforcement Architecture (Browser Internals)

```
Document loads → CSP header parsed → ContentSecurityPolicy object created
                                           │
For each resource load request:            │
  ResourceRequest → ContentSecurityPolicy::AllowRequest()
                           │
                           ├── Check directive for resource type
                           ├── Evaluate source expressions
                           ├── Check nonce match
                           ├── Check hash match
                           ├── Check 'strict-dynamic' propagation
                           └── Decision: Allow / Block / Report
```

### Future CSP Directions

- **CSP Level 4:** Further refinements, better `script-src` granularity
- **Trusted Types v2:** Expanded sink coverage
- **Browser Sanitizer API:** Native DOMPurify alternative
- **Speculation Rules:** New resource loading → new CSP considerations
- **View Transitions:** New execution context implications
- **Fenced Frames:** Privacy-preserving embedding with CSP implications
- **WebAssembly components:** New execution model needs CSP coverage

### Secure-by-Default Framework Design

```typescript
// Framework-level CSP enforcement (platform team)
// Every page automatically gets strict CSP

// shared/csp-middleware.ts
export function createCSPMiddleware(options?: CSPOptions) {
  return (req, res, next) => {
    const nonce = generateNonce();
    req.nonce = nonce; // Available to rendering
    
    const policy = buildPolicy(nonce, {
      connectSrc: options?.apiDomains || [],
      frameSrc: options?.allowedFrames || [],
      reportUri: options?.reportEndpoint || "/api/csp-report",
    });
    
    res.setHeader("Content-Security-Policy", policy);
    next();
  };
}

// Developers never set CSP themselves — it's automatic
// They only declare exceptions via configuration:
// csp.config.ts
export default {
  allowedFrames: ["https://js.stripe.com"],
  apiDomains: ["https://api.example.com"],
};
```

---

## Summary

### Key Takeaways

1. **CSP prevents execution, not injection** — it's a safety net, not a primary defense
2. **Nonce + strict-dynamic is the recommended approach** for dynamic apps
3. **`unsafe-inline` in script-src destroys CSP's value** — never use in production
4. **Always set:** `base-uri 'none'`, `object-src 'none'`, `frame-ancestors 'none'`
5. **Trusted Types + CSP = comprehensive XSS defense** — CSP blocks injected scripts, TT blocks DOM XSS
6. **Deploy incrementally:** Report-only → enforce non-critical → enforce all → tighten
7. **Reporting is essential** — you can't improve what you don't measure
8. **strict-dynamic makes modern apps possible** — enables code splitting, lazy loading, module loaders

### Next Steps

1. Deploy report-only CSP with strict nonce policy today
2. Set up violation reporting endpoint
3. Analyze violations for 1-2 weeks
4. Fix inline scripts (add nonces or externalize)
5. Move to enforcement mode incrementally

### Advanced Topics to Continue Learning

- CSP bypass techniques and defenses
- Trusted Types enterprise deployment
- Browser Sanitizer API (emerging standard)
- Speculation Rules and CSP interaction
- Cross-origin isolation (COOP/COEP) with CSP
- Supply-chain security and SRI at scale
- CSP for WebAssembly applications

