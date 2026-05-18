#!/usr/bin/env python3
"""
Generate or update YAML frontmatter for markdown files under any `docs/` directories.

Follows rules in METADATA_GUIDE.md. Run with `--apply` to write changes.
"""
from __future__ import annotations
import argparse
import os
import re
import sys
from datetime import date
from pathlib import Path
from typing import Dict, List, Optional, Tuple

IGNORE_DIRS = {".git", "node_modules", "dist", ".astro"}
SKIP_FILES = {"README.md", "BRAIN_STORM.md"}
MANAGED_FIELDS = {
    "title",
    "description",
    "slug",
    "thumbnail",
    "publishedDate",
    "modifiedDate",
    "draft",
    "featured",
    "tags",
    "categories",
    "series",
    "seriesOrder",
    "seo",
    "author",
    "lang",
    "relatedPosts",
}


try:
    import yaml  # type: ignore
except Exception:
    yaml = None


def slugify(filename: str) -> str:
    base = Path(filename).stem
    base = re.sub(r"^\d+[-_.\s]*", "", base)
    s = base.lower()
    s = re.sub(r"[^a-z0-9]+", "-", s)
    s = re.sub(r"-+", "-", s).strip("-")
    return s or base.lower()


def title_from_filename(filename: str) -> str:
    base = Path(filename).stem
    base = re.sub(r"^\d+[-_.\s]*", "", base)
    base = base.replace("-", " ").replace("_", " ")
    return base.strip().title()


def extract_frontmatter_and_body(text: str) -> Tuple[Optional[Dict], str]:
    m = re.match(r"^---\s*\n(.*?)\n---\s*\n?", text, flags=re.S)
    if m:
        fm_text = m.group(1)
        body = text[m.end():]
        if yaml:
            try:
                data = yaml.safe_load(fm_text) or {}
            except Exception:
                data = {}
        else:
            # very small YAML frontmatter fallback parser for common simple cases
            def _cast_scalar(v: str):
                v = v.strip()
                if not v:
                    return ""
                if v.lower() in ("true", "false"):
                    return v.lower() == "true"
                mnum = re.match(r"^-?\d+$", v)
                if mnum:
                    try:
                        return int(v)
                    except Exception:
                        pass
                # strip quotes
                if (v.startswith('"') and v.endswith('"')) or (v.startswith("'") and v.endswith("'")):
                    return v[1:-1]
                # simple comma list
                if v.startswith("[") and v.endswith("]"):
                    items = [x.strip().strip('"').strip("'") for x in v[1:-1].split(",") if x.strip()]
                    return items
                return v

            def _parse_simple(fm_text: str) -> Dict:
                out: Dict = {}
                cur_key: Optional[str] = None
                for line in fm_text.splitlines():
                    if not line.strip() or line.strip().startswith("#"):
                        continue
                    mlist = re.match(r"^\s*-\s+(.*)$", line)
                    if mlist and cur_key:
                        out.setdefault(cur_key, []).append(_cast_scalar(mlist.group(1)))
                        continue
                    m = re.match(r"^\s*([A-Za-z0-9_\-]+):\s*(.*)$", line)
                    if m:
                        key = m.group(1)
                        val = m.group(2)
                        if val == "":
                            out[key] = []
                            cur_key = key
                        else:
                            out[key] = _cast_scalar(val)
                            cur_key = None
                return out

            try:
                data = _parse_simple(fm_text)
            except Exception:
                data = {}
        return data, body
    return None, text


def first_h1(body: str) -> Optional[str]:
    for line in body.splitlines():
        m = re.match(r"^\s*#\s+(.+)$", line)
        if m:
            return m.group(1).strip()
    return None


def first_paragraph(body: str) -> str:
    lines = body.splitlines()
    in_code = False
    para = []
    for line in lines:
        if line.strip().startswith("```"):
            in_code = not in_code
            continue
        if in_code:
            continue
        if line.strip().startswith("#"):
            continue
        if not line.strip():
            if para:
                break
            continue
        para.append(re.sub(r"\s+", " ", line).strip())
    return " ".join(para).strip()


