# Rolldown Code Splitting Deep Dive — Vite 8 + React

> **Author**: Special thanks to [anIcedAntFA](https://github.com/anIcedAntFA)\
> **Context**: Phân tích chuyên sâu cách Rolldown (bundler mới của Vite 8) code splitting, so sánh với Rollup (Vite 6), giải thích build output từ project thực tế, best practices khi apply vào Vite + React + TanStack Router.\
> **Date**: 2026-03-27\
> **References**: [Rolldown Automatic Code Splitting](https://rolldown.rs/in-depth/automatic-code-splitting) | [Rolldown Manual Code Splitting](https://rolldown.rs/in-depth/manual-code-splitting) | [Rolldown Dead Code Elimination](https://rolldown.rs/in-depth/dead-code-elimination) | [TanStack Router Code Splitting](https://tanstack.com/router/latest/docs/guide/code-splitting) | [TanStack Router Automatic Code Splitting](https://tanstack.com/router/latest/docs/guide/automatic-code-splitting)

> **Related docs**: [Vite 8 Network Comparison](./vite8-network-comparison.md) — So sánh chi tiết network metrics 3 strategies trên từng route | [Network Loading Deep Dive](./network-loading-deep-dive.md) — Phân tích Vite 6 vs Vite 8

---

## Table of Contents

- [Rolldown Code Splitting Deep Dive — Vite 8 + React](#rolldown-code-splitting-deep-dive--vite-8--react)
  - [Table of Contents](#table-of-contents)
  - [1. Tổng Quan: Rolldown vs Rollup Code Splitting](#1-tổng-quan-rolldown-vs-rollup-code-splitting)
    - [1.1. Vite 6 (Rollup) — `manualChunks` function](#11-vite-6-rollup--manualchunks-function)
    - [1.2. Vite 8 (Rolldown) — `codeSplitting` option](#12-vite-8-rolldown--codesplitting-option)
    - [1.3. Bảng So Sánh Capabilities](#13-bảng-so-sánh-capabilities)
  - [2. Rolldown Automatic Code Splitting — Cách Hoạt Động](#2-rolldown-automatic-code-splitting--cách-hoạt-động)
    - [2.1. Entry Chunks — Initial vs Dynamic](#21-entry-chunks--initial-vs-dynamic)
    - [2.2. Common Chunks — Tách Module Dùng Chung](#22-common-chunks--tách-module-dùng-chung)
    - [2.3. Module Placing Order](#23-module-placing-order)
  - [3. Phân Tích Build Output — Auto Code Splitting (`codeSplitting: true`)](#3-phân-tích-build-output--auto-code-splitting-codesplitting-true)
    - [3.1. Tại Sao `about.js` Lớn 1000 KB?](#31-tại-sao-aboutjs-lớn-1000-kb)
    - [3.2. Tại Sao `request.js` Chỉ 0.07 KB? (Auto Split) / 0.4 KB (Manual Groups)](#32-tại-sao-requestjs-chỉ-007-kb-auto-split--04-kb-manual-groups)
    - [3.3. Tại Sao `clsx` Tách Thành Chunk Riêng?](#33-tại-sao-clsx-tách-thành-chunk-riêng)
    - [3.4. Tại Sao `@radix-ui` Nằm Trong `index.js` Chứ Không Phải `request.js`?](#34-tại-sao-radix-ui-nằm-trong-indexjs-chứ-không-phải-requestjs)
    - [3.5. `about.js` 1000 KB — Có Ảnh Hưởng Gì Không?](#35-aboutjs-1000-kb--có-ảnh-hưởng-gì-không)
    - [3.6. Nếu Split Three.js Ra Riêng — Trang Khác Phải Tải Dư?](#36-nếu-split-threejs-ra-riêng--trang-khác-phải-tải-dư)
  - [4. Cột `gzip` và `map` Sau Build Là Gì?](#4-cột-gzip-và-map-sau-build-là-gì)
    - [Cột 1: Raw Size (740.53 kB)](#cột-1-raw-size-74053-kb)
    - [Cột 2: gzip (230.38 kB)](#cột-2-gzip-23038-kb)
    - [Cột 3: map (3,084.88 kB)](#cột-3-map-308488-kb)
  - [5. TanStack Router — Lazy Loading \& CSS Code Splitting](#5-tanstack-router--lazy-loading--css-code-splitting)
    - [5.1. `autoCodeSplitting` Hoạt Động Thế Nào?](#51-autocodesplitting-hoạt-động-thế-nào)
    - [5.2. Có Support CSS Code Splitting Không?](#52-có-support-css-code-splitting-không)
    - [5.3. Đánh Giá Mức Tối Ưu](#53-đánh-giá-mức-tối-ưu)
    - [5.4. Advanced Config — `codeSplittingOptions` (Research & Suggestion)](#54-advanced-config--codesplittingoptions-research--suggestion)
  - [6. Manual Code Splitting — Groups Config](#6-manual-code-splitting--groups-config)
    - [6.1. Tiêu Chí Để Split Theo Group](#61-tiêu-chí-để-split-theo-group)
      - [Tiêu chí 1: Tần suất update (Cache invalidation)](#tiêu-chí-1-tần-suất-update-cache-invalidation)
      - [Tiêu chí 2: Route exclusivity (Per-route loading)](#tiêu-chí-2-route-exclusivity-per-route-loading)
      - [Tiêu chí 3: Size balance](#tiêu-chí-3-size-balance)
      - [Tiêu chí 4: Domain logic](#tiêu-chí-4-domain-logic)
      - [Recommended Group Config:](#recommended-group-config)
    - [6.2. Tại Sao Vite 6 Không Group Được?](#62-tại-sao-vite-6-không-group-được)
    - [6.3. Tại Sao Vite 8 Rolldown Không Config Split Từng Chunk?](#63-tại-sao-vite-8-rolldown-không-config-split-từng-chunk)
    - [6.4. `runtime.js` — Tại Sao Luôn Xuất Hiện?](#64-runtimejs--tại-sao-luôn-xuất-hiện)
    - [6.5. Limitations Của Manual Code Splitting](#65-limitations-của-manual-code-splitting)
      - [a. `maxSize` là target, không phải hard limit](#a-maxsize-là-target-không-phải-hard-limit)
      - [b. `includeDependenciesRecursively` (default: true)](#b-includedependenciesrecursively-default-true)
  - [7. Tree Shaking \& Code Splitting — Tương Tác Thế Nào?](#7-tree-shaking--code-splitting--tương-tác-thế-nào)
    - [7.1. Tree Shaking Vẫn Hoạt Động Bình Thường](#71-tree-shaking-vẫn-hoạt-động-bình-thường)
    - [7.2. React Hooks — Khác Page Xài Khác Hook?](#72-react-hooks--khác-page-xài-khác-hook)
    - [7.3. UI Libraries và Tree Shaking](#73-ui-libraries-và-tree-shaking)
    - [7.4. Dead Code Elimination (DCE) — Rolldown Specifics](#74-dead-code-elimination-dce--rolldown-specifics)
  - [8. So Sánh 3 Strategies Từ Benchmark Thực Tế](#8-so-sánh-3-strategies-từ-benchmark-thực-tế)
    - [8.1. Vite 8 — No Splitting (`codeSplitting: false`)](#81-vite-8--no-splitting-codesplitting-false)
    - [8.2. Vite 8 — Auto Splitting (`codeSplitting: true`)](#82-vite-8--auto-splitting-codesplitting-true)
    - [8.3. Vite 8 — Manual Groups (`codeSplitting.groups`)](#83-vite-8--manual-groups-codesplittinggroups)
    - [8.4. So Sánh Tổng Hợp](#84-so-sánh-tổng-hợp)
  - [9. Best Practices — Rolldown Code Splitting Cho Vite + React](#9-best-practices--rolldown-code-splitting-cho-vite--react)
    - [1. Bắt đầu với Auto Splitting](#1-bắt-đầu-với-auto-splitting)
    - [2. Dùng Manual Groups khi cần cache optimization](#2-dùng-manual-groups-khi-cần-cache-optimization)
    - [3. Không split quá nhỏ](#3-không-split-quá-nhỏ)
    - [4. Đặt `priority` đúng](#4-đặt-priority-đúng)
    - [5. Dùng `minSize` và `maxSize`](#5-dùng-minsize-và-maxsize)
    - [6. Kết hợp Auto + Manual](#6-kết-hợp-auto--manual)
    - [7. Enable TanStack Router `autoCodeSplitting`](#7-enable-tanstack-router-autocodesplitting)
    - [8. Measure trước khi optimize](#8-measure-trước-khi-optimize)
  - [10. Kết Luận \& Recommendations](#10-kết-luận--recommendations)
    - [Cho Project Feelfree Hiện Tại](#cho-project-feelfree-hiện-tại)
    - [Auto Splitting vs Manual Groups — Khi Nào Chọn?](#auto-splitting-vs-manual-groups--khi-nào-chọn)
    - [Summary — Câu Trả Lời Cho Mỗi Câu Hỏi](#summary--câu-trả-lời-cho-mỗi-câu-hỏi)

---

## 1. Tổng Quan: Rolldown vs Rollup Code Splitting

### 1.1. Vite 6 (Rollup) — `manualChunks` function

Vite 6 dùng Rollup làm bundler. Code splitting được control qua `manualChunks`:

```ts
// vite.config.ts — Vite 6
build: {
  rollupOptions: {
    output: {
      manualChunks(id) {
        if (id.includes('node_modules')) {
          const pkg = id.split('node_modules/')[1].split('/')[0];
          return pkg; // 1 chunk per npm package → 90+ chunks
        }
      },
    },
  },
}
```

**Hạn chế thực tế đã gặp**:

- **Không group được**: Khi thử group (ví dụ `return 'react-vendor'` cho react + react-dom + scheduler), build thành công nhưng **preview fail** (runtime errors). Lý do: Rollup's `manualChunks` xử lý circular dependencies và shared module ordering khác với Rolldown. Khi group modules có cross-dependencies phức tạp (ví dụ react-dom ↔ scheduler ↔ react-reconciler), Rollup có thể tạo ra chunk import order sai.

```ts
// ❌ Vite 6 — Build OK, preview FAIL
manualChunks(id) {
  if (/node_modules[\\/](react|react-dom|scheduler)/.test(id)) return 'react-vendor';
  if (/node_modules[\\/](three|@react-three)/.test(id)) return 'three-vendor';
  // ...
}
```

- **Chỉ có thể per-package splitting hoặc single bundle** — các strategy trung gian (grouped) gặp vấn đề runtime.

### 1.2. Vite 8 (Rolldown) — `codeSplitting` option

Vite 8 dùng Rolldown (Rust-native bundler). Code splitting có 3 modes:

```ts
// Mode 1: No splitting — single bundle
rolldownOptions: { output: { codeSplitting: false } }

// Mode 2: Automatic splitting (default, recommended starting point)
rolldownOptions: { output: { codeSplitting: true } }

// Mode 3: Manual groups (complement automatic splitting)
rolldownOptions: {
  output: {
    codeSplitting: {
      groups: [
        { name: 'react-vendor', test: /react|react-dom|scheduler/, priority: 20 },
        // ...
      ],
    },
  },
}
```

**Hạn chế thực tế đã gặp**:

- **Không config split từng chunk (per-package) được**: Rolldown `codeSplitting.groups` KHÔNG tương đương `manualChunks` function. Nó **không thể** tạo ra 90+ chunks (mỗi npm package 1 chunk) như Rollup. Groups là một cách HIGH-LEVEL để merge modules vào named chunks, không phải để fine-grained split.

- Không có `manualChunks(id)` function API — Rolldown chỉ cung cấp regex-based `test` pattern matching.

### 1.3. Bảng So Sánh Capabilities

| Feature                     | Vite 6 (Rollup)                   | Vite 8 (Rolldown)                              |
| --------------------------- | --------------------------------- | ---------------------------------------------- |
| **Per-package splitting**   | ✅ `manualChunks(id)` function    | ❌ Không có function API                       |
| **Group splitting**         | ❌ Build OK nhưng runtime fail    | ✅ `codeSplitting.groups`                      |
| **Auto splitting**          | ❌ Chỉ route-level dynamic import | ✅ `codeSplitting: true` (smart common chunks) |
| **No splitting**            | ✅ `manualChunks: undefined`      | ✅ `codeSplitting: false`                      |
| **Size constraints**        | ❌ Không có                       | ✅ `minSize`, `maxSize` per group              |
| **Priority**                | ❌ Không có                       | ✅ `priority` per group                        |
| **Runtime chunk**           | Không cần                         | ✅ Tự tạo `runtime.js` khi dùng groups         |
| **Common chunk extraction** | Chỉ qua dynamic import            | ✅ Tự động dựa trên import graph               |

---

## 2. Rolldown Automatic Code Splitting — Cách Hoạt Động

Khi `codeSplitting: true`, Rolldown tự động phân tích module dependency graph và tạo chunks theo 2 loại:

### 2.1. Entry Chunks — Initial vs Dynamic

Rolldown group các modules **connected statically** (via `import ... from` hoặc `require()`) thành 1 chunk.

```
┌─ Initial Entry (từ Vite input) ──────────────────────────────────┐
│                                                                   │
│  main.tsx → App.tsx → Provider.tsx → Router setup                 │
│         → React, React-DOM, i18next, zustand, axios, etc.         │
│         (tất cả static imports → gộp vào 1 entry chunk)           │
│                                                                   │
│  → Output: index-xO_cU7u4.js (740 KB)                            │
└───────────────────────────────────────────────────────────────────┘

┌─ Dynamic Entries (từ import()) ───────────────────────────────────┐
│                                                                   │
│  TanStack Router tạo dynamic imports cho mỗi route:               │
│                                                                   │
│  import('./about-page.tsx')    → about.js  (1002 KB)              │
│  import('./request-page.tsx')  → request.js (0.07 KB)             │
│  import('./support-page.tsx')  → support.js (30 KB)               │
│                                                                   │
└───────────────────────────────────────────────────────────────────┘
```

**Quy tắc**: Nếu module A `import` module B statically → A và B thuộc cùng chunk (trừ khi B cũng bị import bởi entry khác → xem common chunks).

### 2.2. Common Chunks — Tách Module Dùng Chung

**Đây là phần quan trọng nhất để hiểu tại sao output trông như vậy.**

Khi 1 module được **static import bởi ≥ 2 entries khác nhau**, Rolldown tách nó ra thành common chunk riêng.

**Quy tắc chi tiết**: Modules được nhóm vào cùng common chunk **CHỈ KHI** chúng được import bởi **CÙNG TẬP HỢP** entries.

```
Ví dụ từ project:

Entry A (index.js):  imports react, clsx, @radix-ui, axios, zustand
Entry B (about.js):  imports react, clsx, three.js, gsap
Entry C (support.js):imports react, clsx, axios
Entry D (request.js):imports react, clsx, @radix-ui, axios, react-hook-form

──────────────────────────────────────────────────────
Module         Imported by          Kết quả
──────────────────────────────────────────────────────
react          A, B, C, D (ALL)     → Common chunk (chung cho tất cả)
                                       → Nằm trong index.js (initial entry)
clsx           A, B, C, D (ALL)     → Common chunk riêng (clsx-CTRZi0S0.js)
                                       vì nó là module riêng biệt
three.js       B only               → Gộp vào about.js (chỉ 1 entry dùng)
gsap           B only               → Gộp vào about.js
@radix-ui      A, D                 → Nằm trong index.js (shared với request)
react-hook-form D only              → Lẽ ra trong request.js, NHƯNG...
                                       (xem phân tích bên dưới)
──────────────────────────────────────────────────────
```

**Tại sao Rolldown không gộp tất cả shared modules vào 1 common chunk?**

Vì nó sẽ vi phạm semantics. Nếu gộp `clsx` + `three.js` vào 1 chunk, thì khi load trang Request, browser phải download three.js dù không cần. Rolldown đảm bảo: **Khi execute 1 entry, CHỈ CÓ code cần thiết cho entry đó được execute.**

### 2.3. Module Placing Order

Rolldown cố gắng đặt modules theo thứ tự execution ban đầu bằng cách mô phỏng execution từ entry points. Ưu tiên:

1. **Singleton** (mỗi module chỉ xuất hiện 1 lần) — ưu tiên CAO NHẤT
2. **Execution order** — ưu tiên thứ hai

Trong một số trường hợp hiếm (circular dependencies), execution order có thể bị thay đổi. Đây là trade-off chung của tất cả ESM bundler (Rollup, esbuild đều gặp).

---

## 3. Phân Tích Build Output — Auto Code Splitting (`codeSplitting: true`)

Từ benchmark Vite 8 Test 2:

```
dist/assets/request-CHAKWbRo.js                     0.07 kB │ gzip:   0.08 kB
dist/assets/route-CMOO0Xuo.js                       0.07 kB │ gzip:   0.08 kB
dist/assets/chunk-DECur_0Z.js                       0.68 kB │ gzip:   0.41 kB
dist/assets/useParams-CgAA246l.js                   0.69 kB │ gzip:   0.40 kB
dist/assets/route-Cd9kcBmA.js                       1.43 kB │ gzip:   0.61 kB
dist/assets/path-BhrDQ6mR.js                        5.10 kB │ gzip:   1.87 kB
dist/assets/locale-link-BEvpStOf.js                 5.15 kB │ gzip:   2.39 kB
dist/assets/matchContext-DVvOBvgO.js                5.32 kB │ gzip:   2.16 kB
dist/assets/clsx-CTRZi0S0.js                        7.93 kB │ gzip:   3.35 kB   ← clsx tách riêng!
dist/assets/browser-ponyfill-D-LHU0sw.js            9.73 kB │ gzip:   3.23 kB
dist/assets/jsx-runtime-MMsH3eGn.js                 9.88 kB │ gzip:   3.64 kB
dist/assets/support-A6KJpQNm.js                    30.19 kB │ gzip:  10.44 kB
dist/assets/use-current-breakpoint-CDaGcfeb.js     32.51 kB │ gzip:  10.82 kB
dist/assets/Match-D7j3HbXP.js                      54.02 kB │ gzip:  17.77 kB
dist/assets/banner-OWzrJcHu.js                    165.19 kB │ gzip:  51.81 kB
dist/assets/index-xO_cU7u4.js                     740.53 kB │ gzip: 230.38 kB   ← main entry
dist/assets/about-Dsc5e66H.js                   1,002.92 kB │ gzip: 282.86 kB   ← about page + three.js
```

### 3.1. Tại Sao `about.js` Lớn 1000 KB?

```
about-Dsc5e66H.js (1,002.92 KB) chứa:
├── about-page component code (~49 KB)
├── three.js library (~696 KB)                ← CHỈ about page dùng Three.js
├── @react-three/fiber (~30 KB)               ← CHỈ about page dùng
├── gsap (~118 KB)                            ← CHỈ about page dùng animations
├── react-use-measure, its-fine, etc. (~10 KB)
└── about page-specific utilities
    ≈ tổng ~1000 KB
```

**Giải thích**: Rolldown auto splitting phát hiện:

- `three.js`, `@react-three/fiber`, `gsap` **CHỈ** được import bởi about page (qua dynamic `import()` từ TanStack Router)
- Không có entry nào khác import chúng
- → Rolldown gộp chúng VÀO entry chunk của about page, vì KHÔNG CẦN tách ra (không ai khác share)

Đây là behavior **đúng và hợp lý**: Nếu chỉ about page dùng Three.js, tại sao phải tạo chunk riêng? Gộp vào giảm HTTP request, giảm module evaluation overhead.

### 3.2. Tại Sao `request.js` Chỉ 0.07 KB? (Auto Split) / 0.4 KB (Manual Groups)

**Auto split** — Content thực tế của `request-CHAKWbRo.js`:

```js
import { t as e } from './index-xO_cU7u4.js';
var t = e;
export { t as component };
```

**Manual groups** — Content thực tế của `request-Clf_FOh2.js` (0.4 KB):

```js
import { a as v, c as y, ... } from './index-SChmcsXW.js';
// ... vẫn chủ yếu là import + re-export
export { ... as component };
```

**Đây chỉ là thin wrapper / re-export!** Tại sao? Vì **tất cả** dependencies của request page ĐÃ nằm trong index.js hoặc vendor chunks:

```
Request page dependency chain (đã xác minh từ source code):

1. zod → NẰM TRONG index.js vì:
   ├── __root.tsx (line 10): import { ZodError } from 'zod'    ← ROOT ROUTE!
   └── shared/config/query.config.ts (line 3): import { ZodError } from 'zod'
       └── Được import bởi app.provider.tsx → initial entry
   → zod là DIRECT dependency của initial entry, KHÔNG CHỈ request page dùng

2. react-hook-form → NẰM TRONG index.js vì:
   └── shared/components/atoms/form/form.tsx (line 6-14):
       import { Controller, FormProvider, useFormContext, useFormState }
       from 'react-hook-form'
       → File này CHỈ được import bởi request page components (5 files)
       → NHƯNG Rolldown đặt nó trong index.js vì:
          a) form.tsx là modules trong shared/ directory
          b) Transitive deps của form.tsx (react, @radix-ui/react-label,
             @radix-ui/react-slot) ĐÃ nằm trong index.js
          c) Rolldown optimize: gộp module + deps vào chunk chứa
             phần lớn dependencies đã tồn tại → giảm chunk count

3. @radix-ui/* → NẰM TRONG index.js vì:
   └── app.provider.tsx: import TooltipProvider
       → @radix-ui/react-tooltip → kéo @radix-ui core packages vào initial entry
   └── @radix-ui/react-alert-dialog share internals với react-tooltip
       → unique code chỉ ~5 KB → gộp luôn vào index.js

4. axios, zustand, i18next → Shared bởi tất cả routes → index.js
5. clsx → Common chunk riêng (shared bởi nhiều entries)

Kết quả: request page component code (~29 KB ở Vite 6 per-package)
         BỊ INLINED vào index.js bởi Rolldown
         → request chunk chỉ còn thin re-export
```

**So sánh với `support.js` (30 KB)**: Support page có content THỰC — tại sao?

```
Support page chunk content (đã xác minh từ minified output):
├── SupportBanner component + SVG icons
├── Contact section (email button)
├── Tab control (category switching) + ScrollContainer
├── Pagination component (4 SVG arrow icons + logic)
├── Article list (dùng @radix-ui/react-accordion)
├── QuickBoard API endpoints + query hooks (useBoards, useArticles)
├── Zod schemas cho board/article DTOs
└── All support-specific business logic

Tại sao support page KHÔNG bị inline vào index.js?
→ Support page có nhiều UNIQUE code không overlap với index.js:
  - Accordion component pattern (index.js không dùng)
  - QuickBoard API (endpoint riêng, schema riêng)
  - Pagination + Tab UI (không shared với routes khác)
  - 4 SVG arrow icons (inline SVG)
→ Rolldown thấy: unique code đủ lớn (~30 KB) → tạo chunk riêng hiệu quả hơn
   so với inflate index.js thêm 30 KB

Request page thì ngược lại:
  - Form components dùng shared/atoms/form (đã trong index.js)
  - @radix-ui components (đã trong index.js)
  - react-hook-form (đã bị kéo vào index.js)
  - Remaining unique code rất nhỏ → inline vào index.js
```

**Lưu ý quan trọng**: Điều này có nghĩa `index.js` (740 KB gồm 230 KB gzip) chứa:

- Code mọi route đều cần (react, router, i18n, shared components)
- Code chủ yếu request page cần (react-hook-form, Form atoms, request page components)
- Code bị pull vào vì root-level usage (zod qua `__root.tsx`, @radix-ui qua TooltipProvider)

Đây là trade-off của auto splitting: **ít HTTP requests, zero config, nhưng initial bundle có thể chứa code chưa cần thiết cho trang đầu tiên**.

### 3.3. Tại Sao `clsx` Tách Thành Chunk Riêng?

`clsx-CTRZi0S0.js` (7.93 KB) — chứa `clsx` + một số utility code nhỏ liên quan.

**Giải thích**: `clsx` được import bởi NHIỀU entries:

- `index.js` (initial entry) dùng clsx trong shared components
- `about.js` dùng clsx trong about components
- `support.js` dùng clsx
- Có thể `request` route cũng dùng

Theo quy tắc common chunks: module dùng bởi ≥ 2 entries → tách ra chunk riêng.

**Tại sao không để trong `index.js`?**

Vì `index.js` là **initial entry** (load ngay khi vào app). Nếu clsx nằm trong index.js, nó sẽ luôn được load. Nhưng Rolldown phát hiện clsx cũng cần cho dynamic entries (about, support) → tách ra common chunk:

```
Nếu clsx ở index.js:
  → Vào trang Home: load index.js (chứa clsx) ✅
  → Vào trang About: load about.js + index.js đã có clsx ✅ (nhưng lãng phí nếu about.js cũng chứa clsx)

Nếu clsx ở chunk riêng:
  → Vào trang Home: load index.js (import clsx chunk) ✅
  → Vào trang About: load about.js (import clsx chunk — đã cached!) ✅
  → Cache hiệu quả hơn khi clsx ít update
```

**Thực tế**: Chunk `clsx-CTRZi0S0.js` 7.93 KB cũng chứa thêm `class-variance-authority` (CVA) và helper code — không chỉ mỗi clsx (370 bytes). Rolldown gộp các modules có cùng "import pattern" (all được import bởi cùng tập entries) vào chung 1 common chunk.

### 3.4. Tại Sao `@radix-ui` Nằm Trong `index.js` Chứ Không Phải `request.js`?

Observation: `@radix-ui/react-alert-dialog` chỉ dùng ở page Request, nhưng khi auto split, nó nằm trong `index.js` (740 KB) chứ không nằm trong `request.js`.

**Giải thích — Dependency Chain (đã xác minh từ source code)**:

> **"Root layout" là gì?** File `src/app/routes/__root.tsx` sử dụng `createRootRouteWithContext()`. Nó render `<MainLayout>` component (bao gồm Header + Footer) bọc quanh `<Outlet />`. `__root.tsx` LUÔN được load bất kể user ở route nào — đây là root của toàn bộ route tree.

```
Dependency graph (đã verify):

main.tsx (initial entry)
  → app.provider.tsx
    ├── TooltipProvider from @radix-ui/react-tooltip    ← TRỰC TIẾP!
    │   └── Kéo @radix-ui core packages vào initial entry:
    │       @radix-ui/react-primitive, @radix-ui/react-portal,
    │       @radix-ui/react-dismissable-layer, @floating-ui/react
    ├── QueryClientProvider
    │   └── shared/config/query.config.ts
    │       └── import { ZodError } from 'zod'          ← ZOD VÀO INDEX.JS!
    └── RouterProvider → Route tree
        └── __root.tsx
            ├── import { ZodError } from 'zod'          ← ZOD LẦN 2
            ├── ResponseContractErrorPage
            │   └── import { z } from 'zod'             ← ZOD LẦN 3
            └── MainLayout → Header, Footer
```

**Tại sao @radix-ui nằm trong index.js**: `TooltipProvider` được import trong `app.provider.tsx` (bọc toàn bộ app). Đây là radix component đầu tiên vào initial entry. Vì `@radix-ui/react-tooltip` share internal modules với `@radix-ui/react-dialog`, `@radix-ui/react-alert-dialog` (cùng dùng `@radix-ui/react-primitive`, `@radix-ui/react-portal`, etc.), khi tooltip core đã nằm trong initial entry → alert-dialog chỉ thêm ~5 KB unique code → Rolldown gộp luôn vào index.js.

**Đây là behavior đúng**: TooltipProvider PHẢI load ngay từ đầu (nó bọc toàn bộ app). Radix core code theo vào là hệ quả tất yếu. Alert-dialog thêm ~5 KB nhỏ hơn nhiều so với HTTP request overhead riêng.

### 3.5. `about.js` 1000 KB — Có Ảnh Hưởng Gì Không?

**Trả lời**: Phụ thuộc vào context.

| Khía cạnh                          | Đánh giá      | Giải thích                                                                                  |
| ---------------------------------- | ------------- | ------------------------------------------------------------------------------------------- |
| **First visit to About page**      | ⚠️ Chậm hơn   | Phải download 1000 KB (282 KB gzip). Ở 4G (~5 Mbit/s) → ~450ms download                     |
| **Subsequent visits**              | ✅ Cached     | Browser cache toàn bộ 1000 KB chunk. Revisit = 0 download                                   |
| **Other pages**                    | ✅ Không load | about.js **CHỈ** load khi navigate đến `/about`. Trang Home, Request, Support không load nó |
| **Parse/Compile**                  | ⚠️ CPU cost   | 1000 KB JS cần ~100-200ms parse trên mid-range device. Nhưng chỉ 1 lần                      |
| **vs Manual split Three.js riêng** | Trade-off     | Xem phân tích bên dưới                                                                      |

**Kết luận**: 1000 KB cho about page là ACCEPTABLE vì:

1. Chỉ load khi user navigate đến about page (lazy loaded)
2. Three.js (~696 KB source, ~180 KB gzip) chiếm phần lớn — đây là size tối thiểu của 3D engine
3. Gộp vào 1 file = 1 HTTP request thay vì 3-4 requests (about + three + gsap + r3f)

> **“Lazy loaded” nghĩa là gì cụ thể?**
>
> Lazy loaded KHÔNG có nghĩa “không load” — nó có nghĩa: **không nằm trong critical rendering path của initial HTML**.
>
> ```
> Flow khi user GÕ URL /en/about trực tiếp (đây là lần đầu vào trang):
>
> 1. Browser tải index.html
> 2. Parse HTML → tìm <script src="/assets/index.js"> → tải index.js (230 KB gzip)
> 3. Parse + execute index.js → TanStack Router khởi tạo
> 4. Router detect current route = /en/about
> 5. Trigger dynamic import() cho about.js → tải about.js (282 KB gzip)
> 6. Parse + execute about.js → render About page
>
> Vậy có WATERFALL: index.js → (parse, execute, router init) → about.js
>    index.js và about.js KHÔNG download song song!
> ```
>
> **Lợi ích THỰC SỰ của lazy loading**:
>
> - User vào `/en/request` (không phải about): **about.js KHÔNG load** → tiết kiệm 282 KB
> - User vào `/en/about` trực tiếp: about.js vẫn phải load, nhưng **không block** các trang khác
> - So với no splitting (2106 KB single bundle): user trên `/en/request` tiết kiệm ~1000 KB download
>
> **Lazy ≠ "load sau"**: Nếu lần đầu vào trang IS about page, about.js load ngay sau index.js (có waterfall delay). Đây là trade-off chấp nhận được: delay ~200-400ms để đổi lấy các trang khác không phải tải 1000 KB dư thừa.

### 3.6. Nếu Split Three.js Ra Riêng — Trang Khác Phải Tải Dư?

> **⚠️ Cận trọng: Modulepreload behavior không như kỳ vọng!**

Khi dùng manual groups để tách Three.js:

```ts
codeSplitting: {
  groups: [
    { name: 'three-vendor', test: /three|@react-three/, priority: 20 },
  ],
}
```

Kết quả: `three-vendor-DW-RgaFP.js` (722 KB, 186 KB gzip) — chunk riêng.

**QUAN TRỌNG — Phát hiện từ thực tế (verified với Network DevTools trên `/en/request`)**:

HTML head khi vào `/en/request` với manual groups config:

```html
<!-- Static modulepreloads (do Vite generate trong index.html, SAME cho mọi route) -->
<link
	rel="modulepreload"
	crossorigin
	href="/assets/rolldown-runtime-Dw2cE7zH.js"
/>
<link rel="modulepreload" crossorigin href="/assets/react-vendor-DxOn3MsR.js" />
<link rel="modulepreload" crossorigin href="/assets/ui-vendor-BtwBoPwK.js" />
<link rel="modulepreload" crossorigin href="/assets/vendor-C0yVgy27.js" />
<link rel="modulepreload" crossorigin href="/assets/three-vendor-DW-RgaFP.js" />
← 3-VENDOR!
<link rel="modulepreload" crossorigin href="/assets/vendor-CwqRuW2m.js" />
<link rel="modulepreload" crossorigin href="/assets/vendor-Bz2Bo1I1.js" />
<link
	rel="modulepreload"
	crossorigin
	href="/assets/router-vendor-CKJZouPc.js"
/>
<link rel="modulepreload" crossorigin href="/assets/vendor-zTBJ1ko0.js" />
<link
	rel="modulepreload"
	crossorigin
	href="/assets/use-current-breakpoint-DIixPhi9.js"
/>

<!-- Dynamic modulepreloads (do TanStack Router inject runtime, route-specific) -->
<link
	rel="modulepreload"
	as="script"
	crossorigin
	href="/assets/route-DhEPuCHu.js"
/>
<link
	rel="modulepreload"
	as="script"
	crossorigin
	href="/assets/route-5fydGjWl.js"
/>
```

**Kết quả thực tế từ Network tab**: `three-vendor-DW-RgaFP.js` **ĐƯỢC DOWNLOAD** (186 KB, 31ms) dù đang ở trang Request! Không chỉ preload hint — browser thực sự tải file và chiếm bandwidth.

**Tại sao điều này xảy ra?**

```
SPA app (Single Page Application):
1. Vite build tạo 1 file index.html duy nhất
2. Tất cả routes (đều dùng cùng index.html (SPA)
3. Vite inject modulepreload trong index.html cho TẤT CẢ chunks
   mà entry point có thể reach (bao gồm qua dynamic imports)
4. Vì SPA chỉ có 1 HTML → modulepreload apply cho MỌI ROUTE

Phân loại modulepreload:
─────────────────────────────────────────────────────
| Loại              | Source         | Đặc điểm                        |
─────────────────────────────────────────────────────
| Static (vendor)   | Vite build     | Trong index.html, mọi route |
| Dynamic (route)   | TanStack Router| Runtime inject, route-specific |
─────────────────────────────────────────────────────

Static modulepreloads (không có as="script"):
→ Vite generate lúc build
→ Nằm CỐ ĐỊnh trong index.html
→ Apply cho MỌI route (vì SPA chỉ có 1 HTML)
→ Bao gồm TẤT CẢ vendor chunks (kể cả three-vendor)

Dynamic modulepreloads (có as="script"):
→ TanStack Router inject lúc runtime
→ Chỉ cho ROUTE HIỆN TẠI
→ Ví dụ: route-DhEPuCHu.js, about-DcjE6_ER.js
```

**Đây là HẠN CHẾ QUAN TRỌNG của manual groups + SPA**:

| So sánh                | Auto Split                           | Manual Groups                              |
| ---------------------- | ------------------------------------ | ------------------------------------------ |
| Three.js trên /request | ✅ KHÔNG load (trong about.js chunk) | ❌ ĐƯỢC preload + download (186 KB dư!)    |
| React trên /request    | Trong index.js (shared)              | Preloaded (168 KB, cần thiết)              |
| Total preload /request | ~280 KB (index + common chunks)      | ~550 KB (ALL vendor chunks)                |
| about.js trên /request | ✅ KHÔNG load (đợi navigate)         | ✅ KHÔNG load (đợi TanStack Router inject) |

**Tại sao auto split không gặp vấn đề này?**

Với auto split (`codeSplitting: true`), Three.js nằm TRONG about.js (dynamic chunk). Vite chỉ modulepreload từ entry point (index.js) → không thấy about.js trong static dependency chain → không preload about.js + three.js.

Chỉ khi TanStack Router match route `/about` → inject dynamic modulepreload cho about.js → lúc đó mới download.

**Trade-off thực sự** khi split Three.js riêng (manual groups):

|                               | Auto (Three.js trong about.js) | Manual (three-vendor riêng)                      |
| ----------------------------- | ------------------------------ | ------------------------------------------------ |
| About page lần đầu            | 1 request (1000 KB)            | 2 requests (about ~50 KB + three ~722 KB)        |
| About page revisit            | 1 cache hit                    | 2 cache hits (nhưng cả 2 đều cached)             |
| Update about page code        | Invalidate toàn bộ 1000 KB     | Chỉ invalidate about ~50 KB; three-vendor cached |
| Update Three.js               | Invalidate toàn bộ 1000 KB     | Chỉ invalidate three-vendor; about cached        |
| **Trang khác (VD: /request)** | ✅ Không load Three.js         | ⚠️ Three-vendor VẪN được preload (186 KB dư)     |
| Cache strategy                | ⚠️ Coarse (about = 1000 KB)    | ✅ Fine-grained (three-vendor cache lâu)         |

**Kết luận**: Nếu Three.js hoặc about page update THƯỜNG XUYÊN → split riêng tốt hơn (better cache). Nếu hiếm khi update → auto splitting (gộp vào about.js) đơn giản hơn.

---

## 4. Cột `gzip` và `map` Sau Build Là Gì?

Khi chạy `vite build`, output hiển thị 3 cột cho JS/CSS files:

```
dist/assets/index-xO_cU7u4.js   740.53 kB │ gzip: 230.38 kB │ map: 3,084.88 kB
                                  ↑            ↑                  ↑
                              Raw size     Gzip size          Source map size
```

### Cột 1: Raw Size (740.53 kB)

- **Ý nghĩa**: Dung lượng thực tế của file JS sau minify, TRƯỚC khi compress.
- **Đây là "Resource Size"** trong Chrome DevTools.
- **Ảnh hưởng**: Parse/compile time (CPU-bound). Browser phải parse toàn bộ 740 KB text → bytecode → execute.

### Cột 2: gzip (230.38 kB)

- **Ý nghĩa**: Dung lượng file sau khi nén bằng gzip algorithm. Đây là **Transfer Size** — dung lượng thực tế truyền qua network.
- **Tại sao nhỏ hơn nhiều**: gzip tìm patterns lặp lại trong text và thay thế bằng references. JS code có rất nhiều patterns lặp (keywords `function`, `return`, `const`, tên biến, etc.) → compression ratio ~60-70%.
- **Ảnh hưởng**: Download time (network-bound). Ở 4G (5 Mbit/s): `230 KB / 5 Mbps ≈ 368ms`.
- **Production**: Web server (Nginx, Cloudflare, etc.) tự động gzip/brotli compress. Vite chỉ **tính toán** gzip size để hiển thị — không tạo file .gz.

### Cột 3: map (3,084.88 kB)

- **Ý nghĩa**: Dung lượng file **Source Map** (`.js.map`).
- **Source Map là gì**: File mapping từ minified code → original source code. Giúp debug trong DevTools: khi có error, browser hiển thị dòng code GỐC thay vì minified code.
- **Tại sao lớn**: Source map chứa toàn bộ original source code + mapping table. Thường lớn gấp 3-10x raw file.
- **Config hiện tại**: `sourcemap: mode === 'development' ? 'inline' : 'hidden'`
  - **`'hidden'`**: File `.map` được tạo nhưng **KHÔNG** có comment `//# sourceMappingURL=...` trong JS file. Browser KHÔNG tự động load source map → **không ảnh hưởng production performance**.
  - **`'inline'`**: Source map embed trực tiếp trong JS file (cho dev mode).
- **Production impact**: **ZERO** — hidden source maps không được browser tải. Chúng chỉ hữu ích cho error tracking services (Sentry, Datadog) để map stack traces.

```
┌─ Vite Build Output ──────────────────────────────────────────┐
│                                                               │
│  dist/assets/index-xO_cU7u4.js      ← Browser downloads this │
│  dist/assets/index-xO_cU7u4.js.map  ← Browser IGNORES this   │
│                                        (no sourceMappingURL)  │
│                                                               │
│  Raw:  740 KB  → parse/compile       (CPU cost)               │
│  Gzip: 230 KB  → download            (network cost)           │
│  Map:  3084 KB → debug only          (zero runtime cost)      │
│                                                               │
└───────────────────────────────────────────────────────────────┘
```

---

## 5. TanStack Router — Lazy Loading & CSS Code Splitting

### 5.1. `autoCodeSplitting` Hoạt Động Thế Nào?

Đúng — lazy load route là feature của **TanStack Router** (không phải Vite).

```ts
// vite.config.ts
tanstackRouter({ target: 'react', autoCodeSplitting: true });
```

Khi enable `autoCodeSplitting`, TanStack Router plugin tự động:

1. **Tách route files thành 2 phần**:
   - **Critical** (load ngay): path parsing, search params, loaders, beforeLoad, context, links, scripts, styles
   - **Non-critical** (lazy load): `component`, `errorComponent`, `pendingComponent`, `notFoundComponent`

2. **Tạo dynamic `import()` cho non-critical parts**:

   ```ts
   // Generated code (simplified):
   const aboutRoute = createRoute({
   	path: '/about',
   	// Critical: load ngay
   	loader: fetchAboutData,
   	// Non-critical: lazy loaded
   	component: lazyRouteComponent(
   		() => import('./pages/about/about-page.tsx'),
   		'component',
   	),
   });
   ```

3. **Mỗi `import()` tạo 1 dynamic entry point** → Rolldown tạo chunk riêng cho nó.

**Tại sao loader KHÔNG lazy split?**

TanStack team giải thích:

- Loader đã là async boundary → nếu split, phải chờ download chunk + execute loader = double latency
- Loader thường nhỏ hơn component
- Loader là preloadable asset quan trọng nhất (preload on hover) → cần sẵn sàng không cần thêm async overhead

### 5.2. Có Support CSS Code Splitting Không?

**CÓ** — nhưng do Vite chứ không phải TanStack Router.

Vite config: `cssCodeSplit: true` (default) → mỗi JS entry chunk có CSS file riêng.

```
Build output:
dist/assets/index-w_1SL5vL.css       63.67 kB │ gzip: 10.65 kB  ← global + shared styles
dist/assets/about-sTUHqDoP.css       44.28 kB │ gzip:  6.01 kB  ← about page styles
dist/assets/support-BnvU-pbM.css     11.45 kB │ gzip:  2.41 kB  ← support page styles
dist/assets/route-DlphIMJn.css        2.11 kB │ gzip:  0.68 kB  ← route layout styles
dist/assets/banner-BJ8N_ocn.css       3.75 kB │ gzip:  1.00 kB  ← banner component styles
```

**Flow khi navigate**:

```
User vào /en/about:
1. TanStack Router detect route match
2. Inject <link rel="modulepreload" href="/assets/about-Dsc5e66H.js" />
3. Inject <link rel="stylesheet" href="/assets/about-sTUHqDoP.css" />    ← CSS!
4. Browser download cả JS và CSS song song
5. CSS render-blocking → chờ CSS xong mới render about page
6. Kết quả: KHÔNG có FOUC (Flash of Unstyled Content) ✅
```

Từ HTML head (Vite 8 auto split, view source khi ở `/en/about`):

```html
<!-- Dynamically injected bởi TanStack Router -->
<link
	rel="modulepreload"
	as="script"
	crossorigin=""
	href="/assets/about-Dsc5e66H.js"
/>
<link rel="stylesheet" crossorigin="" href="/assets/about-sTUHqDoP.css" />
```

### 5.3. Đánh Giá Mức Tối Ưu

| Khía cạnh                      | Đánh giá  | Chi tiết                                                                         |
| ------------------------------ | --------- | -------------------------------------------------------------------------------- |
| **Route-level code splitting** | ✅ Tối ưu | Chỉ load code cho route hiện tại                                                 |
| **CSS per route**              | ✅ Tối ưu | CSS riêng cho mỗi route, không load dư                                           |
| **Loader not split**           | ✅ Hợp lý | Avoid double async penalty; enable preload on hover                              |
| **Preload on hover**           | ✅ Tối ưu | TanStack Router preload route code khi user hover link → near-instant navigation |
| **SCSS modules**               | ✅ Tối ưu | `.module.scss` → scoped CSS → Vite tách theo component → gộp vào route CSS       |
| **Critical vs non-critical**   | ✅ Tối ưu | Path/search params load ngay (cho URL matching); component lazy load             |

**Kết luận**: TanStack Router + Vite `cssCodeSplit: true` + SCSS modules = **combo code splitting rất tối ưu** cho cả JS lẫn CSS. Mỗi route chỉ load đúng JS + CSS nó cần.

### 5.4. Advanced Config — `codeSplittingOptions` (Research & Suggestion)

> **Reference**: [TanStack Router Automatic Code Splitting](https://tanstack.com/router/latest/docs/guide/automatic-code-splitting)

Ngoài `autoCodeSplitting: true`, TanStack Router còn hỗ trợ fine-grained control qua `codeSplittingOptions`:

#### a. `defaultBehavior` — Thay Đổi Default Split Groupings

Default, TanStack Router split route thành 3 nhóm:

```ts
// Default behavior (không cần config):
codeSplittingOptions: {
	defaultBehavior: [
		['component'], // Group 1: lazy loaded
		['errorComponent'], // Group 2: lazy loaded
		['notFoundComponent'], // Group 3: lazy loaded
		// Còn lại (loader, beforeLoad, context, etc.) → KHÔNG split
	];
}
```

**Tuỳ chỉnh**: Gộp tất cả UI components vào 1 chunk (giảm requests):

```ts
codeSplittingOptions: {
	defaultBehavior: [
		['component', 'errorComponent', 'notFoundComponent', 'pendingComponent'],
		// → 1 lazy chunk cho TẤT CẢ UI parts thay vì 3 chunks riêng
	];
}
```

#### b. `splitBehavior` — Per-Route Programmatic Control

```ts
codeSplittingOptions: {
	splitBehavior: ({ routeId }) => {
		// About page: gộp tất cả vào 1 chunk (vì Three.js → component lớn,
		// errorComponent nhỏ → không cần tách riêng)
		if (routeId === '/$locale/about') {
			return [['component', 'errorComponent', 'notFoundComponent']];
		}
		// Request page: tách loader riêng (nếu cần preload data trước)
		if (routeId === '/$locale/request') {
			return [['component'], ['loader'], ['errorComponent']];
		}
		// Còn lại: dùng default
		return undefined;
	};
}
```

**Priority**: `splitBehavior` > `defaultBehavior`.

#### c. `codeSplitGroupings` — Per-Route Override (Trong Route File)

```ts
// src/app/routes/$locale/about.tsx
export const Route = createFileRoute('/$locale/about')({
	codeSplitGroupings: [
		['component', 'pendingComponent'], // Lazy chunk 1
		['errorComponent'], // Lazy chunk 2
	],
	component: AboutPage,
	errorComponent: AboutError,
});
```

**Priority**: `codeSplitGroupings` (per-route) > `splitBehavior` > `defaultBehavior`.

#### d. Loader Splitting — Có Nên Không?

TanStack Router **KHÔNG split loader mặc định** vì lý do performance:

```
Với loader KHÔNG split (default):
  User hover link → preload loader (đã sẵn sàng)
    → User click → execute loader ngay → fetch data
    → Time: 0ms overhead

Với loader SPLIT:
  User hover link → preload loader chunk (phải download)
    → User click → download loader chunk (nếu chưa xong) → execute → fetch data
    → Time: +50-200ms overhead (double async)
```

**Khi NÀO nên split loader**: Khi loader import heavy dependencies chỉ dùng cho route đó (ví dụ: import parser library 100 KB chỉ cho 1 route). Trong project Feelfree, loaders nhẹ (chỉ API calls) → **KHÔNG cần split loader**.

#### e. Đánh Giá Cho Project Feelfree

| Config Option             | Cần Thay Đổi? | Lý Do                                                      |
| ------------------------- | ------------- | ---------------------------------------------------------- |
| `autoCodeSplitting: true` | ✅ Giữ nguyên | Core feature, đã tối ưu                                    |
| `defaultBehavior`         | ❌ Không cần  | Default 3 groups đã hợp lý cho project này                 |
| `splitBehavior`           | ❌ Không cần  | Không có route nào cần special treatment                   |
| `codeSplitGroupings`      | ❌ Không cần  | Các routes có structure tương đồng                         |
| Loader splitting          | ❌ KHÔNG nên  | Loaders nhẹ (API calls only), split = double async penalty |

**Recommendation**: Config hiện tại (`autoCodeSplitting: true` không có thêm options) đã là **optimal** cho project Feelfree. Chỉ cần advanced config khi:

- Thêm route có heavy loader (import large parsing/processing library)
- Cần giảm số requests (gộp UI components vào 1 chunk)
- Route cụ thể cần khác biệt splitting behavior

---

## 6. Manual Code Splitting — Groups Config

### 6.1. Tiêu Chí Để Split Theo Group

Khi quyết định tạo groups, follow các tiêu chí sau (**ưu tiên từ trên xuống**):

#### Tiêu chí 1: Tần suất update (Cache invalidation)

```
Ít update (long-lived cache)          | Thường xuyên update
────────────────────────────────────────────────────────────
react, react-dom        ← 6-12 tháng  | App code      ← mỗi deploy
three.js                ← 3-6 tháng   | Config files  ← thường xuyên
@tanstack/router        ← 1-2 tháng   |
```

→ Tách code CỐ ĐỊNH ra khỏi code THAY ĐỔI THƯỜNG XUYÊN.

#### Tiêu chí 2: Route exclusivity (Per-route loading)

```
Shared (tất cả routes cần)    | Exclusive (chỉ 1 route cần)
─────────────────────────────────────────────────────────
react, react-dom, router       | three.js → only /about
i18next, axios, zustand        | gsap → only /about
clsx, CVA                      | react-hook-form → mainly /request
```

→ Code exclusive cho 1 route → để auto splitting xử lý (gộp vào route chunk). Code shared → tạo group.

#### Tiêu chí 3: Size balance

```
Mục tiêu: mỗi chunk 50-200 KB (gzip)
──────────────────────────────────────
Quá nhỏ (<10 KB):  HTTP overhead > benefit → merge
Quá lớn (>500 KB): Slow download, block connections → split
Sweet spot:         50-200 KB → parallel download efficient
```

#### Tiêu chí 4: Domain logic

```
Group theo "ecosystem":
─────────────────────────
react-vendor:  react + react-dom + scheduler   (luôn dùng cùng nhau)
three-vendor:  three + @react-three/fiber       (3D engine ecosystem)
ui-vendor:     @radix-ui + @floating-ui + cmdk  (UI component ecosystem)
router-vendor: @tanstack/router + react-query   (routing/data ecosystem)
```

#### Recommended Group Config:

```ts
codeSplitting: {
  groups: [
    // Tier 1: Ít update nhất, shared tất cả routes
    { name: 'react-vendor', test: /node_modules[\\/](react|react-dom|scheduler)/, priority: 20 },

    // Tier 2: Route-exclusive heavy dependencies
    { name: 'three-vendor', test: /node_modules[\\/](three|@react-three)/, priority: 20 },

    // Tier 3: Domain groups
    { name: 'ui-vendor', test: /node_modules[\\/](@radix-ui|@floating-ui|cmdk)/, priority: 15 },
    { name: 'router-vendor', test: /node_modules[\\/]@tanstack/, priority: 15 },

    // Tier 4: Catch-all vendor with size constraints
    { name: 'vendor', test: /node_modules/, priority: 5, minSize: 10000, maxSize: 500000 },
  ],
}
```

### 6.2. Tại Sao Vite 6 Không Group Được?

Rollup `manualChunks` function có **hạn chế structural** khi grouping:

1. **Circular dependency resolution**: Rollup resolves circular imports TRƯỚC chunk assignment. Khi group modules có circular deps (react-dom ↔ scheduler ↔ react-reconciler), chunk ordering có thể sai → runtime error.

2. **Module execution order**: Rollup assume mỗi chunk là independent unit. Grouping phá vỡ assumption này → module initialization order sai.

3. **No runtime chunk**: Rollup không tạo shared runtime chunk. Khi group tạo circular chunk imports, không có runtime để giải quyết → crash.

Cụ thể trong project: Build với group config thành công, nhưng `vite preview` fail vì `react-vendor.js` cố execute trước `scheduler` initialization → `undefined is not a function`.

**Rolldown giải quyết bằng**:

- Forcefully generate `runtime.js` chunk chứa `__esm`, `__export` helpers
- Đảm bảo runtime.js LUÔN execute trước mọi chunk khác
- Circular dependencies được handle qua lazy initialization (`__esm` wrapper)

### 6.3. Tại Sao Vite 8 Rolldown Không Config Split Từng Chunk?

Rolldown **không cung cấp `manualChunks(id)` function** vì design philosophy khác:

1. **Auto splitting đã handle common chunks**: Rolldown tự phát hiện shared modules và tách chúng. Không cần developer micromanage.

2. **Per-package splitting = anti-pattern**: 90+ chunks với 0.03-0.3 KB mỗi cái là BAD cho performance (xem benchmark Vite 6 Test 3). HTTP overhead >> content.

3. **Groups là high-level control**: Groups cho phép developer GROUP modules theo domain logic, không phải SPLIT từng module ra. Đây là mức abstraction phù hợp hơn.

4. **`test` là regex, không phải function**: Performance — regex match nhanh hơn function call cho mỗi module. Nhưng giới hạn flexibility.

**Nếu thực sự cần per-package splitting** (không recommend):

- Rolldown hiện không support
- Workaround: Tạo 1 group per package (verbose, không scalable):
  ```ts
  groups: [
  	{ name: 'react', test: /node_modules[\\/]react[\\/]/, priority: 10 },
  	{
  		name: 'react-dom',
  		test: /node_modules[\\/]react-dom[\\/]/,
  		priority: 10,
  	},
  	{ name: 'three', test: /node_modules[\\/]three[\\/]/, priority: 10 },
  	// ... 80+ dòng nữa → TERRIBLE DX
  ];
  ```

### 6.4. `runtime.js` — Tại Sao Luôn Xuất Hiện?

Khi dùng manual `codeSplitting.groups`, Rolldown LUÔN tạo `rolldown-runtime-*.js` (~0.68 KB):

```
dist/assets/rolldown-runtime-Dw2cE7zH.js   0.68 kB │ gzip: 0.41 kB
```

**Chứa gì**: Helper functions `__esm()`, `__export()`, module registry.

**Tại sao cần**: Manual groups có thể tạo circular chunk imports:

- `react-vendor.js` import từ `vendor.js`
- `vendor.js` import từ `react-vendor.js`
- → Ai execute trước? Runtime.js giải quyết: nó execute ĐẦU TIÊN, register helpers, sau đó các chunks có thể import helpers từ runtime → không circular.

**Impact**: 0.68 KB (0.41 KB gzip) — negligible. Và nó cache indefinitely (rất ít khi thay đổi).

### 6.5. Limitations Của Manual Code Splitting

#### a. `maxSize` là target, không phải hard limit

```
{ name: 'vendor', test: /node_modules/, maxSize: 500000 }
```

Chunk có thể > 500 KB nếu:

- 1 module đơn lẻ > 500 KB (ví dụ three.js ~696 KB → không thể split 1 module ra 2 chunks)
- Split sẽ tạo chunks < `minSize` → Rolldown chọn giữ nguyên

#### b. `includeDependenciesRecursively` (default: true)

Khi group capture 1 module, Rolldown cũng capture **tất cả dependencies** của nó. Ví dụ:

- Group `three-vendor` match `three.js`
- `three.js` import `stats.js` (internal utility)
- `stats.js` cũng bị kéo vào `three-vendor` chunk, DÙ KHÔNG match regex

→ Chunk có thể chứa modules không match `test` pattern.

Nếu muốn disable: `includeDependenciesRecursively: false` — nhưng có thể gây execution order issues.

---

## 7. Tree Shaking & Code Splitting — Tương Tác Thế Nào?

### 7.1. Tree Shaking Vẫn Hoạt Động Bình Thường

**Tree shaking (Dead Code Elimination) và Code Splitting là 2 processes INDEPENDENT**:

```
Source code → [Tree Shaking] → Used code only → [Code Splitting] → Chunks
```

1. **Tree Shaking** chạy TRƯỚC: Rolldown/Rollup phân tích static imports và loại bỏ unused exports.
2. **Code Splitting** chạy SAU: Chỉ split code ĐÃ tree-shaken.

→ Code splitting KHÔNG ảnh hưởng đến tree shaking. Tree shaking KHÔNG bị disable khi split chunks.

### 7.2. React Hooks — Khác Page Xài Khác Hook?

**Question**: Page A dùng `useState` + `useEffect`, Page B dùng `useRef` + `useMemo` — tree shaking có loại bỏ hooks không dùng ở mỗi page?

**Trả lời**: **KHÔNG** — nhưng không phải vì code splitting. Lý do:

```ts
// react/index.js (simplified)
export { useState, useEffect, useRef, useMemo, useCallback, ... }
```

React export TẤT CẢ hooks từ 1 entry point. Khi bất kỳ page nào import `react`:

```ts
import { useState } from 'react';
```

Rolldown thấy `react` package được import → include toàn bộ `react/index.js` → TẤT CẢ hooks đều included vì React internal structure không tree-shakeable ở level individual hooks:

```
Lý do React không tree-shake riêng từng hook:
1. React hooks share internal state (fiber, dispatcher)
2. react package là 1 CJS module converted to ESM → bundler phải include toàn bộ
3. Hooks registered vào shared dispatcher → loại bỏ 1 hook = break others
```

**NHƯNG** tree shaking VẪN hoạt động ở level ĐỦ LỚN:

- Nếu page KHÔNG import `react` → react code KHÔNG load cho page đó
- Nếu library export nhiều components nhưng bạn chỉ import 1 → tree shaking bỏ phần còn lại
- `lucide-react` export 1000+ icons — import 1 icon → tree shaking loại bỏ 999+ icons

### 7.3. UI Libraries và Tree Shaking

**Question**: `@radix-ui/react-alert-dialog` chỉ dùng ở Request page, sao nằm trong `index.js`?

**Phân tích tree shaking + code splitting (đã xác minh từ source code)**:

```
Step 1: Tree Shaking
─────────────────────
@radix-ui/react-alert-dialog: export { Root, Trigger, Content, ... }
Request page: import { AlertDialog } from '@radix-ui/react-alert-dialog'
→ Tree shaking giữ AlertDialog, loại bỏ unused exports ✅ (nếu library hỗ trợ)

Step 2: Code Splitting — Tại sao vẫn ở index.js?
──────────────────────────────────────────────────
Root cause: TooltipProvider trong app.provider.tsx (xem Section 3.4)

app.provider.tsx
  └── import { TooltipProvider } from '@radix-ui/react-tooltip'
      └── @radix-ui/react-tooltip internal deps:
          ├── @radix-ui/react-primitive
          ├── @radix-ui/react-portal
          ├── @radix-ui/react-dismissable-layer
          └── @floating-ui/react

@radix-ui/react-alert-dialog cũng share CÙNG internal deps:
  ├── @radix-ui/react-primitive      ← ĐÃ NẰM TRONG index.js (via tooltip)
  ├── @radix-ui/react-portal         ← ĐÃ NẰM TRONG index.js (via tooltip)
  └── @radix-ui/react-dismissable-layer ← ĐÃ NẰM TRONG index.js (via tooltip)

→ AlertDialog unique code chỉ ~3-5 KB (phần lớn deps đã trong index.js)
→ Rolldown quyết định: gộp vào index.js thay vì tạo chunk tiny 3 KB
```

> **Lưu ý**: Trước đây doc ghi nhầm là `@radix-ui/react-dialog` trong root layout. Thực tế, `TooltipProvider` mới là radix component đầu tiên vào initial entry (qua `app.provider.tsx`). Xem [Section 3.4](#34-tại-sao-radix-ui-nằm-trong-indexjs-chứ-không-phải-requestjs) để biết chi tiết dependency chain đã verify.

**Tree shaking VẪN hoạt động**: Nếu bạn có package `heavy-lib` export 50 functions nhưng chỉ dùng 2 → tree shaking loại 48 functions khỏi bundle. Code splitting sau đó quyết định 2 functions đó nằm ở chunk nào.

**Ví dụ thực tế từ project**:

```
lucide-react (1000+ icons):
  → Project import ~20 icons
  → Tree shaking loại ~980 icons
  → lucide-react-SfC4zUVu.js chỉ 0.03 KB (chỉ re-exports)
  → Actual icon code nằm trong index.js (shared component icons)

zod (100+ validators):
  → Project import schema functions (ZodError, z.string, z.enum, etc.)
  → Tree shaking giữ dùng, loại không dùng
  → Nhưng zod core không split được nhiều (tightly coupled)
  → Nằm trong index.js vì __root.tsx + query.config.ts import trực tiếp
    (xem Section 3.2 cho verified dependency chain)
```

### 7.4. Dead Code Elimination (DCE) — Rolldown Specifics

> **Reference**: [Rolldown Dead Code Elimination](https://rolldown.rs/in-depth/dead-code-elimination) | [Why Bundlers](https://rolldown.rs/in-depth/why-bundlers)

**Tại sao DCE quan trọng trong code splitting?**

Tree shaking và DCE chạy TRƯỚC code splitting. Nghĩa là code splitting chỉ tách **code đã được loại bỏ dead code**. Nếu DCE không hoạt động tốt → chunks sẽ lớn hơn cần thiết.

#### 7.4.1. Annotations — `@__PURE__` và `@__NO_SIDE_EFFECTS__`

Rolldown (giống Rollup/esbuild) dùng annotations để biết function call nào **an toàn để loại bỏ**:

**`@__PURE__`** — Đánh dấu một **call expression** không có side effects:

```js
// Input
const result = /*@__PURE__*/ createContext(defaultValue);

// Nếu `result` không được dùng → Rolldown loại bỏ cả dòng
// Nếu KHÔNG có @__PURE__ → Rolldown giữ lại (vì không biết createContext có side effect không)
```

**Tại sao cần?** Rolldown KHÔNG THỂ biết function có side effect hay không bằng static analysis. `createContext()` có thể modify global state bên trong. `@__PURE__` nói với bundler: "trust me, nó safe to remove."

**`@__NO_SIDE_EFFECTS__`** — Đánh dấu nguyên **function declaration**:

```js
/*@__NO_SIDE_EFFECTS__*/
function createComponent(options) {
	return { ...options, __type: 'component' };
}

// MỌI call site của createComponent đều tự động được coi là @__PURE__
// → Nếu result không dùng → Rolldown loại bỏ
```

**Trong project Feelfree**: Các radix-ui components, React hooks, và library exports đã có sẵn `@__PURE__` annotations (transpiler/library author thêm). Đây là lý do tree shaking hoạt động tốt với `lucide-react`, `clsx`, `class-variance-authority`.

#### 7.4.2. `sideEffects` trong `package.json`

```json
// node_modules/lucide-react/package.json
{
	"sideEffects": false
}
```

Khi `sideEffects: false`:

- Rolldown biết TOÀN BỘ files trong package **không có side effects ở module level**
- Nếu import 1 icon từ `lucide-react` → Rolldown loại bỏ 999+ icons khác
- Nếu KHÔNG có `sideEffects: false` → Rolldown phải giữ mọi file vì `import` statement có thể trigger side effects (CSS injection, polyfill, global mutation)

**Ví dụ ngược — `sideEffects: ["*.css"]`**:

```json
// node_modules/@radix-ui/react-dialog/package.json
{
	"sideEffects": ["*.css"]
}
```

→ Rolldown loại bỏ unused JS exports nhưng GIỮA tất cả `.css` imports (vì CSS import = side effect — inject styles vào DOM).

#### 7.4.3. Treeshake Options trong Rolldown

Rolldown cung cấp các option để fine-tune DCE behavior:

| Option                               | Default | Ý nghĩa                                                  |
| ------------------------------------ | ------- | -------------------------------------------------------- |
| `treeshake.moduleSideEffects`        | `true`  | Respect `sideEffects` field trong package.json           |
| `treeshake.unknownGlobalSideEffects` | `true`  | Giữ code modify unknown globals (window, document)       |
| `treeshake.propertyReadSideEffects`  | `true`  | Giả định property access có thể có side effects (getter) |

```ts
// vite.config.ts — Aggressive DCE (KHÔNG recommend cho production)
rolldownOptions: {
  treeshake: {
    unknownGlobalSideEffects: false,    // Dangerous: có thể loại polyfills
    propertyReadSideEffects: false,     // Dangerous: có thể break getter logic
  },
}
```

> **⚠️ Cho project Feelfree**: KHÔNG cần thay đổi treeshake options. Default values đã optimal. Thay đổi aggressive options có thể break runtime behavior (đặc biệt với React, radix-ui polyfills, i18next side effects).

#### 7.4.4. Plugin Hook Priority

Khi có conflict giữa annotations và config:

```
Priority (cao → thấp):
1. Plugin hooks (transform, resolveId) — có thể override mọi thứ
2. treeshake options trong config
3. sideEffects trong package.json
4. @__PURE__ / @__NO_SIDE_EFFECTS__ annotations trong code
```

**Ý nghĩa thực tế**: Nếu một Vite plugin mark module là có side effects (qua `moduleSideEffects` hook), cả `@__PURE__` annotations lẫn `sideEffects: false` trong package.json đều bị **override**.

---

## 8. So Sánh 3 Strategies Từ Benchmark Thực Tế

### 8.1. Vite 8 — No Splitting (`codeSplitting: false`)

```
Config: rolldownOptions: { output: { codeSplitting: false } }

Output:
  dist/assets/index-KlFI_U-l.js       2,106.34 kB │ gzip: 632.26 kB
  dist/assets/index-lb2CWeDw.css         123.84 kB │ gzip:  18.11 kB
  (+ images/fonts)

Build time: 2.22s
JS files: 1
CSS files: 1
```

| Pros                       | Cons                                             |
| -------------------------- | ------------------------------------------------ |
| ✅ 1 request cho tất cả JS | ❌ 632 KB gzip = ~1s download trên 4G            |
| ✅ Best gzip ratio         | ❌ Parse 2106 KB JS = ~200-400ms trên mobile     |
| ✅ Zero HTTP overhead      | ❌ User load Three.js dù ở trang Request         |
|                            | ❌ BẤT KỲ thay đổi nào invalidate TOÀN BỘ cache  |
|                            | ❌ Không lazy route loading → no benefit cho SPA |

### 8.2. Vite 8 — Auto Splitting (`codeSplitting: true`)

```
Config: rolldownOptions: { output: { codeSplitting: true } }

Output:
  index-xO_cU7u4.js       740.53 kB │ gzip: 230.38 kB  ← shared + react + radix + i18n
  about-Dsc5e66H.js     1,002.92 kB │ gzip: 282.86 kB  ← about + three.js + gsap
  banner-OWzrJcHu.js      165.19 kB │ gzip:  51.81 kB  ← banner component (shared)
  Match-D7j3HbXP.js        54.02 kB │ gzip:  17.77 kB  ← router matching
  use-current-breakpoint   32.51 kB │ gzip:  10.82 kB  ← responsive utility
  support-A6KJpQNm.js      30.19 kB │ gzip:  10.44 kB  ← support page
  clsx-CTRZi0S0.js          7.93 kB │ gzip:   3.35 kB  ← clsx (common chunk)
  ... (more small chunks)
  request-CHAKWbRo.js        0.07 kB ← re-export only!

Build time: 1.61s
JS files: ~17
CSS files: 5
```

| Pros                           | Cons                                                        |
| ------------------------------ | ----------------------------------------------------------- |
| ✅ Route-level lazy loading    | ⚠️ index.js vẫn lớn (230 KB gzip) vì chứa nhiều shared code |
| ✅ Three.js chỉ load cho about | ⚠️ about.js lớn (282 KB gzip) — nhưng OK vì lazy loaded     |
| ✅ Smart common chunks (clsx)  | ⚠️ Một số chunks tiny (0.07 KB) — overhead                  |
| ✅ CSS per-route split         | ⚠️ Ít control qua grouping — phụ thuộc bundler heuristic    |
| ✅ Đơn giản, zero config       |                                                             |

### 8.3. Vite 8 — Manual Groups (`codeSplitting.groups`)

```
Config: codeSplitting.groups (react-vendor, three-vendor, ui-vendor, router-vendor, vendor)

Output:
  react-vendor     541.60 kB │ gzip: 169.52 kB  ← react ecosystem
  three-vendor     722.01 kB │ gzip: 186.49 kB  ← three.js ecosystem
  router-vendor    122.88 kB │ gzip:  37.43 kB  ← tanstack
  index            125.33 kB │ gzip:  40.63 kB  ← app code
  vendor-D4BccWBG  115.69 kB │ gzip:  45.47 kB  ← gsap, etc.
  vendor-CwqRuW2m  103.67 kB │ gzip:  25.28 kB  ← i18n, etc.
  vendor-Bz2Bo1I1  102.17 kB │ gzip:  35.25 kB  ← misc vendor
  ui-vendor         90.74 kB │ gzip:  29.54 kB  ← radix/floating
  vendor-zTBJ1ko0   69.29 kB │ gzip:  20.92 kB  ← other vendor
  about             49.70 kB │ gzip:  15.54 kB  ← about page code only
  support           13.88 kB │ gzip:   4.93 kB  ← support page
  vendor-C0yVgy27    9.30 kB │ gzip:   3.42 kB  ← small vendor
  runtime            0.68 kB │ gzip:   0.41 kB  ← runtime helpers
  ... (route chunks)

Build time: 1.28s
JS files: ~20
CSS files: 4
```

| Pros                                            | Cons                                        |
| ----------------------------------------------- | ------------------------------------------- |
| ✅ Balanced chunk sizes (20-186 KB gzip)        | ⚠️ Cần maintenance khi thêm deps            |
| ✅ Excellent cache strategy (react = 6+ months) | ⚠️ Config verbose                           |
| ✅ Three.js lazy (chỉ load cho about)           | ⚠️ Runtime.js overhead (0.4 KB, negligible) |
| ✅ about.js nhỏ (15 KB) vs auto (282 KB)        | ⚠️ Nhiều requests hơn auto                  |
| ✅ Control grouping rõ ràng                     |                                             |
| ✅ Build nhanh nhất (1.28s)                     |                                             |

### 8.4. So Sánh Tổng Hợp

| Metric                       | No Split           | Auto Split                       | Manual Groups                |
| ---------------------------- | ------------------ | -------------------------------- | ---------------------------- |
| **Build time**               | 2.22s              | 1.61s                            | 1.28s                        |
| **JS requests**              | 1                  | ~17                              | ~20                          |
| **Largest chunk (gzip)**     | 632 KB             | 282 KB (about)                   | 186 KB (three-vendor)        |
| **Initial load (Home)**      | 632 KB             | ~280 KB¹                         | ~340 KB²                     |
| **About page load**          | 0 (đã load)        | 282 KB lazy                      | ~250 KB lazy³                |
| **Cache on app code change** | ❌ ALL invalidated | ⚠️ index.js invalidated (230 KB) | ✅ Chỉ index.js (40 KB)      |
| **Cache on React update**    | ❌ ALL invalidated | ⚠️ index.js invalidated (230 KB) | ✅ Chỉ react-vendor (169 KB) |
| **Route CSS split**          | ❌ 1 file          | ✅ Per-route                     | ✅ Per-route                 |
| **Complexity**               | Minimal            | Minimal                          | Medium                       |

> ¹ Auto split home: index.js (230 KB) + common chunks (~50 KB)
> ² Manual groups home: react-vendor (169 KB) + router-vendor (37 KB) + ui-vendor (29 KB) + index.js (40 KB) + vendors (~65 KB)
> ³ Manual about lazy: about.js (15 KB) + three-vendor (186 KB) + vendor-D4BccWBG (45 KB, gsap)

---

## 9. Best Practices — Rolldown Code Splitting Cho Vite + React

### 1. Bắt đầu với Auto Splitting

```ts
// Recommendation cho hầu hết projects
rolldownOptions: {
  output: {
    codeSplitting: true,
  },
}
```

Auto splitting với TanStack Router `autoCodeSplitting: true` đã xử lý tốt route-level splitting. Chỉ chuyển sang manual groups khi cần optimize cache strategy.

### 2. Dùng Manual Groups khi cần cache optimization

Nên dùng groups khi:

- Deploy thường xuyên (daily/weekly) → cần vendor cache stability
- Dependencies lớn (three.js, monaco-editor) chỉ dùng ở 1-2 routes
- Team lớn, nhiều người contribute → app code change thường xuyên nhưng vendor ít đổi

### 3. Không split quá nhỏ

```
❌ Bad: 90+ chunks (per-package)
  → HTTP overhead > benefit
  → modulepreload bloated HTML
  → V8 parse overhead per module

✅ Good: 15-25 chunks (grouped + auto)
  → Balance requests vs caching
  → Manageable modulepreload count
  → Reasonable parse overhead
```

### 4. Đặt `priority` đúng

```ts
groups: [
	// Cao nhất: frameworks core (match đầu tiên, tránh bị catch-all)
	{ name: 'react-vendor', test: /react|react-dom/, priority: 20 },

	// Cao: domain-specific large libs
	{ name: 'three-vendor', test: /three|@react-three/, priority: 20 },

	// Trung: UI/Router frameworks
	{ name: 'ui-vendor', test: /@radix-ui|@floating-ui/, priority: 15 },

	// Thấp nhất: catch-all
	{ name: 'vendor', test: /node_modules/, priority: 5 },
];
```

Không có `priority` → modules match nhiều patterns sẽ ambiguous.

### 5. Dùng `minSize` và `maxSize`

```ts
{ name: 'vendor', test: /node_modules/, priority: 5, minSize: 10000, maxSize: 500000 }
//                                                    ↑ avoid tiny chunks   ↑ avoid huge chunks
```

- `minSize: 10000` (10 KB) — prevent chunks < 10 KB (HTTP overhead not worth it)
- `maxSize: 500000` (500 KB) — Rolldown sẽ CỐ GẮNG split nếu chunk > 500 KB (nhưng không guarantee)

### 6. Kết hợp Auto + Manual

Manual groups và auto splitting **KHÔNG contradictory**: Module match group → vào group chunk. Module KHÔNG match → auto splitting handle (tạo entry chunks và common chunks).

```
Module flow:
  node_modules/react → match 'react-vendor' group → react-vendor chunk
  node_modules/three → match 'three-vendor' group → three-vendor chunk
  node_modules/tiny-lib → KHÔNG match any group → auto: gộp vào nearest entry chunk
  src/pages/about     → KHÔNG match any group → auto: dynamic entry chunk (about.js)
  src/shared/utils    → KHÔNG match any group → auto: gộp vào initial entry (index.js)
```

### 7. Enable TanStack Router `autoCodeSplitting`

```ts
tanstackRouter({ target: 'react', autoCodeSplitting: true });
```

Đây là MUST-HAVE. Nó tạo dynamic `import()` boundaries cho mỗi route → Rolldown tạo per-route chunks → lazy loading hoạt động.

Không có `autoCodeSplitting`, tất cả route components gộp vào initial bundle → user load 100% code ngay lần đầu.

### 8. Measure trước khi optimize

```bash
# Build và check output
bun run build

# Visual analysis
npx rollup-plugin-visualizer # hoặc dùng stats.html

# Preview + DevTools Network tab
bun run preview
# → Throttle 4G → check waterfall
```

Tối ưu dựa trên DATA, không phải gut feeling. 1000 KB about.js NGHE lớn nhưng thực tế acceptable vì lazy loaded.

---

## 10. Kết Luận & Recommendations

### Cho Project Feelfree Hiện Tại

| Recommendation                                                           | Ưu Tiên  | Lý Do                                                                           |
| ------------------------------------------------------------------------ | -------- | ------------------------------------------------------------------------------- |
| **Giữ `codeSplitting: true`** (auto) hoặc chuyển sang **manual groups**  | High     | Auto splitting đã tốt. Manual groups tốt hơn cho cache strategy trên production |
| **Giữ TanStack Router `autoCodeSplitting: true`**                        | Critical | Route-level splitting + CSS split = core optimization                           |
| **Chấp nhận about.js 1000 KB** (auto) hoặc split Three.js riêng (groups) | Medium   | Trade-off: 1 request vs better cache. Production cả 2 đều OK                    |
| **Không cố per-package splitting trên Vite 8**                           | N/A      | Rolldown không hỗ trợ; cũng không nên vì 90+ chunks là anti-pattern             |
| **Không cố group splitting trên Vite 6**                                 | N/A      | Rollup runtime issues; nên migrate Vite 8                                       |

### Auto Splitting vs Manual Groups — Khi Nào Chọn?

```
Auto Splitting (codeSplitting: true):
  ✅ Khi project nhỏ-trung (< 50 dependencies)
  ✅ Khi deploy ít (monthly)
  ✅ Khi muốn zero config
  ✅ Khi chấp nhận index.js lớn (230 KB gzip)

Manual Groups:
  ✅ Khi project lớn (50+ dependencies)
  ✅ Khi deploy thường xuyên (daily/weekly)
  ✅ Khi cần fine-grained cache control
  ✅ Khi có heavy exclusive dependencies (three.js, monaco)
  ✅ Khi index.js cần nhỏ (40 KB thay vì 230 KB)
```

### Summary — Câu Trả Lời Cho Mỗi Câu Hỏi

| Câu hỏi                             | Trả lời ngắn                                                                                                                                                      |
| ----------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Vite 6 không group được?            | Đúng — Rollup `manualChunks` group fail ở runtime do circular deps                                                                                                |
| Vite 8 không per-package split?     | Đúng — Rolldown chỉ có regex groups, không có function API                                                                                                        |
| about.js 1000 KB có sao không?      | Chấp nhận được — lazy loaded, Three.js chiếm ~700 KB là unavoidable                                                                                               |
| Trang khác phải tải Three.js dư?    | **Auto**: KHÔNG — Three.js trong about.js (lazy). **Manual groups**: CÓ preload dư 186 KB (SPA modulepreload limitation, xem Section 3.6)                         |
| clsx tách riêng tại sao?            | Vì nhiều entries import → Rolldown tạo common chunk                                                                                                               |
| gzip và map là gì?                  | gzip = compressed transfer size; map = source map cho debugging                                                                                                   |
| Lazy load route là TanStack Router? | ĐÚNG — `autoCodeSplitting: true` tạo dynamic import per route                                                                                                     |
| TanStack Router split CSS?          | CÓ — Vite `cssCodeSplit: true` + route lazy loading = CSS per route                                                                                               |
| TanStack Router cần config thêm?    | KHÔNG — `autoCodeSplitting: true` đã optimal. Advanced options (`codeSplittingOptions`) chỉ cần khi có specific requirements (xem Section 5.4)                    |
| Split theo group tiêu chí nào?      | Update frequency → Route exclusivity → Size balance → Domain logic                                                                                                |
| Tree shaking bị ảnh hưởng?          | KHÔNG — tree shaking + DCE chạy trước code splitting, independent (xem Section 7.4)                                                                               |
| @radix-ui sao ở index.js?           | TooltipProvider trong app.provider.tsx kéo radix core vào initial entry (KHÔNG phải Dialog trong root layout — xem Section 3.4)                                   |
| request.js sao chỉ 0.07 KB?         | Dependencies đã trong index.js (zod qua \_\_root.tsx + query.config.ts, RHF qua form.tsx inlined, radix qua TooltipProvider) → chỉ là re-export (xem Section 3.2) |