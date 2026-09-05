const { chromium } = require('playwright');
(async()=>{
 const b=await chromium.launch();
 const ctx=await b.newContext({viewport:{width:1280,height:900}});
 const p=await ctx.newPage();
 await p.route('**/cdnjs.cloudflare.com/**',r=>r.abort());
 await p.route('**/fonts.googleapis.com/**',r=>r.abort());
 const ok=[],fail=[];
 const t=(n,c)=>c?ok.push(n):fail.push(n);

 // 1 form: validation + success
 let posted=null;
 await p.route('**/formsubmit.co/**',r=>{posted=r.request().postData();r.fulfill({status:200,contentType:'application/json',body:JSON.stringify({success:'true'})});});
 await p.goto('file://'+process.cwd()+'/quote.html'); await p.waitForTimeout(500);
 await p.click('button[type=submit]'); await p.waitForTimeout(200);
 t('form blocks empty submit', await p.evaluate(()=>!document.getElementById('ferr').hidden));
 await p.fill('#q-name','QA'); await p.fill('#q-email','qa@test.com'); await p.check('#q-gdpr');
 await p.click('button[type=submit]'); await p.waitForTimeout(900);
 t('form submits + posts', !!posted && posted.includes('qa@test.com'));
 t('form shows success', await p.evaluate(()=>!document.getElementById('fok').hidden));
 t('form clears after send', await p.evaluate(()=>document.getElementById('q-name').value===''));

 // 2 catalogue browser
 await p.goto('file://'+process.cwd()+'/workwear.html'); await p.waitForTimeout(700);
 await p.click('#cnext'); await p.waitForTimeout(300);
 t('catalogue next', await p.evaluate(()=>document.getElementById('ccount').textContent==='PAGE 2 OF 26'));
 await p.click('.cthumb[data-i="20"]'); await p.waitForTimeout(300);
 t('catalogue thumb jump', await p.evaluate(()=>document.getElementById('ccount').textContent==='PAGE 20 OF 26'));
 await p.click('#cprev'); await p.waitForTimeout(300);
 t('catalogue prev', await p.evaluate(()=>document.getElementById('ccount').textContent==='PAGE 19 OF 26'));

 // 3 mobile menu on every page
 const m=await ctx.newPage(); await m.setViewportSize({width:390,height:844});
 await m.route('**/cdnjs.cloudflare.com/**',r=>r.abort());
 await m.route('**/fonts.googleapis.com/**',r=>r.abort());
 let menuOk=true;
 for(const pg of ['index','pricing','faq','contact','workwear','quote']){
  await m.goto('file://'+process.cwd()+'/'+pg+'.html'); await m.waitForTimeout(pg==='index'?1800:500);
  await m.click('#burger'); await m.waitForTimeout(350);
  const n=await m.evaluate(()=>document.querySelectorAll('#navlist.open a').length);
  if(n<8) { menuOk=false; fail.push('menu on '+pg+' -> '+n+' links'); }
 }
 t('mobile menu opens on all pages', menuOk);

 // 4 anchor link
 const ap=await ctx.newPage();
 await ap.route('**/cdnjs.cloudflare.com/**',r=>r.abort());
 await ap.route('**/fonts.googleapis.com/**',r=>r.abort());
 await ap.goto('file://'+process.cwd()+'/index.html'); await ap.waitForTimeout(2600);
 const y0=await ap.evaluate(()=>window.scrollY);
 await ap.click('a[href="#flow"]'); await ap.waitForTimeout(1400);
 const y1=await ap.evaluate(()=>window.scrollY);
 t('#flow anchor scrolls ('+y0+'->'+y1+')', y1>y0+300);
 await ap.close();

 // 5 external link opens new tab, has rel
 t('external links safe', await p.evaluate(()=>[...document.querySelectorAll('a[href^="http"][target="_blank"]')].every(a=>(a.getAttribute('rel')||'').includes('noopener'))));

 // 6 video present with poster
 await p.goto('file://'+process.cwd()+'/what-we-make.html'); await p.waitForTimeout(600);
 t('reel has source + poster', await p.evaluate(()=>{const v=document.getElementById('reelv');
   return !!v && !!v.getAttribute('poster') && !!v.querySelector('source[src$=".mp4"]');}));

 // 7 no page relies on JS for its core copy
 const nj=await b.newContext({viewport:{width:1280,height:900},javaScriptEnabled:false});
 const np=await nj.newPage();
 await np.route('**/cdnjs.cloudflare.com/**',r=>r.abort());
 await np.route('**/fonts.googleapis.com/**',r=>r.abort());
 await np.goto('file://'+process.cwd()+'/index.html'); await np.waitForTimeout(500);
 const noJs=await np.evaluate(()=>document.body.innerText.replace(/\s+/g,' ').trim().length);
 t('homepage readable without JS ('+noJs+' chars)', noJs>3000);
 await nj.close();

 console.log('PASS ('+ok.length+'):'); ok.forEach(x=>console.log('  ✓',x));
 if(fail.length){console.log('FAIL ('+fail.length+'):'); fail.forEach(x=>console.log('  ✗',x));}
 await b.close();
})();
