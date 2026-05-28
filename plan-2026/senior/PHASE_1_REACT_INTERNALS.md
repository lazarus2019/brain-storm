# Phase 1 — Craft Track Deep Dive

> **Target:** Junior → FAANG-ready React/TypeScript engineer **Duration:** 0–3 months (parallel with DSA track) **Goal:** Understand _why_ your tools work, not just _how_ to use them

---

## Table of Contents

1. [React Reconciliation + Fiber](https://claude.ai/chat/66caa6a7-7c60-4209-93d6-c254a560cf68#1-react-reconciliation--fiber)
2. [useEffect Mental Model](https://claude.ai/chat/66caa6a7-7c60-4209-93d6-c254a560cf68#2-useeffect-mental-model-sync-not-lifecycle)
3. [TypeScript Depth](https://claude.ai/chat/66caa6a7-7c60-4209-93d6-c254a560cf68#3-typescript-depth-generics-utility-types-narrowing)
4. [Custom Hook Composition](https://claude.ai/chat/66caa6a7-7c60-4209-93d6-c254a560cf68#4-custom-hook-composition-patterns)

---

## 1. React Reconciliation + Fiber

### What it is

Reconciliation is the algorithm React uses to determine **what changed** between renders and **what DOM operations to perform** as a result. Fiber is the internal architecture (introduced in React 16) that makes reconciliation interruptible, prioritizable, and async-capable.

Understanding this is what separates engineers who can _use_ React from engineers who can _reason_ about React — a distinction FAANG interviewers actively probe.

---

### 1.1 The Virtual DOM

React never writes directly to the DOM on every state change. Instead, it maintains an in-memory tree of plain JavaScript objects called the **Virtual DOM (vDOM)**.

```
Real DOM (expensive)         Virtual DOM (cheap JS objects)
<div class="card">    →     { type: 'div', props: { className: 'card' },
  <h1>Title</h1>              children: [
  <p>Body</p>                   { type: 'h1', props: {}, children: ['Title'] },
</div>                          { type: 'p',  props: {}, children: ['Body'] }
                              ]}
```

When state changes, React produces a **new vDOM tree**, diffs it against the **previous vDOM tree**, and only applies the minimal set of real DOM mutations. This diff process is reconciliation.

**Why this matters:** DOM operations are expensive (they trigger layout/paint). Diffing two JS objects is cheap. React batches and minimizes DOM writes.

---

### 1.2 The Diffing Algorithm (O(n) Heuristics)

A naive tree diff is O(n³). React achieves O(n) using two heuristics:

**Heuristic 1: Elements of different types produce entirely different trees.**

```jsx
// Before
<div><Counter /></div>

// After
<span><Counter /></span>
```

React does not attempt to reuse `Counter`. It tears down the entire subtree and rebuilds it. The `Counter` component is **unmounted and remounted** — state is lost.

**Heuristic 2: The `key` prop signals stable identity across renders.**

```jsx
// Without keys — React diffs by position
// Inserting at the start forces re-render of ALL items
<ul>
  <li>Alice</li>
  <li>Bob</li>
</ul>

// With keys — React diffs by identity
// Only the new item is inserted; Alice and Bob are untouched
<ul>
  <li key="alice">Alice</li>
  <li key="bob">Bob</li>
</ul>
```

**Common mistake:** Using array index as key. When items reorder, their indices change but their keys don't "move" with them — React mismaps old state to new positions.

```jsx
// Dangerous — key = index
{items.map((item, i) => <Row key={i} data={item} />)}

// Correct — key = stable unique identity
{items.map(item => <Row key={item.id} data={item} />)}
```

---

### 1.3 React Fiber: The Architecture

Before Fiber (React ≤15), reconciliation was **synchronous and uninterruptible**. A large tree diff blocked the main thread until it finished — causing dropped frames and janky UIs.

Fiber solves this by representing every unit of work as a **fiber node** — a plain JS object that acts as a linked list node:

```
Fiber Node {
  type,          // element type (div, Component, etc.)
  stateNode,     // reference to real DOM node or class instance
  child,         // first child fiber
  sibling,       // next sibling fiber
  return,        // parent fiber
  pendingProps,
  memoizedProps,
  memoizedState,
  effectTag,     // what mutation to perform (PLACEMENT, UPDATE, DELETION)
  alternate,     // the previous fiber (double-buffering)
}
```

React maintains **two fiber trees** at all times:

- **Current tree** — what's on screen right now
- **Work-in-progress (WIP) tree** — what React is building for the next render

This is called **double buffering**. React builds the WIP tree in the background, then atomically swaps it to current when done.

---

### 1.4 Two Phases of Rendering

**Render phase (interruptible)**

React traverses the fiber tree, runs your component functions, and builds the WIP tree. This phase can be **paused, resumed, or aborted** — which is what enables Concurrent Mode features like `useTransition` and `Suspense`.

```
render phase:
  beginWork(fiber)  →  run component fn → produce child fibers
  completeWork(fiber) → collect DOM mutations into effect list
```

No side effects happen here. This phase is pure.

**Commit phase (synchronous, uninterruptible)**

React walks the effect list and **applies DOM mutations**. This phase cannot be interrupted — a partial DOM update would leave the UI in an inconsistent state.

```
commit phase:
  commitBeforeMutationEffects   → snapshot (getSnapshotBeforeUpdate)
  commitMutationEffects         → apply DOM insertions/updates/deletions
  commitLayoutEffects           → fire useLayoutEffect, componentDidMount/Update
  ← React yields to browser ←
  commitPassiveEffects          → fire useEffect (scheduled async)
```

**Key takeaway:** `useLayoutEffect` fires synchronously during the commit phase, before the browser paints. `useEffect` fires asynchronously after the browser paints. This is not a minor detail — it determines whether your effect causes a visible flash.

---

### 1.5 What Triggers a Re-render

Knowing this prevents unnecessary renders — a real skill gap for most juniors:

|Trigger|Behavior|
|---|---|
|`setState` / `useState` setter|Re-renders that component and all its descendants|
|`useReducer` dispatch|Same as above|
|`useContext` value change|Re-renders every consumer of that context|
|Parent re-renders|Re-renders all children by default|
|`forceUpdate` (class)|Forces re-render regardless of state|

React does **not** automatically bail out child renders. Every parent re-render causes every child to re-render unless you opt out with `React.memo`, `useMemo`, or `useCallback`.

```jsx
// Child re-renders every time Parent re-renders
function Parent() {
  const [count, setCount] = useState(0);
  return <ExpensiveChild />;  // runs on every Parent render
}

// Child only re-renders if its props change
const ExpensiveChild = React.memo(function ExpensiveChild(props) {
  return <div>...</div>;
});
```

**When to use `React.memo`:** Only when the component is demonstrably expensive and its parent re-renders often. Don't apply it everywhere — the comparison itself has a cost.

---

### 1.6 Interview Questions This Enables You to Answer

- _Why do React keys matter, and what happens if you use array index?_
- _What's the difference between render phase and commit phase?_
- _Why does `useLayoutEffect` exist when we have `useEffect`?_
- _How does React decide whether to re-render a child component?_
- _What is the Virtual DOM and why doesn't it guarantee performance?_

---

## 2. useEffect Mental Model: Sync, Not Lifecycle

### The core shift

Most juniors learn `useEffect` as a translation of class lifecycle methods:

```
componentDidMount    →  useEffect(() => {}, [])
componentDidUpdate   →  useEffect(() => {})
componentWillUnmount →  useEffect(() => { return () => {} }, [])
```

This mental model is **wrong** and causes subtle bugs. The correct mental model:

> **`useEffect` synchronizes your component with an external system.**

The dependency array doesn't say _when to run_. It says _what the effect depends on_. React runs the effect whenever the values in the dep array differ from the last render.

---

### 2.1 The Correct Model: Snapshots and Synchronization

Every render is a **snapshot**. When your component renders, React calls your function and captures the result — including all the values your effect will close over.

```jsx
function Timer({ delay }) {
  const [count, setCount] = useState(0);

  useEffect(() => {
    // This function closes over the `delay` from THIS render's snapshot
    // If `delay` changes, this effect cleans up and a new one starts
    const id = setInterval(() => {
      setCount(c => c + 1);  // functional update avoids stale closure
    }, delay);

    return () => clearInterval(id);
  }, [delay]);  // Effect depends on `delay` — re-syncs when it changes
}
```

The cleanup function (`return () => clearInterval(id)`) is not `componentWillUnmount`. It runs **before every re-execution of the effect** (when deps change) and on unmount. Its job is to unsync — undo what the effect did.

---

### 2.2 The Stale Closure Problem

The most common `useEffect` bug in production:

```jsx
function SearchBox() {
  const [query, setQuery] = useState('');

  useEffect(() => {
    // BUG: `query` here is captured from the first render only
    // It will always be '' because the dep array is empty
    fetchResults(query).then(setResults);
  }, []); // <- empty deps "works" but reads stale query forever
}
```

**Fix:** Include all values the effect reads from the component scope in the dep array:

```jsx
useEffect(() => {
  fetchResults(query).then(setResults);
}, [query]); // correct — re-runs when query changes
```

**The ESLint rule `exhaustive-deps` exists precisely to catch this.** Don't disable it. If it's flagging something you don't understand, the rule is telling you there's a logical problem with your effect.

---

### 2.3 Race Conditions in Effects

When you fetch data inside an effect, you can get a race condition if the component re-renders before the fetch completes:

```jsx
// BUG: if userId changes fast, earlier fetches can resolve after later ones
useEffect(() => {
  fetchUser(userId).then(data => setUser(data)); // could be stale data
}, [userId]);

// FIX: use a cleanup flag (ignore pattern)
useEffect(() => {
  let ignore = false;

  fetchUser(userId).then(data => {
    if (!ignore) setUser(data); // discard result if effect was superseded
  });

  return () => { ignore = true; };
}, [userId]);
```

This pattern is fundamental. Every data-fetching effect in production code should handle this. Libraries like React Query and SWR handle it for you — which is the real reason to use them.

---

### 2.4 `useEffect` vs `useLayoutEffect` vs Event Handlers

||When it runs|Use for|
|---|---|---|
|Event handler|On user interaction|State updates, non-visual side effects|
|`useEffect`|After browser paints (async)|Data fetching, subscriptions, analytics|
|`useLayoutEffect`|After DOM mutation, before paint (sync)|Reading DOM measurements, preventing flicker|

**Rule:** If you're reading a DOM measurement (e.g. element width) and immediately updating state to reflect it, use `useLayoutEffect`. Otherwise use `useEffect`. If something shouldn't run on render at all but only on interaction, it belongs in an event handler — not an effect.

```jsx
// Wrong: this causes a visible flicker (paint → update → repaint)
useEffect(() => {
  const width = ref.current.offsetWidth;
  setWidth(width);
}, []);

// Correct: DOM is measured and state updated before the browser paints
useLayoutEffect(() => {
  const width = ref.current.offsetWidth;
  setWidth(width);
}, []);
```

---

### 2.5 Effects You Don't Need

A lot of `useEffect` usage in real codebases is unnecessary. React docs explicitly call this out:

```jsx
// ❌ Deriving state with useEffect
const [fullName, setFullName] = useState('');
useEffect(() => {
  setFullName(`${firstName} ${lastName}`);
}, [firstName, lastName]);

// ✅ Just compute it during render
const fullName = `${firstName} ${lastName}`;
```

```jsx
// ❌ Transforming data with useEffect
useEffect(() => {
  setFilteredItems(items.filter(i => i.active));
}, [items]);

// ✅ Compute during render (or useMemo if expensive)
const filteredItems = useMemo(
  () => items.filter(i => i.active),
  [items]
);
```

**Heuristic:** If your effect only sets state and doesn't interact with an external system (DOM, network, timers, subscriptions), you almost certainly don't need an effect.

---

### 2.6 Interview Questions This Enables You to Answer

- _Explain the mental model behind `useEffect`. What does the dependency array actually mean?_
- _How do you handle a race condition in a fetch inside `useEffect`?_
- _What's the difference between `useEffect` and `useLayoutEffect`?_
- _Why is an empty dependency array not always the right choice?_
- _Give an example of an effect you can eliminate._

---

## 3. TypeScript Depth: Generics, Utility Types, Narrowing

### Why this matters for FAANG

TypeScript at FAANG is not optional syntax on top of JavaScript. It's the primary tool for expressing system contracts. Engineers who know only the basics write types that are either `any`-riddled or so rigid they break on composition. Depth here signals engineering maturity.

---

### 3.1 Generics

Generics let you write code that works across types while preserving type information. They are to types what function parameters are to values.

**Basic generic function:**

```typescript
// Without generics — throws away type information
function identity(arg: any): any {
  return arg;
}

// With generics — preserves type through the call
function identity<T>(arg: T): T {
  return arg;
}

const n = identity(42);     // TypeScript infers T = number → n: number
const s = identity("hi");   // T = string → s: string
```

**Generic constraints** — restrict what `T` can be:

```typescript
// T must have a .length property
function logLength<T extends { length: number }>(value: T): T {
  console.log(value.length);
  return value;
}

logLength("hello");   // ok — string has .length
logLength([1, 2, 3]); // ok — array has .length
logLength(42);        // error — number has no .length
```

**Generic interfaces — reusable data shape contracts:**

```typescript
interface ApiResponse<T> {
  data: T;
  error: string | null;
  status: number;
}

type UserResponse   = ApiResponse<User>;
type ProductResponse = ApiResponse<Product[]>;
```

**Generic React components:**

```typescript
interface ListProps<T> {
  items: T[];
  renderItem: (item: T) => React.ReactNode;
  keyExtractor: (item: T) => string;
}

function List<T>({ items, renderItem, keyExtractor }: ListProps<T>) {
  return (
    <ul>
      {items.map(item => (
        <li key={keyExtractor(item)}>{renderItem(item)}</li>
      ))}
    </ul>
  );
}

// Usage — T inferred as User
<List
  items={users}
  renderItem={u => <span>{u.name}</span>}
  keyExtractor={u => u.id}
/>
```

---

### 3.2 Utility Types

TypeScript ships built-in utility types that transform existing types. These are the types you reach for instead of copy-pasting type definitions.

```typescript
interface User {
  id: string;
  name: string;
  email: string;
  password: string;
  role: 'admin' | 'viewer';
}

// Partial<T> — makes all properties optional
type UserUpdate = Partial<User>;
// { id?: string; name?: string; email?: string; ... }

// Required<T> — makes all properties required (inverse of Partial)
type StrictUser = Required<User>;

// Pick<T, K> — select specific properties
type UserPublic = Pick<User, 'id' | 'name' | 'role'>;
// { id: string; name: string; role: 'admin' | 'viewer' }

// Omit<T, K> — exclude specific properties
type UserSafe = Omit<User, 'password'>;
// { id: string; name: string; email: string; role: ... }

// Readonly<T> — prevent mutation
type FrozenUser = Readonly<User>;

// Record<K, V> — map of keys to values
type RolePermissions = Record<User['role'], string[]>;
// { admin: string[]; viewer: string[] }

// ReturnType<T> — extract a function's return type
function getUser() { return { id: '1', name: 'Alice' }; }
type UserShape = ReturnType<typeof getUser>;
// { id: string; name: string }

// Parameters<T> — extract a function's parameter types as a tuple
type GetUserParams = Parameters<typeof getUser>;

// NonNullable<T> — remove null and undefined
type Id = NonNullable<string | null | undefined>; // string

// Extract<T, U> and Exclude<T, U>
type Events = 'click' | 'focus' | 'blur' | 'change';
type FocusEvents = Extract<Events, 'focus' | 'blur'>;  // 'focus' | 'blur'
type NonFocus  = Exclude<Events, 'focus' | 'blur'>;    // 'click' | 'change'
```

**Building your own utility types:**

```typescript
// DeepPartial — recursively makes all nested properties optional
type DeepPartial<T> = T extends object
  ? { [P in keyof T]?: DeepPartial<T[P]> }
  : T;

// Nullable<T> — adds null to every value type
type Nullable<T> = { [P in keyof T]: T[P] | null };
```

---

### 3.3 Type Narrowing

Narrowing is how TypeScript refines a broad type to a more specific one inside a conditional block. This is where most junior TS code breaks down — types feel too loose, so engineers reach for `as` casts, which defeat the purpose.

**`typeof` narrowing:**

```typescript
function format(value: string | number): string {
  if (typeof value === 'string') {
    return value.toUpperCase(); // TypeScript knows: value is string here
  }
  return value.toFixed(2); // TypeScript knows: value is number here
}
```

**`in` narrowing — checking for property existence:**

```typescript
type Cat = { meow: () => void };
type Dog = { bark: () => void };

function speak(animal: Cat | Dog) {
  if ('meow' in animal) {
    animal.meow(); // narrowed to Cat
  } else {
    animal.bark(); // narrowed to Dog
  }
}
```

**Discriminated unions — the most powerful pattern:**

```typescript
type LoadingState = { status: 'loading' };
type SuccessState = { status: 'success'; data: User[] };
type ErrorState   = { status: 'error'; message: string };

type State = LoadingState | SuccessState | ErrorState;

function render(state: State) {
  switch (state.status) {
    case 'loading':
      return <Spinner />;
    case 'success':
      return <List data={state.data} />; // state.data is available here
    case 'error':
      return <Error msg={state.message} />; // state.message is available here
  }
}
```

**User-defined type guards — when built-ins aren't enough:**

```typescript
// Without type guard — TypeScript can't narrow after this
function isUser(value: unknown): boolean {
  return typeof value === 'object' && value !== null && 'id' in value;
}

// With type guard — TypeScript narrows correctly after calling this
function isUser(value: unknown): value is User {
  return typeof value === 'object' && value !== null && 'id' in value;
}

const data: unknown = fetchSomething();
if (isUser(data)) {
  console.log(data.id); // data: User — safe to access
}
```

**The `never` type as exhaustiveness check:**

```typescript
function assertNever(value: never): never {
  throw new Error(`Unhandled case: ${JSON.stringify(value)}`);
}

function render(state: State) {
  switch (state.status) {
    case 'loading': return <Spinner />;
    case 'success': return <List data={state.data} />;
    case 'error':   return <Error msg={state.message} />;
    default:
      // If you add a new status type and forget to handle it,
      // TypeScript will error here at compile time — not at runtime
      return assertNever(state);
  }
}
```

---

### 3.4 Conditional Types

Used to express type logic that depends on another type:

```typescript
// If T extends U, resolve to X, otherwise Y
type IsArray<T> = T extends any[] ? true : false;

type A = IsArray<string[]>; // true
type B = IsArray<string>;   // false

// infer — extract a type from within a conditional
type UnpackArray<T> = T extends (infer Item)[] ? Item : T;

type C = UnpackArray<User[]>; // User
type D = UnpackArray<string>; // string
```

---

### 3.5 Interview Questions This Enables You to Answer

- _What's the difference between `Partial<T>` and `DeepPartial<T>`?_
- _How would you type a reusable data-fetching hook so it works for any resource?_
- _What is a discriminated union and why is it better than optional properties?_
- _How does TypeScript narrow types, and what is a user-defined type guard?_
- _What is the `never` type useful for?_

---

## 4. Custom Hook Composition Patterns

### What separates senior hook design

Juniors extract logic into custom hooks. Seniors design hooks with clean interfaces, controlled coupling, and composable contracts — the same way they design APIs. Custom hooks are your component's public API surface.

---

### 4.1 The Extraction Pattern

The baseline — move stateful logic out of components when it's reused or complex:

```typescript
// Before: logic tangled inside component
function UserProfile({ userId }: { userId: string }) {
  const [user, setUser]     = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError]   = useState<Error | null>(null);

  useEffect(() => {
    let ignore = false;
    setLoading(true);
    fetchUser(userId)
      .then(data  => { if (!ignore) { setUser(data); setLoading(false); } })
      .catch(err  => { if (!ignore) { setError(err); setLoading(false); } });
    return () => { ignore = true; };
  }, [userId]);

  // ...
}

// After: reusable, testable, composable
function useUser(userId: string) {
  const [user, setUser]     = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError]   = useState<Error | null>(null);

  useEffect(() => {
    let ignore = false;
    setLoading(true);
    fetchUser(userId)
      .then(data => { if (!ignore) { setUser(data); setLoading(false); } })
      .catch(err => { if (!ignore) { setError(err); setLoading(false); } });
    return () => { ignore = true; };
  }, [userId]);

  return { user, loading, error };
}
```

---

### 4.2 The Generic Resource Hook

The pattern above applied generically — one hook for any async resource:

```typescript
type AsyncState<T> =
  | { status: 'idle' }
  | { status: 'loading' }
  | { status: 'success'; data: T }
  | { status: 'error'; error: Error };

function useAsync<T>(
  asyncFn: () => Promise<T>,
  deps: React.DependencyList
): AsyncState<T> {
  const [state, setState] = useState<AsyncState<T>>({ status: 'idle' });

  useEffect(() => {
    let ignore = false;
    setState({ status: 'loading' });

    asyncFn()
      .then(data  => { if (!ignore) setState({ status: 'success', data }); })
      .catch(error => { if (!ignore) setState({ status: 'error', error }); });

    return () => { ignore = true; };
  }, deps); // eslint-disable-line react-hooks/exhaustive-deps

  return state;
}

// Usage
const state = useAsync(() => fetchUser(userId), [userId]);

if (state.status === 'loading') return <Spinner />;
if (state.status === 'error')   return <Error msg={state.error.message} />;
if (state.status === 'success') return <Profile user={state.data} />;
```

Note the discriminated union return type — TypeScript narrows `state.data` and `state.error` correctly in each branch.

---

### 4.3 The Observer Pattern Hook

Subscribe to external event sources and clean up correctly:

```typescript
function useWindowSize() {
  const [size, setSize] = useState({
    width:  window.innerWidth,
    height: window.innerHeight,
  });

  useEffect(() => {
    function handleResize() {
      setSize({ width: window.innerWidth, height: window.innerHeight });
    }

    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []); // no deps — the listener never needs to change

  return size;
}

// Composable: use it in any component
function ResponsiveLayout() {
  const { width } = useWindowSize();
  return width < 768 ? <MobileNav /> : <DesktopNav />;
}
```

---

### 4.4 The Reducer Pattern Hook

When hook state has multiple sub-values that transition together, a reducer is cleaner than multiple `useState` calls:

```typescript
type FormState = {
  values: Record<string, string>;
  errors: Record<string, string>;
  isSubmitting: boolean;
};

type FormAction =
  | { type: 'FIELD_CHANGE'; field: string; value: string }
  | { type: 'SUBMIT_START' }
  | { type: 'SUBMIT_SUCCESS' }
  | { type: 'SUBMIT_ERROR'; errors: Record<string, string> };

function formReducer(state: FormState, action: FormAction): FormState {
  switch (action.type) {
    case 'FIELD_CHANGE':
      return { ...state, values: { ...state.values, [action.field]: action.value } };
    case 'SUBMIT_START':
      return { ...state, isSubmitting: true };
    case 'SUBMIT_SUCCESS':
      return { ...state, isSubmitting: false, errors: {} };
    case 'SUBMIT_ERROR':
      return { ...state, isSubmitting: false, errors: action.errors };
  }
}

function useForm(initialValues: Record<string, string>) {
  const [state, dispatch] = useReducer(formReducer, {
    values: initialValues,
    errors: {},
    isSubmitting: false,
  });

  const handleChange = useCallback((field: string, value: string) => {
    dispatch({ type: 'FIELD_CHANGE', field, value });
  }, []);

  const handleSubmit = useCallback(async (onSubmit: (v: typeof state.values) => Promise<void>) => {
    dispatch({ type: 'SUBMIT_START' });
    try {
      await onSubmit(state.values);
      dispatch({ type: 'SUBMIT_SUCCESS' });
    } catch (err) {
      dispatch({ type: 'SUBMIT_ERROR', errors: { _root: (err as Error).message } });
    }
  }, [state.values]);

  return { ...state, handleChange, handleSubmit };
}
```

---

### 4.5 Composing Hooks (Not Nesting Components)

The real power of hooks is composition — building complex behavior by calling simple hooks:

```typescript
// Each hook has one responsibility
function useMediaQuery(query: string): boolean {
  const [matches, setMatches] = useState(() => matchMedia(query).matches);

  useEffect(() => {
    const mql = matchMedia(query);
    const handler = (e: MediaQueryListEvent) => setMatches(e.matches);
    mql.addEventListener('change', handler);
    return () => mql.removeEventListener('change', handler);
  }, [query]);

  return matches;
}

function useIsMobile(): boolean {
  return useMediaQuery('(max-width: 767px)');
}

function usePrefersDark(): boolean {
  return useMediaQuery('(prefers-color-scheme: dark)');
}

// Compose: build higher-level hooks from primitives
function useTheme() {
  const isMobile   = useIsMobile();
  const prefersDark = usePrefersDark();
  const { user }   = useUser(currentUserId);

  return {
    isMobile,
    isDark: user?.themeOverride ?? prefersDark,
    spacing: isMobile ? 'compact' : 'comfortable',
  };
}
```

---

### 4.6 Hook Design Principles (Senior Signal)

|Principle|What it means|
|---|---|
|Single responsibility|One hook, one concern. Don't build `useEverything`.|
|Stable interface|Return object, not positional tuple, when returning multiple values.|
|Correct cleanup|Every subscription, timer, and listener has a corresponding cleanup.|
|Avoid internal effects for derived state|Compute from existing state, don't useEffect → setState for it.|
|Type the return explicitly|Discriminated union return types > `{ data, loading, error }` with all optional.|
|Don't over-abstract early|Extract when you have ≥2 real use cases, not speculatively.|

---

### 4.7 Interview Questions This Enables You to Answer

- _Design a `usePagination` hook. What does it expose and why?_
- _How would you handle race conditions in a data-fetching hook?_
- _When would you use `useReducer` inside a hook instead of `useState`?_
- _What are the rules of hooks, and what breaks if you violate them?_
- _How do you test a custom hook?_

---

## Phase 1 Craft Track — Weekly Schedule

|Week|Focus|
|---|---|
|1–2|React: vDOM, reconciliation algorithm, key prop mechanics|
|3–4|React: Fiber architecture, render vs commit phase|
|5–6|`useEffect` mental model, stale closures, race conditions|
|7–8|TypeScript: generics, utility types|
|9–10|TypeScript: narrowing, discriminated unions, conditional types|
|11–12|Custom hooks: extraction, composition, reducer pattern|

**Daily habit:** Pick one thing you used this week, find its source code or spec, read 30 minutes of it. No tutorials — primary sources only.

---

## Primary Sources

|Topic|Source|
|---|---|
|React reconciliation|[react.dev — Preserving and Resetting State](https://react.dev/learn/preserving-and-resetting-state)|
|React Fiber internals|[acdlite/react-fiber-architecture (GitHub)](https://github.com/acdlite/react-fiber-architecture)|
|useEffect model|[react.dev — Synchronizing with Effects](https://react.dev/learn/synchronizing-with-effects)|
|You might not need an effect|[react.dev — You Might Not Need an Effect](https://react.dev/learn/you-might-not-need-an-effect)|
|TypeScript handbook|[typescriptlang.org/docs/handbook](https://www.typescriptlang.org/docs/handbook/2/types-from-types.html)|
|Matt Pocock TS tutorials|[totaltypescript.com](https://www.totaltypescript.com/)|
|Dan Abramov on useEffect|[overreacted.io — A Complete Guide to useEffect](https://overreacted.io/a-complete-guide-to-useeffect/)|