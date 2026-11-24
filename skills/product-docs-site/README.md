# product-docs-site

An agent skill that turns a product's code repositories into a complete, Stripe-style documentation site: product guides, architecture, API reference, operations, hardware, roadmap and known gaps. The output is one self-contained HTML file.

The site has:
- tabs for each big area, a sidebar of collapsible groups and an "On this page" list,
- full-text search (press `/`), light and dark themes, and a phone layout,
- real diagrams: Mermaid rendered to SVG, each with a full-screen **Expand** view,
- **Planned** and **Known gap** callouts wherever the code differs from what the product should do, collected on a roadmap page.

Pages are written by several writer agents in parallel, each reading one area of the code. The skill's instructions cover planning, briefing, assembling, checking and publishing.

## Install

From the [youhanasheriff/skills](https://github.com/youhanasheriff/skills) collection:

```
npx skills add youhanasheriff/skills --skill product-docs-site
```

Then run the one-time tool setup from wherever the skill was installed, for example:

```
~/.claude/skills/product-docs-site/scripts/setup_tools.sh
```

`setup_tools.sh` is run once. It installs the build tools into `~/.cache/product-docs-site/tools`: a Python virtual environment with `markdown`, plus Node packages for Mermaid and headless Chrome (about 400 MB).

Requirements: Python 3.10+, Node.js 18+, npm, and an agent that can run subagents.

## Use

Ask for it in plain words inside a project, for example "write full documentation for this product, like Stripe's docs". The skill then:

1. Plans tabs and pages and writes a shared conventions file.
2. Briefs writer agents in parallel, one per area of the code.
3. Writes the Home, overview and roadmap pages itself.
4. Builds, fixes links and diagrams, scans for private data, screenshots pages, and delivers the HTML with its editable Markdown sources.

## Build a site by hand

```
DOCS_TOOLS=~/.cache/product-docs-site/tools \
  ~/.cache/product-docs-site/tools/venv/bin/python scripts/build_docs.py --src path/to/docs/src
```

`path/to/docs/src` holds `site.json` and `docs/*.md`. Copy `assets/example/` to start; building it gives a three-page sample site. Each Markdown file holds many pages:

```
<!-- page id="guide-first-steps" group="Getting started" title="First steps" -->
# First steps
```

The ID prefix (`guide`) picks the tab from `site.json`. The build reports broken links, diagrams that fail to render and diagrams too wide for the page.

## Layout

| Path | What it is |
|---|---|
| `SKILL.md` | The workflow the agent follows |
| `references/` | Conventions template, planning and writer briefs, editor pages |
| `scripts/build_docs.py` | Markdown pages to one HTML file |
| `scripts/render.mjs` | Mermaid to SVG in headless Chrome |
| `scripts/setup_tools.sh` | One-time tool install |
| `scripts/shot.mjs` | Page screenshots for checking layout |
| `scripts/check_docs.sh` | Scan for secrets, IPs, personal paths and emails |
| `assets/site/` | Page design (CSS, JS, Inter font) |
| `assets/example/` | Starter `site.json` and pages |

## Licence

MIT for this repository; see `LICENSE`. The bundled Inter font is under the SIL Open Font License 1.1; see `assets/site/OFL-Inter.txt`.
