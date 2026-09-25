/* Локальный макет: тема, навигация, фильтры, просмотр фотографий, проверка форм. Внешних зависимостей нет. */
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
function setMenu(open) {
 const was = navigation.classList.contains('open');
 if (was === open) return;
 navigation.classList.toggle('open', open);
 menuButton.setAttribute('aria-expanded', String(open));
 menuButton.setAttribute('aria-label', open ? 'Закрыть меню' : 'Открыть меню');
 if (isMobileNav()) lockScroll(open);
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
addEventListener('resize', () => { if (!isMobileNav() && navigation.classList.contains('open')) setMenu(false); });

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
 if (!Object.hasOwn(map, projectId)) return;
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
 form.addEventListener('submit', event => {
  event.preventDefault();
  if (phone && phone.value.replace(/\D/g, '').length < 7) {
   phone.setCustomValidity('Укажите номер телефона');
   phone.reportValidity();
   return;
  }
  const status = form.querySelector('.form-status');
  status.hidden = false;
  status.textContent = 'Поля заполнены. Это локальный макет: заявка не отправлена. Данные остались в форме.';
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
 }
}
