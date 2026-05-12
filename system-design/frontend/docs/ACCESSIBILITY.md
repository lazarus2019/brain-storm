# Accessibility (A11Y) — Complete Deep-Dive Guide

A comprehensive learning path and engineering guide for Web Accessibility, written for frontend engineers moving toward senior/staff-level accessibility architecture.

---

# 1. Big Picture

## What Accessibility Is

Accessibility (A11Y) is the practice of designing and engineering products so that people with disabilities can perceive, understand, navigate, interact with, and contribute to the web. It is not a feature — it is a quality attribute of software, like performance or security.

**Why it matters:**
- ~15–20% of the global population has some form of disability (WHO)
- Accessibility lawsuits have increased dramatically (ADA Title III cases exceed 4,000/year in the US alone)
- Accessible products reach larger audiences, improve SEO, and produce better-structured code
- Many accessibility improvements benefit ALL users (captions in noisy environments, keyboard power users, users with temporary injuries)

**Who accessibility helps:**
- Blind or low-vision users (screen readers, magnifiers)
- Deaf or hard-of-hearing users (captions, transcripts)
- Motor-impaired users (keyboard-only, switch devices, voice control)
- Cognitive disabilities (simplified layouts, clear language, predictable navigation)
- Temporary disabilities (broken arm, eye surgery, loud environments)
- Situational limitations (bright sunlight, one-handed phone use)
- Power users (keyboard-heavy workflows)

## Key Concepts

### Accessibility vs Usability vs Inclusive Design

| Concept | Definition | Scope |
|---------|-----------|-------|
| **Accessibility** | Can people with disabilities use this product? | Compliance, technical implementation |
| **Usability** | Is this product easy and efficient to use? | User experience for all users |
| **Inclusive Design** | Was this product designed considering diverse human abilities from the start? | Design methodology |

### Semantic HTML

Semantic HTML means using HTML elements for their intended purpose. A `<button>` is a button. A `<nav>` is navigation. A `<h1>` is a top-level heading. Browsers and assistive technologies have built-in behavior for semantic elements — keyboard support, role announcements, focus management — all for free.

**Div soup** is when developers use `<div>` and `<span>` for everything, then try to recreate native behavior with JavaScript and ARIA. This is fragile, error-prone, and always worse than semantic HTML.

```
SEMANTIC HTML vs DIV SOUP

✅ <button onClick={handleClick}>Save</button>
   → Focusable, Enter/Space activates, announced as "button"

❌ <div onClick={handleClick} className="btn">Save</div>
   → Not focusable, no keyboard support, not announced as button
   → Requires: tabIndex, onKeyDown, role="button", aria-pressed...
```

### Assistive Technologies

- **Screen readers**: Software that reads UI aloud (NVDA, JAWS, VoiceOver, TalkBack)
- **Screen magnifiers**: Enlarge portions of the screen
- **Switch devices**: Physical buttons to navigate UI sequentially
- **Voice control**: Dragon NaturallySpeaking, Voice Control (macOS/iOS)
- **Braille displays**: Physical devices that render text as braille

### The Accessibility Tree

Browsers build a parallel tree alongside the DOM called the **accessibility tree**. This is what assistive technologies consume.

```
DOM Tree                    Accessibility Tree
─────────                   ──────────────────
<html>                      Document
  <body>                      ├── navigation "Main"
    <nav aria-label="Main">   │   ├── link "Home"
      <a href="/">Home</a>    │   └── link "About"
      <a href="/about">About  ├── heading level 1 "Welcome"
    <main>                    ├── main
      <h1>Welcome</h1>       │   ├── text "Hello world"
      <p>Hello world</p>     │   └── button "Submit"
      <button>Submit</button>
```

**Key insight:** If an element is not in the accessibility tree (or is in the tree with wrong semantics), assistive technologies cannot interact with it. The accessibility tree is the API contract between your UI and assistive technologies.

### Screen Readers and UI Interpretation

Screen readers traverse the accessibility tree, not the DOM. They:
1. Announce the **role** (button, link, heading, region)
2. Announce the **name** (accessible name from text content, label, aria-label)
3. Announce the **state** (expanded, selected, checked, disabled)
4. Announce the **value** (for inputs, sliders)

### Keyboard Navigation Internals

- **Tab** moves focus between interactive elements (links, buttons, inputs)
- **Arrow keys** navigate within composite widgets (tabs, menus, radio groups)
- **Enter/Space** activate the focused element
- **Escape** closes overlays / cancels
- Focus follows a **tab order** determined by DOM order (modified by `tabindex`)
- `tabindex="0"` — adds element to natural tab order
- `tabindex="-1"` — programmatically focusable but not in tab order
- `tabindex="1+"` — **anti-pattern**, creates unpredictable tab order

### ARIA (Accessible Rich Internet Applications)

ARIA adds semantic information to elements that lack it. The first rule of ARIA:

> **Don't use ARIA if you can use native HTML instead.**

ARIA consists of:
- **Roles**: `role="dialog"`, `role="tablist"`, `role="alert"`
- **Properties**: `aria-label`, `aria-describedby`, `aria-required`
- **States**: `aria-expanded`, `aria-selected`, `aria-checked`, `aria-hidden`

**When ARIA is useful:**
- Custom widgets with no native HTML equivalent (tabs, combobox, tree view)
- Dynamic content updates (live regions)
- Enhancing existing semantics (aria-label for icon buttons)

**When ARIA becomes dangerous:**
- Using wrong roles creates worse experience than no ARIA
- `aria-hidden="true"` on focusable elements traps screen reader users
- Overusing `role="presentation"` strips semantics users need
- Conflicting ARIA and native semantics cause unpredictable behavior

### Color Contrast

WCAG requires minimum contrast ratios:
- **AA**: 4.5:1 for normal text, 3:1 for large text
- **AAA**: 7:1 for normal text, 4.5:1 for large text
- Non-text UI components: 3:1 against adjacent colors

### Reduced Motion

Some users experience motion sickness, seizures, or vestigo from animations. Use `prefers-reduced-motion`:

```css
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    animation-duration: 0.01ms !important;
    transition-duration: 0.01ms !important;
  }
}
```

### Focus Management

Focus management is one of the hardest accessibility problems in SPAs:
- When a modal opens → move focus into it
- When a modal closes → return focus to the trigger
- When navigating routes in SPA → announce new page, move focus to main content or heading
- When content is dynamically added → announce it via live regions, don't steal focus

### Live Regions

Live regions announce dynamic content changes to screen readers without moving focus:

```html
<div aria-live="polite" aria-atomic="true">
  <!-- Screen reader announces when content changes -->
  3 items in cart
</div>

<div role="alert">
  <!-- Assertive: interrupts current announcement -->
  Form submission failed
</div>
```

---

# 2. Learning Roadmap by Skill Level

## Level 1 — Newbie

### Concepts to Master
- Use semantic HTML: `<button>`, `<a>`, `<nav>`, `<main>`, `<header>`, `<footer>`, `<section>`, `<article>`, `<h1>`–`<h6>`
- Every `<img>` needs `alt` text (or `alt=""` for decorative images)
- Every form input needs a `<label>` with matching `for`/`id`
- Use `<button>` for actions, `<a>` for navigation — never swap them
- Tab through your page. Can you reach everything? Can you activate everything?
- Check color contrast with browser DevTools
- Never remove `outline` without providing a visible focus style

### Common Beginner Mistakes
1. Using `<div onClick>` instead of `<button>`
2. Removing `:focus` outlines with `outline: none` and no replacement
3. Missing `alt` on images
4. Missing `<label>` on inputs
5. Using color alone to convey meaning (red = error, green = success)
6. Placeholder text as the only label
7. Missing page `<title>`
8. Non-descriptive link text ("Click here")

### 5 Beginner Exercises
1. Build a navigation bar using only semantic HTML (`<nav>`, `<ul>`, `<li>`, `<a>`) — no divs
2. Create a form with proper labels, error messages, and required field indicators — keyboard test it
3. Take an existing page and fix all the contrast issues using browser DevTools
4. Tab through your favorite website — document what works and what's broken
5. Add proper alt text to 10 different types of images (informative, decorative, chart, icon, logo)

---

## Level 2 — Junior

### Concepts to Master
- ARIA roles, states, properties — and when NOT to use them
- Accessible modal: focus trap, escape to close, return focus to trigger
- Accessible dropdown/menu: arrow key navigation, escape to close
- Skip links: `<a href="#main-content" class="skip-link">Skip to main content</a>`
- Live regions: `aria-live="polite"` vs `aria-live="assertive"` vs `role="alert"` vs `role="status"`
- Focus trap: confine Tab cycling within a dialog
- Error handling: associate errors with inputs via `aria-describedby`, announce errors to screen readers
- Screen reader testing basics: enable VoiceOver (macOS) or NVDA (Windows), navigate with it

