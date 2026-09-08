# Translation brief — 7thapparel.com

## Who this is for

7th Apparel is a Dutch B2B apparel manufacturer (KVK 91485452, Uithoorn/Amsterdam) with its
own production house in Lahore, Pakistan (Saee e Kamil, running since 2011). It sells to two
audiences: **brands** (founders and product managers who need small runs made properly) and
**teams** (companies buying uniforms, workwear and merchandise).

The reader is a professional buyer. In Germany and the Netherlands especially, they are
sceptical of suppliers who oversell.

## Voice — this matters more than literal accuracy

The English is deliberately plain, direct, slightly understated, and free of marketing
inflation. It says "we do this, here is the price, here is what can go wrong". **Translate
the intent and the register, not the words.** A sentence that reads naturally to a native
buyer beats one that mirrors English syntax.

Specifically:
- **German**: use *Sie*. Avoid Denglisch where a real German term exists. Compound nouns are
  fine and expected. Do not inflate — German B2B copy that oversells reads as untrustworthy.
- **Dutch**: use *u* (this is B2B and the reader is a buyer, not a consumer). Dutch prose is
  even more direct than English — let it be. Avoid literal Anglicisms where Dutch has its own
  word, but keep the loanwords the trade actually uses (*denim*, *workwear*, *sample*, *fit*).
- **French**: use *vous*. French B2B tolerates slightly more formality than English; that is
  fine, but do not become florid. Follow French typography: non-breaking space before `?` `!`
  `:` `;` and inside `«  »` — write a normal space, we handle the rest.
- **Polish**: formal register (*Państwo* / impersonal constructions). Polish reads badly when
  it mirrors English word order — restructure freely. Avoid calques.

## Absolute rules

1. **Return valid JSON**: exactly the same keys as the input file, every key present, values
   are the translated strings. Nothing else in the file.
2. **Preserve every HTML tag exactly** — same tags, same order, same attributes, byte for
   byte. Only human-readable text between and around tags changes. Never translate, reorder
   or "tidy" an attribute. In particular **never change an `href`, `src`, `class`, `id`,
   `style` or `rel` value** — internal links are rewritten later by a script and will break
   if you touch them. `<br/>` stays `<br/>`.
   - You *may* move an inline tag such as `<em>` or `<strong>` to the word that carries the
     emphasis in the target language. That is the one permitted structural change.
3. **Never translate these**: 7th Apparel · 7thstreet · Saee e Kamil · Saee Kamil · KVK ·
   BTW · Sedex · SMETA · GOTS · OEKO-TEX · BSCI · ISO 9001 · SEDEX ZC5000072720 ·
   vestiging 000057160791 · LinkedIn · Instagram · WhatsApp · any email address, phone
   number, URL, or company name (Hyperlite, Sapphire, US Denim, etc.), and any person's name.
4. **Numbers, units and currency stay as they are**: `$1.2M+`, `€50`, `12 oz`, `220 gsm`,
   `10 pieces`, `48 hours`, `11 of 13`. Translate the words around them. Use the target
   language's decimal/thousands convention only where the English uses a written-out figure.
5. **Place names**: Amsterdam, Uithoorn, Lahore stay. *Netherlands* → Nederland / Niederlande
   / Holandia / Pays-Bas. *Pakistan* → Pakistan / Pakistan / Pakistan / Pakistan.
6. **Length discipline.** Many of these strings sit in buttons, nav items, table cells and
   badges. If the English is under 25 characters, the translation must stay close to that
   length — a nav item that wraps to two lines breaks the header. Prefer the shorter natural
   term. German especially: pick the shorter of two correct options.
7. **UPPERCASE strings stay uppercase** (they are set in caps by CSS-adjacent design intent).
8. Keep the `·` separator character where it appears.

## Glossary — use these consistently

| English | nl | de | pl | fr |
|---|---|---|---|---|
| For Brands | Voor merken | Für Marken | Dla marek | Pour les marques |
| For Teams | Voor teams | Für Teams | Dla firm | Pour les équipes |
| What we make | Wat we maken | Was wir fertigen | Co produkujemy | Ce que nous fabriquons |
| Our factory | Onze fabriek | Unsere Fabrik | Nasza fabryka | Notre usine |
| Our story | Ons verhaal | Unsere Geschichte | Nasza historia | Notre histoire |
| How it works | Hoe het werkt | So funktioniert es | Jak to działa | Comment ça marche |
| Pricing | Prijzen | Preise | Cennik | Tarifs |
| Compliance | Compliance | Compliance | Zgodność | Conformité |
| Contact | Contact | Kontakt | Kontakt | Contact |
| Get a quote | Vraag een offerte aan | Angebot anfordern | Poproś o wycenę | Demander un devis |
| quote (noun) | offerte | Angebot | wycena | devis |
| lead time | levertijd | Lieferzeit | czas realizacji | délai de production |
| minimum order / MOQ | minimale afname | Mindestbestellmenge | minimalne zamówienie | quantité minimum |
| sample | sample | Muster | próbka | échantillon |
| fabric | stof | Stoff | tkanina | tissu |
| knit | tricot | Strick | dzianina | maille |
| woven | geweven | Webware | tkanina | chaîne et trame |
| denim | denim | Denim | denim | denim |
| workwear | werkkleding | Arbeitskleidung | odzież robocza | vêtements de travail |
| hi-vis | hi-vis | Warnschutz | odblaskowa | haute visibilité |
| FR (flame retardant) | vlamvertragend | flammhemmend | trudnopalna | ignifuge |
| leather | leer | Leder | skóra | cuir |
| towels | handdoeken | Handtücher | ręczniki | serviettes |
| cut, sewn and finished | gesneden, genaaid en afgewerkt | zugeschnitten, genäht und ausgerüstet | krojone, szyte i wykańczane | coupé, cousu et fini |
| production house | productiehuis | Produktionsstätte | zakład produkcyjny | atelier de production |
| production floor | productievloer | Produktionsfläche | hala produkcyjna | atelier |
| landed / DDP | franco huis (DDP) | frei Haus (DDP) | z dostawą (DDP) | rendu droits acquittés (DDP) |
| customs | douane | Zoll | odprawa celna | douane |
| tech pack | tech pack | Tech Pack | tech pack | dossier technique |
| capsule (10 pieces) | capsule | Capsule | kapsuła | capsule |
| piece / pieces | stuk / stuks | Stück | sztuka / sztuk | pièce / pièces |
| per style | per stijl | pro Modell | na model | par modèle |
| repeat order | herhaalorder | Folgeauftrag | zamówienie powtórne | réassort |
| brand (the customer) | merk | Marke | marka | marque |
| Download PDF | Download PDF | PDF herunterladen | Pobierz PDF | Télécharger le PDF |
| Play as slideshow | Als diavoorstelling | Als Diashow abspielen | Odtwórz pokaz | Lire le diaporama |
| Menu | Menu | Menü | Menu | Menu |
| Next page / Previous page | Volgende / Vorige | Weiter / Zurück | Następna / Poprzednia | Suivant / Précédent |
| PAGE 1 OF 26 | PAGINA 1 VAN 26 | SEITE 1 VON 26 | STRONA 1 Z 26 | PAGE 1 SUR 26 |

## Page titles and meta descriptions

Keys whose English value looks like a page title (`… | 7th Apparel`, `… — 7th Apparel`) or a
meta description are for search engines. Translate them as **native search copy**, not as a
literal rendering: lead with the term a buyer in that country would actually type
(*kledingfabrikant*, *Bekleidungshersteller*, *producent odzieży*, *fabricant de vêtements*),
keep titles under ~60 characters and descriptions under ~155.
