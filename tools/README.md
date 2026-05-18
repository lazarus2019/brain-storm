# Generate frontmatter for docs files

Tool: `generate_frontmatter.py`

Usage:

1. Dry run (shows what would change):

```
python3 tools/generate_frontmatter.py
```

2. Apply changes (write frontmatter into files):

```
python3 tools/generate_frontmatter.py --apply
```

Notes:

- The script follows rules in `METADATA_GUIDE.md` where possible.
- It will skip `README.md` and `BRAIN_STORM.md` files.
- It does not add any `format: markdown` field to frontmatter.
