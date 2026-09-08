# -*- coding: utf-8 -*-
"""Pull translatable segments out of the English pages.

A segment is a whole *phrase*, not a text node: any element whose children are
all inline is emitted as one unit with its inline markup intact, so a translator
sees a complete sentence and can move <em>/<a> to wherever the target language
needs them. Word-by-word extraction would produce nonsense in German or Polish.
"""
import json, re, os, hashlib, sys
from bs4 import BeautifulSoup, NavigableString, Comment, Doctype

PAGES = ["index","about","compliance","contact","faq","for-brands","for-teams",
         "how-it-works","our-factory","our-story","pricing","quote",
         "what-we-make","workwear"]

INLINE = {"a","em","strong","b","i","span","br","small","sup","sub","u","abbr",
          "mark","time","s","del","ins","cite","q","wbr","big","tt","font","label"}
# Never look inside these at all.
NO_RECURSE = {"script","style","noscript","code","pre","svg","canvas","iframe","head"}
# No children worth walking; read their attributes and move on.
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

# Never translate these.
KEEP = re.compile(r"""^(
    [\s\W\d]*
  |html|7th\s*Apparel|7thstreet|Saee(\s+e)?\s+Kamil
  |KVK(\s*\d+)?|BTW|Sedex|SEDEX|GOTS|OEKO-TEX|SMETA|BSCI|ISO\s*9001|ZC\d+
  |LinkedIn|Instagram|WhatsApp|YouTube|Uithoorn|Lahore|Amsterdam|Nederland
  |https?://\S+|[\w.+-]+@[\w.-]+|\+?\d[\d\s()+-]{5,}
  |[A-Z]{2,4}(\s*·\s*[A-Z]{2,4})+
)$""", re.X)

def translatable(s):
    s = s.strip()
    if not s: return False
    if KEEP.match(s): return False
    if not re.search(r"[A-Za-z]{2}", s): return False
    if re.fullmatch(r"[A-Z]{2,3}", s): return False
    return True

def key(s): return hashlib.sha1(s.encode("utf-8")).hexdigest()[:12]

def all_inline(el):
    """True if every element descendant is an inline tag."""
    for d in el.find_all(True):
        if d.name.lower() not in INLINE: return False
    return True

def inner(el):
    return "".join(str(c) for c in el.contents)

catalogue = {}

def add(s, kind, page):
    s = s.strip()
    if not translatable(s): return
    k = key(s)
    e = catalogue.setdefault(k, {"en": s, "pages": [], "kind": kind})
    if page not in e["pages"]: e["pages"].append(page)

def walk(el, page):
    for child in list(el.children):
        if isinstance(child, (Comment, Doctype)): continue
        if isinstance(child, NavigableString):
            add(str(child), "text", page)          # mixed content
            continue
        name = child.name.lower()
        if name in NO_RECURSE: continue
        if name in VOID:
            for a in ATTRS.get(name, []):
                if child.get(a): add(child[a], "attr:%s:%s" % (name,a), page)
            continue
        for a in ATTRS.get(name, []):
            if child.get(a): add(child[a], "attr:%s:%s" % (name,a), page)
        if child.get("id") == "heroline":
            add(child.get_text(" ", strip=True).replace("\xa0"," "), "heroline", page)
            continue
        if child.get_text(strip=True) and all_inline(child):
            add(inner(child), "html", page)
        else:
            walk(child, page)

for p in PAGES:
    soup = BeautifulSoup(open(p+".html", encoding="utf-8").read(), "html.parser")
    if soup.title and soup.title.string:
        add(soup.title.string, "title", p)
    for m in soup.find_all("meta"):
        n = (m.get("name") or m.get("property") or "").lower()
        if n in META_TRANSLATE and m.get("content"):
            add(m["content"], "attr:meta:"+n, p)
    body = soup.body or soup
    walk(body, p)
    # readable copy inside inline SVG (the film uses <text>)
    for t in soup.select("svg text, svg tspan, svg title, svg desc"):
        if t.get_text(strip=True): add(inner(t), "svgtext", p)

json.dump(catalogue, open("tools/i18n/catalogue.json","w",encoding="utf-8"),
          ensure_ascii=False, indent=1)

from collections import Counter
words = sum(len(re.sub(r"<[^>]+>"," ",v["en"]).split()) for v in catalogue.values())
print("unique segments :", len(catalogue))
print("unique words    :", words)
print("kinds           :", dict(Counter(v["kind"] for v in catalogue.values())))
print("with inline tags:", sum(1 for v in catalogue.values() if "<" in v["en"]))
print("under 3 chars   :", [v["en"] for v in catalogue.values() if len(v["en"])<3])
