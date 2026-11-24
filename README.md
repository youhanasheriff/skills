# Skills

Agent skills I've written and use day to day. Each one is a folder under `skills/` with a `SKILL.md` and any scripts or references it needs.

| Skill | What it does |
|---|---|
| [product-docs-site](skills/product-docs-site) | Builds a complete Stripe-style documentation site from a product's code: product guides, architecture, API reference, operations and a roadmap of known gaps, as one HTML file with real diagrams |

## Install

With the [`skills`](https://skills.sh) command-line tool:

```
npx skills add youhanasheriff/skills                            # pick from the list
npx skills add youhanasheriff/skills --skill product-docs-site  # one skill
```

Or clone the repository and link a skill into your agent's skills folder:

```
git clone https://github.com/youhanasheriff/skills ~/Developer/skills
ln -s ~/Developer/skills/skills/product-docs-site ~/.claude/skills/product-docs-site
```

Some skills need a one-time setup step; see each skill's own README.

## Licence

MIT; see `LICENSE`. Files bundled from others keep their own licences, noted in each skill.