### Common Anti-Patterns
1. `role="button"` on a `<div>` instead of using `<button>`
2. `aria-label` that contradicts visible text
3. `aria-hidden="true"` on elements that contain focusable children
4. Focus trap that doesn't allow Escape to exit
5. Using `aria-live="assertive"` for non-critical updates
6. Visually hiding content with `display: none` when it should be screen-reader accessible
7. Auto-focusing elements that shouldn't receive focus
8. Click handlers without keyboard equivalents

### 5 Mini Project Ideas
1. Build an accessible modal from scratch — focus trap, escape, focus restoration
2. Build an accessible accordion using `<button>`, `aria-expanded`, and `aria-controls`
3. Build a toast notification system with `role="status"` and `aria-live="polite"`
4. Build an accessible form with inline validation and screen-reader-friendly error messages
5. Build a skip-link navigation system and test it with a screen reader

---

## Level 3 — Senior

### Concepts to Master
- **Accessibility architecture**: building accessibility into component APIs, not bolting it on after
- **Design system accessibility**: every component in the system must have accessibility baked in — focus styles, keyboard interactions, ARIA contracts, screen reader announcements
- **Advanced focus management**: managing focus across route changes, dynamic content, portals, multi-step flows
- **Accessibility testing strategy**: unit tests (jest-axe), integration tests (Testing Library queries by role), E2E tests (Playwright accessibility snapshots), manual testing (screen readers)
- **Keyboard interaction models**: WAI-ARIA Authoring Practices define expected keyboard patterns for every widget type (tabs, menus, trees, grids, comboboxes)
- **SSR/CSR accessibility**: hydration mismatches can break ARIA state, dynamic content loaded client-side may not be announced
- **React accessibility patterns**: `useId()` for label associations, `forwardRef` for focus management, portals for modals, `aria-live` regions for async state
- **Accessibility governance**: VPAT documentation, accessibility statements, regular audits, regression tracking
- **Multi-language accessibility**: `lang` attribute on elements, RTL support, translations of ARIA labels

### 5 Production-Grade Project Examples
1. Build an accessible data table with sorting, filtering, pagination, and screen reader announcements
2. Build an accessible combobox/autocomplete following WAI-ARIA APG patterns
3. Build an accessible tab interface with dynamic tab panels and keyboard navigation
4. Build an accessible multi-step wizard with progress announcements and focus management
5. Build an accessible drag-and-drop interface with keyboard alternatives

---

## Level 4 — Expert

### Concepts to Master
- **Accessibility tree deep dive**: how browsers compute accessible names, roles, and states; name computation algorithm (accname spec)
- **Browser accessibility APIs**: MSAA, UIA, ATK/AT-SPI, AX API (macOS) — the platform APIs that screen readers consume
- **Cross-screen-reader inconsistencies**: NVDA vs JAWS vs VoiceOver behavior differences in tables, live regions, and ARIA roles
- **WCAG deep dive**: understanding Success Criteria at the principle level (Perceivable, Operable, Understandable, Robust); WCAG 2.1 vs 2.2 changes
- **ARIA authoring practices**: complete mastery of APG patterns and when to deviate
- **Platform-level accessibility systems**: how to build an accessibility layer across an entire design system, multiple teams, multiple apps

### What Expert Engineers Care About That Juniors Miss
1. **Accessible name computation** — understanding how browsers resolve `aria-labelledby` > `aria-label` > `<label>` > text content > `title` > `placeholder`
2. **Timing** — screen reader announcements are asynchronous; rapid DOM updates can swallow announcements
3. **Virtual buffer** — screen readers in "browse mode" intercept keystrokes; your keyboard handlers may not fire
4. **Reflow announcements** — React re-renders can reset ARIA state and break live region announcements
5. **Testing reality** — automated tools catch ~30% of accessibility issues; the rest requires manual testing
6. **Cognitive accessibility** — not just screen readers; clear language, predictable patterns, error recovery
7. **Progressive enhancement** — what happens when JS fails? Is the page still navigable?
8. **Performance intersection** — long loading states, skeleton screens, and lazy loading all have accessibility implications

### 10 Advanced Discussion Topics
1. How should a design system enforce accessibility contracts across consuming teams?
2. When is it acceptable to deviate from WAI-ARIA APG patterns?
3. How do you handle accessibility in micro-frontend architectures where each fragment owns its own focus management?
4. What is the right strategy for accessibility regression testing in CI?
5. How should live regions work in concurrent React rendering?
6. What accessibility trade-offs exist between SSR-first and CSR-first architectures?
7. How do you audit and manage accessibility debt at scale?
8. How should keyboard interaction models differ between desktop web and mobile web?
9. What is the right organizational model for accessibility ownership — centralized team vs embedded in each team?
10. How should you handle accessibility for dynamic, AI-generated content?

---

# 3. Setup Guide

## Accessibility Tooling Setup

### ESLint Accessibility Plugin

```bash
pnpm add -D eslint-plugin-jsx-a11y
```

```js
// .eslintrc.js (or eslint.config.js)
module.exports = {
  extends: ['plugin:jsx-a11y/recommended'],
  plugins: ['jsx-a11y'],
};
```

This catches at dev time: missing alt text, missing labels, invalid ARIA, interactive elements without keyboard support.

### axe DevTools (Browser Extension)

1. Install "axe DevTools" extension for Chrome/Firefox
2. Open DevTools → axe DevTools tab → "Scan ALL of my page"
3. Review violations, best practices, and incomplete checks
4. Each issue links to its WCAG success criterion

### Lighthouse Accessibility Audit

1. Chrome DevTools → Lighthouse tab → check "Accessibility" → Generate report
2. Review score and individual audit items
3. Note: Lighthouse uses axe-core under the hood; it catches ~30% of issues

### React Accessibility Setup

```tsx
// Use semantic HTML in components
const Button = ({ children, ...props }: ButtonProps) => (
  <button {...props}>{children}</button>  // Not <div role="button">
);

// Use useId for label associations (React 18+)
import { useId } from 'react';

const Input = ({ label, ...props }: InputProps) => {
  const id = useId();
  return (
    <>
      <label htmlFor={id}>{label}</label>
      <input id={id} {...props} />
    </>
  );
};

// Use forwardRef for focus management
const Dialog = forwardRef<HTMLDivElement, DialogProps>(
  ({ children, ...props }, ref) => (
    <div ref={ref} role="dialog" aria-modal="true" {...props}>
      {children}
    </div>
  )
);
```

### Next.js Accessibility Setup

Next.js provides some built-in accessibility features:
- `next/link` renders a semantic `<a>` tag
- `next/image` requires `alt` prop
- Route announcements on navigation (built-in `<RouteAnnouncer>`)

Add to your Next.js project:
```tsx
// app/layout.tsx
export const metadata = {
  title: 'My App',  // Page <title> is critical for accessibility
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">  {/* lang attribute is essential */}
      <body>
        <a href="#main-content" className="skip-link">Skip to main content</a>
        <header><nav aria-label="Main">...</nav></header>
        <main id="main-content">{children}</main>
        <footer>...</footer>
      </body>
    </html>
  );
}
```

### Astro Accessibility Setup

```astro
---
// src/layouts/Base.astro
---
<html lang="en">
  <head><title>{title}</title></head>
  <body>
    <a href="#main-content" class="skip-link">Skip to main content</a>
    <nav aria-label="Main">...</nav>
    <main id="main-content">
      <slot />
    </main>
  </body>
</html>
```

Astro generates static HTML by default, which gives a strong semantic foundation. Ensure interactive islands maintain keyboard support and ARIA state.

### Keyboard Testing Workflow

1. Put your mouse away
2. Tab through the entire page
3. Verify: Can you see where focus is? Can you reach all interactive elements? Can you activate them?
4. Test modals: Does focus trap work? Does Escape close? Does focus return?
5. Test forms: Can you submit? Are errors announced? Can you navigate to error fields?

### Screen Reader Testing Workflow

| Platform | Screen Reader | Shortcut |
|----------|--------------|----------|
| macOS | VoiceOver | Cmd + F5 |
| Windows | NVDA | Free download from nvaccess.org |
| Windows | JAWS | Commercial |
| iOS | VoiceOver | Settings → Accessibility → VoiceOver |
| Android | TalkBack | Settings → Accessibility → TalkBack |

