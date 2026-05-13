# Browser Performance & Rendering

Study notes for browser rendering internals, Critical Rendering Path, layout/paint/compositing pipeline, Core Web Vitals, and production-grade frontend performance engineering.

## Topics

### Critical Rendering Path (CRP)

Complete engineering guide for browser rendering: parsing pipeline, render tree construction, layout/paint/compositing, GPU acceleration, frame budgets, and performance optimization.

- [Deep dive guide](docs/CRITICAL_RENDER_PATH.md)
- [Layout, Paint, Composite & Layers](docs/LAYOUT_PAINT_COMPOSITE_LAYER.md)
- [Web Vitals](docs/WEB_VITALS.md)
- [Brainstorm prompt](docs/BRAIN_STORM.md)

## Key Concepts

- HTML parsing & DOM construction
- CSSOM & render-blocking behavior
- Render tree, layout, paint, compositing
- GPU acceleration & layer promotion
- Core Web Vitals (LCP, CLS, INP)
- React hydration & streaming SSR
- Island architecture (Astro)
- Performance profiling & debugging
- Browser threading & scheduling
- Frame budget engineering (60fps)