def kebab(s: str) -> str:
    s2 = s.lower()
    s2 = re.sub(r"[^a-z0-9]+", "-", s2)
    s2 = re.sub(r"-+", "-", s2).strip("-")
    return s2


def find_thumbnail(path: Path, slug: str, repo_root: Path) -> Optional[str]:
    cur = path.parent
    while True:
        assets = cur / "assets"
        if assets.is_dir():
            cand = assets / f"{slug}.webp"
            if cand.exists():
                return os.path.relpath(cand, start=path.parent).replace(os.sep, "/")
            cand2 = assets / "thumbnail.webp"
            if cand2.exists():
                return os.path.relpath(cand2, start=path.parent).replace(os.sep, "/")
            for f in assets.glob("*.webp"):
                return os.path.relpath(f, start=path.parent).replace(os.sep, "/")
        if cur == repo_root or cur.parent == cur:
            break
        cur = cur.parent
    return None


def category_for_path(path: Path) -> Optional[str]:
    parts = path.parts
    # find index of 'docs'
    try:
        idx = parts.index("docs")
    except ValueError:
        return None
    # if docs is at repo root (idx == 0), next segment is category
    if idx == 0:
        if len(parts) > 1:
            nxt = parts[1]
            if '.' not in nxt:
                return nxt.lower()
        return None
    # otherwise take parent folder name (folder that contains docs)
    parent = parts[idx - 1]
    return parent.lower()


def yaml_dump(data: Dict) -> str:
    if yaml:
        return yaml.safe_dump(data, sort_keys=False, allow_unicode=True).rstrip() + "\n"
    # minimal fallback serializer for simple structures
    def dump(obj, indent=0):
        pad = " " * indent
        lines = []
        if isinstance(obj, dict):
            for k, v in obj.items():
                if v is None:
                    continue
                if isinstance(v, (dict, list)):
                    lines.append(f"{pad}{k}:")
                    lines.extend(dump(v, indent + 2))
                else:
                    if isinstance(v, str) and (":" in v or "#" in v or "\n" in v):
                        v = v.replace("\n", "\n")
                        lines.append(f"{pad}{k}: " + "|\n" + "\n".join([(" " * (indent + 2)) + l for l in v.splitlines()]))
                    elif isinstance(v, str):
                        lines.append(f"{pad}{k}: {v}")
                    else:
                        lines.append(f"{pad}{k}: {v}")
        elif isinstance(obj, list):
            for item in obj:
                if isinstance(item, (dict, list)):
                    lines.append(f"{pad}-")
                    lines.extend(dump(item, indent + 2))
                else:
                    lines.append(f"{pad}- {item}")
        else:
            lines.append(f"{pad}{obj}")
        return lines

    return "\n".join(dump(data)) + "\n"


def sanitize_description_text(s: Optional[str]) -> str:
    if s is None:
        return ""
    s = str(s)
    # remove common markdown characters the frontmatter must not contain
    s = re.sub(r"[>\[\]\(\)\*:]", "", s)
    # remove backticks and excessive punctuation
    s = s.replace('`', '')
    # collapse whitespace
    s = re.sub(r"\s+", " ", s).strip()
    # limit length to 160 chars
    if len(s) > 160:
        s = s[:160].rsplit(" ", 1)[0] + "..."
    return s


def generate_description_from_title(title: str) -> str:
    if not title:
        return ""
    # basic generation: rely on title and expand to short explanatory sentence
    clean_title = re.sub(r"[>\[\]\(\)\*:]", "", str(title))
    clean_title = re.sub(r"\s+", " ", clean_title).strip()
    low = clean_title.lower()
    desc = f"{clean_title}. Practical guide explaining {low} with clear examples, best practices and common pitfalls for developers"
    return sanitize_description_text(desc)


