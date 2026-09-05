# Working on this site

## Before you change anything

Run the tests. They pass at every commit on `main`, so a failure is something you did.

```bash
node tests/qa-responsive.js   # 13 pages × 7 viewports — overflow, header, tap targets
node tests/qa-deep.js         # broken links, dead anchors, duplicate ids, SEO, alt text
node tests/qa-functional.js   # form, catalogue browser, mobile menu, anchors, video
```

The responsive suite reports four inline links under 32px. That is expected and
deliberate — they sit inside sentences, WCAG 2.5.8 exempts targets in a block of text,
and forcing them taller breaks the paragraph.

## Editing across all pages

There is no shared stylesheet, so a header or footer change touches thirteen files.
Do it with a script, and **verify by counting the result** rather than trusting a
success message:

```python
import glob
n = 0
for f in glob.glob('*.html'):
    s = open(f, encoding='utf-8').read()
    if OLD not in s:          # assert the anchor exists — do not fail silently
        print('MISS', f); continue
    open(f, 'w', encoding='utf-8').write(s.replace(OLD, NEW)); n += 1
print('patched', n, 'of 13')
```

Two bugs during development came from a `replace()` that matched nothing while the
script printed success. Count what you changed.

## Rules that exist for a reason

**Content must never depend on JavaScript running.** Every animated element has a
watchdog that forces it visible at 2.6 s and 5 s. Every in-page anchor is handled in JS
with a header offset, because fragment navigation does nothing inside an embedded frame.
Both were bugs found in production-like conditions. Do not remove them.

**Keep the form's mail-client fallback.** If FormSubmit is unreachable, the visitor still
gets their brief into an email. That is the difference between a lost lead and a slow one.

**Numbers on this site are checkable.** Buyer names are published with permission, and
every figure traces to real order data. If you change a number, change it everywhere —
the same figures appear on the homepage, the marquee, the proof strip and the film. Grep
before you edit.

**The nav only just fits at 1200px.** Adding a tenth item means re-checking the header
at 1280 and 1440. It previously overflowed its flex box and printed across the logo.