**Minimum testing matrix:** VoiceOver + Safari (macOS/iOS), NVDA + Firefox/Chrome (Windows)

### Automated Accessibility Testing

```bash
pnpm add -D jest-axe @axe-core/playwright
```

**Jest + jest-axe:**
```tsx
import { render } from '@testing-library/react';
import { axe, toHaveNoViolations } from 'jest-axe';

expect.extend(toHaveNoViolations);

test('Button has no accessibility violations', async () => {
  const { container } = render(<Button>Save</Button>);
  expect(await axe(container)).toHaveNoViolations();
});
```

**Playwright:**
```ts
import { test, expect } from '@playwright/test';
import AxeBuilder from '@axe-core/playwright';

test('home page has no accessibility violations', async ({ page }) => {
  await page.goto('/');
  const results = await new AxeBuilder({ page }).analyze();
  expect(results.violations).toEqual([]);
});
```

### CI Accessibility Testing Integration

```yaml
# GitHub Actions
- name: Run accessibility tests
  run: pnpm test:a11y

- name: Lighthouse CI
  uses: treosh/lighthouse-ci-action@v11
  with:
    urls: |
      http://localhost:3000/
    budgetPath: ./lighthouse-budget.json
```

### Storybook Accessibility Integration

```bash
pnpm add -D @storybook/addon-a11y
```

```ts
// .storybook/main.ts
const config: StorybookConfig = {
  addons: ['@storybook/addon-a11y'],
};
```

Every story now shows an "Accessibility" panel with axe-core violations.

### Recommended Folder Structure

```
src/
├── components/
│   ├── Button/
│   │   ├── Button.tsx
│   │   ├── Button.test.tsx      # includes jest-axe tests
│   │   └── Button.stories.tsx   # a11y addon runs automatically
│   ├── Dialog/
│   │   ├── Dialog.tsx
│   │   ├── Dialog.test.tsx
│   │   └── useFocusTrap.ts      # focus management hook
│   └── SkipLink/
│       └── SkipLink.tsx
├── hooks/
│   ├── useAnnounce.ts           # live region hook
│   ├── useFocusReturn.ts        # return focus to trigger
│   └── useReducedMotion.ts      # prefers-reduced-motion
├── utils/
│   └── a11y.ts                  # shared a11y utilities
└── test/
    └── a11y-matchers.ts         # custom jest-axe setup
```

---

# 4. Accessibility Tooling Comparison

## Automated Testing Tools

| Tool | Type | Catches | CI Integration | Free | Best For |
|------|------|---------|---------------|------|----------|
| **axe-core / axe DevTools** | Engine + Browser extension | ~30% of WCAG issues | Yes (jest-axe, Playwright) | Core: free, DevTools: freemium | Component & page-level testing |
| **Lighthouse** | Audit tool (uses axe-core) | Same as axe + performance | Yes (Lighthouse CI) | Yes | Quick audits, CI budgets |
| **WAVE** | Browser extension | Similar to axe, visual overlay | No (web API available) | Yes | Visual accessibility review |
| **eslint-plugin-jsx-a11y** | Static analysis | Code-level issues at write time | Yes (ESLint) | Yes | Catching issues before runtime |
| **Storybook a11y addon** | Component-level (uses axe-core) | Per-component violations | Indirectly | Yes | Design system development |

## Screen Readers

| Screen Reader | Platform | Browser Pairing | Cost | Learning Curve | Market Share |
|--------------|----------|----------------|------|---------------|-------------|
| **NVDA** | Windows | Firefox, Chrome | Free | Medium | ~30% |
| **JAWS** | Windows | Chrome, Edge | ~$1000/yr | High | ~40% |
| **VoiceOver** | macOS, iOS | Safari | Free (built-in) | Medium | ~25% (mobile dominant) |
| **TalkBack** | Android | Chrome | Free (built-in) | Medium | Growing |

### When to Use What

- **Development time**: eslint-plugin-jsx-a11y (catches issues as you type)
- **Component development**: Storybook a11y addon (per-story checks)
- **Unit/integration tests**: jest-axe + Testing Library (role-based queries enforce semantics)
- **E2E tests**: @axe-core/playwright (full-page scans)
- **Manual testing**: VoiceOver + Safari, NVDA + Firefox (always required)
- **Quick audits**: Lighthouse, axe DevTools browser extension

---

# 5. Cheatsheet

## Semantic HTML Quick Reference

| Instead of | Use | Why |
|-----------|-----|-----|
| `<div onClick>` | `<button>` | Focusable, keyboard support, announced as button |
| `<div class="link">` | `<a href>` | Announced as link, keyboard activatable |
| `<div class="nav">` | `<nav>` | Creates navigation landmark |
| `<div class="header">` | `<header>` | Creates banner landmark |
| `<div class="main">` | `<main>` | Creates main landmark |
| `<span class="heading">` | `<h1>`–`<h6>` | Creates heading structure for navigation |
| `<div class="list">` | `<ul>` / `<ol>` | Screen reader announces "list, 5 items" |
| `<input>` without label | `<label>` + `<input>` | Associates label with input for AT |

## ARIA Quick Reference

| ARIA | Purpose | Example |
|------|---------|---------|
| `aria-label` | Provides accessible name | `<button aria-label="Close">×</button>` |
| `aria-labelledby` | References visible label element | `<div role="dialog" aria-labelledby="title-id">` |
| `aria-describedby` | Associates descriptive text | `<input aria-describedby="error-id">` |
| `aria-expanded` | Indicates expandable state | `<button aria-expanded="false">Menu</button>` |
| `aria-hidden="true"` | Hides from accessibility tree | `<span aria-hidden="true">★</span>` |
| `aria-live="polite"` | Announces content changes | `<div aria-live="polite">{status}</div>` |
| `aria-current="page"` | Indicates current page in nav | `<a aria-current="page" href="/">Home</a>` |
| `aria-required="true"` | Indicates required field | `<input aria-required="true">` |
| `aria-invalid="true"` | Indicates validation error | `<input aria-invalid="true" aria-describedby="err">` |
| `role="alert"` | Assertive live region | `<div role="alert">Error occurred</div>` |
| `role="status"` | Polite live region | `<div role="status">3 results found</div>` |

## Keyboard Interaction Patterns

| Widget | Keys | Behavior |
|--------|------|----------|
| Button | Enter, Space | Activate |
| Link | Enter | Navigate |
| Checkbox | Space | Toggle |
| Radio group | Arrow keys | Move selection |
| Tabs | Arrow keys | Switch tab; Tab moves to panel |
| Menu | Arrow keys, Enter, Escape | Navigate, select, close |
| Dialog | Tab (trapped), Escape | Navigate within, close |
| Combobox | Arrow keys, Enter, Escape | Navigate options, select, close |

## Focus Management Rules

```tsx
// 1. Move focus into modal on open
useEffect(() => {
  if (isOpen) dialogRef.current?.focus();
}, [isOpen]);

// 2. Return focus on close
const triggerRef = useRef<HTMLButtonElement>(null);
const handleClose = () => {
  setIsOpen(false);
  triggerRef.current?.focus();
};

// 3. Trap focus inside modal
const handleKeyDown = (e: KeyboardEvent) => {
  if (e.key === 'Tab') {
    const focusable = dialogRef.current?.querySelectorAll<HTMLElement>(
      'a[href], button, textarea, input, select, [tabindex]:not([tabindex="-1"])'
    );
    if (!focusable?.length) return;
    const first = focusable[0];
    const last = focusable[focusable.length - 1];
    if (e.shiftKey && document.activeElement === first) {
      e.preventDefault();
      last.focus();
    } else if (!e.shiftKey && document.activeElement === last) {
      e.preventDefault();
      first.focus();
    }
  }
  if (e.key === 'Escape') handleClose();
};
```

## Accessible Form Pattern

```tsx
const Form = () => {
  const nameId = useId();
  const nameErrorId = useId();
  const [error, setError] = useState('');

  return (
    <form noValidate onSubmit={handleSubmit}>
      <label htmlFor={nameId}>
        Name <span aria-hidden="true">*</span>
      </label>
      <input
        id={nameId}
        aria-required="true"
        aria-invalid={!!error}
        aria-describedby={error ? nameErrorId : undefined}
      />
      {error && (
        <p id={nameErrorId} role="alert">
          {error}
        </p>
      )}
      <button type="submit">Submit</button>
    </form>
  );
};
```

## Reduced Motion Pattern

