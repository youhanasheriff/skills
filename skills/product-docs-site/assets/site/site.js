{
const $=s=>document.querySelector(s),$$=s=>[...document.querySelectorAll(s)];
const FIRST=$('.page').id.slice(2);
let cur=null,obs=null;
// theme
const root=document.documentElement;
try{const t=localStorage.getItem('docs-theme');if(t)root.dataset.theme=t}catch(e){}
$('.theme').addEventListener('click',()=>{
  const dark=root.dataset.theme?root.dataset.theme==='dark':matchMedia('(prefers-color-scheme:dark)').matches;
  root.dataset.theme=dark?'light':'dark';try{localStorage.setItem('docs-theme',root.dataset.theme)}catch(e){}
});
// copy buttons
for(const pre of $$('pre')){const b=document.createElement('button');b.className='copy';b.type='button';b.textContent='Copy';
  b.addEventListener('click',()=>{navigator.clipboard&&navigator.clipboard.writeText(pre.querySelector('code')?.innerText||pre.innerText);b.textContent='Copied';setTimeout(()=>b.textContent='Copy',1200)});pre.appendChild(b)}
// diagrams: expand
const lb=$('#lightbox'),lbb=$('.lbbody');
function openFig(f){const svg=f.querySelector('svg');if(!svg)return;const c=svg.cloneNode(true);c.removeAttribute('style');
  c.style.maxWidth='none';lbb.innerHTML='';lbb.appendChild(c);lb.hidden=false;$('.lbbar button').focus()}
for(const f of $$('.fig')){f.addEventListener('click',e=>{if(e.target.closest('a'))return;openFig(f)})}
$('.lbbar button').addEventListener('click',()=>{lb.hidden=true});
lb.addEventListener('click',e=>{if(e.target===lb)lb.hidden=true});
document.addEventListener('keydown',e=>{if(e.key==='Escape'&&!lb.hidden)lb.hidden=true});
// routing
function show(){
  const h=decodeURIComponent(location.hash.slice(1));
  let [pid]=h.split('--');let anchor=h.includes('--')?h:null;
  let el=document.getElementById('p-'+pid);
  if(!el){const t=h&&document.getElementById(h);const art=t&&t.closest('.page');if(art){el=art;pid=art.id.slice(2);anchor=h}else{el=document.getElementById('p-'+FIRST);pid=FIRST}}
  if(cur!==el){
    if(cur)cur.hidden=true;el.hidden=false;cur=el;
    const tab=el.dataset.tab;
    $$('.tabs a,.mtabs a').forEach(a=>a.classList.toggle('on',a.dataset.tab===tab));
    $$('.navtab').forEach(n=>n.hidden=n.dataset.tab!==tab);
    $$('.nl').forEach(a=>{const on=a.dataset.s===pid;a.classList.toggle('on',on);if(on){a.closest('details').open=true}});
    const on=$('.nl.on');if(on){const side=$('.side');const r=on.getBoundingClientRect(),sr=side.getBoundingClientRect();if(r.top<sr.top||r.bottom>sr.bottom)on.scrollIntoView({block:'center'})}
    const hs=[...el.querySelectorAll('h2,h3')];
    $('#toc').innerHTML='';
    for(const x of hs){const a=document.createElement('a');a.className=x.tagName.toLowerCase();a.href='#'+x.id;a.dataset.id=x.id;a.title=x.textContent;a.textContent=x.textContent;$('#toc').appendChild(a)}
    document.title=el.querySelector('h1').textContent+' · '+SITE+' Docs';
    if(obs)obs.disconnect();
    obs=new IntersectionObserver(es=>{for(const e of es){if(e.isIntersecting){$$('#toc a').forEach(a=>a.classList.toggle('on',a.dataset.id===e.target.id))}}},{rootMargin:'-120px 0px -70% 0px'});
    hs.forEach(x=>obs.observe(x));
    if(!anchor)window.scrollTo(0,0);
  }
  if(anchor){const t=document.getElementById(anchor);if(t)t.scrollIntoView()}
  $('.side').classList.remove('open');
}
addEventListener('hashchange',show);show();
$('.burger').addEventListener('click',()=>$('.side').classList.toggle('open'));
// search
const q=$('#q'),res=$('#res');let sel=0;
const esc=s=>s.replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
function search(){
  const v=q.value.trim().toLowerCase();if(!v){res.hidden=true;return}
  const terms=v.split(/\s+/).filter(Boolean);const out=[];
  for(const p of IDX){const t=p.t.toLowerCase(),x=p.x.toLowerCase();let sc=0,ok=true;
    for(const w of terms){const it=t.includes(w),ix=x.indexOf(w);if(!it&&ix<0){ok=false;break}sc+=(it?10:0)+(ix>=0?1+Math.min(5,x.split(w).length-1)*0.3:0)}
    if(ok){const i=x.indexOf(terms[0]);out.push({p,sc,sn:i>=0?p.x.slice(Math.max(0,i-60),i+120):p.x.slice(0,150)})}}
  out.sort((a,b)=>b.sc-a.sc);sel=0;
  const re=new RegExp('('+terms.map(w=>w.replace(/[.*+?^${}()|[\]\\]/g,'\\$&')).join('|')+')','gi');
  const hl=s=>esc(s).replace(re,'<mark>$1</mark>');
  res.innerHTML=out.slice(0,12).map((o,i)=>`<a href="#${esc(o.p.s)}" class="${i?'':'sel'}"><div class="rg">${esc(o.p.g)}</div><div class="rt">${hl(o.p.t)}</div><div class="rx">…${hl(o.sn)}…</div></a>`).join('')||'<div class="none">No results</div>';
  res.hidden=false}
q.addEventListener('input',search);q.addEventListener('focus',search);
q.addEventListener('keydown',e=>{const as=[...res.querySelectorAll('a')];
  if((e.key==='ArrowDown'||e.key==='ArrowUp')&&as.length){e.preventDefault();sel=(sel+(e.key==='ArrowDown'?1:-1)+as.length)%as.length;as.forEach((a,i)=>a.classList.toggle('sel',i===sel));as[sel].scrollIntoView({block:'nearest'})}
  if(e.key==='Enter'&&as[sel]){location.hash=as[sel].getAttribute('href');res.hidden=true;q.blur()}
  if(e.key==='Escape'){res.hidden=true;q.blur()}});
res.addEventListener('click',()=>{res.hidden=true});
document.addEventListener('click',e=>{if(!e.target.closest('.search'))res.hidden=true});
document.addEventListener('keydown',e=>{if(e.key==='/'&&document.activeElement!==q&&!/input|textarea/i.test(document.activeElement.tagName)){e.preventDefault();q.focus()}});
}
