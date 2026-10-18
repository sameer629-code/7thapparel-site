/* 7th Apparel — lead capture shared by every page.
   SEVENA_LEADS_URL is the Google Apps Script web app that logs leads in the
   7A Lead Tracker, emails the team and sends the customer a reply from support@.
   While it is empty, the quote form falls back to FormSubmit and WhatsApp links
   open directly (no pre-chat step). */
window.SEVENA_LEADS_URL = '';

/* WhatsApp pre-chat: one short step (name + what they need) before WhatsApp opens,
   so the chat is logged in the tracker with a reference the team can match.
   "Skip" is always one tap away; a visitor is asked only once per browser. */
(function () {
  var URL = window.SEVENA_LEADS_URL;
  if (!URL) return;
  var NUM = '31684660186';
  var LANG = (document.documentElement.getAttribute('lang') || 'en').slice(0, 2).toLowerCase();
  var S = {
    en: { t: 'Before we open WhatsApp', s: 'Two quick details so the right person answers you.', n: 'Your name', c: 'Company or brand (optional)', w: 'What is it about?',
          o: ['Clothing for my brand', 'Workwear & uniforms', 'Sports kits & teamwear', 'Company swag & merchandise', 'Something else'], go: 'Continue to WhatsApp', skip: 'Skip — just open WhatsApp', err: 'Please add your name.', x: 'Close',
          msg: 'Hi 7th Apparel, this is {n}{c}. I would like to ask about {w}. (ref {r})', from: ' from ' },
    nl: { t: 'Voordat WhatsApp opent', s: 'Twee korte gegevens, zodat de juiste persoon u antwoordt.', n: 'Uw naam', c: 'Bedrijf of merk (optioneel)', w: 'Waar gaat het over?',
          o: ['Kleding voor mijn merk', 'Bedrijfskleding & uniformen', 'Sportkleding & teamkleding', 'Merchandise met logo', 'Iets anders'], go: 'Verder naar WhatsApp', skip: 'Overslaan — open WhatsApp', err: 'Vul uw naam in.', x: 'Sluiten',
          msg: 'Hallo 7th Apparel, u spreekt met {n}{c}. Ik heb een vraag over {w}. (ref {r})', from: ' van ' },
    de: { t: 'Bevor WhatsApp öffnet', s: 'Zwei kurze Angaben, damit die richtige Person Ihnen antwortet.', n: 'Ihr Name', c: 'Firma oder Marke (optional)', w: 'Worum geht es?',
          o: ['Kleidung für meine Marke', 'Arbeitskleidung & Uniformen', 'Trikots & Teambekleidung', 'Firmen-Merchandise', 'Etwas anderes'], go: 'Weiter zu WhatsApp', skip: 'Überspringen — WhatsApp öffnen', err: 'Bitte geben Sie Ihren Namen an.', x: 'Schließen',
          msg: 'Hallo 7th Apparel, hier ist {n}{c}. Ich habe eine Frage zu {w}. (Ref. {r})', from: ' von ' },
    pl: { t: 'Zanim otworzymy WhatsApp', s: 'Dwie krótkie informacje, aby odpowiedziała właściwa osoba.', n: 'Imię i nazwisko', c: 'Firma lub marka (opcjonalnie)', w: 'Czego dotyczy pytanie?',
          o: ['Odzież dla mojej marki', 'Odzież robocza i uniformy', 'Stroje sportowe', 'Gadżety firmowe z logo', 'Coś innego'], go: 'Przejdź do WhatsApp', skip: 'Pomiń — otwórz WhatsApp', err: 'Prosimy podać imię.', x: 'Zamknij',
          msg: 'Dzień dobry 7th Apparel, tu {n}{c}. Mam pytanie dotyczące: {w}. (ref {r})', from: ', ' },
    fr: { t: 'Avant d\'ouvrir WhatsApp', s: 'Deux informations rapides pour que la bonne personne vous réponde.', n: 'Votre nom', c: 'Entreprise ou marque (facultatif)', w: 'C\'est à quel sujet ?',
          o: ['Vêtements pour ma marque', 'Vêtements de travail & uniformes', 'Tenues de sport', 'Goodies d\'entreprise', 'Autre chose'], go: 'Continuer vers WhatsApp', skip: 'Passer — ouvrir WhatsApp', err: 'Merci d\'indiquer votre nom.', x: 'Fermer',
          msg: 'Bonjour 7th Apparel, ici {n}{c}. J\'ai une question concernant : {w}. (réf. {r})', from: ', ' }
  };
  var T = S[LANG] || S.en;
  function asked() { try { return localStorage.getItem('7a_wa') === '1'; } catch (e) { return false; } }
  function mark() { try { localStorage.setItem('7a_wa', '1'); } catch (e) {} }
  function ref() { var c = 'ABCDEFGHJKLMNPQRSTUVWXYZ23456789', r = 'W'; for (var i = 0; i < 4; i++) r += c.charAt(Math.floor(Math.random() * c.length)); return r; }

  var css = '.wapc{position:fixed;inset:0;z-index:1000;background:rgba(23,16,46,.55);display:flex;align-items:flex-end;justify-content:center;padding:16px}' +
    '@media(min-width:640px){.wapc{align-items:center}}' +
    '.wapc .box{background:#fff;color:#1B1338;border-radius:16px;max-width:420px;width:100%;padding:22px 20px 18px;box-shadow:0 24px 60px rgba(23,16,46,.35);font:15px/1.5 Inter,system-ui,sans-serif;position:relative}' +
    '.wapc h2{font:600 20px/1.25 "Space Grotesk",Inter,sans-serif;margin:0 28px 4px 0;color:#2C2153}.wapc p{margin:0 0 14px;color:#4a4560}' +
    '.wapc label{display:block;font-size:13px;font-weight:600;margin:10px 0 4px;color:#2C2153}.wapc input,.wapc select{width:100%;box-sizing:border-box;min-height:44px;border:1px solid #C9B8EE;border-radius:10px;padding:8px 12px;font:inherit;background:#fff;color:#1B1338}' +
    '.wapc .go{display:flex;align-items:center;justify-content:center;gap:8px;margin-top:16px;min-height:48px;border-radius:12px;background:#25D366;color:#fff;font-weight:700;text-decoration:none}' +
    '.wapc .skip{display:block;text-align:center;margin-top:10px;color:#6E56A4;font-size:14px}.wapc .er{color:#B42318;font-size:13px;margin:8px 0 0;display:none}' +
    '.wapc .x{position:absolute;top:10px;right:10px;width:36px;height:36px;border:0;background:transparent;font-size:22px;line-height:1;color:#6E56A4;cursor:pointer;border-radius:8px}';

  var el = null, lastFocus = null, orig = '';
  function close() { if (el) { el.remove(); el = null; } document.removeEventListener('keydown', onKey); if (lastFocus) try { lastFocus.focus(); } catch (e) {} }
  function onKey(e) { if (e.key === 'Escape') close(); }

  function open(href) {
    orig = href; lastFocus = document.activeElement;
    if (!document.getElementById('wapc-css')) { var st = document.createElement('style'); st.id = 'wapc-css'; st.textContent = css; document.head.appendChild(st); }
    el = document.createElement('div'); el.className = 'wapc'; el.setAttribute('role', 'dialog'); el.setAttribute('aria-modal', 'true'); el.setAttribute('aria-labelledby', 'wapc-t');
    var opts = T.o.map(function (o) { return '<option>' + o + '</option>'; }).join('');
    el.innerHTML = '<div class="box"><button type="button" class="x" aria-label="' + T.x + '">×</button><h2 id="wapc-t">' + T.t + '</h2><p>' + T.s + '</p>' +
      '<label for="wapc-n">' + T.n + '</label><input id="wapc-n" autocomplete="name">' +
      '<label for="wapc-c">' + T.c + '</label><input id="wapc-c" autocomplete="organization">' +
      '<label for="wapc-w">' + T.w + '</label><select id="wapc-w">' + opts + '</select>' +
      '<p class="er" id="wapc-e">' + T.err + '</p>' +
      '<a class="go" id="wapc-go" target="_blank" rel="noopener noreferrer" href="#">' + T.go + ' →</a>' +
      '<a class="skip" id="wapc-skip" target="_blank" rel="noopener noreferrer" href="' + href + '">' + T.skip + '</a></div>';
    document.body.appendChild(el);
    el.addEventListener('click', function (e) { if (e.target === el) close(); });
    el.querySelector('.x').addEventListener('click', close);
    document.addEventListener('keydown', onKey);
    var r = ref(), n = el.querySelector('#wapc-n'), c = el.querySelector('#wapc-c'), w = el.querySelector('#wapc-w'), go = el.querySelector('#wapc-go');
    function upd() {
      var m = T.msg.replace('{n}', n.value.trim() || '…').replace('{c}', c.value.trim() ? T.from + c.value.trim() : '').replace('{w}', w.value).replace('{r}', r);
      go.href = 'https://wa.me/' + NUM + '?text=' + encodeURIComponent(m);
    }
    [n, c, w].forEach(function (x) { x.addEventListener('input', upd); x.addEventListener('change', upd); }); upd();
    go.addEventListener('click', function (e) {
      if (!n.value.trim()) { e.preventDefault(); el.querySelector('#wapc-e').style.display = 'block'; n.focus(); return; }
      upd();
      try {
        fetch(URL, { method: 'POST', keepalive: true, body: JSON.stringify({ type: 'whatsapp', lang: LANG, page: location.pathname,
          name: n.value.trim(), company: c.value.trim(), interest: w.value, ref: r }) }).catch(function () {});
      } catch (x) {}
      mark(); setTimeout(close, 50);
    });
    el.querySelector('#wapc-skip').addEventListener('click', function () { mark(); setTimeout(close, 50); });
    setTimeout(function () { n.focus(); }, 30);
  }

  document.addEventListener('click', function (e) {
    var a = e.target.closest && e.target.closest('a[href*="wa.me/"]');
    if (!a || (el && el.contains(a)) || asked()) return;
    e.preventDefault(); open(a.getAttribute('href'));
  }, true);
})();