```tsx
const useReducedMotion = () => {
  const [prefersReduced, setPrefersReduced] = useState(false);
  useEffect(() => {
    const mq = window.matchMedia('(prefers-reduced-motion: reduce)');
    setPrefersReduced(mq.matches);
    const handler = (e: MediaQueryListEvent) => setPrefersReduced(e.matches);
    mq.addEventListener('change', handler);
    return () => mq.removeEventListener('change', handler);
  }, []);
  return prefersReduced;
};
```

## Live Region Announcement Hook

```tsx
const useAnnounce = () => {
  const [message, setMessage] = useState('');
  const announce = useCallback((text: string) => {
    setMessage(''); // Clear first to re-trigger announcement
    requestAnimationFrame(() => setMessage(text));
  }, []);

  const Announcer = () => (
    <div aria-live="polite" aria-atomic="true" className="sr-only">
      {message}
    </div>
  );
  return { announce, Announcer };
};
```

## Visually Hidden (Screen Reader Only) CSS

```css
.sr-only {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  border: 0;
}
```

## Common Accessibility Testing Checklist

- [ ] All images have appropriate alt text
- [ ] All form inputs have associated labels
- [ ] Color contrast meets WCAG AA (4.5:1 / 3:1)
- [ ] Page has a single `<h1>` and logical heading hierarchy
- [ ] All interactive elements are keyboard accessible
- [ ] Focus is visible on all interactive elements
- [ ] Skip link exists and works
- [ ] Modals trap focus and restore focus on close
- [ ] Dynamic content changes are announced to screen readers
- [ ] Page works with 200% zoom
- [ ] Animations respect `prefers-reduced-motion`
- [ ] Page has proper `lang` attribute
- [ ] Page has descriptive `<title>`
- [ ] Error messages are associated with inputs and announced
- [ ] ARIA is used correctly (or not at all)

---

# 6. Real-World Engineering Mindset

## Modal Accessibility

**Problem:** Modals overlay the page but screen readers can still read background content. Keyboard users can tab out of the modal into hidden content.

**Implementation strategies:**

| Strategy | How | Pros | Cons |
|----------|-----|------|------|
| `aria-modal="true"` + `role="dialog"` | Browser hides background from AT | Clean, standard | Inconsistent screen reader support |
| `inert` attribute on background | Makes background non-interactive | Native, simple | Browser support still growing |
| Manual focus trap + `aria-hidden` on siblings | JS-managed containment | Works everywhere | Complex, fragile |
| `<dialog>` element (native) | Built-in modal behavior | Focus trap, Escape, top-layer | Styling limitations, older browser support |

**Senior engineer choice:** Use native `<dialog>` with `showModal()` for new projects. It provides focus trapping, Escape to close, top-layer rendering, and `inert` on background — all for free. Fall back to manual implementation only when `<dialog>` doesn't meet requirements.

## SPA Route Announcements

**Problem:** In SPAs, "page navigation" doesn't reload the page. Screen readers don't announce the new content. Users don't know the page changed.

**Strategies:**
1. **Live region announcement**: Announce new page title via `aria-live` region (Next.js does this)
2. **Focus management**: Move focus to new page's `<h1>` or `<main>` on route change
3. **Both**: Announce + move focus (most robust)

**Hidden pitfall:** If you move focus to a non-interactive element, you need `tabindex="-1"` on it. But then the focus outline appears on content, which can be visually jarring — use `:focus:not(:focus-visible)` to hide it.

## Toast Notifications

**Problem:** Toasts appear visually but screen readers may miss them entirely.

**Strategy:**
- Use `role="status"` (polite) for informational toasts
- Use `role="alert"` (assertive) ONLY for errors/urgent messages
- Never put interactive elements (links, buttons) inside toasts — screen reader users can't navigate to them quickly enough before the toast disappears
- If toast has actions, use a persistent notification region instead

## Infinite Scrolling Accessibility

**Problem:** Infinite scrolling removes pagination landmarks. Screen readers can't determine content length. Focus management is unclear. Users can't reach the footer.

**Senior engineer approach:**
- Provide a "Load more" button (not automatic loading)
- Announce loaded count: "Showing 20 of 156 results"
- Ensure footer remains reachable
- Provide alternative pagination option
- Move focus to first new item after loading

## Design Systems

**Problem:** If your design system components aren't accessible, every app using them inherits inaccessible patterns.

**Strategy:**
- **Every component has an accessibility spec** (keyboard interaction, ARIA, focus management)
- **Component APIs enforce accessibility** (required `label` props, built-in keyboard handlers)
- **Storybook a11y addon** runs on every story automatically
- **jest-axe** runs in component test suites
- **Documentation includes accessibility section** for every component

## Drag and Drop Accessibility

**Problem:** Drag and drop is inherently a pointer-based interaction. Keyboard and screen reader users are completely excluded.

**Strategy:**
- Provide keyboard alternatives (arrow keys to reorder, or a "Move" menu)
- Announce position changes: "Item 3, moved to position 1 of 5"
- Use `aria-roledescription="sortable"` for drag handles
- Announce drag start/end: "Grabbed Item 3", "Dropped Item 3, now position 1"
- Libraries like `@dnd-kit` have accessibility built in

---

# 7. Brainstorm / Open Questions

## Accessibility Architecture
1. How should a component API enforce accessibility without being overly restrictive?
2. Should accessible name be a required prop on every interactive component?
3. How do you handle accessibility in server components vs client components?
4. What accessibility guarantees should a design system provide to consuming teams?
5. How should accessibility work across micro-frontend boundaries?
6. When is it acceptable to use `aria-hidden` to simplify the accessibility tree?
7. How should you architect focus management in a multi-panel layout?
8. What is the right abstraction for a reusable focus trap hook?

## UX
9. How do you decide between `aria-live="polite"` and `aria-live="assertive"`?
10. Should error messages be announced immediately or on form submission?
11. How should loading states be communicated to screen reader users?
12. What is the right keyboard interaction model for a data grid?
13. How do you make drag-and-drop accessible without degrading the experience?
14. When should you auto-focus and when is auto-focus harmful?
15. How do you handle complex tooltips that need to be interactive?
16. Should skeleton screens be announced to screen readers?

## Performance
17. Does ARIA processing impact rendering performance?
18. How do rapid React re-renders affect live region announcements?
19. What is the accessibility cost of lazy loading content?
20. How does virtualized scrolling affect screen reader navigation?
21. When does animation become an accessibility hazard?
22. How should you handle long lists — virtualization vs pagination for AT users?
23. What is the performance impact of large accessibility trees?
24. How does concurrent React rendering interact with screen reader announcements?

## Assistive Technology Behavior
25. Why do NVDA and VoiceOver behave differently with `aria-live` regions?
26. How does VoiceOver's rotor differ from NVDA's elements list?
27. What happens when screen readers switch between browse mode and forms mode?
28. How do screen readers handle `role="application"`?
29. Why might a screen reader ignore your `aria-label`?
30. How do braille displays interpret ARIA?
31. What accessibility issues arise with shadow DOM?
32. How do screen readers handle iframes?

## Design Systems
33. How do you version accessibility APIs in a design system?
34. Should design system components allow ARIA prop overrides?
35. How do you test a design system component across multiple screen readers?
36. What accessibility documentation should accompany every component?
37. How do you handle accessibility when wrapping third-party components?
38. Should design tokens include accessibility metadata (contrast ratios)?
39. How do you enforce heading hierarchy across composed pages?
40. What is the right testing strategy for composite components (combobox, data table)?

## Product Trade-offs
41. How do you prioritize accessibility fixes — what's critical vs nice-to-have?
42. Should you delay a feature launch for accessibility compliance?
43. How do you handle third-party widgets that aren't accessible?
44. What is the business case for WCAG AAA compliance?
45. When is "good enough" accessibility actually good enough?
46. How do you communicate accessibility risk to product managers?
47. What accessibility compromises exist in common design patterns?
48. How do you handle A/B tests that may introduce accessibility regressions?

## Testing Strategy
49. What percentage of accessibility issues can automated tools catch?
50. How do you set up accessibility regression testing in CI?
51. When should you test with real screen readers vs automated tools?
52. How do you write meaningful accessibility test assertions?
53. Should accessibility tests be unit tests, integration tests, or E2E tests?
54. How do you test focus management in React Testing Library?
55. What is the right cadence for manual accessibility audits?
56. How do you test color contrast dynamically (dark mode, themes)?

## Enterprise Accessibility
57. How should accessibility ownership be structured in an organization?
58. What is a VPAT and when do you need one?
59. How do you track accessibility debt?
60. What is the cost of NOT building accessibility from the start?
61. How do you train developers who have never used a screen reader?
62. What metrics should you track for accessibility program maturity?
63. How do you handle accessibility across multiple brands and white-label products?
64. What regulatory requirements differ across regions (ADA, EAA, AODA)?

