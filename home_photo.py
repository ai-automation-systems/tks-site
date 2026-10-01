"""Photo presentation of the homepage; other pages remain text-first."""
import re
from img_tag import picture

ARROW='<svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M7 17 17 7M9 7h8v8"/></svg>'

def apply_home_photos(body,form):
 hero=('<figure class="hero-photo">'
  +picture('/img/generated/hero.jpg','Металлический каркас и кран-балка внутри склада для Иргиредмет в Иркутске',sizes='hero',eager=True)
  +'<div class="photo-label"><span>Иркутск</span><strong>Склад для «Иргиредмет»</strong>'
  +f'<a href="/projects/sklad-18-30-15-irkutsk/">Посмотреть решение{ARROW}</a></div></figure>')
 body=re.sub(r'<aside class="hero-panel">.*?</aside>',lambda m:hero,body,count=1,flags=re.S)
 def change_section(number,fn):
  nonlocal body
  pattern=r'<section\b[^>]*id="section-'+str(number)+r'"[^>]*>.*?</section>'
  body=re.sub(pattern,lambda m:fn(m.group()),body,flags=re.S)
 tech=('<figure class="technology-photo">'
  +picture('/img/generated/frame.jpg','Металлический каркас ремонтной мастерской в Магаданской области на этапе монтажа',sizes='grid-2')
  +'<figcaption>Монтаж каркаса мастерской · Магаданская область</figcaption></figure>')
 change_section(2,lambda s:s.replace('<div class="section-content">','<div class="section-content">'+tech,1))
 prod=('<figure class="production-photo">'
  +picture('/img/generated/production.jpg','Металлоконструкции в производственном цехе компании Тентовые конструкции',sizes='grid-2')
  +'<figcaption><span>Собственное производство</span><strong>Цех металлоконструкций</strong><span>Иркутск</span></figcaption></figure>')
 change_section(3,lambda s:s.replace('<div class="section-content">',prod+'<div class="section-content">',1))
 casephotos=[('/img/generated/repair.jpg','Ремонтная мастерская с синим ПВХ-покрытием в Магаданской области'),('/img/generated/warehouse.jpg','Склад для Иргиредмет в Иркутске'),('/img/generated/sport.jpg','Спортивный комплекс в Петропавловске-Камчатском'),('/img/generated/roof.jpg','Склад со сдвижными секциями кровли в Иркутской области')]
 def cases(s):
  iterator=iter(casephotos)
  def add(m):
   src,alt=next(iterator)
   card=m.group()
   card=re.sub(r'<svg.*?</svg>','',card,count=1,flags=re.S)
   img='<div class="case-photo">'+picture(src,alt,sizes='grid-2')+'</div>'
   return card.replace('<article class="info-card">','<article class="info-card photo-case">'+img,1)
  return re.sub(r'<article class="info-card">.*?</article>',add,s,flags=re.S)
 change_section(4,cases)
 servicephotos=[('/img/projects-2026/kovdor-warehouse.jpg','Строительство склада ТМЦ в Ковдоре'),('/img/projects-2026/nogliki-repair.jpg','Ремонтная мастерская в Ногликах'),('/img/production.jpg','Производственный цех'),('/img/projects-2026/aikhal-machinery.jpg','Ремонтно-стояночный бокс с карьерной техникой в Айхале'),('/img/sport.jpg','Спортивный объект'),('/img/projects-2026/kovdor-frame.jpg','Пример металлического каркаса ангара для хранения')]
 def services(s):
  iterator=iter(servicephotos)
  def add(m):
   src,alt=next(iterator)
   card=re.sub(r'<svg.*?</svg>','',m.group(),count=1,flags=re.S)
   img='<div class="service-photo">'+picture(src,alt,sizes='grid-3')+'</div>'
   return card.replace('<article class="info-card">','<article class="info-card service-card">'+img,1)
  return re.sub(r'<article class="info-card">.*?</article>',add,s,flags=re.S)
 change_section(1,services)
 change_section(8,lambda s:s.replace('</div></div></section>','</div><div class="home-final-form">'+form('short','home-final-form')+'</div></div></section>'))
 return body
