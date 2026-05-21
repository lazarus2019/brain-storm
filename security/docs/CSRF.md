---
title: Cross-Site Request Forgery (CSRF)
description: Complete CSRF deep-dive guide covering browser security models, attack
  types, defense mechanisms, authentication architecture, OAuth/OIDC security, React/Next.js/Astro
  patterns, and enterprise AppSec strategy
slug: csrf
modifiedDate: '2026-05-20'
draft: false
featured: true
tags:
- security
- csrf
- authentication
- cookies
- oauth
- browser-security
- samesite
categories:
- security
seo:
  title: Cross-Site Request Forgery (CSRF) — Ultimate Deep-Dive Guide
  description: Complete CSRF engineering guide covering browser security models, attack
    types, defense mechanisms, authentication architecture, OAuth/OIDC, React/Next.js/Astro
    patterns, and enterprise AppSec strategy
  canonical: https://feel-free.com/blogs/csrf
  keywords:
  - csrf
  - cross-site request forgery
  - security
  - samesite cookies
  - csrf tokens
  - oauth csrf
  - browser security
  - authentication
author: lazarus2019
lang: en
relatedPosts:
- cors-and-proxy
- cors-and-proxy-quizs
- csp
- xss
---

# Cross-Site Request Forgery (CSRF) — Ultimate Deep-Dive Guide

A complete engineering guide from beginner concepts to browser-security-engine-level mental models and enterprise-scale secure web architecture.

---

## Table of Contents

