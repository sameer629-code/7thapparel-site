# 7th Apparel — website

Marketing site for **7th Apparel**, the European arm of our own garment production
house. Static HTML, no build step, no framework, no dependencies.

**Live:** not yet deployed · **Preview:** see `docs/PREVIEW.md`

---

## What this is

Thirteen hand-written pages. Everything is plain HTML with inline `<style>` and
`<script>` — deliberately. The site has to be editable by whoever inherits it, load fast
on a phone in a factory, and never break because a package went stale.

| Page | Purpose |
|---|---|
| `index.html` | Home — hero, story film, track record, group structure, capacity, live tracking |
| `for-brands.html` | Brands: capsule → launch → grow → scale |
| `for-teams.html` | Companies, clubs and events buying their own kit |
| `what-we-make.html` | Categories, product reel, full workwear range |
| `workwear.html` | Workwear in depth + the 26-page catalogue browser |
| `our-factory.html` | The production house |
| `how-it-works.html` | Brief to delivery in six steps |
| `pricing.html` | Published price bands and the €5 blank-tee offer |
| `faq.html` | Twelve questions buyers actually ask |
| `compliance.html` | Sedex, GSP+, duty, REX |
| `about.html` | The group and both entities |
| `contact.html` | Origin story, mission, team |
| `quote.html` | The brief form — the only conversion point |

`index_static.html` is a non-animated fallback of the homepage. Not linked; kept as a
reference if the animated version ever needs to be replaced.

---

## Running it

```bash
python3 -m http.server 8000    # then open http://localhost:8000
```

Opening the files directly with `file://` mostly works, but fragment links and the
video behave better over HTTP.

---

## Conventions worth knowing before you edit

**Everything is inline.** Each page carries its own `<style>` and `<script>`. There is no
shared stylesheet. Changing the header means changing it in thirteen files — use a script,
not thirteen manual edits. `scripts/` has examples of how that has been done.

**Nothing load-bearing may depend on JavaScript running.** Three separate bugs during
development came from assuming otherwise: animation frames that never fired, a pinned
scroll trigger that mis-measured, and fragment navigation that silently did nothing inside
an embedded frame. Every animated element now has a watchdog that forces it visible after
2.6 s, and every in-page anchor is handled in JS with a header offset. Keep both.

**External dependencies are two CDN scripts (GSAP and ScrollTrigger) and Google Fonts.**
The site is fully readable with all three blocked — 13,000+ characters of content render
with JavaScript disabled entirely. Do not add a dependency that breaks that.

**The nav is nine items and only just fits.** It switches to a burger below 1200px. If you
add a tenth item, re-check the header at 1280 and 1440 — it previously overflowed its own
flex box and printed across the logo.

---

## The brief form

`quote.html` POSTs to [FormSubmit](https://formsubmit.co), which emails each submission.
No backend, no API key.

```js
var NOTIFY   = 'smrshhzd@gmail.com';
var ENDPOINT = 'https://formsubmit.co/ajax/' + NOTIFY;
```

The first submission triggers a one-time confirmation email to that address. **Until
somebody clicks that link, submissions do not send.**

If the request fails for any reason the form falls back to opening the visitor's mail
client with the whole brief pre-filled, plus a copy-paste box — a lead is never lost
because a third-party service was down. Keep that fallback.

To move to a real backend, replace `ENDPOINT` and the `fetch` call. Everything else stays.

---

## Assets

| Path | What |
|---|---|
| `assets/*.jpg` | Photographs from our own floor. Not stock. |
| `assets/reel.mp4` | 30-second product film, 1:1, with original music |
| `assets/reel-poster.jpg` | Poster frame |
| `assets/catalogue/p01–p26.jpg` | Workwear catalogue pages |
| `assets/catalogue/t01–t26.jpg` | Thumbnails for the strip |
| `assets/team/*.png` | Team portraits, colour-matched |

**The music in `reel.mp4` was composed for this project and is owned outright** — no
licence, no attribution, no expiry. It can be used in paid advertising.

The full catalogue PDF (~29 MB) is deliberately **not** committed. Add it at
`assets/Workwear_Catalogue.pdf` on the host so the download button works, or move it to a
CDN and update the link on `workwear.html`.

---

## Testing

```bash
npm i -D playwright && npx playwright install chromium
node tests/qa-responsive.js    # 13 pages × 7 viewports
node tests/qa-deep.js          # links, SEO, accessibility, assets
node tests/qa-functional.js    # form, catalogue, menu, anchors, video
```

All three passed at the last commit. Run them before any deploy.

---

## Deploying

Any static host works — it is thirteen HTML files and a folder of assets.

A GitHub Pages workflow is included at `.github/workflows/deploy.yml`, disabled by
default. Enable it in **Settings → Pages → Source → GitHub Actions**, then uncomment the
`CNAME` line in the workflow and point the domain's DNS at GitHub. Note that Pages
requires either a public repository or a paid plan.

---

© 7th Apparel. All rights reserved. Not open source — see `LICENSE`.