---

# 8. Practice Questions

## Beginner (20 Questions)

### Q1
**Question:** What is the correct HTML element for a clickable action that does NOT navigate to a new page?
**Type:** Single choice
**Options:** A) `<a href="#">` B) `<div onClick>` C) `<button>` D) `<span role="button">`
**Answer:** C
**Why:** `<button>` is natively focusable, activatable via Enter/Space, and announced as "button" by screen readers. All others require additional work to match this behavior.

### Q2
**Question:** True or False: `alt=""` (empty alt) should be used for decorative images.
**Type:** True/False
**Answer:** True
**Why:** Empty `alt` tells screen readers to skip the image entirely. Without `alt`, the screen reader may read the filename instead (e.g., "IMG_3847.jpg").

### Q3
**Question:** Which of these conveys meaning using color alone and violates WCAG?
**Type:** Single choice
**Options:** A) Red border + error icon + error text B) Red border only C) Red border + error text D) Error icon + error text
**Answer:** B
**Why:** Red border alone relies solely on color to convey the error state. Users who can't perceive color (colorblind, low vision) won't understand the meaning.

### Q4
**Question:** What is the minimum color contrast ratio for normal text under WCAG AA?
**Type:** Single choice
**Options:** A) 2:1 B) 3:1 C) 4.5:1 D) 7:1
**Answer:** C
**Why:** WCAG AA requires 4.5:1 for normal text, 3:1 for large text (18pt or 14pt bold). 7:1 is AAA level.

### Q5
**Question:** What is the purpose of the `<label>` element?
**Type:** Fill in the blank
**Answer:** The `<label>` element creates a programmatic association between a text description and a form input, so screen readers can announce what the input is for, and clicking the label focuses/activates the input.

### Q6
**Question:** What does `tabindex="0"` do?
**Type:** Single choice
**Options:** A) Removes element from tab order B) Adds element to natural tab order C) Makes element the first in tab order D) Makes element unfocusable
**Answer:** B
**Why:** `tabindex="0"` places the element in the tab order at its DOM position. `tabindex="-1"` makes it programmatically focusable only. Positive `tabindex` is an anti-pattern.

### Q7
**Question:** Which HTML element creates a landmark that screen readers can jump to for the main content?
**Type:** Single choice
**Options:** A) `<div id="main">` B) `<section>` C) `<main>` D) `<article>`
**Answer:** C
**Why:** `<main>` creates a "main" landmark in the accessibility tree. Screen readers allow users to jump directly to it. `<div>` creates no landmark regardless of its id.

### Q8
**Question:** True or False: Placeholder text is an acceptable replacement for a form label.
**Type:** True/False
**Answer:** False
**Why:** Placeholder text disappears when the user types, has low contrast by default, and is not consistently exposed to assistive technologies as a label.

### Q9
**Question:** What key combination should activate a `<button>`?
**Type:** Multiple choice
**Options:** A) Enter B) Space C) Tab D) Arrow keys
**Answer:** A, B
**Why:** Native `<button>` elements are activated by both Enter and Space. Tab moves focus. Arrow keys are for composite widgets.

### Q10
**Question:** What is a "skip link"?
**Type:** Fill in the blank
**Answer:** A skip link is a visually hidden (until focused) link at the top of the page that lets keyboard users bypass navigation and jump directly to the main content.

### Q11
**Question:** What does `aria-hidden="true"` do?
**Type:** Single choice
**Options:** A) Visually hides the element B) Removes the element from the accessibility tree C) Prevents keyboard focus D) Both B and C
**Answer:** B
**Why:** `aria-hidden="true"` removes the element from the accessibility tree but does NOT prevent keyboard focus or visual display. If a focusable element is inside `aria-hidden`, screen reader users can focus it but can't perceive it — a dangerous trap.

### Q12
**Question:** Match the HTML element to its implicit ARIA role.
**Type:** Matching
| Element | Role |
|---------|------|
| `<nav>` | navigation |
| `<main>` | main |
| `<button>` | button |
| `<a href>` | link |
| `<header>` | banner (when top-level) |
| `<footer>` | contentinfo (when top-level) |

### Q13
**Question:** True or False: Screen readers can read content styled with `display: none`.
**Type:** True/False
**Answer:** False
**Why:** `display: none` removes the element from both the visual layout and the accessibility tree. Use the `.sr-only` pattern to hide content visually while keeping it accessible.

### Q14
**Question:** What is wrong with this code? `<a href="#" onClick={handleSave}>Save</a>`
**Type:** Scenario
**Answer:** A link (`<a>`) should navigate to a URL. "Save" is an action, not navigation. This should be a `<button>`. Using `<a>` here announces "Save, link" to screen readers, misleading users into expecting navigation.

### Q15
**Question:** Which attribute associates an error message with an input field for screen readers?
**Type:** Single choice
**Options:** A) `aria-label` B) `aria-describedby` C) `aria-errormessage` D) `aria-invalid`
**Answer:** B
**Why:** `aria-describedby` associates additional descriptive text (including errors) with the input. `aria-invalid` marks the field as invalid but doesn't associate the error text. `aria-errormessage` exists but has limited support.

### Q16
**Question:** What heading level should follow an `<h2>`?
**Type:** Single choice
**Options:** A) Only `<h3>` B) `<h3>` or another `<h2>` C) Any heading level D) `<h4>`
**Answer:** B
**Why:** Headings should not skip levels going down (h2 → h4 is wrong). But you can have sibling headings at the same level (h2 → h2) or go to a child level (h2 → h3).

### Q17
**Question:** True or False: Adding `role="button"` to a `<div>` makes it fully accessible as a button.
**Type:** True/False
**Answer:** False
**Why:** `role="button"` only changes the announcement. You still need `tabindex="0"`, `onKeyDown` for Enter/Space, and focus styles. Use `<button>` instead.

### Q18
**Question:** What is the purpose of the `lang` attribute on `<html>`?
**Type:** Fill in the blank
**Answer:** The `lang` attribute tells screen readers which language to use for pronunciation. Without it, a screen reader might read French text with English pronunciation rules.

### Q19
**Question:** Which CSS property, when set to `none`, removes the visible focus indicator?
**Type:** Single choice
**Options:** A) `border` B) `outline` C) `visibility` D) `opacity`
**Answer:** B
**Why:** `outline: none` removes the default browser focus indicator. This makes it impossible for keyboard users to see where focus is. Always provide an alternative visible focus style.

### Q20
**Question:** What is the correct `alt` text for a company logo that also serves as a link to the homepage?
**Type:** Scenario
**Answer:** `alt="CompanyName homepage"` or `alt="CompanyName - Go to homepage"`. The alt text should describe the function (navigating home), not the appearance ("blue square logo").

---

## Junior (20 Questions)

### Q21
**Question:** What is the difference between `aria-live="polite"` and `aria-live="assertive"`?
**Type:** Fill in the blank
**Answer:** `polite` waits until the screen reader finishes its current announcement before reading the new content. `assertive` interrupts the current announcement immediately. Use `assertive` only for critical alerts.

### Q22
**Question:** Your modal opens but screen reader users can still read the background page content. What should you do?
**Type:** Scenario
**Answer:** Add `aria-modal="true"` to the dialog, and either use the `inert` attribute on background content or add `aria-hidden="true"` to sibling elements of the modal. Better yet, use the native `<dialog>` element with `showModal()`.

### Q23
**Question:** True or False: Every ARIA role requires an accessible name.
**Type:** True/False
**Answer:** False
**Why:** Some roles (like `presentation` or `none`) explicitly strip semantics. Landmark roles and interactive widget roles do require accessible names, but not every role does.

### Q24
**Question:** What is a focus trap and when should you use one?
**Type:** Fill in the blank
**Answer:** A focus trap confines Tab/Shift+Tab cycling within a specific container (like a modal dialog), preventing focus from escaping to background content. Use it for modals, dialogs, and flyout panels while they are open.

### Q25
**Question:** Which ARIA attribute should you toggle when a dropdown menu opens?
**Type:** Single choice
**Options:** A) `aria-pressed` B) `aria-expanded` C) `aria-selected` D) `aria-checked`
**Answer:** B
**Why:** `aria-expanded` indicates that a triggering element controls the visibility of another element. The trigger button should have `aria-expanded="false"` when closed and `aria-expanded="true"` when open.

