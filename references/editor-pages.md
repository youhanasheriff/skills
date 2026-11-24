# Pages the editor writes

The editor writes the pages that need the whole picture: Home, the system overview, and Resources. Write them while the writers research. Use the same page-marker format as everyone else.

## Home (`00-home.md`, prefix `start-`)

1. **`start-welcome` Welcome.** `# {Product} documentation`, a one-paragraph lead, then a card grid with one card per tab (raw HTML is fine in Markdown):

   ```
   <div class="cards">
   <a href="#start-quickstart-x"><b>Get started</b><span>One line on what's there.</span></a>
   …
   </div>
   ```

   Then: a table of the products or components (who uses each, what it is, where it runs); what each audience can do; "How these docs are organised" naming every tab; a **Note** callout saying which code and date the docs describe and what **Planned** and **Known gap** mean, linking to the roadmap.
2. **`start-how-it-works`.** One system diagram (no more than 6 to 7 boxes; avoid subgraphs whose titles arrows cross), a short section per component, one end-to-end sequence diagram of the main user action, and where data lives.
3. **`start-concepts` Key concepts.** A term / meaning table of the product's own words.
4. **Quickstarts.** One per audience (end user or admin, engineer). The end-user one is numbered steps with a small step diagram; the engineer one lists repositories, "read these first" links and local-development links.

## Architecture opening (`40-arch-overview.md`)

- **`arch-overview` System overview.** Component diagram with hosting, a channel table (between, channel, carries, trust), design principles, and a "where to go next" table linking each component's first page.
- **`arch-data-flows` Where data lives and moves.** A stores diagram, a table of stores (holds, kept for how long), and a table of what moves on each key event. Mark retention or privacy work as **Planned** where decided.

## Resources (`90-resources.md`, prefix `ref-`)

1. **`ref-roadmap` Roadmap and known gaps.**
   - If a decision document has a gap list, reproduce it grouped by area as tables (the product should / the code today / status), with the totals.
   - Then "Other known gaps found while writing these docs": de-duplicated Known gaps from every writer's report, one table per component (gap / where). Put the ones that matter most for safety or launch first and in bold.
   - Then production work (area / work / needed by) and open questions.
2. **`ref-decisions` Product decisions.** Every decision, newest first (date / topic / decision). Don't name individuals as decision makers unless the user wants that.
3. **`ref-glossary` Glossary.** Technical terms from the engineering pages; product terms stay in Key concepts.
4. **`ref-services` Outside services and accounts.** Service / used for / today / for production.

Config references (`ref-*-config`) are written by the writer who owns that component.

## After all writers report

- Add every new Known gap to the roadmap page.
- Read each writer's "could not confirm" list. Where your own pages state one of those facts, check it in the code or soften it.
- Check your own Home and overview claims against the writers' pages (names, numbers, defaults). Writers read the code more closely than you did.
