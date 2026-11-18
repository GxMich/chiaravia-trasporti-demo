"""Genera il sito dimostrativo di Chiaravia Trasporti e Logistica (azienda di fantasia).
Solo libreria standard di Python, nessun accesso alla rete."""

from pathlib import Path
from html import escape as esc
import json
import hashlib
import re
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parent
CFG = json.loads((ROOT / 'site.config.json').read_text(encoding='utf-8'))
if CFG.get('demo') is not True:
    raise SystemExit('Questo progetto genera solo la versione dimostrativa: l’azienda è di fantasia.')
BASE_PATH = '/chiaravia-trasporti-demo/'

ARROW = '<svg class="arrow" viewBox="0 0 24 24" fill="none" aria-hidden="true"><path d="M5 12h14m-6-6 6 6-6 6" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/></svg>'
PIN = '<svg class="pin" viewBox="0 0 24 24" fill="none" aria-hidden="true"><path d="M12 21s-6.5-6.1-6.5-11a6.5 6.5 0 0 1 13 0c0 4.9-6.5 11-6.5 11Z" stroke="currentColor" stroke-width="1.6" stroke-linejoin="round"/><circle cx="12" cy="10" r="2.3" fill="currentColor"/></svg>'
IMAGE_SIZE = {
    'hero-camion': (2000, 1174), 'camion-strada': (1560, 1600),
    'carico-muletto': (2000, 1334), 'magazzino-muletto': (2000, 1334),
    'piazzale-aereo': (2000, 1333), 'baie-carico': (2000, 1333),
}
SERVICE_LINE = 'Carico dedicato · Pallet e colli · Logistica e magazzino'
DEMO_NOTE = 'Attività di fantasia: nomi, recapiti, prezzi e recensioni sono inventati. Sito dimostrativo realizzato da <a href="https://www.modicamichele.it">Michele Modica</a>.'

SERVICES = [
    {
        'slug': 'carico-dedicato', 'number': '01', 'name': 'Carico dedicato',
        'short': 'Un camion solo per la tua merce.', 'image': 'camion-strada', 'position': '50% 58%',
        'alt': 'Un semirimorchio furgonato in viaggio su una strada extraurbana al tramonto',
        'lead': 'Un mezzo intero riservato alla tua spedizione, che parte quando sei pronto e va dritto a destinazione.',
        'for': 'Carichiamo da te e scarichiamo dal destinatario. In mezzo non ci sono depositi, trasbordi o altre consegne.',
        'tags': ['Carico completo (FTL)', 'Carico parziale diretto', 'Orari concordati'],
        'context': 'Parte quando vuoi tu.<br>Arriva senza soste.',
        'intro': 'Scegli il carico dedicato quando la merce è tanta, è delicata o deve arrivare a un’ora precisa. Il camion lavora solo per te: niente scali in magazzino, niente colli di altri clienti accanto ai tuoi.',
        'includes': [
            ('Carico completo (FTL)', 'Tutto il mezzo per una spedizione sola, con un mittente e un destinatario.'),
            ('Carico parziale diretto', 'La merce non riempie il camion ma deve comunque viaggiare senza passare da un deposito.'),
            ('Finestre di carico e scarico', 'Orari fissati con te e con chi riceve, così nessuno resta ad aspettare al portone.'),
            ('Un viaggio o tanti', 'Una partenza sola oppure viaggi ripetuti con lo stesso schema ogni settimana.'),
        ],
        'need': ['Che merce è e come è imballata', 'Quanti pezzi, quanto pesa, che misure', 'Indirizzo di carico e di consegna', 'Giorni e orari possibili'],
        'promise': 'Ti mandiamo una proposta con mezzo, date e prezzo del viaggio.',
        'band': ('Un camion pieno<br>da far partire?', 'Scrivi merce, tratta e date. Ti rispondiamo con mezzo, tempi e costo.'),
    },
    {
        'slug': 'pallet-colli', 'number': '02', 'name': 'Pallet e colli',
        'short': 'Paghi solo lo spazio che occupi.', 'image': 'carico-muletto', 'position': '50% 55%',
        'alt': 'Un carrello elevatore movimenta pallet all’ingresso di un semirimorchio',
        'lead': 'Spedizioni in groupage per chi ha pochi pallet o qualche collo: la merce condivide il viaggio con altre spedizioni dirette nella stessa zona.',
        'for': 'Un pallet, cinque pallet o qualche scatola imballata: la tariffa si calcola sullo spazio usato.',
        'tags': ['Groupage', 'Collettame', 'Ritiri fissi'],
        'context': 'Pochi pallet,<br>tariffa giusta.',
        'intro': 'Nel groupage, chiamato anche collettame, più clienti dividono lo stesso camion verso la stessa area. Se la tua merce non riempie un mezzo è il modo più economico per spedirla, senza rinunciare al ritiro in sede.',
        'includes': [
            ('Groupage e collettame', 'La tua spedizione viaggia insieme ad altre con la stessa direzione.'),
            ('Pallet e colli sfusi', 'Pallet 80×120, mezzi pallet e colli di misure diverse nella stessa spedizione.'),
            ('Ritiro in azienda', 'Veniamo a prendere la merce da te e la portiamo fino al destinatario.'),
            ('Giorni di ritiro fissi', 'Per chi spedisce tutte le settimane: stesso giorno, stesse condizioni, nessuna richiesta da ripetere.'),
        ],
        'need': ['Quanti pallet o colli', 'Peso e misure di ognuno', 'Se si possono sovrapporre', 'Destinazione e data'],
        'promise': 'Ti mandiamo tariffa e tempi di consegna per la tua tratta.',
        'band': ('Quanti pallet<br>devono partire?', 'Ci bastano numero, misure e destinazione. Ti rispondiamo con prezzo e tempi.'),
    },
    {
        'slug': 'logistica', 'number': '03', 'name': 'Logistica e magazzino',
        'short': 'Il magazzino lo teniamo noi.', 'image': 'magazzino-muletto', 'position': '50% 50%',
        'alt': 'Corsia di un magazzino con scaffalature e carrello elevatore',
        'lead': 'Teniamo la tua merce nel nostro magazzino, prepariamo gli ordini e li spediamo ai tuoi clienti. Un solo referente per deposito e trasporto.',
        'for': 'Ci mandi la merce, noi la riceviamo, la sistemiamo a scaffale e la spediamo quando arriva un ordine.',
        'tags': ['Deposito conto terzi', 'Preparazione ordini', 'Picchi stagionali'],
        'context': 'Più spazio da te,<br>meno pensieri.',
        'intro': 'Con la logistica in conto terzi lo spazio, il personale e i carrelli li mettiamo noi. Tu ti occupi di vendere, noi di ricevere, contare, preparare e spedire.',
        'includes': [
            ('Ricevimento merce', 'Scarichiamo, contiamo i colli e registriamo cosa entra.'),
            ('Deposito a scaffale', 'Pallet e colli in posizioni registrate, facili da ritrovare.'),
            ('Preparazione ordini', 'Prelievo, imballo ed etichetta: l’ordine è pronto per partire.'),
            ('Spedizione', 'Scegliamo il trasporto adatto e consegniamo ai tuoi clienti.'),
        ],
        'need': ['Tipo di merce e confezione', 'Spazio o pallet da occupare', 'Quanto spesso entra ed esce', 'Da quando vuoi partire'],
        'promise': 'Ti mandiamo una proposta con spazi, attività e tariffe.',
        'band': ('Ti serve<br>un magazzino?', 'Raccontaci merce, volumi e cosa dobbiamo fare. Ti rispondiamo con spazi, operazioni e costi.'),
    },
]