### Q26
**Question:** You have a list of tabs. What keyboard interaction model should users expect?
**Type:** Scenario
**Answer:** Arrow left/right to move between tabs. Tab key moves focus from the tab list into the tab panel. The focused tab is activated (either on focus or on Enter/Space, depending on activation mode). Home/End go to first/last tab.

### Q27
**Question:** What is the first rule of ARIA?
**Type:** Fill in the blank
**Answer:** Don't use ARIA if you can use native HTML instead. Native HTML elements (`<button>`, `<input>`, `<select>`, `<a>`, `<dialog>`) have built-in accessibility, keyboard support, and consistent behavior that ARIA cannot fully replicate.

### Q28
**Question:** Your React app navigates to a new page via client-side routing. Screen reader users don't know the page changed. What's wrong?
**Type:** Scenario
**Answer:** SPAs don't trigger a page load, so screen readers don't announce the new page. You need to: 1) announce the new page title via an `aria-live` region, 2) move focus to the page's `<h1>` or `<main>`, and 3) update `document.title`. Next.js has a built-in `<RouteAnnouncer>` for this.

### Q29
**Question:** What is `aria-describedby` and how does it differ from `aria-labelledby`?
**Type:** Fill in the blank
**Answer:** `aria-labelledby` provides the primary accessible name (what the element IS). `aria-describedby` provides supplementary description (additional context). Screen readers typically announce the label first, then the description after a pause.

### Q30
**Question:** True or False: `role="alert"` is the same as `aria-live="assertive"`.
**Type:** True/False
**Answer:** Mostly true, with nuance.
**Why:** `role="alert"` implicitly sets `aria-live="assertive"` and `aria-atomic="true"`. But `role="alert"` also has specific semantics — screen readers may prefix the announcement with "Alert:". They are functionally similar but semantically different.

### Q31
**Question:** What is wrong with this pattern? `<div role="button" tabindex="0">Submit</div>`
**Type:** Scenario
**Answer:** While it's focusable and announced as "button", it's missing: 1) `onKeyDown` handler for Enter and Space, 2) no native form submission, 3) no disabled state handling. Just use `<button type="submit">Submit</button>`.

### Q32
**Question:** What does `aria-controls` do, and does it actually work in screen readers?
**Type:** Fill in the blank
**Answer:** `aria-controls` declares a relationship between a trigger and the element it controls (e.g., a button that opens a dropdown). However, screen reader support for `aria-controls` is inconsistent — JAWS supports it, but NVDA and VoiceOver largely ignore it. Use it for correctness, but don't rely on it as the only mechanism.

### Q33
**Question:** You build a custom `<Select>` component. What minimum accessibility requirements must it meet?
**Type:** Scenario
**Answer:** 1) `role="combobox"` or `role="listbox"` with proper structure, 2) Arrow key navigation, 3) Enter to select, 4) Escape to close, 5) Type-ahead search, 6) `aria-expanded`, `aria-activedescendant`, `aria-selected`, 7) Announce selected value, 8) Focus management. OR: just use native `<select>` whenever possible.

### Q34
**Question:** What is `aria-atomic` and when do you need it?
**Type:** Single choice
**Options:** A) Makes an element non-interactive B) Controls whether the entire live region is re-announced on change C) Makes an element invisible D) Prevents focus
**Answer:** B
**Why:** When `aria-atomic="true"`, the entire live region content is re-announced when any part changes. When `false` (default for `aria-live`), only the changed nodes are announced.

### Q35
**Question:** How should error messages be handled in an accessible form?
**Type:** Scenario
**Answer:** 1) Set `aria-invalid="true"` on the invalid input, 2) Associate the error message via `aria-describedby`, 3) Use `role="alert"` or `aria-live` to announce the error, 4) Move focus to the first invalid field (on form submission), 5) Provide clear, actionable error text.

### Q36
**Question:** What is the difference between `display: none`, `visibility: hidden`, and the `.sr-only` pattern?
**Type:** Matching

| Technique | Visual | Accessibility Tree | Focus |
|-----------|--------|-------------------|-------|
| `display: none` | Hidden | Removed | Not focusable |
| `visibility: hidden` | Hidden | Removed | Not focusable |
| `.sr-only` (clip pattern) | Hidden | Present | Focusable |
| `aria-hidden="true"` | Visible | Removed | Still focusable (danger!) |

### Q37
**Question:** True or False: Screen readers always read content in DOM order, not visual order.
**Type:** True/False
**Answer:** True
**Why:** Screen readers follow DOM order, not CSS visual order. CSS flexbox `order`, CSS Grid placement, and `position: absolute` can create visual order that differs from DOM order, confusing screen reader users.

### Q38
**Question:** What is `aria-roledescription` and when would you use it?
**Type:** Fill in the blank
**Answer:** `aria-roledescription` overrides the screen reader's default role announcement. For example, `role="region" aria-roledescription="slide"` would announce "slide" instead of "region". Use it sparingly — only when the default role name doesn't match user expectations.

### Q39
**Question:** Your live region isn't being announced by the screen reader. What should you investigate?
**Type:** Scenario
**Answer:** 1) Is the live region in the DOM BEFORE content changes? (It must be present on initial render), 2) Are you replacing the entire element or just the text content? (Replacing elements may not trigger announcements), 3) Is `aria-atomic` set correctly?, 4) Is the content actually changing? (Setting the same text won't trigger), 5) Are you updating too rapidly? (Screen readers may skip rapid changes).

### Q40
**Question:** What is the purpose of `aria-current`?
**Type:** Single choice
**Options:** A) Marks the currently focused element B) Marks the current item in a set (e.g., current page in nav) C) Marks the currently active tab D) All of the above
**Answer:** B
**Why:** `aria-current` indicates the current item within a set of related elements. Common values: `page` (current page in nav), `step` (current step in a wizard), `date` (current date in a calendar). It's different from focus or selection.

---

## Senior / Expert (20 Questions)

### Q41
**Question:** How does the accessible name computation algorithm work?
**Type:** Fill in the blank
**Answer:** Browsers resolve accessible names in this priority order: 1) `aria-labelledby` (references another element's text), 2) `aria-label` (inline string), 3) Native labeling (`<label>`, `alt`, `<caption>`, `<legend>`), 4) Text content (for elements like `<button>`), 5) `title` attribute, 6) `placeholder` (last resort, only for inputs). The first non-empty result wins.

### Q42
**Question:** Your team uses React concurrent features (Suspense, transitions). What accessibility concerns arise?
**Type:** Scenario
**Answer:** 1) Suspense boundaries show fallback UI — screen readers may announce the fallback and then the resolved content, causing confusion. 2) `startTransition` defers updates — live region announcements may be delayed or lost. 3) Streaming SSR can send partial HTML — ARIA relationships (`aria-labelledby`, `aria-describedby`) may reference elements that haven't loaded yet. 4) Rapid state transitions may swallow announcements.

### Q43
**Question:** True or False: Automated accessibility testing tools can catch the majority of WCAG violations.
**Type:** True/False
**Answer:** False
**Why:** Studies consistently show automated tools catch approximately 30–40% of WCAG violations. Issues like logical reading order, meaningful alt text quality, keyboard interaction correctness, and cognitive accessibility require manual testing.

### Q44
**Question:** Explain the difference between browse mode and forms/application mode in screen readers.
**Type:** Fill in the blank
**Answer:** In **browse mode** (default), screen readers intercept all keystrokes to provide navigation shortcuts (H for headings, K for links, etc.). In **forms/application mode**, keystrokes pass through to the web app. Screen readers switch to forms mode when focus enters a form control. `role="application"` forces application mode for its entire subtree — this is almost always wrong because it disables all screen reader navigation shortcuts.

### Q45
**Question:** Your design system's Button component is used in 200+ places across 15 apps. You discover the keyboard interaction doesn't handle Space correctly in Safari. How do you approach the fix?
**Type:** Scenario
**Answer:** 1) Confirm the bug (Safari doesn't fire `click` on Space for `<button>` in some contexts — actually it does natively, but custom handlers may break it). 2) Fix in the design system component, not in consuming apps. 3) Add a regression test with `fireEvent.keyDown(button, { key: ' ' })`. 4) Add cross-browser a11y tests to CI. 5) Release a patch version. 6) This illustrates why accessibility belongs in the design system — one fix propagates everywhere.

### Q46
**Question:** What are the accessibility implications of CSS `content-visibility: auto`?
**Type:** Fill in the blank
**Answer:** `content-visibility: auto` skips rendering of off-screen content for performance. However, screen readers may not be able to access content that isn't rendered. This means screen reader users might not be able to find content via heading navigation, search, or the elements list. The content is also excluded from find-in-page. Use with caution and test with screen readers.

### Q47
**Question:** How should you architect accessibility in a micro-frontend system where each fragment is independently deployed?
**Type:** Scenario
**Answer:** Challenges: 1) Focus management across fragment boundaries, 2) Single heading hierarchy across fragments, 3) Landmark structure must be coordinated, 4) Skip links need to work across fragments, 5) Live region announcements may conflict. Solutions: Use a shell/host that owns the page-level accessibility structure (landmarks, skip links, heading hierarchy). Each fragment owns its internal accessibility. Define accessibility contracts between fragments.