1. [Big Picture](#1-big-picture)
2. [Browser Networking & Security Deep Dive](#2-browser-networking--security-deep-dive)
3. [CSRF Attack Types Deep Dive](#3-csrf-attack-types-deep-dive)
4. [CSRF Defense Mechanisms Deep Dive](#4-csrf-defense-mechanisms-deep-dive)
5. [Cookies, Sessions & Authentication Architecture](#5-cookies-sessions--authentication-architecture)
6. [React / Next.js / Astro CSRF Deep Dive](#6-react--nextjs--astro-csrf-deep-dive)
7. [CORS, SOP & CSRF Relationship](#7-cors-sop--csrf-relationship)
8. [Secure Architecture & Enterprise CSRF Strategy](#8-secure-architecture--enterprise-csrf-strategy)
9. [OAuth / OIDC / SSO CSRF Deep Dive](#9-oauth--oidc--sso-csrf-deep-dive)
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

### What CSRF Actually Is

Cross-Site Request Forgery (CSRF) is an attack where a malicious website causes a victim's browser to perform an unwanted action on a trusted site where the victim is authenticated. The attack exploits the browser's **automatic credential attachment** behavior — browsers automatically include cookies (session tokens, auth tokens) with every request to a domain, regardless of which site initiated the request.

**The core problem:** The server cannot distinguish between a request the user intentionally made and a request a malicious site tricked the user's browser into making.

### Why CSRF Exists

CSRF exists because of a fundamental design decision in web browsers:

1. **Browsers automatically attach cookies** to requests based on the destination domain, not the origin of the request
2. **HTTP is stateless** — servers rely on cookies/sessions to maintain authentication state
3. **The web was designed for document linking** — any page can link/submit to any other page
4. **Trust is domain-based** — cookies are scoped to domains, not to specific pages or origins

```
┌─────────────────────────────────────────────────────────────────┐
│                    CSRF Mental Model                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│   User authenticates to bank.com                                 │
│        │                                                          │
│        ▼                                                          │
│   Browser stores session cookie: bank.com → session=abc123       │
│        │                                                          │
│        ▼                                                          │
│   User visits evil.com (in another tab)                          │
│        │                                                          │
│        ▼                                                          │
│   evil.com contains: <form action="bank.com/transfer" ...>       │
│        │                                                          │
│        ▼                                                          │
│   Browser sends POST to bank.com WITH session cookie attached    │
│        │                                                          │
│        ▼                                                          │
│   bank.com sees valid session → executes transfer                │
│                                                                   │
│   ⚠️  Server cannot tell this request came from evil.com          │
└─────────────────────────────────────────────────────────────────┘
```

### CSRF vs Related Attacks

| Attack | What it exploits | Direction | Credential handling |
|--------|-----------------|-----------|-------------------|
| **CSRF** | Server's trust in the browser's cookies | Cross-site → target server | Browser auto-attaches credentials |
| **XSS** | Client's trust in server content | Injected script runs in target origin | Full access to cookies, DOM, storage |
| **Clickjacking** | User's visual perception | Overlaid frames trick clicks | User actively clicks (visible action) |
| **SSRF** | Server's ability to make requests | Server → internal resources | Server's own credentials |
| **CORS misconfiguration** | Overly permissive access control | Cross-origin reads | May allow credential-bearing reads |

**Key distinction:** CSRF is a **write-focused** attack (cause side effects). XSS is a **read+write** attack (full origin access). CORS protects **reading** cross-origin responses, not **sending** requests.

### Browser Trust Model

```
┌─────────────────────────────────────────────────────────────┐
│                Browser Security Model                         │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  Same-Origin Policy (SOP):                                   │
│    - Prevents READING cross-origin responses                 │
│    - Does NOT prevent SENDING cross-origin requests          │
│    - Origin = scheme + host + port                           │
│                                                               │
│  Cookie Policy:                                               │
│    - Cookies attached based on DESTINATION domain            │
│    - Not based on which page initiated the request           │
│    - SameSite attribute modifies this behavior               │
│                                                               │
│  Request Initiation:                                         │
│    - Any page can submit forms to any URL                    │
│    - Any page can load images from any URL                   │
│    - Any page can trigger navigation to any URL              │
│    - JavaScript fetch/XHR: limited by CORS for reads         │
│      but requests ARE still sent (simple requests)           │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

### Origin vs Site

| Concept | Definition | Example |
|---------|-----------|---------|
| **Origin** | scheme + host + port | `https://app.example.com:443` |
| **Site** | scheme + eTLD+1 | `https://example.com` |
| **Same-origin** | Exact scheme + host + port match | `https://a.example.com` ≠ `https://b.example.com` |
| **Same-site** | Same scheme + eTLD+1 | `https://a.example.com` = `https://b.example.com` |

This distinction matters because **SameSite cookies** use the **site** definition, not origin. A subdomain can still send same-site requests.

### CSRF Attack Lifecycle

```
1. VICTIM AUTHENTICATES
   User logs into bank.com → receives session cookie
   
2. ATTACKER SITE LOADED
   User visits evil.com (phishing link, ad, forum post)
   
3. FORGED REQUEST CREATED
   evil.com contains hidden form/script targeting bank.com
   
4. BROWSER AUTO-ATTACHES CREDENTIALS
   Browser sees request to bank.com → attaches bank.com cookies
   
5. SERVER TRUSTS REQUEST
   bank.com receives valid session → processes request
   
6. UNAUTHORIZED ACTION SUCCEEDS
   Money transferred, email changed, password reset, etc.
```

### CSRF Variants Comparison

| Variant | Mechanism | Severity | Common Target |
|---------|-----------|----------|---------------|
| **Traditional CSRF** | Hidden form auto-submits | High | State-changing endpoints |
| **Login CSRF** | Forces login with attacker's account | Medium-High | OAuth/login endpoints |
| **Stored CSRF** | CSRF payload stored in target site (via HTML injection) | Critical | Forums, user content |
| **API CSRF** | Fetch/XHR with credentials | High | JSON APIs using cookies |
| **Client-side CSRF** | Manipulates client-side routing/state | Medium | SPAs with client-side logic |

### When CSRF Becomes Critical

- **Financial transactions:** Wire transfers, payments, purchases
- **Account takeover:** Email/password change, linked account changes
- **Administrative actions:** User management, system configuration
- **Data exfiltration (indirect):** Change notification email, export to attacker-controlled destination
- **Privilege escalation:** Invite attacker as admin, change roles

### Real-World Impact

- **2008 — Netflix:** CSRF allowed attackers to change victim's account details
- **2012 — YouTube:** CSRF in video like/subscribe functionality
- **2016 — GitHub:** Login CSRF in OAuth integration
- **Banking systems:** Multiple undisclosed vulnerabilities involving wire transfers
- **Enterprise SaaS:** Role elevation via CSRF in admin panels

---

## 2. Browser Networking & Security Deep Dive

### How Browsers Attach Cookies

When the browser makes ANY request to `example.com`, it checks its cookie jar:

```
Request to: https://example.com/api/transfer
Cookie jar lookup: domain=example.com, path=/, secure=true

Result: Cookie: session=abc123; csrf_token=xyz789

Attached regardless of:
  - Which tab/window initiated the request
  - Which origin the request came from
  - Whether it was user-initiated or script-initiated
  - Whether it was a form submission, image load, or fetch()
  
UNLESS SameSite restrictions apply.
```

### SameSite Cookie Deep Dive

SameSite is the **most important modern CSRF defense at the browser level**.

| Value | Cross-site GET | Cross-site POST | Cross-site fetch | Top-level navigation |
|-------|---------------|-----------------|------------------|---------------------|
| `Strict` | ❌ Blocked | ❌ Blocked | ❌ Blocked | ❌ Blocked |
| `Lax` | ❌ Blocked | ❌ Blocked | ❌ Blocked | ✅ Sent (top-level GET only) |
| `None` | ✅ Sent | ✅ Sent | ✅ Sent | ✅ Sent |
| Not set (modern default) | Same as `Lax` | Same as `Lax` | Same as `Lax` | Same as `Lax` |

**Critical nuance of `Lax`:**
- Cookies ARE sent on **top-level navigations** (clicking a link, address bar navigation) that use GET
- Cookies are NOT sent on:
  - Cross-site POST form submissions
  - Cross-site subresource requests (images, scripts, iframes)
  - Cross-site fetch/XHR
  - POST navigations from cross-site

**Why `Lax` allows top-level GET navigations:**
If `Strict` were default, clicking a link to GitHub from Google would log you out — terrible UX. `Lax` is the compromise between security and usability.

**The "Lax+POST" 2-minute window (Chrome):**
Chrome previously had a temporary exception: cookies without SameSite set were treated as `Lax` but still sent on top-level cross-site POST within 2 minutes of being set. This was removed in later versions.

### Fetch Credentials Modes

```typescript
// credentials: "omit" — never send cookies
fetch("https://api.example.com/data", { credentials: "omit" });

// credentials: "same-origin" — only send for same-origin (DEFAULT)
fetch("https://api.example.com/data", { credentials: "same-origin" });

// credentials: "include" — always send cookies (even cross-origin)
fetch("https://api.example.com/data", { credentials: "include" });
```

**Critical insight:** Even with `credentials: "include"`, SameSite restrictions still apply at the browser level. The `credentials` option tells the browser you WANT to send cookies, but SameSite may still prevent it.

### Why Forms Are Dangerous

Forms are the original CSRF vector because:

1. **No CORS preflight** — Form submissions are "simple requests"
2. **No JavaScript needed** — Pure HTML can submit forms
3. **Auto-submit possible** — `<body onload="document.forms[0].submit()">`
4. **No SOP restriction on sending** — SOP only restricts reading responses
5. **Cookies auto-attached** — Based on destination domain
6. **Content-Type allowed** — `application/x-www-form-urlencoded`, `multipart/form-data`, `text/plain`

```html
<!-- Attacker page: auto-submitting hidden form -->
<body onload="document.getElementById('csrf-form').submit()">
  <form id="csrf-form" action="https://bank.com/transfer" method="POST">
    <input type="hidden" name="to" value="attacker-account" />
    <input type="hidden" name="amount" value="10000" />
  </form>
</body>
```

### Why GET Requests Can Be Abused

If a server performs state-changing operations on GET:

```html
<!-- Image tag triggers GET with cookies -->
<img src="https://bank.com/transfer?to=attacker&amount=10000" />

<!-- Link click (top-level navigation, bypasses SameSite=Lax) -->
<a href="https://bank.com/transfer?to=attacker&amount=10000">Click here</a>
```

**Rule:** NEVER perform state-changing operations on GET endpoints.

### Navigation Requests vs Subresource Requests

```
┌─────────────────────────────────────────────────────┐
│              Request Classification                    │
├─────────────────────────────────────────────────────┤
│                                                       │
│  TOP-LEVEL NAVIGATION:                               │
│    - Clicking links                                   │
│    - Form submissions                                │
│    - window.location = "..."                         │
│    - <meta http-equiv="refresh">                     │
│    → SameSite=Lax cookies SENT (GET only)           │
│                                                       │
│  SUBRESOURCE REQUESTS:                               │
│    - <img src="...">                                 │
│    - <script src="...">                              │
│    - <iframe src="...">                              │
│    - fetch() / XMLHttpRequest                        │
│    - CSS @import                                     │
│    → SameSite=Lax cookies BLOCKED                   │
│                                                       │
└─────────────────────────────────────────────────────┘
```

### Preflight Requests and CSRF

CORS preflight (OPTIONS) is triggered when:
- Method is not GET, HEAD, or POST
- Content-Type is not `application/x-www-form-urlencoded`, `multipart/form-data`, or `text/plain`
- Custom headers are present (e.g., `X-Requested-With`)

**Why custom headers help prevent CSRF:**
- Adding `X-CSRF-Token` or `Content-Type: application/json` triggers preflight
- Preflight asks: "Is cross-origin allowed?"
- If server doesn't respond with proper CORS headers, browser blocks the request
- **The request is never sent** (unlike simple requests)

```
Simple request (NO preflight):         Preflighted request:
  POST + form-urlencoded                 POST + application/json
  → Request IS sent                      → OPTIONS sent first
  → Response may be blocked              → If denied, request NOT sent
  → Side effect ALREADY happened         → No side effect
```

### Browser Engine Differences

| Behavior | Chromium (Blink) | Firefox (Gecko) | Safari (WebKit) |
|----------|-----------------|-----------------|-----------------|
| Default SameSite | Lax | Lax | Lax (since 2021) |
| Lax+POST window | Removed | Never had | Never had |
| Schemeful same-site | Yes (http≠https) | Yes | Yes |
| Partition cookies (CHIPS) | Supported | Supported | ITP (different approach) |
| 3P cookie blocking | Phase-out paused | ETP strict | ITP full block |

---

## 3. CSRF Attack Types Deep Dive

### 3.1 Form-Based CSRF

**The classic attack.** An attacker creates a hidden form that auto-submits to the target.

```html
<!-- Hosted on evil.com -->
<html>
<body onload="document.getElementById('f').submit()">
  <form id="f" method="POST" action="https://bank.com/api/transfer">
    <input type="hidden" name="recipient" value="attacker-acct" />
    <input type="hidden" name="amount" value="50000" />
    <input type="hidden" name="currency" value="USD" />
  </form>
</body>
</html>
```

**Why it works:**
- Form submission is a "simple request" — no preflight
- Browser attaches bank.com cookies automatically
- SOP doesn't prevent sending, only reading response
- No JavaScript required (works even with JS disabled)

**Mitigation:** CSRF tokens, SameSite=Lax/Strict, Origin validation

### 3.2 Image-Based CSRF (GET)

```html
<!-- Triggers GET request with cookies -->
<img src="https://target.com/api/delete-account?confirm=yes" width="0" height="0" />
```

**Only works if:** Server performs state changes on GET (a vulnerability itself).

### 3.3 Login CSRF

**Forces victim to log in with attacker's credentials:**

```html
<form action="https://target.com/login" method="POST">
  <input type="hidden" name="email" value="attacker@evil.com" />
  <input type="hidden" name="password" value="attacker-password" />
</form>
<script>document.forms[0].submit();</script>
```

**Why it's dangerous:**
- Victim is now logged in as attacker
- Victim enters sensitive data (credit cards, addresses) into attacker's account
- Attacker later logs in and retrieves the data
- Common in OAuth flows without `state` parameter

### 3.4 JSON CSRF

**Targeting APIs that accept JSON:**

```html
<!-- Method 1: Using text/plain content type (no preflight) -->
<form action="https://api.target.com/transfer" method="POST" 
      enctype="text/plain">
  <input name='{"to":"attacker","amount":"10000","ignore":"' value='"}' />
</form>
```

This sends: `{"to":"attacker","amount":"10000","ignore":"="}` as `text/plain`.

**Works when:**
- Server parses body regardless of Content-Type
- Server doesn't validate Content-Type header
- No CSRF token required

**Doesn't work when:**
- Server requires `Content-Type: application/json` (triggers preflight)
- Server validates Content-Type strictly
- CORS not configured to allow cross-origin

### 3.5 GraphQL CSRF

```html
<!-- GraphQL often accepts GET with query parameter -->
<img src='https://api.target.com/graphql?query=mutation{transferFunds(to:"attacker",amount:10000){id}}' />

<!-- Or POST with application/x-www-form-urlencoded -->
<form action="https://api.target.com/graphql" method="POST">
  <input name="query" value='mutation { deleteAccount(id: "victim") { success } }' />
</form>
```

**GraphQL-specific risks:**
- Many GraphQL servers accept both GET and POST
- Some accept `application/x-www-form-urlencoded` (no preflight)
- Introspection may reveal mutation names
- Batched mutations increase blast radius

### 3.6 OAuth CSRF

```
Attack flow:
1. Attacker initiates OAuth login → gets authorization code
2. Attacker does NOT complete the flow (doesn't exchange code)
3. Attacker tricks victim into visiting callback URL:
   https://target.com/auth/callback?code=ATTACKER_CODE
4. Target exchanges code → links attacker's external account to victim
5. Attacker now has access via OAuth provider
```

**Mitigation:** OAuth `state` parameter (cryptographic nonce bound to user session), PKCE.

### 3.7 iframe-Based CSRF

```html
<!-- Hidden iframe loads target page, then submits form -->
<iframe name="csrf-frame" style="display:none"></iframe>
<form action="https://target.com/settings" method="POST" target="csrf-frame">
  <input type="hidden" name="email" value="attacker@evil.com" />
</form>
<script>document.forms[0].submit();</script>
```

**Why iframe variant is stealthy:**
- Form submission in iframe doesn't navigate the parent page
- User sees no visible change
- Multiple iframes = multiple CSRF requests in parallel

### 3.8 Client-Side CSRF

When client-side JavaScript reads attacker-controlled input and uses it to make requests:

```javascript
// Vulnerable: reads URL parameter and uses it as API endpoint
const endpoint = new URLSearchParams(location.search).get("api");
fetch(endpoint, { method: "POST", credentials: "include", body: data });
```

**Attack:** `https://target.com/app?api=https://target.com/admin/delete-user`

### 3.9 Mobile WebView CSRF

- WebViews often share cookie jars with the browser
- Custom URL schemes can trigger cross-app CSRF
- Deep links may bypass SameSite (not a "site" concept in native)
- Embedded browsers may not enforce SameSite consistently

---

## 4. CSRF Defense Mechanisms Deep Dive

### 4.1 Synchronizer Token Pattern

**The gold standard for server-rendered applications.**

```
┌──────────────────────────────────────────────────────────┐
│           Synchronizer Token Pattern                       │
├──────────────────────────────────────────────────────────┤
│                                                            │
│  1. Server generates random token per session              │
│  2. Token stored in server-side session                    │
│  3. Token embedded in form as hidden field                 │
│  4. On submission, server compares form token to session   │
│  5. Mismatch → reject request                             │
│                                                            │
│  WHY IT WORKS:                                            │
│  - Attacker cannot READ the token (SOP blocks response)   │
│  - Attacker cannot GUESS the token (cryptographic random) │
│  - Token proves request originated from legitimate page    │
│                                                            │
└──────────────────────────────────────────────────────────┘
```

```typescript
// Express middleware example
import crypto from "crypto";

// Generate token
function generateCsrfToken(session: Session): string {
  const token = crypto.randomBytes(32).toString("hex");
  session.csrfToken = token;
  return token;
}

// Validate token
function validateCsrfToken(req: Request, session: Session): boolean {
  const token = req.body._csrf || req.headers["x-csrf-token"];
  return token && crypto.timingSafeEqual(
    Buffer.from(token),
    Buffer.from(session.csrfToken)
  );
}
```

### 4.2 Double-Submit Cookie Pattern

**Stateless alternative — no server-side storage needed.**

```
┌──────────────────────────────────────────────────────────┐
│           Double-Submit Cookie Pattern                      │
├──────────────────────────────────────────────────────────┤
│                                                            │
│  1. Server sets CSRF token as a cookie                     │
│  2. Client reads cookie value via JavaScript               │
│  3. Client includes token in request header/body           │
│  4. Server compares cookie value to header/body value      │
│  5. Mismatch → reject                                     │
│                                                            │
│  WHY IT WORKS:                                            │
│  - Attacker can cause browser to SEND the cookie           │
│  - But attacker cannot READ the cookie (SOP)              │
│  - So attacker cannot include matching value in body       │
│                                                            │
│  WEAKNESS:                                                │
│  - Subdomain attacks: subdomain can set parent cookies    │
│  - Must use __Host- prefix to prevent this                │
│                                                            │
└──────────────────────────────────────────────────────────┘
```

```typescript
// Server sets cookie
res.cookie("__Host-csrf", token, {
  httpOnly: false, // Must be readable by JS
  secure: true,
  sameSite: "Lax",
  path: "/",
});

// Client reads and sends
const csrfToken = document.cookie
  .split("; ")
  .find(row => row.startsWith("__Host-csrf="))
  ?.split("=")[1];

fetch("/api/action", {
  method: "POST",
  headers: { "X-CSRF-Token": csrfToken },
  credentials: "same-origin",
});
```

### 4.3 SameSite Cookies

**Browser-level defense — the most impactful modern protection.**

```typescript
// Setting secure session cookie
res.cookie("session", sessionId, {
  httpOnly: true,
  secure: true,
  sameSite: "Lax",   // or "Strict" for maximum protection
  path: "/",
  maxAge: 3600000,
  domain: undefined, // Don't set domain — more restrictive
});
```

| Strategy | Use Case | Trade-off |
|----------|----------|-----------|
| `Strict` | Banking, admin panels | Breaks inbound links (user appears logged out) |
| `Lax` | Most applications | Protects POST but allows GET navigation |
| `Lax` + CSRF token | High-security with good UX | Belt-and-suspenders approach |
| Dual cookies | `Strict` for writes, `Lax` for reads | Complex but optimal UX+security |

**Dual cookie pattern:**
```typescript
// Strict cookie for mutation authentication
res.cookie("__Host-session-strict", token, { sameSite: "Strict", ... });
// Lax cookie for read-only authentication  
res.cookie("__Host-session-lax", token, { sameSite: "Lax", ... });

// Server logic:
// GET requests: accept Lax cookie (user stays logged in via links)
// POST/PUT/DELETE: require Strict cookie (blocks cross-site)
```

### 4.4 Origin Header Validation

```typescript
function validateOrigin(req: Request): boolean {
  const origin = req.headers["origin"];
  const referer = req.headers["referer"];
  
  // Origin is most reliable (sent on POST, PUT, DELETE, PATCH)
  if (origin) {
    return ALLOWED_ORIGINS.includes(origin);
  }
  
  // Fallback to Referer (may be stripped by Referrer-Policy)
  if (referer) {
    const refererOrigin = new URL(referer).origin;
    return ALLOWED_ORIGINS.includes(refererOrigin);
  }
  
  // No Origin AND no Referer — reject (defense-in-depth)
  // Some legitimate cases: bookmarks, typed URLs
  // Handle based on your risk tolerance
  return false;
}
```

**Why Origin validation helps:**
- Browsers always send `Origin` header on cross-origin POST/PUT/DELETE
- Cannot be spoofed by JavaScript (browser-controlled)
- Simple to implement as middleware

**Why it's imperfect:**
- `Origin` may be `null` in some edge cases (redirects, privacy modes, file:// origins)
- `Referer` can be stripped by `Referrer-Policy: no-referrer`
- Should be used as defense-in-depth, not sole protection

### 4.5 Custom Request Headers

```typescript
// Client: Always send custom header
fetch("/api/action", {
  method: "POST",
  headers: {
    "Content-Type": "application/json",
    "X-Requested-With": "XMLHttpRequest", // triggers preflight
  },
  credentials: "same-origin",
});
```

**Why custom headers prevent CSRF:**
1. Adding ANY custom header triggers CORS preflight
2. Preflight sends OPTIONS request to server
3. If server doesn't respond with `Access-Control-Allow-Headers: X-Requested-With`
4. Browser blocks the actual request entirely
5. **The request with side effects is never sent**

**Important:** This only works for XHR/fetch requests. Forms cannot set custom headers.

### 4.6 Defense Comparison

| Defense | Stateless? | Browser support | Subdomain-safe? | Effort |
|---------|-----------|-----------------|-----------------|--------|
| Synchronizer token | No | Universal | Yes | Medium |
| Double-submit cookie | Yes | Universal | Need `__Host-` prefix | Medium |
| SameSite=Lax | Yes | Modern | Yes (scheme-aware) | Low |
| SameSite=Strict | Yes | Modern | Yes | Low (UX cost) |
| Origin validation | Yes | Modern | Yes | Low |
| Custom headers | Yes | Universal | Yes | Low |
| CORS properly configured | — | Modern | Yes | Medium |

### 4.7 Defense-in-Depth Strategy

**Recommended layered approach:**

```
Layer 1: SameSite=Lax on all cookies (browser enforcement)
Layer 2: Origin/Referer validation middleware
Layer 3: CSRF tokens for state-changing operations
Layer 4: Custom headers (Content-Type: application/json)
Layer 5: Strict CORS configuration
Layer 6: Re-authentication for critical actions
```

### Why JWT Apps Are NOT Automatically Safe

**Common misconception:** "We use JWTs, so we're immune to CSRF."

**Reality:**
- If JWT is stored in a cookie → **vulnerable to CSRF** (browser auto-attaches cookie)
- If JWT is in localStorage + Authorization header → **not vulnerable to CSRF** (but vulnerable to XSS)
- If JWT is in httpOnly cookie + sent via header → **safe** but needs mechanism to read token

```
JWT Storage      | CSRF Risk | XSS Risk | Recommendation
─────────────────┼───────────┼──────────┼──────────────────
localStorage     | None      | HIGH     | Avoid for auth
httpOnly cookie  | HIGH      | Low      | Add CSRF protection
Memory (var)     | None      | Medium   | Short-lived only
httpOnly + header| None      | Low      | Best (complex setup)
```

---

## 5. Cookies, Sessions & Authentication Architecture

### Cookie Security Attributes

```typescript
// Maximum security cookie configuration
res.cookie("__Host-session", value, {
  httpOnly: true,     // Not accessible to JavaScript
  secure: true,       // HTTPS only
  sameSite: "Lax",   // Cross-site protection
  path: "/",         // Available to entire site
  maxAge: 3600000,   // 1 hour
  // domain: NOT SET  // __Host- prefix requires no domain
});
```

| Attribute | Purpose | CSRF Impact |
|-----------|---------|-------------|
| `HttpOnly` | Blocks JS access | Prevents XSS from reading token (indirect CSRF help) |
| `Secure` | HTTPS only | Prevents MITM cookie theft |
| `SameSite` | Cross-site control | **Primary browser-level CSRF defense** |
| `__Host-` prefix | Requires Secure + no Domain + path=/ | Prevents subdomain cookie injection |
| `__Secure-` prefix | Requires Secure flag | Minimum transport security |

### Session Cookie vs JWT Cookie

```
┌──────────────────────────────────────────────────────────┐
│  Session Cookie Auth          │  JWT Cookie Auth          │
├───────────────────────────────┼───────────────────────────┤
│  Cookie: session=abc123       │  Cookie: token=eyJhbG...  │
│  Server looks up session      │  Server verifies JWT sig  │
│  Server has revocation        │  No built-in revocation   │
│  Stateful (session store)     │  Stateless                │
│  CSRF: vulnerable             │  CSRF: vulnerable         │
│  Both need SameSite/tokens    │  Both need SameSite/tokens│
└───────────────────────────────┴───────────────────────────┘

KEY INSIGHT: The storage mechanism (cookie) creates CSRF risk,
not the token format. Both session IDs and JWTs in cookies are 
equally vulnerable to CSRF.
```

### Authentication Architecture Comparison

| Architecture | CSRF Risk | XSS Risk | Complexity | Best For |
|-------------|-----------|----------|------------|----------|
| Session cookie (httpOnly, SameSite=Lax) | Low (with SameSite) | Low | Low | Traditional apps, SSR |
| JWT in httpOnly cookie | Low (with SameSite) | Low | Medium | Stateless APIs |
| JWT in localStorage + Auth header | None | **HIGH** | Low | Avoid |
| JWT in memory + refresh cookie | None | Medium | High | SPAs needing max security |
| BFF pattern (Backend-for-Frontend) | Low | Low | High | Enterprise SPAs |

### The BFF Pattern (Recommended for SPAs)

```
┌─────────────────────────────────────────────────────────┐
│                    BFF Pattern                            │
├─────────────────────────────────────────────────────────┤
│                                                           │
│  Browser                                                 │
│    │  (httpOnly session cookie, SameSite=Strict)        │
│    ▼                                                     │
│  BFF (same-origin Node.js server)                       │
│    │  (Authorization: Bearer <token>)                   │
│    ▼                                                     │
│  API Server                                              │
│                                                           │
│  Benefits:                                               │
│  - No tokens exposed to JavaScript                      │
│  - Session cookie is httpOnly + SameSite                │
│  - BFF handles token refresh                            │
│  - CSRF protection via SameSite + tokens                │
│  - API server only accepts bearer tokens (no cookies)   │
│                                                           │
└─────────────────────────────────────────────────────────┘
```

### Refresh Token Architecture

```typescript
// Secure refresh pattern
// 1. Access token: short-lived, in memory (not cookie)
// 2. Refresh token: long-lived, httpOnly cookie, SameSite=Strict

// Login response
res.cookie("__Host-refresh", refreshToken, {
  httpOnly: true,
  secure: true,
  sameSite: "Strict",
  path: "/api/auth/refresh", // Only sent to refresh endpoint
  maxAge: 7 * 24 * 60 * 60 * 1000, // 7 days
});

// Client stores access token in memory
let accessToken = response.data.accessToken; // 15-min expiry

// Refresh endpoint
app.post("/api/auth/refresh", csrfProtection, (req, res) => {
  const refreshToken = req.cookies["__Host-refresh"];
  // Validate, rotate, issue new tokens
});
```

### Session Fixation Prevention

```typescript
// After successful authentication, ALWAYS regenerate session
app.post("/login", async (req, res) => {
  const user = await authenticate(req.body);
  
  // Destroy old session and create new one
  req.session.regenerate((err) => {
    req.session.userId = user.id;
    req.session.csrfToken = crypto.randomBytes(32).toString("hex");
    res.redirect("/dashboard");
  });
});
```

---

## 6. React / Next.js / Astro CSRF Deep Dive

### React SPA CSRF Patterns

**Problem:** React SPAs typically use `fetch()` to call APIs. If authentication uses cookies, CSRF is still a risk.

```typescript
// ❌ VULNERABLE: Cookie-based auth without CSRF protection
fetch("/api/transfer", {
  method: "POST",
  credentials: "same-origin", // sends cookies
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({ to: "recipient", amount: 1000 }),
});

// ✅ SAFE: With CSRF token in header
function useCsrfFetch() {
  const csrfToken = useCsrfToken(); // Read from meta tag or cookie
  
  return (url: string, options: RequestInit = {}) => {
    return fetch(url, {
      ...options,
      credentials: "same-origin",
      headers: {
        ...options.headers,
        "Content-Type": "application/json",
        "X-CSRF-Token": csrfToken,
      },
    });
  };
}
```

**CSRF Token Delivery for SPAs:**

```typescript
// Option 1: Meta tag (set by server on page load)
// In SSR HTML: <meta name="csrf-token" content="{{token}}" />
const token = document.querySelector('meta[name="csrf-token"]')?.content;

// Option 2: Cookie (double-submit pattern)
// Server sets: Set-Cookie: __Host-csrf=token123; Path=/; Secure
const token = getCookie("__Host-csrf");

// Option 3: Dedicated endpoint (for pure SPAs)
const { data } = await fetch("/api/auth/csrf-token", { credentials: "same-origin" });
```

### Next.js CSRF Protection

#### App Router (Server Actions)

```typescript
// Next.js Server Actions have built-in CSRF protection
// They require the Origin header to match, and use POST + custom headers

// app/actions.ts
"use server";

import { cookies } from "next/headers";

export async function transferFunds(formData: FormData) {
  // Server Actions automatically validate:
  // 1. Origin header matches
  // 2. Request uses POST
  // 3. Content-Type is multipart/form-data or application/x-www-form-urlencoded
  
  const session = cookies().get("session");
  // ... process action
}
```

#### API Routes Protection

```typescript
// app/api/transfer/route.ts
import { NextRequest, NextResponse } from "next/server";

export async function POST(req: NextRequest) {
  // Validate Origin
  const origin = req.headers.get("origin");
  if (origin !== process.env.ALLOWED_ORIGIN) {
    return NextResponse.json({ error: "Forbidden" }, { status: 403 });
  }
  
  // Validate CSRF token (double-submit)
  const cookieToken = req.cookies.get("__Host-csrf")?.value;
  const headerToken = req.headers.get("x-csrf-token");
  
  if (!cookieToken || !headerToken || cookieToken !== headerToken) {
    return NextResponse.json({ error: "Invalid CSRF token" }, { status: 403 });
  }
  
  // Process request...
}
```

#### Middleware CSRF Validation

```typescript
// middleware.ts
import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";

const SAFE_METHODS = ["GET", "HEAD", "OPTIONS"];

export function middleware(req: NextRequest) {
  if (SAFE_METHODS.includes(req.method)) {
    return NextResponse.next();
  }
  
  // Validate Origin for all state-changing requests
  const origin = req.headers.get("origin");
  const host = req.headers.get("host");
  
  if (!origin || new URL(origin).host !== host) {
    return NextResponse.json(
      { error: "CSRF validation failed" },
      { status: 403 }
    );
  }
  
  return NextResponse.next();
}

export const config = {
  matcher: "/api/:path*",
};
```

### Astro CSRF Protection

```typescript
// src/pages/api/action.ts (Astro API route)
import type { APIRoute } from "astro";

export const POST: APIRoute = async ({ request, cookies }) => {
  // Validate Origin
  const origin = request.headers.get("origin");
  const url = new URL(request.url);
  
  if (origin !== url.origin) {
    return new Response("CSRF rejected", { status: 403 });
  }
  
  // Double-submit validation
  const csrfCookie = cookies.get("__Host-csrf")?.value;
  const csrfHeader = request.headers.get("x-csrf-token");
  
  if (!csrfCookie || csrfCookie !== csrfHeader) {
    return new Response("Invalid CSRF token", { status: 403 });
  }
  
  // Process...
  return new Response(JSON.stringify({ success: true }), { status: 200 });
};
```

```astro
---
// src/pages/form.astro — Server-rendered form with CSRF token
import crypto from "crypto";

const csrfToken = crypto.randomBytes(32).toString("hex");
Astro.cookies.set("__Host-csrf", csrfToken, {
  httpOnly: false,
  secure: true,
  sameSite: "strict",
  path: "/",
});
---

<form method="POST" action="/api/action">
  <input type="hidden" name="_csrf" value={csrfToken} />
  <button type="submit">Submit</button>
</form>
```

### Why SPAs Still Face CSRF

**Misconception:** "SPAs use JSON APIs with fetch, so CSRF isn't possible."

**Reality:**
1. If using `credentials: "include"` or `"same-origin"` → cookies are sent
2. If API accepts `Content-Type: text/plain` → no preflight (exploit possible)
3. If API accepts form-encoded data → classic form CSRF works
4. If GET endpoints have side effects → image/link-based CSRF works
5. Even with JSON + custom headers → ensure CORS is strict

**SPA is safe from CSRF only when ALL of:**
- Authentication uses Authorization header (not cookies)
- OR SameSite=Strict/Lax cookies are used
- OR CSRF tokens are validated
- AND API rejects requests without proper Content-Type
- AND CORS is strictly configured

### fetch vs axios Defaults

| Behavior | fetch() | axios |
|----------|---------|-------|
| Credentials | `same-origin` (default) | No cookies by default |
| Cross-origin cookies | Must set `credentials: "include"` | Must set `withCredentials: true` |
| Content-Type | None (unless set) | `application/json` (auto) |
| Preflight trigger | Must add custom header manually | Auto (due to Content-Type: application/json) |

```typescript
// axios global config for CSRF
import axios from "axios";

const api = axios.create({
  baseURL: "/api",
  withCredentials: true,
  headers: {
    "X-Requested-With": "XMLHttpRequest",
  },
});

// Read CSRF token from cookie and attach to every request
api.interceptors.request.use((config) => {
  const token = getCookie("__Host-csrf");
  if (token) {
    config.headers["X-CSRF-Token"] = token;
  }
  return config;
});
```

---

## 7. CORS, SOP & CSRF Relationship

### Why CORS Does NOT Stop CSRF

```
┌──────────────────────────────────────────────────────────────┐
│         Common Misconception vs Reality                        │
├──────────────────────────────────────────────────────────────┤
│                                                                │
│  MISCONCEPTION:                                               │
│  "CORS blocks cross-origin requests, so CSRF is prevented"   │
│                                                                │
│  REALITY:                                                     │
│  CORS controls whether the RESPONSE is readable              │
│  The REQUEST is still SENT (for simple requests)             │
│  Side effects happen BEFORE the response is checked          │
│                                                                │
│  ┌─────────┐    POST /transfer     ┌──────────┐             │
│  │ evil.com │ ──────────────────► │ bank.com  │             │
│  │          │    (cookies sent!)   │           │             │
│  │          │ ◄────────────────── │ (executed!)│             │
│  │          │    Response blocked  │           │             │
│  └─────────┘    by CORS           └──────────┘             │
│                                                                │
│  The transfer ALREADY HAPPENED.                              │
│  CORS just prevented evil.com from reading the response.     │
│                                                                │
└──────────────────────────────────────────────────────────────┘
```

**CORS DOES help when:**
- Request requires preflight (custom headers, non-simple Content-Type)
- Preflight is denied → actual request never sent
- This is why `Content-Type: application/json` provides partial protection

### Same-Origin vs Same-Site

```
https://app.example.com:443/path

Origin: https://app.example.com:443
Site:   https://example.com (eTLD+1)

┌────────────────────────────────────────────────────────────┐
│  URL A                      │ URL B                │ Same? │
├─────────────────────────────┼──────────────────────┼───────┤
│ https://a.example.com       │ https://b.example.com│       │
│   Same-origin?              │                      │  NO   │
│   Same-site?                │                      │  YES  │
├─────────────────────────────┼──────────────────────┼───────┤
│ https://example.com         │ http://example.com   │       │
│   Same-origin?              │                      │  NO   │
│   Same-site?                │                      │  NO*  │
│   * Schemeful same-site     │                      │       │
├─────────────────────────────┼──────────────────────┼───────┤
│ https://example.com:443     │ https://example.com  │       │
│   Same-origin?              │                      │  YES  │
│   Same-site?                │                      │  YES  │
└─────────────────────────────┴──────────────────────┴───────┘
```

### Why Custom Headers Help

```
Standard form submission (NO preflight):
  POST /api/transfer HTTP/1.1
  Content-Type: application/x-www-form-urlencoded
  Cookie: session=abc123
  
  → Request SENT → Side effect happens → CORS blocks response (too late)

Request with custom header (PREFLIGHT required):
  OPTIONS /api/transfer HTTP/1.1
  Access-Control-Request-Headers: X-CSRF-Token
  
  Server responds: "I don't allow X-CSRF-Token from your origin"
  → Actual request NEVER SENT → No side effect
```

---

## 8. Secure Architecture & Enterprise CSRF Strategy

### Enterprise CSRF Defense Architecture

```
┌──────────────────────────────────────────────────────────────┐
│              Enterprise Defense Layers                         │
├──────────────────────────────────────────────────────────────┤
│                                                                │
│  CDN/Edge Layer                                               │
│    └─ Rate limiting, bot detection                           │
│                                                                │
│  API Gateway                                                  │
│    └─ Origin validation                                      │
│    └─ CORS enforcement                                       │
│    └─ Request classification                                 │
│                                                                │
│  Application Layer                                            │
│    └─ CSRF token validation                                  │
│    └─ Session management                                     │
│    └─ Re-authentication for critical ops                     │
│                                                                │
│  Cookie Policy                                                │
│    └─ SameSite=Lax (default)                                │
│    └─ SameSite=Strict (admin/financial)                      │
│    └─ __Host- prefix (all session cookies)                   │
│    └─ Secure + HttpOnly                                      │
│                                                                │
│  Monitoring                                                   │
│    └─ CSRF failure alerting                                  │
│    └─ Origin anomaly detection                               │
│    └─ Session usage patterns                                 │
│                                                                │
└──────────────────────────────────────────────────────────────┘
```

### CSRF Review Checklist

```markdown
## Pre-deployment CSRF Checklist

### Cookies
- [ ] All session cookies have SameSite=Lax minimum
- [ ] Admin/sensitive cookies use SameSite=Strict
- [ ] All cookies use Secure flag
- [ ] Session cookies use HttpOnly
- [ ] Using __Host- prefix for critical cookies
- [ ] No overly broad Domain attribute

### Endpoints
- [ ] All state-changing operations use POST/PUT/DELETE (never GET)
- [ ] Origin header validated on state-changing requests
- [ ] CSRF tokens required for form submissions
- [ ] APIs require Content-Type: application/json (triggers preflight)
- [ ] Custom header required (X-Requested-With or similar)

### CORS
- [ ] Access-Control-Allow-Origin is NOT wildcard with credentials
- [ ] Allowed origins are explicitly listed
- [ ] Access-Control-Allow-Credentials only when needed
- [ ] No origin reflection (don't echo back Origin header)

### Authentication
- [ ] Session regeneration after login
- [ ] Re-authentication for critical actions (password change, etc.)
- [ ] Token rotation on privilege changes
- [ ] Proper logout (server-side session destruction)

### Framework
- [ ] CSRF middleware enabled and configured
- [ ] Token validation on all non-GET routes
- [ ] SPA receives CSRF token securely
- [ ] GraphQL mutations protected
```

### Multi-Tenant SaaS Architecture

```typescript
// Multi-tenant CSRF considerations
// Each tenant may have custom domains: tenant1.app.com, tenant2.app.com

// Problem: SameSite considers all subdomains as same-site
// Solution: Use __Host- prefix (no Domain attribute = exact host match)

// Middleware for multi-tenant CSRF
function multiTenantCsrf(req: Request, res: Response, next: NextFunction) {
  const tenantId = extractTenantFromHost(req.headers.host);
  const sessionTenant = req.session.tenantId;
  
  // Ensure request targets same tenant as session
  if (tenantId !== sessionTenant) {
    return res.status(403).json({ error: "Cross-tenant request rejected" });
  }
  
  // Standard CSRF validation
  validateCsrfToken(req, res, next);
}
```

### Microfrontend CSRF Strategy

```
┌──────────────────────────────────────────────────────────┐
│           Microfrontend CSRF Architecture                  │
├──────────────────────────────────────────────────────────┤
│                                                            │
│  Shell App (app.example.com)                              │
│    ├─ MFE-A (app.example.com/feature-a)                  │
│    ├─ MFE-B (app.example.com/feature-b)                  │
│    └─ Shared Auth Module                                  │
│                                                            │
│  Strategy:                                                │
│  1. Single session cookie at shell level                  │
│  2. Shared CSRF token service                            │
│  3. Each MFE reads token from shared cookie              │
│  4. Central API gateway validates                        │
│                                                            │
│  If different origins (mfe-a.example.com):               │
│  - BFF pattern per MFE                                   │
│  - Or shared auth service with token exchange            │
│                                                            │
└──────────────────────────────────────────────────────────┘
```

---

## 9. OAuth / OIDC / SSO CSRF Deep Dive

### OAuth State Parameter

The `state` parameter is OAuth's CSRF protection:

```
┌──────────────────────────────────────────────────────────┐
│           OAuth CSRF Attack (without state)                │
├──────────────────────────────────────────────────────────┤
│                                                            │
│  1. Attacker starts OAuth flow → gets code                │
│  2. Attacker captures callback URL:                       │
│     https://app.com/callback?code=ATTACKER_CODE           │
│  3. Tricks victim into visiting that URL                  │
│  4. App exchanges code → gets attacker's tokens           │
│  5. App links attacker's account to victim's session      │
│  6. Attacker now accesses victim's data via linked acct   │
│                                                            │
├──────────────────────────────────────────────────────────┤
│           OAuth with state (CSRF protected)               │
│                                                            │
│  1. App generates random state, stores in session         │
│  2. Auth URL includes: &state=random123                  │
│  3. Provider redirects back: ?code=xxx&state=random123   │
│  4. App verifies state matches session                    │
│  5. Attacker's callback has different state → rejected    │
│                                                            │
└──────────────────────────────────────────────────────────┘
```

```typescript
// Secure OAuth implementation
import crypto from "crypto";

// Step 1: Generate and store state
app.get("/auth/login", (req, res) => {
  const state = crypto.randomBytes(32).toString("hex");
  const codeVerifier = crypto.randomBytes(32).toString("base64url"); // PKCE
  const codeChallenge = crypto
    .createHash("sha256")
    .update(codeVerifier)
    .digest("base64url");
  
  req.session.oauthState = state;
  req.session.codeVerifier = codeVerifier;
  
  const authUrl = new URL("https://provider.com/authorize");
  authUrl.searchParams.set("client_id", CLIENT_ID);
  authUrl.searchParams.set("redirect_uri", REDIRECT_URI);
  authUrl.searchParams.set("state", state);
  authUrl.searchParams.set("code_challenge", codeChallenge);
  authUrl.searchParams.set("code_challenge_method", "S256");
  authUrl.searchParams.set("response_type", "code");
  
  res.redirect(authUrl.toString());
});

// Step 2: Validate state on callback
app.get("/auth/callback", (req, res) => {
  const { code, state } = req.query;
  
  // CSRF check: validate state
  if (!state || state !== req.session.oauthState) {
    return res.status(403).send("OAuth state mismatch — possible CSRF");
  }
  
  // Clear state (one-time use)
  delete req.session.oauthState;
  
  // Exchange code with PKCE verifier
  const tokens = await exchangeCode(code, req.session.codeVerifier);
  delete req.session.codeVerifier;
  
  // Continue authentication...
});
```

### Login CSRF

**Often overlooked but dangerous:**

```
Attack scenario:
1. Attacker crafts form that logs victim into attacker's account
2. Victim unknowingly operates as attacker
3. Victim adds payment method, enters sensitive data
4. Attacker logs back in → accesses victim's data

Defense:
- CSRF protection on login endpoint
- Session regeneration after login
- Display account identity prominently
- SameSite=Lax blocks cross-site POST (login forms)
```

### SPA OAuth Strategy

```typescript
// Recommended: Authorization Code + PKCE (no client secret)
// For SPAs that can't securely store client_secret

// 1. Generate PKCE values client-side
function generatePKCE() {
  const verifier = crypto.randomUUID() + crypto.randomUUID();
  const challenge = await sha256Base64Url(verifier);
  
  // Store verifier in sessionStorage (survives redirect)
  sessionStorage.setItem("pkce_verifier", verifier);
  
  // Generate state for CSRF
  const state = crypto.randomUUID();
  sessionStorage.setItem("oauth_state", state);
  
  return { challenge, state };
}

// 2. On callback, validate state
function handleCallback() {
  const params = new URLSearchParams(location.search);
  const state = params.get("state");
  const storedState = sessionStorage.getItem("oauth_state");
  
  if (state !== storedState) {
    throw new Error("CSRF detected: state mismatch");
  }
  
  sessionStorage.removeItem("oauth_state");
  // Exchange code...
}
```

---

## 10. Setup Guide

### Complete CSRF Protection Setup

#### Step 1: Cookie Configuration

```typescript
// Express/NestJS session setup
import session from "express-session";

app.use(session({
  name: "__Host-session",
  secret: process.env.SESSION_SECRET,
  resave: false,
  saveUninitialized: false,
  cookie: {
    httpOnly: true,
    secure: true, // production: always true
    sameSite: "lax",
    maxAge: 60 * 60 * 1000, // 1 hour
    path: "/",
  },
}));
```

#### Step 2: CSRF Middleware (Express)

```typescript
// csrf-middleware.ts
import crypto from "crypto";
import { Request, Response, NextFunction } from "express";

const SAFE_METHODS = new Set(["GET", "HEAD", "OPTIONS"]);

export function csrfProtection(req: Request, res: Response, next: NextFunction) {
  // Skip safe methods
  if (SAFE_METHODS.has(req.method)) {
    return next();
  }
  
  // Layer 1: Origin validation
  const origin = req.headers.origin;
  const expectedOrigin = `${req.protocol}://${req.headers.host}`;
  
  if (origin && origin !== expectedOrigin) {
    return res.status(403).json({ error: "Origin mismatch" });
  }
  
  // Layer 2: CSRF token validation (double-submit)
  const cookieToken = req.cookies["__Host-csrf"];
  const headerToken = req.headers["x-csrf-token"] as string;
  
  if (!cookieToken || !headerToken) {
    return res.status(403).json({ error: "Missing CSRF token" });
  }
  
  if (!crypto.timingSafeEqual(
    Buffer.from(cookieToken),
    Buffer.from(headerToken)
  )) {
    return res.status(403).json({ error: "CSRF token mismatch" });
  }
  
  next();
}

// Token generation endpoint
export function csrfTokenEndpoint(req: Request, res: Response) {
  const token = crypto.randomBytes(32).toString("hex");
  
  res.cookie("__Host-csrf", token, {
    httpOnly: false, // JS must read it
    secure: true,
    sameSite: "strict",
    path: "/",
    maxAge: 60 * 60 * 1000,
  });
  
  res.json({ csrfToken: token });
}
```

#### Step 3: NestJS Guard

```typescript
// csrf.guard.ts
import { CanActivate, ExecutionContext, Injectable, ForbiddenException } from "@nestjs/common";
import crypto from "crypto";

@Injectable()
export class CsrfGuard implements CanActivate {
  canActivate(context: ExecutionContext): boolean {
    const req = context.switchToHttp().getRequest();
    
    if (["GET", "HEAD", "OPTIONS"].includes(req.method)) {
      return true;
    }
    
    const origin = req.headers.origin;
    const host = req.headers.host;
    
    if (origin && new URL(origin).host !== host) {
      throw new ForbiddenException("CSRF: Origin mismatch");
    }
    
    const cookieToken = req.cookies?.["__Host-csrf"];
    const headerToken = req.headers["x-csrf-token"];
    
    if (!cookieToken || !headerToken) {
      throw new ForbiddenException("CSRF: Missing token");
    }
    
    try {
      if (!crypto.timingSafeEqual(Buffer.from(cookieToken), Buffer.from(headerToken))) {
        throw new ForbiddenException("CSRF: Token mismatch");
      }
    } catch {
      throw new ForbiddenException("CSRF: Validation failed");
    }
    
    return true;
  }
}
```

#### Step 4: React API Client Setup

```typescript
// api-client.ts
import axios from "axios";

const api = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL || "/api",
  withCredentials: true,
  headers: {
    "Content-Type": "application/json",
    "X-Requested-With": "XMLHttpRequest",
  },
});

// Attach CSRF token from cookie
api.interceptors.request.use((config) => {
  if (!["get", "head", "options"].includes(config.method || "")) {
    const csrfToken = document.cookie
      .split("; ")
      .find((row) => row.startsWith("__Host-csrf="))
      ?.split("=")[1];
    
    if (csrfToken) {
      config.headers["X-CSRF-Token"] = csrfToken;
    }
  }
  return config;
});

// Handle 403 — refresh CSRF token and retry
api.interceptors.response.use(
  (res) => res,
  async (error) => {
    if (error.response?.status === 403 && !error.config._retry) {
      error.config._retry = true;
      await api.get("/auth/csrf-token"); // Refreshes cookie
      return api(error.config);
    }
    return Promise.reject(error);
  }
);

export default api;
```

#### Step 5: Next.js Complete Setup

```typescript
// lib/csrf.ts
import { cookies } from "next/headers";
import crypto from "crypto";

export function generateCsrfToken(): string {
  return crypto.randomBytes(32).toString("hex");
}

export function setCsrfCookie(token: string) {
  cookies().set("__Host-csrf", token, {
    httpOnly: false,
    secure: true,
    sameSite: "strict",
    path: "/",
    maxAge: 3600,
  });
}

export function validateCsrf(request: Request): boolean {
  const cookieStore = cookies();
  const cookieToken = cookieStore.get("__Host-csrf")?.value;
  const headerToken = request.headers.get("x-csrf-token");
  
  if (!cookieToken || !headerToken) return false;
  
  try {
    return crypto.timingSafeEqual(
      Buffer.from(cookieToken),
      Buffer.from(headerToken)
    );
  } catch {
    return false;
  }
}
```

#### Step 6: Automated CSRF Testing

```typescript
// tests/csrf.test.ts
import { describe, it, expect } from "vitest";

describe("CSRF Protection", () => {
  it("rejects POST without CSRF token", async () => {
    const res = await fetch("/api/action", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ data: "test" }),
    });
    expect(res.status).toBe(403);
  });
  
  it("rejects POST with mismatched Origin", async () => {
    const res = await fetch("/api/action", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Origin": "https://evil.com",
      },
      body: JSON.stringify({ data: "test" }),
    });
    expect(res.status).toBe(403);
  });
  
  it("accepts POST with valid CSRF token", async () => {
    // Get token
    const tokenRes = await fetch("/api/auth/csrf-token");
    const { csrfToken } = await tokenRes.json();
    
    const res = await fetch("/api/action", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-CSRF-Token": csrfToken,
        "Cookie": `__Host-csrf=${csrfToken}`,
      },
      body: JSON.stringify({ data: "test" }),
    });
    expect(res.status).toBe(200);
  });
  
  it("allows GET without CSRF token", async () => {
    const res = await fetch("/api/data");
    expect(res.status).toBe(200);
  });
});
```

---

## 11. Security Tooling Comparison

| Tool | Purpose | CSRF Relevance | Learning Curve | CI/CD | Enterprise |
|------|---------|---------------|----------------|-------|------------|
| **csurf** (deprecated) | Express CSRF middleware | Direct | Low | ✅ | ❌ (unmaintained) |
| **csrf-csrf** | Modern double-submit CSRF | Direct | Low | ✅ | ✅ |
| **lusitania** | CSRF token library | Direct | Low | ✅ | ✅ |
| **Auth.js / NextAuth** | Authentication framework | Session + OAuth CSRF | Medium | ✅ | ✅ |
| **OWASP ZAP** | DAST scanner | Detects missing CSRF | Medium | ✅ | ✅ |
| **Burp Suite** | Penetration testing | CSRF testing + bypass | High | ❌ | ✅ (Pro) |
| **Semgrep** | SAST (code patterns) | Finds missing protections | Low | ✅ | ✅ |
| **Snyk** | Dependency scanning | Vulnerable auth libraries | Low | ✅ | ✅ |
| **Helmet.js** | Security headers | Indirect (CSP, etc.) | Low | ✅ | ✅ |

### Recommended Stack for React/Next.js/Astro

```
Authentication:  Auth.js (NextAuth) or custom with CSRF middleware
CSRF Library:    csrf-csrf (double-submit) or custom middleware
Headers:         Helmet.js
SAST:            Semgrep rules for CSRF patterns
DAST:            OWASP ZAP in CI pipeline
Dependencies:    Snyk or Dependabot
Manual Testing:  Burp Suite (penetration testing)
```

---

## 12. Cheatsheet

### CSRF Attack Quick Reference

| Vector | Payload | Requires JS? | Bypasses SameSite=Lax? |
|--------|---------|-------------|----------------------|
| Auto-submit form (POST) | `<form action="..." method="POST">` + `onload=submit` | Optional | ❌ |
| Image tag (GET) | `<img src="https://target/action">` | No | ❌ |
| Link click (GET navigation) | `<a href="https://target/action">` | No | ✅ (top-level) |
| fetch + credentials | `fetch(url, {credentials: "include"})` | Yes | ❌ |
| Form to iframe | `<form target="hidden-iframe">` | Optional | ❌ |

### Secure Cookie Template

```
Set-Cookie: __Host-session=<value>;
  Secure;
  HttpOnly;
  SameSite=Lax;
  Path=/;
  Max-Age=3600