def image(name, alt, *, cls='', eager=False, sizes='(max-width: 760px) calc(100vw - 40px), 44vw', style=''):
    width, height = IMAGE_SIZE[name]
    candidates = []
    for size in (480, 720, 900, 1200):
        if (ROOT / 'img' / f'{name}-{size}.webp').exists():
            candidates.append(f'img/{name}-{size}.webp {size}w')
    candidates.append(f'img/{name}.webp {width}w')
    loading = 'fetchpriority="high" loading="eager"' if eager else 'loading="lazy"'
    position = f' style="object-position:{style}"' if style else ''
    return f'<img class="{cls}" src="img/{name}.webp" srcset="{", ".join(candidates)}" sizes="{sizes}" width="{width}" height="{height}" alt="{esc(alt)}" {loading} decoding="async"{position}>'


def brand():
    return '<span class="brand"><span class="brand-name">Chiaravia<span class="brand-stop">.</span></span><span class="brand-detail">Trasporti<br>&amp; Logistica</span></span>'


def button(label, href, *, style='primary', extra=''):
    return f'<a class="button button-{style}" href="{esc(href)}" {extra}><span>{label}</span>{ARROW}</a>'


def header(active):
    links = [('servizi', 'servizi.html', 'Servizi'), ('metodo', 'index.html#metodo', 'Come lavoriamo'), ('azienda', 'azienda.html', 'Azienda')]
    def nav_links(mobile=False):
        return ''.join(f'<a href="{url}"{(" aria-current=\"page\"" if key == active else "")}>{label}{ARROW if mobile else ""}</a>' for key, url, label in links) + (f'<a href="contatti.html"{(" aria-current=\"page\"" if active == "contatti" else "")}>Contatti{ARROW}</a>' if mobile else '')
    header_cta = '' if active == 'contatti' else button('Contatti', 'contatti.html', style='outline', extra='data-header-cta')
    menu_cta = '' if active == 'contatti' else button('Richiedi un preventivo', 'contatti.html', style='accent')
    return f'''<a class="skip-link" href="#contenuto">Vai al contenuto</a>
<header class="site-header" data-header>
  <div class="header-inner container">
    <a class="brand-link" href="index.html" title="Torna alla home">{brand()}</a>
    <nav class="desktop-nav" aria-label="Navigazione principale">{nav_links()}</nav>{header_cta}
    <button class="menu-toggle" type="button" aria-expanded="false" aria-controls="mobile-menu" aria-label="Apri il menu" data-menu-toggle><span></span><span></span></button>
  </div>
</header>
<dialog class="mobile-menu" id="mobile-menu" aria-label="Navigazione" data-mobile-menu>
  <div class="mobile-menu-top">{brand()}<button class="menu-close" type="button" data-menu-close aria-label="Chiudi il menu">Chiudi <span aria-hidden="true">×</span></button></div>
  <p class="eyebrow">Trasporto merci e logistica</p>
  <nav aria-label="Navigazione mobile"><a href="index.html">Home{ARROW}</a>{nav_links(True)}</nav>
  <div class="mobile-menu-bottom"><span>Chiaravia Trasporti e Logistica<br>San Ferlino (Piemonte)</span>{menu_cta}</div>
</dialog><noscript><nav class="noscript-nav container" aria-label="Navigazione senza JavaScript"><a href="index.html">Home</a><a href="servizi.html">Servizi</a><a href="azienda.html">Azienda</a><a href="contatti.html">Contatti</a></nav></noscript>'''


