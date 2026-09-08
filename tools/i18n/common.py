# -*- coding: utf-8 -*-
"""Shared pieces for the multilingual build: URLs, switcher markup, CSS, scripts."""
import re

SITE   = "https://7thapparel.com"
LANGS  = ["nl","de","pl","fr"]
ALL    = ["en"] + LANGS
PAGES  = ["index","about","compliance","contact","faq","for-brands","for-teams",
          "how-it-works","our-factory","our-story","pricing","quote",
          "what-we-make","workwear"]
CODE   = {"en":"EN","nl":"NL","de":"DE","pl":"PL","fr":"FR"}
OGLOC  = {"en":"en_GB","nl":"nl_NL","de":"de_DE","pl":"pl_PL","fr":"fr_FR"}
ARIA   = {"en":"Language","nl":"Taal","de":"Sprache","pl":"Język","fr":"Langue"}
# Banner: [sentence, call to action, dismiss]
HINT = {
 "nl":["Deze site is ook in het Nederlands beschikbaar.","Naar het Nederlands","Nee, dank u"],
 "de":["Diese Seite gibt es auch auf Deutsch.","Auf Deutsch ansehen","Nein, danke"],
 "pl":["Ta strona jest dostępna także po polsku.","Przejdź na polski","Nie, dziękuję"],
 "fr":["Ce site est aussi disponible en français.","Voir en français","Non merci"],
}

def path(lang, page):
    slug = "" if page == "index" else page
    return ("/" + slug) if lang == "en" else "/%s/%s" % (lang, slug)

def canonical(lang, page):
    return SITE + path(lang, page)

# ---------------------------------------------------------------- head links
def head_links(lang, page):
    out = []
    for l in ALL:
        out.append('<link rel="alternate" hreflang="%s" href="%s">' % (l, canonical(l, page)))
    out.append('<link rel="alternate" hreflang="x-default" href="%s">' % canonical("en", page))
    return "".join(out)

# ---------------------------------------------------------------- switcher
def switcher(lang, page):
    opts = "".join(
        '<option value="%s" data-l="%s"%s>%s</option>'
        % (path(l, page), l, " selected" if l == lang else "", CODE[l])
        for l in ALL)
    return ('<div class="langwrap"><select class="langsel" id="langsel" aria-label="%s">'
            '%s</select></div>' % (ARIA[lang], opts))

# ---------------------------------------------------------------- css
def _chev(stroke):
    return ("url(\"data:image/svg+xml;charset=UTF-8,%3Csvg xmlns='http://www.w3.org/2000/svg'"
            " viewBox='0 0 10 6'%3E%3Cpath d='M1 1l4 4 4-4' fill='none' stroke='" + stroke +
            "' stroke-width='1.7' stroke-linecap='round' stroke-linejoin='round'/%3E%3C/svg%3E\")")

def css(dark_header):
    fg, bd, chev = ("#E6DDF8", "rgba(200,184,238,.42)", _chev("%23C9B8EE")) if dark_header \
              else ("#2C2153", "#cfc4e8",               _chev("%232C2153"))
    return """
/*i18n-start*/
/* ---- language switcher (added by tools/i18n/build.py) ---- */
.langwrap{flex:0 0 auto;display:flex;align-items:center}
.langsel{appearance:none;-webkit-appearance:none;-moz-appearance:none;
 background-color:transparent;background-image:%s;background-repeat:no-repeat;
 background-position:right 8px center;background-size:9px 6px;
 border:1.5px solid %s;border-radius:8px;color:%s;
 font:600 13px/1 'Inter',system-ui,-apple-system,sans-serif;letter-spacing:.03em;
 padding:11px 25px 11px 10px;min-height:42px;cursor:pointer}
.langsel:hover{border-color:%s}
.langsel option{color:#2C2153;background:#fff;font-weight:500;letter-spacing:0}
@media(max-width:430px){.langsel{font-size:12px;padding:10px 21px 10px 8px;min-height:40px;
 background-position:right 6px center}}
@media print{.langwrap{display:none}}
/* ---- "this page exists in your language" hint ---- */
.langhint{position:fixed;left:16px;bottom:16px;z-index:88;max-width:340px;display:none;
 background:#2C2153;color:#F4F0FA;border:1px solid rgba(200,184,238,.35);border-radius:12px;
 padding:14px 16px;font:400 14.5px/1.45 'Inter',system-ui,-apple-system,sans-serif;
 box-shadow:0 16px 42px rgba(0,0,0,.32)}
.langhint.show{display:block}
.langhint a{color:#E0A83C;font-weight:600;text-decoration:underline;text-underline-offset:2px}
.langhint button{background:none;border:0;color:#C9B8EE;font:inherit;cursor:pointer;
 text-decoration:underline;text-underline-offset:2px;padding:0;margin-left:12px}
.langhint p{margin:0 0 9px}
@media(max-width:820px){.langhint{left:14px;right:84px;bottom:14px;max-width:none}}
/*i18n-end*/
""" % (chev, bd, fg, fg)

