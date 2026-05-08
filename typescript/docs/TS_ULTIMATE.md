# TypeScript ULTIMATE Deep-Dive

> A complete learning path and practical engineering guide: Beginner → Expert → Compiler-Minded Architect

---

# 1. Big Picture

## What TypeScript Actually Is

TypeScript is a **static type system layered on top of JavaScript**. It is NOT a new language — it is JavaScript with a compile-time type layer that is **completely erased** before execution. Every valid JavaScript program is a valid TypeScript program. TypeScript adds zero runtime behavior.

**Why this matters:** TypeScript doesn't "run." It **checks**, then **emits** JavaScript. The types you write are a parallel universe that exists only during development and compilation. At runtime, there is no `interface`, no `type`, no generic — just plain JavaScript.

## Why TypeScript Exists

JavaScript was designed for 10-line scripts in 1995. Modern applications are 500K+ LOC monorepos with hundreds of engineers. TypeScript exists to:

1. **Catch errors before runtime** — shift bugs left
2. **Enable tooling** — autocomplete, refactoring, navigation
3. **Serve as documentation** — types ARE the contract
4. **Enable large-scale collaboration** — enforce API boundaries
5. **Reduce cognitive load** — the compiler remembers what you forget

## Core Concepts

### JavaScript Runtime vs TypeScript Compile-Time

```
┌─────────────────────────────────────────────────┐
│                 COMPILE TIME                     │
│  ┌───────────┐    ┌───────────┐    ┌──────────┐ │
│  │  Source    │───>│  Parser   │───>│   AST    │ │
│  │  .ts/.tsx  │    └───────────┘    └────┬─────┘ │
│  └───────────┘                          │       │
│                                   ┌─────▼─────┐ │
│                                   │   Type    │ │
│                                   │  Checker  │ │
│                                   └─────┬─────┘ │
│                                   ┌─────▼─────┐ │
│                                   │  Emitter  │ │
│                                   └─────┬─────┘ │
│                                         │       │
│  Types exist HERE ─────────────────────│       │
│  Types are ERASED at the boundary ──────┤       │
└─────────────────────────────────────────┼───────┘
                                          │
┌─────────────────────────────────────────▼───────┐
│                  RUNTIME                         │
│  ┌───────────┐                                  │
│  │   .js     │  ← No types. Just JavaScript.    │
│  │  output   │                                  │
│  └───────────┘                                  │
│                                                  │
│  V8 / SpiderMonkey / JavaScriptCore              │
└──────────────────────────────────────────────────┘
```

### Key Terminology

| Term | Definition |
|---|---|
| **Transpilation** | Converting TS → JS. Types are stripped, syntax may be downleveled (e.g., `enum` → IIFE). |
| **Type checking** | Verifying that values conform to their declared/inferred types. Separate from emit. |
| **Type inference** | The compiler deduces types without explicit annotations. TS has one of the most powerful inference engines of any mainstream language. |
| **Structural typing** | Types are compatible if their **shapes** match, not their names. A `Dog` with `{name: string}` is assignable to `{name: string}` even without inheritance. |
| **Nominal typing** | Types are compatible only if they share the same **declaration**. TypeScript does NOT have this natively (but you can simulate it with branded types). |
| **Type erasure** | All type annotations, interfaces, type aliases, generics — everything type-level — is removed during emit. Zero runtime cost. |
| **AST** | Abstract Syntax Tree — the tree data structure the parser produces from source code. Every node represents a syntactic construct. |
| **Declaration files** | `.d.ts` files — type-only descriptions of JS modules. They are the public API contract of a library. |
| **Module resolution** | How TS finds the file/types for `import x from "y"`. Complex rules involving `node`, `node16`, `bundler` strategies. |
| **Control flow analysis** | The compiler tracks variable types through `if`, `switch`, assignments, etc. This is how narrowing works. |
| **Narrowing** | Refining a broad type to a more specific one via control flow (`typeof`, `instanceof`, discriminants, `in`, truthiness). |
| **Generics** | Type parameters — functions/types that work over a range of types rather than a single one. The backbone of reusable type-safe code. |
| **Distributive conditional types** | `T extends U ? X : Y` distributes over union members when `T` is a naked type parameter. `string | number` becomes `(string extends U ? X : Y) | (number extends U ? X : Y)`. |

### Compiler Pipeline

```
Source Code (.ts / .tsx)
        │
        ▼
┌──────────────┐
│    Scanner    │  Tokenizes source into a stream of tokens
└──────┬───────┘
       ▼
┌──────────────┐
│    Parser     │  Builds AST from tokens
└──────┬───────┘
       ▼
┌──────────────┐
│    Binder     │  Creates symbols, sets up scopes, connects declarations
└──────┬───────┘
       ▼
┌──────────────┐
│ Type Checker  │  Resolves types, checks assignability, reports diagnostics
└──────┬───────┘
       ▼
┌──────────────┐
│   Emitter     │  Produces .js, .d.ts, .js.map outputs
└──────────────┘
```

**Key insight:** The **Binder** is the step most people don't know about. It creates the **symbol table** — the mapping from names to declarations. Without it, the type checker can't resolve anything.

### Type System Comparisons

