#!/usr/bin/env python3
"""Bundle site_v1/*.html into one self-contained Artifact preview page.

Every page becomes a JS string in PAGES{} and is rendered into an iframe via
srcdoc. Internal .html links are intercepted and routed by postMessage.
Navigation is a floating dock (bottom-left), NOT a top tab bar — the site has
its own header, and a second bar on top of it reads as two menus.

Run:  python3 /root/work/bundle.py
Out:  /root/work/artifact_site_preview.html
"""
import base64, json, mimetypes, os, re

SRC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(SRC, 'preview.html')

PAGES = [
    ('home',         'index.html',        'Home'),
    ('for-brands',   'for-brands.html',   'For Brands'),
    ('for-teams',    'for-teams.html',    'For Teams'),
    ('what-we-make', 'what-we-make.html', 'What we make'),
    ('our-factory',  'our-factory.html',  'Production house'),
    ('how-it-works', 'how-it-works.html', 'How it works'),
    ('pricing',      'pricing.html',      'Pricing'),
    ('faq',          'faq.html',          'FAQ'),
    ('compliance',   'compliance.html',   'Compliance'),
    ('about',        'about.html',        'About'),
    ('contact',      'contact.html',      'Contact & story'),
    ('quote',        'quote.html',        'Quote'),
]

MAX_INLINE = 5_000_000  # never base64 a large binary into the preview
_cache = {}
def data_uri(rel):
    if rel in _cache:
        return _cache[rel]
    p = os.path.join(SRC, rel)
    if not os.path.isfile(p):
        return rel
    if os.path.getsize(p) > MAX_INLINE:
        return rel  # left as a relative link; served normally on the real host
    mt = mimetypes.guess_type(p)[0] or 'application/octet-stream'
    b = base64.b64encode(open(p, 'rb').read()).decode()
    u = 'data:%s;base64,%s' % (mt, b)
    _cache[rel] = u
    return u

INTERCEPT = ("<script>document.addEventListener('click',function(e){var a=e.target.closest('a');"
             "if(!a)return;var h=a.getAttribute('href')||'';"
             "if(h.endsWith('.html')){e.preventDefault();"
             "parent.postMessage({go:h.replace('.html','').replace('index','home')},'*');return;}"
             "if(/^https?:/i.test(h)){e.preventDefault();parent.postMessage({open:h},'*');}"
             "},true);</script>")

def prep(fn):
    s = open(os.path.join(SRC, fn), encoding='utf-8').read()
    # inline local assets referenced in src="" / href="" / url()
    s = re.sub(r'(?:src|href)="(assets/[^"]+)"',
               lambda m: m.group(0).replace(m.group(1), data_uri(m.group(1))), s)
    s = re.sub(r'url\((assets/[^)\'"]+)\)',
               lambda m: 'url(%s)' % data_uri(m.group(1)), s)
    s = s.replace('</body>', INTERCEPT + '</body>') if '</body>' in s else s + INTERCEPT
    return s

pages = {k: prep(fn) for k, fn, _ in PAGES}
labels = {k: lb for k, _, lb in PAGES}
menu = ''.join('<button role="option" data-p="%s">%s</button>' % (k, lb) for k, _, lb in PAGES)