```

### Defense Quick Reference

```typescript
// Minimum viable CSRF protection (modern apps)
// 1. Set SameSite=Lax on all auth cookies ✓
// 2. Validate Origin header on POST/PUT/DELETE ✓
// 3. Require Content-Type: application/json (triggers preflight) ✓
// 4. Add CSRF token for form submissions ✓
// 5. Never perform state changes on GET ✓
```

### Common Anti-Patterns

| Anti-Pattern | Why It's Wrong | Fix |
|-------------|---------------|-----|
| CSRF token in URL query param | Leaks via Referer header, logs | Use header or POST body |
| Predictable tokens | Attacker can guess | Use `crypto.randomBytes(32)` |
| Token not bound to session | Token reuse across sessions | Regenerate on auth |
| GET endpoints with side effects | Image/link CSRF bypasses everything | Use POST for mutations |
| `SameSite=None` without reason | Opts out of browser protection | Use Lax minimum |
| Trusting Referer alone | Can be stripped | Use Origin + Referer fallback |
| `Access-Control-Allow-Origin: *` with credentials | Doesn't work (browser rejects), but indicates misconfiguration | Explicit origin list |

### Secure Fetch Patterns

```typescript
// ✅ Safe: JSON API with custom header
fetch("/api/action", {
  method: "POST",
  credentials: "same-origin",
  headers: {
    "Content-Type": "application/json",
    "X-CSRF-Token": getCsrfToken(),
  },
  body: JSON.stringify(data),
});

