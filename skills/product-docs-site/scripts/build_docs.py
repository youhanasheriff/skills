#!/usr/bin/env python3
"""Build a product documentation site into one self-contained HTML file.

Usage:
  python build_docs.py --src <docs-src-dir> [--out PATH]

<docs-src-dir> holds `site.json` (title, tabs, …) and `docs/*.md`. Each Markdown
file holds many pages, each starting with
  <!-- page id="prefix-name" group="Sidebar group" title="Sidebar label" -->
The id prefix (text before the first hyphen) picks the tab.

Needs the Python packages `markdown` and `mdx_truly_sane_lists`, and a tools
folder prepared by `setup_tools.sh` (Node.js, Mermaid, headless Chrome). Set
DOCS_TOOLS to that folder (default ~/.cache/product-docs-site/tools).
Rendered diagrams are cached in <src>/.diagram-cache/.
"""
import base64, hashlib, html, json, os, re, shutil, subprocess, sys
from pathlib import Path

import markdown

HERE = Path(__file__).resolve().parent
ASSETS = HERE.parent / 'assets' / 'site'
if '--src' not in sys.argv:
    sys.exit(__doc__)
SRC = Path(sys.argv[sys.argv.index('--src') + 1]).resolve()
CFG = json.loads((SRC / 'site.json').read_text())
DOCS = SRC / 'docs'
CACHE = SRC / '.diagram-cache'
TOOLS = Path(os.environ.get('DOCS_TOOLS', Path.home() / '.cache' / 'product-docs-site' / 'tools'))
OUT = (SRC / CFG.get('output', f"../{CFG['name']} Docs.html")).resolve()
if '--out' in sys.argv:
    OUT = Path(sys.argv[sys.argv.index('--out') + 1]).resolve()

TABS = [(t['prefix'], t['name'], t.get('subtitle', '')) for t in CFG['tabs']]
TAB_BY_PREFIX = {p: (name, sub) for p, name, sub in TABS}

# Colour classes for flowchart nodes. `own` is the product's own parts; aliases
# in site.json ("class_aliases": ["acme"]) get the same style.
_OWN = 'fill:#eef2ff,stroke:#2f5fe0,stroke-width:1.4px,color:#1a1f36'
CLASSDEFS = '\n'.join(
    [f'classDef {n} {_OWN}' for n in ['own'] + CFG.get('class_aliases', [])] + [
        'classDef ext fill:#fff4e5,stroke:#b7791f,stroke-width:1.4px,color:#1a1f36',
        'classDef data fill:#ecfdf3,stroke:#1f7a4d,stroke-width:1.4px,color:#1a1f36',
        'classDef bad fill:#fef1f1,stroke:#b91c1c,stroke-width:1.4px,color:#1a1f36',
        'classDef hw fill:#f3f0ff,stroke:#6d4bd8,stroke-width:1.4px,color:#1a1f36',
    ])

# Sidebar groups that two files share inside one tab get merged; rename them
# per file in site.json: "group_rename": [{"file": "41-x.md", "group": "Data", "to": "Server · Data"}]
GROUP_RENAME = {(r['file'], r['group']): r['to'] for r in CFG.get('group_rename', [])}

PAGE_RE = re.compile(r'^<!--\s*page\s+(.*?)\s*-->\s*$', re.M)
ATTR_RE = re.compile(r'(\w+)="([^"]*)"')
FENCE_RE = re.compile(r'^```mermaid[ \t]*\n(.*?)^```[ \t]*$', re.M | re.S)
METHODS = r'(GET|POST|PUT|PATCH|DELETE|WS|WEBSOCKET)'


def slug(t):
    t = re.sub(r'<[^>]+>', '', t)
    t = html.unescape(t).lower()
    t = re.sub(r'[^a-z0-9]+', '-', t).strip('-')
    return t[:60] or 'section'


def load_pages():
    pages = []
    for f in sorted(DOCS.glob('*.md')):
        text = f.read_text()
        marks = list(PAGE_RE.finditer(text))
        for i, m in enumerate(marks):
            attrs = dict(ATTR_RE.findall(m.group(1)))
            body = text[m.end(): marks[i + 1].start() if i + 1 < len(marks) else len(text)]
            pid = attrs.get('id', '').strip()
            prefix = pid.split('-')[0]
            if prefix not in TAB_BY_PREFIX:
                print(f'WARN {f.name}: page {pid!r} has unknown prefix', file=sys.stderr)
                continue
            group = attrs.get('group', 'General')
            group = GROUP_RENAME.get((f.name, group), group)
            pages.append(dict(id=pid, group=group, title=attrs.get('title', pid),
                              body=body.strip('\n'), file=f.name, prefix=prefix))
    seen = set()
    for p in pages:
        if p['id'] in seen:
            print(f"WARN duplicate page id {p['id']} in {p['file']}", file=sys.stderr)
        seen.add(p['id'])
    order = {p: i for i, (p, _, _) in enumerate(TABS)}
    pages.sort(key=lambda p: order[p['prefix']])  # stable: keeps file order within a tab
    return pages