def build_frontmatter(meta: Dict, existing: Optional[Dict]) -> Dict:
    fm: Dict = {}
    # managed fields
    if meta.get("title"):
        fm["title"] = meta["title"]
    if meta.get("description"):
        fm["description"] = sanitize_description_text(meta["description"])
    fm["slug"] = meta["slug"]
    if meta.get("thumbnail"):
        fm["thumbnail"] = meta["thumbnail"]
    if meta.get("publishedDate"):
        fm["publishedDate"] = meta["publishedDate"]
    fm["modifiedDate"] = meta["modifiedDate"]
    fm["draft"] = meta.get("draft", True)
    fm["featured"] = meta.get("featured", False)
    if meta.get("tags"):
        fm["tags"] = meta["tags"]
    if meta.get("categories"):
        fm["categories"] = meta["categories"]
    if meta.get("series"):
        fm["series"] = meta["series"]
    if meta.get("seriesOrder") is not None:
        fm["seriesOrder"] = meta["seriesOrder"]
    # SEO
    seo = {}
    if meta.get("title"):
        seo["title"] = meta["title"]
    if meta.get("description"):
        seo["description"] = sanitize_description_text(meta["description"])
    if meta.get("slug"):
        seo["canonical"] = f"https://feel-free.com/blogs/{meta['slug']}"
    if meta.get("tags"):
        seo["keywords"] = meta["tags"][:10]
    if meta.get("thumbnail"):
        seo["image"] = meta["thumbnail"]
    if seo:
        fm["seo"] = seo
    fm["author"] = meta.get("author", "lazarus2019")
    fm["lang"] = meta.get("lang", "en")
    if meta.get("relatedPosts"):
        fm["relatedPosts"] = meta["relatedPosts"]

    # preserve unknown existing fields
    if existing:
        for k, v in existing.items():
            if k not in MANAGED_FIELDS:
                fm[k] = v

    return fm