def contact_links():
    links = []
    if CFG.get('phone'):
        phone = re.sub(r'[^+0-9]', '', CFG['phone'])
        links.append(f'<a href="tel:{phone}">{esc(CFG["phone"])}</a>')
    if CFG.get('email'):
        links.append(f'<a href="mailto:{esc(CFG["email"])}">{esc(CFG["email"])}</a>')
    return ''.join(links)


def footer(active=''):
    direct = contact_links()
    request = '' if active == 'contatti' else '<a href="contatti.html">Contatti</a>'
    return f'''<footer class="site-footer">
  <div class="container">
    <div class="footer-top"><a class="brand-link" href="index.html" title="Torna alla home">{brand()}</a><p>Trasporto merci e logistica<br>San Ferlino (Piemonte)</p></div>
    <div class="footer-grid">
      <div><p class="footer-label">Servizi</p>{''.join(f'<a href="servizio-{s["slug"]}.html">{s["name"]}</a>' for s in SERVICES)}</div>
      <div><p class="footer-label">Chiaravia</p><a href="azienda.html">L’azienda</a><a href="index.html#metodo">Come lavoriamo</a>{request}</div>
      <div class="footer-contact"><p class="footer-label">Sede</p><address>{esc(CFG['legal_address'])}</address>{direct}</div>
    </div>
    <div class="footer-bottom"><p>© <span data-year>2026</span> {esc(CFG['legal_name'])}</p><a href="privacy.html">Privacy e cookie</a><a class="back-top" href="#contenuto">Torna su <span aria-hidden="true">↑</span></a></div>
    <p class="demo-disclosure">{DEMO_NOTE}</p>
  </div>
</footer>
<div class="mobile-action" data-mobile-action><span>Hai merce<br>da spedire?</span>{button('Richiedi un preventivo', 'contatti.html', style='primary')}</div>'''


PAGES = []


def page(path, title, description, body, active='', body_class=''):
    url = CFG['url'].rstrip('/') + ('/' if path == 'index.html' else '/' + path)
    css_version = hashlib.sha256((ROOT / 'assets' / 'site.css').read_bytes()).hexdigest()[:10]
    js_version = hashlib.sha256((ROOT / 'assets' / 'site.js').read_bytes()).hexdigest()[:10]
    og_version = hashlib.sha256((ROOT / 'assets' / 'og.jpg').read_bytes()).hexdigest()[:10]
    schema = {
        '@context': 'https://schema.org', '@type': 'Organization',
        'name': CFG['legal_name'], 'description': 'Sito dimostrativo: azienda e dati inventati.', 'url': CFG['url'],
    }
    base = f'\n<base href="{BASE_PATH}">' if path == '404.html' else ''
    output = f'''<!doctype html>
<html lang="it">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">{base}
<title>{esc(title)}</title>
<meta name="description" content="{esc(description)}">
<meta name="robots" content="noindex, nofollow">
<meta name="theme-color" content="#133f3c">
<link rel="canonical" href="{esc(url)}">
<meta property="og:type" content="website">
<meta property="og:locale" content="it_IT">
<meta property="og:site_name" content="{esc(CFG['name'])} (demo)">
<meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(description)}">
<meta property="og:url" content="{esc(url)}">
<meta property="og:image" content="{esc(CFG['url'])}/assets/og.jpg?v={og_version}">
<meta property="og:image:alt" content="Chiaravia Trasporti e Logistica, sito dimostrativo di un’azienda di fantasia">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="assets/favicon.png" type="image/png" sizes="128x128">
<link rel="apple-touch-icon" href="assets/apple-touch-icon.png" sizes="180x180">
<link rel="preload" href="assets/fonts/sora-latin.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="assets/fonts/figtree-latin.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="assets/site.css?v={css_version}">
<script type="application/ld+json">{json.dumps(schema, ensure_ascii=False).replace('<', chr(92) + 'u003c')}</script>
<script src="assets/site.js?v={js_version}" defer></script>
</head>
<body class="{body_class}">
{header(active)}
<main id="contenuto" tabindex="-1">
{body}
</main>
{footer(active)}
</body>
</html>
'''
    (ROOT / path).write_text(output, encoding='utf-8', newline='\n')
    if path != '404.html':
        PAGES.append(path)


def crumbs(items):
    parts = ['<li><a href="index.html">Home</a></li>']
    for text, link in items:
        parts.append(f'<li>{f"<a href={chr(34)}{link}{chr(34)}>{text}</a>" if link else f"<span aria-current={chr(34)}page{chr(34)}>{text}</span>"}</li>')
    return '<nav class="breadcrumbs" aria-label="Percorso"><ol>' + ''.join(parts) + '</ol></nav>'


def cta(title, lead, *, service='', eyebrow='Richiesta di preventivo', tone=''):
    href = 'contatti.html' + ('?servizio=' + service if service else '')
    inner = f'''<div><p class="eyebrow">{eyebrow}</p><h2 class="display-md" data-reveal>{title}</h2></div><div class="cta-content"><p>{lead}</p>{button('Richiedi un preventivo', href, style='accent')}<span class="cta-note">{SERVICE_LINE}</span></div>'''
    if tone:
        return f'''<section class="contact-cta section contact-cta-{tone}"><div class="container"><div class="cta-layout cta-card">{inner}</div></div></section>'''
    return f'''<section class="contact-cta section"><div class="container cta-layout">{inner}</div></section>'''