def prep_mermaid(code):
    code = code.strip('\n')
    first = code.lstrip().split('\n', 1)[0].strip()
    if first.startswith(('flowchart', 'graph')):
        code += '\n' + CLASSDEFS
    return code


def _run_render(jobs):
    if not jobs:
        return
    for j in jobs:
        (CACHE / f"{j['id']}.err").unlink(missing_ok=True)
    jf = CACHE / 'jobs.json'
    jf.write_text(json.dumps(jobs))
    print(f'rendering {len(jobs)} diagrams…', file=sys.stderr)
    if not (TOOLS / 'node_modules').exists():
        sys.exit(f'No tools at {TOOLS}. Run setup_tools.sh first, or set DOCS_TOOLS.')
    shutil.copy(HERE / 'render.mjs', TOOLS / 'render.mjs')
    subprocess.run(['node', str(TOOLS / 'render.mjs'), str(jf), str(CACHE)], check=True, cwd=TOOLS,
                   env={**os.environ, 'DOCS_FONT': str(ASSETS / 'inter-latin.woff2')})


def svg_size(h):
    p = CACHE / f'{h}.svg'
    if not p.exists():
        return None
    m = re.search(r'viewBox="[\d.\-]+ [\d.\-]+ ([\d.]+) ([\d.]+)"', p.read_text())
    return (float(m.group(1)), float(m.group(2))) if m else None


def flipped(code):
    """Return the code with its main direction swapped, or None if not applicable."""
    lines = code.split('\n')
    head = lines[0].strip()
    m = re.match(r'^(flowchart|graph)\s+(TB|TD|LR|RL|BT)\b', head)
    if m:
        new = 'LR' if m.group(2) in ('TB', 'TD', 'BT') else 'TB'
        lines[0] = f'{m.group(1)} {new}'
        return '\n'.join(lines)
    if head.startswith('stateDiagram'):
        for i, l in enumerate(lines[1:], 1):
            if re.match(r'^\s*direction\s+(LR|TB)\s*$', l) and not lines[i - 1].strip().startswith('state '):
                lines[i] = l.replace('LR', 'TB') if 'LR' in l else l.replace('TB', 'LR')
                return '\n'.join(lines)
        return '\n'.join([lines[0], '  direction LR'] + lines[1:])
    return None


CHOICE = {}
MAXW = 960


def fit(sz):
    if not sz:
        return -1
    w, h = sz
    scale = min(1.0, 760 / w)
    return scale - (0.15 if h * scale > 1500 else 0)


def render_diagrams(jobs):
    CACHE.mkdir(exist_ok=True)
    uniq = list({j['id']: j for j in jobs}.values())
    _run_render([j for j in uniq if not (CACHE / f"{j['id']}.svg").exists()])
    alts = []
    for j in uniq:
        sz = svg_size(j['id'])
        if sz and sz[0] > MAXW:
            alt = flipped(j['code'])
            if alt:
                ah = hashlib.sha1(alt.encode()).hexdigest()[:14]
                alts.append({'id': ah, 'code': alt, 'of': j['id']})
    _run_render([{'id': a['id'], 'code': a['code']} for a in alts if not (CACHE / f"{a['id']}.svg").exists()])
    for a in alts:
        if fit(svg_size(a['id'])) > fit(svg_size(a['of'])) + 0.05:
            CHOICE[a['of']] = a['id']


def clean_svg(svg, did):
    svg = re.sub(r'<\?xml[^>]*>', '', svg).strip()
    # natural size: take width from viewBox so it never stretches
    m = re.search(r'viewBox="([\d.\-]+) ([\d.\-]+) ([\d.]+) ([\d.]+)"', svg)
    if m:
        w, h = float(m.group(3)), float(m.group(4))
        svg = re.sub(r'<svg([^>]*?)\sstyle="[^"]*"', r'<svg\1', svg, count=1)
        svg = re.sub(r'<svg([^>]*?)\swidth="[^"]*"', r'<svg\1', svg, count=1)
        svg = re.sub(r'<svg([^>]*?)\sheight="[^"]*"', r'<svg\1', svg, count=1)
        svg = svg.replace('<svg', f'<svg width="{w:.0f}" height="{h:.0f}" style="max-width:100%"', 1)
    return svg


