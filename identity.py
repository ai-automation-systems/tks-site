"""Название, телефон и реквизиты, полученные от партнёра. Применяется ко всем сгенерированным страницам."""
import re
LOGO='<svg class="tks-symbol" viewBox="0 0 40 40" fill="none" aria-hidden="true"><path d="M4 33V15L20 6l16 9v18M11 33V19l9-5 9 5v14M4 33h32" stroke="currentColor" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round"/></svg><span class="tks-wordmark">ТКС</span><span class="tks-description">Тентово-каркасные<br>сооружения</span>'
LEGAL='<div class="shell footer-legal"><strong>ООО «Воронежская строительная компания-Гарант»</strong><div class="legal-numbers"><span>ИНН 3662258649</span><span>КПП 366201001</span><span>ОГРН 1183668001879</span></div><p>Юридический адрес: 394020, г. Воронеж, ул. Антонова-Овсеенко, дом 1, кв. 30.</p></div>'
def apply_identity(html):
 html=re.sub(r'(<a class="brand"[^>]*>).*?</a>',lambda m:m.group(1)+LOGO+'</a>',html,flags=re.S)
 html=html.replace('Тентовые конструкции','ТКС — Тентово-каркасные сооружения')
 html=html.replace('tel:+78006004626','tel:+79309183075')
 for old in ['8 800 600-46-26','8 800 600–46–26','8 (800) 600-46-26']:
  html=html.replace(old,'+7 (930) 918-30-75')
 html=html.replace('+7 800 600-46-26','+7 930 918-30-75')
 html=re.sub(r'<div class="header-contact">.*?</div>','<a class="header-phone" href="tel:+79309183075">+7 (930) 918-30-75</a>',html,flags=re.S)
 html=html.replace('<div class="shell footer-bottom">',LEGAL+'<div class="shell footer-bottom">')
 return html