def process_files(root: Path, apply: bool = False) -> Tuple[int, List[str]]:
    repo_root = root.resolve()
    files: List[Path] = []
    for p in repo_root.rglob("*"):
        if not p.is_file():
            continue
        if p.suffix.lower() not in {".md", ".mdx"}:
            continue
        parts = set(p.parts)
        if any(i in parts for i in IGNORE_DIRS):
            continue
        if p.name in SKIP_FILES:
            continue
        if "docs" not in p.parts:
            continue
        files.append(p)

    metas: Dict[str, Dict] = {}
    file_by_slug: Dict[str, Path] = {}

    today = date.today().isoformat()

    # first pass: collect metadata
    for p in files:
        text = p.read_text(encoding="utf-8")
        existing, body = extract_frontmatter_and_body(text)
        title = None
        if existing and existing.get("title"):
            title = existing.get("title")
        else:
            title = first_h1(body) or title_from_filename(p.name)
        slug = existing.get("slug") if existing and existing.get("slug") else slugify(p.name)
        # generate a new description based on the title and sanitize it
        desc = generate_description_from_title(title)
        thumb = find_thumbnail(p, slug, repo_root)
        # category rules
        cat = category_for_path(p) or None
        categories = [cat] if cat else []
        # tags: derive from category, parent folder, filename tokens
        tags = []
        if cat:
            tags.append(kebab(cat))
        parent = p.parent.name
        if parent and kebab(parent) not in tags:
            tags.append(kebab(parent))
        for tok in re.split(r"[-_\s]+", Path(p.name).stem):
            tok = tok.lower()
            tok = re.sub(r"^\d+", "", tok)
            if not tok:
                continue
            t = kebab(tok)
            if t and t not in tags:
                tags.append(t)
            if len(tags) >= 6:
                break
        if len(tags) < 2:
            tags.append("general")

        # series rules
        m = re.match(r"^(\d+)[-_.\s]+", p.name)
        series = None
        seriesOrder = None
        if m:
            seriesOrder = int(m.group(1))
            series = p.parent.name.replace("-", " ").title()

        publishedDate = existing.get("publishedDate") if existing and existing.get("publishedDate") else None

        # filter tags: remove empty and 'docs'
        tags = [t for t in tags if t and t != 'docs']

        meta = {
            "path": str(p),
            "title": title,
            "description": desc,
            "slug": slug,
            "thumbnail": thumb,
            "publishedDate": publishedDate,
            "modifiedDate": today,
            "draft": existing.get("draft") if existing and existing.get("draft") is not None else True,
            "featured": existing.get("featured") if existing and existing.get("featured") is not None else False,
            "tags": [t for t in tags if t],
            "categories": categories,
            "series": series,
            "seriesOrder": seriesOrder,
            "author": existing.get("author") if existing and existing.get("author") else "lazarus2019",
            "lang": existing.get("lang") if existing and existing.get("lang") else "en",
            "existing": existing,
        }

        metas[slug] = meta
        file_by_slug[slug] = p

    # second pass: compute related posts
    for slug, meta in metas.items():
        scores: Dict[str, int] = {}
        for other_slug, other_meta in metas.items():
            if other_slug == slug:
                continue
            score = 0
            if meta.get("series") and meta.get("series") == other_meta.get("series"):
                score += 5
            tags_a = set(meta.get("tags", []))
            tags_b = set(other_meta.get("tags", []))
            score += 2 * len(tags_a & tags_b)
            if meta.get("categories") and other_meta.get("categories") and meta.get("categories") == other_meta.get("categories"):
                score += 1
            if score > 0:
                scores[other_slug] = score
        related = [s for s, _ in sorted(scores.items(), key=lambda kv: (-kv[1], kv[0]))][:3]
        metas[slug]["relatedPosts"] = related

    # third pass: write frontmatter
    changed = []
    for slug, meta in metas.items():
        p = file_by_slug[slug]
        existing = meta.get("existing")
        fm = build_frontmatter(meta, existing)
        fm_text = "---\n" + yaml_dump(fm) + "---\n\n"
        orig = p.read_text(encoding="utf-8")
        _, body = extract_frontmatter_and_body(orig)
        new_text = fm_text + body.lstrip("\n")
        if new_text != orig:
            changed.append(str(p))
            if apply:
                p.write_text(new_text, encoding="utf-8")

    return len(changed), changed


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=".", help="Repository root")
    ap.add_argument("--apply", action="store_true", help="Write changes to files")
    args = ap.parse_args()
    root = Path(args.root)
    total, changed_files = process_files(root, apply=args.apply)
    if args.apply:
        print(f"Updated {total} files")
        for f in changed_files:
            print(f"WROTE: {f}")
    else:
        print(f"Would update {total} files (run with --apply to write)")
        for f in changed_files:
            print(f"DRY: {f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
#!/usr/bin/env python3
"""
Generate frontmatter for markdown files under docs/ following METADATA_GUIDE.md rules.
This script updates files in-place. It preserves unknown custom frontmatter fields.
"""

import re
import os
from pathlib import Path
from datetime import date
from collections import Counter

ROOT = Path(__file__).resolve().parents[1]
TODAY = date.today().isoformat()

MANAGED_KEYS = [
    'title', 'description', 'slug', 'thumbnail',
    'publishedDate', 'modifiedDate', 'draft', 'featured',
    'tags', 'categories', 'series', 'seriesOrder',
    'seo', 'author', 'contributors', 'lang', 'relatedPosts'
]

STOPWORDS = set([
    'the','and','for','with','that','this','from','using','use','how','what',
    'a','an','of','in','on','to','by','is','are','it','as','be','or','we','our'
])


def kebab(s: str) -> str:
    s = s.strip()
    s = re.sub(r"[A-Z]+(?=[A-Z][a-z])", lambda m: m.group(0).lower(), s)
    s = re.sub(r"[\s_]+", "-", s)
    s = re.sub(r"[^a-zA-Z0-9-]+", "-", s)
    s = re.sub(r"-+", "-", s)
    return s.strip('-').lower()


def title_case_from_dir(name: str) -> str:
    parts = re.split(r"[-_\s]+", name)
    return ' '.join([p.capitalize() for p in parts if p])


def find_docs_files(root: Path):
    files = []
    for p in root.rglob('docs/**/*'):
        if p.is_file() and p.suffix.lower() in ('.md', '.mdx'):
            if p.name in ('README.md', 'BRAIN_STORM.md'):
                continue
            if p.name.startswith('.'):
                continue
            files.append(p)
    return sorted(files)


def split_frontmatter(text: str):
    if text.lstrip().startswith('---'):
        parts = re.split(r'^---\s*$', text, maxsplit=2, flags=re.M)
        if len(parts) >= 3:
            fm_text = parts[1].strip()
            body = parts[2].lstrip('\n')
            return fm_text, body
    return None, text


def parse_frontmatter_blocks(fm_text: str):
    # Split into top-level blocks keyed by top-level keys
    lines = fm_text.splitlines()
    blocks = []
    key = None
    buf = []
    for ln in lines:
        m = re.match(r'^([A-Za-z0-9_]+)\s*:\s*(.*)$', ln)
        if m and not ln.startswith('  '):
            # top-level key
            if key is not None:
                blocks.append((key, buf))
            key = m.group(1)
            buf = [ln]
        else:
            if key is None:
                key = '__meta__'
                buf = [ln]
            else:
                buf.append(ln)
    if key is not None:
        blocks.append((key, buf))
    return blocks


def serialize_list(name: str, items):
    out = f"{name}:\n"
    for it in items:
        out += f"  - {it}\n"
    return out


def generate_description(body: str):
    # remove code fences
    body_no_code = re.sub(r'```[\s\S]*?```', '', body)
    # split paragraphs
    paras = [p.strip() for p in re.split(r'\n\s*\n', body_no_code) if p.strip()]
    desc = ''
    for p in paras:
        if p.startswith('#'):
            continue
        # collapse whitespace
        p = re.sub(r'\s+', ' ', p).strip()
        if len(p) >= 40:
            desc = p
            break
    if not desc and paras:
        desc = re.sub(r'\s+', ' ', paras[0]).strip()
    if not desc:
        return ''
    # truncate to 160 chars, prefer whole sentences
    if len(desc) <= 160:
        return desc
    # try to keep up to last sentence within limit
    sentences = re.split(r'(?<=[.!?])\s+', desc)
    s = ''
    for sent in sentences:
        if len(s) + len(sent) <= 160:
            s = (s + ' ' + sent).strip()
        else:
            break
    if s:
        return s
    # fallback truncate without cutting words
    truncated = desc[:157].rsplit(' ', 1)[0]
    return truncated + '...'


def extract_tags(body: str, max_tags=6):
    # gather tokens from headings and code spans
    text = ''
    # headings
    headings = re.findall(r'^(#{2,})\s*(.+)$', body, flags=re.M)
    for h in headings:
        text += ' ' + h[1]
    # inline code and code blocks
    code = re.findall(r'`([^`]+)`', body)
    text += ' ' + ' '.join(code)
    # also include first paragraph
    body_no_code = re.sub(r'```[\s\S]*?```', '', body)
    paras = [p.strip() for p in re.split(r'\n\s*\n', body_no_code) if p.strip()]
    if paras:
        text += ' ' + paras[0]
    # tokenize
    tokens = re.findall(r"[A-Za-z0-9+#]+", text)
    tokens = [t.lower() for t in tokens if len(t) >= 2]
    tokens = [t for t in tokens if t not in STOPWORDS]
    if not tokens:
        return []
    cnt = Counter(tokens)
    common = [t for t,_ in cnt.most_common()]
    tags = []
    for t in common:
        tag = kebab(t)
        if tag and tag not in tags:
            tags.append(tag)
        if len(tags) >= max_tags:
            break
    return tags


def find_thumbnail(file_path: Path, slug: str):
    # search upward for assets/ and prefer slug.webp -> thumbnail.webp -> first .webp
    cur = file_path.parent
    root = ROOT
    candidates = []
    while True:
        assets = cur / 'assets'
        if assets.exists() and assets.is_dir():
            # check for slug.webp
            for ext in ('.webp', '.png', '.jpg', '.jpeg', '.avif'):
                f = assets / (slug + ext)
                if f.exists():
                    return os.path.relpath(f, start=file_path.parent).replace('\\', '/')
            # thumbnail.webp
            f = assets / 'thumbnail.webp'
            if f.exists():
                return os.path.relpath(f, start=file_path.parent).replace('\\', '/')
            # first .webp
            for f in sorted(assets.iterdir()):
                if f.suffix.lower() == '.webp':
                    return os.path.relpath(f, start=file_path.parent).replace('\\', '/')
            # fallback to other formats
            for f in sorted(assets.iterdir()):
                if f.suffix.lower() in ('.png', '.jpg', '.jpeg', '.avif'):
                    return os.path.relpath(f, start=file_path.parent).replace('\\', '/')
        if cur == root or cur.parent == cur:
            break
        cur = cur.parent
    # no assets found; return default relative path ../assets/slug.webp
    fallback = os.path.join('..', 'assets', f'{slug}.webp').replace('\\', '/')
    return fallback


def build_frontmatter(managed: dict, preserved_blocks: list):
    # Build frontmatter string in exact order
    lines = []
    lines.append('---')
    # title
    lines.append(f"title: {managed.get('title','Title')}")
    # description
    desc = managed.get('description','Description')
    lines.append(f"description: {desc}")
    lines.append('')
    # slug
    lines.append(f"slug: {managed.get('slug')}")
    lines.append('')
    # Media
    lines.append('# Media')
    lines.append(f"thumbnail: {managed.get('thumbnail')}")
    lines.append('')
    # Publishing
    lines.append('# Publishing')
    lines.append(f"publishedDate: '{managed.get('publishedDate')}'")
    lines.append(f"modifiedDate: '{managed.get('modifiedDate')}'")
    lines.append(f"draft: {str(managed.get('draft')).lower()}")
    lines.append(f"featured: {str(managed.get('featured')).lower()}")
    lines.append('')
    # Taxonomy
    lines.append('# Taxonomy')
    tags = managed.get('tags', [])
    if tags:
        lines.append('tags:')
        for t in tags:
            lines.append(f"  - {t}")
    else:
        lines.append('tags:')
        lines.append('  - example')
    lines.append('')
    cats = managed.get('categories', [])
    if cats:
        lines.append('categories:')
        for c in cats:
            lines.append(f"  - {c}")
    else:
        lines.append('categories:')
        lines.append("  - frontend")
    lines.append('')
    # series (optional)
    if managed.get('series'):
        lines.append(f"series: {managed.get('series')}")
        if managed.get('seriesOrder') is not None:
            lines.append(f"seriesOrder: {managed.get('seriesOrder')}")
        lines.append('')
    # SEO
    lines.append('# SEO')
    lines.append('seo:')
    lines.append(f"  title: {managed.get('seo_title', managed.get('title'))}")
    lines.append(f"  description: {managed.get('seo_description', managed.get('description'))}")
    lines.append(f"  canonical: https://feel-free.com/blogs/{managed.get('slug')}")
    keywords = managed.get('seo_keywords', [])
    if keywords:
        lines.append('  keywords:')
        for k in keywords:
            lines.append(f"    - {k}")
    else:
        lines.append('  keywords:')
        lines.append('    - react')
        lines.append('    - frontend')
    lines.append(f"  image: {managed.get('thumbnail')}")
    lines.append('')
    # Author
    lines.append('# Author')
    lines.append(f"author: {managed.get('author','lazarus2019')}")
    contributors = managed.get('contributors')
    if contributors:
        lines.append('contributors:')
        for c in contributors:
            lines.append(f"  - {c}")
    lines.append('')
    # Localization
    lines.append('# Localization')
    lines.append(f"lang: {managed.get('lang','en')}")
    lines.append('')
    # Content relations
    related = managed.get('relatedPosts')
    if related:
        lines.append('relatedPosts:')
        for r in related:
            lines.append(f"  - {r}")
    lines.append('---')

    # append preserved blocks for unknown keys (insert before final ---? Actually we should keep unknown keys preserved; they will be lost if appended after closing --- )
    # To preserve unknown fields, we insert them before the final '---'.
    # Approach: find index of last '---' marker at end and insert preserved blocks before it.

    # Build raw string
    out = '\n'.join(lines)

    # If there are preserved blocks, re-insert them before final '---'
    if preserved_blocks:
        # remove trailing '---'
        if out.endswith('\n---'):
            out = out[:-4]
        # append preserved blocks
        for blk_key, blk_lines in preserved_blocks:
            out += '\n'
            out += '\n'.join(blk_lines)
        out += '\n---'
    return out + '\n\n'


def process_file(p: Path):
    text = p.read_text(encoding='utf-8')
    fm_text, body = split_frontmatter(text)

    preserved = []
    existing = {}
    if fm_text:
        blocks = parse_frontmatter_blocks(fm_text)
        for k, lines in blocks:
            if k in MANAGED_KEYS or k == '__meta__':
                # skip managed keys for now
                continue
            preserved.append((k, lines))
        # try to extract some managed values simply
        m = re.search(r"^slug:\s*(.+)$", fm_text, flags=re.M)
        if m:
            existing['slug'] = m.group(1).strip()
        m = re.search(r"^publishedDate:\s*'?(\d{4}-\d{2}-\d{2})'?", fm_text, flags=re.M)
        if m:
            existing['publishedDate'] = m.group(1)
        m = re.search(r"^author:\s*(.+)$", fm_text, flags=re.M)
        if m:
            existing['author'] = m.group(1).strip()
        m = re.search(r"^draft:\s*(true|false)", fm_text, flags=re.M)
        if m:
            existing['draft'] = (m.group(1).lower() == 'true')
        m = re.search(r"^contributors:\s*", fm_text, flags=re.M)
        if m:
            # naive: capture following indented lines
            contribs = re.findall(r'^\s*-\s*(.+)$', fm_text, flags=re.M)
            existing['contributors'] = [c.strip() for c in contribs]

    # title
    title = None
    m = re.search(r'^#\s+(.+)$', body, flags=re.M)
    if m:
        title = m.group(1).strip()
    if not title:
        # derive from filename
        stem = p.stem
        # remove numeric prefix
        stem = re.sub(r'^\d+[-_. ]*', '', stem)
        title = ' '.join([w.capitalize() for w in re.split(r'[-_\s]+', stem) if w])

    # slug
    if 'slug' in existing:
        slug = existing['slug']
    else:
        slug = kebab(re.sub(r'^\d+[-_. ]*', '', p.stem))

    # category
    parts = p.parts
    try:
        idx = parts.index('docs')
    except ValueError:
        idx = -1
    category = None
    if idx != -1:
        if len(parts) > idx + 2:
            # there's a directory after docs
            category = parts[idx + 1]
        else:
            # file directly under docs; fallback to parent folder before docs
            if idx - 1 >= 0:
                category = parts[idx - 1]
    if category:
        category = kebab(category)

    # series detection
    series = None
    seriesOrder = None
    mnum = re.match(r'^(\d+)[-_. ]', p.name)
    if mnum:
        seriesOrder = int(mnum.group(1))
        series = title_case_from_dir(p.parent.name)

    # thumbnail
    thumb = find_thumbnail(p, slug)

    # description
    description = generate_description(body)

    # tags
    tags = extract_tags(body)

    # seo keywords
    seo_keywords = tags[:10]

    managed = {
        'title': title,
        'description': description or 'Description',
        'slug': slug,
        'thumbnail': thumb,
        'publishedDate': existing.get('publishedDate', TODAY),
        'modifiedDate': TODAY,
        'draft': existing.get('draft', True),
        'featured': False,
        'tags': tags,
        'categories': [category] if category else [],
        'series': series,
        'seriesOrder': seriesOrder,
        'seo_title': title,
        'seo_description': description or title,
        'seo_keywords': seo_keywords,
        'author': existing.get('author', 'lazarus2019'),
        'contributors': existing.get('contributors'),
        'lang': 'en',
        'relatedPosts': None
    }

    new_fm = build_frontmatter(managed, preserved)
    new_text = new_fm + body
    if text != new_text:
        p.write_text(new_text, encoding='utf-8')
        return True, p
    return False, p


def main():
    files = find_docs_files(ROOT)
    print(f"Found {len(files)} docs files")
    changed = []
    for f in files:
        try:
            updated, path = process_file(f)
            if updated:
                changed.append(path)
                print(f"Updated: {path}")
        except Exception as e:
            print(f"Error processing {f}: {e}")
    print('\nSummary:')
    print(f"Files scanned: {len(files)}")
    print(f"Files updated: {len(changed)}")
    for p in changed:
        print(f" - {p}")

if __name__ == '__main__':
    main()
