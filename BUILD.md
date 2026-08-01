# Build Notes

This workshop is published with the local `workshop-publisher` tool:

```bash
~/Development/workshop-publisher
```

The installed command is:

```bash
workshop-publish
```

## One-Time Setup

Install or refresh the editable local publisher:

```bash
uv tool install -e ~/Development/workshop-publisher
```

That puts `workshop-publish` on your path. Because it is installed with `-e`,
changes in `~/Development/workshop-publisher` are used by the command.

Install the workshop environment:

```bash
uv sync --frozen
```

Codespaces uses `.devcontainer/devcontainer.json` to install `uv`, run the same
locked sync, and register a Jupyter kernel named `Natural PDF Workshop`.

## Rebuild

Run this from the workshop root, the directory containing
`workshop-config.yaml`:

```bash
cd /Users/soma/Library/CloudStorage/Dropbox/Soma/Curriculum/2026-nicar/02-fri-natural-pdf/natural-pdf-workshop
workshop-publish
```

The publisher reads `workshop-config.yaml`, deletes and recreates `docs/`, and
regenerates `README.md`.

The generated site entry point is:

```bash
docs/index.html
```

## Colab Kernel Restart After Install

Colab ships with a Pillow that doesn't match what `natural-pdf` needs, and the
preloaded copy stays stale after `pip install`. The `restart_check` key under
`default_install` in `workshop-config.yaml` handles this: every generated setup
cell ends with a Colab-only block that runs the configured import
(`from PIL import ImageText`) and, if it raises `ImportError`, restarts the
kernel once. Everything is already installed at that point, so the student just
continues with the next cell — no re-run needed. Outside Colab the block is a
no-op. Notebooks can override or opt out with `restart_check` in their own
`install:` dict (`restart_check: false` disables it).

## Current Warning Behavior

`workshop-publish` prints warnings but still exits successfully. Use
`workshop-publish --strict` when you want warnings to fail the build.

The current warnings are:

- `04-Page structure.ipynb` has 0 `solution`-tagged cells.
- `05-Final boss.ipynb` has 0 `solution`-tagged cells.

Those warnings mean the code-along versions of those notebooks will not blank
any cells. If that is intentional because they are demo-only notebooks, the
warnings are safe to ignore.

## Useful Options

```bash
workshop-publish --help
workshop-publish --no-clean
workshop-publish --strict
workshop-publish --output-dir docs-test
workshop-publish --execute
```

Use `--execute` only when you want the publisher to execute notebooks before
publishing. Because `workshop-config.yaml` sets
`execution_environment: "project"`, it runs `uv sync --frozen` and executes with
the project `.venv`. It also loads `.env` if present.
