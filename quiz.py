"""Пошаговый расчёт стоимости. Структура повторяет квиз с tentsbv.ru/task/,
но собран в коде: без сторонних скриптов, в типографике сайта, заявка уходит
тем же маршрутом, что и обычная форма, вместе с UTM-метками.

Разметка отдаётся целиком, шаги переключает js/quiz.js — без JS страница
остаётся читаемой, а контакты доступны обычной формой ниже.
"""
from pathlib import Path
import json, html
from img_tag import picture

ROOT = Path(__file__).resolve().parent
SPEC = json.loads((ROOT/'content/quiz.json').read_text())
INTRO_PHOTO = '/img/projects-2026/kovdor-warehouse.jpg'


def e(s):
    return html.escape(str(s), quote=True)


def _tip(text):
    """Пояснение к шагу. Карточки эксперта с именем и фото убраны по решению заказчика."""
    paras = ''.join(f'<p>{e(p)}</p>' for p in text.split('\n') if p.strip())
    return f'<div class="quiz-tip">{paras}</div>'


def _options(step, idx):
    kind = 'checkbox' if step['type'] == 'multi' or step.get('multi') else 'radio'
    name = f'q{idx}_{step["id"]}'
    out = []
    for n, opt in enumerate(step.get('options', [])):
        label = opt['label'] if isinstance(opt, dict) else opt
        img = ''
        if isinstance(opt, dict) and opt.get('img'):
            img = (f'<span class="quiz-card-media">'
                   f'<img src="/img/quiz/{e(opt["img"])}" alt="" width="840" height="840" '
                   f'loading="lazy" decoding="async"></span>')
        out.append(
            f'<label class="quiz-option{" quiz-option-card" if img else ""}">'
            f'<input type="{kind}" name="{name}" value="{e(label)}">'
            f'{img}<span class="quiz-option-label">{e(label)}</span></label>')
    if step.get('other'):
        out.append(
            f'<label class="quiz-option quiz-option-other">'
            f'<input type="checkbox" name="{name}" value="{e(SPEC["ui"]["otherLabel"])}" data-other>'
            f'<span class="quiz-option-label">{e(SPEC["ui"]["otherLabel"])}</span>'
            f'<input type="text" class="quiz-other-input" name="{name}_other" '
            f'aria-label="{e(SPEC["ui"]["otherLabel"])}" disabled></label>')
    cls = 'quiz-cards' if step['type'] == 'cards' else 'quiz-list'
    return f'<div class="{cls}">' + ''.join(out) + '</div>'


def _step(step, idx, total):
    head = f'<p class="quiz-step-num">Шаг {idx + 1} из {total}</p><h2>{e(step["title"])}</h2>'
    marks = []
    if step.get('hint'):
        marks.append(f'<span class="quiz-hint">{e(step["hint"])}</span>')
    if step.get('skippable'):
        marks.append(f'<span class="quiz-skip">{e(SPEC["ui"]["skipLabel"])}</span>')
    head += f'<div class="quiz-marks">{"".join(marks)}</div>' if marks else ''
    body = _tip(step['tip']) if step.get('tip') else ''
    if step['type'] == 'text':
        body += (f'<label class="quiz-field"><span class="sr-only">{e(step["title"])}</span>'
                 f'<textarea name="q{idx}_{step["id"]}" rows="4" '
                 f'maxlength="{step.get("maxlength", 1000)}" '
                 f'placeholder="{e(step.get("placeholder", ""))}"></textarea>'
                 f'<span class="quiz-counter"><span data-count>0</span> / {step.get("maxlength", 1000)}</span>'
                 f'</label>')
    else:
        body += _options(step, idx)
    return (f'<section class="quiz-step" data-step="{idx}" data-progress="{step.get("progress", 0)}"'
            f'{" data-skippable" if step.get("skippable") else ""} hidden>'
            f'{head}{body}</section>')


def _consent(text):
    """Слова о политике ведут на саму политику — в новой вкладке, чтобы не потерять ответы."""
    words = 'политике конфиденциальности'
    return e(text).replace(words, f'<a href="/privacy/" target="_blank">{words}</a>', 1)


