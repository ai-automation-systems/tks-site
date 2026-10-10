/* Пошаговый расчёт: переключение шагов, прогресс, сбор ответов и отправка без перезагрузки. */
'use strict';

(function () {
 const form = document.querySelector('[data-quiz]');
 if (!form) return;

 const intro = form.querySelector('.quiz-intro');
 const steps = [...form.querySelectorAll('.quiz-step')];
 const nav = form.querySelector('.quiz-nav');
 const bar = form.querySelector('[data-bar]');
 const percent = form.querySelector('[data-percent]');
 const nextLabel = form.querySelector('[data-next-label]');
 const backButton = form.querySelector('.quiz-back');
 const status = form.querySelector('.form-status');
 const goal = (name) => { try { if (window.ym && window.YM_ID) ym(window.YM_ID, 'reachGoal', name); } catch (e) {} };

 let current = -1;            // -1 — стартовый экран
 const LAST = steps.length - 1;
 const isFinal = (step) => step.hasAttribute('data-final');
 let moving = false;

 function show(i) {
  current = i;
  intro.hidden = i >= 0;
  nav.hidden = i < 0;
  steps.forEach((s, n) => { s.hidden = n !== i; });
  if (i < 0) return;
  const step = steps[i];
  const p = Number(step.dataset.progress || 0);
  bar.style.width = p + '%';
  percent.textContent = p + '%';
  nextLabel.textContent = isFinal(step) ? 'Получить расчёт'
   : (i === LAST - 1 ? 'Последний шаг' : 'Далее');
  backButton.hidden = i === 0;
  form.querySelector('.quiz-body').scrollIntoView({ block: 'nearest', behavior: 'smooth' });
  const first = step.querySelector('input:not([type=hidden]),textarea');
  if (first && step.querySelector('textarea')) first.focus({ preventScroll: true });
  if (isFinal(step)) goal('quiz_finish');
 }

 // Шаг пройден, если он помечен необязательным или на нём есть ответ.
 function filled(step) {
  if (step.hasAttribute('data-skippable')) return true;
  const area = step.querySelector('textarea');
  if (area) return area.value.trim().length > 0;
  return !!step.querySelector('input:checked');
 }

 function warn(step) {
  step.classList.add('quiz-step-warn');
  setTimeout(() => step.classList.remove('quiz-step-warn'), 1200);
 }

 form.querySelector('.quiz-start').addEventListener('click', () => { goal('quiz_start'); show(0); });
 backButton.addEventListener('click', () => show(Math.max(0, current - 1)));

 // «Другое» открывает своё поле ввода только когда отмечено.
 form.querySelectorAll('[data-other]').forEach(box => {
  const text = box.closest('label').querySelector('.quiz-other-input');
  box.addEventListener('change', () => {
   text.disabled = !box.checked;
   if (box.checked) text.focus();
  });
 });

 form.querySelectorAll('textarea[maxlength]').forEach(area => {
  const out = area.closest('.quiz-field').querySelector('[data-count]');
  area.addEventListener('input', () => { out.textContent = area.value.length; });
 });

 function collect() {
  const lines = [];
  steps.forEach(step => {
   if (isFinal(step)) return;
   const title = step.querySelector('h2').textContent.trim();
   const area = step.querySelector('textarea');
   let value;
   if (area) value = area.value.trim();
   else {
    const picked = [...step.querySelectorAll('input:checked')].map(i => {
     if (!i.hasAttribute('data-other')) return i.value;
     const extra = i.closest('label').querySelector('.quiz-other-input').value.trim();
     return extra ? 'Другое: ' + extra : i.value;
    });
    value = picked.join(', ');
   }
   lines.push([title, value || 'не указано']);
  });
  return lines;
 }

 function advance() {
  if (moving) return;
  const step = steps[current];
  if (!filled(step)) return warn(step);
  if (current < LAST) {
   moving = true;
   show(current + 1);
   setTimeout(() => { moving = false; }, 300);
  }
 }

 form.addEventListener('submit', async event => {
  event.preventDefault();
  const step = steps[current];
  if (!isFinal(step)) return advance();

  const phone = form.querySelector('[name=phone]');
  const name = form.querySelector('[name=name]');
  const consent = form.querySelector('[name=consent]');
  if (!name.value.trim()) return name.reportValidity();
  if (!window.checkPhone(phone)) return;
  const email = form.querySelector('[name=email]');
  if (email && !email.checkValidity()) return email.reportValidity();
  if (!consent.checked) return consent.reportValidity();

  // Каждый вопрос уходит отдельной строкой письма, см. buildPayload в main.js.
  form.quizAnswers = collect();
  const button = form.querySelector('.quiz-next');
  button.disabled = true;
  status.hidden = false;
  status.textContent = 'Отправляем…';

  try {
   await window.sendForm(form);
   goal('form_submit');
   form.querySelector('.quiz-body').hidden = true;
   nav.hidden = true;
   status.className = 'form-status quiz-done';
   status.textContent = 'Заявка отправлена. Свяжемся с вами в течение рабочего дня.';
  } catch (err) {
   status.textContent = 'Не удалось отправить. Позвоните нам: +7 (930) 918-30-75';
   button.disabled = false;
  }
 });

 // Enter листает вперёд, но не внутри многострочного поля.
 form.addEventListener('keydown', event => {
  if (event.key === 'Enter' && event.target.tagName !== 'TEXTAREA' && current >= 0 && !isFinal(steps[current])) {
   event.preventDefault();
   advance();
  }
 });
})();
