# Chiaravia Trasporti e Logistica — sito dimostrativo

> **Azienda di fantasia.** Chiaravia Trasporti e Logistica e il paese di San Ferlino non esistono. Nomi, recapiti, indirizzo e testi sono inventati. Il sito è una demo realizzata da [Michele Modica](https://www.modicamichele.it) per mostrare come potrebbe presentarsi online un'impresa di trasporto merci e logistica.

**Online:** https://gxmich.github.io/chiaravia-trasporti-demo/

## Cosa mostra la demo

- **Home** con tre servizi presentati come righe editoriali (carico dedicato, pallet e colli, logistica e magazzino), metodo di lavoro in tre passi, spedizioni ricorrenti e domande frequenti.
- **Pagina servizi** con la guida «Quale servizio ti serve?» e **tre pagine servizio** che spiegano cosa comprende ogni servizio prima di chiedere i dati.
- **Richiesta di preventivo in tre passi**: le domande cambiano in base al servizio (trasporto, magazzino o caso da valutare), con errori legati ai campi, preselezione del servizio dall'URL e un riepilogo finale strutturato da copiare o scaricare come testo. È simulata: nessun dato viene inviato o salvato.
- Menu mobile con `dialog` e gestione del focus, azione rapida su telefono, animazioni leggere che rispettano «riduci movimento».

Tutte le pagine hanno `noindex, nofollow` e `robots.txt` blocca l'indicizzazione: un'azienda inventata non deve comparire nelle ricerche.

## Tecnologie

HTML, CSS e JavaScript senza framework né librerie esterne. Font Sora e Figtree ospitati in locale. Le pagine vengono generate da `build.py` (solo libreria standard di Python) a partire dai contenuti e da `site.config.json`.

## Avviarla in locale

```bash
python build.py               # rigenera le pagine HTML, sitemap e robots.txt
python -m http.server 8771    # poi apri http://localhost:8771
```

Stile e comportamento sono in `assets/site.css` e `assets/site.js`. Crediti delle foto in [CREDITI-FOTO.md](CREDITI-FOTO.md). Il sito è pubblicato con GitHub Pages dal ramo `main`.
