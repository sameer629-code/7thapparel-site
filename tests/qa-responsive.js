const { chromium } = require('playwright');
const fs=require('fs');
const GS=fs.readFileSync('node_modules/gsap/dist/gsap.min.js','utf8');
const ST=fs.readFileSync('node_modules/gsap/dist/ScrollTrigger.min.js','utf8');
const PAGES=['index','for-brands','for-teams','what-we-make','workwear','our-factory','how-it-works','pricing','faq','compliance','about','contact','quote'];
const VPS=[{w:1920,h:1080,n:'xl'},{w:1440,h:900,n:'desk'},{w:1280,h:800,n:'lap'},{w:1024,h:768,n:'sm'},{w:768,h:1024,n:'tab'},{w:390,h:844,n:'phone'},{w:320,h:568,n:'tiny'}];
(async()=>{
 const b=await chromium.launch();
 const bad=[];
 for(const vp of VPS){
  const p=await b.newPage({viewport:{width:vp.w,height:vp.h}});
  await p.route('**/gsap.min.js',r=>r.fulfill({contentType:'application/javascript',body:GS}));
  await p.route('**/ScrollTrigger.min.js',r=>r.fulfill({contentType:'application/javascript',body:ST}));
  await p.route('**/fonts.googleapis.com/**',r=>r.abort());
  p.on('pageerror',e=>bad.push(`${vp.n} JSERR ${e.message.slice(0,70)}`));
  for(const pg of PAGES){
   await p.goto('file://'+process.cwd()+'/'+pg+'.html',{waitUntil:'domcontentloaded'});
   await p.waitForTimeout(pg==='index'?2400:800);
   const r=await p.evaluate(()=>{
    const out={};
    out.ovf=document.documentElement.scrollWidth-window.innerWidth;
    // header integrity
    const lg=document.querySelector('nav .logo'), ul=document.querySelector('#navlist'),
          cta=document.querySelector('nav>a.btn'), bur=document.getElementById('burger');
    const R=e=>e?e.getBoundingClientRect():null;
    const l=R(lg),u=R(ul),c=R(cta);
    const navVisible=ul&&getComputedStyle(ul).display!=='none';
    out.hdrOverlap = (navVisible&&l&&u)? Math.round(l.right-u.left) : null;
    out.ctaClipped = c? Math.round(c.right)>window.innerWidth+1 : null;
    out.burgerShown = bur? getComputedStyle(bur).display!=='none' : false;
    out.navShown = navVisible;
    // generic element collisions in the header band
    out.imgNoAlt=[...document.querySelectorAll('img')].filter(i=>!i.getAttribute('alt')).length;
    out.emptyLinks=[...document.querySelectorAll('a')].filter(a=>!a.textContent.trim()&&!a.querySelector('img,svg')&&!a.getAttribute('aria-label')).length;
    out.h1=document.querySelectorAll('h1').length;
    out.tinyTap=[...document.querySelectorAll('a,button')].filter(e=>{const r=e.getBoundingClientRect();return r.width>0&&r.height>0&&r.height<32;}).length;
    out.placeholder=/\[number\]|lorem ipsum|TODO|FIXME|XXX|undefined|NaN/i.test(document.body.innerText);
    // contrast-ish: any text that is the same colour as its background
    out.badLinks=[...document.querySelectorAll('a[href]')].map(a=>a.getAttribute('href')).filter(h=>h&&(h==='#'||h===''||h.startsWith('javascript:'))).length;
    return out;
   });
   const tag=`${vp.n} ${pg}`;
   if(r.ovf>2) bad.push(`${tag}: H-OVERFLOW ${r.ovf}px`);
   if(r.hdrOverlap!==null && r.hdrOverlap>0) bad.push(`${tag}: HEADER OVERLAP ${r.hdrOverlap}px`);
   if(r.ctaClipped) bad.push(`${tag}: CTA clipped off-screen`);
   if(r.navShown && r.burgerShown) bad.push(`${tag}: nav AND burger both visible`);
   if(!r.navShown && !r.burgerShown) bad.push(`${tag}: no navigation at all`);
   if(r.imgNoAlt) bad.push(`${tag}: ${r.imgNoAlt} img missing alt`);
   if(r.emptyLinks) bad.push(`${tag}: ${r.emptyLinks} empty link`);
   if(r.h1!==1) bad.push(`${tag}: ${r.h1} h1 (want 1)`);
   if(r.placeholder) bad.push(`${tag}: PLACEHOLDER TEXT`);
   if(r.badLinks) bad.push(`${tag}: ${r.badLinks} dead href`);
   if(vp.n==='phone'&&r.tinyTap>0) bad.push(`${tag}: ${r.tinyTap} tap target <32px`);
  }
  await p.close();
 }
 console.log(bad.length?bad.join('\n'):'PASS — no issues');
 console.log('checks:',PAGES.length*VPS.length,'page/viewport combinations');
 await b.close();
})();
