# Multilingual build

The site is written once, in English, and the other four languages are generated.

```
python3 tools/i18n/extract.py    # English pages  ->  catalogue.json
python3 tools/i18n/build.py      # catalogue + nl/de/pl/fr.json  ->  /nl /de /pl /fr
```

## How it works

`extract.py` walks each English page and pulls out **whole phrases**, not text nodes: any
element whose children are all inline tags is taken as one segment with its markup intact, so
a translator sees a complete sentence and can put `<em>` wherever the target language needs
it. Extracting text node by text node would have produced word salad in German and Polish —
the homepage headline alone is seven separate `<span>`s.

Each segment is keyed by a hash of the English, so identical strings share one translation and
changing the English creates a new key rather than silently keeping a stale translation.

`build.py` re-walks each page in the same order, swaps in the translation, then:

- rewrites `assets/…` to `/assets/…` (relative paths break one directory down)
- prefixes internal links with the language code
- sets `<html lang>`, the canonical URL, `og:locale`
- writes the full reciprocal `hreflang` set, including `x-default`, on all 70 pages
- injects the language switcher, its CSS, and the detection script

It is **re-runnable**: it strips its own previous output first, so you can edit English copy,
re-extract, re-translate the changed keys and rebuild without accumulating duplicates.

## Editing the site after this

Edit the English page as usual, then:

1. `python3 tools/i18n/extract.py` — any changed string gets a new key
2. translate the new keys into `tools/i18n/{nl,de,pl,fr}.json`
3. `python3 tools/i18n/build.py`

`build.py` prints anything it could not translate. Brand names, numbers, certification codes
and the like are deliberately never translated and will always show in that list.

## Language detection

English pages carry a small script in `<head>` that redirects a first-time visitor whose
browser prefers Dutch, German, Polish or French. It runs before anything paints, so there is
no flash. It never fires if the visitor has already chosen a language, if they explicitly
asked for English, or if `?lang=` is in the URL.

Country is a **secondary** signal: a visitor with an English browser coming from a Dutch IP
is not redirected — they get a small dismissible bar offering the Dutch version, read from
Cloudflare's `/cdn-cgi/trace`. Redirecting on IP alone breaks crawlers and traps people who
want English, which is why Google advises against it.

The choice is remembered in `localStorage` under `7a_lang`.
