# Phase 3 — Deep Dive: Frontend System Design + Architecture

> **Duration:** 6–10 months (parallel tracks) **Goal:** Whiteboard-design 3 frontend systems from scratch with tradeoffs. Own features end-to-end. Write component APIs others want to use.

---

## Table of Contents

### Craft Track

1. [Design Patterns — Observer, Strategy, Factory](https://claude.ai/chat/66caa6a7-7c60-4209-93d6-c254a560cf68#1-design-patterns--observer-strategy-factory)
2. [Component API Design](https://claude.ai/chat/66caa6a7-7c60-4209-93d6-c254a560cf68#2-component-api-design)
3. [Micro-Frontend Tradeoffs](https://claude.ai/chat/66caa6a7-7c60-4209-93d6-c254a560cf68#3-micro-frontend-tradeoffs)
4. [Monorepo Tooling — Turborepo vs Nx vs Alternatives](https://claude.ai/chat/66caa6a7-7c60-4209-93d6-c254a560cf68#4-monorepo-tooling--turborepo-vs-nx-vs-alternatives)
5. [Accessibility at Architecture Level](https://claude.ai/chat/66caa6a7-7c60-4209-93d6-c254a560cf68#5-accessibility-at-architecture-level)

### Interview Track

6. [Frontend System Design Framework](https://claude.ai/chat/66caa6a7-7c60-4209-93d6-c254a560cf68#6-frontend-system-design-framework)
7. [System Design — News Feed](https://claude.ai/chat/66caa6a7-7c60-4209-93d6-c254a560cf68#7-system-design--news-feed)
8. [System Design — Autocomplete](https://claude.ai/chat/66caa6a7-7c60-4209-93d6-c254a560cf68#8-system-design--autocomplete)
9. [System Design — Real-Time Chat UI](https://claude.ai/chat/66caa6a7-7c60-4209-93d6-c254a560cf68#9-system-design--real-time-chat-ui)
10. [System Design — Infinite Scroll](https://claude.ai/chat/66caa6a7-7c60-4209-93d6-c254a560cf68#10-system-design--infinite-scroll)
11. [API Design from the Client's Perspective](https://claude.ai/chat/66caa6a7-7c60-4209-93d6-c254a560cf68#11-api-design-from-the-clients-perspective)
12. [State Management at Scale](https://claude.ai/chat/66caa6a7-7c60-4209-93d6-c254a560cf68#12-state-management-at-scale)

---

# CRAFT TRACK

---

## 1. Design Patterns — Observer, Strategy, Factory

### Why patterns matter at FAANG

Patterns are not vocabulary for impressing interviewers. They are battle-tested solutions to recurring architectural problems. At FAANG scale, a poorly chosen pattern in a shared component is a production incident waiting to happen. Knowing _when not to use_ a pattern is as important as knowing the pattern itself.

---

### 1.1 Observer Pattern

**Problem it solves:** One object changes state, and many other objects need to react — without the source knowing who they are or how many there are.

**Structure:**

```
Subject (EventEmitter)
  ├── subscribe(observer)
  ├── unsubscribe(observer)
  └── notify(data)
        ├── observer1.update(data)
        ├── observer2.update(data)
        └── observer3.update(data)
```

**TypeScript implementation:**

```typescript
type Listener<T> = (data: T) => void;

class EventEmitter<Events extends Record<string, unknown>> {
  private listeners = new Map<
    keyof Events,
    Set<Listener<Events[keyof Events]>>
  >();

  on<K extends keyof Events>(event: K, listener: Listener<Events[K]>): () => void {
    if (!this.listeners.has(event)) {
      this.listeners.set(event, new Set());
    }
    this.listeners.get(event)!.add(listener as Listener<Events[keyof Events]>);

    // Return unsubscribe function — caller manages cleanup
    return () => this.off(event, listener);
  }

  off<K extends keyof Events>(event: K, listener: Listener<Events[K]>): void {
    this.listeners.get(event)?.delete(listener as Listener<Events[keyof Events]>);
  }

  emit<K extends keyof Events>(event: K, data: Events[K]): void {
    this.listeners.get(event)?.forEach(listener => listener(data));
  }
}

// Usage — typed events
type AppEvents = {
  'user:login':  { userId: string; timestamp: number };
  'cart:update': { itemCount: number };
  'error':       { message: string; code: number };
};

const bus = new EventEmitter<AppEvents>();

const unsub = bus.on('user:login', ({ userId }) => {
  console.log(`Welcome, ${userId}`);
});

bus.emit('user:login', { userId: 'u123', timestamp: Date.now() });

// Critical: always unsubscribe to prevent memory leaks
unsub();
```

**React integration — custom event bus hook:**

```typescript
function useEventBus<K extends keyof AppEvents>(
  event: K,
  handler: Listener<AppEvents[K]>
): void {
  useEffect(() => {
    const unsub = bus.on(event, handler);
    return unsub; // cleanup on unmount
  }, [event, handler]);
}
```

**When to use:** Cross-component communication without prop drilling or shared state. Analytics events. Real-time notifications. Plugin systems.

**When NOT to use:** Replace with React Context/Zustand/Redux if the data needs to be synchronously readable by consumers — event buses are fire-and-forget, not queryable state.

**Memory leak trap:**

```typescript
// Leak: listener added but never removed
useEffect(() => {
  bus.on('resize', handleResize); // no cleanup
}, []);

// Correct: return the unsubscribe
useEffect(() => {
  return bus.on('resize', handleResize);
}, []);
```

---

### 1.2 Strategy Pattern

**Problem it solves:** A family of algorithms that are interchangeable. The algorithm varies independently from the client that uses it.

**Classic example — sorting, validation, formatting:**

```typescript
// Strategy interface — the contract
interface SortStrategy<T> {
  sort(items: T[]): T[];
}

// Concrete strategies
class AlphabeticalSort<T extends { name: string }> implements SortStrategy<T> {
  sort(items: T[]): T[] {
    return [...items].sort((a, b) => a.name.localeCompare(b.name));
  }
}

class DateSort<T extends { createdAt: Date }> implements SortStrategy<T> {
  sort(items: T[]): T[] {
    return [...items].sort((a, b) => b.createdAt.getTime() - a.createdAt.getTime());
  }
}

class RelevanceSort<T extends { score: number }> implements SortStrategy<T> {
  sort(items: T[]): T[] {
    return [...items].sort((a, b) => b.score - a.score);
  }
}

// Context — uses whatever strategy is injected
class ProductList<T extends { name: string; createdAt: Date; score: number }> {
  constructor(
    private items: T[],
    private strategy: SortStrategy<T>
  ) {}

  setStrategy(strategy: SortStrategy<T>): void {
    this.strategy = strategy;
  }

  getSorted(): T[] {
    return this.strategy.sort(this.items);
  }
}
```

**React hook version — strategy as a prop:**

```typescript
type FilterStrategy<T> = (items: T[], query: string) => T[];

interface SearchableListProps<T> {
  items: T[];
  filterStrategy: FilterStrategy<T>;
  renderItem: (item: T) => React.ReactNode;
}

function SearchableList<T>({ items, filterStrategy, renderItem }: SearchableListProps<T>) {
  const [query, setQuery] = useState('');
  const filtered = useMemo(
    () => filterStrategy(items, query),
    [items, query, filterStrategy]
  );

  return (
    <>
      <input value={query} onChange={e => setQuery(e.target.value)} />
      <ul>{filtered.map(renderItem)}</ul>
    </>
  );
}

// Caller swaps strategy without changing SearchableList
<SearchableList
  items={products}
  filterStrategy={(items, q) => items.filter(p => p.name.includes(q))}
  renderItem={p => <ProductCard key={p.id} product={p} />}
/>
```

**Real-world use cases in frontend:**

- Form validation strategies (required, email, minLength)
- Price calculation strategies (discount, tax, bundle)
- Payment method processing
- Analytics provider swapping (GA → Amplitude)
- Auth strategies (JWT, OAuth, session)

---

### 1.3 Factory Pattern

**Problem it solves:** Centralize and encapsulate object creation. Callers request objects without knowing their concrete class. Enables extension without modification (Open/Closed Principle).

**Simple factory — the starting point:**

```typescript
type ButtonVariant = 'primary' | 'secondary' | 'danger' | 'ghost';

interface ButtonConfig {
  className: string;
  ariaRole: string;
  focusable: boolean;
}

// Factory function — centralize creation logic
function createButtonConfig(variant: ButtonVariant): ButtonConfig {
  const configs: Record<ButtonVariant, ButtonConfig> = {
    primary:   { className: 'btn-primary',   ariaRole: 'button', focusable: true },
    secondary: { className: 'btn-secondary', ariaRole: 'button', focusable: true },
    danger:    { className: 'btn-danger',     ariaRole: 'button', focusable: true },
    ghost:     { className: 'btn-ghost',      ariaRole: 'button', focusable: true },
  };
  return configs[variant];
}
```

**Abstract factory — families of related objects:**

```typescript
// Abstract factory — creates related UI components as a family
interface UIComponentFactory {
  createButton(label: string): React.ReactElement;
  createInput(placeholder: string): React.ReactElement;
  createModal(title: string, content: React.ReactNode): React.ReactElement;
}

// Concrete factory — Material Design family
class MaterialFactory implements UIComponentFactory {
  createButton(label: string) {
    return <MaterialButton>{label}</MaterialButton>;
  }
  createInput(placeholder: string) {
    return <TextField placeholder={placeholder} variant="outlined" />;
  }
  createModal(title: string, content: React.ReactNode) {
    return <MaterialDialog title={title}>{content}</MaterialDialog>;
  }
}

// Concrete factory — custom design system family
class DesignSystemFactory implements UIComponentFactory {
  createButton(label: string) {
    return <Button variant="primary">{label}</Button>;
  }
  createInput(placeholder: string) {
    return <Input placeholder={placeholder} />;
  }
  createModal(title: string, content: React.ReactNode) {
    return <Modal title={title}>{content}</Modal>;
  }
}

// Context provider — inject the factory
const UIFactoryContext = React.createContext<UIComponentFactory>(new MaterialFactory());

function App() {
  return (
    <UIFactoryContext.Provider value={new DesignSystemFactory()}>
      <AppContent />
    </UIFactoryContext.Provider>
  );
}
```

**Factory for component registration — plugin systems:**

```typescript
type WidgetType = 'chart' | 'table' | 'map' | 'text';
type WidgetProps = { data: unknown; config: Record<string, unknown> };

class WidgetRegistry {
  private static registry = new Map<
    WidgetType,
    React.ComponentType<WidgetProps>
  >();

  static register(type: WidgetType, component: React.ComponentType<WidgetProps>): void {
    this.registry.set(type, component);
  }

  static create(type: WidgetType, props: WidgetProps): React.ReactElement {
    const Component = this.registry.get(type);
    if (!Component) throw new Error(`Unknown widget type: ${type}`);
    return <Component {...props} />;
  }
}

// Register widgets (can be done lazily, from plugins)
WidgetRegistry.register('chart', ChartWidget);
WidgetRegistry.register('table', TableWidget);

// Consumer
function Dashboard({ widgets }: { widgets: Array<{ type: WidgetType; data: unknown }> }) {
  return (
    <div>
      {widgets.map((w, i) =>
        WidgetRegistry.create(w.type, { data: w.data, config: {} })
      )}
    </div>
  );
}
```

---

### 1.4 Interview Questions

**Q: Explain the Observer pattern and give a real frontend example.** A: A subject maintains a list of listeners. When state changes, it notifies all listeners without knowing their identities. Real example: EventEmitter for cross-component communication, or React's Context propagation.

**Q: How does the Strategy pattern differ from simple conditionals?** A: Conditionals grow with every new case and require modifying the core logic. Strategy externalizes each algorithm as a swappable object — adding a new strategy requires no changes to the context. Open/Closed Principle in practice.

**Q: When would you use a Factory vs direct instantiation?** A: When creation logic is complex, when the concrete type varies at runtime, or when you want to decouple callers from implementations. Factory also centralizes changes — if a constructor signature changes, only the factory needs updating.

**Q: What's the memory leak risk with the Observer pattern and how do you prevent it?** A: Listeners that are added but never removed keep references to their enclosing scope, preventing garbage collection. Prevention: always return and call an unsubscribe function, use WeakRef for non-critical observers, and clean up in useEffect return.

---

## 2. Component API Design

### The core principle

A component's API is a contract with every team that uses it. Bad API design compounds — every consumer inherits your mistakes and every breaking change requires coordinated migration across teams. Design component APIs with the same rigor as public REST APIs.

---

### 2.1 The Inverted Triangle of Flexibility

```
                 ┌─────────────────────┐
     least ──►   │  Fully controlled   │  ◄── most flexible
   flexible      │  (pure controlled)  │       (hardest to use)
                 ├─────────────────────┤
                 │  Compound pattern   │
                 ├─────────────────────┤
                 │  Render props       │
                 ├─────────────────────┤
     most ──►    │  Opinionated/preset │  ◄── least flexible
   flexible      │  (zero-config)      │       (easiest to use)
                 └─────────────────────┘
```

Design at the level your consumers actually need. Over-flexible APIs are as harmful as rigid ones — they shift the cognitive burden to the caller.

---

### 2.2 Controlled vs Uncontrolled

```typescript
// Uncontrolled: manages its own state
// Caller provides initial value but doesn't control it
function Input({ defaultValue, onChange }: {
  defaultValue?: string;
  onChange?: (value: string) => void;
}) {
  const [value, setValue] = useState(defaultValue ?? '');
  return (
    <input
      value={value}
      onChange={e => {
        setValue(e.target.value);
        onChange?.(e.target.value);
      }}
    />
  );
}

// Controlled: caller owns all state
// Component is a pure view — no internal state
function Input({ value, onChange }: {
  value: string;
  onChange: (value: string) => void;
}) {
  return (
    <input value={value} onChange={e => onChange(e.target.value)} />
  );
}

// Best practice: support BOTH (like HTML inputs do)
function Input({
  value,
  defaultValue,
  onChange,
}: {
  value?: string;          // if provided → controlled mode
  defaultValue?: string;   // if provided → uncontrolled mode
  onChange?: (value: string) => void;
}) {
  const isControlled = value !== undefined;
  const [internalValue, setInternalValue] = useState(defaultValue ?? '');
  const displayValue = isControlled ? value : internalValue;

  function handleChange(e: React.ChangeEvent<HTMLInputElement>) {
    if (!isControlled) setInternalValue(e.target.value);
    onChange?.(e.target.value);
  }

  return <input value={displayValue} onChange={handleChange} />;
}
```

---

### 2.3 Compound Components

Compound components expose multiple subcomponents that share implicit state through context. The caller assembles them — complete control over structure, zero prop drilling.

```typescript
// Internal context — shared between compound parts
type SelectContextValue = {
  value:    string;
  onChange: (value: string) => void;
  isOpen:   boolean;
  toggle:   () => void;
};
const SelectContext = React.createContext<SelectContextValue | null>(null);

function useSelectContext() {
  const ctx = useContext(SelectContext);
  if (!ctx) throw new Error('Select compound components must be used within <Select>');
  return ctx;
}

// Root — owns state, provides context
function Select({ value, onChange, children }: {
  value:    string;
  onChange: (value: string) => void;
  children: React.ReactNode;
}) {
  const [isOpen, setIsOpen] = useState(false);
  return (
    <SelectContext.Provider value={{ value, onChange, isOpen, toggle: () => setIsOpen(v => !v) }}>
      <div className="select-root">{children}</div>
    </SelectContext.Provider>
  );
}

// Sub-components — consume context
function Trigger({ children }: { children: React.ReactNode }) {
  const { toggle, isOpen } = useSelectContext();
  return (
    <button onClick={toggle} aria-expanded={isOpen} aria-haspopup="listbox">
      {children}
    </button>
  );
}

function Options({ children }: { children: React.ReactNode }) {
  const { isOpen } = useSelectContext();
  return isOpen ? <ul role="listbox">{children}</ul> : null;
}

function Option({ value, children }: { value: string; children: React.ReactNode }) {
  const ctx = useSelectContext();
  return (
    <li
      role="option"
      aria-selected={ctx.value === value}
      onClick={() => { ctx.onChange(value); }}
    >
      {children}
    </li>
  );
}

// Attach subcomponents as static properties
Select.Trigger  = Trigger;
Select.Options  = Options;
Select.Option   = Option;

// Caller usage — complete structural control
<Select value={selected} onChange={setSelected}>
  <Select.Trigger>{selected || 'Choose...'}</Select.Trigger>
  <Select.Options>
    <Select.Option value="react">React</Select.Option>
    <Select.Option value="vue">Vue</Select.Option>
  </Select.Options>
</Select>
```

---

### 2.4 Props API Principles

```typescript
// ❌ Anti-patterns
interface BadButtonProps {
  isRound?: boolean;          // boolean props for visual state — use variant
  redBackground?: boolean;    // styling concerns leak into API
  onClick1?: () => void;      // numbered props — use children or slots
  onClick2?: () => void;
  textColor: 'black' | 'white'; // caller shouldn't control this
}

// ✅ Well-designed API
interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'danger' | 'ghost';
  size?:    'sm' | 'md' | 'lg';
  isLoading?: boolean;
  leftIcon?:  React.ReactElement;
  rightIcon?: React.ReactElement;
  // onClick, disabled, type → inherited from ButtonHTMLAttributes
}
```

**The five API design rules:**

|Rule|Bad|Good|
|---|---|---|
|Extend HTML elements|Custom `onClick` prop|Extend `ButtonHTMLAttributes`|
|Variant over booleans|`isRound isPrimary isLarge`|`variant="primary" size="lg"`|
|Forward refs|Consumer can't access DOM|`React.forwardRef` always|
|Composable children|`title` + `description` + `icon` props|`children` / slots / compound|
|Avoid leaking internals|`innerContainerClassName`|Expose what callers need, no more|

---

### 2.5 Interview Questions

**Q: What's the difference between controlled and uncontrolled components and when do you use each?** A: Controlled: parent owns all state, component is a pure view. Uncontrolled: component manages its own state internally. Use controlled when you need to validate, synchronize, or derive from the value. Use uncontrolled for simple cases or DOM integrations (file inputs, canvas).

**Q: What are compound components and what problem do they solve?** A: Components broken into cooperating sub-components that share implicit state through context. They solve the tension between flexibility and simplicity — callers control structure without the root component needing an explosion of props.

**Q: Why should components extend HTML element types rather than defining custom prop interfaces from scratch?** A: Consumers get all native attributes (disabled, aria-_, data-_, event handlers) automatically. It prevents the common bug where a prop like `onClick` works but `tabIndex` silently does nothing.

---

## 3. Micro-Frontend Tradeoffs

### What it is

Micro-frontends apply microservice thinking to the frontend — splitting a large application into independently deployable, loosely coupled frontend units owned by separate teams.

---

### 3.1 Core Tradeoffs

```
Benefit                              Cost
─────────────────────────────────    ─────────────────────────────────────
Team autonomy (own stack/deploy)  ↔  Coordination overhead
Independent deployability         ↔  Version compatibility risk
Incremental migration             ↔  Bundle duplication (React loaded 3×)
Isolated failures                 ↔  Cross-fragment UX inconsistency
Parallel development              ↔  Shared state complexity
```

**The hard truth:** Micro-frontends solve organizational problems, not technical ones. If your team is small and unified, they add complexity with zero benefit.

---

### 3.2 Integration Strategies

**1. Build-time integration (npm packages)** Each micro-frontend is a published npm package. The shell app installs and bundles them together.

```
✅ Simple — no runtime complexity
✅ Type-safe across boundaries
✅ Tree-shaking works
❌ Every change requires republishing + shell re-deploy
❌ Not independently deployable — defeats the purpose
```

**2. Runtime integration via iframes**

```
✅ Complete isolation (styles, globals, errors)
✅ Any framework, any version
❌ Terrible UX (accessibility, deep linking, scroll sync)
❌ Communication requires postMessage — complex and fragile
❌ SEO / performance implications
```

**3. Runtime integration via JavaScript (Module Federation)**

```javascript
// webpack.config.js — Host app
new ModuleFederationPlugin({
  name: 'shell',
  remotes: {
    checkout: 'checkout@https://checkout.example.com/remoteEntry.js',
    catalog:  'catalog@https://catalog.example.com/remoteEntry.js',
  },
  shared: {
    react:     { singleton: true, requiredVersion: '^18.0.0' },
    'react-dom': { singleton: true, requiredVersion: '^18.0.0' },
  },
});

// webpack.config.js — Checkout micro-frontend
new ModuleFederationPlugin({
  name: 'checkout',
  filename: 'remoteEntry.js',
  exposes: {
    './CheckoutFlow': './src/CheckoutFlow',
  },
  shared: { react: { singleton: true } },
});

// Shell usage
const CheckoutFlow = React.lazy(() => import('checkout/CheckoutFlow'));
```

```
✅ True independent deployment
✅ Shared singleton dependencies (React loaded once)
✅ Works at runtime — no rebuild required
❌ Version mismatch risk (shared singleton can conflict)
❌ Complex debugging (multiple webpack builds)
❌ Network dependency at runtime — remote failure = broken feature
```

**4. Server-side composition (Edge / SSR)**

Each team renders their fragment. A composition layer (edge, nginx, Next.js middleware) assembles them.

```
✅ Best performance (no JS needed for composition)
✅ True isolation
❌ Complex infra — requires a composition layer
❌ Harder shared state (must use URL params or cookies)
```

---

### 3.3 Shared State Between Micro-Frontends

The hardest problem in micro-frontends:

```typescript
// Option 1: URL as shared state (best for navigation)
// Each MFE reads URL params — no coordination needed

// Option 2: Custom Events (browser-native, framework-agnostic)
// MFE A dispatches
window.dispatchEvent(new CustomEvent('user:authenticated', {
  detail: { userId: 'u123', token: '...' },
  bubbles: true,
}));

// MFE B listens
window.addEventListener('user:authenticated', (e: CustomEvent) => {
  store.setUser(e.detail);
});

// Option 3: Shared singleton store (risky — tight coupling)
window.__APP_STATE__ = createGlobalStore();
```

---

### 3.4 When to Use Micro-Frontends

**Yes, if:**

- Multiple teams that need to deploy independently
- Legacy system needing incremental modernization (strangle fig pattern)
- Different parts of the app have wildly different tech requirements

**No, if:**

- Single team (organizational benefit gone, technical cost remains)
- Consistent UX is critical (hard to enforce across MFE boundaries)
- App is small-to-medium scale

---

### 3.5 Interview Questions

**Q: What problem do micro-frontends solve and what's the main cost?** A: Organizational: multiple teams can own, develop, and deploy frontend independently. The main cost is complexity — bundle duplication, cross-boundary state management, version coordination, and UX inconsistency.

**Q: How does Module Federation work?** A: Webpack's Module Federation allows one build (remote) to expose modules, and another build (host) to consume them at runtime from a URL. Dependencies like React can be declared as shared singletons to avoid loading them multiple times.

**Q: How do micro-frontends communicate without tight coupling?** A: URL params for navigation state (stateless, bookmarkable), CustomEvents on `window` for fire-and-forget events (framework-agnostic), or a lightweight pub/sub bus. Avoid direct imports between MFEs — that's build-time coupling.

---

## 4. Monorepo Tooling — Turborepo vs Nx vs Alternatives

> You're familiar with Turborepo. This section focuses on the **mental model differences** and the decision criteria — not basic setup.

---

### 4.1 The Core Problem All Tools Solve

In a monorepo with N packages, a naive build runs every package's build/test/lint on every CI run — O(N) always. Good monorepo tooling achieves:

1. **Task graph:** Only run tasks whose inputs have changed
2. **Caching:** Never recompute what was already computed (local + remote)
3. **Parallelism:** Run independent tasks concurrently

---

### 4.2 Mental Model Comparison

```
                 Turborepo              Nx                    Bun Workspaces
─────────────────────────────────────────────────────────────────────────────
Philosophy       Build orchestrator     Integrated dev         Package manager
                 (does one thing well)  platform               + native speed

Owns what?       Task pipeline only     Workspace + tasks +    Install + run
                                        generators + plugins   (not a task runner)

Config           turbo.json             nx.json + project.json package.json scripts

Learning curve   Low                    Medium–High            Very low

Generators       ❌ No                  ✅ Yes (nx generate)   ❌ No

Plugins          ❌ No                  ✅ Rich ecosystem       ❌ No

Remote cache     ✅ Vercel (paid)       ✅ Nx Cloud (paid)     N/A
                    Self-host (oss)        Self-host (oss)

Language aware   ❌ Task-level only     ✅ Knows TS, React,    ❌ No
                                          Next, etc.

Project graph    ❌                     ✅ nx graph            ❌
visualization

Best for         Teams who want fast    Teams who want full    Replacing npm/yarn
                 builds, minimal        workspace management   for install speed
                 config, flexibility    + scaffolding
```

---

### 4.3 Turborepo Deep Dive (Your Baseline)

**What Turborepo actually does:**

```
Your packages:        app-web → depends on → ui, utils
                      app-mobile → depends on → ui, utils
                      ui → depends on → utils

Turborepo builds a task graph:
  build:utils → build:ui → build:app-web
                         → build:app-mobile (parallel)
```

**Pipeline config:**

```json
// turbo.json
{
  "$schema": "https://turbo.build/schema.json",
  "pipeline": {
    "build": {
      "dependsOn": ["^build"],  // ^ = run deps first
      "outputs": [".next/**", "dist/**"],
      "cache": true
    },
    "test": {
      "dependsOn": ["build"],
      "outputs": ["coverage/**"],
      "cache": true,
      "inputs": ["src/**/*.ts", "test/**/*.ts"]
    },
    "lint": {
      "outputs": [],
      "cache": true
    },
    "dev": {
      "cache": false,
      "persistent": true   // long-running task
    }
  }
}
```

**Turborepo cache key:** Hash of (inputs + task config + env variables). If any input file changes, the cache is invalidated for that task and all downstream tasks.

**What Turborepo does NOT do:**

- Code generators (`nx generate component`)
- Dependency graph visualization
- Enforcing module boundaries
- Plugin system

---

### 4.4 Nx — What It Adds Over Turborepo

**1. Project graph and affected commands:**

```bash
# Nx computes which packages are affected by your changes
nx affected --target=build  # only builds changed + downstream
nx affected --target=test   # only tests what could be broken
nx graph                    # visual dependency graph in browser
```

This is more powerful than Turborepo's `--filter` because Nx understands the TypeScript import graph — not just package.json dependencies.

**2. Generators — scaffolding that stays consistent:**

```bash
# Generate a new React component with tests, story, and barrel export
nx generate @nx/react:component Button --directory=libs/ui/src

# Generate an entire new app
nx generate @nx/next:app dashboard

# Custom generator for your design system
nx generate @company/generators:design-system-component Card
```

Turborepo has no equivalent. Without generators, every developer creates files differently.

**3. Module boundary enforcement:**

```json
// .eslintrc.json — enforce architectural rules
{
  "rules": {
    "@nx/enforce-module-boundaries": ["error", {
      "depConstraints": [
        {
          "sourceTag": "scope:feature",
          "onlyDependOn": ["scope:ui", "scope:util"]
        },
        {
          "sourceTag": "scope:ui",
          "onlyDependOn": ["scope:util"]
        }
      ]
    }]
  }
}
```

This prevents `ui` from importing `feature` code — architectural rules enforced at lint time, not code review.

**4. Nx Cloud — distributed task execution:**

Unlike Turborepo's remote cache (replay past results), Nx Cloud also distributes task _execution_ across multiple agents — tasks run in parallel across machines, not just cached locally.

---

### 4.5 Bun Workspaces — What It Is (and Isn't)

**Bun is a JavaScript runtime + package manager + bundler.** Bun Workspaces is the monorepo support built into the package manager.

```
Bun Workspaces does:
✅ Extremely fast install (written in Zig, 10–25× faster than npm)
✅ workspace: protocol for cross-package deps
✅ Shared lockfile
✅ Run scripts across workspaces with filtering

Bun Workspaces does NOT do:
❌ Task graph / dependency-aware task ordering
❌ Caching (no build cache, no remote cache)
❌ Generators
❌ Affected computation
```

**Bun as package manager inside a Turbo or Nx repo:**

```json
// package.json — use Bun as the package manager, Turbo for tasks
{
  "packageManager": "bun@1.x",
  "scripts": {
    "build": "turbo run build",
    "test":  "turbo run test"
  }
}
```

This is actually the most common real-world setup: Bun for install speed + Turborepo or Nx for task orchestration.

---

### 4.6 pnpm Workspaces — The Baseline Comparison

pnpm is the most widely used monorepo package manager in production (used by Vue, Vite, Nuxt, and most large OSS monorepos).

```
pnpm advantages over npm/yarn in monorepos:
✅ Content-addressable store — packages stored once, hard-linked
✅ Strict dependency isolation (prevents phantom dependencies)
✅ workspace: protocol — workspace packages referenced directly
✅ Filtering: pnpm --filter <pkg> run build
✅ Fast (not as fast as Bun, but faster than npm/yarn)

pnpm vs Bun:
pnpm: battle-tested, strict isolation, broad ecosystem support
Bun:  faster installs, but runtime compatibility issues with some npm packages
```

---

### 4.7 Decision Framework

```
Q1: Do you need code generators and strict architectural enforcement?
  Yes → Nx
  No  → continue

Q2: Is build speed / simplicity the primary concern?
  Yes → Turborepo (+ pnpm or Bun as package manager)
  No  → continue

Q3: Are you migrating an existing large codebase with many contributors?
  Yes → Nx (generators + boundary enforcement prevent drift)
  No  → Turborepo

Q4: Package manager only? (no task graph needed, very small repo)
  Yes → Bun Workspaces or pnpm Workspaces
```

---

### 4.8 Turborepo → Nx Migration Path (if you ever need it)

```bash
# Nx can wrap an existing Turborepo without full migration
npx nx@latest init  # detects turbo.json, creates nx.json alongside it

# Nx reads turbo.json and adds its own caching/affected computation
# You keep turbo.json — it's additive, not a rewrite
```

---

### 4.9 Remote Cache Comparison

||Turborepo|Nx Cloud|Self-hosted|
|---|---|---|---|
|Vercel hosted|Free tier + paid|—|—|
|Nx Cloud|—|Free tier + paid|—|
|Self-hosted (OSS)|✅ `ducktape` / custom|✅ Nx Cloud CE|Both support|
|Cache granularity|Task output|Task output|—|
|Distributed execution|❌|✅ DTE|—|

---

### 4.10 Interview Questions

**Q: What is the core value of a monorepo, and what tooling problem does it create?** A: Monorepos enable shared code, atomic commits across packages, and single source of truth. The tooling problem: naive CI runs every task for every package on every commit — O(N) always. Good tooling computes a task graph, caches outputs, and only reruns what changed.

**Q: How does Turborepo's caching work?** A: It hashes task inputs (source files, env vars, task config) to create a cache key. On a cache hit (same hash), it replays the cached output instead of re-running. Cache can be local or remote (Vercel or self-hosted). Downstream tasks also benefit — if `build:utils` is cached, `build:ui` that depends on it can also hit cache.

**Q: What does Nx provide that Turborepo doesn't?** A: Code generators for consistent scaffolding, module boundary enforcement via ESLint rules, TypeScript-aware project graph (understands imports, not just package.json deps), `affected` commands based on real import analysis, and distributed task execution via Nx Cloud.

**Q: When would you choose pnpm over Bun for a monorepo?** A: pnpm has strict phantom dependency prevention (no accessing unlisted packages), better ecosystem compatibility, and a long production track record. Bun wins on raw install speed but has runtime compatibility gaps with some npm packages and is newer in production. For most teams, pnpm + Turborepo is the safer default.

**Q: Can you use Bun with Turborepo?** A: Yes — they operate at different layers. Bun handles package installation (fast), Turborepo handles task orchestration and caching. Set `"packageManager": "bun"` in root package.json, use Bun for `bun install`, and Turborepo for `turbo run build`.

---

## 5. Accessibility at Architecture Level

### The mindset shift

Junior: adds `alt` text and `aria-label` as an afterthought. Senior: designs component APIs so accessibility is impossible to get wrong by default.

---

### 5.1 The Accessibility Tree

Browsers expose a parallel tree alongside the DOM — the **Accessibility Tree** — which screen readers and assistive technologies consume. Every component you build contributes to this tree.

```
DOM:                        Accessibility Tree:
<button class="icon-btn">   role=button
  <svg>...</svg>            name="" (❌ empty — meaningless to screen reader)
</button>

<button aria-label="Close"> role=button
  <svg>...</svg>            name="Close" (✅ announced correctly)
</button>
```

---

### 5.2 ARIA — When to Use and When Not To

**The ARIA hierarchy:**

```
1. No ARIA — use native HTML element (best)
   <button> not <div role="button">
   <input type="checkbox"> not <div role="checkbox">
   <nav> not <div role="navigation">

2. ARIA to supplement native semantics
   <button aria-expanded="true" aria-controls="menu">
   <input aria-invalid="true" aria-describedby="error-msg">

3. ARIA to create custom widgets (last resort)
   <div role="combobox" aria-expanded="true" aria-activedescendant="opt1">
```

**First rule of ARIA:** Don't use ARIA if a native HTML element has the same semantics. `<button>` is better than `<div role="button">` — it has keyboard handling, focus management, and form submission built in.

---

### 5.3 Keyboard Navigation Architecture

Every interactive component must be keyboard accessible. The patterns:

**Simple: tab to focus, Enter/Space to activate**

```typescript
// ❌ Not keyboard accessible
<div onClick={handleClick} className="btn">Submit</div>

// ✅ Native button — keyboard free
<button onClick={handleClick}>Submit</button>

// ✅ If you must use div (don't)
<div
  role="button"
  tabIndex={0}
  onClick={handleClick}
  onKeyDown={e => { if (e.key === 'Enter' || e.key === ' ') handleClick(); }}
>
  Submit
</div>
```

**Composite widgets: roving tabIndex**

For components with multiple interactive children (tabs, toolbars, menus), only one child is in the tab order at a time. Arrow keys move focus within the widget.

```typescript
function Tabs({ tabs }: { tabs: { id: string; label: string; content: React.ReactNode }[] }) {
  const [activeTab, setActiveTab] = useState(tabs[0].id);
  const [focusedTab, setFocusedTab] = useState(tabs[0].id);

  function handleKeyDown(e: React.KeyboardEvent, currentIdx: number) {
    let nextIdx = currentIdx;
    if (e.key === 'ArrowRight') nextIdx = (currentIdx + 1) % tabs.length;
    if (e.key === 'ArrowLeft')  nextIdx = (currentIdx - 1 + tabs.length) % tabs.length;
    if (e.key === 'Home')       nextIdx = 0;
    if (e.key === 'End')        nextIdx = tabs.length - 1;

    if (nextIdx !== currentIdx) {
      e.preventDefault();
      setFocusedTab(tabs[nextIdx].id);
      setActiveTab(tabs[nextIdx].id);
      // Programmatically focus the new tab
      tabRefs.current[nextIdx]?.focus();
    }
  }

  const tabRefs = useRef<(HTMLButtonElement | null)[]>([]);

  return (
    <div>
      <div role="tablist" aria-label="Content sections">
        {tabs.map((tab, idx) => (
          <button
            key={tab.id}
            role="tab"
            ref={el => { tabRefs.current[idx] = el; }}
            aria-selected={activeTab === tab.id}
            aria-controls={`panel-${tab.id}`}
            id={`tab-${tab.id}`}
            tabIndex={focusedTab === tab.id ? 0 : -1}  // roving tabIndex
            onClick={() => { setActiveTab(tab.id); setFocusedTab(tab.id); }}
            onKeyDown={e => handleKeyDown(e, idx)}
          >
            {tab.label}
          </button>
        ))}
      </div>
      {tabs.map(tab => (
        <div
          key={tab.id}
          role="tabpanel"
          id={`panel-${tab.id}`}
          aria-labelledby={`tab-${tab.id}`}
          hidden={activeTab !== tab.id}
        >
          {tab.content}
        </div>
      ))}
    </div>
  );
}
```

---

### 5.4 Focus Management

Focus management is the skill that separates junior and senior a11y work:

```typescript
// Modal: focus must move inside on open, return to trigger on close
function Modal({ isOpen, onClose, children }: {
  isOpen: boolean;
  onClose: () => void;
  children: React.ReactNode;
}) {
  const modalRef  = useRef<HTMLDivElement>(null);
  const triggerRef = useRef<HTMLElement | null>(null);

  useEffect(() => {
    if (isOpen) {
      // Save current focus to restore later
      triggerRef.current = document.activeElement as HTMLElement;
      // Move focus into modal
      modalRef.current?.focus();
    } else {
      // Restore focus to trigger when modal closes
      triggerRef.current?.focus();
    }
  }, [isOpen]);

  // Trap focus within modal while open
  function handleKeyDown(e: React.KeyboardEvent) {
    if (e.key === 'Escape') { onClose(); return; }
    if (e.key !== 'Tab') return;

    const focusable = modalRef.current?.querySelectorAll<HTMLElement>(
      'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
    );
    if (!focusable || focusable.length === 0) return;

    const first = focusable[0];
    const last  = focusable[focusable.length - 1];

    if (e.shiftKey && document.activeElement === first) {
      e.preventDefault();
      last.focus();
    } else if (!e.shiftKey && document.activeElement === last) {
      e.preventDefault();
      first.focus();
    }
  }

  if (!isOpen) return null;

  return (
    <div
      ref={modalRef}
      role="dialog"
      aria-modal="true"
      aria-labelledby="modal-title"
      tabIndex={-1}             // focusable but not in natural tab order
      onKeyDown={handleKeyDown}
    >
      <h2 id="modal-title">Modal Title</h2>
      {children}
      <button onClick={onClose}>Close</button>
    </div>
  );
}
```

---

### 5.5 Live Regions — Dynamic Content

When content changes dynamically (toasts, status messages, loading states), screen readers won't announce it unless you use a live region:

```typescript
function Toast({ message, type }: { message: string; type: 'success' | 'error' }) {
  return (
    <div
      role="status"         // for non-critical updates (polite)
      aria-live="polite"    // wait for user to finish before announcing
      aria-atomic="true"    // announce entire region, not just changes
    >
      {message}
    </div>
  );
}

// For errors or urgent messages:
<div role="alert" aria-live="assertive">
  Payment failed. Please try again.
</div>
```

---

### 5.6 Accessible Component API Design

Design APIs where accessibility is the default, not opt-in:

```typescript
// ❌ Caller can forget a11y props
interface IconButtonProps {
  icon: React.ReactElement;
  onClick: () => void;
}

// ✅ Force caller to provide accessible name
interface IconButtonProps {
  icon: React.ReactElement;
  onClick: () => void;
  'aria-label': string;        // required — no default possible for icon buttons
}

// ✅ Automatic aria associations
function FormField({ label, error, children, id }: {
  label:    string;
  error?:   string;
  id:       string;
  children: (props: { id: string; 'aria-describedby'?: string; 'aria-invalid'?: boolean }) => React.ReactNode;
}) {
  const errorId = error ? `${id}-error` : undefined;

  return (
    <div>
      <label htmlFor={id}>{label}</label>
      {children({
        id,
        'aria-describedby': errorId,
        'aria-invalid': !!error,
      })}
      {error && <p id={errorId} role="alert">{error}</p>}
    </div>
  );
}

// Usage — all aria wiring is automatic
<FormField id="email" label="Email" error={errors.email}>
  {props => <input type="email" {...props} />}
</FormField>
```

---

### 5.7 Interview Questions

**Q: What is the accessibility tree and why does it matter?** A: A parallel representation of the DOM that browsers expose to assistive technologies. ARIA roles, labels, and states populate this tree. Components that look correct visually can be completely broken for screen reader users if the accessibility tree is wrong.

**Q: When should you use ARIA vs native HTML?** A: Native HTML first — `<button>`, `<input>`, `<nav>` carry built-in semantics and keyboard behavior. Use ARIA only to supplement (aria-expanded, aria-describedby) or to build custom widgets with no native equivalent (combobox, tree). Wrong ARIA is worse than no ARIA.

**Q: What is a roving tabIndex and when do you use it?** A: A pattern for composite widgets where only one child is in the natural tab order (tabIndex=0) at a time. Other children have tabIndex=-1. Arrow keys move focus within the widget, updating which element has tabIndex=0. Used for tabs, toolbars, menus, radio groups.

**Q: How do you manage focus when opening and closing a modal?** A: On open: save reference to the triggering element, move focus into the modal. Inside modal: trap tab/shift-tab within modal, close on Escape. On close: return focus to the saved trigger element.

---

---

# INTERVIEW TRACK

---

## 6. Frontend System Design Framework

Apply this framework to every system design question. Interviewers are not testing knowledge of specific features — they're testing your ability to think structurally about tradeoffs.

```
STEP 1 — Requirements (3–5 min)
  Functional:  What must it do?
  Non-functional: performance, scale, offline, a11y

STEP 2 — High-level architecture (5 min)
  Component tree (high level)
  Data flow direction
  External services / APIs

STEP 3 — Data model (5 min)
  What does the client store?
  Shape of API response?
  What gets normalized?

STEP 4 — Core features (15 min)
  Pick 2–3 key features, go deep
  Rendering strategy, state management, network

STEP 5 — Optimizations + tradeoffs (5 min)
  Performance, caching, error handling, offline, a11y
  What you would NOT build v1 and why

STEP 6 — Follow-up / edge cases (5 min)
```

---

## 7. System Design — News Feed

**Interviewer signal:** How do you handle real-time updates, infinite data, and performance at scale?

---

### Requirements

**Functional:**

- Display chronological / ranked posts from followed users
- Support text, image, video posts
- Like, comment, share interactions
- Real-time new post indicator ("3 new posts")

**Non-functional:**

- 60fps scroll
- First feed visible < 2s
- Works on slow 3G

---

### Component Architecture

```
<App>
  └── <FeedPage>
        ├── <NewPostsBanner count={3} onRefresh={...} />
        ├── <VirtualizedFeedList>
        │     ├── <PostCard type="text" />
        │     ├── <PostCard type="image" />
        │     └── <PostCard type="video" />
        └── <IntersectionObserver> (infinite scroll trigger)
```

---

### Data Model

```typescript
interface Post {
  id:         string;
  authorId:   string;
  type:       'text' | 'image' | 'video';
  content:    string;
  mediaUrls?: string[];
  likeCount:  number;
  commentCount: number;
  createdAt:  number; // unix timestamp
  isLikedByMe: boolean;
}

interface FeedPage {
  posts:       Post[];
  nextCursor?: string; // null = no more pages
}

// Normalized store — avoid duplicate post objects across pages
interface FeedStore {
  postIds:  string[];         // ordered list of IDs
  entities: Record<string, Post>; // keyed by ID
  nextCursor: string | null;
  newPostCount: number;
}
```

---

### Feed Loading Strategy

**Cursor-based pagination (not page-number):**

```typescript
// Page numbers break when new content is inserted at the top
// Cursor = stable pointer to last seen item
GET /feed?cursor=post_abc123&limit=20

// First load
GET /feed?limit=20
→ { posts: [...], nextCursor: "post_xyz456" }

// Next page
GET /feed?cursor=post_xyz456&limit=20
```

**Optimistic updates for interactions:**

```typescript
function useLikePost() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (postId: string) => api.likePost(postId),

    onMutate: async (postId) => {
      await queryClient.cancelQueries({ queryKey: ['feed'] });
      const prev = queryClient.getQueryData(['feed']);

      // Optimistically update the cache immediately
      queryClient.setQueryData(['feed'], (old: FeedStore) => ({
        ...old,
        entities: {
          ...old.entities,
          [postId]: {
            ...old.entities[postId],
            isLikedByMe: true,
            likeCount: old.entities[postId].likeCount + 1,
          },
        },
      }));

      return { prev }; // rollback data
    },

    onError: (_, __, context) => {
      // Rollback on failure
      queryClient.setQueryData(['feed'], context?.prev);
    },
  });
}
```

---

### Real-Time New Posts

```typescript
// WebSocket connection — listen for new posts from followed users
function useFeedUpdates() {
  const [newPostCount, setNewPostCount] = useState(0);

  useEffect(() => {
    const ws = new WebSocket('wss://api.example.com/feed/updates');

    ws.onmessage = (event) => {
      const { type, data } = JSON.parse(event.data);
      if (type === 'new_post') {
        setNewPostCount(prev => prev + 1);
        // Don't automatically insert — bad UX (content jumps while reading)
        // Instead, show "3 new posts" banner
      }
    };

    return () => ws.close();
  }, []);

  return newPostCount;
}

// Only insert new posts when user explicitly clicks the banner
function NewPostsBanner({ count, onRefresh }: { count: number; onRefresh: () => void }) {
  if (count === 0) return null;
  return (
    <button onClick={onRefresh} aria-live="polite">
      {count} new post{count > 1 ? 's' : ''} — Click to refresh
    </button>
  );
}
```

---

### Performance: Virtualization

A feed of 500 posts = 500 DOM nodes = guaranteed jank. Virtualization renders only the visible portion:

```typescript
import { useVirtualizer } from '@tanstack/react-virtual';

function VirtualizedFeedList({ posts }: { posts: Post[] }) {
  const containerRef = useRef<HTMLDivElement>(null);

  const virtualizer = useVirtualizer({
    count:           posts.length,
    getScrollElement: () => containerRef.current,
    estimateSize:    () => 400, // estimated post height
    overscan:        3,          // render 3 extra items above/below viewport
  });

  return (
    <div ref={containerRef} style={{ height: '100vh', overflowY: 'auto' }}>
      <div style={{ height: `${virtualizer.getTotalSize()}px`, position: 'relative' }}>
        {virtualizer.getVirtualItems().map(virtualItem => (
          <div
            key={virtualItem.key}
            style={{
              position:  'absolute',
              top:       `${virtualItem.start}px`,
              width:     '100%',
            }}
          >
            <PostCard post={posts[virtualItem.index]} />
          </div>
        ))}
      </div>
    </div>
  );
}
```

---

### Key Tradeoffs to Mention in Interview

|Decision|Tradeoff|
|---|---|
|Cursor pagination|Stable position vs harder to jump to page N|
|Optimistic likes|Instant UX vs can show wrong count briefly|
|WebSocket for updates|Real-time vs connection overhead (polling is simpler)|
|Virtualization|Smooth scroll vs complex implementation, breaks Ctrl+F|
|Normalize store|No duplication vs more complex read/write|

---

## 8. System Design — Autocomplete

**Interviewer signal:** Debouncing, caching, network race conditions, keyboard UX, accessibility.

---

### Requirements

- Suggest completions as user types
- Keyboard navigable (↑↓ to select, Enter to confirm, Escape to close)
- Accessible to screen readers
- Debounced API calls
- Cache repeated queries

---

### Component Architecture

```
<Autocomplete>
  ├── <Input aria-autocomplete="list" aria-controls="listbox" />
  └── <Listbox role="listbox" id="listbox">
        ├── <Option role="option" aria-selected />
        ├── <Option role="option" />
        └── ...
```

---

### Core Implementation

```typescript
function useAutocomplete(fetchSuggestions: (q: string) => Promise<string[]>) {
  const [query,       setQuery]       = useState('');
  const [suggestions, setSuggestions] = useState<string[]>([]);
  const [activeIndex, setActiveIndex] = useState(-1);
  const [isOpen,      setIsOpen]      = useState(false);

  // Cache — avoid network on repeated queries
  const cache = useRef(new Map<string, string[]>());

  // Debounce + race condition guard
  useEffect(() => {
    if (!query.trim()) { setSuggestions([]); setIsOpen(false); return; }

    if (cache.current.has(query)) {
      setSuggestions(cache.current.get(query)!);
      setIsOpen(true);
      return;
    }

    let cancelled = false;
    const timer = setTimeout(async () => {
      try {
        const results = await fetchSuggestions(query);
        if (cancelled) return;
        cache.current.set(query, results);
        setSuggestions(results);
        setIsOpen(results.length > 0);
        setActiveIndex(-1);
      } catch { /* swallow — don't break the input */ }
    }, 300); // 300ms debounce

    return () => { cancelled = true; clearTimeout(timer); };
  }, [query, fetchSuggestions]);

  function handleKeyDown(e: React.KeyboardEvent) {
    if (!isOpen) return;

    switch (e.key) {
      case 'ArrowDown':
        e.preventDefault();
        setActiveIndex(i => Math.min(i + 1, suggestions.length - 1));
        break;
      case 'ArrowUp':
        e.preventDefault();
        setActiveIndex(i => Math.max(i - 1, -1));
        break;
      case 'Enter':
        if (activeIndex >= 0) {
          setQuery(suggestions[activeIndex]);
          setIsOpen(false);
        }
        break;
      case 'Escape':
        setIsOpen(false);
        setActiveIndex(-1);
        break;
    }
  }

  return { query, setQuery, suggestions, activeIndex, isOpen, handleKeyDown };
}
```

---

### Accessibility Wiring

```typescript
function Autocomplete({ fetchSuggestions }: { fetchSuggestions: (q: string) => Promise<string[]> }) {
  const listboxId = useId();
  const { query, setQuery, suggestions, activeIndex, isOpen, handleKeyDown } =
    useAutocomplete(fetchSuggestions);

  return (
    <div>
      <input
        type="text"
        value={query}
        onChange={e => setQuery(e.target.value)}
        onKeyDown={handleKeyDown}
        role="combobox"
        aria-expanded={isOpen}
        aria-autocomplete="list"
        aria-controls={listboxId}
        aria-activedescendant={
          activeIndex >= 0 ? `option-${activeIndex}` : undefined
        }
      />
      {isOpen && (
        <ul id={listboxId} role="listbox">
          {suggestions.map((s, i) => (
            <li
              key={s}
              id={`option-${i}`}
              role="option"
              aria-selected={i === activeIndex}
              onMouseDown={e => {
                e.preventDefault(); // prevent input blur before click registers
                setQuery(s);
              }}
            >
              {s}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
```

---

### Key Tradeoffs

|Decision|Tradeoff|
|---|---|
|Client-side cache|Fast repeat queries vs stale suggestions|
|300ms debounce|Fewer requests vs slight perceived delay|
|Optimistic selection|Instant UX vs race with last request|
|aria-activedescendant|Screen reader support vs complexity|

---

## 9. System Design — Real-Time Chat UI

**Interviewer signal:** WebSocket lifecycle, message ordering, optimistic sends, offline handling.

---

### Core Architecture

```
<ChatApp>
  ├── <ConversationList />        ← WebSocket: presence + unread counts
  └── <MessageThread conversationId>
        ├── <VirtualizedMessageList />  ← ordered + deduplicated
        ├── <TypingIndicator />         ← ephemeral, via WebSocket
        └── <MessageComposer />         ← optimistic send
```

---

### WebSocket Connection Management

```typescript
class ChatConnection {
  private ws:         WebSocket | null = null;
  private queue:      object[]  = [];     // messages sent while disconnected
  private reconnectDelay = 1000;          // exponential backoff

  connect(url: string) {
    this.ws = new WebSocket(url);

    this.ws.onopen = () => {
      this.reconnectDelay = 1000; // reset backoff on success
      this.flushQueue();          // send queued messages
    };

    this.ws.onclose = () => {
      setTimeout(() => this.connect(url), this.reconnectDelay);
      this.reconnectDelay = Math.min(this.reconnectDelay * 2, 30_000); // max 30s
    };
  }

  send(message: object) {
    if (this.ws?.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(message));
    } else {
      this.queue.push(message); // buffer for when reconnected
    }
  }

  private flushQueue() {
    while (this.queue.length > 0) {
      this.ws!.send(JSON.stringify(this.queue.shift()));
    }
  }
}
```

---

### Message State Model

```typescript
type MessageStatus = 'sending' | 'sent' | 'delivered' | 'failed';

interface Message {
  id:          string;
  tempId?:     string;   // client-generated ID before server confirms
  senderId:    string;
  content:     string;
  timestamp:   number;
  status:      MessageStatus;
}

// Optimistic send flow:
// 1. User hits send → add message with status='sending', tempId=uuid()
// 2. Send over WebSocket
// 3. Server responds with confirmed message + real ID
// 4. Replace tempId entry with real ID, set status='sent'
// 5. On error: set status='failed', show retry UI
```

---

### Message Deduplication

```typescript
// Server may resend messages on reconnect — deduplicate by ID
function mergeMessages(existing: Message[], incoming: Message[]): Message[] {
  const map = new Map(existing.map(m => [m.id, m]));
  for (const msg of incoming) {
    map.set(msg.id, msg); // incoming wins (more recent status)
  }
  return Array.from(map.values()).sort((a, b) => a.timestamp - b.timestamp);
}
```

---

### Key Tradeoffs

|Decision|Tradeoff|
|---|---|
|WebSocket over polling|Real-time vs connection overhead|
|Optimistic messages|Instant UX vs reconciliation on failure|
|Exponential backoff|Resilient vs delayed reconnect|
|Deduplication on client|Correct rendering vs slightly more complex state|

---

## 10. System Design — Infinite Scroll

**Interviewer signal:** Performance, memory management, scroll position preservation.

---

### IntersectionObserver-based trigger

```typescript
function useInfiniteScroll({
  onLoadMore,
  hasMore,
}: {
  onLoadMore: () => void;
  hasMore:    boolean;
}) {
  const sentinelRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const sentinel = sentinelRef.current;
    if (!sentinel || !hasMore) return;

    const observer = new IntersectionObserver(
      entries => {
        if (entries[0].isIntersecting) onLoadMore();
      },
      { rootMargin: '200px' } // trigger 200px before bottom is reached
    );

    observer.observe(sentinel);
    return () => observer.disconnect();
  }, [onLoadMore, hasMore]);

  return sentinelRef;
}

// Usage
function Feed() {
  const { data, fetchNextPage, hasNextPage, isFetchingNextPage } =
    useInfiniteQuery({ queryKey: ['feed'], queryFn: fetchFeedPage });

  const sentinelRef = useInfiniteScroll({
    onLoadMore: fetchNextPage,
    hasMore:    !!hasNextPage,
  });

  const posts = data?.pages.flatMap(p => p.posts) ?? [];

  return (
    <>
      <VirtualizedFeedList posts={posts} />
      <div ref={sentinelRef} />
      {isFetchingNextPage && <Spinner />}
      {!hasNextPage && <p>You've reached the end</p>}
    </>
  );
}
```

---

### Memory Management for Long Lists

Without virtualization, 1000+ items = DOM memory explosion:

```
Strategy 1: Virtualization (recommended) — @tanstack/virtual
  Render only visible items. DOM stays small regardless of list size.

Strategy 2: Page eviction
  Keep at most N pages in memory. When user scrolls down past page 3,
  evict page 1. Reinstate it if user scrolls back up.

Strategy 3: Windowing + placeholder
  Keep DOM nodes but replace off-screen content with empty placeholders
  of the same height. Simple but loses semantic content.
```

---

## 11. API Design from the Client's Perspective

### What interviewers test

Not REST vs GraphQL theology. They test whether you understand the client-side implications of API design choices.

---

### 11.1 REST vs GraphQL for Frontend

```
REST — predictable, cacheable, over-fetches
  GET /users/123          → full User object (even if you need only name)
  GET /users/123/posts    → waterfall request — can't batch
  GET /users/123/friends  → another waterfall

GraphQL — precise, flexible, harder to cache
  query {
    user(id: "123") {
      name                     ← only what you need
      posts(last: 5) { title }
      friends(first: 10) { name avatar }  ← single round trip
    }
  }
```

**Client-side tradeoffs:**

||REST|GraphQL|
|---|---|---|
|Network|Multiple requests (waterfalls)|Single round trip|
|Over-fetching|Common|Eliminated|
|Caching|HTTP cache works naturally|Requires client library (Apollo, urql)|
|Type safety|Manual / OpenAPI codegen|Automatic (schema → types)|
|Error handling|HTTP status codes|Always 200, errors in body|
|Complexity|Simple|High (client library, caching layer)|

---

### 11.2 Pagination Patterns

```
Offset pagination:    GET /posts?page=3&limit=20
  ✅ Easy to implement, jump to any page
  ❌ Breaks when items inserted/deleted (items shift between pages)
  ❌ Expensive for DB (OFFSET 60 scans 60 rows to skip)

Cursor pagination:    GET /posts?cursor=post_abc&limit=20
  ✅ Stable — new items don't shift existing ones
  ✅ Efficient — index seek, no scan
  ❌ Can't jump to page N

Keyset pagination:    WHERE created_at < '2024-01-01' ORDER BY created_at DESC LIMIT 20
  Same as cursor, just more explicit about the key used
```

---

### 11.3 Optimistic UI Contract

For optimistic UI to work, the API must be designed with it in mind:

```typescript
// Client sends mutation with client-generated ID
POST /posts
{ tempId: "client_uuid_123", content: "Hello" }

// Server responds with same tempId to allow reconciliation
{ id: "post_server_456", tempId: "client_uuid_123", content: "Hello" }

// Client can now replace the optimistic entry by matching tempId
```

---

### 11.4 Interview Questions

**Q: When would you choose GraphQL over REST for a new product?** A: When multiple clients (mobile, web, internal tools) need different data shapes from the same API, reducing over-fetching and waterfall requests. REST is simpler and better for public APIs that need HTTP caching. GraphQL's client-side complexity (Apollo, normalized cache, batching) is only worth it at scale.

**Q: Why does cursor pagination outperform offset pagination?** A: OFFSET N forces the DB to scan and skip N rows — O(N) even if you don't read them. Cursor uses an indexed WHERE clause — direct seek O(log n). Also, cursor is stable when items are inserted or deleted between pages; offset pages shift.

**Q: How do you handle loading, error, and empty states in a list component?** A: Discriminated union state: `status: 'loading' | 'success' | 'error' | 'empty'`. Each maps to a distinct UI. Never rely on `items.length === 0` to distinguish empty from loading — you'll flash empty state before data arrives.

---

## 12. State Management at Scale

### The layers of state

```
URL state          → current route, query params, filters
Server state       → data fetched from APIs (React Query, SWR)
Global UI state    → theme, auth, notifications (Zustand, Context)
Local UI state     → modal open, hover, focus (useState)
Form state         → field values, validation (React Hook Form)
```

The most common mistake: putting server state into global UI state (Redux store full of API responses). React Query / SWR renders this unnecessary — they are the server state layer.

---

### 12.1 Decision Tree

```
Is it shared between routes/distant components?
  No  → useState / useReducer in the component
  Yes → continue

Is it server data (fetched from API)?
  Yes → React Query / SWR (not Redux)
  No  → continue

Is it complex (many fields, transitions)?
  Yes → useReducer or Zustand
  No  → Context (theme, auth user, feature flags)
```

---

### 12.2 Zustand at Scale

```typescript
// Feature-sliced store — avoid one giant store
// auth.store.ts
interface AuthSlice {
  user:   User | null;
  token:  string | null;
  login:  (credentials: Credentials) => Promise<void>;
  logout: () => void;
}

const useAuthStore = create<AuthSlice>((set) => ({
  user:  null,
  token: null,

  login: async (credentials) => {
    const { user, token } = await api.login(credentials);
    set({ user, token });
  },

  logout: () => set({ user: null, token: null }),
}));

// Select specific slices to avoid over-rendering
// Component only re-renders when `user` changes, not the whole store
const user = useAuthStore(state => state.user);
```

---

### 12.3 React Query Patterns at Scale

```typescript
// Query key factory — centralize keys, avoid typos
const queryKeys = {
  feed:     ()               => ['feed']              as const,
  feedPage: (cursor: string) => ['feed', cursor]      as const,
  post:     (id: string)     => ['posts', id]         as const,
  user:     (id: string)     => ['users', id]         as const,
};

// Prefetch on hover — load before user navigates
function PostLink({ postId }: { postId: string }) {
  const queryClient = useQueryClient();

  return (
    <a
      href={`/post/${postId}`}
      onMouseEnter={() => {
        queryClient.prefetchQuery({
          queryKey: queryKeys.post(postId),
          queryFn:  () => api.getPost(postId),
          staleTime: 60_000,
        });
      }}
    >
      View Post
    </a>
  );
}
```

---

### 12.4 Interview Questions

**Q: Why shouldn't API responses be stored in Redux?** A: Redux is for client-owned global state. API data has its own lifecycle: loading, error, stale, cache invalidation, background refetch. Redux doesn't handle these. React Query / SWR are built specifically for server state — they handle caching, deduplication, stale-while-revalidate, and optimistic updates out of the box.

**Q: How do you prevent context from causing excessive re-renders?** A: Split context by update frequency. Fast-changing values (mouse position, scroll) should never be in context. For global state, use a selector-based store (Zustand) so components only re-render when their selected slice changes. Or split context into value + dispatch providers so consumers of dispatch don't re-render on value changes.

**Q: How would you implement role-based access control on the frontend?** A: Store user roles/permissions in auth state. Create a `usePermission(action)` hook that checks permissions. Use a `<PermissionGate permission="edit:post">` component to conditionally render. Critically — frontend RBAC is UX only. All permission enforcement must happen server-side. Frontend hides/shows UI; backend enforces access.

---

## Phase 3 — Weekly Study Schedule

|Week|Craft Focus|Interview Focus|
|---|---|---|
|1|Design patterns — Observer + Strategy|Design framework: practice with known systems|
|2|Design patterns — Factory + Component API design|News Feed — data model + pagination|
|3|Component API — compound components + controlled/uncontrolled|News Feed — real-time + virtualization|
|4|Monorepo tooling — Turborepo deep config + Nx comparison|Autocomplete — debounce + cache + a11y|
|5|Micro-frontends — Module Federation hands-on|Real-time Chat — WebSocket + optimistic messages|
|6|Accessibility — keyboard patterns + focus management|Infinite scroll — IntersectionObserver + memory|
|7|Accessibility — ARIA live regions + API-level a11y|API design — REST vs GraphQL tradeoffs|
|8|Full system: build one compound component library|State management — mock interview on system design|

**Weekly habit:** Design one system from scratch (no notes) in 45 minutes. Record yourself explaining it. Replay and find where you hesitated.

---

## Primary Sources

| Topic                            | Source                                                                                          |
| -------------------------------- | ----------------------------------------------------------------------------------------------- |
| Design patterns                  | [patterns.dev](https://www.patterns.dev/)                                                       |
| Component API design             | [Headless UI source (GitHub)](https://github.com/tailwindlabs/headlessui)                       |
| Micro-frontends                  | [micro-frontends.org](https://micro-frontends.org/)                                             |
| Module Federation                | [webpack.js.org/concepts/module-federation](https://webpack.js.org/concepts/module-federation/) |
| Turborepo docs                   | [turbo.build/repo/docs](https://turbo.build/repo/docs)                                          |
| Nx docs                          | [nx.dev/getting-started/intro](https://nx.dev/getting-started/intro)                            |
| WAI-ARIA patterns                | [w3.org/WAI/ARIA/apg/patterns](https://www.w3.org/WAI/ARIA/apg/patterns/)                       |
| Frontend system design           | [greatfrontend.com/system-design](https://www.greatfrontend.com/system-design)                  |
| Shan Lam frontend design         | [youtube.com — Frontend System Design](https://www.youtube.com/@FrontendSystemDesign)           |
| React Query patterns             | [tkdodo.eu/blog](https://tkdodo.eu/blog/practical-react-query)                                  |
| Refactoring Guru Design patterns | https://refactoring.guru/design-patterns                                                        |