def service_row(s, detailed=False):
    extra = (f'<ul class="service-includes">{"".join(f"<li>{title}</li>" for title, _ in s["includes"])}</ul>' if detailed
             else f'<ul class="text-tags">{"".join(f"<li>{tag}</li>" for tag in s["tags"])}</ul>')
    return f'''<article class="service-row" data-reveal>
  <span class="service-number" aria-hidden="true">{s['number']}</span>
  <a class="service-image" href="servizio-{s['slug']}.html" tabindex="-1" aria-hidden="true">{image(s['image'], '', sizes='(max-width: 760px) calc(100vw - 72px), 34vw', style=s['position'])}</a>
  <div class="service-description"><p class="eyebrow">{s['short']}</p><h3><a href="servizio-{s['slug']}.html">{s['name']}{ARROW}</a></h3><p>{s['for']}</p>{extra}</div>
</article>'''


def faq(items):
    return '<div class="faq-list">' + ''.join(f'<details><summary>{q}<span class="faq-toggle" aria-hidden="true"></span></summary><div class="faq-answer"><p>{a}</p></div></details>' for q, a in items) + '</div>'


def home():
    body = f'''<section class="home-hero">
  <div class="container hero-layout">
    <div class="hero-copy"><p class="eyebrow hero-kicker" data-entrance="0"><span class="eyebrow-line"></span>Trasporto merci su strada</p>
      <h1 class="display-xl" data-entrance="1">Ogni carico<br>merita un viaggio <span class="accent-word">pulito.</span></h1>
      <p class="hero-intro" data-entrance="2">Da San Ferlino spostiamo la merce delle aziende: camion dedicati, pallet in groupage, magazzino in conto terzi. Per una spedizione sola o per quelle di tutti i lunedì.</p>
      <div class="hero-actions" data-entrance="3">{button('Richiedi un preventivo', 'contatti.html')}<a class="text-link" href="#servizi">Guarda i servizi <span aria-hidden="true">↓</span></a></div>
      <div class="hero-footnote" data-entrance="4">{PIN}<span>Chiaravia Trasporti e Logistica<br><strong>San Ferlino (Piemonte)</strong></span></div>
    </div>
    <figure class="hero-visual" data-entrance="2">
      <div class="hero-photo">{image('hero-camion', 'Un autoarticolato con semirimorchio furgonato percorre una strada extraurbana', eager=True, sizes='(max-width: 760px) calc(100vw - 40px), (min-width: 1560px) 650px, 42vw')}</div>
      <figcaption class="hero-image-caption"><span class="caption-index" aria-hidden="true">C.</span><span>Dicci cosa parte.<br><strong>Al resto pensiamo noi.</strong></span><a href="contatti.html" aria-label="Descrivi il tuo carico">{ARROW}</a></figcaption>
    </figure>
  </div>
</section>

<section class="services-section section" id="servizi" aria-labelledby="services-heading">
  <div class="container"><div class="section-heading"><div><p class="eyebrow">I servizi</p><h2 class="display-md" id="services-heading" data-reveal>Un collo, un camion<br><span class="muted">o un magazzino intero.</span></h2></div><div class="heading-aside"><p>La merce cambia, e cambia il modo giusto di farla viaggiare. Qui trovi cosa comprende ognuno dei tre servizi.</p><a class="text-link" href="servizi.html">Metti a confronto i servizi {ARROW}</a></div></div>
    <div class="service-list">{''.join(service_row(s) for s in SERVICES)}</div>
  </div>
</section>

<section class="method-section section" id="metodo" aria-labelledby="method-heading"><div class="container">
  <div class="method-top"><div><p class="eyebrow">Come lavoriamo</p><h2 class="display-md" id="method-heading" data-reveal>Prima le domande.<br>Poi il camion si mette <span class="light-accent nowrap">in strada.</span></h2></div><p class="method-intro">Una spedizione fila liscia quando i dettagli sono chiari prima della partenza. Li chiariamo con te, uno per volta.</p></div>
  <div class="method-bottom"><figure class="method-photo" data-reveal>{image('piazzale-aereo', 'Vista dall’alto di semirimorchi parcheggiati in ordine in un piazzale logistico', sizes='(max-width: 760px) calc(100vw - 48px), 44vw')}<figcaption>Ritiri, viaggi e consegne.<br>Tutto sotto gli occhi.</figcaption></figure>
    <ol class="process-list"><li data-reveal><span class="process-number">01</span><div><h3>Leggiamo la richiesta</h3><p>Che merce è, quanta, da dove a dove. Oppure cosa va fatto in magazzino.</p></div></li><li data-reveal><span class="process-number">02</span><div><h3>Controlliamo i dettagli</h3><p>Mezzo, orari, accesso al carico. Se manca qualcosa ti chiamiamo.</p></div></li><li data-reveal><span class="process-number">03</span><div><h3>Ti mandiamo la proposta</h3><p>Prezzo, tempi e condizioni scritti, prima di prenotare il viaggio.</p></div></li></ol>
  </div>
</div></section>

<section class="recurring-section section" aria-labelledby="recurring-heading"><div class="container recurring-layout"><div><p class="eyebrow">Spedizioni ricorrenti</p><h2 class="display-md" id="recurring-heading" data-reveal>Spedisci ogni settimana?<br><span class="muted">Mettiamolo in calendario.</span></h2></div><div class="recurring-copy"><p class="body-large">Se le partenze si ripetono, conviene fissarle: giorni di ritiro sempre uguali, prezzi decisi una volta, una persona sola che segue trasporto e magazzino.</p><ul class="recurring-points" data-reveal><li>Ritiri nei giorni stabiliti</li><li>Volumi che cambiano con le stagioni</li><li>Deposito e consegne coordinati</li></ul><a class="text-link" href="servizio-logistica.html">Vedi logistica e magazzino {ARROW}</a></div></div></section>

<section class="faq-section section" aria-labelledby="faq-heading"><div class="container faq-layout"><div><p class="eyebrow">Prima di chiedere un preventivo</p><h2 class="display-sm" id="faq-heading" data-reveal>Domande frequenti</h2><p>La tua domanda non c’è?<br><a class="inline-link" href="contatti.html?servizio=da-valutare">Scrivila nella richiesta.</a></p></div>{faq([
    ('Spedite anche un pallet solo?', 'Sì. Con pallet e colli la merce viaggia in groupage con altre spedizioni e paghi lo spazio che occupa, anche se è un pallet solo.'),
    ('Fate preventivi su tratte particolari?', 'Sì. Scrivi partenza, arrivo, merce e date. Ti rispondiamo con mezzo, tempi e prezzo del viaggio.'),
    ('Potete tenere voi la mia merce?', 'Sì. Con la logistica in conto terzi la riceviamo, la teniamo a scaffale, prepariamo gli ordini e li spediamo.'),
    ('Non so ancora peso e misure. Posso chiedere lo stesso?', 'Sì. Inserisci quello che sai e lascia vuoto il resto. Completiamo i dati insieme prima della proposta.'),
])}</div></section>
{cta('Vuoi un prezzo?<br>Parliamone.', 'Descrivi la tua spedizione in tre passi, con le sole domande che servono per il servizio scelto.')}'''
    page('index.html', 'Chiaravia Trasporti e Logistica — Trasporto merci e magazzino', 'Trasporto merci da San Ferlino: carico dedicato, pallet e colli in groupage, logistica e magazzino. Sito dimostrativo di un’azienda di fantasia.', body, body_class='page-home')


