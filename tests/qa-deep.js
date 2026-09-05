const { chromium } = require('playwright');
const fs=require('fs');
const GS=fs.readFileSync('node_modules/gsap/dist/gsap.min.js','utf8');
const ST=fs.readFileSync('node_modules/gsap/dist/ScrollTrigger.min.js','utf8');
const PAGES=['index','for-brands','for-teams','what-we-make','workwear','our-factory','how-it-works','pricing','faq','compliance','about','contact','quote'];
(async()=>{
 const b=await chromium.launch();
 const p=await b.newPage({viewport:{width:1440,height:900}});
 await p.route('**/gsap.min.js',r=>r.fulfill({contentType:'application/javascript',body:GS}));
 await p.route('**/ScrollTrigger.min.js',r=>r.fulfill({contentType:'application/javascript',body:ST}));
 await p.route('**/fonts.googleapis.com/**',r=>r.abort());
 const bad=[]; const seenTitles=new Map(); const seenDesc=new Map();
 const missingAssets=new Set();
 p.on('requestfailed',req=>{const u=req.url(); if(u.startsWith('file://')&&/assets\//.test(u)) missingAssets.add(u.split('/site_v1/')[1]);});
 for(const pg of PAGES){
  await p.goto('file://'+process.cwd()+'/'+pg+'.html',{waitUntil:'load'});
  await p.waitForTimeout(pg==='index'?2200:600);
  const r=await p.evaluate(()=>{
   const ids={},dupIds=[];
   document.querySelectorAll('[id]').forEach(e=>{ids[e.id]=(ids[e.id]||0)+1;});
   for(const k in ids) if(ids[k]>1) dupIds.push(k+'×'+ids[k]);
   const hs=[...document.querySelectorAll('h1,h2,h3,h4')].map(h=>+h.tagName[1]);
   let skip=null; for(let i=1;i<hs.length;i++) if(hs[i]-hs[i-1]>1){skip=`h${hs[i-1]}→h${hs[i]}`;break;}
   const inlineExempt=a=>{const p=a.parentElement; if(!p) return false;
     return /^(P|LI|TD|SPAN|B|EM|SMALL)$/.test(p.tagName) && p.textContent.trim().length>a.textContent.trim().length+8;};
   return {
    title:document.title, tlen:document.title.length,
    desc:(document.querySelector('meta[name=description]')||{}).content||'',
    hasViewport:!!document.querySelector('meta[name=viewport]'),
    charset:!!document.querySelector('meta[charset]'),
    lang:document.documentElement.getAttribute('lang'),
    dupIds, headingSkip:skip,
    internal:[...new Set([...document.querySelectorAll('a[href$=".html"]')].map(a=>a.getAttribute('href')))],
    anchors:[...new Set([...document.querySelectorAll('a[href^="#"]')].map(a=>a.getAttribute('href').slice(1)))].filter(x=>x),
    ext:[...new Set([...document.querySelectorAll('a[href^="http"]')].map(a=>a.getAttribute('href')))],
    extNoRel:[...document.querySelectorAll('a[href^="http"][target="_blank"]')].filter(a=>!(a.getAttribute('rel')||'').includes('noopener')).length,
    tinyReal:[...document.querySelectorAll('a,button')].filter(e=>{const b=e.getBoundingClientRect();
      return b.width>0&&b.height>0&&b.height<32&&!inlineExempt(e);}).length,
    imgs:[...document.querySelectorAll('img')].map(i=>({s:i.getAttribute('src')||'',a:!!i.getAttribute('alt'),w:i.naturalWidth})),
    videos:[...document.querySelectorAll('video source')].map(s=>s.getAttribute('src')),
   };
  });
  if(r.tlen>72) bad.push(`${pg}: title ${r.tlen} chars (>72 truncates in search)`);
  if(!r.desc) bad.push(`${pg}: no meta description`);
  else if(r.desc.length>165) bad.push(`${pg}: meta description ${r.desc.length} chars`);
  if(!r.hasViewport) bad.push(`${pg}: no viewport meta`);
  if(!r.charset) bad.push(`${pg}: no charset`);
  if(!r.lang) bad.push(`${pg}: <html> has no lang`);
  if(r.dupIds.length) bad.push(`${pg}: duplicate ids ${r.dupIds.join(',')}`);
  if(r.headingSkip) bad.push(`${pg}: heading level skip ${r.headingSkip}`);
  if(r.extNoRel) bad.push(`${pg}: ${r.extNoRel} target=_blank without noopener`);
  if(r.tinyReal) bad.push(`${pg}: ${r.tinyReal} non-inline tap target <32px`);
  for(const l of r.internal) if(!fs.existsSync(''+process.cwd()+'/'+l)) bad.push(`${pg}: broken link -> ${l}`);
  for(const a of r.anchors) { const has=await p.evaluate(id=>!!document.getElementById(id),a); if(!has) bad.push(`${pg}: dead anchor #${a}`); }
  for(const im of r.imgs){ if(!im.a) bad.push(`${pg}: img no alt ${im.s.slice(0,40)}`);
    if(im.w===0&&!im.s.startsWith('data:')) bad.push(`${pg}: image failed to load ${im.s.slice(0,50)}`); }
  for(const v of r.videos) if(!fs.existsSync(''+process.cwd()+'/'+v)) bad.push(`${pg}: missing video ${v}`);
  if(seenTitles.has(r.title)) bad.push(`${pg}: title duplicates ${seenTitles.get(r.title)}`); else seenTitles.set(r.title,pg);
  if(r.desc && seenDesc.has(r.desc)) bad.push(`${pg}: meta desc duplicates ${seenDesc.get(r.desc)}`); else if(r.desc) seenDesc.set(r.desc,pg);
 }
 if(missingAssets.size) bad.push('MISSING ASSETS: '+[...missingAssets].join(', '));
 console.log(bad.length?bad.join('\n'):'PASS — deep checks clean');
 await b.close();
})();
