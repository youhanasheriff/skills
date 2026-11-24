---
name: product-docs-site
description: Build a complete Stripe-style documentation site for a whole product from its codebase — product guides, architecture, API reference, operations, hardware, roadmap and known gaps — written by parallel writer agents that read the code, with real Mermaid diagrams rendered to SVG, and delivered as one self-contained HTML file (tabs, sidebar, search, on-this-page, light/dark) plus a private published page. Use this whenever the user asks for "full documentation", "complete docs", "docs like Stripe's", a product handbook, a docs site or developer portal for their app, project or repositories, even if they don't say "site" or "HTML". Also use it to update, re-categorise or redraw diagrams in a docs site previously built this way.
---

# Product docs site

Turns one or more code repositories into a documentation site in the shape of Stripe's docs: a top bar with tabs for each big area, a sidebar of collapsible groups, an "On this page" rail, search, light and dark themes, and drawn diagrams. Everything is written from reading the code, and every page says where the code differs from what the product should do.

The workflow below has produced sites of 130 to 150 pages with over 100 diagrams; the notes on each step are the mistakes that cost time.

## What you deliver

1. `<project>/artifacts/<product>-docs/<Product> Docs.html`: one self-contained file (fonts, diagrams and search index inlined; typically 2 to 6 MB).
2. The editable sources beside it in `src/`: `site.json`, `docs/*.md`, `CONVENTIONS.md`, `PAGE_PLAN.md`, a short `README.md` on how to rebuild.
3. The same HTML published as a private artifact page (when an artifacts publishing tool is available), so the user has a link to share.

The bundled builder does the HTML; your work is the content and its accuracy.

## Bundled files