def md_to_html(body, pid, jobs, diag_ids, quiet=False):
    figs = {}

    def fence(m):
        code = prep_mermaid(m.group(1))
        h = hashlib.sha1(code.encode()).hexdigest()[:14]
        jobs.append({'id': h, 'code': code})
        key = f'MERMAIDFIG{len(figs)}X{pid.replace("-", "")}'
        figs[key] = h
        diag_ids.append(h)
        return f'\n\n<div class="figph">{key}</div>\n\n'

    body = FENCE_RE.sub(fence, body)
    out = markdown.markdown(body, extensions=['tables', 'fenced_code', 'mdx_truly_sane_lists', 'sane_lists'],
                            extension_configs={'mdx_truly_sane_lists': {'nested_indent': 2, 'truly_sane': True}},
                            output_format='html5')
    # headings: ids and endpoint cards
    used = set()

    def head(m):
        lvl, inner = m.group(1), m.group(2)
        base = f'{pid}--{slug(inner)}'
        hid, n = base, 2
        while hid in used:
            hid, n = f'{base}-{n}', n + 1
        used.add(hid)
        cls = ''
        if lvl == '3':
            em = re.match(rf'^(?:<code>)?{METHODS}\s+(\S.*?)(?:</code>)?$', inner)
            if em:
                meth = em.group(1)
                cls = ' class="ep"'
                inner = f'<span class="m {meth.lower()}">{meth}</span><code>{em.group(2)}</code>'
        return f'<h{lvl} id="{hid}"{cls}>{inner}</h{lvl}>'

    out = re.sub(r'<h([23])>(.*?)</h\1>', head, out)
    out = re.sub(r'<h1>(.*?)</h1>', r'<h1>\1</h1>', out, count=1)
    # callouts
    def callout(m):
        inner = m.group(1)
        k = re.match(r'\s*<p><strong>(Note|Planned|Known gap|Warning|Tip)</strong>', inner)
        if not k:
            return m.group(0)
        cls = {'Note': 'note', 'Tip': 'note', 'Planned': 'planned', 'Known gap': 'gap', 'Warning': 'warn'}[k.group(1)]
        return f'<blockquote class="callout {cls}">{inner}</blockquote>'
    out = re.sub(r'<blockquote>(.*?)</blockquote>', callout, out, flags=re.S)
    out = re.sub(r'<table>', '<div class="tw"><table>', out)
    out = out.replace('</table>', '</table></div>')
    for key, h in figs.items():
        h = CHOICE.get(h, h)
        svgp = CACHE / f'{h}.svg'
        if svgp.exists():
            fig = f'<figure class="fig" data-d="{h}"><button class="zoom" type="button">Expand</button>{clean_svg(svgp.read_text(), h)}</figure>'
        else:
            err = (CACHE / f'{h}.err').read_text()[:300] if (CACHE / f'{h}.err').exists() else 'not rendered'
            if not quiet: print(f'WARN diagram failed on {pid}: {err.splitlines()[0] if err else ""}', file=sys.stderr)
            fig = f'<figure class="fig err"><p>Diagram failed to render.</p></figure>'
        out = re.sub(rf'<div class="figph">{key}</div>|<p>{key}</p>', lambda _m: fig, out)
    return out


def plain(htmltext):
    t = re.sub(r'<figure.*?</figure>', ' ', htmltext, flags=re.S)
    t = re.sub(r'<[^>]+>', ' ', t)
    return re.sub(r'\s+', ' ', html.unescape(t)).strip()