| Aspect | TypeScript | Flow | Rust | Go | Java/C# |
|---|---|---|---|---|---|
| **Typing** | Structural | Structural | Nominal + traits | Structural (interfaces) | Nominal |
| **Soundness** | Intentionally unsound | More sound | Sound | Sound | Mostly sound |
| **Inference** | Powerful, bidirectional | Strong | Powerful | Minimal | Limited |
| **Generics** | Yes, type-erased | Yes | Yes, monomorphized | Yes (since 1.18) | Yes, reified (C#) / erased (Java) |
| **Null safety** | `strictNullChecks` | Yes | `Option<T>` | Nil checks | Nullable annotations |
| **Runtime types** | No (erased) | No (erased) | Yes | Yes | Yes (reflection) |
| **Philosophy** | Pragmatic DX | Correctness | Safety + performance | Simplicity | Enterprise OOP |

**Why TypeScript is intentionally unsound:**
- Soundness would break too much real-world JS code
- Examples of intentional unsoundness: bivariant function parameters (in methods), `any`, type assertions, `enum` value access
- Trade-off: **ergonomics and adoption over mathematical purity**

### When TypeScript Helps vs Hurts

**Helps:**
- Large codebases (>10K LOC)
- Team collaboration
- Refactoring confidence
- API contract enforcement
- Tooling (IDE autocomplete, go-to-definition)
- Onboarding new engineers

**Becomes dangerous when:**
- Types lie (assertions, `any` leaks, unsound patterns)
- Over-engineered type gymnastics that no one can read
- Runtime validation is skipped because "TypeScript handles it"
- Build times explode from complex conditional types
- Types create a false sense of security at system boundaries (API, DB, user input)

**Overengineered typing signals:**
- You need more than 3 levels of nested conditional types
- Reading a type requires more effort than reading the implementation
- `as any` is used to silence errors caused by your own types
- Compile times degrade noticeably
- New team members can't understand your types within 10 minutes

---

# 2. Learning Roadmap by Skill Level

## Level 1 — Newbie

### Core Concepts

```typescript
// Primitive types
let name: string = "Alice";
let age: number = 30;
let active: boolean = true;
let nothing: null = null;
let notDefined: undefined = undefined;
let id: bigint = 100n;
let sym: symbol = Symbol("id");

// Type inference — let TS figure it out
let city = "Berlin";  // inferred as string
const country = "DE"; // inferred as "DE" (literal type!)

// WHY: `let` widens, `const` narrows. The compiler knows a const
// can never change, so it infers the narrowest possible type.
```

```typescript
// Objects
type User = {
  name: string;
  age: number;
  email?: string; // optional
};

// Interface — almost identical, but extendable via declaration merging
interface Product {
  id: string;
  price: number;
}

// WHY use type vs interface?
// - `type` for unions, intersections, mapped types, primitives
// - `interface` for object shapes you might extend or merge
// - In practice: pick one convention and be consistent
// - Performance: interfaces are slightly faster for the compiler
//   in large codebases (they are cached by name)
```

```typescript
// Arrays
const nums: number[] = [1, 2, 3];
const names: Array<string> = ["a", "b"]; // generic syntax
const tuple: [string, number] = ["age", 30]; // fixed-length typed array

// Functions
function greet(name: string): string {
  return `Hello, ${name}`;
}

// Arrow function with inferred return
const add = (a: number, b: number) => a + b;

// Void — function returns nothing
function log(msg: string): void {
  console.log(msg);
}
```

```typescript
// Union types
type Status = "loading" | "success" | "error";

function handle(status: Status) {
  // Narrowing via control flow
  if (status === "loading") {
    // status: "loading"
  } else if (status === "success") {
    // status: "success"
  } else {
    // status: "error"
  }
}

// typeof narrowing
function process(input: string | number) {
  if (typeof input === "string") {
    return input.toUpperCase(); // narrowed to string
  }
  return input.toFixed(2); // narrowed to number
}
```

### Common Beginner Mistakes

1. **Using `any` everywhere** — defeats the purpose of TypeScript
2. **Not enabling `strict: true`** — you're missing half the safety
3. **Confusing `type` vs `interface`** — they're ~90% interchangeable
4. **Thinking types exist at runtime** — they don't. `typeof` at runtime is JavaScript's `typeof`, not TypeScript's
5. **Using `as` to silence errors** — you're lying to the compiler
6. **Not using union types** — reaching for `enum` when `"a" | "b"` suffices
7. **Typing everything explicitly** — let inference work; annotate parameters, infer returns
8. **Confusing `null` vs `undefined`** — use `strictNullChecks` and pick one convention
9. **Mutating objects and expecting types to track it** — TS tracks control flow, not mutation history
10. **Not reading error messages carefully** — TS errors are verbose but precise

### 10 Beginner Exercises

1. Create a `User` type with name, email, age (optional). Write a function that greets the user.
2. Write a function that accepts `string | number` and returns the length (string) or the number doubled.
3. Create a `TodoItem` type. Write functions to add, remove, toggle completion.
4. Write a function using a tuple `[string, number]` to represent `[name, age]`.
5. Create a type for RGB color `{ r: number, g: number, b: number }` and a function to convert to hex string.
6. Write a function that accepts an array of numbers and returns the sum, min, and max as an object.
7. Create a discriminated union for `Shape` (circle, rectangle, triangle) and a function to calculate area.
8. Write a `stringify` function that handles `string | number | boolean | null | undefined`.
9. Create an `interface` for a blog post and extend it for a published post (adds `publishedAt: Date`).
10. Write a function that filters an array to only include items matching a predicate, preserving the type.

---

## Level 2 — Junior

### Generics

```typescript
// The most important concept for reusable type-safe code

// Generic function
function identity<T>(value: T): T {
  return value;
}
const str = identity("hello"); // T inferred as "hello" (literal)
const num = identity(42);      // T inferred as 42

// Generic constraint
function getLength<T extends { length: number }>(item: T): number {
  return item.length;
}

// WHY constraints matter: Without `extends`, you can't access `.length`
// because T could be anything. Constraints narrow the type parameter.

// Generic interface
interface Repository<T> {
  findById(id: string): T | null;
  findAll(): T[];
  save(entity: T): void;
}
```

### Utility Types

```typescript
// Built-in mapped types — KNOW THESE COLD

type User = { name: string; age: number; email: string };

type PartialUser = Partial<User>;          // all optional
type RequiredUser = Required<PartialUser>; // all required
type ReadonlyUser = Readonly<User>;        // all readonly
type NameAndAge = Pick<User, "name" | "age">;
type WithoutEmail = Omit<User, "email">;
type StringRecord = Record<string, number>; // { [key: string]: number }
type NonNull = NonNullable<string | null>;  // string
type ReturnOfFn = ReturnType<typeof getLength>; // number
type ParamsOfFn = Parameters<typeof identity>; // [value: unknown]
```

### keyof, typeof, Indexed Access

```typescript
type User = { name: string; age: number; role: "admin" | "user" };

type UserKeys = keyof User;            // "name" | "age" | "role"
type UserName = User["name"];          // string
type UserRole = User["role"];          // "admin" | "user"

const config = { api: "/api", timeout: 3000 } as const;
type Config = typeof config;           // { readonly api: "/api"; readonly timeout: 3000 }
type ConfigKeys = keyof typeof config; // "api" | "timeout"

// WHY `as const`: Without it, TS widens string/number literals.
// With it, the exact values are preserved as literal types.
```

### Mapped Types

```typescript
// The foundation of utility types

type Optional<T> = {
  [K in keyof T]?: T[K];
};

type Getters<T> = {
  [K in keyof T as `get${Capitalize<string & K>}`]: () => T[K];
};

type UserGetters = Getters<User>;
// { getName: () => string; getAge: () => number; getRole: () => "admin" | "user" }
```

### Discriminated Unions

```typescript
// THE most important pattern for modeling state in TypeScript

type Result<T, E = Error> =
  | { ok: true; value: T }
  | { ok: false; error: E };

function handle<T>(result: Result<T>) {
  if (result.ok) {
    console.log(result.value); // narrowed: { ok: true; value: T }
  } else {
    console.error(result.error); // narrowed: { ok: false; error: E }
  }
}

// WHY: Discriminated unions + exhaustive checks = the safest state modeling.
// The discriminant (`ok`) lets the compiler narrow precisely.
// Add `never` exhaustiveness check:
function assertNever(x: never): never {
  throw new Error(`Unexpected: ${x}`);
}
```

### Enums vs Unions

```typescript
// PREFER string unions over enums in most cases

// Enum — has runtime cost, creates an object
enum Direction {
  Up = "UP",
  Down = "DOWN",
}

// String union — zero runtime cost, just types
type Direction2 = "UP" | "DOWN";

// WHY prefer unions:
// 1. No runtime overhead (type erasure)
// 2. Better inference
// 3. Simpler to compose
// 4. No reverse mapping weirdness (numeric enums)
// 5. Works with `as const` objects for iteration

// WHEN enums are OK:
// - You need runtime iteration over values
// - You want computed members
// - You're in a backend-heavy codebase that uses them consistently

// Better alternative: const object + type
const DIRECTIONS = { Up: "UP", Down: "DOWN" } as const;
type Direction3 = (typeof DIRECTIONS)[keyof typeof DIRECTIONS]; // "UP" | "DOWN"
```

### Function Overloads

```typescript
// Use when a function has multiple call signatures with different return types

function parse(input: string): object;
function parse(input: string, reviver: Function): object;
function parse(input: string, reviver?: Function): object {
  return reviver ? JSON.parse(input, reviver as any) : JSON.parse(input);
}

// WHY: Overloads give callers precise return types based on their arguments.
// The implementation signature is NOT visible to callers.
// Prefer generics + conditional types over overloads when possible —
// overloads don't compose well.
```

### Common Anti-Patterns

1. **`any` as escape hatch** → Use `unknown` and narrow
2. **Type assertions (`as`) to bypass errors** → Fix the type, don't lie
3. **Over-using `interface extends`** → Composition (intersection `&`) is more flexible
4. **Giant shared types file** → Colocate types with their domain
5. **Not using `satisfies`** → `satisfies` checks type while preserving inference
6. **Ignoring `readonly`** → Mutation bugs are real
7. **Using `object` type** → Too broad. Use `Record<string, unknown>` or specific shapes
8. **String-based event systems without literal types** → Lose type safety
9. **Not using discriminated unions for state** → Using `isLoading && data` booleans
10. **Exporting internal types** → Leaky abstractions that break on internal changes

### 10 Mini Project Ideas

1. Type-safe event emitter with literal event names and typed payloads
2. Generic `Result<T, E>` monad with `map`, `flatMap`, `unwrapOr`
3. Type-safe local storage wrapper with schema validation
4. Builder pattern for constructing complex objects with type safety
5. Type-safe route params extractor from route strings
6. Generic form validator with discriminated union error results
7. Type-safe state machine (status transitions enforced at type level)
8. Typed fetch wrapper with response type inference
9. Type-safe configuration loader with defaults and overrides
10. Generic repository pattern with typed query builders

---

## Level 3 — Senior

### Advanced Generics

```typescript
// Constraint propagation
function merge<T extends object, U extends object>(a: T, b: U): T & U {
  return { ...a, ...b };
}

// Default type parameters
type ApiResponse<T = unknown, E = { message: string }> =
  | { status: "success"; data: T }
  | { status: "error"; error: E };

// Multiple constraints via intersection
function clone<T extends object & { id: string }>(item: T): T {
  return { ...item };
}
```

### Conditional Types

```typescript
// The type-level `if` statement

type IsString<T> = T extends string ? true : false;

type A = IsString<string>;      // true
type B = IsString<number>;      // false
type C = IsString<"hello">;     // true

// Distributive behavior: naked type params distribute over unions
type D = IsString<string | number>; // true | false → boolean

// Preventing distribution: wrap in tuple
type IsStringStrict<T> = [T] extends [string] ? true : false;
type E = IsStringStrict<string | number>; // false

// WHY distribution exists: It's the intended behavior for type-level
// "map over union." When you write `T extends U`, if T is a union,
// each member is checked individually. This is powerful but surprising.
```

### The `infer` Keyword

```typescript
// Extract types from other types — the regex of the type system

type ReturnOf<T> = T extends (...args: any[]) => infer R ? R : never;
type ElementOf<T> = T extends (infer E)[] ? E : never;
type PromiseValue<T> = T extends Promise<infer V> ? V : T;

// Infer in template literals
type ExtractRouteParams<T extends string> =
  T extends `${string}:${infer Param}/${infer Rest}`
    ? Param | ExtractRouteParams<Rest>
    : T extends `${string}:${infer Param}`
      ? Param
      : never;

type Params = ExtractRouteParams<"/users/:userId/posts/:postId">;
// "userId" | "postId"
```

### Recursive Types

```typescript
// Types that reference themselves

type DeepPartial<T> = {
  [K in keyof T]?: T[K] extends object ? DeepPartial<T[K]> : T[K];
};

type DeepReadonly<T> = {
  readonly [K in keyof T]: T[K] extends object ? DeepReadonly<T[K]> : T[K];
};

// JSON type
type Json = string | number | boolean | null | Json[] | { [key: string]: Json };

// Path access type
type Path<T, K extends string> =
  K extends `${infer Head}.${infer Tail}`
    ? Head extends keyof T
      ? Path<T[Head], Tail>
      : never
    : K extends keyof T
      ? T[K]
      : never;

// WHY recursion limits matter: TS has a depth limit (~50 levels).
// Exceeding it gives "Type instantiation is excessively deep and possibly infinite."
// Design recursive types to terminate quickly.
```

### Template Literal Types

```typescript
type HTTPMethod = "GET" | "POST" | "PUT" | "DELETE";
type Endpoint = "/users" | "/posts";
type Route = `${HTTPMethod} ${Endpoint}`;
// "GET /users" | "GET /posts" | "POST /users" | ... (8 combinations)

type CSSProperty = `${string}-${string}`;
type EventName<T extends string> = `on${Capitalize<T>}`;
type ClickEvent = EventName<"click">; // "onClick"
```

### Variance — Covariance / Contravariance

```typescript
// THE concept that separates senior from expert understanding

// Covariance: if Dog extends Animal, then Array<Dog> extends Array<Animal>
// (output/read position — same direction)

// Contravariance: if Dog extends Animal, then
// (handler: Animal => void) extends (handler: Dog => void)
// (input/write position — reversed direction)

// WHY this matters:
type Animal = { name: string };
type Dog = Animal & { breed: string };

// Covariant (safe): readonly arrays, return types, Promises
const dogs: readonly Dog[] = [{ name: "Rex", breed: "Lab" }];
const animals: readonly Animal[] = dogs; // ✅ OK

// Contravariant (safe): function parameters in strict mode
type Handler<T> = (item: T) => void;
const animalHandler: Handler<Animal> = (a) => console.log(a.name);
const dogHandler: Handler<Dog> = animalHandler; // ✅ OK — Animal handler can handle Dogs

// TypeScript's `in` and `out` variance annotations (4.7+)
type Producer<out T> = () => T;       // covariant
type Consumer<in T> = (item: T) => void; // contravariant
type Processor<in out T> = (item: T) => T; // invariant
```

### Runtime Validation Strategy

```typescript
// THE CRITICAL INSIGHT: Types don't exist at runtime.
// Every system boundary needs runtime validation.

// Boundaries that NEED runtime validation:
// 1. API responses
// 2. User input (forms)
// 3. URL parameters
// 4. Environment variables
// 5. Database query results
// 6. WebSocket messages
// 7. localStorage/sessionStorage
// 8. PostMessage from iframes/workers
// 9. Third-party SDK responses
// 10. File uploads / parsed files

// Strategy: Schema-first, derive types

// With Zod
import { z } from "zod";

const UserSchema = z.object({
  id: z.string().uuid(),
  name: z.string().min(1),
  email: z.string().email(),
  role: z.enum(["admin", "user"]),
});

type User = z.infer<typeof UserSchema>; // Type derived from schema

// WHY schema-first:
// 1. Single source of truth (no type/validation drift)
// 2. Runtime safety at boundaries
// 3. Types are always correct (derived, not duplicated)
// 4. Composable schemas = composable types
```

### Monorepo TypeScript Architecture

```
monorepo/
├── tsconfig.base.json          ← shared compiler options
├── packages/
│   ├── shared/
│   │   ├── tsconfig.json       ← extends base, uses composite
│   │   ├── src/
│   │   └── package.json
│   ├── ui/
│   │   ├── tsconfig.json       ← references shared
│   │   ├── src/
│   │   └── package.json
│   └── app/
│       ├── tsconfig.json       ← references shared + ui
│       ├── src/
│       └── package.json
└── package.json
```

```jsonc
// tsconfig.base.json
{
  "compilerOptions": {
    "strict": true,
    "target": "ES2022",
    "module": "ESNext",
    "moduleResolution": "bundler",
    "declaration": true,
    "declarationMap": true,
    "sourceMap": true,
    "esModuleInterop": true,
    "skipLibCheck": true,
    "forceConsistentCasingInFileNames": true,
    "isolatedModules": true,
    "verbatimModuleSyntax": true
  }
}

// packages/shared/tsconfig.json
{
  "extends": "../../tsconfig.base.json",
  "compilerOptions": {
    "composite": true,
    "outDir": "dist",
    "rootDir": "src"
  },
  "include": ["src"]
}
```

### 10 Production-Grade Project Examples

1. Type-safe API client generator from OpenAPI spec
2. Full-stack type-safe app with tRPC + React Query
3. Design system with polymorphic components and compound patterns
4. Schema-driven form library with runtime validation
5. Type-safe i18n system with exhaustive key checking
6. Event-driven architecture with typed event bus
7. Type-safe CLI tool with command parsing and validation
8. Database ORM wrapper with type-safe query builder
9. Plugin system with typed extension points
10. Monorepo shared package with declaration-only exports

---

## Level 4 — Expert

### Type-Level Programming

```typescript
// Types as a programming language — TypeScript's type system is Turing complete

// Type-level arithmetic (simplified)
type BuildTuple<N extends number, T extends any[] = []> =
  T["length"] extends N ? T : BuildTuple<N, [...T, any]>;

type Add<A extends number, B extends number> =
  [...BuildTuple<A>, ...BuildTuple<B>]["length"];

type Sum = Add<3, 4>; // 7

// String parsing at type level
type Split<S extends string, D extends string> =
  S extends `${infer Head}${D}${infer Tail}`
    ? [Head, ...Split<Tail, D>]
    : [S];

type Parts = Split<"a.b.c", ".">; // ["a", "b", "c"]
```

### Compiler Mental Model

**What the compiler actually does with generics:**

```typescript
function wrap<T>(value: T): { wrapped: T } {
  return { wrapped: value };
}

const result = wrap("hello");
// Inference steps:
// 1. Compiler sees call site: wrap("hello")
// 2. "hello" has type "hello" (string literal)
// 3. T is bound to "hello"
// 4. Return type becomes { wrapped: "hello" }
// 5. result: { wrapped: "hello" }
//
// If you wrote wrap<string>("hello"), T = string,
// and you LOSE the literal type. Let inference work.
```

**Inference priority rules:**
1. Explicit type argument always wins
2. Contextual typing (e.g., callback parameter types) is next
3. Candidate types from arguments are collected
4. Best common type is selected
5. If ambiguous, TS widens or falls back to constraints

### Distributive Conditional Internals

```typescript
type ToArray<T> = T extends any ? T[] : never;

type Result = ToArray<string | number>;
// Distributes:
// = (string extends any ? string[] : never) | (number extends any ? number[] : never)
// = string[] | number[]
// NOT (string | number)[]

// To get (string | number)[], prevent distribution:
type ToArrayNonDist<T> = [T] extends [any] ? T[] : never;
type Result2 = ToArrayNonDist<string | number>; // (string | number)[]
```

### Declaration Emit Strategy

```typescript
// When publishing a library, your .d.ts files ARE your public API

// Rules for clean declaration emit:
// 1. Don't use inferred return types for public functions — annotate them
// 2. Don't export internal types
// 3. Use `/** @internal */` + stripInternal tsconfig option
// 4. Test your declarations with `tsd` or `expect-type`
// 5. Use `composite: true` for project references
// 6. Generate declaration maps for go-to-source in consumers

// Testing declarations:
// npm install -D tsd
import { expectType, expectError } from "tsd";

expectType<string>(myFunction("input"));
expectError(myFunction(42)); // should error
```

### Architecture Review Checklist

| Area | Question |
|---|---|
| **Strictness** | Is `strict: true` enabled? Any `any` leaks? |
| **Boundaries** | Are all external inputs validated at runtime? |
| **Inference** | Are we fighting inference or working with it? |
| **Public API** | Are exported types intentional and stable? |
| **Generics** | Are generic constraints tight enough? Too tight? |
| **Performance** | Are there deeply nested conditional types? |
| **Module resolution** | Is `moduleResolution` correct for the runtime? |
| **Declaration emit** | Do `.d.ts` files expose internal types? |
| **Discriminated unions** | Are states modeled as unions, not boolean combos? |
| **Error handling** | Is `Result<T, E>` used instead of thrown errors? |
| **Schema alignment** | Do types and runtime schemas derive from one source? |
| **Monorepo** | Are project references set up correctly? |

### What Expert Engineers Care About That Juniors Miss

1. **Inference quality** — Does the API surface infer well, or do users need to annotate?
2. **Declaration stability** — Changing an internal type shouldn't break consumer `.d.ts`
3. **Type computation cost** — Complex types slow down IDE and CI
4. **Contravariance in callbacks** — Function parameter types go in the opposite direction
5. **`satisfies` vs `as const` vs annotation** — Each has different inference behavior
6. **Module boundary types** — What types cross package boundaries?
7. **Branded types for nominal safety** — `UserId` should not be assignable to `PostId`
8. **Excess property checking** — Only works on object literals, not variables
9. **Widening vs narrowing** — When and why TS widens or narrows
10. **`isolatedModules` implications** — Required for SWC/esbuild, restricts `const enum` and namespace merging

### 15 Advanced Engineering Discussion Topics

1. How do you version public types in a library without breaking consumers?
2. When should you use `unknown` vs generics for maximum flexibility?
3. How do you balance type strictness with developer velocity?
4. What's the right granularity for discriminated union variants?
5. How do you handle API response types when the backend schema is unreliable?
6. Should internal packages in a monorepo export types or just implementations?
7. How do you test types (not runtime behavior, but type correctness)?
8. When is `any` acceptable in production code?
9. How do you design generic hooks that compose well?
10. What's the cost of deep `DeepPartial<T>` types on compile performance?
11. How should you type error boundaries in React?
12. What's the right strategy for typing third-party libraries with incomplete types?
13. How do you handle type drift between frontend and backend?
14. When should you use branded types vs wrapper classes?
15. How do you prevent type exports from becoming your library's implicit API?

---

## Level 5 — Compiler / Language Architect Mindset

### TypeScript Compiler Architecture

```
┌────────────────────────────────────────────────────┐
│                  tsc / tsserver                      │
│                                                      │
│  ┌──────────┐  ┌────────┐  ┌────────┐  ┌─────────┐ │
│  │ Program  │──│ Source  │──│ Source │──│Compiler │ │
│  │          │  │  File   │  │  File  │  │ Options │ │
│  └────┬─────┘  └────────┘  └────────┘  └─────────┘ │
│       │                                              │
│  ┌────▼─────┐                                       │
│  │ Scanner  │ → Token stream                        │
│  └────┬─────┘                                       │
│  ┌────▼─────┐                                       │
│  │ Parser   │ → AST (SyntaxTree nodes)              │
│  └────┬─────┘                                       │
│  ┌────▼─────┐                                       │
│  │ Binder   │ → Symbols + Scopes                    │
│  └────┬─────┘                                       │
│  ┌────▼─────────┐                                   │
│  │ Type Checker  │ → Type resolution, diagnostics   │
│  │ (checker.ts)  │   ~50K lines, the heart of TS    │
│  └────┬─────────┘                                   │
│  ┌────▼─────┐                                       │
│  │ Emitter  │ → .js / .d.ts / .map                  │
│  └──────────┘                                       │
│                                                      │
│  ┌────────────────────┐                             │
│  │ Language Service    │ → IDE features              │
│  │ (completions, hover,│   (powers VS Code TS)      │
│  │  diagnostics, etc.) │                            │
│  └────────────────────┘                             │
└────────────────────────────────────────────────────┘
```

**Key files in the compiler:**
- `scanner.ts` — tokenizer
- `parser.ts` — AST construction
- `binder.ts` — symbol table creation
- `checker.ts` — type checking (~50K LOC, the brain)
- `emitter.ts` — JavaScript output
- `transformer.ts` — AST transforms before emit

### Babel vs tsc vs SWC vs esbuild

| Feature | tsc | Babel | SWC | esbuild |
|---|---|---|---|---|
| **Language** | TypeScript | JavaScript | Rust | Go |
| **Type checking** | ✅ Yes | ❌ No | ❌ No | ❌ No |
| **Speed** | Slow | Medium | Fast | Fastest |
| **Emit quality** | Reference | Good | Good | Good |
| **Plugin system** | Transformers | Rich plugins | Limited | Minimal |
| **Declaration emit** | ✅ Yes | ❌ No | ❌ No | ❌ No |
| **Decorators** | TS legacy + TC39 | TC39 via plugin | TC39 | Limited |
| **Best for** | Type checking, .d.ts | Legacy/custom transforms | Fast builds | Bundling |

**Key insight:** Modern setups use **tsc for type checking only** (`noEmit: true`) + **SWC/esbuild for transpilation**. This gives you the best of both: type safety + speed.

### Ergonomics vs Soundness Trade-offs

TypeScript deliberately chose **ergonomics** over **soundness** in several cases:

| Unsound Pattern | Why It Exists |
|---|---|
| Method parameter bivariance | Too many callback patterns would break |
| `any` type | Escape hatch for gradual adoption |
| Type assertions (`as`) | Developers know more than the compiler sometimes |
| `enum` member access | Convenience over safety |
| Index signatures return `T` not `T | undefined` | Too noisy (use `noUncheckedIndexedAccess`) |
| Function arity (fewer params assignable to more) | Callback convention in JS |

### Future of TypeScript

- **Type annotations proposal (TC39 Stage 1)** — types as comments in JS
- **Isolated declarations** — faster declaration emit without type checking
- **`using` / `await using`** — explicit resource management (TS 5.2+)
- **Decorator metadata** — runtime access to decorator info
- **Continued focus on performance** — faster checking, faster IDE
- **Go port of tsc** — announced 2025, 10x faster type checking

---

# 3. Setup Guide

## Installing TypeScript

```bash
# Global (for CLI)
npm install -g typescript

# Project-level (recommended)
npm install -D typescript

# Check version
npx tsc --version
```

## tsconfig Setups

### Beginner

```jsonc
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "ESNext",
    "moduleResolution": "bundler",
    "strict": true,
    "esModuleInterop": true,
    "skipLibCheck": true,
    "outDir": "dist"
  },
  "include": ["src"]
}
```

### Production App (React + Next.js)

```jsonc
{
  "compilerOptions": {
    "target": "ES2022",
    "lib": ["ES2022", "DOM", "DOM.Iterable"],
    "module": "ESNext",
    "moduleResolution": "bundler",
    "jsx": "preserve",
    "strict": true,
    "noUncheckedIndexedAccess": true,
    "exactOptionalPropertyTypes": true,
    "noEmit": true,
    "esModuleInterop": true,
    "skipLibCheck": true,
    "forceConsistentCasingInFileNames": true,
    "isolatedModules": true,
    "verbatimModuleSyntax": true,
    "incremental": true,
    "resolveJsonModule": true,
    "paths": {
      "@/*": ["./src/*"]
    }
  },
  "include": ["src", "next-env.d.ts"],
  "exclude": ["node_modules"]
}
```

### Library

```jsonc
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "ESNext",
    "moduleResolution": "bundler",
    "strict": true,
    "declaration": true,
    "declarationMap": true,
    "sourceMap": true,
    "outDir": "dist",
    "rootDir": "src",
    "esModuleInterop": true,
    "skipLibCheck": true,
    "forceConsistentCasingInFileNames": true,
    "isolatedModules": true,
    "verbatimModuleSyntax": true,
    "stripInternal": true
  },
  "include": ["src"],
  "exclude": ["**/*.test.ts", "**/*.spec.ts"]
}
```

### Monorepo Base

```jsonc
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "ESNext",
    "moduleResolution": "bundler",
    "strict": true,
    "declaration": true,
    "declarationMap": true,
    "sourceMap": true,
    "composite": true,
    "esModuleInterop": true,
    "skipLibCheck": true,
    "forceConsistentCasingInFileNames": true,
    "isolatedModules": true,
    "verbatimModuleSyntax": true
  }
}
```

## Strict Mode Explained

`"strict": true` enables ALL of these:

| Flag | What It Does | Why It Matters |
|---|---|---|
| `strictNullChecks` | `null`/`undefined` not assignable to other types | Prevents the #1 runtime error |
| `strictFunctionTypes` | Contravariant function parameters | Catches callback type bugs |
| `strictBindCallApply` | Typed `bind`, `call`, `apply` | No more `any` leaking from these |
| `strictPropertyInitialization` | Class properties must be initialized | Catches uninitialized members |
| `noImplicitAny` | Must annotate when inference fails | No hidden `any` |
| `noImplicitThis` | Must type `this` in functions | Prevents `this` confusion |
| `useUnknownInCatchVariables` | `catch(e)` gives `unknown` not `any` | Forces proper error handling |
| `alwaysStrict` | Emits `"use strict"` | JS strict mode everywhere |

**Additional recommended flags beyond `strict`:**

```jsonc
{
  "noUncheckedIndexedAccess": true,     // obj[key] returns T | undefined
  "exactOptionalPropertyTypes": true,   // { x?: string } ≠ { x: string | undefined }
  "noFallthroughCasesInSwitch": true,   // prevents switch fallthrough
  "forceConsistentCasingInFileNames": true // prevents case-sensitivity bugs
}
```

## Path Aliases

```jsonc
// tsconfig.json
{
  "compilerOptions": {
    "baseUrl": ".",
    "paths": {
      "@/*": ["./src/*"],
      "@components/*": ["./src/components/*"],
      "@utils/*": ["./src/utils/*"]
    }
  }
}
```

**Note:** Path aliases in tsconfig are ONLY for the type checker. Your bundler (Vite, webpack, Next.js) must also be configured to resolve them.

## ESM vs CJS

```jsonc
// For ESM output (modern):
{
  "compilerOptions": {
    "module": "ESNext",        // or "NodeNext" for Node.js
    "moduleResolution": "bundler" // or "nodenext"
  }
}
// package.json: "type": "module"

// For CJS output (legacy):
{
  "compilerOptions": {
    "module": "CommonJS",
    "moduleResolution": "node"
  }
}

// For libraries supporting BOTH (dual package):
// Use tsup or unbuild to build ESM + CJS from ESM source
```

## Recommended Architecture for Your Stack

```
your-project/
├── tsconfig.base.json           ← strict, shared options
├── apps/
│   ├── web/                     ← Next.js app
│   │   ├── tsconfig.json        ← extends base
│   │   └── src/
│   └── docs/                    ← Astro site
│       ├── tsconfig.json
│       └── src/
├── packages/
│   ├── ui/                      ← Shared React components
│   │   ├── tsconfig.json        ← composite: true
│   │   └── src/
│   ├── shared/                  ← Shared types + utils
│   │   ├── tsconfig.json        ← composite: true
│   │   └── src/
│   └── config/                  ← Shared configs (TS, ESLint)
│       └── tsconfig/
├── turbo.json                   ← Turborepo config
└── package.json
```

---

# 4. TypeScript Tooling Comparison

## Build & Transpilation Tools

| Tool | Philosophy | Type Check | Speed | DX | Library Author | When To Use | When NOT |
|---|---|---|---|---|---|---|---|
| **tsc** | Reference compiler | ✅ | Slow | Good | ✅ `.d.ts` emit | Type checking, declarations | Fast builds |
| **Babel** | JS transforms | ❌ | Medium | Rich plugins | ⚠️ | Legacy, custom transforms | New projects |
| **SWC** | Fast Rust compiler | ❌ | Very fast | Good | ⚠️ | Next.js, fast builds | Need type checking |
| **esbuild** | Ultra-fast bundler | ❌ | Fastest | Minimal config | ⚠️ | Bundling, dev servers | Complex transforms |
| **tsup** | Zero-config lib build | ❌ (uses esbuild) | Fast | Excellent | ✅ | Library publishing | App builds |
| **tsx** | TS execution | ❌ | Fast | Instant run | ❌ | Scripts, dev | Production |
| **ts-node** | TS execution | Optional | Slow | OK | ❌ | Legacy scripts | New projects |
| **Vite** | Dev-first bundler | ❌ (uses esbuild) | Fast | Best-in-class | ⚠️ | App dev servers | Libraries |

## Linting & Formatting

| Tool | Philosophy | Speed | TS Support | When To Use |
|---|---|---|---|---|
| **ESLint** | Extensible linting | Slow | Via `typescript-eslint` | Need custom rules, TS-aware linting |
| **Biome** | Fast all-in-one | Very fast | Native | Speed-focused, simpler rulesets |

## Runtime Validation

| Tool | Philosophy | Bundle Size | Composability | Inference | When To Use |
|---|---|---|---|---|---|
| **Zod** | Schema-first | ~14KB | Excellent | ✅ `z.infer` | Most projects, best ecosystem |
| **Valibot** | Modular/tree-shakeable | ~1KB used | Excellent | ✅ | Bundle-sensitive projects |
| **io-ts** | FP-style codecs | ~5KB | FP-heavy | ✅ | FP-oriented codebases |

**Recommendation for your stack:** Zod for most things. Valibot if bundle size matters (Astro).

---

# 5. Cheatsheet

## Type Syntax Quick Reference

```typescript
// Primitives
string, number, boolean, null, undefined, bigint, symbol, void, never, unknown, any

// Object
{ key: Type }
{ key?: Type }          // optional
{ readonly key: Type }  // immutable

// Array
Type[]
Array<Type>
[Type, Type]            // tuple
readonly Type[]         // immutable array

// Function
(a: A, b: B) => Return
(...args: A[]) => Return

// Union & Intersection
A | B                   // either
A & B                   // both

// Literal
"exact" | 42 | true

// Template Literal
`prefix${string}suffix`
```

## Generic Patterns

```typescript
// Identity
<T>(x: T) => T

// Constrained
<T extends string>(x: T) => T

// Default
<T = string>(x: T) => T

// Multiple
<T, U>(x: T, y: U) => [T, U]

// Constrained by another param
<T, K extends keyof T>(obj: T, key: K) => T[K]
```

## Conditional Type Patterns

```typescript
T extends U ? X : Y              // basic
T extends infer U ? U : never    // extract
T extends (...args: infer P) => infer R ? [P, R] : never  // function parts
[T] extends [U] ? X : Y          // non-distributive
T extends any ? T[] : never      // distributive map
```

## Utility Type Implementations

```typescript
type MyPartial<T>    = { [K in keyof T]?: T[K] };
type MyRequired<T>   = { [K in keyof T]-?: T[K] };
type MyReadonly<T>   = { readonly [K in keyof T]: T[K] };
type MyPick<T, K extends keyof T> = { [P in K]: T[P] };
type MyOmit<T, K extends keyof T> = Pick<T, Exclude<keyof T, K>>;
type MyRecord<K extends keyof any, V> = { [P in K]: V };
type MyExclude<T, U> = T extends U ? never : T;
type MyExtract<T, U> = T extends U ? T : never;
type MyNonNullable<T> = T extends null | undefined ? never : T;
type MyReturnType<T extends (...args: any) => any> = T extends (...args: any) => infer R ? R : never;
type MyParameters<T extends (...args: any) => any> = T extends (...args: infer P) => any ? P : never;
```

## Narrowing Patterns

```typescript
typeof x === "string"           // typeof guard
x instanceof MyClass            // instanceof guard
"key" in obj                    // in operator
x === null                      // equality
x != null                       // non-null
Array.isArray(x)                // array check
x.kind === "circle"             // discriminant

// Custom type guard
function isString(x: unknown): x is string {
  return typeof x === "string";
}

// Assertion function
function assertDefined<T>(x: T | undefined): asserts x is T {
  if (x === undefined) throw new Error("Expected defined");
}
```

## React Typing Patterns

```typescript
// Component props
type Props = {
  children: React.ReactNode;
  onClick?: (e: React.MouseEvent<HTMLButtonElement>) => void;
  variant?: "primary" | "secondary";
};

// FC (optional — you can just type the function directly)
const Button = ({ children, onClick, variant = "primary" }: Props) => { ... };

// forwardRef
const Input = React.forwardRef<HTMLInputElement, InputProps>((props, ref) => { ... });

// Polymorphic component
type PolymorphicProps<C extends React.ElementType> = {
  as?: C;
} & React.ComponentPropsWithoutRef<C>;

// Generic component
function List<T>({ items, renderItem }: {
  items: T[];
  renderItem: (item: T) => React.ReactNode;
}) { ... }

// Event handlers
onChange: React.ChangeEventHandler<HTMLInputElement>
onSubmit: React.FormEventHandler<HTMLFormElement>

// Context with non-null
const MyContext = React.createContext<ContextType | null>(null);
function useMyContext() {
  const ctx = React.useContext(MyContext);
  if (!ctx) throw new Error("Missing provider");
  return ctx;
}
```

## Common Errors & Fixes

| Error | Cause | Fix |
|---|---|---|
| `Type 'X' is not assignable to type 'Y'` | Shape mismatch | Check property types |
| `Object is possibly 'undefined'` | Missing null check | Add `if (x)` or `x!` or `x ?? default` |
| `Type 'string' is not assignable to type '"a" \| "b"'` | Widened literal | Use `as const` or explicit annotation |
| `Property does not exist on type` | Missing property in type | Add to type or narrow first |
| `Type instantiation is excessively deep` | Recursive type too deep | Simplify recursion, add termination |
| `Argument not assignable to parameter` | Wrong argument type | Check function signature |
| `Cannot find module` | Module resolution failure | Check paths, `moduleResolution`, `types` |
| `'X' refers to a value, but is used as a type` | Mixing value/type namespaces | Use `typeof X` or import the type |

## Performance Tips

1. Use `interface` over `type` for object shapes (cached by name)
2. Avoid deep recursive types — cap at 3-4 levels
3. Use `skipLibCheck: true` — don't re-check `node_modules` types
4. Use `incremental: true` — caches previous results
5. Avoid complex conditional types in hot paths
6. Prefer `satisfies` over `as const` + assertion chains
7. Use project references in monorepos for parallel checking
8. Profile with `--generateTrace` flag

---

# 6. Real-World Engineering Mindset

## API Typing

**Problem:** API responses come from outside the type system. Types can lie.

**Strategies:**

| Strategy | Approach | Pros | Cons | Best For |
|---|---|---|---|---|
| **Trust the backend** | Cast `response.json() as User` | Simple | Unsafe, types can drift | Prototypes |
| **Runtime validation** | `UserSchema.parse(data)` | Safe, single source of truth | Bundle size, perf | Production |
| **Code generation** | OpenAPI → types + client | Auto-synced, accurate | Build step, rigidity | Large APIs |
| **tRPC** | End-to-end type inference | Zero drift, amazing DX | Requires Node backend | Full-stack TS |

**Senior choice:** tRPC if you own the backend. OpenAPI codegen + Zod validation otherwise.

## React Component Typing

**Problem:** Components need to be flexible, composable, and type-safe.

```typescript
// ❌ Don't: Overly permissive
type Props = { [key: string]: any };

// ❌ Don't: Overly restrictive
type Props = { variant: "primary"; color: "blue" };

// ✅ Do: Constrained flexibility
type Props = {
  variant: "primary" | "secondary" | "ghost";
  size?: "sm" | "md" | "lg";
  children: React.ReactNode;
} & Omit<React.ComponentPropsWithRef<"button">, "className">;

// ✅ Do: Polymorphic for design systems
type ButtonProps<C extends React.ElementType = "button"> = {
  as?: C;
  variant: "primary" | "secondary";
} & Omit<React.ComponentPropsWithoutRef<C>, "as" | "variant">;
```

## Generic Hooks

```typescript
// Pattern: Generic hook with constrained inference
function useLocalStorage<T>(
  key: string,
  initialValue: T,
  schema: z.ZodType<T> // runtime validation!
): [T, (value: T | ((prev: T) => T)) => void] {
  const [stored, setStored] = useState<T>(() => {
    const item = localStorage.getItem(key);
    if (!item) return initialValue;
    const parsed = schema.safeParse(JSON.parse(item));
    return parsed.success ? parsed.data : initialValue;
  });
  // ...
}

// WHY schema parameter: localStorage is a system boundary.
// Types don't exist at runtime. Schema validates at the boundary.
```

## SDK Design

```typescript
// Pattern: Builder-style type-safe SDK

class APIClient<TRoutes extends Record<string, RouteConfig>> {
  constructor(private routes: TRoutes) {}

  call<K extends keyof TRoutes>(
    route: K,
    input: TRoutes[K]["input"]
  ): Promise<TRoutes[K]["output"]> {
    // ...
  }
}

// Type-safe config
const client = new APIClient({
  getUser: {
    method: "GET",
    path: "/users/:id",
    input: z.object({ id: z.string() }),
    output: z.object({ name: z.string() }),
  },
} as const);

// Usage: fully inferred
const user = await client.call("getUser", { id: "123" });
// user: { name: string }
```

## Schema-Driven Development

```typescript
// THE strategy for modern TypeScript apps:
// Schema is the source of truth for BOTH types and validation

// 1. Define schema
const UserSchema = z.object({
  id: z.string().uuid(),
  name: z.string(),
  email: z.string().email(),
  role: z.enum(["admin", "user"]),
  metadata: z.record(z.unknown()).optional(),
});

// 2. Derive type
type User = z.infer<typeof UserSchema>;

// 3. Use everywhere
// - API response validation
// - Form validation
// - Database row typing
// - Event payload typing

// WHY: One change to the schema updates BOTH the type and the validation.
// No drift. No duplication. No "I updated the type but forgot the validator."
```

## Monorepo Shared Types

**Problem:** Types shared across packages can create tight coupling.

**Strategy:**

```typescript
// packages/shared/src/types.ts — shared domain types
export type UserId = string & { __brand: "UserId" };
export type PostId = string & { __brand: "PostId" };

export type User = {
  id: UserId;
  name: string;
};

// Schemas live here too
export const UserSchema = z.object({ ... });
export type User = z.infer<typeof UserSchema>;

// RULE: Shared types should be DOMAIN types, not implementation types.
// Don't share React component prop types across packages.
// Don't share internal state types.
// Share: entities, value objects, API contracts, events.
```

---

# 7. Brainstorm / Open Questions

## Type Systems (10)

1. Should this return type be inferred or explicitly annotated? When does explicit annotation improve clarity vs harm DX?
2. Is this generic truly necessary, or is it adding complexity for a single use case?
3. What happens when your conditional type distributes unexpectedly over a union?
4. Can you model this domain concept with discriminated unions instead of class hierarchies?
5. When is `unknown` the right choice over a generic `T`?
6. How do you handle types that are "almost the same" across contexts (e.g., API vs DB vs UI)?
7. Should you use branded types for IDs, or is `string` good enough?
8. How do you type a function that returns different types based on runtime configuration?
9. What's the type-level equivalent of "dependency injection"? (Answer: generics + constraints)
10. When does structural typing cause bugs that nominal typing would prevent?

## API Design (10)

11. Should API client types be generated or hand-written?
12. How do you handle API versioning in your type layer?
13. What happens to consumers when you change a shared type?
14. Should you use Zod schemas at the API boundary, at the consumer, or both?
15. How do you type a REST API client that works with any endpoint shape?
16. When is tRPC overkill? When is it essential?
17. Should GraphQL types be generated from the schema or hand-maintained?
18. How do you type middleware that transforms request/response shapes?
19. What's the right abstraction level for a typed HTTP client?
20. How do you handle partial responses and sparse fieldsets in types?

## Runtime vs Compile-Time (10)

21. Where are the boundaries in your system where types stop being trustworthy?
22. Are you validating at every system boundary, or only some?
23. What runtime guarantees does TypeScript NOT provide that you assume it does?
24. How do you handle `JSON.parse()` — the most dangerous untyped operation?
25. Should you use `satisfies` or `as const` to preserve literals at the boundary?
26. How do you type `localStorage` / `sessionStorage` safely?
27. What happens when a third-party API changes shape but your types don't?
28. Should environment variables be typed with `z.env()` or manual casting?
29. How do you type `postMessage` between workers/iframes?
30. When should runtime validation throw vs return `Result<T, E>`?

## DX (10)

31. Does this type improve autocomplete, or does it make it worse?
32. Is this error message helpful to the developer, or cryptic?
33. Would `satisfies` give better inference than explicit annotation here?
34. Are your generic constraints helping inference or fighting it?
35. Does this type compose well, or does it force users to unwrap/re-wrap?
36. Would a simpler type with a runtime check give better DX?
37. Is this overloaded function signature really needed, or would a union input suffice?
38. How many levels deep can a developer read this type before giving up?
39. Does your library require users to write `as const` to get good inference?
40. Would a builder pattern give better autocomplete than a config object?

## Compiler Behavior (10)

41. Why does TypeScript infer `string` here instead of the literal type?
42. Why does this generic fail to infer when there are multiple inference sites?
43. What's the difference between `T extends X` in a conditional vs in a constraint?
44. Why does excess property checking only work on object literals?
45. How does control flow analysis interact with closures and callbacks?
46. Why does `readonly` not work as deeply as you'd expect?
47. When does TypeScript widen a type, and can you prevent it?
48. Why does `satisfies` preserve the narrower type while `:` annotation doesn't?
49. What happens to `never` in a union vs an intersection?
50. How does the compiler decide which overload to select?

## Performance (10)

51. How does this conditional type affect `tsc --watch` performance?
52. Is this recursive type hitting the depth limit in practice?
53. Would `interface` be faster than `type` here for the compiler?
54. Are you using `skipLibCheck` to avoid re-checking `node_modules`?
55. Would project references speed up your monorepo builds?
56. How do you profile TypeScript compilation performance?
57. Is this mapped type being instantiated too many times?
58. Should you cache complex computed types with intermediate type aliases?
59. How does `--generateTrace` help identify type-checking bottlenecks?
60. What's the performance impact of `noUncheckedIndexedAccess` in a large codebase?

## Library Architecture (10)

61. What types should be in your public API surface vs internal?
62. How do you version breaking type changes independently from runtime changes?
63. Should your library export Zod schemas, types, or both?
64. How do you test that your declaration files are correct?
65. What's the right amount of generics for a library API?
66. Should your library use `interface` or `type` for extensibility?
67. How do you handle peer dependency types (e.g., React types)?
68. When should a library use `const` type parameters (TS 5.0)?
69. How do you design types that survive a major version upgrade?
70. Should internal package types be re-exported from a barrel file?

## Large-Scale Systems (12)

71. What type architecture scales across 50+ packages?
72. How do you prevent type changes in one package from cascading failures?
73. Should you use a shared types package or derive types locally?
74. How do you handle type alignment between frontend and backend in a monorepo?
75. What's the migration strategy for adding strict mode to a 200K LOC codebase?
76. How do you enforce type conventions across teams?
77. Should you use module augmentation for third-party types or wrapper types?
78. What's the right level of type abstraction for a platform team?
79. How do you handle gradual TypeScript adoption in a legacy JS codebase?
80. When should you write custom ESLint rules for type conventions?
81. How do you maintain type safety across micro-frontends?
82. What's the strategy for typing a shared design system used by 10 teams?

---

# 8. Practice Questions

## Beginner (25 Questions)

### Q1
**Type:** What is the resulting type?
```typescript
const x = "hello";
```
**Answer:** `"hello"` (string literal type)
**Why:** `const` declarations infer the narrowest possible type. Since `x` can never be reassigned, TS infers the literal `"hello"` instead of `string`.

### Q2
**Type:** What is the resulting type?
```typescript
let x = "hello";
```
**Answer:** `string`
**Why:** `let` can be reassigned, so TS widens to `string`.

### Q3
**Type:** True or False: TypeScript types exist at runtime.
**Answer:** False
**Why:** All types are erased during compilation. At runtime, only JavaScript exists.

### Q4
**Type:** What error does this produce?
```typescript
function greet(name: string): string {
  return 42;
}
```
**Answer:** `Type 'number' is not assignable to type 'string'`
**Why:** The return type is annotated as `string` but the function returns a `number`.

### Q5
**Type:** What is the resulting type?
```typescript
const arr = [1, "two", true];
```
**Answer:** `(string | number | boolean)[]`
**Why:** TS infers the best common type for array elements.

### Q6
**Type:** Fill in the blank: To make a property optional, use `___`.
**Answer:** `?` after the property name: `{ name?: string }`

### Q7
**Type:** What is the type of `x` after the `if`?
```typescript
function f(x: string | number) {
  if (typeof x === "string") {
    // x is ?
  }
}
```
**Answer:** `string`
**Why:** `typeof` guard narrows the union.

### Q8
**Type:** Which is correct?
```typescript
// A
interface User { name: string }
// B
type User = { name: string }
```
**Answer:** Both are correct. `interface` supports declaration merging; `type` supports unions and intersections. For object shapes, they're interchangeable.

### Q9
**Type:** What's wrong?
```typescript
const user: { name: string; age: number } = { name: "Alice" };
```
**Answer:** Property `age` is missing. All non-optional properties are required.

### Q10
**Type:** What is the resulting type?
```typescript
function add(a: number, b: number) {
  return a + b;
}
```
**Answer:** Return type is inferred as `number`.

### Q11
**Type:** What does `void` mean as a return type?
**Answer:** The function doesn't return a meaningful value. It can return `undefined` or nothing. Unlike `never`, the function DOES complete.

### Q12
**Type:** What's the difference between `null` and `undefined` in TypeScript?
**Answer:** Both are distinct types when `strictNullChecks` is on. `undefined` means "not yet assigned." `null` means "intentionally empty." Convention: pick one and be consistent.

### Q13
**Type:** Debugging. Why does this error?
```typescript
const obj = { name: "Alice", age: 30 };
obj.email = "a@b.com";
```
**Answer:** Property `email` does not exist on `{ name: string; age: number }`. TS inferred the shape at declaration.

### Q14
**Type:** What is a tuple type?
**Answer:** A fixed-length array with typed positions: `[string, number]` means exactly 2 elements, first is string, second is number.

### Q15
**Type:** What does `unknown` mean?
**Answer:** The type-safe counterpart of `any`. You can assign anything TO `unknown`, but you can't use it without narrowing first. Always prefer `unknown` over `any`.

### Q16
**Type:** What is `never`?
**Answer:** The type with no values. Represents: unreachable code, impossible types, exhaustiveness checks. A function returning `never` never completes (throws or infinite loops).

### Q17
**Type:** What's wrong here?
```typescript
function f(x: string | number) {
  return x.toUpperCase();
}
```
**Answer:** `toUpperCase` doesn't exist on `number`. Must narrow first with `typeof x === "string"`.

### Q18
**Type:** True or False: `any` disables type checking for that value.
**Answer:** True. `any` bypasses all type checks and propagates unsafety to everything it touches. Avoid it.

### Q19
**Type:** What is a union type?
**Answer:** A type that can be one of several types: `string | number` means "either string OR number."

### Q20
**Type:** Scenario. A colleague writes `as any` to fix a type error. What do you suggest?
**Answer:** Find the root cause. Use `unknown` + narrowing, fix the type definition, or use a type guard. `as any` hides bugs.

### Q21
**Type:** What is `readonly`?
```typescript
type User = { readonly name: string };
```
**Answer:** The property cannot be reassigned after initialization. Compile-time only — not enforced at runtime.

### Q22
**Type:** What does `Array.isArray()` do to types?
**Answer:** It's a built-in type guard. Narrows `unknown` or a union to the array type.

### Q23
**Type:** What is the result?
```typescript
type A = string & number;
```
**Answer:** `never` — no value can be both `string` AND `number`.

### Q24
**Type:** How do you type a function that accepts any number of arguments?
**Answer:** Rest parameters: `function f(...args: string[]): void`

### Q25
**Type:** What is the `satisfies` operator?
```typescript
const config = { api: "/api", port: 3000 } satisfies Record<string, string | number>;
```
**Answer:** Checks that the value matches the type WITHOUT widening. The inferred type keeps literal types and specific structure, unlike `: Type` annotation.

---

## Junior (25 Questions)

### Q26
**Type:** What is the resulting type?
```typescript
function identity<T>(x: T): T { return x; }
const result = identity(42);
```
**Answer:** `42` (numeric literal type)
**Why:** Generic `T` is inferred from the argument. `42` is a literal.

### Q27
**Type:** What does `keyof` do?
```typescript
type User = { name: string; age: number };
type Keys = keyof User;
```
**Answer:** `"name" | "age"` — a union of all property name literal types.

### Q28
**Type:** Implement `Pick` from scratch.
**Answer:**
```typescript
type MyPick<T, K extends keyof T> = { [P in K]: T[P] };
```

### Q29
**Type:** What is a discriminated union?
**Answer:** A union where each member has a common literal property (the discriminant) that TypeScript uses for narrowing.
```typescript
type Shape =
  | { kind: "circle"; radius: number }
  | { kind: "rect"; width: number; height: number };
```

### Q30
**Type:** Why prefer `"a" | "b"` over `enum { A = "a", B = "b" }`?
**Answer:** String unions have zero runtime cost (erased), better inference, simpler composition, and no reverse mapping issues.

### Q31
**Type:** What is `typeof` in a type position?
```typescript
const config = { api: "/api" };
type Config = typeof config;
```
**Answer:** Extracts the TypeScript type from a JavaScript value. Here: `{ api: string }`.

### Q32
**Type:** What does `as const` do?
```typescript
const arr = [1, 2, 3] as const;
```
**Answer:** Makes the value deeply readonly with literal types: `readonly [1, 2, 3]` instead of `number[]`.

### Q33
**Type:** What is the resulting type?
```typescript
type Partial<T> = { [K in keyof T]?: T[K] };
type Result = Partial<{ a: string; b: number }>;
```
**Answer:** `{ a?: string; b?: number }`

### Q34
**Type:** What is an indexed access type?
```typescript
type User = { name: string; settings: { theme: "dark" | "light" } };
type Theme = User["settings"]["theme"];
```
**Answer:** `"dark" | "light"` — you can access nested types using bracket notation.

### Q35
**Type:** What is declaration merging?
**Answer:** Multiple declarations of the same `interface` name merge into one:
```typescript
interface Window { myGlobal: string }
// Merges with lib.dom.d.ts Window interface
```
This is why `interface` is preferred for extension points. `type` cannot merge.

### Q36
**Type:** What does `Exclude<T, U>` do?
**Answer:** Removes from `T` any member that is assignable to `U`:
```typescript
type Result = Exclude<"a" | "b" | "c", "a">; // "b" | "c"
```

### Q37
**Type:** What does `Extract<T, U>` do?
**Answer:** Keeps from `T` only members assignable to `U`:
```typescript
type Result = Extract<"a" | "b" | "c", "a" | "b">; // "a" | "b"
```

### Q38
**Type:** Write a generic function that safely accesses an object property.
**Answer:**
```typescript
function get<T, K extends keyof T>(obj: T, key: K): T[K] {
  return obj[key];
}
```

### Q39
**Type:** What is the difference between `Record<string, T>` and `{ [key: string]: T }`?
**Answer:** Functionally identical. `Record` is the utility type wrapper for index signatures. `Record<K, V>` is more flexible because `K` can be a union of literals.

### Q40
**Type:** What's wrong with this overload?
```typescript
function f(x: string): string;
function f(x: number): number;
function f(x: string | number) {
  return x;
}
```
**Answer:** The implementation return type should be `string | number`. TS uses the implementation signature internally. The overload signatures are what callers see.

### Q41
**Type:** What does `NonNullable<T>` do?
**Answer:** Removes `null` and `undefined` from `T`:
```typescript
type Result = NonNullable<string | null | undefined>; // string
```

### Q42
**Type:** What is `ReturnType<T>`?
**Answer:** Extracts the return type of a function type:
```typescript
type R = ReturnType<() => string>; // string
```

### Q43
**Type:** What is a mapped type with key remapping?
**Answer:** Using `as` to transform keys:
```typescript
type Getters<T> = {
  [K in keyof T as `get${Capitalize<string & K>}`]: () => T[K];
};
```

### Q44
**Type:** Explain `Parameters<T>`.
**Answer:** Extracts function parameter types as a tuple:
```typescript
type P = Parameters<(a: string, b: number) => void>; // [string, number]
```

### Q45
**Type:** What is `Awaited<T>`?
**Answer:** Recursively unwraps `Promise`:
```typescript
type A = Awaited<Promise<Promise<string>>>; // string
```

### Q46
**Type:** True or False: You can use `keyof` on a value.
**Answer:** False. `keyof` works on types. Use `keyof typeof value` for values.

### Q47
**Type:** What is `satisfies` vs `as const`?
**Answer:** `as const` makes values readonly + literal. `satisfies` checks against a type while preserving inference. They serve different purposes and can be combined:
```typescript
const x = { a: 1, b: 2 } as const satisfies Record<string, number>;
```

### Q48
**Type:** What is `Omit<T, K>`?
**Answer:** Creates a type with all properties of `T` except `K`:
```typescript
type Without = Omit<{ a: 1; b: 2; c: 3 }, "a" | "b">; // { c: 3 }
```

### Q49
**Type:** Scenario: You have a large `switch` on a discriminated union. How do you ensure exhaustiveness?
**Answer:** Use `never` in the default case:
```typescript
default: {
  const _exhaustive: never = value;
  throw new Error(`Unhandled: ${_exhaustive}`);
}
```
If you add a new union member and forget a case, TS errors because the new member isn't assignable to `never`.

### Q50
**Type:** What are module systems in TypeScript?
**Answer:** `module` in tsconfig controls output format. `ESNext` = ES modules (`import/export`). `CommonJS` = Node.js modules (`require/exports`). `NodeNext` = Node.js ESM detection based on `package.json` `"type"`.

---

## Senior (25 Questions)

### Q51
**Type:** What is the resulting type?
```typescript
type IsString<T> = T extends string ? true : false;
type Result = IsString<string | number>;
```
**Answer:** `boolean` (which is `true | false`)
**Why:** Distributive conditional types. `T = string | number` distributes: `IsString<string> | IsString<number>` = `true | false` = `boolean`.

### Q52
**Type:** How do you prevent distribution?
**Answer:** Wrap both sides in tuples:
```typescript
type IsString<T> = [T] extends [string] ? true : false;
type Result = IsString<string | number>; // false
```

### Q53
**Type:** What does `infer` do in this type?
```typescript
type UnwrapPromise<T> = T extends Promise<infer U> ? U : T;
```
**Answer:** `infer U` captures the inner type of `Promise`. For `Promise<string>`, `U = string`. For non-Promise types, returns `T` unchanged.

### Q54
**Type:** Write a `DeepPartial<T>` type.
**Answer:**
```typescript
type DeepPartial<T> = T extends object
  ? { [K in keyof T]?: DeepPartial<T[K]> }
  : T;
```

### Q55
**Type:** What is variance and why should you care?
**Answer:** Variance describes how subtyping of container types relates to subtyping of their contents. Covariance (output positions) preserves direction. Contravariance (input positions) reverses it. Matters for: callback typing, generic constraints, array mutability.

### Q56
**Type:** What's wrong with this code?
```typescript
const animals: Animal[] = [];
const dogs: Dog[] = [{ name: "Rex", breed: "Lab" }];
const animalsRef: Animal[] = dogs; // TS allows this!
animalsRef.push({ name: "Cat" }); // Pushes non-Dog into dogs array!
```
**Answer:** Arrays are covariant in TypeScript (unsound). A `Dog[]` assigned to `Animal[]` allows pushing non-Dog animals. Use `readonly Dog[]` to prevent this.

### Q57
**Type:** Scenario: Your React component needs to accept either `onClick` or `href`, but not both.
**Answer:**
```typescript
type ButtonProps = { label: string } & (
  | { onClick: () => void; href?: never }
  | { href: string; onClick?: never }
);
```
Using `never` for mutually exclusive props.

### Q58
**Type:** How do you type a function that takes a string path and returns the nested value?
**Answer:**
```typescript
type Get<T, Path extends string> =
  Path extends `${infer Head}.${infer Tail}`
    ? Head extends keyof T ? Get<T[Head], Tail> : never
    : Path extends keyof T ? T[Path] : never;

function get<T, P extends string>(obj: T, path: P): Get<T, P> { ... }
```

### Q59
**Type:** What is the `const` type parameter (TS 5.0)?
**Answer:**
```typescript
function create<const T>(config: T): T { return config; }
const result = create({ a: 1, b: "two" });
// result: { readonly a: 1; readonly b: "two" }
// Without `const`: { a: number; b: string }
```
`const` tells TS to infer literal/readonly types from arguments.

### Q60
**Type:** Why is `z.infer<typeof Schema>` better than writing the type manually?
**Answer:** Single source of truth. Manual types can drift from validation logic. With `z.infer`, the type is always in sync with the schema. Change the schema → type updates automatically.

### Q61
**Type:** Scenario: Your recursive type hits "Type instantiation is excessively deep." How do you fix it?
**Answer:** 1) Add explicit termination conditions. 2) Reduce depth with iterative approaches (tail-call style). 3) Cache intermediate results with helper types. 4) Simplify the type if possible.