| Path | Use |
|---|---|
| `scripts/build_docs.py` | Markdown pages → the single HTML file. Renders Mermaid, checks links, reports wide or failed diagrams |
| `scripts/render.mjs` | Mermaid → SVG in headless Chrome with the Inter font loaded first (so labels are measured right and don't clip) |
| `scripts/setup_tools.sh` | One-time install of the build tools into `~/.cache/product-docs-site/tools` |
| `scripts/shot.mjs` | Screenshots of given pages for checking layout: `node shot.mjs <html> <out-prefix> page-id[@light\|@dark] …` |
| `scripts/check_docs.sh` | Scans the sources for IPs, secrets, personal paths and emails |
| `assets/site/` | Page design (CSS, JS, embedded Inter font). Shared by every site |
| `assets/example/` | A tiny `site.json` + `docs/` to copy as a starting point |
| `references/conventions-template.md` | The writing rules every writer follows; copy and fill per project |
| `references/planning-and-writers.md` | Choosing tabs, splitting work, PAGE_PLAN and writer-brief templates, recovery, wide-diagram helper brief |
| `references/editor-pages.md` | What you write yourself: Home, system overview, roadmap, decisions, glossary |

## Workflow

### 1. Scope (short)

Find the repositories and their default branches. Note who owns and operates the product, names to avoid, and anything private.

**Before planning anything, ask the user whether they want to add information beyond the codebase.** Ask once, in one short question, and give examples so they know what counts:
- product requirements, specs or a feature list,
- decisions already taken, a roadmap, user flows or a known-gaps list,
- hosting, deployment or account details that aren't in the repositories,
- who the docs are for, names or terms to use or avoid, anything to leave out.

They can answer with files, links, pasted text or "no". Also ask which repositories are in scope if that isn't obvious from the workspace.

- **If they add sources:** read them, list them in CONVENTIONS.md under "Sources of truth", and point every writer at them. Decisions found there drive the **Planned** and **Known gap** callouts. Where a source and the code disagree, the page states what the code does and marks the difference.
- **If they say no (or don't answer):** use the project's code and the files inside its repositories only (code, configs, READMEs, in-repo docs). Don't invent decisions or plans. Without a decision source, use **Planned** only for work the repositories themselves describe as planned, such as a roadmap file or TODO comments, and say where it comes from. Use **Known gap** for code that is broken, inconsistent, unfinished or contradicts its own docs.

Why ask: the code shows what the product does, not what it is meant to do. The extra sources are what turn the docs from a description into a useful map of gaps, and only the user knows they exist.

Don't ask about layout or style: the design is fixed.

### 2. Set up the workspace

```
<project>/artifacts/<product>-docs/src/
  site.json          (copy assets/example/site.json, set title, name, logo letter, tabs, footer)
  CONVENTIONS.md     (from references/conventions-template.md, filled in)
  PAGE_PLAN.md       (tabs, files, owners, planned page IDs)
  docs/
```

Start `scripts/setup_tools.sh` in the background now (it downloads Chrome for Testing and Mermaid, a few minutes). Read `references/planning-and-writers.md` for choosing tabs, splitting sections and the PAGE_PLAN template.

### 3. Launch writers in parallel

One writer per section (usually 5 to 7), all launched in the same turn, each with the brief template in `references/planning-and-writers.md`. Writers read the code and the agreed sources only, and write only their own files. They must not build, run or deploy anything.

Why parallel writers: each section needs deep reading of one area of the code. One agent doing everything runs out of context and goes shallow; six agents each go deep, and you keep the whole-site view.

### 4. Write the editor pages while they work

Home, `arch-overview`, `arch-data-flows` and the Resources pages: see `references/editor-pages.md`. Then test-build with whatever exists:

```
DOCS_TOOLS=~/.cache/product-docs-site/tools ~/.cache/product-docs-site/tools/venv/bin/python <skill>/scripts/build_docs.py --src <…>/src
```

Link warnings to pages not written yet are expected at this stage.

### 5. Assemble

As each writer reports: collect its Known gaps and its "could not confirm" items. When all are in:

1. Build. Fix every `BROKEN LINK` (wrong ID, or a planned page a writer dropped) and every failed diagram (the error text says which line; usual causes are reserved node IDs like `call` or `end` and unquoted labels with parentheses).
2. Fix sidebar groups that two files share in one tab (they merge into one mixed group) with `group_rename` in `site.json`, rather than editing writers' files.
3. Fix `WIDE DIAGRAM` lines. The builder already tries the other direction for wide flowcharts. If more than a handful remain, hand them to one helper with the brief in `references/planning-and-writers.md` §6; otherwise re-lay them out yourself.
4. Add every new Known gap to the roadmap page, most serious first.
5. Run `scripts/check_docs.sh <src>` and clear anything private. Hits on product facts are fine, for example a model name the product calls at runtime. Leftover names of other companies in identifiers are facts to state as Known gaps, not to hide.

### 6. Check how it looks

Screenshot a few pages in light and dark (Home, one diagram-heavy architecture page, one API page, the roadmap) with `scripts/shot.mjs`, and one at phone width. Look at them. Diagrams should fit the column, subgraph titles shouldn't clip, and tables shouldn't overflow. Don't skip this: an earlier build looked fine in the build log but had clipped diagram titles and diagrams cut off on the right.

### 7. Deliver

- Write `src/README.md` (layout of `src/`, build command, how to edit a page or diagram).
- Publish the HTML as a private artifact from the file on disk (read the artifacts guide first if the session hasn't yet), with an icon such as `book`.
- Final reply: the link and local path, page / diagram / word counts, the tab list with a line each, the few most important Known gaps the writing turned up, and plainly what was not verified (docs come from reading code; nothing was run; any facts writers couldn't confirm).

## Rules that apply throughout

- **Accuracy over coverage.** Every claim comes from the code or a named document. When the two disagree, the code wins and the page says so. Writers mark decided-but-unbuilt work **Planned** and mismatches **Known gap**; this is what makes the docs useful to the team, not just pretty.
- **Nothing private in the output.** No secret values, private IPs, SSH hosts, personal paths or people's emails. Name variables, never values.
- **Don't modify the product repositories.** The docs live in their own folder.
- **Diagrams, not drawings.** Every diagram is Mermaid rendered to SVG; never ASCII art. Colour classes: `own`, `ext`, `data`, `bad`, `hw` (plus any alias in `site.json` `class_aliases`).

## Updating an existing docs site

To re-categorise: change `group`/`title` attributes or `site.json` tabs and rebuild. To redraw diagrams: edit the Mermaid text; only changed diagrams re-render (cache in `src/.diagram-cache/`). To refresh after code changes: brief writers on the changed areas only, with their existing file as the starting point, then rebuild and republish to the same artifact (`slug` + `base_version`).
