# React Core — Complete Deep-Dive Engineering Guide

> For a frontend engineer moving from "React developer" into senior frontend engineer, React architecture expert, framework-level thinker, and performance-focused engineer.

---

## Table of Contents

- [1. Big Picture](#1-big-picture)
- [2. Learning Roadmap by Skill Level](#2-learning-roadmap-by-skill-level)
- [3. Setup Guide](#3-setup-guide)
- [4. Cheatsheet](#4-cheatsheet)
- [5. Real-World Engineering Mindset](#5-real-world-engineering-mindset)
- [6. Brainstorm / Open Questions](#6-brainstorm--open-questions)
- [7. Practice Questions](#7-practice-questions)
- [8. Personalized Recommendations](#8-personalized-recommendations)
- [9. Official Documentation & Reference Links](#9-official-documentation--reference-links)
- [Summary, Next Steps, and Advanced Topics](#summary-next-steps-and-advanced-topics)

---

## 1. Big Picture

### 1.1 What React Actually Is

React is a **JavaScript library for building user interfaces through composable, declarative components**. It is not a framework — it doesn't include routing, data fetching, or state management. It does one thing: given state, produce UI. Everything else is the ecosystem's job.

At its core, React is a **reconciler** — an engine that compares what your UI *should* look like (based on current state) with what it *currently* looks like (in the DOM), and applies the minimal set of changes. You describe the destination; React figures out the journey.

**Why this matters:** React decoupled *what* you want from *how* to get there. Before React, you wrote imperative instructions ("find this DOM node, change its text, add this class"). With React, you write a function that returns what the UI should look like, and React handles the DOM mutations.

### 1.2 Why React Exists — The Problems It Solves

1. **State-UI synchronization.** The hardest problem in frontend: keeping the DOM in sync with application state. Manually tracking which DOM nodes need updating when state changes leads to bugs, especially as UIs grow complex.

2. **Composition.** HTML doesn't compose well. React components are JavaScript functions that return markup — they compose like functions, accept arguments (props), and encapsulate behavior.

3. **Predictability.** Given the same state and props, a React component always renders the same output. This makes UIs testable, debuggable, and reasoning about them tractable.

4. **Performance at scale.** Direct DOM manipulation is fast for small changes but becomes unmanageable at scale. React's reconciliation batches and minimizes DOM operations.

### 1.3 Programming Model Comparison

| Approach | Mental model | State sync | Composition | Scaling |
|---|---|---|---|---|
| **Vanilla DOM** | `document.querySelector` + manual mutation | You track everything | Functions, but no UI abstraction | Breaks quickly |
| **jQuery** | Select → mutate → hope it's consistent | Manual, error-prone | Plugins, no component model | Spaghetti at scale |
| **React** | State → render function → virtual DOM → minimal DOM updates | Automatic via reconciliation | Components (functions) | Designed for large apps |
| **Declarative** | "Here's what it should look like" | Framework handles sync | Natural composition | Scales well |
| **Imperative** | "Here's the steps to change it" | Manual tracking | Procedural | Breaks at scale |

### 1.4 Core Internal Concepts

#### Virtual DOM

The virtual DOM is a lightweight JavaScript object tree that mirrors the structure of the real DOM. When state changes, React creates a new virtual DOM tree, diffs it against the previous one, and applies only the necessary changes to the real DOM.

**Why not just update the DOM directly?** DOM operations are expensive — not because individual operations are slow, but because they trigger layout recalculations, style recomputations, and paints. Batching and minimizing these operations is a significant performance win.

```text
State Change
    ↓
New Virtual DOM tree (JavaScript objects — cheap)
    ↓
Diff against previous Virtual DOM tree (JavaScript — cheap)
    ↓
Minimal DOM mutations (expensive, but minimized)
    ↓
Browser layout + paint
```

**Important nuance:** The virtual DOM is not "faster than the real DOM." It's a trade-off: you pay the cost of diffing in JavaScript to avoid paying the cost of unnecessary DOM operations. For trivial UIs, vanilla DOM is faster. For complex, frequently-updating UIs, the virtual DOM wins.

#### Reconciliation

Reconciliation is React's diffing algorithm. When you call `setState` or a component re-renders, React:

1. Calls your component function to get a new element tree.
2. Compares it to the previous element tree.
3. Determines the minimum set of changes needed.
4. Applies those changes in the commit phase.

**Key rules:**
- Elements of **different types** → destroy old tree, build new tree.
- Elements of **same type** → update attributes, recurse on children.
- **Keys** on list items → stable identity for efficient reordering.

```text
Previous tree:          New tree:              Result:
<div>                   <div>                  Update className
  <span>A</span>         <span>A</span>       No change
  <span>B</span>         <span>C</span>       Update text content
</div>                  </div>
```

#### Rendering vs. Commit Phase

**This is one of the most misunderstood concepts in React.**

"Rendering" in React does NOT mean updating the DOM. It means calling your component function.

```text
Phase 1: RENDER (pure, can be interrupted in concurrent mode)
  └── React calls your component function
  └── Produces a new element tree (virtual DOM)
  └── Diffs against previous tree
  └── NO side effects, NO DOM mutations

Phase 2: COMMIT (synchronous, cannot be interrupted)
  └── React applies DOM mutations
  └── Runs useLayoutEffect callbacks
  └── Browser paints
  └── Runs useEffect callbacks
```

**Why this matters:** Your component function may be called multiple times without the DOM ever updating. In concurrent mode, React may *start* rendering, *pause*, and *restart*. If your render function has side effects, things break.

#### Fiber Architecture

Fiber is React's internal data structure — a linked-list tree of "units of work." Each fiber node represents a component instance, a DOM element, or a fragment.

```text
FiberNode {
  type: ComponentOrTag,     // 'div', MyComponent, etc.
  stateNode: DOMElement,    // actual DOM node (if host component)
  child: FiberNode,         // first child
  sibling: FiberNode,       // next sibling
  return: FiberNode,        // parent
  pendingProps: {...},
  memoizedState: {...},     // hooks linked list
  effectTag: 'UPDATE',      // what needs to happen in commit
  lanes: 0b0001,            // priority
}
```

**Why Fiber exists:** Before Fiber (React 15), reconciliation was recursive and synchronous — once started, it couldn't be interrupted. A large tree diff would block the main thread, causing dropped frames. Fiber breaks reconciliation into interruptible units of work that can be paused, resumed, and prioritized.

**Analogy:** Pre-Fiber React was like a single `for` loop processing 10,000 items — it blocked until done. Fiber is like a generator function (`yield`) that processes items incrementally, yielding control back to the browser between chunks.

#### Scheduler

React's scheduler decides *when* and *in what order* to process updates. Not all updates are equal:

| Priority | Example | Urgency |
|---|---|---|
| Immediate (Sync) | Text input typing | Must not lag |
| User-blocking | Click handler result | High, but can batch |
| Normal | Data fetch result | Can defer briefly |
| Low | Off-screen update | Can defer significantly |
| Idle | Prefetch, analytics | Whenever |

The scheduler uses the browser's `MessageChannel` (not `requestIdleCallback`) to schedule work in small chunks between frames, keeping the main thread responsive.

#### Concurrent Rendering

Concurrent rendering means React can work on multiple state updates simultaneously and interrupt lower-priority renders to handle higher-priority ones.

```text
User types in search box (high priority)
  → React starts rendering search results
  → User types another character
  → React ABANDONS the in-progress render
  → Starts a new render with updated input
  → Commits only the final result

Without concurrent rendering:
  → Each keystroke blocks until render completes
  → UI feels sluggish
```

**Opt-in via:**
- `useTransition` — marks a state update as non-urgent.
- `useDeferredValue` — defers a value to a lower priority.
- `startTransition` — wraps a state update as a transition.

#### Hydration

Hydration is the process of attaching React's event handlers and state to server-rendered HTML. The server sends static HTML (fast first paint), then React "hydrates" it — making it interactive without re-creating the DOM.

```text
Server: Render component tree → HTML string → send to client
Client: Parse HTML → display (fast!) → load JS → React hydrates
  → Attaches event listeners
  → Connects state
  → DOM is now interactive
```

**Hydration mismatch:** If the server HTML doesn't match what React would render on the client, React warns and falls back to client-side rendering. This happens when you use `Date.now()`, `Math.random()`, or browser-only APIs during render.

### 1.5 The Full Lifecycle

```text
┌─────────────────────────────────────────────────────────────┐
│ 1. TRIGGER                                                  │
│    setState() / props change / context change / forceUpdate │
└──────────────────────────┬──────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│ 2. RENDER PHASE (Pure, interruptible in concurrent mode)    │
│                                                             │
│    React calls component functions top-down                 │
│    Produces new fiber tree (virtual DOM)                    │
│    Diffs against current fiber tree                         │
│    Marks fibers with effect tags (UPDATE, PLACEMENT, etc.)  │
│                                                             │
│    ⚠️ No side effects! No DOM mutations!                    │
└──────────────────────────┬──────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│ 3. COMMIT PHASE (Synchronous, cannot be interrupted)        │
│                                                             │
│    a. Before mutation: read DOM (getSnapshotBeforeUpdate)   │
│    b. Mutation: apply DOM changes (insert, update, delete)  │
│    c. Layout: run useLayoutEffect, update refs              │
│                                                             │
└──────────────────────────┬──────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│ 4. BROWSER PAINT                                            │
│                                                             │
│    Browser recalculates layout, paints pixels               │
│                                                             │
└──────────────────────────┬──────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│ 5. PASSIVE EFFECTS                                          │
│                                                             │
│    useEffect callbacks run asynchronously after paint       │
│    (data fetching, subscriptions, logging)                  │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 1.6 Comparison With Other Frameworks

| Dimension | React | Vue | Svelte | SolidJS | Angular |
|---|---|---|---|---|---|
| **Model** | Virtual DOM + reconciliation | Virtual DOM + reactivity | Compile-time, no virtual DOM | Fine-grained reactivity, no VDOM | Zone.js + change detection |
| **Reactivity** | Pull-based (re-render whole subtree) | Push-based (dependency tracking) | Compile-time assignments | Push-based (signals) | Zone.js-based dirty checking |
| **Update granularity** | Component-level | Component-level | Statement-level | DOM node-level | Component-level |
| **Bundle size** | ~45KB (react + react-dom) | ~33KB | ~2-5KB (compiled) | ~7KB | ~65KB+ |
| **Learning curve** | Medium (hooks, mental model) | Low (options API) / Medium (composition) | Low | Medium (different paradigm) | High (DI, RxJS, modules) |
| **Ecosystem** | Massive, fragmented | Large, cohesive | Growing | Small | Large, opinionated |
| **Concurrent rendering** | Yes (unique) | No (planned) | N/A (no runtime) | N/A (fine-grained) | No |
| **SSR story** | Next.js, Remix | Nuxt | SvelteKit | SolidStart | Angular Universal |
| **Philosophy** | Library — bring your own stack | Progressive framework | Disappearing framework | Reactive primitives | Full framework |

**React's unique advantages:**
- Concurrent rendering (no other major framework has this).
- Largest ecosystem and hiring pool.
- Server Components architecture (unique).
- Battle-tested at Facebook/Meta scale.

**React's weaknesses:**
- Re-renders entire subtrees by default (Vue/Solid are more precise).
- Requires memoization discipline (useMemo, useCallback, React.memo).
- Larger bundle than Svelte/Solid.
- "Library not framework" means more decisions and integration work.

### 1.7 When React Is a Good Fit

**Good fit:**
- Large, long-lived applications with many engineers.
- Complex, interactive UIs with frequent state changes.
- Teams that want a massive ecosystem and hiring pool.
- Applications that benefit from concurrent rendering (search, dashboards).
- SSR/SSG needs (via Next.js).
- Cross-platform needs (React Native).

**Problematic:**
- Simple static sites (Astro is better — you already know this).
- Performance-critical UIs where every kilobyte and millisecond matters (SolidJS, Svelte).
- Small teams that want conventions over configuration (Vue, Angular).
- When the virtual DOM overhead isn't justified (simple CRUD apps).

---

## 2. Learning Roadmap by Skill Level

### Level 1 — Newbie

**Goal:** Understand JSX, components, props, state, and the basic rendering model.

#### JSX

JSX is syntactic sugar for `React.createElement` calls. It looks like HTML but is JavaScript.

```tsx
// JSX
const element = <h1 className="title">Hello</h1>;

// Compiles to
const element = React.createElement('h1', { className: 'title' }, 'Hello');

// Returns a plain JavaScript object
// { type: 'h1', props: { className: 'title', children: 'Hello' } }
```

**Key rules:**
- `className` not `class` (it's JavaScript, `class` is reserved).
- `htmlFor` not `for`.
- Self-closing tags required: `<img />`, `<br />`.
- Expressions in `{}`: `{user.name}`, `{isActive && <Badge />}`.
- Must return a single root element (or use `<>...</>` fragments).

#### Components

Components are functions that return JSX. They are the unit of composition in React.

```tsx
// Function component (the only way you should write components in 2026)
function Greeting({ name }: { name: string }) {
  return <h1>Hello, {name}</h1>;
}

// Usage
<Greeting name="Thaison" />
```

**Mental model:** A component is a function. Props are arguments. JSX is the return value. React calls your function, gets back a description of UI, and renders it.

#### Props

Props are immutable data passed from parent to child. They flow one direction: down.

```tsx
interface CardProps {
  title: string;
  children: React.ReactNode;
  variant?: 'primary' | 'secondary';
}

function Card({ title, children, variant = 'primary' }: CardProps) {
  return (
    <div className={`card card--${variant}`}>
      <h2>{title}</h2>
      {children}
    </div>
  );
}
```

**Key rule:** Never mutate props. They are read-only. If a child needs to change data, it calls a callback prop provided by the parent.

#### State

State is mutable data owned by a component. When state changes, the component re-renders.

```tsx
import { useState } from 'react';

function Counter() {
  const [count, setCount] = useState(0);

  return (
    <div>
      <p>Count: {count}</p>
      <button onClick={() => setCount(count + 1)}>Increment</button>
      <button onClick={() => setCount(prev => prev + 1)}>
        Increment (functional update — safer)
      </button>
    </div>
  );
}
```

**Critical mental model:** `setState` does NOT mutate the variable immediately. It *schedules* a re-render. The new value is available on the *next* render.

```tsx
const [count, setCount] = useState(0);

function handleClick() {
  setCount(count + 1);
  console.log(count); // Still 0! State updates are asynchronous.
  setCount(count + 1); // Still uses count=0, so count becomes 1, not 2.
}

// Fix: use functional updates
function handleClickCorrect() {
  setCount(prev => prev + 1); // prev=0 → 1
  setCount(prev => prev + 1); // prev=1 → 2
}
```

#### Event handling

```tsx
function Form() {
  const handleSubmit = (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    // handle form
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    console.log(e.target.value);
  };

  return (
    <form onSubmit={handleSubmit}>
      <input onChange={handleChange} />
      <button type="submit">Submit</button>
    </form>
  );
}
```

**React uses synthetic events** — a cross-browser wrapper. Events are pooled and recycled (though this is less relevant since React 17 removed event pooling). Events are delegated to the root, not attached to individual DOM nodes.

#### Conditional rendering

```tsx
// Short-circuit
{isLoggedIn && <Dashboard />}

// Ternary
{isLoggedIn ? <Dashboard /> : <LoginForm />}

// Early return
function Page({ user }: { user: User | null }) {
  if (!user) return <LoginForm />;
  return <Dashboard user={user} />;
}
```

**Pitfall:** `{count && <Display />}` renders `0` when count is 0 (because `0` is falsy but is a valid React child). Fix: `{count > 0 && <Display />}`.

#### List rendering

```tsx
function TodoList({ items }: { items: Todo[] }) {
  return (
    <ul>
      {items.map(item => (
        <li key={item.id}>{item.text}</li>
      ))}
    </ul>
  );
}
```

**Keys are critical.** They tell React which items changed, were added, or removed. Without stable keys, React can't efficiently reconcile lists.

| Key approach | Result |
|---|---|
| `key={item.id}` (stable, unique) | ✅ Correct — React tracks identity |
| `key={index}` | ⚠️ Breaks on reorder/insert/delete |
| No key | ❌ Warning + buggy behavior |

#### Basic hooks

| Hook | Purpose | Example |
|---|---|---|
| `useState` | Local state | `const [x, setX] = useState(0)` |
| `useEffect` | Side effects after render | `useEffect(() => { fetch(...) }, [])` |
| `useRef` | Mutable ref that doesn't trigger re-render | `const ref = useRef(null)` |

#### Component lifecycle (hooks mental model)

```text
Mount:    Component function called → DOM inserted → useEffect runs
Update:   State/props change → function called → DOM updated → useEffect cleanup → useEffect runs
Unmount:  useEffect cleanup runs → DOM removed
```

#### Common beginner mistakes

| Mistake | Why it's wrong | Fix |
|---|---|---|
| Mutating state directly | React won't re-render | Create new object/array: `setItems([...items, newItem])` |
| Using index as key in dynamic lists | Breaks identity on reorder | Use stable, unique IDs |
| Side effects in render | Unpredictable, can cause infinite loops | Put side effects in `useEffect` |
| `{0 && <Component />}` rendering `0` | `0` is falsy but renderable | Use `{count > 0 && <Component />}` |
| Forgetting dependency array in useEffect | Effect runs every render | Always specify dependencies |
| Setting state in a loop | Causes multiple re-renders | Batch into one state update |

#### 5 beginner exercises

1. **Counter:** Build a counter with increment, decrement, and reset buttons.
2. **Toggle:** Build a show/hide component that toggles content visibility.
3. **Todo list:** Build a list where you can add and remove items. Use proper keys.
4. **Controlled input:** Build a search input that filters a list of items as you type.
5. **Fetch and display:** Fetch data from a public API on mount, show loading state, display results.

#### Level 1 success criteria

- [ ] Can explain JSX as `createElement` calls.
- [ ] Can build components with props and state.
- [ ] Can handle events and conditional rendering.
- [ ] Can render lists with stable keys.
- [ ] Can explain why `setState` is asynchronous.

---

### Level 2 — Junior

**Goal:** Master hooks, composition patterns, and build interactive UIs with proper data flow.

#### useEffect

`useEffect` runs *after* the browser paints. It's for side effects: data fetching, subscriptions, DOM measurements, timers.

```tsx
useEffect(() => {
  // Effect: runs after render
  const controller = new AbortController();

  fetch(`/api/users/${userId}`, { signal: controller.signal })
    .then(res => res.json())
    .then(data => setUser(data));

  // Cleanup: runs before next effect or unmount
  return () => controller.abort();
}, [userId]); // Dependency array: re-run when userId changes
```

**Dependency array rules:**

| Pattern | Behavior |
|---|---|
| `useEffect(fn)` | Runs after every render (rarely what you want) |
| `useEffect(fn, [])` | Runs once after mount (like componentDidMount) |
| `useEffect(fn, [a, b])` | Runs when `a` or `b` changes |

**Common mistake:** Missing dependencies. If your effect uses `count` but `[count]` isn't in the dependency array, the effect captures a stale `count`.

**When NOT to use useEffect:**

| Situation | Instead of useEffect | Use |
|---|---|---|
| Transform data for rendering | Effect + state | Compute during render |
| Respond to user event | Effect triggered by state | Event handler directly |
| Initialize state from props | Effect + setState | `useState(initialValue)` or derive |
| Fetch on mount | useEffect | React Query / useSWR (better error/loading/cache) |

[React docs: You Might Not Need an Effect](https://react.dev/learn/you-might-not-need-an-effect)

#### useMemo and useCallback

```tsx
// useMemo: cache an expensive computation
const sortedItems = useMemo(
  () => items.sort((a, b) => a.name.localeCompare(b.name)),
  [items]
);

// useCallback: cache a function reference
const handleClick = useCallback(
  (id: string) => setSelected(id),
  [] // no dependencies — function never changes
);
```

**When to use:**
- `useMemo`: Expensive computations (sorting, filtering large lists). NOT for trivial operations.
- `useCallback`: When passing callbacks to memoized children (`React.memo`). Without it, new function references defeat memoization.

**When NOT to use:**
- Trivial computations (adding two numbers). The memoization overhead exceeds the savings.
- When there's no child component relying on reference equality.
- Premature optimization — profile first.

#### Refs

```tsx
// DOM ref
function TextInput() {
  const inputRef = useRef<HTMLInputElement>(null);

  const focusInput = () => {
    inputRef.current?.focus();
  };

  return <input ref={inputRef} />;
}

// Mutable value (doesn't trigger re-render)
function Timer() {
  const intervalRef = useRef<number | null>(null);

  useEffect(() => {
    intervalRef.current = window.setInterval(() => {
      // ...
    }, 1000);
    return () => {
      if (intervalRef.current) clearInterval(intervalRef.current);
    };
  }, []);
}
```

**Mental model:** `useRef` is a box that holds a mutable value. Changing `.current` does NOT cause a re-render. Use it for DOM access, timer IDs, previous values, or any mutable value that shouldn't trigger re-renders.

#### Controlled vs. uncontrolled components

| Type | State lives in | Use case |
|---|---|---|
| **Controlled** | React state (`value={state}`) | Validation, formatting, derived state |
| **Uncontrolled** | DOM (`ref` to access value) | Simple forms, file inputs |

```tsx
// Controlled
function ControlledInput() {
  const [value, setValue] = useState('');
  return <input value={value} onChange={e => setValue(e.target.value)} />;
}

// Uncontrolled
function UncontrolledInput() {
  const ref = useRef<HTMLInputElement>(null);
  const handleSubmit = () => console.log(ref.current?.value);
  return <input ref={ref} defaultValue="" />;
}
```

**Senior take:** Default to controlled. Use uncontrolled only for file inputs or when integrating with non-React libraries.

#### Context API

```tsx
// 1. Create context with default value and type
interface ThemeContextType {
  theme: 'light' | 'dark';
  toggle: () => void;
}

const ThemeContext = createContext<ThemeContextType | null>(null);

// 2. Custom hook for type-safe access
function useTheme() {
  const ctx = useContext(ThemeContext);
  if (!ctx) throw new Error('useTheme must be used within ThemeProvider');
  return ctx;
}

// 3. Provider
function ThemeProvider({ children }: { children: React.ReactNode }) {
  const [theme, setTheme] = useState<'light' | 'dark'>('light');
  const toggle = useCallback(() =>
    setTheme(prev => prev === 'light' ? 'dark' : 'light'), []);

  const value = useMemo(() => ({ theme, toggle }), [theme, toggle]);

  return (
    <ThemeContext.Provider value={value}>
      {children}
    </ThemeContext.Provider>
  );
}
```

**Context performance pitfall:** When context value changes, ALL consumers re-render — even if they only use a part of the value. Solutions:
1. Split contexts (one for state, one for dispatch).
2. Memoize the value object with `useMemo`.
3. Use external state management (Zustand, Jotai) for frequently-changing state.

#### Composition patterns

```tsx
// 1. Children composition (most common)
function Layout({ children }: { children: React.ReactNode }) {
  return <div className="layout">{children}</div>;
}

// 2. Slot pattern
function Dialog({ header, body, footer }: {
  header: React.ReactNode;
  body: React.ReactNode;
  footer: React.ReactNode;
}) {
  return (
    <div className="dialog">
      <div className="dialog-header">{header}</div>
      <div className="dialog-body">{body}</div>
      <div className="dialog-footer">{footer}</div>
    </div>
  );
}

// 3. Render prop
function DataFetcher<T>({ url, render }: {
  url: string;
  render: (data: T) => React.ReactNode;
}) {
  const [data, setData] = useState<T | null>(null);
  useEffect(() => { fetch(url).then(r => r.json()).then(setData); }, [url]);
  if (!data) return <Spinner />;
  return <>{render(data)}</>;
}

// 4. Compound component
function Select({ children, value, onChange }: SelectProps) {
  return (
    <SelectContext.Provider value={{ value, onChange }}>
      <div className="select">{children}</div>
    </SelectContext.Provider>
  );
}
Select.Option = function Option({ value, children }: OptionProps) {
  const ctx = useSelectContext();
  return <div onClick={() => ctx.onChange(value)}>{children}</div>;
};
```

**Senior preference:** Children composition > render props > HOCs. Keep components simple. Use compound components for complex, related UI groups.

#### Lifting state

When two siblings need shared state, lift it to their common parent.

```tsx
function Parent() {
  const [selected, setSelected] = useState<string | null>(null);
  return (
    <>
      <Sidebar selected={selected} onSelect={setSelected} />
      <Content selectedId={selected} />
    </>
  );
}
```

**When lifting becomes painful (too many props):** Consider context, URL state, or external state management.

#### Custom hooks

```tsx
function useLocalStorage<T>(key: string, initialValue: T) {
  const [value, setValue] = useState<T>(() => {
    const stored = localStorage.getItem(key);
    return stored ? JSON.parse(stored) : initialValue;
  });

  useEffect(() => {
    localStorage.setItem(key, JSON.stringify(value));
  }, [key, value]);

  return [value, setValue] as const;
}

// Usage
const [theme, setTheme] = useLocalStorage('theme', 'light');
```

**Custom hooks let you extract stateful logic** from components — same way you extract pure logic into utility functions. They follow the same rules as hooks (call at top level, only in components/hooks).

#### Async UI handling

```tsx
function UserProfile({ userId }: { userId: string }) {
  const [user, setUser] = useState<User | null>(null);
  const [error, setError] = useState<Error | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    setError(null);
    const controller = new AbortController();

    fetch(`/api/users/${userId}`, { signal: controller.signal })
      .then(res => {
        if (!res.ok) throw new Error('Failed to fetch');
        return res.json();
      })
      .then(setUser)
      .catch(err => {
        if (err.name !== 'AbortError') setError(err);
      })
      .finally(() => setLoading(false));

    return () => controller.abort();
  }, [userId]);

  if (loading) return <Skeleton />;
  if (error) return <ErrorMessage error={error} />;
  if (!user) return null;
  return <div>{user.name}</div>;
}
```

**Better approach:** Use React Query / TanStack Query. It handles loading, error, caching, refetching, and race conditions automatically.

#### Common anti-patterns

| Anti-pattern | Problem | Fix |
|---|---|---|
| useEffect for derived state | Unnecessary render + effect cycle | Compute during render |
| useEffect to respond to events | Indirect, hard to trace | Handle in event handler |
| Prop drilling 5+ levels | Maintenance nightmare | Context or state management |
| Giant components (500+ lines) | Hard to test, reason about | Extract sub-components and hooks |
| `any` in TypeScript | No type safety | Proper types or `unknown` |
| Fetching in useEffect without cleanup | Race conditions, memory leaks | AbortController or React Query |
| Sync state from props via useEffect | Extra render cycle | Derive from props or use key |

#### 5 mini project ideas

1. **Multi-step form:** Form wizard with validation, back/forward navigation, and state preservation.
2. **Real-time search:** Debounced search input that fetches and displays results. Handle loading, error, empty states.
3. **Theme switcher:** Dark/light theme with context, persisted to localStorage, respects `prefers-color-scheme`.
4. **Sortable table:** Table with column sorting, pagination, and loading states. Handle 1,000 rows.
5. **Chat UI:** WebSocket-based chat with message list, input, typing indicator, and scroll-to-bottom behavior.

#### Level 2 success criteria

- [ ] Can use useEffect correctly (with cleanup, proper dependencies).
- [ ] Can explain when useMemo/useCallback are needed vs. wasteful.
- [ ] Can use context without causing unnecessary re-renders.
- [ ] Can build custom hooks to extract reusable logic.
- [ ] Can handle async data with loading/error/success states.

---

### Level 3 — Senior

**Goal:** Master rendering optimization, React internals, concurrent features, architecture, and production-grade patterns.

#### Rendering optimization

**Rule #1:** A component re-renders when:
1. Its state changes.
2. Its parent re-renders (even if props are the same).
3. A context it consumes changes.

**Rule #2:** Re-renders are NOT inherently bad. React is fast at re-rendering. Only optimize when you measure a real problem.

**Optimization toolkit:**

| Tool | What it does | When to use |
|---|---|---|
| `React.memo` | Skips re-render if props haven't changed (shallow compare) | Expensive components with frequent parent renders |
| `useMemo` | Caches computation result | Expensive calculations |
| `useCallback` | Caches function reference | Callbacks passed to `React.memo` children |
| `children` prop | Children don't re-render when parent state changes (if passed as props) | Layout components |
| State colocation | Move state down to where it's used | Prevent unnecessary subtree re-renders |
| Context splitting | Separate frequently-changing and rarely-changing contexts | Reduce context consumer re-renders |

**The "children as props" pattern:**

```tsx
// ❌ Slow: ExpensiveChild re-renders when count changes
function Parent() {
  const [count, setCount] = useState(0);
  return (
    <div>
      <button onClick={() => setCount(c => c + 1)}>{count}</button>
      <ExpensiveChild />
    </div>
  );
}

// ✅ Fast: ExpensiveChild is created before Parent renders, won't re-render
function App() {
  return (
    <Parent>
      <ExpensiveChild />
    </Parent>
  );
}
function Parent({ children }: { children: React.ReactNode }) {
  const [count, setCount] = useState(0);
  return (
    <div>
      <button onClick={() => setCount(c => c + 1)}>{count}</button>
      {children}
    </div>
  );
}
```

**Why this works:** `children` is a prop. The `<ExpensiveChild />` element is created in `App`'s scope, not `Parent`'s. When `Parent` re-renders (due to count change), `children` is the same React element reference — React skips re-rendering it.

#### Reconciliation deep dive

```text
Reconciliation algorithm (simplified):

1. Compare root elements:
   - Different type? → Unmount old tree, mount new tree.
   - Same type? → Update props, recurse into children.

2. For children:
   - Keyed children: Match by key, reorder efficiently.
   - Unkeyed children: Match by index (fragile!).

3. For each child:
   - Recursively apply step 1.

4. Collect all mutations (effects) into a list.

5. Commit all mutations to DOM synchronously.
```

**What makes this O(n) instead of O(n³):**
- React assumes elements of different types produce different trees (no cross-type comparison).
- Keys provide stable identity for list items.
- These heuristics make the diff linear, at the cost of occasionally over-updating (rebuilding subtrees that could theoretically be reused).

#### Concurrent rendering in depth

```tsx
import { useTransition, useDeferredValue } from 'react';

function SearchPage() {
  const [query, setQuery] = useState('');
  const [isPending, startTransition] = useTransition();

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    // Urgent: update input immediately
    setQuery(e.target.value);

    // Non-urgent: update results in a transition (can be interrupted)
    startTransition(() => {
      setFilteredResults(filterResults(e.target.value));
    });
  };

  return (
    <div>
      <input value={query} onChange={handleChange} />
      {isPending ? <Spinner /> : <Results items={filteredResults} />}
    </div>
  );
}

// Alternative: useDeferredValue
function SearchResults({ query }: { query: string }) {
  const deferredQuery = useDeferredValue(query);
  const results = useMemo(() => filterResults(deferredQuery), [deferredQuery]);
  return <ResultList items={results} />;
}
```

**Key insight:** `useTransition` wraps the *state setter*. `useDeferredValue` wraps the *value consumer*. Use `useTransition` when you control the state update. Use `useDeferredValue` when you receive the value as a prop.

#### Suspense

```tsx
import { Suspense, lazy } from 'react';

// Code splitting with lazy
const HeavyComponent = lazy(() => import('./HeavyComponent'));

function App() {
  return (
    <Suspense fallback={<Spinner />}>
      <HeavyComponent />
    </Suspense>
  );
}

// Data fetching (with a Suspense-compatible library like React Query v5+)
function UserProfile({ userId }: { userId: string }) {
  const { data: user } = useSuspenseQuery({
    queryKey: ['user', userId],
    queryFn: () => fetchUser(userId),
  });

  // No loading check needed — Suspense handles it
  return <div>{user.name}</div>;
}

function App() {
  return (
    <Suspense fallback={<ProfileSkeleton />}>
      <UserProfile userId="123" />
    </Suspense>
  );
}
```

**Mental model:** Suspense is a try/catch for loading states. When a child "suspends" (throws a promise), the nearest `<Suspense>` boundary shows the fallback. When the promise resolves, React retries rendering the child.

#### Server rendering and hydration

```text
SSR lifecycle:

1. Server: Render component tree → HTML string
   - No useEffect, no browser APIs
   - Data fetched server-side (getServerSideProps, loader, etc.)

2. Network: HTML sent to client
   - User sees content immediately (First Contentful Paint)

3. Client: React hydrates
   - Attaches event listeners
   - Connects state management
   - Page becomes interactive (Time to Interactive)

Streaming SSR (React 18+):
   - Server sends HTML in chunks as components resolve
   - Client hydrates chunks independently
   - Suspense boundaries define chunk boundaries
```

#### State architecture

| Pattern | When to use | Example |
|---|---|---|
| Local state (useState) | Component-specific, UI state | Form input, toggle, dropdown open |
| Lifted state | Shared between siblings | Selected item in sidebar + content |
| Context | App-wide, rarely-changing | Theme, locale, auth user |
| URL state | Shareable, bookmarkable | Search params, pagination, filters |
| External store (Zustand) | Frequently-changing, cross-cutting | Shopping cart, notifications |
| Server state (React Query) | Remote data with caching | API responses |

**Architecture principle:** "State should live as close as possible to where it's used."

```text
                    ┌─────────────────────┐
                    │ Server State         │  React Query / SWR
                    │ (API data, cache)    │  Don't duplicate in local state!
                    └────────┬────────────┘
                             │
                    ┌────────┴────────────┐
                    │ URL State            │  useSearchParams / router
                    │ (filters, pages)     │  Shareable, bookmarkable
                    └────────┬────────────┘
                             │
                    ┌────────┴────────────┐
                    │ Global Client State  │  Zustand / Jotai / Context
                    │ (auth, theme, cart)  │  Rarely, only when needed
                    └────────┬────────────┘
                             │
                    ┌────────┴────────────┐
                    │ Local State          │  useState / useReducer
                    │ (UI, forms, toggles) │  Default — keep it here
                    └─────────────────────┘
```

#### Testing strategy

| Layer | Tool | What to test |
|---|---|---|
| Unit | Vitest | Utility functions, custom hooks |
| Component | Testing Library | Component behavior (user interactions, output) |
| Integration | Testing Library + MSW | Features with mocked API |
| E2E | Playwright | Critical user flows |
| Visual | Storybook + Chromatic | Component appearance, responsive layouts |

**Philosophy:** Test behavior, not implementation. Don't test that `setState` was called — test that the UI changed.

```tsx
// ✅ Good: tests behavior
test('increments counter on click', () => {
  render(<Counter />);
  fireEvent.click(screen.getByRole('button', { name: /increment/i }));
  expect(screen.getByText('Count: 1')).toBeInTheDocument();
});

// ❌ Bad: tests implementation
test('calls setState', () => {
  const spy = jest.spyOn(React, 'useState');
  // ... testing internal state management
});
```

#### Performance profiling

1. **React DevTools Profiler:** Record renders, see which components re-rendered and why.
2. **React DevTools "Highlight updates":** Visual indicator of re-renders.
3. **Chrome DevTools Performance tab:** Flame chart showing JavaScript execution, layout, and paint.
4. **`why-did-you-render`:** Library that logs unnecessary re-renders.
5. **Lighthouse:** Overall performance metrics (LCP, FID, CLS).

**Profiling workflow:**
1. Reproduce the slow interaction.
2. Profile with React DevTools → identify which components re-render unnecessarily.
3. Profile with Chrome DevTools → identify if the bottleneck is JS, layout, or paint.
4. Fix the specific bottleneck (memoize, virtualize, debounce, etc.).
5. Measure again to confirm improvement.

#### 5 production-grade project examples

1. **Dashboard with real-time data:** WebSocket feeds, virtualized charts, concurrent rendering for search/filter. State: Zustand for client, React Query for server, URL for filters.
2. **E-commerce product listing:** SSR for SEO, infinite scroll, optimistic cart updates, image lazy loading, skeleton loading. Architecture: Next.js App Router + Server Components.
3. **Design system:** Component library with Storybook, compound components, accessible primitives, theme system via CSS variables + context.
4. **Multi-step onboarding wizard:** URL-based step tracking, form validation with Zod, state preservation across steps, analytics tracking.
5. **Content management editor:** Rich text editing, autosave with debounce, optimistic updates, conflict resolution, undo/redo with useReducer.

#### Level 3 success criteria

- [ ] Can explain the render/commit lifecycle in detail.
- [ ] Can identify and fix unnecessary re-renders using profiling tools.
- [ ] Can use concurrent features (useTransition, Suspense) correctly.
- [ ] Can design a state architecture for a large application.
- [ ] Can articulate testing strategy at each layer.

---

### Level 4 — Expert

**Goal:** Understand React at the framework level — fiber, scheduler, compiler, Server Components, and architectural philosophy.

#### Fiber architecture deep dive

Every React element maps to a fiber node. The fiber tree is a mutable work-in-progress structure that React traverses during reconciliation.

```text
Fiber tree traversal (DFS):

    App (fiber)
    │
    ├── child → Header (fiber)
    │            │
    │            └── child → Logo (fiber)
    │                         │
    │                         └── sibling → Nav (fiber)
    │
    └── sibling → Main (fiber)
                   │
                   └── child → Content (fiber)

Traversal order: App → Header → Logo → Nav → Main → Content

Each fiber has:
  .child     → first child
  .sibling   → next sibling
  .return    → parent
```

**Double buffering:** React maintains two fiber trees:
- **Current:** What's on screen.
- **Work-in-progress:** What's being rendered.

On commit, they swap. This allows React to prepare the next UI without touching the DOM until everything is ready.

#### React Scheduler mental model

```text
Update queue:
  ┌─────────────────────────────────────────┐
  │ Sync (discrete events: click, input)    │ ← highest priority
  │ Continuous (drag, scroll)               │
  │ Default (setState in setTimeout)        │
  │ Transition (startTransition)            │
  │ Idle (offscreen, prefetch)              │ ← lowest priority
  └─────────────────────────────────────────┘

Scheduler loop:
  1. Pick highest priority work
  2. Process fiber nodes (render phase)
  3. Check: has 5ms elapsed?
     - Yes → yield to browser (MessageChannel) → resume later
     - No → continue processing
  4. When all fibers processed → commit to DOM
```

**Rendering lanes:** React uses a bitmask system to track update priorities. Each update is assigned a "lane" (a bit). Multiple updates can share a lane, and React processes lanes from highest to lowest priority.

```text
SyncLane:        0b0000000000000000000000000000001
InputContinuousLane: 0b0000000000000000000000000000100
DefaultLane:     0b0000000000000000000000000010000
TransitionLane1: 0b0000000000000000000000001000000
IdleLane:        0b0100000000000000000000000000000
```

#### React Compiler (React Forget)

The React Compiler automatically memoizes components and hooks — removing the need for manual `useMemo`, `useCallback`, and `React.memo`.

**What it does:**
- Analyzes your component at build time.
- Inserts memoization where beneficial.
- Tracks dependency relationships automatically.
- Eliminates "stale closure" bugs from manual memoization.

**What it means for you:**
- Write simple, unmemoized code.
- The compiler optimizes it.
- `useMemo` and `useCallback` become optional.
- Components must follow the rules of React (pure render functions) — the compiler enforces this.

**Current status:** Production at Meta, available as a Babel plugin. Being integrated into frameworks.

[React Compiler docs](https://react.dev/learn/react-compiler)

#### React Server Components (RSC)

RSC splits components into two types:

| Type | Runs on | Can use | Bundle impact |
|---|---|---|---|
| Server Component (default in App Router) | Server only | async/await, DB, file system | Zero JS sent to client |
| Client Component (`'use client'`) | Server (SSR) + Client | useState, useEffect, events | JS sent to client |

```tsx
// Server Component (default) — runs on server, zero client JS
async function UserList() {
  const users = await db.query('SELECT * FROM users');
  return (
    <ul>
      {users.map(user => (
        <li key={user.id}>
          <UserCard user={user} />   {/* Server Component */}
          <LikeButton userId={user.id} />  {/* Client Component */}
        </li>
      ))}
    </ul>
  );
}

// Client Component — has interactivity
'use client';
function LikeButton({ userId }: { userId: string }) {
  const [liked, setLiked] = useState(false);
  return <button onClick={() => setLiked(!liked)}>❤️</button>;
}
```

**Mental model:** Server Components are the default. You opt into the client with `'use client'`. Think of `'use client'` as a boundary — everything below it becomes client code.

**Why this matters:**
- Massive bundle size reduction (server-only code never ships to client).
- Direct database/file access in components (no API routes needed).
- Automatic code splitting at the component level.
- Progressive enhancement — interactive parts are islands in a sea of server-rendered content.

#### Streaming SSR

```text
Traditional SSR:
  Server renders ALL components → sends complete HTML → client hydrates ALL

Streaming SSR (React 18+):
  Server renders what it can → sends partial HTML → streams remaining as Suspense boundaries resolve
  Client hydrates each chunk independently

  Browser receives:
  1. <html><body><Header /><Sidebar />  ← immediate
  2. <Suspense fallback> loading...     ← placeholder
  3. <!-- stream: resolved content -->  ← arrives when data is ready
```

**Benefits:** Faster Time to First Byte, progressive rendering, better perceived performance.

#### Framework comparison philosophy

| Philosophy | React | Vue | Svelte | SolidJS |
|---|---|---|---|---|
| **Core belief** | UI = f(state), composition over convention | Progressive enhancement, approachable | Less code, compile-time | Fine-grained reactivity |
| **Trade-off** | Freedom + ecosystem vs. decision fatigue | Cohesion vs. smaller ecosystem | Small bundles vs. less flexibility | Performance vs. smaller community |
| **Rendering** | Coarse (component-level), optimize with memo | Coarse (component-level), auto-tracking | Fine (surgical DOM updates) | Fine (signal-based) |
| **Future bet** | Compiler will solve memoization; RSC for server-first | Vapor mode (compile-time) | Already compiled | Already fine-grained |

**Expert insight:** React's "re-render everything" model is a deliberate trade-off. It's simple to reason about (predictable) at the cost of performance (addressed by memoization and the compiler). Solid's fine-grained model is more performant but harder to compose and debug. React bets that a compiler can bridge the gap.

#### Architecture review checklist

- [ ] Is state colocated as close as possible to its usage?
- [ ] Is server state managed by React Query / SWR (not duplicated in useState)?
- [ ] Are expensive computations memoized?
- [ ] Are list items keyed with stable IDs?
- [ ] Are side effects in useEffect (not in render)?
- [ ] Is the component tree depth reasonable (< 15 levels)?
- [ ] Are Suspense boundaries placed for progressive loading?
- [ ] Is code-split at route level minimum?
- [ ] Are forms controlled with proper validation?
- [ ] Is accessibility addressed (ARIA, keyboard nav, focus management)?
- [ ] Are error boundaries in place for runtime errors?
- [ ] Is the testing pyramid followed (unit > integration > e2e)?
- [ ] Are bundle sizes monitored and budgeted?
- [ ] Can a new engineer understand the component tree in 10 minutes?
- [ ] Is the rendering performance profiled for critical paths?

#### What expert engineers care about that juniors miss

| Expert concern | Junior blind spot |
|---|---|
| Render count under real conditions | "It works" |
| Bundle size per route | "We'll optimize later" |
| Hydration mismatch in SSR | "Works in dev" |
| State ownership and boundaries | "Just use global state" |
| Accessibility from day one | "We'll add it later" |
| Error boundaries for resilience | "It won't crash" |
| Component API design (props surface area) | "Just add another prop" |
| Key stability in dynamic lists | "Index works fine" |
| Effect cleanup and race conditions | "It fetches data" |
| Concurrent rendering compatibility | "We don't use transitions" |
| Server/client component boundary | "Everything is a client component" |
| Testing behavior, not implementation | "Mock everything" |

#### 10 advanced engineering discussion topics

1. **Signals vs. VDOM:** Will React adopt signals (like Solid, Angular, Preact)? What would it sacrifice? What would it gain?
2. **Compiler limits:** What patterns can't the React Compiler optimize? How does this constrain component design?
3. **RSC data flow:** In a Server Components world, is React Query still necessary? How does caching work across the server/client boundary?
4. **Hydration cost:** For a large e-commerce page, hydration can take 2-5 seconds. What strategies exist to reduce this (partial hydration, islands, progressive hydration)?
5. **Component boundaries:** When should you split a component? When does splitting harm performance (more fibers, more reconciliation)?
6. **State machine UI:** Should complex UI flows (multi-step forms, wizards, modals) be modeled as state machines (XState)? What's the trade-off vs. useState/useReducer?
7. **Micro-frontends with React:** When does it make sense? How do you share state, routing, and styles across independent React apps?
8. **React Native convergence:** Should web and mobile share component logic? At what level of abstraction?
9. **Build-time vs. runtime:** React leans runtime (VDOM, hooks). Svelte leans build-time. Where is the optimal balance? How does the React Compiler shift this?
10. **Framework lock-in:** If you build a 200-component design system in React, what's the migration cost to another framework? How do you minimize it?

---

## 3. Setup Guide

### Step 1: Project setup

#### Vite (recommended for SPAs)

```bash
npm create vite@latest my-app -- --template react-ts
cd my-app
npm install
npm run dev
```

#### Next.js (recommended for production apps)

```bash
npx create-next-app@latest my-app --typescript --tailwind --eslint --app --src-dir
cd my-app
npm run dev
```

#### Astro (for content-heavy sites with React islands)

```bash
npm create astro@latest my-site
cd my-site
npx astro add react
npm run dev
```

### Step 2: TypeScript configuration

```jsonc
// tsconfig.json (key settings)
{
  "compilerOptions": {
    "strict": true,
    "noUncheckedIndexedAccess": true,  // arrays[i] returns T | undefined
    "exactOptionalPropertyTypes": true, // distinguishes undefined from missing
    "jsx": "react-jsx",
    "moduleResolution": "bundler",
    "target": "ES2022",
    "lib": ["ES2022", "DOM", "DOM.Iterable"],
    "paths": {
      "@/*": ["./src/*"]
    }
  }
}
```

### Step 3: ESLint setup

```bash
npm install -D eslint @eslint/js typescript-eslint eslint-plugin-react-hooks eslint-plugin-react-refresh
```

Essential rules:
- `react-hooks/rules-of-hooks` — enforces hook call rules.
- `react-hooks/exhaustive-deps` — catches missing effect dependencies.
- `react-refresh/only-export-components` — ensures HMR works.

### Step 4: Folder structures

#### Small project

```text
src/
├── components/
│   ├── Button.tsx
│   ├── Card.tsx
│   └── Header.tsx
├── hooks/
│   └── useLocalStorage.ts
├── pages/           (or routes/)
│   ├── Home.tsx
│   └── About.tsx
├── utils/
│   └── formatDate.ts
├── App.tsx
└── main.tsx
```

#### Medium project

```text
src/
├── components/       ← shared/generic UI components
│   ├── ui/
│   │   ├── Button.tsx
│   │   ├── Input.tsx
│   │   └── Modal.tsx
│   └── layout/
│       ├── Header.tsx
│       ├── Footer.tsx
│       └── Sidebar.tsx
├── features/         ← domain-specific modules
│   ├── auth/
│   │   ├── components/
│   │   ├── hooks/
│   │   ├── api.ts
│   │   └── types.ts
│   ├── dashboard/
│   │   ├── components/
│   │   ├── hooks/
│   │   └── types.ts
│   └── settings/
├── hooks/            ← shared custom hooks
├── lib/              ← third-party wrappers, config
├── stores/           ← global state (Zustand)
├── types/            ← shared types
├── utils/            ← pure utility functions
├── App.tsx
└── main.tsx
```

#### Large enterprise project

```text
src/
├── app/              ← Next.js App Router / routing
│   ├── (auth)/
│   ├── (dashboard)/
│   └── layout.tsx
├── components/       ← shared design system
│   ├── primitives/   ← atomic components (Button, Input)
│   ├── patterns/     ← composed components (SearchBar, DataTable)
│   └── layouts/      ← page layouts
├── features/         ← domain modules (each is self-contained)
│   ├── billing/
│   │   ├── components/
│   │   ├── hooks/
│   │   ├── api/
│   │   ├── stores/
│   │   ├── types.ts
│   │   └── index.ts   ← public API of the feature
│   └── users/
├── hooks/            ← truly shared hooks
├── lib/              ← framework wrappers
│   ├── api-client.ts
│   ├── query-client.ts
│   └── auth.ts
├── stores/           ← global stores
├── types/            ← shared types / API schemas
└── utils/            ← pure functions
```

**Principle:** Features are self-contained modules. They can import from `components/`, `hooks/`, `lib/`, `utils/`, `types/`. They must NOT import from other features (use events, stores, or API to communicate).

### Step 5: State management integration

#### Zustand (recommended for client state)

```tsx
import { create } from 'zustand';

interface CartStore {
  items: CartItem[];
  addItem: (item: CartItem) => void;
  removeItem: (id: string) => void;
  total: () => number;
}

const useCartStore = create<CartStore>((set, get) => ({
  items: [],
  addItem: (item) => set(state => ({ items: [...state.items, item] })),
  removeItem: (id) => set(state => ({ items: state.items.filter(i => i.id !== id) })),
  total: () => get().items.reduce((sum, item) => sum + item.price, 0),
}));
```

#### React Query (recommended for server state)

```tsx
import { QueryClient, QueryClientProvider, useQuery } from '@tanstack/react-query';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 5 * 60 * 1000,   // 5 minutes
      gcTime: 10 * 60 * 1000,     // 10 minutes
      retry: 1,
      refetchOnWindowFocus: false,
    },
  },
});

function useUsers() {
  return useQuery({
    queryKey: ['users'],
    queryFn: () => fetch('/api/users').then(r => r.json()),
  });
}
```

### Step 6: Testing setup

```bash
npm install -D vitest @testing-library/react @testing-library/jest-dom @testing-library/user-event jsdom msw
```

```tsx
// vitest.config.ts
import { defineConfig } from 'vitest/config';

export default defineConfig({
  test: {
    environment: 'jsdom',
    setupFiles: ['./src/test/setup.ts'],
    globals: true,
  },
});

// src/test/setup.ts
import '@testing-library/jest-dom/vitest';
```

### Step 7: Debugging tooling

| Tool | Purpose |
|---|---|
| React DevTools | Component tree, props, state, profiler |
| React DevTools Profiler | Render timing, commit chart |
| Chrome DevTools Performance | JS execution, layout, paint |
| `why-did-you-render` | Log unnecessary re-renders |
| React strict mode | Detect impure renders, missing cleanups |

---

## 4. Cheatsheet

### Hooks reference

| Hook | Signature | Purpose |
|---|---|---|
| `useState` | `const [val, set] = useState(init)` | Local state |
| `useReducer` | `const [state, dispatch] = useReducer(reducer, init)` | Complex state logic |
| `useEffect` | `useEffect(() => { ... return cleanup }, [deps])` | Side effects after paint |
| `useLayoutEffect` | Same as useEffect | Side effects before paint (DOM measurements) |
| `useRef` | `const ref = useRef(init)` | Mutable value / DOM ref |
| `useMemo` | `const val = useMemo(() => compute, [deps])` | Cache computation |
| `useCallback` | `const fn = useCallback(fn, [deps])` | Cache function reference |
| `useContext` | `const val = useContext(MyContext)` | Read context value |
| `useId` | `const id = useId()` | Unique ID for accessibility |
| `useTransition` | `const [pending, start] = useTransition()` | Non-urgent state updates |
| `useDeferredValue` | `const deferred = useDeferredValue(val)` | Defer a value |
| `useImperativeHandle` | `useImperativeHandle(ref, () => api)` | Customize ref exposed to parent |
| `useSyncExternalStore` | `useSyncExternalStore(sub, getSnap)` | Subscribe to external store |

### Rendering rules

| Rule | Details |
|---|---|
| Components re-render when state changes | `setState` triggers re-render of component + children |
| Parent re-render → children re-render | Unless children are memoized (`React.memo`) |
| Context change → all consumers re-render | Even if they use only part of the value |
| Props change alone doesn't cause re-render | Parent re-rendering does (props change is a consequence) |
| `setState` with same value → no re-render | React bails out (but the function may still be called once) |
| Render must be pure | No side effects, no DOM mutation, no subscriptions |

### State update rules

```tsx
// Batching: multiple setStates = one re-render (React 18+)
function handleClick() {
  setCount(c => c + 1);
  setFlag(f => !f);
  // One re-render, not two
}

// Object state: always create new object
setUser({ ...user, name: 'New' });       // ✅
user.name = 'New'; setUser(user);         // ❌ Same reference, no re-render

// Array state: always create new array
setItems([...items, newItem]);             // ✅ Add
setItems(items.filter(i => i.id !== id));  // ✅ Remove
setItems(items.map(i => i.id === id ? { ...i, done: true } : i)); // ✅ Update
items.push(newItem); setItems(items);      // ❌ Mutates original
```

### useEffect dependency rules

| Dependency | Effect runs |
|---|---|
| `[a, b]` | When `a` or `b` changes (Object.is comparison) |
| `[]` | Once after mount |
| omitted | Every render (almost never correct) |

**Object/array dependencies:** Objects and arrays are compared by reference. `{ a: 1 }` !== `{ a: 1 }`. Solutions:
1. Destructure: `[obj.a, obj.b]` instead of `[obj]`.
2. Stabilize with `useMemo`.
3. Use a primitive derived value.

### Common composition patterns

```tsx
// Compound component
<Select value={v} onChange={setV}>
  <Select.Option value="a">A</Select.Option>
  <Select.Option value="b">B</Select.Option>
</Select>

// Render prop
<Tooltip render={({ isVisible }) => isVisible ? <Info /> : null} />

// Polymorphic component
<Button as="a" href="/about">Link Button</Button>

// Forwarded ref
const Input = forwardRef<HTMLInputElement, InputProps>((props, ref) => (
  <input ref={ref} {...props} />
));
```

### Common React warnings

| Warning | Cause | Fix |
|---|---|---|
| "Each child in a list should have a unique key" | Missing or non-unique `key` prop | Add stable `key={item.id}` |
| "Cannot update a component while rendering another" | Calling setState of parent during child render | Move to useEffect or event handler |
| "Maximum update depth exceeded" | Infinite re-render loop | Fix useEffect deps or conditional setState |
| "Hydration mismatch" | Server/client render different output | Remove Date.now(), Math.random() from render |
| "Can't perform a React state update on an unmounted component" | setState in async callback after unmount | Use AbortController or check mounted ref |
| "React Hook useEffect has a missing dependency" | Effect uses a value not in deps array | Add it to deps or restructure |

### TypeScript patterns

```tsx
// Component props
interface ButtonProps {
  variant: 'primary' | 'secondary';
  size?: 'sm' | 'md' | 'lg';
  children: React.ReactNode;
  onClick?: () => void;
}

// Extending HTML element props
interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label: string;
  error?: string;
}

// Generic component
function List<T>({ items, renderItem }: {
  items: T[];
  renderItem: (item: T) => React.ReactNode;
}) {
  return <ul>{items.map((item, i) => <li key={i}>{renderItem(item)}</li>)}</ul>;
}

// Discriminated union for component states
type AsyncState<T> =
  | { status: 'loading' }
  | { status: 'error'; error: Error }
  | { status: 'success'; data: T };

// Event handlers
const handleClick = (e: React.MouseEvent<HTMLButtonElement>) => {};
const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {};
const handleSubmit = (e: React.FormEvent<HTMLFormElement>) => {};
```

### Performance tips

| Tip | When |
|---|---|
| Colocate state | Always — move state down to where it's used |
| `React.memo` | When profiling shows unnecessary re-renders of expensive components |
| `useMemo` | Expensive computations (sorting, filtering large arrays) |
| `useCallback` | Callbacks passed to `React.memo` children |
| Virtualize long lists | > 100 items visible, use `@tanstack/react-virtual` |
| Lazy load routes | Always — `React.lazy` + `Suspense` for route-level code splitting |
| Debounce search input | User-typed input triggering expensive operations |
| Avoid inline objects in JSX | `style={{ color: 'red' }}` creates new object every render |

### Accessibility tips

| Practice | How |
|---|---|
| Semantic HTML | Use `<button>`, `<nav>`, `<main>`, `<article>` |
| ARIA labels | `aria-label`, `aria-labelledby`, `aria-describedby` |
| Keyboard navigation | `onKeyDown`, `tabIndex`, focus management |
| Focus management | `useRef` + `.focus()` for modals, dialogs |
| Live regions | `aria-live="polite"` for dynamic content |
| Color contrast | 4.5:1 minimum for text |
| `useId` for form labels | Unique IDs for `htmlFor` / `id` pairs |
| Skip navigation link | Hidden link to skip to main content |

---

## 5. Real-World Engineering Mindset

### Form management

**Problem:** Forms need validation, error display, submission handling, and state management. Simple forms are easy; complex forms (multi-step, dynamic fields, async validation) are hard.

| Strategy | Complexity it handles | Bundle size | DX |
|---|---|---|---|
| `useState` + manual | Simple forms | 0KB | Tedious at scale |
| `useReducer` + manual | Medium forms | 0KB | More structured |
| React Hook Form | Complex forms | ~9KB | Excellent |
| Formik | Complex forms | ~13KB | Good but heavier |
| Conform (for RSC) | Server-validated forms | ~5KB | Next.js native |

**Senior choice:** React Hook Form + Zod for validation. Uncontrolled by default (performance), with `register` for simple inputs and `Controller` for custom components.

```tsx
const schema = z.object({
  email: z.string().email(),
  password: z.string().min(8),
});

function LoginForm() {
  const { register, handleSubmit, formState: { errors } } = useForm({
    resolver: zodResolver(schema),
  });

  return (
    <form onSubmit={handleSubmit(onSubmit)}>
      <input {...register('email')} />
      {errors.email && <span>{errors.email.message}</span>}
    </form>
  );
}
```

---

### Global state

**Problem:** Some state needs to be accessed across many components (auth user, theme, shopping cart).

| Strategy | Re-render scope | DevTools | Persistence | Best for |
|---|---|---|---|---|
| Context | All consumers | React DevTools | Manual | Rarely-changing (theme, locale) |
| Zustand | Selector-based (minimal) | Zustand DevTools | Middleware | Client UI state |
| Jotai | Atom-based (minimal) | Jotai DevTools | Atom-level | Fine-grained shared atoms |
| Redux Toolkit | Selector-based | Redux DevTools | RTK middleware | Large teams wanting convention |
| React Query | Query-based | RQ DevTools | Built-in cache | Server state (NOT global client state) |

**Senior choice:** Zustand for client state (small API, minimal re-renders). React Query for server state. Context only for theme/locale/auth. Never Redux for a new project unless the team already knows it.

---

### Table rendering

**Problem:** Tables with sorting, filtering, pagination, and many rows are performance-sensitive.

| Strategy | Row limit | Features | Bundle |
|---|---|---|---|
| Plain `<table>` | < 100 rows | Manual sorting/filtering | 0KB |
| TanStack Table (headless) | < 10,000 rows | Full-featured, bring your own UI | ~15KB |
| Virtualized table (TanStack Virtual) | 100,000+ rows | Only renders visible rows | ~5KB |
| AG Grid | Unlimited | Enterprise features | 200KB+ |

**Senior choice:** TanStack Table for most cases. Add virtualization (`@tanstack/react-virtual`) when rows exceed ~500. AG Grid only for spreadsheet-like requirements.

---

### Virtualization

**Problem:** Rendering 10,000+ DOM nodes causes jank.

**Solution:** Only render items visible in the viewport + a small overscan buffer.

```tsx
import { useVirtualizer } from '@tanstack/react-virtual';

function VirtualList({ items }: { items: Item[] }) {
  const parentRef = useRef<HTMLDivElement>(null);

  const virtualizer = useVirtualizer({
    count: items.length,
    getScrollElement: () => parentRef.current,
    estimateSize: () => 50,
    overscan: 5,
  });

  return (
    <div ref={parentRef} style={{ height: 400, overflow: 'auto' }}>
      <div style={{ height: virtualizer.getTotalSize() }}>
        {virtualizer.getVirtualItems().map(row => (
          <div key={row.key} style={{
            position: 'absolute',
            top: row.start,
            height: row.size,
          }}>
            {items[row.index].name}
          </div>
        ))}
      </div>
    </div>
  );
}
```

---

### SSR vs. CSR vs. SSG

| Rendering | When HTML is generated | SEO | TTFB | Interactivity | Best for |
|---|---|---|---|---|---|
| CSR | Client (after JS loads) | Poor | Fast (empty shell) | After JS | Dashboards, internal tools |
| SSR | Server (per request) | Excellent | Slower | After hydration | Dynamic pages with SEO |
| SSG | Build time | Excellent | Fastest | After hydration | Marketing, blogs, docs |
| ISR | Build + revalidation | Excellent | Fast | After hydration | E-commerce, content sites |
| RSC | Server (streamed) | Excellent | Fast (streaming) | Progressive | Next.js App Router apps |

**Senior choice:** Default to SSR/RSC (Next.js App Router). Use SSG for truly static content. Use CSR only for authenticated dashboards. ISR for content that changes hourly/daily.

---

### Code splitting

```tsx
import { lazy, Suspense } from 'react';

// Route-level splitting (always do this)
const Dashboard = lazy(() => import('./pages/Dashboard'));
const Settings = lazy(() => import('./pages/Settings'));

// Component-level splitting (for heavy components)
const RichTextEditor = lazy(() => import('./components/RichTextEditor'));

function App() {
  return (
    <Suspense fallback={<PageSkeleton />}>
      <Routes>
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/settings" element={<Settings />} />
      </Routes>
    </Suspense>
  );
}
```

**Senior choice:** Always split at route level. Split heavy components (editors, charts, maps) at component level. Monitor bundle sizes with `source-map-explorer` or `@next/bundle-analyzer`.

---

### Optimistic updates

**Problem:** Waiting for server response before updating UI feels slow.

```tsx
const mutation = useMutation({
  mutationFn: updateTodo,
  onMutate: async (newTodo) => {
    await queryClient.cancelQueries({ queryKey: ['todos'] });
    const previous = queryClient.getQueryData(['todos']);
    queryClient.setQueryData(['todos'], old =>
      old.map(t => t.id === newTodo.id ? { ...t, ...newTodo } : t)
    );
    return { previous };
  },
  onError: (err, newTodo, context) => {
    queryClient.setQueryData(['todos'], context.previous); // Rollback
  },
  onSettled: () => {
    queryClient.invalidateQueries({ queryKey: ['todos'] }); // Refetch truth
  },
});
```

**Senior choice:** Use React Query's optimistic update pattern. Always implement rollback. Show subtle indicators that the change is pending.

---

### Modal architecture

**Problem:** Modals need to render outside the component tree (portals), manage focus, handle escape key, and prevent body scroll.

**Senior choice:** Build on top of Radix UI or headless UI primitives. Use portals (`createPortal`). Manage focus trap. Handle `Escape` key. Prevent background scroll. Use compound component pattern for composability.

---

### Design systems

**Senior choice:** Build on Radix UI primitives (accessible, unstyled). Style with Tailwind CSS or CSS Modules. Publish as a shared package in a monorepo. Document with Storybook. Test visually with Chromatic.

---

## 6. Brainstorm / Open Questions

### Architecture

1. Should this state live in the component, in context, in a store, or in the URL?
2. When does a component become "too big"? What are the signals?
3. How do you decide between a feature folder structure and a type-based folder structure?
4. Should Server Components replace API routes for data fetching?
5. When should you create a custom hook vs. just write the logic inline?
6. How do you enforce feature module boundaries in a large codebase?
7. When does component composition break down and you need a state machine?
8. Should your design system be a separate package or a folder in the monorepo?

### Rendering

9. Why does React re-render the entire subtree instead of just the changed component?
10. What breaks if concurrent rendering interrupts a render that reads from a mutable source?
11. When should you use `useLayoutEffect` instead of `useEffect`?
12. What happens when a Suspense boundary is nested inside another Suspense boundary?
13. How does React decide which updates to batch?
14. What is the cost of having 500 `useMemo` calls in a component tree?
15. Why does React call your component function twice in Strict Mode?
16. What happens when `key` changes on a component — does it re-render or remount?

### Performance

17. How do you identify whether a performance problem is in React (JS) or in the browser (layout/paint)?
18. When is `React.memo` harmful (costs more than it saves)?
19. How would this component behave with 10,000 items?
20. What's the performance difference between CSS-in-JS and CSS Modules in SSR?
21. How much does hydration cost for a page with 200 interactive components?
22. When should you move computation to a Web Worker?
23. What's the impact of 50 context providers nested at the root?
24. How do you measure and budget JavaScript bundle size per route?

### DX / Maintainability

25. How do you prevent prop drilling without reaching for global state?
26. When is TypeScript strict mode worth the extra effort?
27. How do you write tests that don't break when implementation changes?
28. Should you co-locate tests next to components or in a separate folder?
29. How do you manage 100+ components without a design system?
30. When does abstraction hurt more than it helps?
31. How do you onboard a new engineer to a 500-component codebase?
32. Should stories in Storybook be the single source of truth for component documentation?

### Accessibility

33. How do you ensure keyboard navigation works in a custom dropdown?
34. What ARIA attributes does a modal need to be accessible?
35. How should focus behave when a route changes in a SPA?
36. When should you use `aria-live` vs. focus management for dynamic content?
37. How do you test accessibility automatically and what can't be automated?
38. What's the cost of adding accessibility retroactively vs. from day one?

### Scaling

39. At what team size does a monorepo become essential?
40. How do you prevent one team's changes from breaking another team's components?
41. When should you migrate from a single Next.js app to micro-frontends?
42. How do you share components between React web and React Native?
43. What deployment strategy works for 50 engineers shipping to the same app?
44. How do you manage CSS at scale without conflicts?

### Product trade-offs

45. When should you ship with known performance issues vs. fix them first?
46. What's the cost of choosing the wrong state management library?
47. Should you build a custom component or use a library (trade-offs of each)?
48. When is "good enough" UI better than "perfect" UI?
49. How do you balance developer experience with user experience?
50. When should you rewrite a component from scratch vs. refactor incrementally?
51. What's the real cost of adding a new npm dependency?
52. Should you optimize for first render performance or interaction performance?

---

## 7. Practice Questions

### Beginner (15 questions)

**Q1. True/False:** JSX is HTML.

<details><summary>Answer</summary>False. JSX is syntactic sugar for <code>React.createElement</code> calls. It looks like HTML but is JavaScript. Key differences: <code>className</code> not <code>class</code>, <code>htmlFor</code> not <code>for</code>, camelCase attributes, self-closing tags required.</details>

---

**Q2. Single choice:** What does `useState` return?

- A. The current state value
- B. A function to update state
- C. An array of [value, setter]
- D. An object with value and setter

<details><summary>Answer</summary>C. <code>useState</code> returns a tuple: <code>[currentValue, setterFunction]</code>. Array destructuring lets you name them anything.</details>

---

**Q3. Fill in the blank:** To prevent a list rendering bug, every item in a `.map()` must have a unique `_______` prop.

<details><summary>Answer</summary><code>key</code>. Keys give React stable identity for each item. Without stable keys, React can't efficiently reconcile additions, removals, or reorders.</details>

---

**Q4. Debugging:** This code renders `0` instead of nothing when count is 0. Why?

```tsx
{count && <Badge count={count} />}
```

<details><summary>Answer</summary><code>0</code> is falsy in JavaScript, so the short-circuit evaluates to <code>0</code>. But <code>0</code> is a valid React child and renders as text. Fix: <code>{count > 0 && &lt;Badge count={count} /&gt;}</code>.</details>

---

**Q5. Single choice:** When does a component re-render?

- A. Only when its props change
- B. Only when its state changes
- C. When its state changes OR its parent re-renders
- D. Only when you call `forceUpdate`

<details><summary>Answer</summary>C. A component re-renders when its own state changes, when its parent re-renders (passing new or same props), or when a consumed context value changes.</details>

---

**Q6. True/False:** `setState` updates the value immediately.

<details><summary>Answer</summary>False. <code>setState</code> schedules a re-render. The new value is available on the next render, not immediately after calling <code>setState</code>.</details>

---

**Q7. Scenario:** You have this code. What renders?

```tsx
function App() {
  return <Greeting name="React" />;
}
function Greeting({ name }: { name: string }) {
  return <h1>Hello, {name}!</h1>;
}
```

<details><summary>Answer</summary><code>&lt;h1&gt;Hello, React!&lt;/h1&gt;</code>. The <code>name</code> prop is passed from App to Greeting and interpolated into JSX.</details>

---

**Q8. Multiple choice:** Which are valid ways to handle events in React? (Select all)

- A. `<button onClick={handleClick}>`
- B. `<button onclick={handleClick}>`
- C. `<button onClick={() => handleClick(id)}>`
- D. `document.addEventListener('click', handleClick)`

<details><summary>Answer</summary>A and C. React uses camelCase event names (<code>onClick</code>, not <code>onclick</code>). D works but bypasses React's event system and won't be cleaned up automatically.</details>

---

**Q9. Fill in the blank:** Components must start with a _______ letter.

<details><summary>Answer</summary>Capital (uppercase). <code>&lt;myComponent /&gt;</code> is treated as an HTML tag. <code>&lt;MyComponent /&gt;</code> is treated as a React component.</details>

---

**Q10. Debugging:** Why does this component not update when the button is clicked?

```tsx
function Counter() {
  let count = 0;
  return <button onClick={() => { count++; }}>{count}</button>;
}
```

<details><summary>Answer</summary><code>count</code> is a local variable, not React state. Mutating it doesn't trigger a re-render. Fix: use <code>const [count, setCount] = useState(0)</code> and <code>setCount(c => c + 1)</code>.</details>

---

**Q11. True/False:** React components can return multiple root elements.

<details><summary>Answer</summary>True — using Fragments: <code>&lt;&gt;...&lt;/&gt;</code> or <code>&lt;React.Fragment&gt;...&lt;/React.Fragment&gt;</code>. Without fragments, you'd need a wrapper div.</details>

---

**Q12. Single choice:** What does the `children` prop contain?

- A. The component's state
- B. The component's parent reference
- C. The content passed between opening and closing tags
- D. The component's DOM node

<details><summary>Answer</summary>C. <code>children</code> is whatever is placed between <code>&lt;Component&gt;</code> and <code>&lt;/Component&gt;</code> tags.</details>

---

**Q13. Matching:** Match the hook to its purpose.

| Hook | Purpose |
|---|---|
| A. `useState` | 1. Side effects after render |
| B. `useEffect` | 2. Access DOM element |
| C. `useRef` | 3. Local mutable state |

<details><summary>Answer</summary>A→3, B→1, C→2</details>

---

**Q14. Scenario:** You render a list of 5 items using `index` as key. You remove the 2nd item. What problem might occur?

<details><summary>Answer</summary>React thinks item at index 1 changed (it's now what was index 2), index 2 changed, etc. It updates all items instead of removing one. This can cause incorrect state in components with local state (e.g., an input value stays attached to the wrong item). Fix: use <code>item.id</code> as key.</details>

---

**Q15. True/False:** Props are mutable — a child component can modify them.

<details><summary>Answer</summary>False. Props are read-only in React. A child should never mutate props. If a child needs to change data, it calls a callback prop provided by the parent.</details>

---

### Junior (15 questions)

**Q16. Single choice:** What happens if you omit the dependency array from `useEffect`?

- A. The effect runs once on mount
- B. The effect never runs
- C. The effect runs after every render
- D. React throws an error

<details><summary>Answer</summary>C. Without a dependency array, the effect runs after every render. This is rarely the desired behavior and can cause performance issues or infinite loops.</details>

---

**Q17. True/False:** `useMemo` guarantees a performance improvement.

<details><summary>Answer</summary>False. <code>useMemo</code> adds overhead (storing the value, comparing dependencies). For trivial computations, the memoization cost exceeds the computation cost. Only use it for genuinely expensive operations.</details>

---

**Q18. Debugging:** This effect causes an infinite loop. Why?

```tsx
const [data, setData] = useState([]);
useEffect(() => {
  setData([...data, newItem]);
}, [data]);
```

<details><summary>Answer</summary><code>setData</code> creates a new array → <code>data</code> reference changes → effect re-runs → <code>setData</code> again → infinite loop. Fix: use functional update: <code>setData(prev => [...prev, newItem])</code> and remove <code>data</code> from dependencies.</details>

---

**Q19. Single choice:** What is the difference between a controlled and uncontrolled input?

- A. Controlled inputs use refs; uncontrolled use state
- B. Controlled inputs use state (`value`); uncontrolled use refs (`defaultValue`)
- C. There is no difference
- D. Controlled inputs are faster

<details><summary>Answer</summary>B. A controlled input's value is driven by React state (<code>value={state}</code>). An uncontrolled input manages its own value in the DOM (<code>defaultValue</code>), accessed via ref.</details>

---

**Q20. Fill in the blank:** When context value changes, _______ consumers re-render.

<details><summary>Answer</summary>All. Every component that calls <code>useContext(MyContext)</code> re-renders when the context value changes, regardless of whether they use the specific part that changed.</details>

---

**Q21. Scenario:** You pass an inline function `onClick={() => handleClick(id)}` to a `React.memo` child. The child still re-renders every time. Why?

<details><summary>Answer</summary>The arrow function creates a new function reference on every parent render. <code>React.memo</code> does shallow comparison and sees a "new" prop. Fix: wrap with <code>useCallback</code>: <code>const handler = useCallback(() => handleClick(id), [id])</code>.</details>

---

**Q22. True/False:** `useRef` changes trigger re-renders.

<details><summary>Answer</summary>False. Mutating <code>ref.current</code> does NOT trigger a re-render. That's the key difference from <code>useState</code>. Use refs for values that need to persist across renders without causing re-renders (timers, previous values, DOM nodes).</details>

---

**Q23. Multiple choice:** Which are valid uses of `useEffect`? (Select all)

- A. Fetching data from an API
- B. Computing a filtered list from props
- C. Setting up a WebSocket subscription
- D. Deriving state from props

<details><summary>Answer</summary>A and C. B and D should be computed during render (derive directly, or use useMemo). Effects are for side effects that interact with the outside world.</details>

---

**Q24. Scenario:** You have 5 levels of prop drilling. What are your options?

<details><summary>Answer</summary>
1. <strong>Context</strong> — for rarely-changing data (theme, auth, locale).<br>
2. <strong>Composition</strong> — pass components as children/props to skip intermediate levels.<br>
3. <strong>External state</strong> — Zustand, Jotai (for frequently-changing data).<br>
4. <strong>URL state</strong> — for shareable/bookmarkable state.<br>
Best approach depends on how often the data changes and how many consumers need it.
</details>

---

**Q25. Debugging:** This custom hook has a bug. What is it?

```tsx
function useWindowWidth() {
  const [width, setWidth] = useState(window.innerWidth);
  useEffect(() => {
    window.addEventListener('resize', () => setWidth(window.innerWidth));
  }, []);
  return width;
}
```

<details><summary>Answer</summary>Missing cleanup — the event listener is never removed, causing a memory leak. Fix: return a cleanup function: <code>return () => window.removeEventListener('resize', handler)</code>. Also need to assign the handler to a variable to remove the same reference.</details>

---

**Q26. Single choice:** How do you prevent `useEffect` from running on mount?

- A. Use `useEffect(fn, [])`
- B. Use a ref to track if it's the first render
- C. Use `useLayoutEffect`
- D. You can't — effects always run on mount

<details><summary>Answer</summary>B. Effects with dependencies always run on mount (first render). To skip the initial run, use a ref: <code>const isFirst = useRef(true)</code>, then check and set it in the effect.</details>

---

**Q27. Fill in the blank:** `useCallback(fn, [deps])` is equivalent to `useMemo(() => _______, [deps])`.

<details><summary>Answer</summary><code>fn</code>. <code>useCallback(fn, deps)</code> is syntactic sugar for <code>useMemo(() => fn, deps)</code>. Both cache based on dependencies; <code>useCallback</code> specifically caches functions.</details>

---

**Q28. True/False:** Context is a good choice for frequently-updating global state like a real-time stock ticker.

<details><summary>Answer</summary>False. Context changes re-render all consumers. For frequently-updating state, use an external store like Zustand (which allows selector-based subscriptions) or <code>useSyncExternalStore</code>.</details>

---

**Q29. Scenario:** You use `useEffect` to set state from props:

```tsx
useEffect(() => { setName(props.initialName); }, [props.initialName]);
```

What's wrong?

<details><summary>Answer</summary>This is an anti-pattern — it creates an unnecessary render cycle (render with old state → effect runs → setState → re-render with new state). Better: derive from props directly, or use <code>key</code> to reset the component: <code>&lt;NameInput key={userId} initialName={name} /&gt;</code>.</details>

---

**Q30. Debugging:** Your form submits but `e.target.value` inside the submit handler is undefined. Why?

<details><summary>Answer</summary>In a submit handler, <code>e.target</code> is the form element, not an input. Use controlled state to access input values, or use <code>new FormData(e.target)</code> to get all form values, or access specific inputs via <code>e.target.elements.fieldName</code>.</details>

---

### Senior / Expert (20 questions)

**Q31. Scenario:** Your React table freezes with 20,000 rows. What should you investigate first?

<details><summary>Answer</summary>
1. <strong>First:</strong> Are you rendering all 20K DOM nodes? → Virtualize with <code>@tanstack/react-virtual</code>.<br>
2. <strong>Second:</strong> Are rows re-rendering unnecessarily? → Profile with React DevTools, memoize rows.<br>
3. <strong>Third:</strong> Is sorting/filtering happening on every render? → Memoize with <code>useMemo</code>.<br>
4. <strong>Fourth:</strong> Is the data transformation expensive? → Move to a Web Worker.<br>
Virtualization is almost always the answer for large lists.
</details>

---

**Q32. True/False:** React guarantees that `useEffect` cleanup runs before the component's DOM nodes are removed.

<details><summary>Answer</summary>False. <code>useEffect</code> cleanup runs <em>after</em> the DOM is updated (it's asynchronous). <code>useLayoutEffect</code> cleanup runs <em>before</em> the DOM is updated (synchronous). This matters for animations, measurements, and focus management.</details>

---

**Q33. Single choice:** What happens when you change the `key` prop on a component?

- A. The component re-renders with new props
- B. The component unmounts and remounts (full reset)
- C. Nothing — key is only for lists
- D. React throws a warning

<details><summary>Answer</summary>B. Changing <code>key</code> tells React "this is a different instance." React unmounts the old component (runs cleanup, destroys state) and mounts a fresh instance. This is a powerful pattern for resetting component state.</details>

---

**Q34. Debugging:** A user reports that after navigating to a page and back, the scroll position is lost and data refetches. What's the architecture issue?

<details><summary>Answer</summary>
1. <strong>Data refetch:</strong> No caching layer. Use React Query with appropriate <code>staleTime</code> to keep data across navigations.<br>
2. <strong>Scroll position:</strong> Component unmounts on navigation, losing scroll state. Options: restore scroll with <code>scrollRestoration</code>, persist scroll position, or keep the component mounted (layout with outlet).
</details>

---

**Q35. Scenario:** You have a Server Component that fetches data and passes it to a Client Component. The Client Component needs to refetch on user action. How do you architect this?

<details><summary>Answer</summary>
1. Server Component fetches initial data, passes as props.<br>
2. Client Component receives initial data and uses it as <code>initialData</code> for React Query.<br>
3. React Query handles refetching, caching, and loading states client-side.<br>
This gives you the best of both worlds: fast initial load (server-fetched, zero client JS for initial render) + interactive refetching (client-side).
</details>

---

**Q36. True/False:** In React 18, all `setState` calls are automatically batched, even in timeouts and promises.

<details><summary>Answer</summary>True. React 18 introduced automatic batching for all state updates, regardless of where they occur (event handlers, promises, timeouts, native event handlers). In React 17, only event handlers were batched.</details>

---

**Q37. Single choice:** What is the primary purpose of `useSyncExternalStore`?

- A. Synchronize state between components
- B. Subscribe to external stores safely in concurrent rendering
- C. Sync server and client state
- D. Store data in localStorage

<details><summary>Answer</summary>B. <code>useSyncExternalStore</code> ensures consistent reads from external mutable stores during concurrent rendering. Without it, tearing can occur — different parts of the UI reading different versions of the store during a concurrent render.</details>

---

**Q38. Debugging:** Your SSR page shows a hydration mismatch warning. The server renders "10:30 AM" but the client renders "10:30 PM". What's happening?

<details><summary>Answer</summary>The server and client are in different time zones. <code>new Date().toLocaleTimeString()</code> produces different output on server vs. client. Fix: use <code>suppressHydrationWarning</code> for this element, render a placeholder on server and update on client, or ensure consistent timezone handling (UTC).</details>

---

**Q39. Design question:** You're building a component library used by 10 teams. How do you decide the component API surface (which props to expose)?

<details><summary>Answer</summary>
1. <strong>Start minimal</strong> — only expose what's needed. It's easier to add props than remove them.<br>
2. <strong>Use composition over configuration</strong> — prefer <code>&lt;Select&gt;&lt;Option /&gt;&lt;/Select&gt;</code> over <code>&lt;Select options={[...]} /&gt;</code>.<br>
3. <strong>Support <code>className</code> and style overrides</strong> — don't lock down styling.<br>
4. <strong>Use discriminated unions for variants</strong> — <code>variant: 'primary' | 'secondary'</code>.<br>
5. <strong>Forward refs</strong> — consumers may need DOM access.<br>
6. <strong>Extend native element props</strong> — <code>ButtonProps extends ButtonHTMLAttributes</code>.
</details>

---

**Q40. Scenario:** `useTransition` is wrapping a state update, but the UI still feels janky. Why?

<details><summary>Answer</summary>
Possible causes:<br>
1. The <strong>rendering itself</strong> is expensive (many components) — transitions can interrupt, but each chunk still needs time.<br>
2. The expensive work is in the <strong>commit phase</strong> (DOM mutations) — transitions only help with render phase.<br>
3. The expensive work is <strong>synchronous layout/paint</strong> — transitions don't help with CSS/layout costs.<br>
4. The component is <strong>not concurrent-safe</strong> — it reads from mutable sources that change during render.<br>
Profile to identify whether the bottleneck is React render, DOM mutation, or browser layout/paint.
</details>

---

**Q41. True/False:** Suspense boundaries catch errors thrown by child components.

<details><summary>Answer</summary>False. Suspense catches <em>promises</em> thrown during render (pending state). <strong>Error boundaries</strong> catch errors. They are different mechanisms. You often need both at the same boundary level.</details>

---

**Q42. Fill in the blank:** React's reconciliation algorithm is O(______) because it uses heuristics: different element types produce different trees, and keys provide stable identity.

<details><summary>Answer</summary><code>n</code>. A general tree diff is O(n³). React's heuristic-based approach is O(n) by assuming: 1) different types → different trees, 2) keys provide identity. This is fast at the cost of occasionally unnecessary unmount/remount.</details>

---

**Q43. Scenario:** In a concurrent render, your component reads from a global mutable variable that another part of the app modifies. What can go wrong?

<details><summary>Answer</summary><strong>Tearing.</strong> Concurrent rendering can pause and resume. If the global variable changes between pauses, different parts of the component tree read different values, producing an inconsistent UI. Fix: use <code>useSyncExternalStore</code> to ensure consistent reads, or move the value into React state.</details>

---

**Q44. Design question:** You need to choose between putting a complex calculation in `useMemo` or moving it to a Web Worker. How do you decide?

<details><summary>Answer</summary>
<code>useMemo</code>: Caches the result, but still runs on the main thread. Good for expensive-but-fast computations (< 16ms).<br>
<strong>Web Worker</strong>: Runs off the main thread, but has serialization overhead (data must be cloned/transferred). Good for truly heavy work (> 16ms) that would block the UI.<br>
Measure with DevTools. If the computation takes > 1 frame (16ms), consider a Worker. If it's < 5ms but runs often, <code>useMemo</code> is sufficient.
</details>

---

**Q45. Debugging:** A production app crashes with "Maximum update depth exceeded." The error points to a component with `useEffect`. What's the investigation checklist?

<details><summary>Answer</summary>
1. Check if <code>useEffect</code> sets state that's also in its dependency array (effect → setState → re-render → effect → loop).<br>
2. Check for object/array dependencies that are recreated every render (new reference → effect runs → setState → loop).<br>
3. Check for parent re-renders causing prop changes that trigger the effect.<br>
4. Add a counter log in the effect to confirm the loop.<br>
5. Fix: stabilize dependencies with useMemo, use functional setState, or restructure to remove the dependency cycle.
</details>

---

**Q46. Scenario:** You have a Next.js App Router project. A page loads slowly because it imports a heavy charting library. The chart is below the fold. How do you optimize?

<details><summary>Answer</summary>
1. <strong>Dynamic import</strong> with <code>next/dynamic</code> or <code>React.lazy</code> — don't load the charting library until needed.<br>
2. <strong>Intersection Observer</strong> — only load when the chart scrolls into view.<br>
3. <strong>Suspense boundary</strong> — show a skeleton while the chart loads.<br>
4. If the chart is purely visual (no interactivity), consider rendering it as a <strong>Server Component</strong> or even as an image/SVG.
</details>

---

**Q47. True/False:** React Server Components can use `useState` and `useEffect`.

<details><summary>Answer</summary>False. Server Components run only on the server and cannot use hooks that depend on client-side state or lifecycle (<code>useState</code>, <code>useEffect</code>, <code>useContext</code>, etc.). They can use <code>async/await</code> instead. For interactivity, use Client Components (<code>'use client'</code>).</details>

---

**Q48. Design question:** Your team has 30 engineers contributing to one Next.js app. How do you prevent merge conflicts and ensure consistent architecture?

<details><summary>Answer</summary>
1. <strong>Feature folder structure</strong> — each team owns a feature module with clear boundaries.<br>
2. <strong>Shared component library</strong> — design system as a shared package.<br>
3. <strong>Code owners</strong> — CODEOWNERS file for review routing.<br>
4. <strong>Architectural Decision Records (ADRs)</strong> — document conventions.<br>
5. <strong>ESLint rules</strong> — enforce import boundaries between features.<br>
6. <strong>CI checks</strong> — bundle size budgets, type checking, tests.<br>
7. <strong>Monorepo</strong> (Turborepo) — independent packages reduce coupling.
</details>

---

**Q49. Scenario:** After upgrading to React 18, some of your tests fail because state updates are now batched differently. How do you fix them?

<details><summary>Answer</summary>React 18 batches all state updates (including those in promises and timeouts). Tests that relied on intermediate renders between setState calls may fail. Fix: wrap state updates in <code>act()</code>, use <code>waitFor</code> from Testing Library, or update assertions to expect the final batched state.</details>

---

**Q50. Design question:** You're building a real-time collaborative editor (like Google Docs). What React architecture decisions are critical?

<details><summary>Answer</summary>
1. <strong>State:</strong> CRDT or OT library (Yjs, Automerge) — NOT React state for the document model.<br>
2. <strong>Rendering:</strong> Virtualize the document for large texts. Only render visible portions.<br>
3. <strong>Updates:</strong> Use <code>useSyncExternalStore</code> to subscribe to the CRDT store.<br>
4. <strong>Cursors:</strong> Other users' cursors are overlaid, updated via WebSocket.<br>
5. <strong>Offline:</strong> CRDT handles conflict resolution. Sync on reconnect.<br>
6. <strong>Performance:</strong> Debounce sync operations. Use Web Workers for CRDT operations.<br>
7. <strong>React's role:</strong> React renders the UI. The document state lives outside React.
</details>

---

## 8. Personalized Recommendations

### React Core concepts to master first

| Priority | Concept | Why |
|---|---|---|
| 1 | Render/commit lifecycle | Foundation for everything — understand when and why components re-render |
| 2 | State management patterns | Know when to use local, URL, context, external, and server state |
| 3 | useEffect correctly | Most misused hook — learn when to use it and when not to |
| 4 | Composition patterns | Senior-level component design — children, slots, compound components |
| 5 | Reconciliation and keys | Understand performance at the framework level |
| 6 | Concurrent rendering | useTransition, Suspense — React's future |
| 7 | Server Components | The Next.js App Router model — where React is heading |
| 8 | Performance profiling | DevTools, Profiler, bundle analysis — evidence-based optimization |

### Advanced topics that matter most for your stack

| Topic | Why it matters for you |
|---|---|
| React Server Components | Next.js App Router is built on RSC — essential |
| Streaming SSR | Understand how Next.js renders and hydrates |
| Code splitting with lazy + Suspense | Bundle optimization for Next.js and Astro |
| React Query integration | Server state management in any React app |
| Design system architecture | Scale UI across projects |
| React Compiler | Will change how you write components (no more manual memoization) |

### Common mistakes frontend engineers make

| Mistake | Why it happens | Fix |
|---|---|---|
| Over-using useEffect | Treating it as a lifecycle method | Derive state, handle in events, use React Query |
| Global state for everything | "It's easier" | Colocate state, use URL state, server state |
| Not profiling before optimizing | "Memoize everything" | Profile first, optimize measured bottlenecks |
| Ignoring accessibility | "We'll add it later" | Build accessible from day one |
| Massive components | "Just add another feature" | Extract hooks and sub-components early |
| Testing implementation | "Mock useState" | Test behavior with Testing Library |
| Skipping error boundaries | "It won't crash" | Every route should have an error boundary |
| Not code-splitting | "The app is small" | Split at route level from the start |

### How to evolve from component developer to frontend architect

```text
Phase 1: Component Mastery
  └── Build any component with proper state, effects, composition

Phase 2: Pattern Recognition
  └── Identify anti-patterns, choose correct state location, optimize renders

Phase 3: System Design
  └── Design component architecture, state architecture, data flow

Phase 4: Performance Engineering
  └── Profile, measure, optimize with evidence. Bundle budgets.

Phase 5: Architecture Leadership
  └── Design system, monorepo strategy, team conventions, ADRs

Phase 6: Framework Understanding
  └── Fiber, scheduler, RSC, compiler. Understand WHY React works this way.

Phase 7: Cross-Cutting Concerns
  └── Accessibility, testing strategy, CI/CD, monitoring, observability
```

### 30-day learning plan

#### Week 1: Rendering Internals (Days 1–7)

| Day | Task | Deliverable |
|---|---|---|
| 1 | Read React docs: "Render and Commit" | Mental model diagram |
| 2 | Build: component that logs render count | Understanding of re-render triggers |
| 3 | Profile an app with React DevTools Profiler | Identify unnecessary re-renders |
| 4 | Study: reconciliation algorithm | Can explain O(n) diff heuristics |
| 5 | Build: optimize a slow list with React.memo | Before/after profiling comparison |
| 6 | Study: "children as props" optimization pattern | Implement in a real component |
| 7 | Study: fiber architecture overview | Can explain double buffering, work loop |

#### Week 2: Hooks Mastery (Days 8–14)

| Day | Task | Deliverable |
|---|---|---|
| 8 | Read: "You Might Not Need an Effect" | List of effects to refactor |
| 9 | Refactor: replace useEffect-based derived state with direct computation | Cleaner code |
| 10 | Build: custom hook with proper cleanup (useMediaQuery) | Reusable hook |
| 11 | Study: useCallback/useMemo — when they help vs. hurt | Decision framework |
| 12 | Build: context + custom hook with memoization | Type-safe, optimized context |
| 13 | Study: useReducer for complex state | Implement a multi-step form |
| 14 | Build: form with React Hook Form + Zod | Production-ready form |

#### Week 3: Concurrent & Server (Days 15–21)

| Day | Task | Deliverable |
|---|---|---|
| 15 | Study: useTransition and useDeferredValue | Implement search with transition |
| 16 | Build: Suspense with React Query (useSuspenseQuery) | Suspense-based data loading |
| 17 | Study: Error Boundaries | Implement route-level error boundaries |
| 18 | Study: React Server Components model | Mental model of server/client boundary |
| 19 | Build: Next.js page with Server + Client Components | Working RSC page |
| 20 | Study: Streaming SSR in Next.js | Understand how loading.tsx works |
| 21 | Study: hydration — what it is, what goes wrong | Can debug hydration mismatches |

#### Week 4: Architecture (Days 22–30)

| Day | Task | Deliverable |
|---|---|---|
| 22 | Design: state architecture for a medium app | Architecture diagram |
| 23 | Build: Zustand store with selectors | Optimized global state |
| 24 | Study: code splitting with lazy + Suspense | Implement route-level splitting |
| 25 | Study: design system patterns (compound components, Radix) | Component API design |
| 26 | Study: testing strategy (Testing Library + MSW) | Integration test for a feature |
| 27 | Study: bundle analysis (source-map-explorer) | Bundle size budget |
| 28 | Study: accessibility audit (axe, keyboard nav) | Accessibility checklist |
| 29 | Study: React Compiler | Understand what it automates |
| 30 | Write: architecture decision record for your project | ADR document |

---

## 9. Official Documentation & Reference Links

### Beginner

- [React docs — Learn React](https://react.dev/learn) — Start here. The official tutorial covers all fundamentals.
- [React docs — Describing the UI](https://react.dev/learn/describing-the-ui) — JSX, components, props, conditional rendering, lists.
- [React docs — Adding Interactivity](https://react.dev/learn/adding-interactivity) — State, events, rendering and committing.
- [React docs — Managing State](https://react.dev/learn/managing-state) — State design principles, lifting state, reducers, context.
- [React docs — Hooks API Reference](https://react.dev/reference/react/hooks) — Complete hook reference.

### Intermediate

- [React docs — You Might Not Need an Effect](https://react.dev/learn/you-might-not-need-an-effect) — Essential for avoiding useEffect anti-patterns.
- [React docs — Synchronizing with Effects](https://react.dev/learn/synchronizing-with-effects) — Deep dive on useEffect.
- [React docs — Reusing Logic with Custom Hooks](https://react.dev/learn/reusing-logic-with-custom-hooks) — Custom hook patterns.
- [React docs — Referencing Values with Refs](https://react.dev/learn/referencing-values-with-refs) — When and how to use refs.
- [React docs — Separating Events from Effects](https://react.dev/learn/separating-events-from-effects) — Critical distinction.
- [TanStack Query docs](https://tanstack.com/query/latest) — Server state management.
- [Testing Library docs](https://testing-library.com/docs/react-testing-library/intro/) — Component testing.
- [Zustand GitHub](https://github.com/pmndrs/zustand) — Minimal state management.

### Advanced

- [React docs — useTransition](https://react.dev/reference/react/useTransition) — Concurrent rendering.
- [React docs — Suspense](https://react.dev/reference/react/Suspense) — Loading states and code splitting.
- [React docs — React Compiler](https://react.dev/learn/react-compiler) — Automatic memoization.
- [React docs — Server Components](https://react.dev/reference/rsc/server-components) — RSC reference.
- [Next.js docs — App Router](https://nextjs.org/docs/app) — Server Components in practice.
- [Dan Abramov — A Complete Guide to useEffect](https://overreacted.io/a-complete-guide-to-useeffect/) — Deep mental model.
- [Dan Abramov — Before You memo()](https://overreacted.io/before-you-memo/) — Composition before memoization.
- [Kent C. Dodds — Application State Management with React](https://kentcdodds.com/blog/application-state-management-with-react) — State architecture.
- [Radix UI](https://www.radix-ui.com/) — Accessible component primitives.

### Expert / Internals

- [React RFCs Repository](https://github.com/reactjs/rfcs) — Proposals for new features.
- [React Source Code](https://github.com/facebook/react) — Read the implementation.
- [Andrew Clark — React Fiber Architecture](https://github.com/acdlite/react-fiber-architecture) — Fiber explained.
- [React Working Group discussions](https://github.com/reactwg) — Internal discussions on React 18+, Server Components.
- [Sebastian Markbåge — React Server Components RFC](https://github.com/reactjs/rfcs/blob/main/text/0188-server-components.md) — Original RSC proposal.
- [React docs — React 18 release](https://react.dev/blog/2022/03/29/react-v18) — Concurrent rendering rationale.
- [Astro docs — React integration](https://docs.astro.build/en/guides/integrations-guide/react/) — React islands in Astro.
- [Vite docs](https://vite.dev/) — Build tooling for React SPAs.

---

## Summary, Next Steps, and Advanced Topics

### Concise Summary

React is a **declarative UI library** built on a **virtual DOM reconciliation engine**. Its core loop is: state changes → component re-renders → diff → minimal DOM mutations. The key to mastery is understanding:

1. **Rendering model:** Components are functions. Renders are cheap. Commits are expensive. Don't fear re-renders — understand them.
2. **State architecture:** Colocate state. Use the right tool for each type (local, URL, context, external, server).
3. **Composition:** Build UIs from small, focused components. Prefer composition over configuration.
4. **Concurrent rendering:** React's unique advantage. `useTransition` and `Suspense` enable responsive UIs under load.
5. **Server Components:** React's future direction. Server-first rendering with selective client interactivity.
6. **Performance:** Profile first, optimize second. Virtualize long lists. Split code at routes. Memoize only what's measured as expensive.

### Next Steps

1. Build a real project using the render/commit mental model — log renders, profile, optimize.
2. Refactor existing useEffect calls — remove derived state effects, add cleanups.
3. Implement Suspense + React Query for data fetching.
4. Migrate a page to Server Components (Next.js App Router).
5. Build a custom hook library for your team.
6. Set up bundle size monitoring.

### Suggested Advanced Topics

| Topic | Why it matters |
|---|---|
| React Compiler (React Forget) | Will eliminate manual memoization |
| React Server Actions | Server-side mutations from Client Components |
| Partial Prerendering (PPR) | Next.js's hybrid static/dynamic rendering |
| Signals debate | Alternative reactivity model (Preact, Angular, Solid) |
| View Transitions API | Native browser page transitions |
| WASM in React | Heavy computation in the browser |
| React Native cross-platform | Shared logic between web and mobile |
| Micro-frontends | Scaling React across teams |
| Module Federation | Sharing code between independently deployed apps |
| Edge rendering | React on Cloudflare Workers / Deno Deploy |
