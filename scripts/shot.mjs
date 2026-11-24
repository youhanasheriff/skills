import puppeteer from 'puppeteer';
const [,,file,outPrefix,...hashes]=process.argv;
const b=await puppeteer.launch({headless:true,args:['--no-sandbox']});
const p=await b.newPage();await p.setViewport({width:1440,height:1000,deviceScaleFactor:1});
for(const [i,h] of hashes.entries()){
  const [hash,theme]=h.split('@');
  await p.goto('file://'+file+'#'+hash);
  if(theme){await p.evaluate(t=>document.documentElement.dataset.theme=t,theme)}
  await p.evaluate(()=>new Promise(r=>setTimeout(r,300)));
  await p.screenshot({path:`${outPrefix}${i}.png`,fullPage:false});
}
const wide=await p.evaluate(()=>[...document.querySelectorAll('.fig svg')].map(s=>[s.closest('.page').id,+s.getAttribute('width')]).filter(x=>x[1]>760));
console.log('wide diagrams', wide.length, JSON.stringify(wide.slice(0,40)));
await b.close();