GUIDE = [
    ('Hai abbastanza merce per un camion, o deve viaggiare senza scali.', 'Carico dedicato', 'servizio-carico-dedicato.html'),
    ('Spedisci qualche pallet o un po’ di colli imballati.', 'Pallet e colli', 'servizio-pallet-colli.html'),
    ('Ti manca spazio e ti serve qualcuno che prepari e spedisca gli ordini.', 'Logistica e magazzino', 'servizio-logistica.html'),
    ('Ti servono più servizi insieme, o non sai quale scegliere.', 'Da valutare insieme', 'contatti.html?servizio=da-valutare'),
]


def services():
    body = f'''<section class="page-intro section"><div class="container">{crumbs([('Servizi', '')])}<div class="section-heading"><div><p class="eyebrow">Trasporto merci e logistica</p><h1 class="display-lg" data-entrance="1">Cosa deve<br><span class="muted">partire?</span></h1></div><p class="intro-aside" data-entrance="2">Un collo, un camion pieno, un magazzino da gestire. Ecco cosa trovi in ognuno dei tre servizi.</p></div></div></section>
<section class="all-services"><div class="container"><div class="service-list">{''.join(service_row(s, detailed=True) for s in SERVICES)}</div></div></section>
<section class="guide-section section" aria-labelledby="guide-heading"><div class="container guide-layout"><div><p class="eyebrow">Come scegliere</p><h2 class="display-sm" id="guide-heading" data-reveal>Quale servizio<br><span class="muted">ti serve?</span></h2><p>Parti dalla frase che descrive meglio la tua situazione.</p></div><ul class="guide-list">{''.join(f'<li data-reveal><a href="{href}"><span class="guide-case">{case}</span><span class="guide-answer">{answer}{ARROW}</span></a></li>' for case, answer, href in GUIDE)}</ul></div></section>
{cta('Sai già cosa ti serve?<br>Chiedi il prezzo.', 'Tre passi, solo le domande utili per il servizio scelto. Ti rispondiamo con una proposta scritta.', tone='petrol')}'''
    page('servizi.html', 'Servizi di trasporto e logistica — Chiaravia', 'Carico dedicato, pallet e colli in groupage, logistica e magazzino in conto terzi: cosa comprende ogni servizio.', body, 'servizi')


def service(s):
    title = s['name'].replace(' e magazzino', '<br>e magazzino').replace(' dedicato', '<br>dedicato')
    others = ''.join(f'<a href="servizio-{other["slug"]}.html"><span class="small-index">{other["number"]}</span><span>{other["name"]}</span>{ARROW}</a>' for other in SERVICES if other['slug'] != s['slug'])
    body = f'''<section class="service-hero"><div class="container">{crumbs([('Servizi', 'servizi.html'), (s['name'], '')])}<div class="service-hero-layout"><div class="service-hero-copy"><p class="eyebrow" data-entrance="0"><span class="service-index">{s['number']}</span> Servizi Chiaravia</p><h1 class="display-lg" data-entrance="1">{title}</h1><p class="body-large" data-entrance="2">{s['lead']}</p>{button('Richiedi un preventivo', 'contatti.html?servizio=' + s['slug'], extra='data-entrance="3"')}<p class="service-hero-note">{s['promise']}</p></div><figure class="service-hero-image" data-entrance="2">{image(s['image'], s['alt'], eager=True, style=s['position'])}<figcaption>{s['short']}</figcaption></figure></div></div></section>
<section class="service-context section" aria-labelledby="includes-heading"><div class="container section-heading"><div><p class="eyebrow">Cosa comprende</p><h2 class="display-sm" id="includes-heading" data-reveal>{s['context']}</h2></div><p class="body-large">{s['intro']}</p></div><div class="container"><div class="includes-grid">{''.join(f'<article data-reveal><span class="include-mark" aria-hidden="true"></span><h3>{heading}</h3><p>{copy}</p></article>' for heading, copy in s['includes'])}</div></div></section>
<section class="service-checklist"><div class="container checklist-layout"><p class="checklist-label">Per un preventivo veloce, prepara questi dati:</p><ul class="checklist">{''.join(f'<li>{text}</li>' for text in s['need'])}</ul></div></section>
<section class="related-section section"><div class="container"><div class="related-heading"><p class="eyebrow">Altri servizi</p><a class="text-link" href="servizi.html">Tutti i servizi {ARROW}</a></div><div class="related-links">{others}</div></div></section>
{cta(s['band'][0], s['band'][1], service=s['slug'])}'''
    page(f'servizio-{s["slug"]}.html', f'{s["name"]} — Chiaravia Trasporti e Logistica', s['lead'], body, 'servizi', 'page-service')