// ❌ Dangerous: No protection
fetch("/api/action", {
  method: "POST",
  credentials: "include",
  body: formData, // No Content-Type header set = no preflight
});
```

---

## 13. Real-World Engineering Mindset

### Banking/Payment Systems

**Problem:** Financial transactions are the highest-value CSRF target.

**Strategy:**
1. `SameSite=Strict` on session cookies (accept UX trade-off)
2. CSRF tokens (synchronizer pattern — server-side binding)
3. Re-authentication for transactions above threshold
4. Transaction signing (separate confirmation step)
5. Velocity checks and anomaly detection
6. Out-of-band confirmation (SMS/push for high-value)

**What a senior security engineer would choose:**
- Defense-in-depth: SameSite=Strict + synchronizer tokens + re-auth + out-of-band
- Accept the UX cost of Strict (users accessing from links appear logged out)
- Never use double-submit alone (subdomain attacks in financial context)
- Transaction-specific tokens that expire quickly

### Internal Admin Dashboards

**Problem:** Admin panels have highest privilege but often weakest protection.

**Strategy:**
1. `SameSite=Strict` (internal tools can afford UX cost)
2. Separate authentication domain from public-facing app
3. Short session timeouts (15-30 min)
4. IP allowlisting at network layer
5. Audit logging on all state changes
6. MFA on session and critical actions

**Hidden pitfall:** Internal tools often skip CSRF protection because "it's internal" — but compromised employee machines, XSS on any internal page, or phishing links can still exploit this.

### Multi-Region Authentication

**Problem:** Session replication across regions adds latency; CSRF tokens must be globally consistent.

**Strategy:**
1. Stateless tokens (HMAC-based double-submit) — no session store dependency
2. JWT sessions with regional validation
3. CSRF token derived from session: `HMAC(session_id, secret)` — consistent across regions
4. Sticky sessions at CDN level for form-heavy flows

---

## 14. Brainstorm / Open Questions

### Browser Networking (15 questions)
1. Why do browsers attach cookies to requests they didn't originate?
2. How does a browser decide whether a request is "same-site"?
3. What happens to SameSite cookies during a redirect chain?
4. Can a service worker bypass SameSite restrictions?
5. How does browser cookie partitioning (CHIPS) affect CSRF?
6. What is the difference between a "navigation" and a "subresource" request?
7. Why does the browser send cookies on form submissions but not always on fetch?
8. How does the 2-minute Lax+POST exception work in Chrome's cookie model?
9. Can WebSocket connections be used for CSRF attacks?
10. How do browsers handle cookies during HTTP→HTTPS redirects?
11. What role does the `Sec-Fetch-Site` header play in CSRF defense?
12. How would a browser implement SameSite checking internally?
13. What happens to credentials during a cross-origin redirect?
14. How does Private Network Access specification interact with CSRF?
15. Can `<link rel="preload">` trigger CSRF?

### Authentication (15 questions)
16. When should you use cookie-based auth vs bearer tokens?
17. How does session fixation relate to CSRF?
18. What's the CSRF implication of storing refresh tokens in cookies?
19. How should CSRF protection differ between SSR and SPA auth?
20. Can a BFF pattern eliminate CSRF concerns entirely?
21. How does token rotation affect CSRF token validity?
22. Should API keys be sent as cookies or headers?
23. How does OAuth's implicit flow create CSRF risks?
24. What's the CSRF risk of "remember me" functionality?
25. How should passwordless auth (magic links) handle CSRF?
26. Does WebAuthn/passkeys eliminate CSRF?
27. How should CSRF protection work with sliding session windows?
28. What's the security difference between session ID rotation and CSRF token rotation?
29. How does federated authentication (SAML) handle CSRF?
30. Should logout endpoints require CSRF protection?

### Cookies (15 questions)
31. Why is `__Host-` prefix more secure than `__Secure-`?
32. What happens when two cookies have the same name but different paths?
33. How can a subdomain override parent domain cookies?
34. What's the maximum safe cookie size for CSRF tokens?
35. How does cookie order affect CSRF validation?
36. Can cookies be set via HTTP response during a CORS request?
37. What's the security implication of `Domain=.example.com` vs no Domain?
38. How do third-party cookie restrictions affect CSRF?
39. Can cookies be exfiltrated via CSS injection without XSS?
40. What's the difference between persistent and session cookies for CSRF?
41. How does Safari's ITP affect cookie-based CSRF defenses?
42. Can a 302 redirect set cookies that bypass SameSite?
43. What happens to cookies when a browser is in private/incognito mode?
44. How should cookie attributes differ between development and production?
45. Can a CORS preflight response set cookies?

### SameSite (15 questions)
46. Why does SameSite=Lax allow top-level GET navigations?
47. What's the CSRF risk remaining with SameSite=Lax?
48. When is SameSite=Strict absolutely necessary?
49. How does schemeful same-site change the security model?
50. What are the edge cases where SameSite=Lax doesn't protect?
51. How do pop-up windows interact with SameSite?
52. What's the SameSite behavior during OAuth redirects?
53. Can SameSite be bypassed via browser bugs?
54. How does SameSite interact with iframe navigation?
55. What's the difference between "same-site" in SameSite cookies vs Sec-Fetch-Site?
56. How does SameSite work with WebSocket upgrade requests?
57. What happens when SameSite cookies meet server-side redirects?
58. Should SameSite=None ever be used? What are legitimate cases?
59. How does Android WebView handle SameSite?
60. What's the SameSite behavior for `<form method="GET">`?

### OAuth Security (15 questions)
61. Why is the `state` parameter necessary even with SameSite cookies?
62. How does PKCE protect against authorization code interception?
63. What's the CSRF risk in the OAuth implicit flow?
64. Can login CSRF bypass SameSite=Lax?
65. How should a SPA validate OAuth state without server-side sessions?
66. What's the CSRF implication of OAuth token refresh?
67. How does OIDC's `nonce` differ from OAuth's `state`?
68. Can an OAuth provider be used as a CSRF vector against the relying party?
69. What's the security risk of using localStorage for OAuth state?
70. How should OAuth callback endpoints validate the request?
71. Can PKCE replace the `state` parameter for CSRF?
72. What happens if the OAuth state is predictable?
73. How does OpenID Connect's front-channel logout create CSRF risks?
74. What's the CSRF implication of silent token renewal via iframe?
75. How should federated logout handle CSRF across identity providers?

### SSR Authentication (15 questions)
76. How should Next.js middleware handle CSRF for API routes?
77. What's the CSRF implication of Server Actions in Next.js?
78. How does Astro's server-side rendering affect CSRF token delivery?
79. Should SSR apps use synchronizer tokens or double-submit?
80. How does edge rendering (Cloudflare Workers) affect session management?
81. What's the CSRF risk of SSR hydration mismatches?
82. How should streaming SSR handle CSRF tokens?
83. Can React Server Components be CSRF-attacked?
84. How does ISR (Incremental Static Regeneration) interact with CSRF?
85. What's the CSRF risk of Next.js revalidation endpoints?
86. How should CSRF tokens work with partial prerendering?
87. What's the session architecture for hybrid SSR/SPA apps?
88. How does Remix's form handling affect CSRF defense?
89. Should GraphQL queries in SSR be CSRF-protected?
90. How does server-side cookie forwarding affect CSRF in BFF patterns?

### API Security (15 questions)
91. Should REST APIs that only accept JSON need CSRF protection?
92. How does GraphQL's single endpoint affect CSRF defense strategy?
93. What's the CSRF risk of Server-Sent Events (SSE)?
94. How should WebSocket connections handle CSRF during handshake?
95. Should internal APIs behind API gateways need CSRF protection?
96. How does gRPC-web handle CSRF?
97. What's the CSRF risk of file upload endpoints?
98. How should CSRF work with API versioning?
99. Should webhook endpoints have CSRF protection?
100. How does tRPC handle CSRF for mutations?
101. What's the CSRF risk of GraphQL subscriptions?
102. How should batch API endpoints validate CSRF?
103. Should rate limiting interact with CSRF validation?
104. How does API gateway origin validation differ from app-level?
105. What's the CSRF implication of JSONP endpoints?

### Enterprise AppSec (15 questions)
106. How should CSRF governance work in a microservices architecture?
107. What's the organizational responsibility model for CSRF (platform vs product)?
108. How should CSRF incidents be detected and responded to?
109. What CSRF metrics should security teams monitor?
110. How should CSRF protection be tested in CI/CD?
111. What's the migration strategy from no CSRF protection to full protection?
112. How should CSRF exceptions/bypasses be governed?
113. What's the CSRF strategy for third-party integrations?
114. How should CSRF protection evolve with browser API changes?
115. What's the cost-benefit of each CSRF defense layer?
116. How should security reviews evaluate CSRF in new features?
117. What's the CSRF implication of A/B testing infrastructure?
118. How should CSRF protection work across deployment environments?
119. What's the disaster recovery plan for CSRF token infrastructure?
120. How should CSRF findings be prioritized in bug bounty programs?

### Browser Behavior (5 additional questions)
121. How do browser extensions affect CSRF security models?
122. Can Developer Tools bypass SameSite for testing?
123. How does browser prefetching (`<link rel="prefetch">`) interact with CSRF?
124. What's the CSRF implication of browser back/forward cache (bfcache)?
125. How do browsers handle CSRF defense during network errors and retries?

---

## 15. Practice Questions

### Beginner (35 questions)

**Q1.** What does CSRF stand for?
- **Type:** Fill in the blank
- **Answer:** Cross-Site Request Forgery
- **Why:** Understanding the full name reveals the attack mechanism — forging requests across sites.

**Q2.** True or False: CSRF attacks require the attacker to know the victim's password.
- **Type:** True/False
- **Answer:** False
- **Why:** CSRF exploits existing authenticated sessions. The browser automatically attaches cookies — no password needed.

**Q3.** Which HTTP methods should NEVER perform state-changing operations?
- A) POST and PUT
- B) GET and HEAD
- C) DELETE and PATCH
- D) POST and DELETE
- **Type:** Single choice
- **Answer:** B) GET and HEAD
- **Why:** GET/HEAD should be idempotent and safe. State changes on GET enable simple CSRF via `<img>` tags and links.

**Q4.** What browser behavior makes CSRF possible?
- A) JavaScript execution
- B) Automatic cookie attachment to requests
- C) HTML rendering
- D) DNS resolution
- **Type:** Single choice
- **Answer:** B) Automatic cookie attachment to requests
- **Why:** Browsers attach cookies based on destination domain, regardless of which site initiated the request.

**Q5.** Which cookie attribute directly prevents cross-site cookie sending?
- A) HttpOnly
- B) Secure
- C) SameSite
- D) Path
- **Type:** Single choice
- **Answer:** C) SameSite
- **Why:** SameSite controls whether cookies are sent on cross-site requests. HttpOnly prevents JS access, Secure requires HTTPS.

**Q6.** True or False: An attacker needs to inject JavaScript into the target site to perform CSRF.
- **Type:** True/False
- **Answer:** False
- **Why:** CSRF works from the attacker's own site. A simple HTML form is sufficient. No code injection needed (that would be XSS).

**Q7.** What is the default SameSite value in modern browsers when not explicitly set?
- A) None
- B) Strict
- C) Lax
- D) No default
- **Type:** Single choice
- **Answer:** C) Lax
- **Why:** Since 2020+, Chrome/Firefox/Safari default to Lax when SameSite isn't specified.

**Q8.** Which HTML element can trigger a GET-based CSRF without any user interaction?
- A) `<a>` tag
- B) `<img>` tag
- C) `<form>` tag
- D) `<button>` tag
- **Type:** Single choice
- **Answer:** B) `<img>` tag
- **Why:** Browsers automatically load `<img src="...">`, sending a GET request with cookies. No click needed.

**Q9.** True or False: SameSite=Lax cookies are sent when a user clicks a cross-site link.
- **Type:** True/False
- **Answer:** True
- **Why:** Lax allows cookies on top-level GET navigations (link clicks, address bar). This is intentional for UX.

**Q10.** What is the purpose of a CSRF token?
- A) Encrypt the request body
- B) Prove the request originated from a legitimate page
- C) Authenticate the user
- D) Prevent XSS attacks
- **Type:** Single choice
- **Answer:** B) Prove the request originated from a legitimate page
- **Why:** CSRF tokens are secrets embedded in legitimate pages that attackers cannot read (due to SOP).

**Q11.** Which of these is NOT a CSRF defense?
- A) SameSite cookies
- B) CSRF tokens
- C) HTTPS
- D) Origin header validation
- **Type:** Single choice
- **Answer:** C) HTTPS
- **Why:** HTTPS protects transport (encryption/integrity) but doesn't prevent CSRF. A cross-site form can target HTTPS endpoints.

**Q12.** True or False: The Same-Origin Policy prevents CSRF attacks.
- **Type:** True/False
- **Answer:** False
- **Why:** SOP prevents reading cross-origin responses, not sending requests. CSRF only needs to send a request (side effect occurs regardless of whether attacker reads response).

**Q13.** What happens when a hidden form auto-submits to a banking site?
- A) Browser blocks it due to CORS
- B) Request is sent with the bank's cookies attached
- C) Browser asks user for permission
- D) Request fails due to Same-Origin Policy
- **Type:** Single choice
- **Answer:** B) Request is sent with the bank's cookies attached
- **Why:** Form submissions are "simple requests" — no preflight, no SOP blocking. Browser attaches cookies for the destination.

**Q14.** Which SameSite value provides the strongest CSRF protection?
- A) None
- B) Lax
- C) Strict
- D) Secure
- **Type:** Single choice
- **Answer:** C) Strict
- **Why:** Strict never sends cookies on any cross-site request, including top-level navigations.

**Q15.** What does `HttpOnly` on a cookie prevent?
- A) Cross-site requests
- B) JavaScript access to the cookie
- C) CSRF attacks
- D) Cookie transmission over HTTP
- **Type:** Single choice
- **Answer:** B) JavaScript access to the cookie
- **Why:** HttpOnly means `document.cookie` cannot read/write it. This prevents XSS from stealing the cookie, but doesn't affect CSRF (browser still sends it).

**Q16.** True or False: A form submission from evil.com to bank.com is blocked by CORS.
- **Type:** True/False
- **Answer:** False
- **Why:** Form submissions don't use CORS. They're "simple requests" — always sent by the browser. CORS only applies to XHR/fetch.

**Q17.** What is the relationship between sessions and CSRF?
- A) Sessions cause CSRF
- B) CSRF exploits browser session management
- C) Sessions prevent CSRF
- D) They are unrelated
- **Type:** Single choice
- **Answer:** B) CSRF exploits browser session management
- **Why:** CSRF exists because sessions (via cookies) are automatically included in requests, allowing forged requests to be authenticated.

**Q18.** Which content type does NOT trigger a CORS preflight?
- A) application/json
- B) application/x-www-form-urlencoded
- C) application/xml
- D) multipart/mixed
- **Type:** Single choice
- **Answer:** B) application/x-www-form-urlencoded
- **Why:** Only `application/x-www-form-urlencoded`, `multipart/form-data`, and `text/plain` are "simple" content types (no preflight).

**Q19.** True or False: CSRF can only work if the victim is currently logged into the target site.
- **Type:** True/False
- **Answer:** True
- **Why:** CSRF relies on the browser sending valid authentication cookies. If the user isn't logged in, there's no valid session to exploit.

**Q20.** What is "login CSRF"?
- A) Attacking the login page with brute force
- B) Forcing a victim to log in with the attacker's credentials
- C) Stealing login credentials via CSRF
- D) Bypassing login entirely
- **Type:** Single choice
- **Answer:** B) Forcing a victim to log in with the attacker's credentials
- **Why:** Victim unknowingly uses attacker's account, then enters sensitive data that attacker can later access.

**Q21–Q35:** *(Additional beginner questions covering form methods, cookie scoping, request types, basic defenses, and browser behavior fundamentals)*

**Q21.** What's the key difference between CSRF and XSS?
- **Type:** Short answer
- **Answer:** XSS executes attacker's code in the victim's browser within the target origin. CSRF tricks the victim's browser into making an unwanted request to a target where they're authenticated. XSS exploits trust a user has in a site; CSRF exploits trust a site has in the user's browser.

**Q22.** True or False: Adding `credentials: "include"` to a fetch request creates CSRF vulnerability.
- **Type:** True/False
- **Answer:** True (partially) — It enables cookies to be sent cross-origin, which can enable CSRF if not properly protected.

**Q23.** Which of these can an attacker site do WITHOUT user interaction?
- A) Submit a POST form
- B) Click a link
- C) Load an image
- D) Both A and C
- **Type:** Single choice
- **Answer:** D) Both A and C
- **Why:** Auto-submit forms (`onload`) and image loads happen without interaction. Link clicks require user action.

**Q24.** What is the "origin" of a request from `https://app.example.com:8080/page`?
- **Type:** Fill in the blank
- **Answer:** `https://app.example.com:8080`
- **Why:** Origin = scheme + host + port.

