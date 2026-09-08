# -*- coding: utf-8 -*-
"""Generate /nl /de /pl /fr from the English pages, and add the switcher,
hreflang tags and language detection to every page including English.

Run from the repo root:  python3 tools/i18n/build.py
"""
import json, os, re, sys, shutil
from bs4 import BeautifulSoup, NavigableString, Comment, Doctype
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common as C
from common import PAGES, LANGS, ALL

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))

# ---- the same traversal extract.py uses, so the keys line up ---------------
INLINE = {"a","em","strong","b","i","span","br","small","sup","sub","u","abbr",
          "mark","time","s","del","ins","cite","q","wbr","big","tt","font","label"}
NO_RECURSE = {"script","style","noscript","code","pre","svg","canvas","iframe","head"}
VOID = {"img","input","br","hr","source","track","link","meta","area","col","embed"}
ATTRS = {
    "img": ["alt"], "a": ["title","aria-label"],
    "input": ["placeholder","aria-label","title"],
    "textarea": ["placeholder","aria-label"],
    "select": ["aria-label"], "button": ["aria-label","title"],
    "option": ["label"], "div": ["aria-label","title"],
    "section": ["aria-label"], "nav": ["aria-label"], "form": ["aria-label"],
    "abbr": ["title"], "th": ["title"], "video": ["aria-label"],
}
META_TRANSLATE = {"description","og:title","og:description",
                  "twitter:title","twitter:description"}

import hashlib
def key(s): return hashlib.sha1(s.strip().encode("utf-8")).hexdigest()[:12]
def all_inline(el): return all(d.name.lower() in INLINE for d in el.find_all(True))
def inner(el): return "".join(str(c) for c in el.contents)

# ---- French typography: nbsp before ; : ? ! and inside guillemets ----------
def fr_spaces(html):
    out, i = [], 0
    for m in re.finditer(r"<[^>]*>", html):
        out.append(_fr(html[i:m.start()])); out.append(m.group(0)); i = m.end()
    out.append(_fr(html[i:]))
    return "".join(out)
def _fr(t):
    t = re.sub(r" +([;:?!])", " \\1", t)
    t = re.sub(r"«\s+", "« ", t)
    t = re.sub(r"\s+»", " »", t)
    return t

class Missing(Exception): pass

SOURCE = {}

def build_page(page, lang, tr, stats):
    soup = BeautifulSoup(SOURCE[page], "html.parser")

    def T(s, ctx):
        k = key(s)
        if k not in tr:
            stats["missing"].append((page, ctx, s[:60])); return s
        v = tr[k]
        return fr_spaces(v) if lang == "fr" else v

    # <title> and meta
    if soup.title and soup.title.string:
        soup.title.string.replace_with(T(soup.title.string.strip(), "title"))
    for m in soup.find_all("meta"):
        n = (m.get("name") or m.get("property") or "").lower()
        if n in META_TRANSLATE and m.get("content"):
            m["content"] = T(m["content"].strip(), "meta:"+n)

    def walk(el):
        for child in list(el.children):
            if isinstance(child, (Comment, Doctype)): continue
            if isinstance(child, NavigableString):
                s = str(child)
                if s.strip() and re.search(r"[A-Za-z]{2}", s):
                    k = key(s)
                    if k in tr: child.replace_with(NavigableString(
                        s.replace(s.strip(), (fr_spaces(tr[k]) if lang=="fr" else tr[k]))))
                continue
            name = child.name.lower()
            if name in NO_RECURSE: continue
            if name in VOID:
                for a in ATTRS.get(name, []):
                    if child.get(a): child[a] = T(child[a].strip(), name+"@"+a)
                continue
            for a in ATTRS.get(name, []):
                if child.get(a): child[a] = T(child[a].strip(), name+"@"+a)
            if child.get("id") == "heroline":
                rebuild_hero(child, lang, T); continue
            if child.get_text(strip=True) and all_inline(child):
                k = key(inner(child))
                if k in tr:
                    frag = BeautifulSoup(fr_spaces(tr[k]) if lang=="fr" else tr[k], "html.parser")
                    child.clear()
                    for node in list(frag.contents): child.append(node)
                else:
                    stats["missing"].append((page, "html", inner(child)[:60]))
            else:
                walk(child)
    walk(soup.body or soup)

    # readable copy inside inline SVG
    for t in soup.select("svg text, svg tspan, svg title, svg desc"):
        if t.get_text(strip=True):
            k = key(inner(t))
            if k in tr:
                frag = BeautifulSoup(tr[k], "html.parser")
                t.clear()
                for node in list(frag.contents): t.append(node)
    return soup

