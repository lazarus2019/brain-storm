# Cloudflare Workers

This folder collects research notes about Cloudflare, with a focus on Workers, edge computing, and supporting platform primitives.

## What this covers

The current notes are centered on how Cloudflare Workers can be used to build globally distributed backend logic for modern frontend apps such as React, Next.js, and Astro.

### Main themes

- Edge-first request handling
- Workers runtime basics and limitations
- KV, Durable Objects, D1, R2, and Queues
- Integration patterns for frontend frameworks
- Performance, latency, and cost tradeoffs
- Architecture brainstorming and proof-of-concept ideas

## Docs

- [Brainstorm prompt](docs/BRAIN_STORM.md)
- [Cloudflare Workers deep dive](docs/CLOUDFLARE_WORKER.md)

## Summary

Cloudflare Workers run JavaScript or TypeScript on Cloudflare's global edge network using a V8 isolate runtime. They are a strong fit for request routing, authentication, API gateways, feature flags, personalization, rate limiting, and other edge tasks where low latency and global distribution matter.

Use Workers when you want:

- fast execution close to users
- minimal cold starts
- simple request-in / response-out services
- tight integration with Cloudflare's storage and messaging primitives

Avoid using Workers for:

- heavy CPU workloads
- filesystem-dependent apps
- long-running server processes
- large legacy Node.js services that need full runtime compatibility

## Recommended next steps

1. Read the deep dive.
2. Pick one use case to prototype.
3. Compare Workers against your current backend and deployment model.
4. Capture architecture notes, tradeoffs, and open questions in this folder.
