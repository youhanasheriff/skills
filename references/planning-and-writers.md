# Planning the site and briefing writers

## Contents
1. Choosing tabs
2. Splitting the work into writer sections
3. PAGE_PLAN.md template
4. Writer brief template
5. Running writers and recovering from interruptions
6. Fixing wide diagrams with a helper

## 1. Choosing tabs

Tabs follow the product, not a fixed list. Pick 6 to 8. Each tab has an ID prefix (the text before the first hyphen of every page ID in it).

Always present:

| Prefix | Tab | Holds |
|---|---|---|
| `start` | Home | Welcome with cards to every tab, how it works, key concepts, quickstarts per audience |
| `arch` | Architecture | System overview and data flows first, then one group per component |
| `ops` | Operations | Hosting today, deploys, config and secrets, backups, monitoring, releases, local development, production plan, runbooks |
| `ref` | Resources | Roadmap and known gaps, decisions, glossary, outside services, config references |

Then one tab per user-facing surface and one for interfaces, for example:

| Product shape | Extra tabs |
|---|---|
| Device + app + server | `use` Using the device · `app` Caregiver app · `hw` Hardware · `api` API reference |
| Desktop app + cloud + consoles | `app` Desktop app · `console` Administration · `api` API reference |
| Web SaaS | `guide` Product guides · `admin` Admin · `api` API reference · `sdk` SDKs |

Within a tab, group pages by what the reader is doing (Getting started, Everyday use, …), not by source folder.

## 2. Splitting the work into writer sections

One writer per area that one person could read in a sitting, about 12 to 25 pages each. Five to seven writers is typical for a multi-repo product. Good splits seen so far:

- User guide for the main surface (from the user's side, real phrases and labels).
- Second surface (app, console) guides, plus that component's architecture.
- Core component architecture + its local interfaces + its config reference.
- Server architecture + **every** endpoint in the router + server config reference.
- Hardware (if any) from the design package, cross-checked against drivers.
- Operations from deploy files, CI, release scripts and hosting notes.

The editor (you) writes Home, the system overview and data-flow pages, and Resources (roadmap, decisions, glossary, services), and assembles everything.

File naming: two-digit order prefix so `sorted()` gives tab order inside a tab, e.g. `00-home.md`, `10-using.md`, `20-app.md`, `40-arch-overview.md`, `41-arch-core.md`, `42-arch-server.md`, `50-api-server.md`, `60-operations.md`, `90-resources.md`, `91-ref-core-config.md`.

## 3. PAGE_PLAN.md template

Write `src/PAGE_PLAN.md` before briefing anyone, so writers can cross-link to pages that don't exist yet.

```
# {Product} docs: page plan

The tab of a page comes from its ID prefix. Each writer owns the files listed.

| Tab | ID prefix | File | Owner |
|---|---|---|---|
| Home | `start-` | `00-home.md` | editor |
| … | … | … | writer A |

Keep these IDs; others link to them. You may split, merge or add pages with your own prefix if the code calls for it, but report any planned ID you drop. Groups are suggestions.

## {Tab} ({owner})
- `prefix-page-id` Title
- …
```

List 10 to 25 planned page IDs per writer, each with a short title that says what the page covers.

## 4. Writer brief template

Each writer starts with no context, so the brief carries everything. Keep the shared rules in CONVENTIONS.md and keep the brief to scope.

```
You are writing one section of a full, Stripe-style documentation site for {Product}, {one-line description}.

Workspace: {abs path}
First read these two files fully and follow them exactly:
- {abs}/src/CONVENTIONS.md
- {abs}/src/PAGE_PLAN.md

Your section: **{Section}** (writer {X}), ID prefix `{prefix}-`. Write it to {abs}/src/docs/{NN-name}.md
{If several files: list each file and which planned pages go in it.}

Cover every planned `{prefix}-` page in PAGE_PLAN.md: {what the reader needs from this section, e.g. "for each feature: what it does, how to use it with the real labels, limits and defaults with numbers from the code, and what admins control"}. Mark decided-but-unbuilt behaviour as **Planned** and mismatches as **Known gap**, using {decision source path}.

Main sources: {repo paths and the folders that matter}. Verify facts in code; docs/ may be stale.

Include Mermaid diagrams: {the specific diagrams this section should have}. Aim for roughly {N} pages and at least {M} diagrams. Read only; do not edit any repository or other writers' files. Do not build or run anything. End with the final report described in CONVENTIONS.md.
```

For an API section add: "document **every** route in the router, each as `### METHOD /path`". For a config reference add: "every key with type, default and effect; never copy secret values".

## 5. Running writers and recovering from interruptions

- Launch all writers in one turn so they run in parallel. If your environment has an asynchronous task tool (one that wakes you on completion), use it; otherwise use the subagent tool with several calls in one message. Keep each `taskId` or thread link.
- While they run: set up tools (`setup_tools.sh`), write the editor pages, and test-build with whatever files exist. Missing-page link warnings are expected until all writers finish.
- If the machine sleeps or the run is stopped, check each task's status. A writer that was mid-research keeps its context: send its thread a message ("The pause is over. Nothing has been written yet; finish and write your file as briefed") rather than starting a fresh writer, which would redo all the reading. Check `src/docs/` first to see what was already written.
- As each writer reports, copy its Known gaps into a working list for the roadmap page and note anything it could not confirm.

## 6. Fixing wide diagrams with a helper

After the first full build, the builder prints `WIDE DIAGRAM on <page>: W×H`. It already tries the flipped direction for wide flowcharts and state diagrams. If more than about five remain, brief one helper:

```
Re-lay out these Mermaid diagrams in {abs}/src/docs/*.md so each is at most 900 px wide (ideally under 800) with text at full size. Conventions: {abs}/src/CONVENTIONS.md (Diagrams section).

Build and measure: {exact build command}
The build prints WIDE DIAGRAM lines with page id and size.

Diagrams: {page id, size, file, diagram type — one per line}

Ways to get there: fewer boxes per row; stack groups vertically (subgraphs with `direction TB`, or invisible links `a ~~~ b`); shorten labels with `<br>`; split one diagram into two with a short sentence between; for erDiagrams split by area and list key columns only when the tables below already list every column. Keep every fact, box, arrow and colour class. Edit only those mermaid blocks. Rebuild until none are over 900 px and none fail. Report final sizes.
```

Don't edit the same files yourself while the helper runs; if you need a change in those files meanwhile (for example sidebar group names), make it in `site.json` (`group_rename`) instead.
