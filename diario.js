'use strict';
(() => {
  const $ = (selector) => document.querySelector(selector);
  const regions = ['Argentina', 'Uruguay', 'Costa Rica', 'España', 'Mundo'];
  const sectionIds = {Política:'politica',Economía:'economia',Fútbol:'futbol',Básquetbol:'basquetbol',Tenis:'tenis',Tech:'tech',IA:'ia',Viajes:'viajes'};
  const themeButton = $('.theme-toggle');
  function syncTheme() {
    const dark = document.documentElement.dataset.theme === 'dark';
    themeButton.setAttribute('aria-label', dark ? 'Activar modo día' : 'Activar modo noche');
    themeButton.querySelector('span').textContent = dark ? '☼' : '☾';
    $('.theme-label').textContent = dark ? 'Modo día' : 'Modo noche';
  }
  syncTheme();
  themeButton.addEventListener('click', () => {
    const theme = document.documentElement.dataset.theme === 'dark' ? 'light' : 'dark';
    document.documentElement.dataset.theme = theme;
    try { localStorage.setItem('diario-theme', theme); } catch (_) { /* Theme works without storage. */ }
    syncTheme();
  });
  function node(tag, className, value) {
    const el = document.createElement(tag);
    if (className) el.className = className;
    if (value !== undefined) el.textContent = value;
    return el;
  }
  function externalURL(value) {
    try { const url = new URL(value); return ['https:', 'http:'].includes(url.protocol) ? url.href : null; } catch (_) { return null; }
  }
  function link(text, href, className) {
    const el = node('a', className, text); el.href = href; return el;
  }
  async function getJSON(path) {
    const response = await fetch(path, {cache:'no-cache'});
    if (!response.ok) throw new Error(`No se pudo cargar ${path} (${response.status})`);
    return response.json();
  }
  function dateLabel(date, options = {}) {
    return new Intl.DateTimeFormat('es-AR', {timeZone:'America/Costa_Rica', day:'numeric', month:'long', year:'numeric', ...options}).format(new Date(date));
  }
  function dayLabel(date) { return dateLabel(`${date}T12:00:00-06:00`, {weekday:'long'}); }
  function relative(date, reference = Date.now()) {
    const minutes = Math.max(0, Math.floor((reference - new Date(date).getTime()) / 60000));
    if (minutes < 1) return 'recién';
    if (minutes < 60) return `hace ${minutes} min`;
    if (minutes < 1440) return `hace ${Math.floor(minutes / 60)} h`;
    return `hace ${Math.floor(minutes / 1440)} d`;
  }
  let referenceTime = Date.now();
  let archived = false;
  function article(item, kind = 'small') {
    const el = node('article', kind);
    const href = externalURL(item.url);
    if (!href) return el;
    const kicker = node('p', 'kicker');
    if (kind !== 'section-story') {
      kicker.append(node('span', '', item.section), node('span', 'dot', '·'));
    }
    kicker.append(node('span', 'kicker-region', item.region));
    const title = node(kind === 'lead' ? 'h1' : 'h3', 'headline');
    title.append(link(item.title, href));
    const meta = node('div', 'article-meta');
    meta.append(node('span', 'outlet', item.outlet));
    if (item.independent) {
      const badge = node('span', 'badge', 'independiente');
      badge.title = 'Medio independiente según el criterio editorial del diario';
      meta.append(badge);
    }
    meta.append(node('span', '', '·'));
    const time = node('time', '', relative(item.published_at, referenceTime));
    time.dateTime = item.published_at;
    time.title = dateLabel(item.published_at, {hour:'2-digit',minute:'2-digit'}) + (archived ? ' · Tiempo relativo al cierre de esta edición' : '');
    meta.append(time);
    let picture;
    if (item.image && /^assets\/noticias\/[a-f0-9]+\.(jpg|png|webp)$/.test(item.image)) {
      picture = node('img', 'article-image'); picture.src = item.image; picture.alt = '';
      picture.loading = kind === 'lead' ? 'eager' : 'lazy';
      picture.decoding = 'async';
      if (kind === 'lead') picture.fetchPriority = 'high';
      picture.addEventListener('error', () => { const figure = picture.closest('figure'); (figure || picture).remove(); });
    }
    if (kind === 'featured' && picture) el.append(picture);
    el.append(kicker, title);
    if (kind === 'lead' && item.excerpt) el.append(node('p', 'excerpt', item.excerpt));
    el.append(meta);
    if (kind === 'lead' && picture) {
      const figure = node('figure');
      figure.append(picture, node('figcaption', 'image-caption', 'Imagen publicada por ' + (item.image_credit || item.outlet)));
      el.append(figure);
    }
    if (kind === 'lead' && item.coverage?.length > 1) el.append(node('p','coverage',`En agenda en ${item.coverage.length} medios · ${item.coverage.join(' / ')}`));
    return el;
  }
  function renderRegions(items) {
    const tabs = $('#region-tabs');
    function select(region) {
      for (const button of tabs.children) button.setAttribute('aria-pressed', String(button.textContent === region));
      const target = $('#region-results'); target.replaceChildren();
      const matching = items.filter(item => item.region === region).slice(0, 4);
      matching.forEach(item => target.append(article(item)));
      if (!matching.length) target.append(node('p', 'empty-section', 'Esta edición no tiene notas seleccionadas de esta región.'));
    }
    regions.forEach(region => {
      const button = node('button', '', region); button.type = 'button';
      button.addEventListener('click', () => select(region)); tabs.append(button);
    });
    select(regions[0]);
  }
  async function renderDiario() {
    const date = new URLSearchParams(location.search).get('fecha');
    if (date && !/^\d{4}-\d{2}-\d{2}$/.test(date)) throw new Error('La fecha solicitada no es válida. Volvé al archivo para elegir una edición.');
    archived = Boolean(date);
    const data = await getJSON(date ? `data/archivo/${date}.json` : 'data/diario.json');
    if (!data.lead || !Array.isArray(data.destacadas) || !data.sections) throw new Error('La edición está incompleta. Probá de nuevo en un rato.');
    referenceTime = archived ? new Date(data.generated_at).getTime() : Date.now();
    $('#edition-date').textContent = dayLabel(data.date);
    $('#edition-status').textContent = archived ? 'Una mirada a ese día' : 'Tu lectura del día';
    $('#updated').textContent = `Cierre ${new Intl.DateTimeFormat('es-AR', {timeZone:data.timezone, hour:'2-digit',minute:'2-digit',hourCycle:'h23'}).format(new Date(data.generated_at))} · Costa Rica`;
    document.title = `Diario Celeste — ${dayLabel(data.date)}`;
    if (archived) {
      const banner = $('#archive-banner'); banner.hidden = false;
      banner.append(document.createTextNode('Estás leyendo una edición guardada. Los tiempos corresponden a su cierre. '), link('Volvé al diario de hoy ↗', 'index.html'));
    } else if (Date.now()-new Date(data.generated_at).getTime() > 36*3600000) {
      const banner = $('#stale-banner'); banner.hidden = false;
      banner.textContent = `Última edición disponible: ${dayLabel(data.date)}. Todavía no hay una actualización más reciente.`;
    }
    $('#lead').append(article(data.lead, 'lead'));
    data.resumen.forEach(line => $('#summary').append(node('li', '', line)));
    $('#summary-note').textContent = data.resumen_method === 'claude' ? 'Resumen generado con IA a partir de los titulares.' : 'Una selección de titulares de esta edición.';
    data.destacadas.forEach(item => $('#featured').append(article(item, 'featured')));
    Object.entries(sectionIds).forEach(([name, id], index) => {
      const section = node('section', 'news-section'); section.id = id;
      section.setAttribute('aria-labelledby', id + '-title');
      const heading = node('h2', '', name); heading.id = id + '-title';
      heading.append(node('span', 'section-number', String(index+1).padStart(2,'0')));
      section.append(heading);
      const items = data.sections[name] || [];
      items.forEach(item => section.append(article(item, 'section-story')));
      if (items.length < 4) section.append(node('p','empty-section',items.length ? 'Hay pocas novedades verificadas en las últimas 36 horas. Volvé en la próxima edición.' : 'Sin novedades verificadas en las últimas 36 horas. Volvé en la próxima edición.'));
      $('#sections').append(section);
    });
    renderRegions([data.lead, ...data.destacadas, ...Object.values(data.sections).flat()]);
    $('#news').hidden = false;
  }
  async function renderArchive() {
    const entries = await getJSON('data/archivo/index.json');
    if (!entries.length) $('#archive-list').append(node('p', 'notice', 'Esta es nuestra primera edición. Las anteriores van a aparecer acá después de la próxima actualización.'));
    entries.forEach(entry => {
      if (!/^\d{4}-\d{2}-\d{2}$/.test(entry.date)) return;
      const card = link('', `index.html?fecha=${entry.date}`, 'archive-card');
      const time = node('time', '', dayLabel(entry.date)); time.dateTime = entry.date;
      card.append(time, node('h2', '', entry.lead), node('p', '', `${entry.count} noticias · Abrí esta edición ↗`));
      $('#archive-list').append(card);
    });
  }
  async function renderSources() {
    const [sources, verification] = await Promise.all([getJSON('sources.json'), getJSON('data/feed-verification.json')]);
    $('#source-list').append(node('p','small-label','Última comprobación: '+dateLabel(verification.checked_at,{hour:'2-digit',minute:'2-digit'})));
    regions.forEach(region => {
      const section = node('section', 'source-region'); section.append(node('h2', '', region));
      const table = node('table', 'source-table'); const head = node('thead'); const row = node('tr');
      ['Medio', 'Temas', 'Independiente', 'RSS'].forEach(label => { const th = node('th', '', label); th.scope='col'; row.append(th); }); head.append(row); table.append(head);
      const body = node('tbody');
      sources.filter(source => source.region === region).forEach(source => {
        const row = node('tr'); const name = node('td');
        name.append(link(source.outlet, externalURL(source.rss) || '#'));
        const status = node('td', source.verified ? 'feed-ok':'feed-error', source.verified ? 'Verificado':'No disponible');
        row.append(name, node('td', '', source.topics.join(' · ')), node('td', '', source.independent ? 'Sí':'No'), status);
        body.append(row);
      });
      table.append(body); section.append(table); $('#source-list').append(section);
    });
  }
  const render = {diario:renderDiario, archivo:renderArchive, fuentes:renderSources}[document.body.dataset.page];
  render().then(() => { $('#loading').hidden = true; }).catch(error => {
    const loading = $('#loading'); loading.className = 'notice'; loading.setAttribute('role','alert');
    loading.replaceChildren(node('p','',error.message), link('Volvé a la portada', 'index.html'));
  });
})();
