/* Тема, навигация, фильтры, просмотр фотографий, формы и метки источника. Без внешних библиотек. */
'use strict';

const SVG = (d, w = 1.7) => `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="${w}" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">${d}</svg>`;
const ICON = {
 close: SVG('<path d="M18 6 6 18M6 6l12 12"/>'),
 prev: SVG('<path d="m15 18-6-6 6-6"/>'),
 next: SVG('<path d="m9 18 6-6-6-6"/>')
};

/* ── Тема ──────────────────────────────────────────────────── */
const root = document.documentElement;
const themeButton = document.querySelector('.theme-toggle');
const systemDark = matchMedia('(prefers-color-scheme: dark)');
const isDark = () => root.dataset.theme ? root.dataset.theme === 'dark' : systemDark.matches;
function paintTheme() {
 // Класс нужен, чтобы иконка солнца/луны совпадала и при системной тёмной теме без явного выбора.
 root.classList.toggle('theme-dark', isDark());
 themeButton?.setAttribute('aria-label', isDark() ? 'Включить светлую тему' : 'Включить тёмную тему');
}
themeButton?.addEventListener('click', () => {
 root.dataset.theme = isDark() ? 'light' : 'dark';
 try { localStorage.setItem('theme', root.dataset.theme); } catch (e) {}
 paintTheme();
});
systemDark.addEventListener('change', paintTheme);
paintTheme();

/* ── Блокировка прокрутки под меню и просмотрщиком ─────────── */
let locks = 0;
function lockScroll(on) {
 locks = Math.max(0, locks + (on ? 1 : -1));
 const gap = innerWidth - root.clientWidth;
 document.body.style.overflow = locks ? 'hidden' : '';
 document.body.style.paddingRight = locks && gap > 0 ? gap + 'px' : '';
}

/* ── Навигация ─────────────────────────────────────────────── */
const menuButton = document.querySelector('.menu-toggle');
const navigation = document.querySelector('.nav');
const isMobileNav = () => getComputedStyle(menuButton).display !== 'none';
let menuLocked = false;
function setMenu(open) {
 const was = navigation.classList.contains('open');
 if (was === open) return;
 navigation.classList.toggle('open', open);
 menuButton.setAttribute('aria-expanded', String(open));
 menuButton.setAttribute('aria-label', open ? 'Закрыть меню' : 'Открыть меню');
 // Снимать замок нужно по тому, ставили ли мы его, а не по текущей ширине экрана:
 // иначе поворот телефона меняет вёрстку на широкую, разблокировка не срабатывает
 // и страница остаётся непрокручиваемой.
 if (open && isMobileNav()) { menuLocked = true; lockScroll(true); }
 else if (!open && menuLocked) { menuLocked = false; lockScroll(false); }
}
function closeSubmenus() {
 document.querySelectorAll('.nav-group.open').forEach(el => {
  el.classList.remove('open');
  el.querySelector('button').setAttribute('aria-expanded', 'false');
 });
}
menuButton.addEventListener('click', () => setMenu(!navigation.classList.contains('open')));
document.querySelectorAll('.submenu-toggle').forEach(button => button.addEventListener('click', () => {
 const group = button.closest('.nav-group'), open = !group.classList.contains('open');
 closeSubmenus();
 group.classList.toggle('open', open);
 button.setAttribute('aria-expanded', String(open));
}));
document.addEventListener('click', event => {
 if (!event.target.closest('.header')) { setMenu(false); closeSubmenus(); }
});
document.addEventListener('keydown', event => {
 if (event.key !== 'Escape') return;
 const open = document.querySelector('.nav-group.open');
 if (open) { const b = open.querySelector('button'); closeSubmenus(); b.focus(); }
 else if (navigation.classList.contains('open')) { setMenu(false); menuButton.focus(); }
});
navigation.querySelectorAll('a').forEach(a => a.addEventListener('click', () => setMenu(false)));
function releaseMenu() {
 if (isMobileNav()) return;
 if (navigation.classList.contains('open')) setMenu(false);
 if (menuLocked) { menuLocked = false; lockScroll(false); }
}
addEventListener('resize', releaseMenu);
addEventListener('orientationchange', releaseMenu);
// matchMedia срабатывает ровно в момент смены раскладки — надёжнее, чем resize,
// который на мобильных браузерах приходит не всегда.
matchMedia('(min-width: 1024px)').addEventListener('change', releaseMenu);
// Возврат «назад» из кеша браузера не перезапускает скрипт: снимаем замок вручную,
// иначе страница откроется незрокручиваемой.
addEventListener('pageshow', () => {
 if (!navigation.classList.contains('open') && menuLocked) { menuLocked = false; lockScroll(false); }
});

