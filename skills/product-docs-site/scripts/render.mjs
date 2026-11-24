// Usage: node render.mjs jobs.json outdir
// jobs.json: [{"id": "<hash>", "code": "<mermaid>"}]; writes <outdir>/<id>.svg or <id>.err
import fs from 'node:fs';
import path from 'node:path';
import puppeteer from 'puppeteer';

const [, , jobsFile, outDir] = process.argv;
const jobs = JSON.parse(fs.readFileSync(jobsFile, 'utf8'));
fs.mkdirSync(outDir, { recursive: true });

const config = {
  theme: 'base',
  fontFamily: 'Inter, system-ui, sans-serif',
  themeVariables: {
    fontFamily: 'Inter, system-ui, sans-serif',
    fontSize: '14px',
    primaryColor: '#eef2ff',
    primaryBorderColor: '#2f5fe0',
    primaryTextColor: '#1a1f36',
    secondaryColor: '#f7f8fb',
    tertiaryColor: '#ffffff',
    lineColor: '#5b6478',
    textColor: '#1a1f36',
    clusterBkg: '#f7f8fb',
    clusterBorder: '#c9d1e3',
    edgeLabelBackground: '#ffffff',
    actorBkg: '#eef2ff',
    actorBorder: '#2f5fe0',
    actorTextColor: '#1a1f36',
    signalColor: '#5b6478',
    signalTextColor: '#1a1f36',
    labelBoxBkgColor: '#eef2ff',
    labelBoxBorderColor: '#2f5fe0',
    noteBkgColor: '#fff8e1',
    noteBorderColor: '#d4a72c',
    noteTextColor: '#1a1f36',
    activationBkgColor: '#dfe7ff',
    activationBorderColor: '#2f5fe0',
  },
  flowchart: { htmlLabels: true, curve: 'basis', nodeSpacing: 36, rankSpacing: 48, padding: 12, useMaxWidth: false },
  sequence: { useMaxWidth: false, wrap: true, width: 140, actorMargin: 30, noteMargin: 10, messageMargin: 32, boxMargin: 8, mirrorActors: false },
  state: { useMaxWidth: false },
  er: { useMaxWidth: false, fontSize: 13 },
  class: { useMaxWidth: false },
};

const fontFile = process.env.DOCS_FONT;
const fontB64 = fontFile ? fs.readFileSync(fontFile).toString('base64') : '';
const mermaidJs = fs.readFileSync(new URL('./node_modules/mermaid/dist/mermaid.min.js', import.meta.url), 'utf8');
const browser = await puppeteer.launch({ headless: true, args: ['--no-sandbox'] });
const page = await browser.newPage();
await page.setContent(`<!doctype html><html><head><style>@font-face{font-family:Inter;src:url(data:font/woff2;base64,${fontB64}) format("woff2");font-weight:100 900}body{font-family:Inter}</style></head><body><span style="font-family:Inter">Inter</span><div id="c"></div></body></html>`);
await page.addScriptTag({ content: mermaidJs });
await page.evaluate(async (cfg) => {
  await document.fonts.load('14px Inter'); await document.fonts.ready;
  window.mermaid.initialize({ startOnLoad: false, securityLevel: 'loose', ...cfg });
}, config);
let ok = 0, bad = 0;
for (const job of jobs) {
  const r = await page.evaluate(async (id, code) => {
    try { const { svg } = await window.mermaid.render('m' + id, code, document.getElementById('c')); return { svg }; }
    catch (e) { document.querySelectorAll('[id^="dm"],[id^="m"]').forEach(n => { if (n.id !== 'c') n.remove() }); return { err: String(e && e.message || e) }; }
  }, job.id, job.code);
  if (r.svg) { fs.writeFileSync(path.join(outDir, job.id + '.svg'), r.svg); ok++; }
  else { fs.writeFileSync(path.join(outDir, job.id + '.err'), r.err); bad++; }
}
await browser.close();
console.log(`rendered ${ok}, failed ${bad}`);