SHELL = """<title>7th Apparel Website</title>
<style>
:root{--deep:#17102E;--purple:#2C2153;--lilac:#A88FD8;--pale:#C9B8EE;--gold:#E0A83C;--bone:#F4F0FA}
*{box-sizing:border-box}
html,body{height:100%%}
body{margin:0;background:var(--deep);font-family:'IBM Plex Mono',ui-monospace,Menlo,monospace}
.frame{border:0;width:100%%;height:100%%;display:block;background:var(--bone)}
.dock{position:fixed;left:16px;bottom:16px;z-index:50;font-size:11px;letter-spacing:.05em}
.toggle{display:flex;align-items:center;gap:8px;background:rgba(28,20,58,.92);backdrop-filter:blur(12px);border:1px solid rgba(168,143,216,.34);color:var(--pale);border-radius:999px;padding:8px 14px 8px 10px;cursor:pointer;font:inherit;box-shadow:0 10px 30px rgba(0,0,0,.4)}
.toggle:hover{border-color:var(--gold);color:var(--gold)}
.toggle svg{height:18px;width:auto}
.toggle b{color:#fff;font-weight:600}
.menu{display:none;flex-direction:column;gap:2px;margin-bottom:8px;background:rgba(28,20,58,.97);backdrop-filter:blur(14px);border:1px solid rgba(168,143,216,.34);border-radius:12px;padding:8px;box-shadow:0 18px 44px rgba(0,0,0,.5);max-height:66vh;overflow:auto}
.dock.open .menu{display:flex}
.menu button{font:inherit;text-align:left;background:transparent;border:0;color:var(--pale);border-radius:7px;padding:8px 12px;cursor:pointer;white-space:nowrap}
.menu button:hover{background:rgba(168,143,216,.16);color:#fff}
.menu button[aria-current="true"]{background:var(--gold);color:#1B1338;font-weight:600}
.menu .hd{color:var(--lilac);opacity:.75;padding:4px 12px 8px;font-size:10px;border-bottom:1px solid rgba(168,143,216,.2);margin-bottom:4px}
.toggle:focus-visible,.menu button:focus-visible{outline:2px solid var(--gold);outline-offset:2px}
@media (max-width:640px){.dock{left:10px;bottom:10px}}
</style>
<iframe class="frame" id="f" title="7th Apparel website preview"></iframe>
<div class="dock" id="dock">
  <div class="menu" id="menu" role="listbox" aria-label="Pages"><div class="hd">DRAFT PREVIEW &middot; NOT LIVE ON 7THAPPAREL.COM</div>%(menu)s</div>
  <button class="toggle" id="tg" aria-expanded="false"><svg viewBox="0 0 100 100" fill="none" aria-hidden="true"><path d="M12 16 H88 L44 92" stroke="#A88FD8" stroke-width="12" stroke-linecap="round" stroke-linejoin="round"/><line x1="8" y1="60" x2="76" y2="60" stroke="#E0A83C" stroke-width="4" stroke-linecap="round"/></svg><span>Preview &middot; <b id="cur">Home</b></span></button>
</div>
<script>
var PAGES=%(pages)s;
var LABELS=%(labels)s;
var f=document.getElementById('f'),dock=document.getElementById('dock'),tg=document.getElementById('tg'),cur=document.getElementById('cur');
function go(k){
  if(!PAGES[k])k='home';
  f.srcdoc=PAGES[k]; cur.textContent=LABELS[k];
  document.querySelectorAll('.menu button').forEach(function(b){b.setAttribute('aria-current',b.dataset.p===k?'true':'false');});
  dock.classList.remove('open'); tg.setAttribute('aria-expanded','false');
  try{history.replaceState(null,'','#'+k);}catch(e){}
}
tg.addEventListener('click',function(){var o=dock.classList.toggle('open');tg.setAttribute('aria-expanded',o?'true':'false');});
document.querySelectorAll('.menu button').forEach(function(b){if(b.dataset.p)b.addEventListener('click',function(){go(b.dataset.p);});});
document.addEventListener('click',function(e){if(!dock.contains(e.target))dock.classList.remove('open');});
document.addEventListener('keydown',function(e){if(e.key==='Escape')dock.classList.remove('open');});
window.addEventListener('message',function(e){
  if(!e.data)return;
  if(e.data.go){go(e.data.go);return;}
  if(e.data.open&&/^https?:/i.test(e.data.open)){window.open(e.data.open,'_blank','noopener');}
});
go((location.hash||'#home').slice(1));
</script>
"""

html = SHELL % {
    'menu': menu,
    'pages': json.dumps(pages).replace('</', '<\\/'),
    'labels': json.dumps(labels),
}
open(OUT, 'w', encoding='utf-8').write(html)
print('MB: %.2f  pages: %d' % (len(html) / 1048576, len(pages)))