/* ── Фильтры ───────────────────────────────────────────────── */
document.querySelectorAll('.filter-section').forEach(section => {
 const buttons = section.querySelectorAll('[data-filter]');
 const cards = section.querySelectorAll('.filter-card');
 const status = section.querySelector('.filter-status');
 const total = cards.length;
 const apply = button => {
  buttons.forEach(b => b.setAttribute('aria-pressed', String(b === button)));
  let count = 0;
  cards.forEach(card => {
   const visible = button.dataset.filter === 'Все' || card.dataset.category === button.dataset.filter;
   card.hidden = !visible;
   if (visible) {
    count++;
    // Перезапуск анимации появления, чтобы переключение читалось как движение, а не рывок.
    card.style.animation = 'none';
    void card.offsetWidth;
    card.style.animation = '';
   }
  });
  status.textContent = count === total ? `Показано объектов: ${total}` : `Показано объектов: ${count} из ${total}`;
 };
 buttons.forEach(button => button.addEventListener('click', () => apply(button)));
 apply(section.querySelector('[data-filter][aria-pressed=true]') || buttons[0]);
});

/* ── Предзаполнение форм из адреса страницы ────────────────── */
const params = new URLSearchParams(location.search);
const purposeMap = { warehouse: 'Склад', repair: 'Ремонтная мастерская', production: 'Производство', vehicles: 'Техника', sport: 'Спорт', agriculture: 'Сельское хозяйство' };
const incomingPurpose = purposeMap[params.get('purpose')];
if (incomingPurpose) document.querySelectorAll('[name="purpose"]').forEach(el => el.value = incomingPurpose);
const projectId = params.get('project');
if (projectId) fetch('/js/content-map.json').then(r => r.json()).then(map => {
 if (!Object.prototype.hasOwnProperty.call(map, projectId)) return;
 document.querySelectorAll('.form-context').forEach(el => { el.hidden = false; el.textContent = 'Выбранный проект: ' + map[projectId].title; });
}).catch(() => {});
if (params.has('ready') || params.get('type') === 'ready') document.querySelectorAll('.form-context').forEach(el => {
 el.hidden = false;
 el.textContent = 'Запрос по готовому ангару' + (params.has('ready') ? ' · ' + params.get('ready') : '');
});

/* ── Формы ─────────────────────────────────────────────────── */
document.querySelectorAll('form').forEach(form => {
 const phone = form.querySelector('[name="phone"]');
 phone?.addEventListener('input', () => phone.setCustomValidity(''));
 // Колесо мыши над числовым полем меняло значение при обычной прокрутке страницы.
 form.querySelectorAll('input[type="number"]').forEach(input =>
  input.addEventListener('wheel', () => { if (document.activeElement === input) input.blur(); }, { passive: true }));
 form.querySelectorAll('input[type="file"]').forEach(input => {
  const remove = input.parentElement.querySelector('.remove-file');
  input.addEventListener('change', () => remove.hidden = !input.files.length);
  remove.addEventListener('click', () => { input.value = ''; remove.hidden = true; input.focus(); });
 });
 form.addEventListener('submit', async event => {
  event.preventDefault();
  if (phone && phone.value.replace(/\D/g, '').length < 7) {
   phone.setCustomValidity('Укажите номер телефона');
   phone.reportValidity();
   phone.setCustomValidity('');
   return;
  }
  const status = form.querySelector('.form-status');
  const button = form.querySelector('[type=submit]');
  status.hidden = false;
  button.disabled = true;
  status.textContent = 'Отправляем…';
  try {
   await sendForm(form);
   form.querySelector('.form-grid').hidden = true;
   form.querySelector('.form-bottom').hidden = true;
   status.textContent = 'Заявка отправлена. Свяжемся с вами в течение рабочего дня.';
  } catch (err) {
   status.textContent = 'Не удалось отправить. Позвоните нам: +7 (930) 918-30-75';
   button.disabled = false;
  }
 });
});