HERO_EM = {   # which word indices carry <em>
 "en": (2, 6), "nl": (2, 7), "de": (2, 5), "pl": (1, 5), "fr": (2, 7),
}
def rebuild_hero(h1, lang, T):
    """The hero is one <span class="w"> per word, so it has to be rebuilt, not
    replaced word by word — word order and word count both change."""
    line = T(h1.get_text(" ", strip=True).replace(" ", " "), "heroline")
    words = line.split()
    em = set(HERO_EM.get(lang, ()))
    h1.clear()
    soup = BeautifulSoup("", "html.parser")
    for i, w in enumerate(words):
        outer = soup.new_tag("span"); outer["class"] = "w"
        insp = soup.new_tag("span")
        if i in em:
            e = soup.new_tag("em"); e.string = w; insp.append(e)
        else:
            insp.string = w
        if i < len(words) - 1: insp.append(NavigableString(" "))
        outer.append(insp); h1.append(outer)

# ---- string-level rewrites on the serialised page --------------------------
def absolutise_assets(html):
    html = re.sub(r'((?:src|href|poster|data-src)=")assets/', r"\1/assets/", html)
    html = re.sub(r'(srcset="[^"]*?)(?<![/\w])assets/', r"\1/assets/", html)
    html = re.sub(r"url\((['\"]?)assets/", r"url(\1/assets/", html)
    return html

def prefix_links(html, lang):
    if lang == "en": return html
    def rep(m):
        a, p = m.group(1), m.group(2)
        if p.startswith("/assets/") or p.startswith("//"): return m.group(0)
        return '%s="/%s%s"' % (a, lang, "" if p == "/" else p)
    return re.sub(r'(href|action)="(/[^"]*)"', rep, html)

def strip_i18n(html):
    """Remove anything a previous run of this script added, so it is re-runnable."""
    html = re.sub(r"/\*i18n-start\*/.*?/\*i18n-end\*/", "", html, flags=re.S)
    html = re.sub(r'<div class="langwrap">.*?</div>', "", html, flags=re.S)
    html = html.replace('<div class="langhint" id="langhint"></div>', "")
    html = re.sub(r'<script data-i18n="1">.*?</script>', "", html, flags=re.S)
    html = re.sub(r'<link rel="alternate" hreflang="[^"]*" href="[^"]*">', "", html)
    return html


def put_attr(html, tag_re, attr, value, required=False, where=""):
    """Set one attribute on the first tag matching tag_re, whatever order its
    attributes are in — bs4 re-orders them alphabetically on output."""
    m = re.search(tag_re, html)
    if not m:
        if required: raise Missing("no %s in %s" % (tag_re, where))
        return html
    tag = m.group(0)
    if re.search(r'\b%s="' % attr, tag):
        tag = re.sub(r'(\b%s=")[^"]*(")' % attr,
                     lambda mm: mm.group(1) + value + mm.group(2), tag, count=1)
    else:
        tag = tag[:-1].rstrip("/") + ' %s="%s">' % (attr, value)
    return html[:m.start()] + tag + html[m.end():]


