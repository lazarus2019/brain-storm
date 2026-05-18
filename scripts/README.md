# Scripts

Small utility scripts used by this repository to generate documentation and other auxiliary artifacts.

## Overview

This folder contains simple shell scripts that help generate or scaffold content in the repository. Most scripts are lightweight helpers intended to be run from the repository root.

## Included scripts

- `generate-docs.sh`
  - Purpose: generate a new documentation folder from the `github/` template.
  - Behavior: copies the `github/` template into `./<name>/`, performs text substitutions for the tokens `github`, `GITHUB`, and `Github` inside files, and renames files whose names contain those tokens.
  - Usage:

    ```bash
    # create ./test from the github template
    bash scripts/generate-docs.sh test

    # overwrite existing ./test
    bash scripts/generate-docs.sh test --force

    # make executable and run
    chmod +x scripts/generate-docs.sh
    ./scripts/generate-docs.sh mydocs
    ```

  - Notes:
    - The script uses Bash globstar (`shopt -s globstar`), so Bash 4+ is recommended.
    - It uses GNU-style `sed -i` in-place edits; on non-GNU `sed` (macOS/BSD) you may need to adapt the `sed -i` usage.
    - The template source is the repository folder `github/` at the repo root.

- `generate-category.sh`, `generate-series.sh`, `generate-sitemap.sh`
  - Status: present as stubs in this repo. These scripts are placeholders and currently empty — add implementation and update this README when they gain functionality.

## Template

The template used by `generate-docs.sh` is the `github/` directory at the repository root. Edit files inside `github/` to customize the base content used when scaffolding new documentation folders.

## How it works (high level)

1. Copy `github/` to the target directory `./<name>/`.
2. Replace textual tokens inside files (`github`, `GITHUB`, `Github`) so content reflects the new target name.
3. Rename any files or paths containing the tokens to use the new name.

## Testing / Examples

From the repository root:

```bash
# generate a directory named "test" from the template
bash scripts/generate-docs.sh test

# if the target exists, overwrite with --force
bash scripts/generate-docs.sh test --force
```

After running, inspect the generated folder (e.g., `./test`) to verify renamed files and substituted content.

## Contributing

If you add or change script behavior, update this README with the new usage and notes. When adding features that change file content or rename behavior, include tests or a short example run in this README.

## Troubleshooting

- If you see errors from `sed -i`, you may be running a non-GNU `sed` (macOS). Use GNU sed or adjust the in-place edit syntax (e.g., `sed -i '' -e "s/.../.../g"` on macOS).
- If globs don't expand, confirm you're running the script with Bash (not sh) and that Bash supports `globstar`.