TERRITORY = [
    ('Vicino al casello', 'Dal piazzale all’autostrada ci vogliono pochi minuti. I camion non attraversano il centro del paese.'),
    ('Pianura e colline', 'San Ferlino è tra i campi della pianura e le prime colline: strade larghe e accessi facili per i mezzi pesanti.'),
    ('Nel Nord Ovest', 'Da qui i principali poli industriali e logistici del Piemonte si raggiungono in giornata.'),
    ('Un paese piccolo', 'Conosciamo bene le aziende della zona. Molte le serviamo da anni, con gli stessi autisti.'),
]


def company():
    body = f'''<section class="page-intro company-intro section"><div class="container">{crumbs([('Azienda', '')])}<p class="eyebrow" data-entrance="0">Chi siamo</p><h1 class="display-lg" data-entrance="1">Ogni consegna puntuale<br><span class="muted">nasce&nbsp;prima, in ufficio.</span></h1><div class="company-intro-bottom"><p class="body-large" data-entrance="2">Chiaravia Trasporti e Logistica è un’impresa di trasporto merci con sede a San Ferlino, in Piemonte. Camion dedicati, spedizioni di pallet e colli, magazzino in conto terzi: una sola squadra per far arrivare la tua merce.</p></div><figure class="company-banner" data-entrance="3">{image('baie-carico', 'Baie di carico di un edificio logistico', eager=True, sizes='(max-width: 760px) calc(100vw - 48px), min(1432px, 100vw - 128px)')}<figcaption>Ricevere, tenere, spedire.<br>Ogni cosa al suo posto.</figcaption></figure></div></section>
<section class="territory-section section" aria-labelledby="territory-heading"><div class="container"><div class="section-heading"><div><p class="eyebrow">Dove siamo</p><h2 class="display-md" id="territory-heading" data-reveal>Da San Ferlino,<br><span class="muted">sulle strade del <span class="nowrap">Nord Ovest.</span></span></h2></div><p class="body-large">San Ferlino è un paese di fantasia in Piemonte, scelto per questa demo. Il piazzale e il magazzino che descriviamo qui non esistono.</p></div><div class="territory-grid">{''.join(f'<article data-reveal><h3>{heading}</h3><p>{copy}</p></article>' for heading, copy in TERRITORY)}</div></div></section>
<section class="company-services section" aria-labelledby="company-services-heading"><div class="container"><div class="related-heading"><div><p class="eyebrow">Cosa facciamo</p><h2 class="display-sm" id="company-services-heading">Tre servizi,<br><span class="muted">un solo referente.</span></h2></div><a class="text-link" href="servizi.html">Tutti i servizi {ARROW}</a></div><div class="company-service-list">{''.join(f'<a href="servizio-{s["slug"]}.html"><span class="small-index">{s["number"]}</span><span class="company-service-name">{s["name"]}</span><span class="company-service-copy">{s["short"]}</span>{ARROW}</a>' for s in SERVICES)}</div></div></section>
<section class="company-data"><div class="container"><p>{esc(CFG['legal_name'])} · {esc(CFG['legal_address'])} · Dati di fantasia</p></div></section>
{cta('Hai merce da spostare?<br>Scrivici.', 'Raccontaci cosa deve partire e da dove. Ti rispondiamo con una proposta.', tone='light')}'''
    page('azienda.html', 'L’azienda — Chiaravia Trasporti e Logistica', 'Chiaravia Trasporti e Logistica, impresa di trasporto merci e magazzino a San Ferlino. Azienda di fantasia per un sito dimostrativo.', body, 'azienda')


def field(name, label, *, kind='text', required=False, hint='', placeholder='', options=None, attrs='', note='facoltativo'):
    if kind == 'date':
        placeholder = 'gg/mm/aaaa'
        hint = hint or 'Se la data non è ancora decisa, lascia vuoto.'
    req = ' required' if required else ''
    identifier = f'f-{name}'
    described = identifier + '-error' + (' ' + identifier + '-hint' if hint else '')
    common = f'id="{identifier}" name="{name}" aria-describedby="{described}"{req} {attrs}'
    if options:
        control = f'<select {common}>' + ''.join(f'<option value="{esc(value)}">{label}</option>' for value, label in options) + '</select>'
    elif kind == 'textarea':
        control = f'<textarea {common} rows="4" maxlength="2000" placeholder="{esc(placeholder)}"></textarea>'
    else:
        limit = '' if kind == 'date' else f' maxlength="{254 if kind == "email" else 180}"'
        control = f'<input {common} type="{kind}"{limit} placeholder="{esc(placeholder)}">'
    return f'<div class="field"><label for="{identifier}">{label}{" <span class=required-mark>*</span>" if required else f" <span class=optional>({note})</span>"}</label>{control}{f"<p class=field-hint id={identifier}-hint>{hint}</p>" if hint else ""}<p class="field-error" id="{identifier}-error" hidden></p></div>'