**Q25.** True or False: A cookie set with `Domain=.example.com` is sent to all subdomains.
- **Type:** True/False
- **Answer:** True
- **Why:** The leading dot (or any Domain attribute) makes the cookie available to the specified domain and all subdomains.

**Q26.** What does the `Secure` cookie attribute do?
- **Type:** Short answer
- **Answer:** Ensures the cookie is only sent over HTTPS connections, preventing transmission over unencrypted HTTP.

**Q27.** Why can't an attacker read a CSRF token from another origin?
- **Type:** Short answer
- **Answer:** The Same-Origin Policy prevents JavaScript on one origin from reading responses (DOM, cookies, fetch responses) from another origin.

**Q28.** True or False: CSRF tokens should be regenerated on every request.
- **Type:** True/False
- **Answer:** False — Per-session tokens are acceptable. Per-request adds complexity without significant security gain in most cases (and breaks back button/tabs).

**Q29.** What type of CSRF attack uses `<img src="...">`?
- **Type:** Short answer
- **Answer:** GET-based CSRF. The img tag triggers an automatic GET request with cookies attached.

**Q30.** Which header do browsers ALWAYS send on cross-origin POST requests?
- A) Referer
- B) Origin
- C) X-Requested-With
- D) Authorization
- **Type:** Single choice
- **Answer:** B) Origin
- **Why:** Browsers reliably send the Origin header on cross-origin POST/PUT/DELETE. Referer may be stripped by policy.