def set_head(html, lang, page, dark):
    url = C.canonical(lang, page)
    html = re.sub(r'<html\b[^>]*\blang="[^"]*"', '<html lang="%s"' % lang, html, count=1)
    html = put_attr(html, r'<link\b[^>]*\brel="canonical"[^>]*>', "href", url,
                    required=True, where="%s/%s" % (lang, page))
    html = put_attr(html, r'<meta\b[^>]*\bproperty="og:url"[^>]*>', "content", url)
    if re.search(r'<meta\b[^>]*\bproperty="og:locale"[^>]*>', html):
        html = put_attr(html, r'<meta\b[^>]*\bproperty="og:locale"[^>]*>',
                        "content", C.OGLOC[lang])
    else:
        html = html.replace("</head>",
              '<meta property="og:locale" content="%s"></head>' % C.OGLOC[lang], 1)
    html = re.sub(r'<link rel="alternate" hreflang="[^"]*" href="[^"]*">', "", html)
    html = html.replace("</head>", C.head_links(lang, page) + "</head>", 1)
    html = html.replace("</style>", C.css(dark, lang) + "</style>", 1)
    if lang == "en":
        html = html.replace("</head>", C.detect_script(page) + "</head>", 1)
    return html


def shorten_nav(html, lang):
    """Swap in short nav labels inside <ul id="navlist"> only."""
    short = C.NAV_SHORT.get(lang)
    if not short: return html
    m = re.search(r'<ul id="navlist">.*?</ul>', html, re.S)
    if not m: raise Missing("no navlist for " + lang)
    block = m.group(0)
    for href, label in short.items():
        pat = r'(<a href="/%s%s"[^>]*>)[^<]*(</a>)' % (lang, href)
        block, n = re.subn(pat, lambda mm: mm.group(1) + label + mm.group(2), block)
        if not n: raise Missing("nav label %s not found for %s" % (href, lang))
    return html[:m.start()] + block + html[m.end():]


def set_body(html, lang, page):
    html = shorten_nav(html, lang)
    sw = C.switcher(lang, page)
    m = re.search(r'<a class="btn" href="[^"]*quote"[^>]*>(.*?)</a>', html, re.S)
    if not m: raise Missing("no nav CTA on %s/%s" % (lang, page))
    label = m.group(1)
    cta = (html[m.start():m.start(1)]
           + '<span class="ctaLong">%s</span><span class="ctaShort">%s</span>'
             % (label, C.CTA_SHORT[lang]) + "</a>")
    html = html[:m.start()] + sw + cta + html[m.end():]
    tail = C.switch_script()
    if lang == "en":
        tail = C.HINT_EL + tail + C.hint_script(page)
    return html.replace("</body>", tail + "</body>", 1)

def main():
    os.chdir(ROOT)
    for page in PAGES:
        SOURCE[page] = strip_i18n(open(page + ".html", encoding="utf-8").read())
    stats = {"missing": [], "written": []}
    for lang in ALL:
        tr = {} if lang == "en" else json.load(
            open(os.path.join(HERE, lang + ".json"), encoding="utf-8"))
        if lang != "en":
            os.makedirs(os.path.join(ROOT, lang), exist_ok=True)
        for page in PAGES:
            dark = (page == "index")
            if lang == "en":
                html = SOURCE[page]
            else:
                html = C.restore_svg_case(str(build_page(page, lang, tr, stats)))
                html = absolutise_assets(html)
                html = prefix_links(html, lang)
            html = set_head(html, lang, page, dark)
            html = set_body(html, lang, page)
            out = (page + ".html") if lang == "en" else os.path.join(lang, page + ".html")
            open(out, "w", encoding="utf-8").write(html)
            stats["written"].append(out)
    print("pages written:", len(stats["written"]))
    if stats["missing"]:
        print("MISSING TRANSLATIONS:", len(stats["missing"]))
        for row in stats["missing"][:25]: print("  ", row)
    else:
        print("no missing translations")

if __name__ == "__main__":
    main()