def contacts():
    service_choices = ''.join(f'<label class="service-choice"><input type="radio" name="servizio" value="{s["slug"]}" required><span class="choice-indicator" aria-hidden="true"></span><span><strong>{s["name"]}</strong><small>{s["for"]}</small></span><span class="small-index" aria-hidden="true">{s["number"]}</span></label>' for s in SERVICES)
    direct = contact_links()
    body = f'''<section class="contact-intro"><div class="container">{crumbs([('Contatti', '')])}<div class="contact-intro-layout"><div><p class="eyebrow" data-entrance="0">Richiesta di preventivo</p><h1 class="display-lg" data-entrance="1">Partiamo<br><span class="muted">dalla tua merce.</span></h1></div><div class="contact-intro-note"><p>Tre passi e solo le domande che servono al servizio scelto. Recapiti e richiesta sono di prova: nulla viene inviato.</p>{f'<div class="direct-contacts">{direct}</div>' if direct else ''}</div></div></div></section>

<section class="quote-section"><div class="container quote-layout">
  <aside class="quote-sidebar"><ol class="quote-progress" aria-label="Passaggi della richiesta"><li data-progress="0"><span>01</span><div><strong>Il servizio</strong><small>Camion, pallet o magazzino</small></div></li><li data-progress="1"><span>02</span><div><strong>La merce</strong><small>Cosa, quanta, dove</small></div></li><li data-progress="2"><span>03</span><div><strong>I recapiti</strong><small>Nome e un contatto</small></div></li></ol><div class="quote-help"><p class="eyebrow">Ti manca qualche dato?</p><p>Scrivi quello che sai. Il resto lo sistemiamo insieme.</p><a class="inline-link" href="servizi.html">Rileggi i servizi</a></div></aside>
  <div class="quote-main"><noscript><p class="noscript-message">Il modulo guidato funziona con JavaScript attivo. Le informazioni sui servizi restano consultabili nelle pagine dedicate.</p></noscript>
    <form class="quote-form" data-quote-form aria-label="Richiesta di preventivo">
      <p class="form-error-summary" role="alert" data-errors hidden></p>
      <p class="step-announcement sr-only" aria-live="polite" data-step-announcement></p>
      <fieldset class="quote-step" data-step="0" disabled><legend class="sr-only">Scegli un servizio</legend><div class="step-heading"><p class="eyebrow">Passo 1 di 3</p><h2 tabindex="-1">Cosa ti serve?</h2><p>Scegli la voce più vicina alla tua richiesta.</p></div><div class="service-choices">{service_choices}<label class="service-choice"><input type="radio" name="servizio" value="da-valutare" required><span class="choice-indicator" aria-hidden="true"></span><span><strong>Da valutare insieme</strong><small>Ti servono più servizi, o non sai ancora quale fa per te.</small></span><span class="small-index" aria-hidden="true">04</span></label></div><p class="field-error" id="service-error" hidden>Scegli un servizio per andare avanti.</p></fieldset>
      <fieldset class="quote-step" data-step="1" hidden disabled><legend class="sr-only">Descrivi la merce</legend><div class="step-heading"><p class="eyebrow">Passo 2 di 3</p><h2 tabindex="-1" data-detail-heading>Raccontaci la merce.</h2><p>I campi con * sono obbligatori. Gli altri rendono la proposta più precisa.</p></div>
        {field('merce', 'Cosa deve partire?', kind='textarea', required=True, placeholder='Es. 4 pallet di vasetti in vetro, oppure un macchinario in cassa di legno.')}
        <div data-fields-for="transport"><div class="field-grid">{field('da', 'Partenza', required=True, placeholder='Città o CAP', attrs='autocomplete="off"')}{field('a', 'Destinazione', required=True, placeholder='Città o CAP', attrs='autocomplete="off"')}{field('quantita', 'Quantità', required=True, placeholder='Es. 6 pallet o 30 colli')}{field('peso', 'Peso totale', placeholder='Es. circa 1.500 kg')}</div><div class="field-grid">{field('dimensioni', 'Misure', placeholder='Es. 120 × 80 × 140 cm a pallet')}{field('data', 'Data di partenza', kind='date')}</div>{field('frequenza', 'Ogni quanto', options=[('', 'Da definire'), ('singola', 'Una volta sola'), ('settimanale', 'Ogni settimana'), ('mensile', 'Ogni mese'), ('ricorrente', 'Con un’altra cadenza')])}</div>
        <div data-fields-for="logistics"><div class="field-grid">{field('attivita', 'Cosa facciamo in magazzino', required=True, options=[('', 'Scegli un’attività'), ('stoccaggio', 'Deposito in conto terzi'), ('preparazione', 'Preparazione ordini'), ('movimentazione', 'Ricevimento e movimentazione'), ('flusso', 'Deposito e spedizioni insieme'), ('da-definire', 'Da decidere insieme')])}{field('volumi', 'Volumi di massima', placeholder='Es. circa 40 pallet al mese')}{field('cadenza', 'Entrate e uscite', options=[('', 'Da definire'), ('giornaliera', 'Ogni giorno'), ('settimanale', 'Ogni settimana'), ('mensile', 'Ogni mese'), ('variabile', 'Variabile o stagionale')])}{field('avvio', 'Quando partire', placeholder='Es. da marzo, oppure da concordare')}</div></div>
        <div data-fields-for="unsure">{field('contesto', 'Cosa vuoi organizzare?', placeholder='Es. una nuova linea di consegne o spedizioni fisse', hint='Puoi scrivere tratte, quantità o attività da valutare.')}</div>
      </fieldset>
      <fieldset class="quote-step" data-step="2" hidden disabled><legend class="sr-only">Aggiungi i tuoi recapiti</legend><div class="step-heading"><p class="eyebrow">Passo 3 di 3</p><h2 tabindex="-1">A chi rispondiamo?</h2><p>Servono il tuo nome e un recapito, email o telefono.</p></div><div class="field-grid">{field('nome', 'Nome e cognome', required=True, attrs='autocomplete="name"')}{field('azienda', 'Azienda', attrs='autocomplete="organization"')}{field('email', 'Email', kind='email', placeholder='nome@azienda.it', attrs='autocomplete="email"', note='o telefono')}{field('telefono', 'Telefono', kind='tel', placeholder='Fisso o cellulare', attrs='autocomplete="tel" inputmode="tel"', note='o email')}</div><p class="field-error" id="contact-error" hidden>Scrivi almeno un’email o un numero di telefono.</p><div class="request-preview"><p class="eyebrow">La richiesta in breve</p><dl data-mini-summary></dl><button class="inline-button" type="button" data-edit-details>Modifica i dettagli {ARROW}</button></div><p class="form-privacy">Nel sito vero questi dati servirebbero solo a rispondere. Qui non escono dal browser. <a class="inline-link" href="privacy.html">Nota privacy</a></p></fieldset>
      <div class="form-actions" data-form-actions hidden><button class="back-button" type="button" data-prev>{ARROW} Indietro</button><button class="button button-primary" type="button" data-next><span>Avanti</span>{ARROW}</button><button class="button button-primary" type="button" data-finish hidden><span>Vedi il riepilogo</span>{ARROW}</button></div>
    </form>
    <section class="quote-result" data-result hidden aria-labelledby="result-heading"><p class="eyebrow">Riepilogo della richiesta</p><h2 class="display-sm" id="result-heading" tabindex="-1">Ecco cosa arriverebbe<br>al nostro ufficio.</h2><div class="summary-sheet" data-summary-sheet></div><p class="result-message">Sito dimostrativo: la richiesta non viene inviata a nessuno.</p><div class="result-actions"><button class="button button-outline" type="button" data-copy><span>Copia il testo</span></button><button class="button button-outline" type="button" data-download><span>Scarica .txt</span><span aria-hidden="true">↓</span></button></div><p class="copy-feedback" role="status" data-copy-feedback></p><div class="result-secondary"><button class="inline-button" type="button" data-edit-request>Modifica la richiesta</button><button class="inline-button" type="button" data-new-request>Nuova richiesta</button></div></section>
  </div>
</div></section>'''
    page('contatti.html', 'Richiedi un preventivo — Chiaravia Trasporti e Logistica', 'Preventivo per carico dedicato, pallet e colli o logistica e magazzino: tre passi con le sole domande utili. Modulo dimostrativo, non invia dati.', body, 'contatti', 'page-contact')


