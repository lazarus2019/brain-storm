# Security

Study notes for web and application security: browser and server attack vectors, defensive patterns, secure-by-default architecture, and operational practices.

## Contents

- [Deep dive guide — Security](security/docs/BRAIN_STORM.md) — Outline and deep-dive prompts for a comprehensive security guide.
- [CORS & Proxy guide](security/docs/CORS_AND_PROXY.md)
- [CORS & Proxy — Quizzes](security/docs/CORS_AND_PROXY_QUIZS.md)
- [Content Security Policy (CSP)](security/docs/CSP.md)
- [Cross-Site Request Forgery (CSRF)](security/docs/CSRF.md)
- [Cross-Site Scripting (XSS)](security/docs/XSS.md)
- [Brainstorm prompt](security/docs/BRAIN_STORM.md)

## Key topics covered

- OWASP Top 10 and threat modeling
- Cross-Site Scripting (XSS): reflected, stored, DOM XSS; context-aware escaping and sanitization
- Cross-Site Request Forgery (CSRF): tokens, double-submit cookies, SameSite cookies
- Cross-Origin Resource Sharing (CORS): correct configuration, preflight, credentials, proxy considerations
- Content Security Policy (CSP): directives, reporting, incremental deployment
- Secure headers: HSTS, X-Frame-Options / frame-ancestors, X-Content-Type-Options, Referrer-Policy, Permissions-Policy
- Cookie security: Secure, HttpOnly, SameSite
- Authentication & session management: JWT considerations, session rotation, token handling
- Input validation and output encoding by context
- Subresource Integrity (SRI) and integrity checks for third-party assets
- Supply chain and dependency security (SCA, reproducible builds)
- Security testing and tooling: static analysis, dynamic testing (OWASP ZAP, Burp, Snyk), fuzzing
- Runtime monitoring, logging, and incident response
- Secure-by-default deployment patterns and runtime hardening
- Practical mitigation patterns and example implementations
- 50 practice questions with answers
- 30-day learning plan

## Who this is for

Frontend engineers, backend engineers, security engineers, SREs, platform engineers, and architects who want practical security guidance for web applications.