**Q31.** True or False: `SameSite=None` requires the `Secure` attribute.
- **Type:** True/False
- **Answer:** True
- **Why:** Browsers reject `SameSite=None` cookies without `Secure` flag (Chrome enforces this since 2020).

**Q32.** What's the purpose of the `__Host-` cookie prefix?
- **Type:** Short answer
- **Answer:** It requires the cookie to have `Secure`, no `Domain` attribute, and `Path=/`. This prevents subdomain cookie injection attacks.

**Q33.** Can a CSRF attack steal data from the target site?
- **Type:** Short answer
- **Answer:** Not directly. CSRF causes actions (side effects) but can't read responses (SOP blocks that). However, indirect data theft is possible (e.g., changing notification email to attacker's address).

**Q34.** What is the difference between "same-site" and "same-origin"?
- **Type:** Short answer
- **Answer:** Same-origin requires exact scheme+host+port match. Same-site only requires same scheme+eTLD+1 (registrable domain). `a.example.com` and `b.example.com` are same-site but cross-origin.

**Q35.** True or False: REST APIs that only accept `Content-Type: application/json` are immune to form-based CSRF.
- **Type:** True/False
- **Answer:** True (mostly) — HTML forms can only send `application/x-www-form-urlencoded`, `multipart/form-data`, or `text/plain`. If the server strictly requires and validates `application/json`, form-based CSRF fails. However, `fetch()` with `credentials: include` could still work if CORS allows it.