### Q48
**Question:** What is `aria-activedescendant` and why is it critical for combobox/listbox patterns?
**Type:** Fill in the blank
**Answer:** `aria-activedescendant` allows a composite widget (like a combobox) to keep DOM focus on the input while visually and semantically indicating which option is "active" in the list. The input remains focused (so the user can type), but `aria-activedescendant` points to the id of the currently highlighted option. Screen readers announce the active option without moving DOM focus.

### Q49
**Question:** You need to make an interactive data visualization (chart) accessible. What strategies exist?
**Type:** Scenario
**Answer:** 1) **Text alternative**: Provide a summary/description of the chart's key insights, 2) **Data table**: Provide an accessible `<table>` with the same data, toggleable via a button, 3) **Keyboard navigation**: Allow arrow keys to navigate data points, announcing values, 4) **Sonification**: Audio representations of data trends, 5) **ARIA**: `role="img"` with `aria-label` for simple charts; `role="graphics-document"` for complex ones. The best approach combines a text summary + data table alternative.

### Q50
**Question:** What is the WCAG principle "Robust" and why does it matter for React applications?
**Type:** Fill in the blank
**Answer:** "Robust" (WCAG Principle 4) means content must be robust enough to be interpreted reliably by a wide variety of user agents, including assistive technologies. For React: 1) Valid HTML output matters (React can produce invalid HTML via portals, fragments, and incorrect nesting), 2) ARIA attributes must be valid, 3) Custom components must map to correct roles, 4) The app must work across different screen readers and browsers.

### Q51
**Question:** How does SSR hydration affect accessibility?
**Type:** Scenario
**Answer:** 1) Server-rendered HTML is immediately accessible — screen readers can read it before JS loads, 2) During hydration, React attaches event handlers — there's a window where interactive elements look clickable but aren't functional, 3) If hydration changes the DOM structure (mismatch), ARIA relationships can break, 4) `useId()` ensures consistent IDs between server and client for label associations, 5) Progressive enhancement means the page should be navigable even if JS fails.

### Q52
**Question:** Your CI pipeline runs axe-core and passes, but users report accessibility issues. What's happening?
**Type:** Scenario
**Answer:** Axe-core catches ~30% of issues. Common misses: 1) Logical reading order (visual vs DOM mismatch), 2) Quality of alt text (axe checks existence, not quality), 3) Keyboard interaction correctness (axe doesn't test keyboard flows), 4) Focus management (axe doesn't test focus behavior), 5) Screen reader announcements (axe doesn't use a screen reader), 6) Cognitive accessibility (clear language, predictable patterns). Solution: Automated testing is necessary but not sufficient — add manual testing, screen reader testing, and accessibility audit cadence.

### Q53
**Question:** What is the difference between WCAG 2.1 and WCAG 2.2, and what new criteria were added?
**Type:** Fill in the blank
**Answer:** WCAG 2.2 (2023) added: 1) **Focus Not Obscured (Minimum)** — focused element must not be entirely hidden by other content, 2) **Dragging Movements** — drag actions must have non-dragging alternatives, 3) **Target Size (Minimum)** — interactive targets must be at least 24×24 CSS pixels, 4) **Consistent Help** — help mechanisms must be in consistent locations, 5) **Redundant Entry** — don't ask users to re-enter information already provided. WCAG 2.2 also removed 4.1.1 Parsing.

### Q54
**Question:** How would you implement an accessible combobox following WAI-ARIA APG?
**Type:** Scenario
**Answer:** Key requirements: 1) `role="combobox"` on the input, 2) `aria-expanded` to indicate popup state, 3) `aria-controls` pointing to the listbox, 4) `role="listbox"` on the options container, 5) `role="option"` on each option, 6) `aria-activedescendant` on the input pointing to the highlighted option, 7) Arrow keys to navigate options, 8) Enter to select, 9) Escape to close, 10) Type-ahead filtering, 11) Announce result count changes via live region. This is one of the most complex ARIA patterns — consider using a library like Downshift or React Aria.

### Q55
**Question:** What is `inert` and how does it solve modal accessibility?
**Type:** Fill in the blank
**Answer:** The `inert` attribute makes an element and all its descendants non-interactive and invisible to assistive technologies. For modals: instead of manually adding `aria-hidden="true"` to all sibling content and managing focus traps, you can add `inert` to the `<main>` content behind the modal. The native `<dialog>` element with `showModal()` applies `inert` to background content automatically.

### Q56
**Question:** True or False: `role="presentation"` and `role="none"` are functionally identical.
**Type:** True/False
**Answer:** True
**Why:** `role="none"` was introduced as an alias for `role="presentation"` because the name is clearer. Both strip the element's implicit role from the accessibility tree. However, if the element is focusable or has ARIA attributes, the role is ignored (the "presentational role conflict resolution").

### Q57
**Question:** How should you handle accessibility for dynamically loaded content behind "infinite scroll"?
**Type:** Scenario
**Answer:** 1) Replace infinite scroll with "Load more" button — gives users control, 2) Announce new content count: "10 more items loaded, 30 total", 3) Don't move focus — let users choose when to explore new content, 4) Provide a link to skip to the end/footer, 5) If using virtualized list, ensure items remain in the accessibility tree (or provide alternatives), 6) Add `role="feed"` with `aria-busy` during loading for proper semantics.

### Q58
**Question:** What accessibility issues arise with React portals?
**Type:** Scenario
**Answer:** 1) DOM order differs from visual order — screen readers read content in DOM order, but portals are rendered at the end of `<body>`, 2) `aria-labelledby` / `aria-describedby` references may break across portal boundaries in some browsers, 3) Focus management must be explicitly handled — portals don't automatically trap or manage focus, 4) Landmark structure — portal content is outside the normal document flow, potentially outside `<main>`, 5) Tab order follows DOM, not visual layout.

### Q59
**Question:** An enterprise client requires a VPAT (Voluntary Product Accessibility Template). What is your approach?
**Type:** Scenario
**Answer:** 1) Run comprehensive automated scans (axe, Lighthouse) across all pages/states, 2) Conduct manual audit against all WCAG 2.1 AA success criteria, 3) Test with multiple screen readers (NVDA + Chrome, VoiceOver + Safari), 4) Document conformance level for each criterion (Supports, Partially Supports, Does Not Support, Not Applicable), 5) Include remarks explaining exceptions and remediation plans, 6) VPAT follows the ITI template format, 7) Plan for annual re-evaluation, 8) Budget for 40–80 hours of audit work depending on app complexity.

### Q60
**Question:** What is the "accessibility object model" (AOM) and why does it matter for the future of web accessibility?
**Type:** Fill in the blank
**Answer:** AOM is a proposed set of APIs that would allow JavaScript to directly interact with the accessibility tree, bypassing the need for ARIA attributes in HTML. Benefits: 1) Set accessibility properties without polluting HTML, 2) React to screen reader actions (e.g., increment/decrement), 3) Virtual accessibility nodes for canvas/WebGL rendering, 4) Better performance than DOM attribute updates. Status: partially implemented in browsers, still evolving. It would fundamentally change how frameworks handle accessibility.

---

# 9. Personalized Recommendations

## For Your Stack (React, Next.js, Astro, TypeScript)

### Most Important Concepts to Master First
1. **Semantic HTML** — you probably use more `<div>`s than necessary. Audit your components.
2. **Keyboard navigation** — tab through your apps weekly. Fix what's broken.
3. **Focus management in SPAs** — route changes, modals, dynamic content. This is where React apps fail most.
4. **Screen reader testing** — spend 30 minutes with VoiceOver. It will change how you write components.
5. **Accessible forms** — labels, errors, validation. Every app has forms.

### Common Mistakes Frontend Engineers Make
1. Using CSS to communicate meaning (hidden labels replaced by icons)
2. Building custom controls when native HTML works
3. Testing only with automated tools, never with keyboard/screen reader
4. Treating accessibility as a separate task rather than a quality attribute
5. Over-using ARIA instead of fixing semantic HTML
6. Ignoring focus management in client-side routing
7. Not testing with zoom (200%) and reflow

