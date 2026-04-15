# Brain Storm

Repository for researching and collecting notes on technology, architecture, and system design.

## Purpose

This repository is an index of study materials, experiments, and references. Each concept should have its own README, with deeper notes and examples stored beside it.

## Current concepts

### Nix Flakes

Study notes for reproducible development environments, multi-shell setups, project recipes, automation, and developer experience improvements.

- [Concept overview](nix-flake-samples/README.md)
- [Deep dive guide](nix-flake-samples/docs/NIX_FLAKE.md)
- [Brainstorm prompt](nix-flake-samples/docs/BRAIN_STORM.md)

### Cloudflare Workers

Study notes for edge computing, runtime constraints, storage primitives, and frontend-to-edge architecture.

- [Concept overview](cloudflare/README.md)
- [Deep dive guide](cloudflare/docs/CLOUDFLARE_WORKER.md)
- [Brainstorm prompt](cloudflare/docs/BRAIN_STORM.md)

### GitHub Actions

Study notes for CI/CD automation, deployment pipelines, release engineering, and platform engineering with GitHub Actions.

- [Concept overview](github/README.md)
- [Deep dive guide](github/docs/GITHUB_ACTION.md)
- [Brainstorm prompt](github/docs/BRAIN_STORM.md)

## Suggested structure

- README.md — repository home and concept index
- <topic>/README.md — concept overview
- <topic>/docs/*.md — detailed research notes
- <topic>/assets/ — diagrams, screenshots, and reference images

## How to use this repo

1. Pick a topic to research.
2. Create a folder for the topic.
3. Add a README that explains the concept at a high level.
4. Add supporting docs for deeper analysis, tradeoffs, examples, and open questions.
5. Keep links from this root README updated as new concepts are added.

## Notes

The current focus is Nix Flakes, but this repository can grow to cover broader topics such as platform engineering, distributed systems, software architecture, and system design.