---

### Junior (35 questions)

**Q36.** How does the double-submit cookie pattern work?
- **Type:** Scenario-based
- **Answer:** Server sets CSRF token as a cookie. Client reads the cookie via JavaScript and includes the same value in a request header. Server compares cookie value to header value. Attacker can cause browser to send the cookie but cannot read it (SOP), so they can't include the matching header value.

**Q37.** Your React app uses `fetch("/api/action", { credentials: "same-origin" })`. Is it vulnerable to CSRF from `evil.com`?
- **Type:** Scenario-based
- **Answer:** The fetch itself isn't exploitable from evil.com (evil.com can't make your browser run your app's fetch code). But if the API endpoint accepts form-urlencoded POST, an attacker could create their own form targeting that endpoint. The vulnerability depends on the API's content-type handling and SameSite cookie settings.

**Q38.** True or False: `Content-Type: application/json` on a fetch request triggers CORS preflight.
- **Type:** True/False
- **Answer:** True
- **Why:** `application/json` is not one of the three "simple" content types, so the browser sends an OPTIONS preflight first.

**Q39.** What's wrong with this CSRF token implementation?
```javascript
const token = Math.random().toString(36).substring(2);
```
- **Type:** Debugging
- **Answer:** `Math.random()` is not cryptographically secure. It's predictable and can be reproduced if the attacker knows the seed. Use `crypto.randomBytes(32)` or `crypto.getRandomValues()`.

**Q40.** Your API returns CORS header `Access-Control-Allow-Origin: *`. Can CSRF still occur?
- **Type:** Scenario-based
- **Answer:** Yes. CORS wildcard with credentials is actually rejected by browsers (`*` + `credentials: include` doesn't work). But more importantly, CSRF doesn't need to read the response — it just needs to send the request. Form-based CSRF doesn't use CORS at all.

**Q41.** When should you use `SameSite=Strict` vs `SameSite=Lax`?
- **Type:** Short answer
- **Answer:** Use Strict for admin panels, banking, and internal tools where UX from external links is less important. Use Lax for public-facing apps where users navigate from external links (Google search, emails) and need to remain logged in.

**Q42.** True or False: If an API requires the `Authorization: Bearer <token>` header, it's immune to CSRF.
- **Type:** True/False
- **Answer:** True — Browsers never automatically attach Authorization headers. They must be set by JavaScript, and an attacker's site can't force the victim's browser to add this header to requests.

**Q43.** Your Express app uses `csurf` middleware. A request fails with "invalid csrf token". What should you check?
- **Type:** Debugging
- **Answer:** 1) Is the token included in the request (body `_csrf`, query, or header `x-csrf-token`)? 2) Does the cookie/session containing the secret exist? 3) Has the session expired? 4) Is the token from the correct session? 5) Are cookies being sent (check SameSite/Secure settings)?

**Q44.** How does Origin header validation prevent CSRF?
- **Type:** Short answer
- **Answer:** Browsers automatically set the Origin header on cross-origin requests to the initiating origin. Server checks if Origin matches expected values. Attacker's site sends `Origin: https://evil.com` which doesn't match — request rejected. Origin header cannot be spoofed by JavaScript.

**Q45.** What's the vulnerability in this code?
```javascript
app.get("/api/delete-user/:id", authenticateUser, (req, res) => {
  deleteUser(req.params.id);
  res.json({ success: true });
});
```
- **Type:** Debugging
- **Answer:** State-changing operation (delete) on GET endpoint. An attacker can use `<img src="/api/delete-user/123">` to trigger deletion. Even SameSite=Lax doesn't help because link clicks (top-level GET) send Lax cookies. Must use POST/DELETE method.

**Q46.** True or False: CSRF tokens should be transmitted over HTTPS to prevent interception.
- **Type:** True/False
- **Answer:** True — If tokens are sent over HTTP, they can be intercepted via MITM, allowing the attacker to forge valid requests.

**Q47.** An OAuth login flow doesn't use the `state` parameter. What's the risk?
- **Type:** Scenario-based
- **Answer:** Login CSRF — attacker can trick victim into completing OAuth with attacker's account. Victim's session gets linked to attacker's identity, or attacker gains access to victim's account through the linked provider.

**Q48.** What's the difference between a CSRF token in a hidden form field vs a custom header?
- **Type:** Comparison
- **Answer:** Hidden field: works with traditional form submissions, no JS needed. Custom header: only works with XHR/fetch (requires JS), but triggers CORS preflight for cross-origin requests (additional protection layer). Headers can't be set by HTML forms.

**Q49.** Your React app stores the JWT in localStorage and sends it via Authorization header. Is CSRF a concern?
- **Type:** Scenario-based
- **Answer:** No CSRF risk — browsers don't automatically attach localStorage values to requests. But XSS risk is HIGH — any XSS can read localStorage and steal the token. Consider httpOnly cookies instead.

**Q50–Q70:** *(Additional junior questions covering React patterns, axios configuration, OAuth basics, token delivery, CORS interaction, and practical debugging)*

**Q50.** True or False: A `<form>` tag can set custom request headers.
- **Type:** True/False
- **Answer:** False — Forms can only set method, action, enctype, and form fields. Custom headers require JavaScript (fetch/XHR).

**Q51.** What's the CSRF risk of `withCredentials: true` in axios?
- **Type:** Short answer
- **Answer:** It causes cookies to be sent on cross-origin requests. If your API relies on cookies for auth and the CORS configuration allows the requesting origin, cross-origin CSRF via fetch becomes possible.

**Q52.** How do you deliver a CSRF token to a React SPA?
- **Type:** Short answer
- **Answer:** Options: 1) Meta tag in server-rendered HTML, 2) Cookie (double-submit: non-httpOnly cookie readable by JS), 3) Dedicated `/api/csrf-token` endpoint, 4) Response header on initial page load.

**Q53.** True or False: Preflight requests (OPTIONS) include cookies.
- **Type:** True/False
- **Answer:** False — OPTIONS preflight requests never include credentials/cookies. Only the actual request after successful preflight includes them.

**Q54.** What makes `text/plain` content type dangerous for CSRF?
- **Type:** Short answer
- **Answer:** `text/plain` is a "simple" content type — no CORS preflight triggered. Forms can send `enctype="text/plain"`, and if the server parses the body regardless of Content-Type, JSON-like payloads can be crafted.

**Q55.** Your CSRF token validation uses string comparison (`===`). What's the security risk?
- **Type:** Debugging
- **Answer:** Timing attack — string comparison may short-circuit on first mismatch, leaking information about correct characters. Use `crypto.timingSafeEqual()` for constant-time comparison.

---

### Senior (35 questions)