### Q62
**Type:** What is a template literal type used for in practice?
**Answer:** Route params extraction, event naming (`on${Event}`), CSS property typing, string pattern validation. Powerful for string-based APIs.

### Q63
**Type:** How do you type a React hook that returns different shapes based on input?
**Answer:** Use overloads or conditional return types:
```typescript
function useQuery<T>(key: string, enabled: true): { data: T; isLoading: boolean };
function useQuery<T>(key: string, enabled: false): { data: undefined; isLoading: false };
```

### Q64
**Type:** What is `asserts x is T`?
**Answer:** An assertion function signature. After calling, the compiler narrows the type:
```typescript
function assertString(x: unknown): asserts x is string {
  if (typeof x !== "string") throw new Error("Not string");
}
assertString(value);
// value is now string
```

### Q65
**Type:** What's the difference between `type A = B & C` and `interface A extends B, C {}`?
**Answer:** Intersection (`&`) works with any types, resolves conflicts as `never`. Interface `extends` only works with object types, errors on conflicts. Interface extends is slightly faster for the compiler.

### Q66
**Type:** How should you type errors in TypeScript?
**Answer:** Use discriminated union `Result<T, E>` instead of throwing:
```typescript
type Result<T, E = Error> =
  | { ok: true; value: T }
  | { ok: false; error: E };
```
TypeScript can't track thrown exceptions in types. `Result` makes errors explicit and type-safe.

