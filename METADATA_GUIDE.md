# Astro Blog Metadata Rules

Generate frontmatter for all `.md` and `.mdx` files.

Skip:

```txt
README.md
BRAIN_STORM.md
```

Also ignore:

```txt
.git/
node_modules/
dist/
.astro/
.*
```

---

# Frontmatter Template

```yaml
---
title: Title
description: Description

slug: blog-slug

# Media
thumbnail: ../assets/blog-slug.webp

# Publishing
publishedDate: '2025-05-01'
modifiedDate: '2025-05-01'
draft: true
featured: false

# Taxonomy
tags:
  - react

categories:
  - frontend

series: React Basics
seriesOrder: 1

# SEO
seo:
  title: SEO Title
  description: SEO Description
  canonical: https://feel-free.com/blogs/blog-slug
  keywords:
    - react
  image: ../assets/blog-slug.webp

# Author
author: lazarus2019

# Localization
lang: en

# Content relations
relatedPosts:
  - another-post
---
```

Optional fields:

```yaml
series:
seriesOrder:
contributors:
relatedPosts:
```

Do not generate empty values.

---

# Category Rules

Category = first directory after `docs/`

Example:

```txt
docs/frontend/react-hooks.md
```

```yaml
categories:
  - frontend
```

---

# Series Rules

Treat as series when:

## Filename starts with number

```txt
docs/react/1-hooks.md
```

```yaml
series: React
seriesOrder: 1
```

---

## Nested series directory

```txt
docs/frontend/react-performance/1-memoization.md
```

```yaml
series: React Performance
seriesOrder: 1
```

Series name = nearest parent directory.

Convert directory names to title case:

| Directory | Series |
|---|---|
| `react-performance` | `React Performance` |
| `series-1` | `Series 1` |

---

# Slug Rules

Generate from filename:

- lowercase
- kebab-case
- remove extension
- remove numeric prefix

Examples:

| Filename | Slug |
|---|---|
| `1-react-hooks.md` | `react-hooks` |
| `Advanced Hooks.md` | `advanced-hooks` |

---

# Title Rules

Priority:

1. first H1 heading
2. filename

Cleanup:

- remove numeric prefix
- convert kebab/snake case to title case

---

# Description Rules

Generate concise SEO summary:

- 120–160 chars
- summarize article intent
- avoid generic text

---

# Thumbnail Rules

Thumbnail filename MUST equal slug.

Preferred format:

```txt
.webp
```

Lookup order:

1. `<slug>.webp`
2. `thumbnail.webp`
3. first `.webp` in nearest `assets/`

Example:

```txt
docs/assets/react-hooks.webp
docs/frontend/react-hooks.md
```

```yaml
thumbnail: ../assets/react-hooks.webp
```

---

# Publishing Rules

```yaml
draft: true
featured: false
```

- preserve existing `publishedDate`
- always update `modifiedDate`

---

# Tag Rules

Generate 2–6 relevant tags:

- lowercase
- kebab-case
- technology-focused

Good:

```yaml
tags:
  - react
  - hooks
  - frontend
```

---

# SEO Rules

```yaml
seo:
  title: <title>
  description: <description>
  canonical: https://feel-free.com/blogs/<slug>
  image: <thumbnail>
```

Generate keywords from:

- tags
- technologies
- domain terms

Max 10 keywords.

---

# Defaults

```yaml
author: lazarus2019
lang: en
```

---

# Related Posts

Generate max 3 related posts using:

- same category
- overlapping tags
- same series

---

# Update Rules

When frontmatter exists:

- update managed fields
- preserve unknown fields
- preserve markdown body
- never duplicate frontmatter

Only modify frontmatter.