**Q71.** Design a CSRF protection strategy for a Next.js App Router application that uses Server Actions, API routes, and edge middleware.
- **Type:** Architecture challenge
- **Answer:** Server Actions: leverage built-in Origin validation. API routes: middleware validates Origin header + double-submit CSRF token. Edge middleware: validate Origin for all non-GET requests to /api/*. Session cookies: `__Host-` prefix, SameSite=Lax, httpOnly. For critical operations: additional CSRF token in Server Action form data bound to session.

**Q72.** Your enterprise app has 50 microservices behind an API gateway. Where should CSRF validation happen?
- **Type:** Architecture challenge
- **Answer:** Gateway level: Origin validation (first line), reject obviously cross-site requests. Service level: CSRF token validation (defense-in-depth). Rationale: Gateway handles broad filtering; services validate tokens because they own session context. Never solely at gateway — compromised gateway = total bypass.

**Q73.** True or False: GraphQL APIs are inherently protected from CSRF because they use POST.
- **Type:** True/False
- **Answer:** False — Many GraphQL servers accept GET requests with query parameters, and some accept POST with `application/x-www-form-urlencoded`. Both bypass preflight. Must explicitly require `Content-Type: application/json` and validate it.

**Q74.** A security audit finds that your SPA sets `SameSite=None; Secure` on session cookies for cross-site iframe embedding. How do you maintain CSRF protection?
- **Type:** Scenario-based
- **Answer:** Since SameSite=None removes browser CSRF protection: 1) Require CSRF tokens on all mutations, 2) Validate Origin header strictly, 3) Use `X-Frame-Options` / CSP `frame-ancestors` to limit who can embed, 4) Consider token-binding to frame context, 5) Add `Sec-Fetch-Dest` header validation.

**Q75.** How should CSRF protection differ for a real-time WebSocket-based application?
- **Type:** Architecture challenge
- **Answer:** WebSocket handshake (HTTP Upgrade) sends cookies — validate CSRF at handshake time. Options: 1) Validate Origin header during WS upgrade, 2) Require auth token as WS protocol/query param (not cookie), 3) First message must include CSRF token. After handshake, WS messages don't carry cookies — subsequent messages are inherently CSRF-safe.

**Q76.** Your production monitoring shows CSRF token validation failures spiking. How do you investigate?
- **Type:** Incident response
- **Answer:** 1) Check if it's a deploy issue (token format change?), 2) Check cookie expiry (sessions expiring?), 3) Check for bot traffic (missing tokens), 4) Correlate with specific endpoints/users, 5) Check if CDN is caching pages with stale tokens, 6) Check SameSite cookie changes in browser updates, 7) Check if CSRF cookie is being stripped by proxy/CDN.

**Q77.** Design session architecture for an application that runs on both `app.example.com` and `admin.example.com`.
- **Type:** Architecture challenge
- **Answer:** Separate session cookies per subdomain using `__Host-` prefix (no Domain attribute). This ensures admin session isn't sent to app and vice versa. If SSO needed: use OAuth/OIDC between them rather than shared cookies. Admin uses SameSite=Strict; app uses SameSite=Lax.

**Q78.** True or False: Server-side rendering eliminates the need for CSRF tokens if using SameSite=Lax.
- **Type:** True/False
- **Answer:** False — SameSite=Lax still allows top-level GET navigations with cookies. If any GET endpoint has side effects (which it shouldn't, but legacy code...), or if you need to support browsers that don't implement SameSite, tokens are still valuable as defense-in-depth.

**Q79.** How do you implement CSRF protection for a multi-region application where sessions are stored in different regional databases?
- **Type:** Architecture challenge
- **Answer:** Use stateless CSRF: HMAC-based token derived from session ID + server secret. Token = `HMAC(session_id + timestamp, secret)`. Validation only needs the session ID (available in cookie) and the shared secret (available in all regions). No cross-region token lookup needed.

**Q80.** A penetration tester claims they can bypass your CSRF protection using a Flash file. Is this still relevant?
- **Type:** Scenario-based
- **Answer:** No — Flash is deprecated and removed from all modern browsers (end of life: Dec 2020). Flash-based CSRF bypass techniques (custom headers via Flash crossdomain.xml) are no longer viable. However, similar concepts may apply to other plugins or browser extensions.

**Q81–Q105:** *(Additional senior questions covering edge auth, production debugging, enterprise governance, OAuth security, and advanced architecture patterns)*

**Q81.** How should Cloudflare Workers handle CSRF for edge-rendered pages?
- **Type:** Architecture
- **Answer:** At the edge: validate Origin header, enforce SameSite on cookies set from Workers. Challenge: Workers are stateless — use HMAC-based double-submit (token derived from session, verified without session store lookup). For KV-stored sessions: validate CSRF token against session-bound secret.

---

### Expert / Browser Security Engineer (35 questions)

**Q106.** Explain how a browser implements SameSite cookie checking internally. What data structures and request metadata are involved?
- **Type:** Deep analysis
- **Answer:** Browser maintains: 1) Cookie jar indexed by domain/path, 2) Each request has a "site for cookies" computed from the request initiator's eTLD+1, 3) Navigation vs subresource classification (based on request destination), 4) Top-level site context. On each request, browser: computes target site, computes initiator site, checks if same-site (schemeful), checks navigation type, applies Strict/Lax/None policy. Chromium uses `net::SiteForCookies` and `net::IsolationInfo`.

**Q107.** A researcher discovers that during a 302 redirect from `evil.com → bank.com`, SameSite=Lax cookies are sent. Is this a browser bug?
- **Type:** Scenario-based
- **Answer:** It depends on the redirect type. If it's a top-level navigation (user clicked link on evil.com → 302 to bank.com), Lax cookies ARE correctly sent (it's still a top-level GET navigation). If it's a subresource redirect (evil.com's script fetches evil.com/redirect → 302 to bank.com), cookies should NOT be sent. The "site for cookies" is computed based on the initiator, not intermediate redirects.

**Q108.** How could browser cookie partitioning (CHIPS - Cookies Having Independent Partitioned State) affect CSRF defense strategies?
- **Type:** Deep analysis
- **Answer:** CHIPS partitions cookies by top-level site. A partitioned cookie set under `bank.com` when embedded in `shopping.com` is different from `bank.com` in top-level context. Impact on CSRF: partitioned cookies are inherently CSRF-safe when embedded (attacker's top-level site gets different partition). But unpartitioned cookies (first-party) still follow traditional CSRF rules. Defense strategy: minimal change for most apps — CHIPS primarily affects third-party embeds.

**Q109.** Design a CSRF protection mechanism that works even if XSS is present on the page.
- **Type:** Architecture challenge
- **Answer:** If XSS exists, traditional CSRF tokens are compromised (attacker's script reads them). Possible defenses: 1) Re-authentication (password/biometric) for critical actions — XSS can't provide this, 2) Hardware token challenge (WebAuthn) — bound to origin, 3) Out-of-band confirmation (push notification), 4) Request signing with hardware key. Note: if XSS exists, CSRF is the lesser problem — XSS gives full origin access.

**Q110.** How does the `Sec-Fetch-*` header family interact with CSRF defense, and should servers rely on it?
- **Type:** Deep analysis
- **Answer:** `Sec-Fetch-Site`: `cross-site`, `same-site`, `same-origin`, `none`. `Sec-Fetch-Mode`: `navigate`, `cors`, `no-cors`, `same-origin`. `Sec-Fetch-Dest`: `document`, `empty`, etc. Servers CAN use these for defense: reject `Sec-Fetch-Site: cross-site` on mutation endpoints. Benefits: browser-set (can't be spoofed by JS), reliable. Caveats: older browsers don't send them, so can't be sole defense. Use as additional signal in defense-in-depth.

**Q111.** Explain how an attacker could exploit a CSRF vulnerability in combination with an open redirect to bypass Origin validation.
- **Type:** Attack chain
- **Answer:** If target has open redirect: `bank.com/redirect?url=evil.com`. Attacker chains: evil.com → form POST to bank.com/redirect → but this doesn't help because Origin is still evil.com. However, if the open redirect is on a same-site domain AND the redirect itself triggers a POST (307 redirect preserves method), then Origin becomes the redirecting site (same-site). This bypasses origin checking if server only checks same-site, not same-origin.

**Q112–Q140:** *(Additional expert questions covering browser networking internals, advanced bypass techniques, specification-level analysis, and large-scale architecture decisions)*

**Q112.** True or False: A 307 redirect preserves the HTTP method and body, while a 302 typically converts POST to GET.
- **Type:** True/False
- **Answer:** True — 307 guarantees method preservation. 302 in practice converts POST→GET (though spec says shouldn't). This matters for CSRF because a 307 from same-site to target preserves the POST + cookies, potentially bypassing some defenses.

**Q113.** How would you design a CSRF-immune authentication system for a browser-based application from scratch?
- **Type:** Architecture challenge
- **Answer:** Use the "split token" approach: 1) Authentication via non-cookie mechanism (Authorization header with token stored in memory), 2) Refresh via httpOnly Strict cookie on dedicated endpoint, 3) BFF pattern for token management, 4) WebAuthn for critical operations. Alternative: Cookie-based with SameSite=Strict + synchronizer tokens + Origin validation + re-auth for critical ops.

---

## 16. Personalized Recommendations

### For Your Stack (React + Next.js + Astro + Vite + TypeScript)

#### Priority CSRF Concepts

1. **Immediate:** SameSite cookie configuration for Next.js sessions
2. **Immediate:** Origin validation middleware in Next.js/Astro API routes
3. **High:** Understanding how Server Actions handle CSRF (built-in protection)
4. **High:** CSRF token delivery pattern for React SPAs
5. **Medium:** OAuth state/PKCE implementation for social login
6. **Medium:** Cookie architecture for SSR vs client-side rendering
7. **Advanced:** Edge rendering (Vercel Edge) session implications
8. **Advanced:** Multi-tenant CSRF isolation

#### Common Authentication Mistakes

| Mistake | Impact | Fix |
|---------|--------|-----|
| JWT in localStorage | XSS → token theft | httpOnly cookie + CSRF token |
| No CSRF on API routes | CSRF via form/fetch | Middleware validation |
| SameSite not set explicitly | Browser-dependent behavior | Always set Lax minimum |
| GET endpoints with side effects | Image/link CSRF | POST for all mutations |
| Shared session across subdomains | Cross-subdomain CSRF | `__Host-` prefix |
| No Origin validation | Basic CSRF possible | Middleware check |
| OAuth without state | Login CSRF | Always use state + PKCE |

#### 60-Day Learning Plan

**Week 1-2: Foundations**
- [ ] Understand browser cookie mechanics (SameSite, Secure, HttpOnly, prefixes)
- [ ] Implement basic CSRF token middleware in Express/Next.js
- [ ] Set up SameSite=Lax on all session cookies
- [ ] Test CSRF vulnerability in a local app (create attacker page)

**Week 3-4: Framework Integration**
- [ ] Implement double-submit CSRF in Next.js API routes
- [ ] Configure axios/fetch CSRF interceptors for React
- [ ] Understand Next.js Server Actions CSRF behavior
- [ ] Implement Astro API route CSRF protection
- [ ] Add Origin validation middleware

**Week 5-6: OAuth & Authentication Architecture**
- [ ] Implement OAuth with state + PKCE
- [ ] Design BFF pattern for SPA authentication
- [ ] Implement secure refresh token architecture
- [ ] Test login CSRF prevention

**Week 7-8: Advanced & Enterprise**
- [ ] Design multi-tenant CSRF isolation
- [ ] Implement CSRF monitoring and alerting
- [ ] Add automated CSRF testing to CI/CD (ZAP/Semgrep)
- [ ] Review and harden existing applications
- [ ] Conduct CSRF threat modeling for your architecture
- [ ] Study browser Sec-Fetch-* headers and implement server-side checks

**Ongoing:**
- [ ] Read OWASP CSRF Prevention Cheat Sheet quarterly
- [ ] Monitor browser vendor blog posts for SameSite changes
- [ ] Participate in security reviews
- [ ] Practice with OWASP WebGoat/Juice Shop

---

## 17. Official Documentation & Reference Links

### Beginner

| Resource | URL |
|----------|-----|
| OWASP CSRF Attack Description | https://owasp.org/www-community/attacks/csrf |
| MDN: Using HTTP Cookies | https://developer.mozilla.org/en-US/docs/Web/HTTP/Cookies |
| MDN: SameSite Cookies | https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Set-Cookie/SameSite |
| web.dev: SameSite Cookies Explained | https://web.dev/samesite-cookies-explained/ |
| MDN: Same-Origin Policy | https://developer.mozilla.org/en-US/docs/Web/Security/Same-origin_policy |
| PortSwigger: CSRF | https://portswigger.net/web-security/csrf |

### Intermediate

| Resource | URL |
|----------|-----|
| OWASP CSRF Prevention Cheat Sheet | https://cheatsheetseries.owasp.org/cheatsheets/Cross-Site_Request_Forgery_Prevention_Cheat_Sheet.html |
| MDN: CORS | https://developer.mozilla.org/en-US/docs/Web/HTTP/CORS |
| Auth.js (NextAuth) | https://authjs.dev |
| OAuth 2.0 | https://oauth.net/2/ |
| OpenID Connect | https://openid.net/connect/ |
| MDN: Fetch API credentials | https://developer.mozilla.org/en-US/docs/Web/API/fetch |
| Chrome: SameSite Updates | https://www.chromium.org/updates/same-site/ |

### Advanced

| Resource | URL |
|----------|-----|
| RFC 6749: OAuth 2.0 | https://datatracker.ietf.org/doc/html/rfc6749 |
| RFC 7636: PKCE | https://datatracker.ietf.org/doc/html/rfc7636 |
| Chromium SameSite FAQ | https://www.chromium.org/updates/same-site/faq |
| Fetch Metadata (Sec-Fetch-*) | https://web.dev/fetch-metadata/ |
| OWASP Testing Guide: CSRF | https://owasp.org/www-project-web-security-testing-guide/ |
| PortSwigger: Bypassing SameSite | https://portswigger.net/web-security/csrf/bypassing-samesite-restrictions |

### Expert / Browser Internals

| Resource | URL |
|----------|-----|
| Chromium Cookie Source Code | https://source.chromium.org/chromium/chromium/src/+/main:net/cookies/ |
| HTML Spec: Origin | https://html.spec.whatwg.org/multipage/origin.html |
| Fetch Spec | https://fetch.spec.whatwg.org/ |
| Cookie Spec (RFC 6265bis) | https://datatracker.ietf.org/doc/html/draft-ietf-httpbis-rfc6265bis |
| W3C Fetch Metadata | https://www.w3.org/TR/fetch-metadata/ |
| Chromium Network Stack | https://source.chromium.org/chromium/chromium/src/+/main:net/ |

---

## 18. Advanced Engineering Topics

### Browser Credential Behavior Internals

The browser's cookie-sending decision follows this algorithm:

```
function shouldSendCookie(cookie, request):
  1. Domain match: cookie.domain matches request URL
  2. Path match: cookie.path is prefix of request path
  3. Secure check: if cookie.secure, request must be HTTPS
  4. HttpOnly check: if cookie.httpOnly and request from JS, block read
  5. SameSite check:
     a. Compute request's "site for cookies" from initiator
     b. Compute target site from request URL
     c. If cross-site:
        - Strict: block
        - Lax: allow only if top-level navigation + safe method (GET)
        - None: allow (requires Secure)
  6. Partition check (CHIPS): if partitioned, must match top-level partition key
```

### Future Browser Authentication Directions

- **WebAuthn/Passkeys:** Phishing-resistant, origin-bound credentials. Eliminates CSRF for auth flows.
- **FedCM (Federated Credential Management):** Browser-mediated identity federation without redirects. Reduces OAuth CSRF surface.
- **Login Status API:** Browser knows when user is logged in — may enable new trust signals.
- **Storage Access API:** Controlled cookie access for embedded contexts — affects cross-site auth patterns.
- **Private State Tokens:** Replacement for tracking cookies that provides limited trust signals.

### Secure-by-Default Platform Design

For platform teams building internal frameworks:

```typescript
// Framework-level CSRF protection (team doesn't need to think about it)
// Every route handler automatically gets CSRF validation

// platform/createApiHandler.ts
export function createApiHandler(handler: Handler) {
  return async (req: Request) => {
    // Automatic: skip for safe methods
    if (!["GET", "HEAD", "OPTIONS"].includes(req.method)) {
      // Automatic: Origin validation
      if (!validateOrigin(req)) {
        return new Response("Forbidden", { status: 403 });
      }
      // Automatic: CSRF token validation
      if (!validateCsrfToken(req)) {
        return new Response("Invalid CSRF", { status: 403 });
      }
    }
    // Automatic: set secure cookie defaults
    const res = await handler(req);
    enforceSecureCookieDefaults(res);
    return res;
  };
}
```

---

## Summary

### Key Takeaways

1. **CSRF exploits browser automatic credential attachment** — understand this mental model deeply
2. **SameSite=Lax is the most impactful single defense** — modern browsers default to it
3. **Defense-in-depth is essential:** SameSite + Origin validation + CSRF tokens + proper CORS
4. **Authentication architecture determines CSRF surface** — cookie-based auth needs CSRF protection, bearer token auth doesn't
5. **SPAs are NOT immune** — if using cookies for auth, CSRF applies
6. **OAuth needs its own CSRF protection** — always use `state` + PKCE
7. **Server Actions / RSC have built-in protections** — but understand what they protect and what they don't

### Next Steps

1. Audit your current applications for CSRF vulnerabilities
2. Implement SameSite + Origin validation as minimum baseline
3. Add automated CSRF testing to your CI/CD pipeline
4. Study OAuth security deeply (state, PKCE, redirect validation)
5. Practice attacking your own apps to build attacker mindset

### Advanced Topics to Continue Learning

- Browser process isolation and site isolation
- Spectre/Meltdown implications on web security
- WebAuthn/Passkeys as CSRF-immune authentication
- FedCM and the future of web identity
- Supply chain attacks on authentication libraries
- Post-quantum implications on session security
- Browser storage partitioning and its security implications