### Q67
**Type:** What is `isolatedModules` and why enable it?
**Answer:** Ensures each file can be transpiled independently (no cross-file type analysis). Required for SWC, esbuild, Babel. Prohibits `const enum`, namespace merging across files, re-exporting types without `type` keyword.

### Q68
**Type:** What is `verbatimModuleSyntax` (TS 5.0)?
**Answer:** Replaces `isolatedModules` + `importsNotUsedAsValues`. Requires `import type` for type-only imports. Makes import/export behavior match the module system exactly. Recommended for all new projects.

### Q69
**Type:** Write a type that extracts all keys of `T` whose values are of type `V`.
**Answer:**
```typescript
type KeysOfType<T, V> = {
  [K in keyof T]: T[K] extends V ? K : never;
}[keyof T];

type StringKeys = KeysOfType<{ a: string; b: number; c: string }, string>;
// "a" | "c"
```

### Q70
**Type:** What is a branded type?
**Answer:** Simulated nominal typing using intersection with a phantom property:
```typescript
type UserId = string & { __brand: "UserId" };
type PostId = string & { __brand: "PostId" };

function getUser(id: UserId) { ... }
getUser("123" as UserId); // ✅
getUser("123" as PostId); // ❌ Type error
```

### Q71
**Type:** Scenario: You're building a component library. Should you export your types from a barrel file?
**Answer:** Export only public API types from the barrel. Use `/** @internal */` + `stripInternal` for implementation types. Test your public API surface with `tsd`. A barrel re-export makes every exported type part of your contract.