def build():
    pages = load_pages()
    jobs = []
    # first pass to collect diagrams
    for p in pages:
        md_to_html(p['body'], p['id'], jobs, [], quiet=True)
    render_diagrams(jobs)
    total_diagrams = 0
    for p in pages:
        dids = []
        p['html'] = md_to_html(p['body'], p['id'], [], dids)
        total_diagrams += len(dids)
        m = re.search(r'<h1>(.*?)</h1>', p['html'])
        p['h1'] = re.sub(r'<[^>]+>', '', m.group(1)) if m else p['title']
        if not m:
            p['html'] = f'<h1>{html.escape(p["title"])}</h1>' + p['html']
        p['text'] = plain(p['html'])
    ids = {p['id'] for p in pages}
    anchors = set(ids)
    for p in pages:
        anchors.update(re.findall(r'<h[23] id="([^"]+)"', p['html']))
    broken = []
    for p in pages:
        for href in re.findall(r'href="#([^"]+)"', p['html']):
            if href not in anchors:
                base = href.split('--')[0]
                broken.append((p['id'], href, base in ids))
    # navigation
    by_tab = {}
    for p in pages:
        by_tab.setdefault(p['prefix'], []).append(p)
    tabs_html, mtabs, nav = [], [], []
    for prefix, name, sub in TABS:
        if prefix not in by_tab:
            continue
        first = by_tab[prefix][0]['id']
        tabs_html.append(f'<a data-tab="{prefix}" href="#{first}">{html.escape(name)}</a>')
        groups = {}
        for p in by_tab[prefix]:
            groups.setdefault(p['group'], []).append(p)
        g_html = ''.join(
            f'<details class="ng" open><summary>{html.escape(g)}</summary>' +
            ''.join(f'<a class="nl" href="#{p["id"]}" data-s="{p["id"]}">{html.escape(p["title"])}</a>' for p in ps) +
            '</details>' for g, ps in groups.items())
        nav.append(f'<div class="navtab" data-tab="{prefix}" hidden><div class="navhead">{html.escape(name)}<span>{html.escape(sub)}</span></div>{g_html}</div>')
    tabs_joined = ''.join(tabs_html)
    articles = []
    for i, p in enumerate(pages):
        tabname = TAB_BY_PREFIX[p['prefix']][0]
        tabfirst = by_tab[p['prefix']][0]['id']
        prev = pages[i - 1] if i else None
        nxt = pages[i + 1] if i + 1 < len(pages) else None
        pn = '<nav class="pn">' + (f'<a href="#{prev["id"]}"><span>Previous</span>{html.escape(prev["title"])}</a>' if prev else '<span></span>') + \
             (f'<a class="next" href="#{nxt["id"]}"><span>Next</span>{html.escape(nxt["title"])}</a>' if nxt else '') + '</nav>'
        crumb = f'<div class="crumb"><a href="#{tabfirst}">{html.escape(tabname)}</a><span>›</span>{html.escape(p["group"])}</div>'
        articles.append(f'<article class="page" id="p-{p["id"]}" data-tab="{p["prefix"]}" hidden>{crumb}{p["html"]}{pn}</article>')
    index = [{'s': p['id'], 't': p['h1'], 'g': f"{TAB_BY_PREFIX[p['prefix']][0]} › {p['group']}", 'x': p['text']} for p in pages]
    words = sum(len(p['text'].split()) for p in pages)
    font = base64.b64encode((ASSETS / 'inter-latin.woff2').read_bytes()).decode()
    css = (ASSETS / 'site.css').read_text().replace('FONTDATA', font)
    js = (ASSETS / 'site.js').read_text()
    foot = f'{len(pages)} pages · {total_diagrams} diagrams · ~{round(words, -3) // 1000}k words' + (f"<br>{html.escape(CFG['footer'])}" if CFG.get('footer') else '')
    doc = f'''<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{html.escape(CFG['title'])}</title>
<style>{css}</style></head>
<body>
<header class="top"><button class="burger" aria-label="Open menu">&#9776;</button><a class="brand" href="#{pages[0]['id']}"><span class="logo">{html.escape(CFG.get('logo', CFG['name'][:1]))}</span>{html.escape(CFG['name'])} <span class="docs">Docs</span></a>
<div class="search"><input id="q" type="search" placeholder="Search the docs" autocomplete="off" aria-label="Search"><kbd>/</kbd><div id="res" hidden></div></div>
<button class="theme" type="button" aria-label="Switch theme" title="Switch theme">&#9680;</button></header>
<nav class="tabs" aria-label="Sections">{tabs_joined}</nav>
<div class="wrap">
<aside class="side"><div class="mtabs">{tabs_joined}</div>{''.join(nav)}<div class="sidefoot">{foot}</div></aside>
<main id="main">{''.join(articles)}</main>
<aside class="toc"><div class="toct">On this page</div><div id="toc"></div></aside>
</div>
<div id="lightbox" hidden><div class="lbbar"><span>Diagram</span><button type="button">Close</button></div><div class="lbbody"></div></div>
<script>const SITE={json.dumps(CFG['name'])};const IDX={json.dumps(index, ensure_ascii=False).replace("</", "<\\/")};
{js}</script>
</body></html>'''
    OUT.write_text(doc)
    print(f'wrote {OUT} ({len(doc)/1e6:.2f} MB): {len(pages)} pages, {total_diagrams} diagrams, ~{words} words', file=sys.stderr)
    for p in pages:
        for w, h in re.findall(r'<svg width="(\d+)" height="(\d+)"', p['html']):
            if int(w) > 900:
                print(f'WIDE DIAGRAM on {p["id"]}: {w}x{h} px (column is ~760; re-lay out to under 900)', file=sys.stderr)
    for src, href, base_ok in broken:
        print(f'BROKEN LINK on {src}: #{href}' + (' (page exists, anchor missing)' if base_ok else ''), file=sys.stderr)
    return broken


if __name__ == '__main__':
    build()