def _contacts(idx, total):
    c = SPEC['contacts']
    rows = []
    for f in c['fields']:
        req = ' required' if f.get('required') else ''
        star = ' <em>*</em>' if f.get('required') else ''
        if f['name'] == 'phone':
            # Код страны уже стоит перед полем; маску и проверку «с 9 или 4» ведёт main.js.
            ctrl = (f'<span class="phone-field"><span class="phone-prefix" aria-hidden="true">{e(f["prefix"])}</span>'
                    f'<input type="tel" name="phone" inputmode="numeric" autocomplete="tel" '
                    f'placeholder="(900) 000-00-00" data-phone{req}></span>')
        else:
            t = 'email' if f['name'] == 'email' else 'text'
            ac = {'name': 'name', 'email': 'email'}.get(f['name'], '')
            ctrl = (f'<input type="{t}" name="{e(f["name"])}" placeholder="{e(f.get("placeholder", ""))}"'
                    f'{f" autocomplete={ac}" if ac else ""}{req}>')
        rows.append(f'<label class="quiz-field"><span>{e(f["label"])}{star}</span>{ctrl}</label>')
    return (f'<section class="quiz-step quiz-contacts" data-step="{idx}" data-progress="100" data-final hidden>'
            f'<p class="quiz-step-num">Шаг {total} из {total}</p>'
            f'<h2>{e(c["title"])}</h2><p class="quiz-sub">{e(c["subtitle"])}</p>'
            f'<div class="quiz-contact-grid">{"".join(rows)}</div>'
            f'<label class="quiz-check"><input type="checkbox" name="messenger" value="Да">'
            f'<span>{e(c["messenger"])}</span></label>'
            f'<label class="quiz-check"><input type="checkbox" name="consent" value="Да" required>'
            f'<span>{_consent(c["consent"])}</span></label>'
            f'</section>')


def quiz(uid='quiz', form_key='', endpoint='', utm_fields=(), arrow=''):
    i = SPEC['intro']
    steps = SPEC['steps']
    total = len(steps) + 1
    intro = (f'<section class="quiz-intro" data-step="intro">'
             '<div class="quiz-intro-media">'+picture(INTRO_PHOTO,'',sizes='hero',eager=True)+'</div>'
             f'<div class="quiz-intro-body"><p class="quiz-badge">{e(i["badge"])}</p>'
             f'<h2>{e(i["title"])}</h2><ul class="quiz-bullets">'
             + ''.join(f'<li>{e(b)}</li>' for b in i['bullets'])
             + f'</ul><button type="button" class="button quiz-start">{e(i["button"])}{arrow}</button>'
             f'</div></section>')
    hidden = ('<input type="hidden" name="_subject" value="Расчёт с сайта t-karkas.ru">'
              '<input type="hidden" name="_template" value="table">'
              '<input type="hidden" name="_captcha" value="false">'
              '<input type="checkbox" name="_honey" style="display:none" tabindex="-1" aria-hidden="true" autocomplete="off">'
              + ''.join(f'<input type="hidden" name="{n}" data-utm="{n}">' for n in utm_fields)
              + '<input type="hidden" name="page" data-page>')
    body = ''.join(_step(s, n, total) for n, s in enumerate(steps)) + _contacts(len(steps), total)
    nav = (f'<div class="quiz-nav" hidden>'
           f'<div class="quiz-progress"><span class="quiz-progress-label">{e(SPEC["ui"]["progressLabel"])} '
           f'<b data-percent>0%</b></span><span class="quiz-progress-track"><i data-bar></i></span></div>'
           f'<div class="quiz-nav-buttons">'
           f'<button type="button" class="quiz-back" aria-label="Назад"></button>'
           f'<button type="submit" class="button quiz-next">'
           f'<span data-next-label>{e(SPEC["ui"]["next"])}</span>{arrow}</button></div></div>')
    note = ''
    return (f'<form class="quiz" id="{uid}" action="{endpoint}" method="post" novalidate '
            f'data-quiz data-steps="{total}">{hidden}{intro}'
            f'<div class="quiz-body">{body}</div>{nav}{note}'
            f'<p class="form-status" role="status" hidden></p></form>')