### Q72
**Type:** How do you type `React.forwardRef` with generics?
**Answer:** You can't directly. Workaround:
```typescript
function GenericList<T>(props: ListProps<T>, ref: React.Ref<HTMLDivElement>) { ... }
export default React.forwardRef(GenericList) as <T>(
  props: ListProps<T> & React.RefAttributes<HTMLDivElement>
) => React.ReactElement;
```

### Q73
**Type:** What's the difference between `composite: true` and `references` in tsconfig?
**Answer:** `composite` makes a project buildable as a dependency (requires `declaration`, produces `.tsbuildinfo`). `references` declares dependencies on other composite projects. Together they enable incremental multi-project builds.

### Q74
**Type:** What is the `NoInfer<T>` utility type (TS 5.4)?
**Answer:** Prevents a type parameter from being used as an inference site:
```typescript
function foo<T>(a: T, b: NoInfer<T>) { ... }
foo("hello", 42); // Error: 42 not assignable to string
// Without NoInfer, T would be inferred as string | number
```

### Q75
**Type:** What is covariance in React component props?
**Answer:** Props are in **input position** (consumed by the component), so they should be **contravariant**. But TS treats method signatures as bivariant for compatibility. This can cause bugs when passing wider prop types to narrower expectations.

---

## Expert / Compiler-Level (25 Questions)