/* ── Просмотр фотографий ───────────────────────────────────── */
const photoLinks = [...document.querySelectorAll('[data-photo]')];
if (photoLinks.length) {
 const dialog = document.createElement('dialog');
 dialog.className = 'photo-dialog';
 dialog.setAttribute('aria-label', 'Просмотр фотографии');
 dialog.innerHTML =
  `<div class="photo-dialog-toolbar">
    <p class="photo-dialog-caption"></p>
    <span class="photo-dialog-counter"></span>
    <button type="button" class="photo-dialog-close" aria-label="Закрыть просмотр">${ICON.close}</button>
   </div>
   <div class="photo-dialog-stage">
    <button type="button" class="photo-nav photo-prev" aria-label="Предыдущая фотография">${ICON.prev}</button>
    <img class="photo-dialog-image" alt="">
    <button type="button" class="photo-nav photo-next" aria-label="Следующая фотография">${ICON.next}</button>
   </div>`;
 document.body.append(dialog);

 const image = dialog.querySelector('.photo-dialog-image');
 const caption = dialog.querySelector('.photo-dialog-caption');
 const counter = dialog.querySelector('.photo-dialog-counter');
 const prevButton = dialog.querySelector('.photo-prev');
 const nextButton = dialog.querySelector('.photo-next');
 let group = [], index = 0, lastLink = null;

 // Соседние снимки одной галереи; скрытые фильтром не участвуют в перелистывании.
 const groupOf = link => {
  const box = link.closest('.image-gallery, .album-grid, .case-gallery');
  const pool = box ? [...box.querySelectorAll('[data-photo]')] : photoLinks;
  return pool.filter(a => !a.closest('[hidden]'));
 };
 const preload = i => { const a = group[i]; if (a) new Image().src = a.href; };

 function show(i) {
  index = (i + group.length) % group.length;
  const link = group[index];
  const w = Number(link.dataset.w) || 0;
  // Не растягиваем мелкий исходник: ограничиваем его натуральной шириной.
  image.style.maxWidth = w ? `min(100%, ${w}px)` : '100%';
  image.src = link.href;
  image.alt = link.dataset.caption || '';
  caption.textContent = link.dataset.caption || '';
  counter.textContent = `${index + 1} / ${group.length}`;
  dialog.dataset.single = String(group.length < 2);
  prevButton.disabled = nextButton.disabled = group.length < 2;
  preload(index + 1);
  preload(index - 1);
 }

 const open = link => { lastLink = link; group = groupOf(link); show(group.indexOf(link)); dialog.showModal(); lockScroll(true); };
 photoLinks.forEach(a => a.addEventListener('click', event => { event.preventDefault(); open(a); }));
 prevButton.addEventListener('click', () => show(index - 1));
 nextButton.addEventListener('click', () => show(index + 1));
 dialog.querySelector('.photo-dialog-close').addEventListener('click', () => dialog.close());
 dialog.addEventListener('click', event => { if (event.target === dialog || event.target.classList.contains('photo-dialog-stage')) dialog.close(); });
 dialog.addEventListener('keydown', event => {
  if (event.key === 'ArrowLeft') { event.preventDefault(); show(index - 1); }
  if (event.key === 'ArrowRight') { event.preventDefault(); show(index + 1); }
 });
 dialog.addEventListener('close', () => { image.removeAttribute('src'); lockScroll(false); lastLink?.focus(); });

 // Листание свайпом на телефоне.
 let startX = 0, startY = 0;
 dialog.addEventListener('touchstart', e => { startX = e.touches[0].clientX; startY = e.touches[0].clientY; }, { passive: true });
 dialog.addEventListener('touchend', e => {
  const dx = e.changedTouches[0].clientX - startX, dy = e.changedTouches[0].clientY - startY;
  if (Math.abs(dx) > 50 && Math.abs(dx) > Math.abs(dy)) show(index + (dx < 0 ? 1 : -1));
 }, { passive: true });
}

/* ── Плавающая кнопка обратной связи ─────────────────────── */
{
 const fab = document.querySelector('[data-fab]');
 if (fab) {
  const toggle = fab.querySelector('.fab-toggle');
  const set = open => {
   fab.classList.toggle('open', open);
   toggle.setAttribute('aria-expanded', String(open));
  };
  toggle.addEventListener('click', () => set(!fab.classList.contains('open')));
  document.addEventListener('click', e => { if (!fab.contains(e.target)) set(false); });
  document.addEventListener('keydown', e => {
   if (e.key === 'Escape' && fab.classList.contains('open')) { set(false); toggle.focus(); }
  });

  // У подвала кнопка убирается: там уже есть телефон, почта и мессенджер,
  // а висящий кружок перекрывает подпись и реквизиты.
  const footer = document.querySelector('.footer');
  if (footer && 'IntersectionObserver' in window) {
   new IntersectionObserver(entries => {
    const atFooter = entries[0].isIntersecting;
    if (atFooter) set(false);
    fab.classList.toggle('fab-tucked', atFooter);
   }, { rootMargin: '0px 0px -40px 0px' }).observe(footer);
  }
 }
}