# ---------------------------------------------------------------- scripts
# Runs in <head> on English pages only, before anything paints, so there is no flash.
def detect_script(page):
    return ("<script data-i18n=\"1\">(function(){try{var S={nl:1,de:1,pl:1,fr:1},p=location.pathname;"
            "if(/^\\/(nl|de|pl|fr)(\\/|$)/.test(p))return;"
            "if(/[?&]lang=/.test(location.search))return;"
            "var s=null;try{s=localStorage.getItem('7a_lang')}catch(e){}"
            "var k=null;"
            "if(s){if(s==='en')return;if(S[s])k=s}"
            "else{var L=navigator.languages||[navigator.language||''];"
            "for(var i=0;i<L.length;i++){var c=(L[i]||'').slice(0,2).toLowerCase();"
            "if(c==='en')break;if(S[c]){k=c;break}}}"
            "if(!k)return;var r=p.replace(/\\/index\\.html$/,'/').replace(/\\.html$/,'');"
            "r=(r==='/')?'':r.replace(/^\\//,'');"
            "location.replace('/'+k+'/'+r+location.search+location.hash)}catch(e){}})();</script>")

def switch_script():
    return ("<script data-i18n=\"1\">(function(){var s=document.getElementById('langsel');if(!s)return;"
            "s.addEventListener('change',function(){var o=s.options[s.selectedIndex];"
            "try{localStorage.setItem('7a_lang',o.getAttribute('data-l'))}catch(e){}"
            "location.href=s.value})})();</script>")

def hint_script(page):
    import json
    urls = {l: path(l, page) for l in LANGS}
    return ("<script data-i18n=\"1\">(function(){try{"
            "if(/^\\/(nl|de|pl|fr)(\\/|$)/.test(location.pathname))return;"
            "var s=null;try{s=localStorage.getItem('7a_lang')}catch(e){}if(s)return;"
            "var S={nl:1,de:1,pl:1,fr:1},L=navigator.languages||[navigator.language||''];"
            "for(var i=0;i<L.length;i++){if(S[(L[i]||'').slice(0,2).toLowerCase()])return}"
            "var M={NL:'nl',BE:'nl',DE:'de',AT:'de',CH:'de',PL:'pl',FR:'fr',LU:'fr',MC:'fr'},"
            "T=%s,U=%s;"
            "fetch('/cdn-cgi/trace',{cache:'no-store'}).then(function(r){return r.text()})"
            ".then(function(t){var m=/(?:^|\\n)loc=([A-Z]{2})/.exec(t);if(!m)return;"
            "var l=M[m[1]];if(!l)return;var e=document.getElementById('langhint');if(!e)return;"
            "e.innerHTML='<p>'+T[l][0]+'</p><a href=\"'+U[l]+'\" id=\"langgo\">'+T[l][1]"
            "+'</a><button type=\"button\" id=\"langno\">'+T[l][2]+'</button>';"
            "document.getElementById('langgo').addEventListener('click',function(){"
            "try{localStorage.setItem('7a_lang',l)}catch(x){}});"
            "document.getElementById('langno').addEventListener('click',function(){"
            "try{localStorage.setItem('7a_lang','en')}catch(x){}e.classList.remove('show')});"
            "e.classList.add('show')}).catch(function(){})}catch(e){}})();</script>"
            % (json.dumps(HINT, ensure_ascii=False), json.dumps(urls)))

HINT_EL = '<div class="langhint" id="langhint"></div>'

# ---------------------------------------------------------------- svg case
SVG_CASE = ["viewBox","preserveAspectRatio","linearGradient","radialGradient","clipPath",
            "gradientUnits","gradientTransform","patternUnits","patternTransform",
            "spreadMethod","stopColor","stopOpacity","textLength","lengthAdjust",
            "baseFrequency","numOctaves","stdDeviation","feGaussianBlur","feOffset",
            "feBlend","feColorMatrix","feComposite","feFlood","feMerge","feMergeNode",
            "feMorphology","feTurbulence","markerWidth","markerHeight","refX","refY",
            "maskUnits","maskContentUnits","clipPathUnits","primitiveUnits",
            "startOffset","pathLength","requiredExtensions","systemLanguage",
            "diffuseConstant","surfaceScale","specularConstant","specularExponent",
            "kernelMatrix","xChannelSelector","yChannelSelector","attributeName",
            "repeatCount","keyTimes","keySplines","calcMode","baseProfile"]

def restore_svg_case(html):
    """bs4's html.parser lowercases SVG names; browsers mostly fix this, but not always."""
    for name in SVG_CASE:
        html = re.sub(r"(?<=[\s<])%s(?=[\s=>/])" % name.lower(), name, html)
    return html