### Q76
**Type:** Why does TypeScript use structural typing instead of nominal typing?
**Answer:** JavaScript has no type declarations at runtime. Structural typing matches JS's duck-typing nature. Nominal typing would require inheritance or explicit `implements`, which doesn't match how JS developers think.

### Q77
**Type:** What happens internally when the compiler processes `T extends U ? X : Y` where T is a union?
**Answer:** The compiler iterates over each union member, checks `extends` individually, collects results, and unions them. This is the "distribution" behavior. It happens ONLY when `T` is a naked type parameter (not wrapped in a tuple/array/etc).

### Q78
**Type:** Your generic utility causes compile times to explode. What should you investigate?
**Answer:** 1) Deeply nested conditional types. 2) Unbounded recursion. 3) Large union type distribution (N members → N checks). 4) Mapped types over large objects. 5) Use `--generateTrace` to profile. 6) Check if intermediate types can be cached via type aliases.

### Q79
**Type:** What is the difference between `checker.ts` and `binder.ts` in the compiler?
**Answer:** Binder creates symbols and sets up scopes (name resolution). Checker resolves types, checks assignability, produces diagnostics. Binder runs once per file. Checker can be lazy (types resolved on demand).

### Q80
**Type:** Why can't TypeScript narrow through function calls?
```typescript
function isString(x: unknown): boolean {
  return typeof x === "string";
}
let val: unknown = "hello";
if (isString(val)) {
  val.toUpperCase(); // Error! Still unknown
}
```
**Answer:** TS doesn't track narrowing across function boundaries (control flow doesn't cross calls). Solution: use a type predicate `x is string` as return type.