### Tooling Best Fits for Your Stack
- **eslint-plugin-jsx-a11y** — catches issues at write time in React/Next.js
- **@testing-library/react** — queries by role enforce semantics
- **jest-axe** — component-level automated checks
- **@axe-core/playwright** — E2E accessibility scans
- **Storybook a11y addon** — if you use Storybook for component development
- **VoiceOver** — built into macOS, no setup needed

### 30-Day Learning Plan

| Week | Focus | Milestone |
|------|-------|-----------|
| **Week 1** | Semantic HTML + keyboard navigation | Tab through 3 of your apps, fix all keyboard issues |
| **Week 2** | ARIA basics + focus management | Build an accessible modal and accordion from scratch |
| **Week 3** | Screen reader testing + automated testing | Set up jest-axe in a project, test with VoiceOver for 1 hour |
| **Week 4** | Forms + live regions + SPA routing | Build an accessible form with validation, add route announcements to a Next.js app |

### Evolution Path

```
Small workspace               → Platform-scale accessibility
──────────────────────────────────────────────────────────────
Fix obvious issues (alt, labels, contrast)
  → Add keyboard support to all components
    → Build accessible components from scratch
      → Master ARIA patterns (APG)
        → Set up automated a11y testing in CI
          → Build accessibility into design system
            → Define accessibility contracts across teams
              → Run accessibility audits and VPAT process
                → Accessibility architecture across org
```

---

# 10. Official Documentation & Reference Links

## Beginner
- [MDN Web Accessibility](https://developer.mozilla.org/en-US/docs/Web/Accessibility) — best starting point
- [The A11Y Project](https://www.a11yproject.com) — community-driven checklist and resources
- [WebAIM Introduction to Accessibility](https://webaim.org/intro/) — clear fundamentals
- [MDN ARIA Basics](https://developer.mozilla.org/en-US/docs/Learn/Accessibility/WAI-ARIA_basics)

## Intermediate
- [WAI-ARIA Authoring Practices Guide (APG)](https://www.w3.org/WAI/ARIA/apg/) — **essential** — keyboard patterns and ARIA for every widget type
- [React Accessibility Docs](https://react.dev/reference/react-dom/components/common#accessibility)
- [WebAIM Contrast Checker](https://webaim.org/resources/contrastchecker/)
- [Deque University](https://dequeuniversity.com) — structured accessibility training
- [Inclusive Components by Heydon Pickering](https://inclusive-components.design/) — practical component patterns
- [eslint-plugin-jsx-a11y](https://github.com/jsx-eslint/eslint-plugin-jsx-a11y)
- [Testing Library — ByRole queries](https://testing-library.com/docs/queries/byrole/)

## Advanced
- [WCAG 2.1 Specification](https://www.w3.org/TR/WCAG21/)
- [WCAG 2.2 Specification](https://www.w3.org/TR/WCAG22/)
- [Accessible Name and Description Computation](https://www.w3.org/TR/accname-1.1/)
- [ARIA 1.2 Specification](https://www.w3.org/TR/wai-aria-1.2/)
- [HTML AAM (Accessibility API Mappings)](https://www.w3.org/TR/html-aam-1.0/) — how HTML maps to platform accessibility APIs
- [Adrian Roselli's Blog](https://adrianroselli.com) — expert-level accessibility analysis
- [Scott O'Hara's Blog](https://www.scottohara.me) — deep ARIA and assistive technology research
- [Marcy Sutton's Work](https://marcysutton.com) — accessibility engineering and testing

## Expert / Assistive Technologies
- [W3C WAI Resources](https://www.w3.org/WAI/)
- [Accessibility Object Model (AOM) Explainer](https://wicg.github.io/aom/explainer.html)
- [NVDA User Guide](https://www.nvaccess.org/files/nvda/documentation/userGuide.html)
- [VoiceOver User Guide](https://support.apple.com/guide/voiceover/welcome/mac)
- [Deque axe-core Rules](https://github.com/dequelabs/axe-core/blob/develop/doc/rule-descriptions.md)
- [React Aria (Adobe)](https://react-spectrum.adobe.com/react-aria/) — production-grade accessible component hooks
- [Radix UI Primitives](https://www.radix-ui.com/primitives) — accessible unstyled components
- [GOV.UK Design System](https://design-system.service.gov.uk/) — exemplary accessibility in practice

## Case Studies & Talks
- [How GitHub Does Accessibility](https://github.blog/engineering/user-experience/improving-github-accessibility/)
- [Accessibility at Spotify](https://engineering.atspotify.com)
- [Léonie Watson's Talks](https://tink.uk) — screen reader user and accessibility expert
- [Accessibility in SPAs (Marcy Sutton)](https://www.youtube.com/results?search_query=marcy+sutton+accessibility+spa)

---

# 11. Advanced Engineering Topics

## Accessibility Trees — Deep Dive

The accessibility tree is a parallel representation of the DOM that browsers expose to assistive technologies via platform accessibility APIs:

| Platform | API |
|----------|-----|
| Windows | UI Automation (UIA), MSAA/IAccessible2 |
| macOS/iOS | NSAccessibility / AX API |
| Linux | ATK/AT-SPI |

Each node in the tree has: **role**, **name**, **state**, **value**, **description**, **relationships**. Browsers compute these from HTML semantics + ARIA attributes.

**Chrome DevTools → Elements → Accessibility pane** shows you the computed accessibility tree for any element.

## React Rendering and Accessibility Timing

React's reconciliation affects accessibility:
- **State updates** that change ARIA attributes are batched — screen readers may see intermediate states
- **useEffect** runs after paint — if you move focus in useEffect, there's a frame where focus hasn't moved yet
- **Concurrent features** (Suspense, transitions) can delay or split rendering, causing ARIA relationships to temporarily break
- **StrictMode** double-invokes effects in development, which can confuse live region announcements during testing

## SSR Hydration Accessibility Concerns

1. Server-rendered HTML is immediately accessible — screen readers can navigate it before JS loads
2. Interactive elements in server HTML that require JS handlers have a "dead zone" during hydration
3. `useId()` (React 18+) generates stable IDs across server/client for label associations
4. If hydration adds/removes DOM nodes, `aria-labelledby` references can break
5. Progressive enhancement: ensure core content is navigable without JS

## Accessibility Debt Management

Accessibility debt accumulates silently:
- Track accessibility issues in the same system as bugs (not a separate backlog)
- Categorize by WCAG level (A = critical, AA = standard, AAA = aspirational)
- Prioritize by user impact: can users complete core tasks?
- Add accessibility checks to PR review checklist
- Run quarterly accessibility audits
- Track % of components with accessibility tests

## Inclusive Design Systems

An accessible design system should:
1. **Enforce accessibility in component APIs** (required `label`, built-in keyboard handlers)
2. **Document keyboard interaction model** for every component
3. **Include focus management utilities** (useFocusTrap, useFocusReturn, useAnnounce)
4. **Ship with accessibility tests** (jest-axe for every component)
5. **Provide accessibility guidelines** in documentation alongside visual examples
6. **Version accessibility contracts** — changing keyboard behavior is a breaking change
7. **Test across screen readers** as part of the release process

---

# Summary

Accessibility is not a checklist — it is a **quality attribute** like performance or security. It must be designed in, built in, tested for, and maintained continuously.

**Key takeaways:**
1. Start with semantic HTML — it solves 50%+ of accessibility for free
2. Keyboard testing is the highest-ROI accessibility practice
3. Automated tools catch ~30% of issues — manual testing is essential
4. ARIA is powerful but dangerous — use it to enhance, not replace, native HTML
5. Focus management is the hardest accessibility problem in SPAs
6. Accessibility belongs in the design system, not in each consuming app
7. Screen reader testing with VoiceOver takes 30 minutes to learn and transforms your understanding

## Next Steps
1. Tab through your current project — document what's broken
2. Set up eslint-plugin-jsx-a11y and jest-axe
3. Spend 30 minutes with VoiceOver navigating your app
4. Build one accessible modal from scratch
5. Read WAI-ARIA Authoring Practices Guide for your most common component patterns

## Advanced Topics to Continue Later
- Accessibility Object Model (AOM)
- Canvas/WebGL accessibility
- Voice control accessibility
- Cognitive accessibility and WCAG 2.2
- International accessibility regulations (EAA, EN 301 549)
- Accessibility in native apps vs web
- AI-generated content accessibility
- Accessibility metrics and organizational maturity models
