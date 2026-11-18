/* Chiaravia (demo): native navigation, restrained motion, and a local-only request builder. */
(() => {
  'use strict';
  document.documentElement.classList.add('has-js');
  const motion = window.matchMedia('(prefers-reduced-motion: reduce)');
  const running = new Set();
  const ease = 'cubic-bezier(.22, 1, .36, 1)';

  function animate(element, frames, options = {}) {
    if (motion.matches || !element?.animate) return;
    const animation = element.animate(frames, { duration: 560, easing: ease, ...options });
    running.add(animation);
    animation.finished.then(() => running.delete(animation), () => running.delete(animation));
    return animation;
  }
  motion.addEventListener('change', () => {
    if (motion.matches) running.forEach(animation => animation.cancel());
  });

  document.querySelectorAll('[data-year]').forEach(element => {
    element.textContent = String(new Date().getFullYear());
  });

  /* The dialog provides native focus containment and Escape handling. */
  const menu = document.querySelector('[data-mobile-menu]');
  const menuToggle = document.querySelector('[data-menu-toggle]');
  if (menu && menuToggle) {
    const closeMenu = () => menu.close();
    menuToggle.addEventListener('click', () => {
      if (menu.open) return closeMenu();
      menu.showModal();
      menuToggle.setAttribute('aria-expanded', 'true');
      menu.querySelector('[data-menu-close]').focus({ preventScroll: true });
      animate(menu.querySelector('nav'), [
        { opacity: 0, transform: 'translateY(14px)' },
        { opacity: 1, transform: 'translateY(0)' },
      ], { duration: 280 });
    });
    menu.querySelector('[data-menu-close]').addEventListener('click', closeMenu);
    menu.addEventListener('click', event => {
      if (event.target.closest('a[href]')) closeMenu();
    });
    menu.addEventListener('keydown', event => {
      if (event.key !== 'Tab' || event.ctrlKey || event.altKey || event.metaKey) return;
      const controls = [...menu.querySelectorAll('a[href], button:not([disabled])')]
        .filter(element => element.getClientRects().length);
      if (!controls.length) return;
      const index = controls.indexOf(document.activeElement);
      const nextIndex = event.shiftKey
        ? (index <= 0 ? controls.length - 1 : index - 1)
        : (index + 1) % controls.length;
      event.preventDefault();
      controls[nextIndex].focus();
    });
    menu.addEventListener('close', () => {
      menuToggle.setAttribute('aria-expanded', 'false');
      menuToggle.focus({ preventScroll: true });
    });
    window.matchMedia('(min-width: 1001px)').addEventListener('change', event => {
      if (event.matches && menu.open) closeMenu();
    });
  }

  /* Keep the mobile action available when the main actions are outside view. */
  const header = document.querySelector('[data-header]');
  const mobileAction = document.querySelector('[data-mobile-action]');
  const visibleActions = new Set();
  let footerVisible = false;
  let scrollQueued = false;
  const updateScrollState = () => {
    const scrollY = window.scrollY;
    header?.classList.toggle('is-scrolled', scrollY > 12);
    mobileAction?.classList.toggle('is-visible', scrollY > 200 && !visibleActions.size && !footerVisible);
    scrollQueued = false;
  };
  window.addEventListener('scroll', () => {
    if (!scrollQueued) {
      scrollQueued = true;
      requestAnimationFrame(updateScrollState);
    }
  }, { passive: true });
  if ('IntersectionObserver' in window) {
    const actionObserver = new IntersectionObserver(entries => {
      entries.forEach(entry => {
        if (entry.target.matches('.site-footer')) footerVisible = entry.isIntersecting;
        else if (entry.isIntersecting) visibleActions.add(entry.target);
        else visibleActions.delete(entry.target);
      });
      updateScrollState();
    }, { rootMargin: `-${header?.offsetHeight || 0}px 0px 0px 0px` });
    document.querySelectorAll('main a.button[href^="contatti.html"], .site-footer').forEach(element => actionObserver.observe(element));
  }
  updateScrollState();

  /* Opening sequence lives in CSS (data-entrance), so it starts with the first paint.
     Scroll reveals only hide groups that start below the fold: nothing visible at load
     ever blinks, and every group is shown again if motion is turned off. */
  if ('IntersectionObserver' in window) {
    const pending = new Set();
    const reveal = element => {
      pending.delete(element);
      element.classList.remove('reveal-pending');
      animate(element, [
        { opacity: 0, transform: 'translateY(22px)' },
        { opacity: 1, transform: 'translateY(0)' },
      ]);
    };
    const revealObserver = new IntersectionObserver(entries => {
      entries.forEach(entry => {
        if (!entry.isIntersecting) return;
        revealObserver.unobserve(entry.target);
        if (pending.has(entry.target)) reveal(entry.target);
      });
    }, { threshold: 0.08, rootMargin: '0px 0px -4% 0px' });
    const fold = window.innerHeight * 0.94;
    document.querySelectorAll('[data-reveal]').forEach(element => {
      if (motion.matches || element.getBoundingClientRect().top < fold) return;
      element.classList.add('reveal-pending');
      pending.add(element);
      revealObserver.observe(element);
    });
    motion.addEventListener('change', () => {
      if (!motion.matches) return;
      pending.forEach(element => element.classList.remove('reveal-pending'));
      pending.clear();
    });
  }
  document.querySelectorAll('.faq-list details').forEach(details => {
    details.addEventListener('toggle', () => {
      if (details.open) animate(details.querySelector('.faq-answer'), [
        { opacity: 0, transform: 'translateY(-4px)' },
        { opacity: 1, transform: 'translateY(0)' },
      ], { duration: 220 });
    });
  });

  const form = document.querySelector('[data-quote-form]');
  if (!form) return;
  const steps = [...form.querySelectorAll('[data-step]')];
  const progress = [...document.querySelectorAll('[data-progress]')];
  const next = form.querySelector('[data-next]');
  const previous = form.querySelector('[data-prev]');
  const finish = form.querySelector('[data-finish]');
  const errors = form.querySelector('[data-errors]');
  const result = document.querySelector('[data-result]');
  const summarySheet = document.querySelector('[data-summary-sheet]');
  const copyFeedback = document.querySelector('[data-copy-feedback]');
  const fieldsFor = [...form.querySelectorAll('[data-fields-for]')];
  const serviceNames = {
    'carico-dedicato': 'Carico dedicato',
    'pallet-colli': 'Pallet e colli',
    'logistica': 'Logistica e magazzino',
    'da-valutare': 'Da valutare insieme',
  };
  let current = 0;
  let exportText = '';
  let copyReset;

  const field = name => form.elements.namedItem(name);
  const value = name => String(field(name)?.value || '').trim();
  const selectedLabel = name => {
    const control = field(name);
    return control?.value ? control.selectedOptions[0].textContent.trim() : '';
  };
  const normaliseDate = raw => {
    let year, month, day;
    let match = /^(\d{4})-(\d{2})-(\d{2})$/.exec(raw);
    if (match) [, year, month, day] = match;
    else {
      match = /^(\d{1,2})[/.](\d{1,2})[/.](\d{4})$/.exec(raw);
      if (!match) return '';
      [, day, month, year] = match;
    }
    const parsed = new Date(Number(year), Number(month) - 1, Number(day));
    if (parsed.getFullYear() !== Number(year) || parsed.getMonth() !== Number(month) - 1 || parsed.getDate() !== Number(day)) return '';
    return `${year}-${String(month).padStart(2, '0')}-${String(day).padStart(2, '0')}`;
  };
  const service = () => value('servizio');
  const clearErrors = () => {
    form.querySelectorAll('[aria-invalid]').forEach(element => element.removeAttribute('aria-invalid'));
    form.querySelectorAll('.field-error').forEach(element => { element.hidden = true; });
    errors.hidden = true;
    errors.textContent = '';
  };

  function syncServiceFields() {
    const type = service() === 'logistica' ? 'logistics' : service() === 'da-valutare' ? 'unsure' : 'transport';
    fieldsFor.forEach(group => {
      const active = group.dataset.fieldsFor === type;
      group.hidden = !active;
      group.querySelectorAll('input, select, textarea').forEach(input => { input.disabled = !active; });
    });
    const headings = {
      'carico-dedicato': 'Quale carico deve partire?',
      'pallet-colli': 'Quanti pallet o colli spedisci?',
      'logistica': 'Cosa dobbiamo gestire in magazzino?',
      'da-valutare': 'Raccontaci cosa ti serve.',
    };
    form.querySelector('[data-detail-heading]').textContent = headings[service()] || 'Parliamo della tua merce.';
  }

  const formatDate = raw => raw ? new Date(`${raw}T12:00:00`).toLocaleDateString('it-IT', { day: 'numeric', month: 'long', year: 'numeric' }) : '';

  /* The finished request is grouped the way an office would read it. */
  function summarySections() {
    const sections = [['Merce', [['Descrizione', value('merce')]]]];
    if (service() === 'logistica') {
      sections.push(['Magazzino', [['Servizio richiesto', selectedLabel('attivita')], ['Volumi', value('volumi')], ['Entrate e uscite', selectedLabel('cadenza')], ['Avvio previsto', value('avvio')]]]);
    } else if (service() === 'da-valutare') {
      sections[0][1].push(['Da organizzare', value('contesto')]);
    } else {
      sections[0][1].push(['Quantità', value('quantita')], ['Peso', value('peso')], ['Dimensioni', value('dimensioni')]);
      sections.push(['Viaggio', [['Partenza', value('da')], ['Destinazione', value('a')], ['Data desiderata', formatDate(value('data'))], ['Frequenza', selectedLabel('frequenza')]]]);
    }
    sections.push(['Contatto', [['Nome', value('nome')], ['Azienda', value('azienda')], ['Email', value('email')], ['Telefono', value('telefono')]]]);
    return sections.map(([title, rows]) => [title, rows.filter(([, text]) => text)]).filter(([, rows]) => rows.length);
  }

  function definitionList(entries) {
    const dl = document.createElement('dl');
    entries.forEach(([label, text]) => {
      const row = document.createElement('div');
      const dt = document.createElement('dt');
      const dd = document.createElement('dd');
      dt.textContent = label;
      dd.textContent = text;
      row.append(dt, dd);
      dl.append(row);
    });
    return dl;
  }

  function renderMiniSummary() {
    const mini = form.querySelector('[data-mini-summary]');
    const entries = [['Servizio', serviceNames[service()] || 'Da valutare insieme']];
    if (service() === 'logistica') {
      entries.push(['Magazzino', selectedLabel('attivita') || 'Da definire']);
      if (value('volumi')) entries.push(['Volumi', value('volumi')]);
    } else if (service() !== 'da-valutare') {
      entries.push(['Percorso', `${value('da')} → ${value('a')}`], ['Quantità', value('quantita')]);
    } else entries.push(['Richiesta', value('merce')]);
    mini.replaceChildren(...definitionList(entries).children);
  }

  /* Align the progress (phone) or the form card (desktop) below the sticky header,
     so the step label is never hidden. Skip the jump when it is already in place. */
  const compact = window.matchMedia('(max-width: 760px)');
  function bringFormIntoView() {
    const target = compact.matches ? document.querySelector('.quote-sidebar') : document.querySelector('.quote-main');
    if (!target) return;
    const offset = (header?.offsetHeight || 0) + 16;
    const top = target.getBoundingClientRect().top;
    if (top >= offset - 4 && top < window.innerHeight * 0.35) return;
    window.scrollTo({ top: Math.max(0, window.scrollY + top - offset), behavior: motion.matches ? 'auto' : 'smooth' });
  }

  function showStep(index, moveFocus = true) {
    clearErrors();
    current = index;
    steps.forEach((step, i) => {
      step.hidden = i !== current;
      step.disabled = i !== current;
    });
    syncServiceFields();
    progress.forEach((item, i) => {
      item.classList.toggle('is-complete', i < current);
      if (i === current) item.setAttribute('aria-current', 'step');
      else item.removeAttribute('aria-current');
    });
    previous.hidden = current === 0;
    next.hidden = current === 2;
    finish.hidden = current !== 2;
    if (current === 2) renderMiniSummary();
    if (moveFocus) {
      const heading = steps[current].querySelector('h2');
      heading.focus({ preventScroll: true });
      bringFormIntoView();
      form.querySelector('[data-step-announcement]').textContent = `Passaggio ${current + 1} di 3. ${heading.textContent}`;
      animate(steps[current], [
        { opacity: 0, transform: 'translateY(10px)' },
        { opacity: 1, transform: 'translateY(0)' },
      ], { duration: 280 });
    }
  }

  function markError(input, message) {
    input.setAttribute('aria-invalid', 'true');
    const messageElement = document.getElementById(`${input.id}-error`);
    if (messageElement) {
      messageElement.textContent = message;
      messageElement.hidden = false;
    }
  }

  function validateStep() {
    clearErrors();
    let firstInvalid = null;
    if (current === 0 && !service()) {
      const radios = [...form.querySelectorAll('[name="servizio"]')];
      radios.forEach(radio => radio.setAttribute('aria-invalid', 'true'));
      document.getElementById('service-error').hidden = false;
      firstInvalid = radios[0];
    }
    steps[current].querySelectorAll('input:enabled, textarea:enabled, select:enabled').forEach(input => {
      if (input.type === 'radio') return;
      input.value = input.value.trim();
      let message = '';
      if (input.required && !input.value) message = input.tagName === 'SELECT' ? 'Scegli una delle opzioni.' : 'Compila questo campo per continuare.';
      else if (input.type === 'email' && input.value && !input.validity.valid) message = 'Inserisci un’email completa, ad esempio nome@azienda.it.';
      else if (input.getAttribute('type') === 'date' && input.value) {
        const date = normaliseDate(input.value);
        if (!date) message = 'Inserisci una data valida nel formato giorno/mese/anno.';
        else if (date < input.min) message = 'Scegli una data da oggi in avanti, oppure lascia il campo vuoto.';
        else input.value = date;
      } else if (input.type === 'tel' && input.value) {
        const digits = input.value.replace(/\D/g, '');
        if (digits.length < 6 || digits.length > 18 || !/^[+()\d\s./-]+$/.test(input.value)) message = 'Inserisci un numero di telefono completo, con eventuale prefisso.';
      } else if (input.value && !input.validity.valid) message = 'Controlla il valore inserito.';
      if (message) {
        markError(input, message);
        firstInvalid ||= input;
      }
    });
    if (current === 2 && !value('email') && !value('telefono')) {
      document.getElementById('contact-error').hidden = false;
      field('email').setAttribute('aria-invalid', 'true');
      field('telefono').setAttribute('aria-invalid', 'true');
      firstInvalid ||= field('email');
    }
    if (!firstInvalid) return true;
    errors.textContent = current === 0 ? 'Scegli un servizio per continuare.' : 'Controlla i campi indicati: manca un’informazione o un dato non è completo.';
    errors.hidden = false;
    firstInvalid.focus();
    return false;
  }

  const goNext = () => {
    if (validateStep()) showStep(Math.min(2, current + 1));
  };
  function completeRequest() {
    if (!validateStep()) return;
    const sections = summarySections();
    const head = document.createElement('div');
    head.className = 'summary-head';
    const title = document.createElement('h3');
    title.textContent = 'Richiesta di preventivo';
    const meta = document.createElement('p');
    const serviceLabel = serviceNames[service()] || 'Da valutare insieme';
    const today = new Date().toLocaleDateString('it-IT', { day: 'numeric', month: 'long', year: 'numeric' });
    meta.textContent = `${serviceLabel} · ${today}`;
    head.append(title, meta);
    const blocks = sections.map(([label, rows]) => {
      const block = document.createElement('section');
      block.className = 'summary-block';
      const blockTitle = document.createElement('h4');
      blockTitle.textContent = label;
      block.append(blockTitle, definitionList(rows));
      return block;
    });
    summarySheet.replaceChildren(head, ...blocks);
    exportText = `CHIARAVIA TRASPORTI E LOGISTICA (azienda di fantasia, richiesta dimostrativa)\nRichiesta di preventivo\nServizio: ${serviceLabel}\nData: ${today}\n\n` + sections.map(([label, rows]) => `${label.toUpperCase()}\n` + rows.map(([key, text]) => `${key}: ${text}`).join('\n')).join('\n\n') + '\n\nDEMO: sito dimostrativo, la richiesta non viene inviata a nessuno.\n';
    form.hidden = true;
    result.hidden = false;
    progress.forEach(item => {
      item.removeAttribute('aria-current');
      item.classList.add('is-complete');
    });
    const resultHeading = document.getElementById('result-heading');
    resultHeading.focus({ preventScroll: true });
    bringFormIntoView();
    animate(result, [{ opacity: 0, transform: 'translateY(12px)' }, { opacity: 1, transform: 'translateY(0)' }], { duration: 280 });
  }

  next.addEventListener('click', goNext);
  previous.addEventListener('click', () => showStep(Math.max(0, current - 1)));
  finish.addEventListener('click', completeRequest);
  form.addEventListener('submit', event => {
    event.preventDefault();
    current === 2 ? completeRequest() : goNext();
  });
  form.addEventListener('keydown', event => {
    if (event.key === 'Enter' && !event.isComposing && event.target.matches('input:not([type="radio"])')) {
      event.preventDefault();
      current === 2 ? completeRequest() : goNext();
    }
  });
  form.addEventListener('input', event => {
    if (event.target.matches('input, select, textarea')) {
      const messageElement = document.getElementById(`${event.target.id}-error`);
      event.target.removeAttribute('aria-invalid');
      if (messageElement) messageElement.hidden = true;
      if (event.target.name === 'email' || event.target.name === 'telefono') {
        document.getElementById('contact-error').hidden = true;
        field('email').removeAttribute('aria-invalid');
        field('telefono').removeAttribute('aria-invalid');
      }
    }
  });
  form.querySelectorAll('[name="servizio"]').forEach(radio => {
    radio.setAttribute('aria-describedby', 'service-error');
    radio.addEventListener('change', () => { clearErrors(); syncServiceFields(); });
  });
  form.querySelector('[data-edit-details]').addEventListener('click', () => showStep(1));
  document.querySelector('[data-edit-request]').addEventListener('click', () => {
    result.hidden = true;
    form.hidden = false;
    copyFeedback.textContent = '';
    showStep(1);
  });
  document.querySelector('[data-new-request]').addEventListener('click', () => {
    clearTimeout(copyReset);
    form.reset();
    exportText = '';
    summarySheet.replaceChildren();
    copyFeedback.textContent = '';
    document.querySelector('[data-copy] span').textContent = 'Copia il testo';
    result.hidden = true;
    form.hidden = false;
    showStep(0);
  });
  document.querySelector('[data-copy]').addEventListener('click', async () => {
    try {
      if (!navigator.clipboard?.writeText) throw new Error('Clipboard unavailable');
      await navigator.clipboard.writeText(exportText);
      document.querySelector('[data-copy] span').textContent = 'Copiato';
      copyFeedback.textContent = 'Testo della richiesta copiato negli appunti.';
      clearTimeout(copyReset);
      copyReset = setTimeout(() => { document.querySelector('[data-copy] span').textContent = 'Copia il testo'; }, 2500);
    } catch {
      copyFeedback.textContent = 'La copia automatica non è disponibile: puoi selezionare il testo o scaricare il file.';
    }
  });
  document.querySelector('[data-download]').addEventListener('click', () => {
    const url = URL.createObjectURL(new Blob([exportText], { type: 'text/plain;charset=utf-8' }));
    const link = document.createElement('a');
    link.href = url;
    link.download = 'chiaravia-richiesta-demo.txt';
    document.body.append(link);
    link.click();
    link.remove();
    setTimeout(() => URL.revokeObjectURL(url), 1000);
    copyFeedback.textContent = 'File della richiesta scaricato sul tuo dispositivo.';
  });

  const initial = new URLSearchParams(window.location.search).get('servizio');
  if (Object.hasOwn(serviceNames, initial)) {
    form.querySelector(`[name="servizio"][value="${initial}"]`).checked = true;
    current = 1;
  }
  field('email').setAttribute('aria-describedby', 'f-email-error contact-error');
  field('telefono').setAttribute('aria-describedby', 'f-telefono-error contact-error');
  const today = new Date();
  field('data').min = `${today.getFullYear()}-${String(today.getMonth() + 1).padStart(2, '0')}-${String(today.getDate()).padStart(2, '0')}`;
  form.noValidate = true;
  form.classList.add('is-ready');
  form.querySelector('[data-form-actions]').hidden = false;
  showStep(current, false);
})();