### Q81
**Type:** What is the `in` and `out` variance annotation (TS 4.7)?
**Answer:**
```typescript
type Producer<out T> = { get(): T };       // covariant
type Consumer<in T> = { set(v: T): void }; // contravariant
```
These are explicit declarations of variance. Without them, TS infers variance structurally (slower). With them, the compiler can short-circuit variance checks (faster, more correct).

### Q82
**Type:** What is "declaration emit" and why does it matter?
**Answer:** Generating `.d.ts` files from `.ts` source. Critical for libraries. Challenges: inferred types may reference private types, complex expressions may produce huge declarations, internal types may leak. Use `stripInternal`, explicit return types on public functions, and test with `tsd`.

### Q83
**Type:** True or False: `const enum` values are inlined at every usage site.
**Answer:** True — tsc replaces references with literal values. But: `isolatedModules` mode disables this (SWC/esbuild can't inline across files). Prefer regular unions over `const enum`.

### Q84
**Type:** What does `--generateTrace` do?
**Answer:** Produces Chrome trace files showing where the compiler spends time. Open in `chrome://tracing`. Shows: type checking duration per file, expensive type instantiations, slow conditional types. Essential for performance debugging.

### Q85
**Type:** Why does this fail?
```typescript
type Foo<T> = T extends { a: infer U; b: infer U } ? U : never;
type Result = Foo<{ a: string; b: number }>;
```
**Answer:** `U` is inferred from both positions. Since `a: string` and `b: number`, the compiler must find a type that satisfies both. In **covariant position**, it unions: `string | number`. In **contravariant position**, it intersects: `string & number = never`. Here both are covariant (property values), so `Result = string | number`.

### Q86
**Type:** What is module resolution `bundler` vs `nodenext`?
**Answer:** `bundler` assumes a bundler (Vite, webpack) resolves imports — no file extensions required, supports `exports` field. `nodenext` follows Node.js ESM rules strictly — requires `.js` extensions, respects `"type": "module"`. Use `bundler` for apps, `nodenext` for Node.js libraries.

### Q87
**Type:** What is "isolated declarations" (TS 5.5)?
**Answer:** A mode where `.d.ts` files can be generated without running the full type checker — only local syntax information is used. Requires explicit return type annotations on exported functions. Enables parallel declaration emit by tools like SWC/esbuild.

### Q88
**Type:** Why does `never` disappear from unions but dominate intersections?
**Answer:** `never` is the bottom type (empty set). Union: `T | never = T` (adding nothing). Intersection: `T & never = never` (intersecting with nothing). Same as set theory: `A ∪ ∅ = A`, `A ∩ ∅ = ∅`.

### Q89
**Type:** How does the TypeScript language service differ from tsc?
**Answer:** tsc is a batch compiler (input → output). The language service is an incremental, interactive API used by IDEs for completions, hover info, diagnostics, refactoring. It maintains a program state and updates incrementally. `tsserver` wraps the language service in a process with a JSON protocol.

### Q90
**Type:** What is the difference between `extends` in generics vs conditional types?
**Answer:** In generics (`T extends U`): **constraint** — limits what T can be. In conditional types (`T extends U ? X : Y`): **test** — checks if T is assignable to U and branches.

### Q91
**Type:** What is a custom transformer?
**Answer:** A function that manipulates the AST between parsing and emit. Used for: compile-time code generation, macro-like behavior, custom syntax transforms. Registered via `ts.CustomTransformers`. Example: `typescript-plugin-styled-components`.

### Q92
**Type:** What happens when you use `Omit` with a union type?
```typescript
type A = { kind: "a"; x: number } | { kind: "b"; y: string };
type Result = Omit<A, "kind">;
```
**Answer:** `Omit` doesn't distribute over unions. `keyof A` is only the common keys (`"kind"`). After omitting `"kind"`, you get `{}` — losing all information. To handle union Omit, use a distributive version:
```typescript
type DistributiveOmit<T, K extends keyof any> = T extends any ? Omit<T, K> : never;
```

### Q93
**Type:** How does `satisfies` work internally?
**Answer:** It checks that the expression is assignable to the given type but returns the expression's inferred type (not the target type). Unlike annotation (`: Type`), which widens to the annotation type. This gives you type checking AND narrow inference.

### Q94
**Type:** What is the "homomorphic mapped type" optimization?
**Answer:** When a mapped type maps over `keyof T` (where T is a type parameter), TS preserves optional/readonly modifiers from the original. This is why `Partial<T>` adds `?` but doesn't lose `readonly`. Non-homomorphic mapped types (mapping over arbitrary keys) don't preserve modifiers.

### Q95
**Type:** Design question: How would you type a plugin system where plugins can extend the host's type?
**Answer:** Use module augmentation + interface merging:
```typescript
// host
interface PluginRegistry {}
function getPlugin<K extends keyof PluginRegistry>(name: K): PluginRegistry[K];

// plugin
declare module "host" {
  interface PluginRegistry {
    myPlugin: { doStuff(): void };
  }
}
```

### Q96
**Type:** Why might `ReturnType` fail on overloaded functions?
**Answer:** `ReturnType` uses the LAST overload signature. If a function has 3 overloads, only the last one's return type is extracted. This is a known limitation. Workaround: use conditional types matching specific parameter patterns.

### Q97
**Type:** What is bivariance and where does TS use it?
**Answer:** Bivariance means a type position accepts both wider AND narrower types. TS uses bivariance for method parameters (`method(x: T)` syntax) for compatibility. `strictFunctionTypes` only makes arrow/function-expression parameters contravariant, not method shorthand.

### Q98
**Type:** How does `noUncheckedIndexedAccess` change typing behavior?
**Answer:** Without it: `obj[key]` returns `T`. With it: returns `T | undefined`. Forces null checking on every dynamic access. Trade-off: safer but more verbose. Recommended for new projects.

### Q99
**Type:** What is the Go port of tsc and why was it built?
**Answer:** Announced in 2025. Rewrites the TypeScript compiler in Go for ~10x faster type checking. Motivation: tsc is single-threaded JS, and type checking is the bottleneck in large codebases. The Go port can parallelize and use more efficient data structures.

### Q100
**Type:** Architecture question: You're designing a monorepo with 50 packages. What type architecture prevents cascading type breakage?
**Answer:**
1. Define **domain types** in a shared package with explicit versioning
2. Use **interface boundaries** between packages — never export implementation types
3. Use **project references** for incremental builds
4. Use **`stripInternal`** to hide internal types from `.d.ts`
5. Test public API types with **`tsd`**
6. Use **branded types** for cross-package IDs
7. Version shared type packages independently
8. Use **schema-first** (Zod) for any types crossing runtime boundaries

---

# 9. Personalized Recommendations

## For Your Stack: React + Next.js + Astro + Monorepos

### Most Important Concepts (Prioritized)

1. **Discriminated unions** — for state modeling (loading/success/error)
2. **Generics** — for reusable hooks, components, utilities
3. **Runtime validation (Zod)** — for API boundaries, form data, env vars
4. **`satisfies`** — for config objects, route definitions
5. **Template literal types** — for route typing, event naming
6. **Branded types** — for IDs across domains
7. **`as const`** — for config objects, route arrays
8. **Conditional types + `infer`** — for library/utility authoring

### Advanced Topics to Prioritize

1. Polymorphic component typing (design systems)
2. Generic React hooks with proper inference
3. Schema-driven development (Zod everywhere)
4. tRPC or OpenAPI codegen for API safety
5. Monorepo type architecture with project references
6. Declaration file authoring (if building internal packages)
7. Variance understanding (callback typing)
8. Compile performance optimization

### Common Frontend Engineer Mistakes

1. **Not validating API responses** — "TypeScript catches it" (no, it doesn't at runtime)
2. **Over-typing React props** — typing every possible HTML attribute manually instead of using `ComponentPropsWithRef`
3. **Using `any` for event handlers** — use `React.ChangeEvent<HTMLInputElement>` etc.
4. **Not using discriminated unions for state** — using `isLoading && data` boolean soup
5. **Ignoring `as const`** — losing literal types for route definitions, action types
6. **Fighting inference** — annotating everything instead of letting generics infer
7. **Not using `satisfies`** — losing narrow types in config objects
8. **Sharing implementation types across packages** — leaky abstractions

### 60-Day Learning Plan

#### Days 1–10: Foundations Audit
- Review strict mode flags — ensure all are enabled
- Convert 3 existing components to use discriminated unions
- Add Zod validation to all API calls
- Practice: Q1–Q25

#### Days 11–20: Generics Mastery
- Build 3 generic React hooks
- Implement 5 utility types from scratch
- Understand `keyof`, `typeof`, indexed access
- Practice: Q26–Q50

#### Days 21–35: Advanced Patterns
- Implement a polymorphic `<Box as={...}>` component
- Build a type-safe event emitter
- Create a type-safe router with param extraction
- Explore `infer`, conditional types, recursive types
- Practice: Q51–Q75

#### Days 36–45: Architecture
- Set up monorepo with project references
- Create a shared types package with branded IDs
- Implement schema-driven form validation
- Design a type-safe API client layer

#### Days 46–55: Library Authoring
- Build a small utility library with proper `.d.ts` output
- Test declarations with `tsd`
- Profile compile performance with `--generateTrace`
- Practice: Q76–Q100

#### Days 56–60: Review & Strategy
- Review all brainstorm questions (Section 7)
- Write an ADR for your team's TypeScript conventions
- Create a TypeScript architecture review checklist
- Plan next learning targets from Advanced Topics (Section 11)

---

# 10. Official Documentation & Reference Links

## Beginner

- [TypeScript Handbook](https://www.typescriptlang.org/docs/handbook/)
- [TypeScript Playground](https://www.typescriptlang.org/play)
- [TypeScript in 5 Minutes](https://www.typescriptlang.org/docs/handbook/typescript-in-5-minutes.html)
- [Total TypeScript — Beginners](https://www.totaltypescript.com/tutorials/beginners-typescript)

## Intermediate

- [TypeScript Handbook — Generics](https://www.typescriptlang.org/docs/handbook/2/generics.html)
- [TypeScript Handbook — Utility Types](https://www.typescriptlang.org/docs/handbook/utility-types.html)
- [TypeScript Handbook — Narrowing](https://www.typescriptlang.org/docs/handbook/2/narrowing.html)
- [TypeScript Handbook — Mapped Types](https://www.typescriptlang.org/docs/handbook/2/mapped-types.html)
- [TypeScript Handbook — Conditional Types](https://www.typescriptlang.org/docs/handbook/2/conditional-types.html)
- [React TypeScript Cheatsheet](https://react-typescript-cheatsheet.netlify.app/)
- [Total TypeScript](https://www.totaltypescript.com/)
- [Effective TypeScript](https://effectivetypescript.com/)
- [type-fest](https://github.com/sindresorhus/type-fest) — Collection of essential TypeScript types
- [ts-pattern](https://github.com/gvergnaud/ts-pattern) — Exhaustive pattern matching

## Advanced

- [TypeScript Handbook — Template Literal Types](https://www.typescriptlang.org/docs/handbook/2/template-literal-types.html)
- [TypeScript Handbook — Variance](https://www.typescriptlang.org/docs/handbook/2/generics.html#variance-annotations)
- [TypeScript — Project References](https://www.typescriptlang.org/docs/handbook/project-references.html)
- [TypeScript — Module Resolution](https://www.typescriptlang.org/docs/handbook/modules/theory.html)
- [Zod Documentation](https://zod.dev/)
- [tRPC Documentation](https://trpc.io/docs)
- [TanStack Query](https://tanstack.com/query)
- [TypeScript Performance Wiki](https://github.com/microsoft/TypeScript/wiki/Performance)
- [tsd — Test TypeScript Declarations](https://github.com/tsdjs/tsd)
- [tsup — Bundle TypeScript libraries](https://tsup.egoist.dev/)
- [arethetypeswrong](https://arethetypeswrong.github.io/) — Check package type correctness

## Expert / Compiler Internals

- [TypeScript Compiler Source](https://github.com/microsoft/TypeScript/tree/main/src/compiler)
- [TypeScript Compiler Notes](https://github.com/microsoft/TypeScript-Compiler-Notes)
- [TypeScript Architecture Overview](https://github.com/microsoft/TypeScript/wiki/Architectural-Overview)
- [TypeScript — checker.ts](https://github.com/microsoft/TypeScript/blob/main/src/compiler/checker.ts)
- [TypeScript Design Goals](https://github.com/microsoft/TypeScript/wiki/TypeScript-Design-Goals)
- [TypeScript Performance Tracing](https://github.com/microsoft/TypeScript/wiki/Performance-Tracing)
- [TypeScript Compiler API](https://github.com/microsoft/TypeScript/wiki/Using-the-Compiler-API)
- [TypeScript Language Service API](https://github.com/microsoft/TypeScript/wiki/Using-the-Language-Service-API)
- [Basarat's TypeScript Deep Dive](https://basarat.gitbook.io/typescript/)

---

# 11. Advanced Engineering Topics

## Type-Level Programming

TypeScript's type system is Turing complete. You can compute at the type level:

```typescript
// Type-level string manipulation
type CamelCase<S extends string> =
  S extends `${infer Head}_${infer Tail}`
    ? `${Head}${Capitalize<CamelCase<Tail>>}`
    : S;

type Result = CamelCase<"hello_world_foo">; // "helloWorldFoo"

// Type-level JSON parser (extreme example — don't do this in production)
// Demonstrates that TS types can parse strings, but at severe performance cost
```

**When to use type-level programming:** Library APIs, route typing, config validation.
**When NOT to:** Application code. If it's not in a library consumed by many, keep it simple.

## Compile-Time Performance Optimization

1. **Use `interface` over `type` for object shapes** — interfaces are cached
2. **Avoid deep conditional type chains** — each level multiplies computation
3. **Use `--incremental`** — caches type information across builds
4. **Use project references** — enables parallel checking
5. **Profile with `--generateTrace`** — find the actual bottleneck
6. **Limit union size** — 100+ member unions slow down assignability checks
7. **Avoid `Omit` on unions** — use distributive version
8. **Use explicit type annotations on public APIs** — reduces inference work
9. **Enable `skipLibCheck`** — don't re-check `node_modules`

## Soundness Trade-offs

| Sound | TypeScript's Choice | Why |
|---|---|---|
| Method bivariance is unsound | Allow it | Too many callback patterns break |
| Array covariance is unsound | Allow it | Disallowing breaks common patterns |
| Index access returns `T` not `T \| undefined` | Allow (opt-in fix via flag) | Too noisy for most code |
| `any` exists | Allow it | Gradual adoption |
| Type assertions bypass checks | Allow it | Developer autonomy |

**Philosophy:** TypeScript optimizes for **practical JavaScript usage** over **mathematical type theory**. The goal is catching 95% of bugs with 5% of the effort, not proving program correctness.

## Future of TypeScript

- **Go port** — 10x faster type checking, same semantics
- **Type annotations in JS (TC39)** — types as comments, no build step
- **Isolated declarations** — parallel `.d.ts` emit without type checking
- **Improved performance** — ongoing work on checker speed
- **Better ESM support** — continued refinement of module resolution
- **Decorator metadata** — runtime type information (limited, opt-in)

---

# Summary

## Key Takeaways

1. **TypeScript is a compile-time type system that is completely erased at runtime.** Never trust types at system boundaries.
2. **Structural typing is the core philosophy.** Shapes matter, names don't.
3. **Inference is your best friend.** Annotate inputs, let outputs be inferred.
4. **Discriminated unions are THE pattern** for modeling state safely.
5. **Schema-first development (Zod)** bridges the runtime/compile-time gap.
6. **Generics + constraints** are the foundation of reusable type-safe code.
7. **Variance matters** for callbacks, arrays, and generic containers.
8. **Performance is a real concern** — profile before optimizing types.
9. **Library authors have different concerns than app developers** — declaration emit, public API stability, inference quality.
10. **The compiler is your pair programmer.** Understand its mental model and it will catch your mistakes before users do.

## Next Steps

1. Enable ALL strict flags in your projects today
2. Add Zod to every API boundary
3. Convert 5 boolean-state components to discriminated unions
4. Build one generic utility type from scratch
5. Read the TypeScript Performance wiki
6. Follow the 60-day plan in Section 9

## Advanced Topics to Continue Learning

- Custom TypeScript compiler plugins
- Type-safe distributed event systems
- Compiler API for code generation
- Building TypeScript ESLint rules
- Contributing to DefinitelyTyped
- Reading the TypeScript compiler source (`checker.ts`)
- Exploring the Go port when released