/* ── Цели Яндекс.Метрики: звонки и переходы в контакты ─────── */
(function () {
 const goal = (name) => { try { if (window.ym && window.YM_ID) ym(window.YM_ID, 'reachGoal', name); } catch (e) {} };
 document.addEventListener('click', event => {
  const el = event.target.closest('a,button');
  if (!el) return;
  // Явная метка на элементе имеет приоритет над догадкой по ссылке.
  const explicit = el.dataset.goal;
  if (explicit) goal(explicit);
  const href = el.getAttribute('href') || '';
  if (href.startsWith('tel:')) goal('call_click');
  else if (/^\/contacts\/?$/.test(href)) goal('contacts_view');
 }, { capture: true });
 // Заявка обычной формы (квиз шлёт свою цель сам).
 document.querySelectorAll('form:not([data-quiz])').forEach(f =>
  f.addEventListener('submit', () => goal('form_submit')));
})();

/* ── Метки источника ───────────────────────────────────────── */
/* Параметры перехода запоминаются на весь визит: человек приходит по рекламе
   на любую страницу, а заявку оставляет позже на /raschet/ — метка не должна потеряться. */
(function () {
 const KEYS = ['utm_source', 'utm_medium', 'utm_campaign', 'utm_content', 'utm_term'];
 const store = (k, v) => { try { sessionStorage.setItem(k, v); } catch (e) {} };
 const load = (k) => { try { return sessionStorage.getItem(k) || ''; } catch (e) { return ''; } };

 const q = new URLSearchParams(location.search);
 KEYS.forEach(k => { const v = q.get(k); if (v) store(k, v); });
 // Источник перехода запоминаем только при первом заходе, иначе его затрёт свой же домен.
 if (!load('referrer')) store('referrer', document.referrer || 'прямой заход');

 document.querySelectorAll('[data-utm]').forEach(input => {
  input.value = input.dataset.utm === 'referrer' ? load('referrer') : load(input.dataset.utm);
 });
 document.querySelectorAll('[data-page]').forEach(input => {
  input.value = location.pathname + location.search;
 });
})();

/* Письмо должно читаться человеком, поэтому поля уезжают с русскими подписями,
   а не как name="utm_source". FormSubmit подставляет ключи JSON прямо в письмо. */
const FIELD_LABELS = {
 name: 'Имя', phone: 'Телефон', email: 'Почта', company: 'Компания',
 purpose: 'Назначение ангара', location: 'Место строительства', comment: 'Комментарий',
 tender: 'Закупка', messenger: 'Удобен мессенджер', answers: 'Ответы на вопросы',
 page: 'Страница заявки', referrer: 'Источник перехода',
 utm_source: 'Источник', utm_medium: 'Канал', utm_campaign: 'Кампания',
 utm_content: 'Объявление', utm_term: 'Запрос'
};
const SERVICE_FIELDS = ['_subject', '_template', '_captcha', '_honey'];
const SKIP_FIELDS = ['consent', '_honey'];
function buildPayload(form) {
 const data = {};
 new FormData(form).forEach((value, key) => {
  if (typeof value !== 'string' || !value.trim()) return;
  if (SKIP_FIELDS.includes(key)) return;
  if (SERVICE_FIELDS.includes(key)) { data[key] = value; return; }
  // Ответы квиза уже собраны в читаемый блок «Ответы на вопросы»,
  // поэтому сырые поля шагов (q0_purpose и подобные) в письмо не дублируем.
  if (/^q\d+_/.test(key)) return;
  const label = FIELD_LABELS[key] || key;
  data[label] = data[label] ? data[label] + ', ' + value : value;
 });
 ['_subject', '_template', '_captcha'].forEach(k => {
  const el = form.querySelector(`[name="${k}"]`);
  if (el) data[k] = el.value;
 });
 return data;
}
// Сервис может на мгновение отказать при всплеске обращений — делаем одну
// повторную попытку, терять заявку из-за секундного сбоя нельзя.
window.sendForm = async function (form) {
 // Скрытую галочку видят только боты. Отсекаем на своей стороне и молча:
 // бот не должен понять, что его отбраковали, а квота сервиса не тратится.
 const honey = form.querySelector('[name="_honey"]');
 if (honey && honey.checked) return { success: 'true', skipped: true };
 const body = JSON.stringify(buildPayload(form));
 let last;
 for (let attempt = 0; attempt < 2; attempt++) {
  if (attempt) await new Promise(r => setTimeout(r, 1500));
  try {
   const res = await fetch(form.action, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
    body
   });
   const out = await res.json().catch(() => ({}));
   if (res.ok && out.success !== 'false' && out.success !== false) return out;
   last = new Error(out.message || res.status);
  } catch (err) {
   last = err;
  }
 }
 throw last;
}