def privacy():
    body = f'''<section class="legal-page section"><div class="container">{crumbs([('Privacy e cookie', '')])}<p class="eyebrow">Nota privacy</p><h1 class="display-lg">Privacy e cookie.</h1><div class="legal-copy legal-short"><p>Questo è il sito dimostrativo di un’azienda che non esiste. Non usa cookie di profilazione né strumenti di statistica e non carica nulla da servizi esterni: font, immagini e script sono ospitati insieme alle pagine.</p><p>I dati scritti nel modulo servono solo a comporre il riepilogo sullo schermo. Non vengono inviati né salvati. Il servizio di hosting può registrare dati tecnici delle visite, come l’indirizzo IP.</p><p>Un sito reale avrebbe qui l’informativa completa del titolare del trattamento.</p><a class="text-link" href="contatti.html">Torna alla richiesta di preventivo {ARROW}</a></div></div></section>'''
    page('privacy.html', 'Privacy e cookie — Chiaravia', 'Nota privacy del sito dimostrativo: nessun cookie di profilazione, nessuna risorsa esterna, nessun dato inviato dal modulo.', body)


def not_found():
    body = f'''<section class="not-found section"><div class="container not-found-layout"><div><p class="eyebrow">Errore 404 · Pagina non trovata</p><h1 class="display-lg">Questa strada<br>non porta da nessuna parte.</h1><p>L’indirizzo può essere cambiato o non esistere più. Riparti dalla home o scegli il servizio che ti interessa.</p><div class="hero-actions">{button('Torna alla home', 'index.html')}<a class="text-link" href="servizi.html">Tutti i servizi {ARROW}</a></div></div><nav class="not-found-links" aria-label="Servizi"><p class="eyebrow">I servizi</p>{''.join(f'<a href="servizio-{item["slug"]}.html"><span class="small-index">{item["number"]}</span><span>{item["name"]}</span>{ARROW}</a>' for item in SERVICES)}</nav></div></section>'''
    page('404.html', 'Pagina non trovata — Chiaravia', 'Pagina non trovata: riparti dalla home o dai servizi.', body)


def build():
    PAGES.clear()
    home()
    services()
    for item in SERVICES:
        service(item)
    company()
    contacts()
    privacy()
    not_found()
    namespace = 'http://www.sitemaps.org/schemas/sitemap/0.9'
    ET.register_namespace('', namespace)
    root = ET.Element(f'{{{namespace}}}urlset')
    for path in sorted(PAGES):
        item = ET.SubElement(root, f'{{{namespace}}}url')
        ET.SubElement(item, f'{{{namespace}}}loc').text = CFG['url'].rstrip('/') + ('/' if path == 'index.html' else '/' + path)
    ET.indent(root, space='  ')
    ET.ElementTree(root).write(ROOT / 'sitemap.xml', encoding='utf-8', xml_declaration=True)
    (ROOT / 'robots.txt').write_text('# Sito dimostrativo di un’azienda di fantasia: escluso dai motori di ricerca.\nUser-agent: *\nDisallow: /\n', encoding='utf-8')
    print(f'Chiaravia: {len(PAGES)} pagine + 404 generate. Demo senza invio dati; indicizzazione disattivata.')


if __name__ == '__main__':
    build()
