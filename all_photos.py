"""Photo layout for all interior pages; images matched to original manufacturer records."""
from pathlib import Path
import json,re,html
from img_tag import picture,natural,best
ROOT=Path(__file__).resolve().parent
M=json.loads((ROOT/'content/all-photos.json').read_text())
def e(s):return html.escape(str(s),quote=True)
EXPAND='<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M15 3h6v6M21 3l-8 8M9 21H3v-6M3 21l8-8"/></svg>'
def photo(x,cls='',eager=False,caption=None,sizes='grid-3'):
 if not x:return ''
 cap=caption or x['caption']
 src=x['src'];w,h=natural(src)
 # Ссылка ведёт на вариант не шире 1600px; data-w/data-h не дают просмотрщику растянуть мелкий снимок.
 return (f'<figure class="site-photo {cls}"><a class="photo-expand" href="{e(best(src))}" data-photo'
  f' data-caption="{e(cap)}" data-w="{w}" data-h="{h}" aria-label="Увеличить: {e(cap)}">'
  +picture(src,cap,sizes=sizes,eager=eager)
  +f'<span class="expand-mark" aria-hidden="true">{EXPAND}</span></a><figcaption>{e(cap)}</figcaption></figure>')
def grid(xs,cls='',sizes='grid-2'):
 # Подсказка sizes должна соответствовать самой широкой колонке сетки, иначе браузер
 # возьмёт слишком мелкий вариант и снимок будет мылить.
 return '<div class="image-gallery '+cls+'">'+''.join(photo(x,sizes=sizes) for x in xs)+'</div>'
def cp(id,n=0):return M['cases'][id][n]
P=M['production'];T=M['technology'];O=M['gallery']['Офис']
hero_by_url={
 '/angary/':cp('P07'),'/angary/sklady/':cp('P14'),'/angary/remontnye-masterskie/':cp('P05'),'/angary/proizvodstvennye/':cp('P26'),'/angary/dlya-tehniki/':cp('P20'),'/angary/sportivnye/':cp('P15'),'/angary/selskohozyaystvennye/':P[2],'/angary/gotovye/':P[2],'/technology/':cp('P14',1),'/proektirovanie/':dict(P[0],caption='Проектирование каркасной конструкции · иллюстрация производителя'),'/production/':P[2],'/montazh/':cp('P09',1),'/dostavka/':P[5],'/process/':P[4],'/raschet/':cp('P07'),'/about/':P[2],'/tendery/':O[2],'/contacts/':O[0],'/projects/':cp('P11'),'/about/team/':O[2],'/career/':P[2],'/gallery/':P[2],'/materials/':cp('P14',1),'/materials/pokrytie-angara/':T[22],'/materials/teplyy-angar/':cp('P05'),'/materials/podgotovka-ploshchadki/':T[0],'/materials/stoimost-angara/':cp('P07'),'/materials/proverka-proizvodstva/':P[2]}
manifest=json.loads((ROOT/'content/manifest.json').read_text()) if (ROOT/'content/manifest.json').exists() else {}
case_paths={x['url']:x['id'] for x in manifest.get('projects',[])}
def apply_all_photos(p,body):
 path=p['url']
 if path in ['/','/review/']:return body
 id=case_paths.get(path)
 selected=cp(id) if id else hero_by_url.get(path)
 if not selected:return body
 complex_hero=path in ['/raschet/','/about/team/','/gallery/','/materials/']
 def hero(m):
  content=m.group(1);tail=''
  if complex_hero:
   d=re.search(r'<div class="hero-description[^\"]*">(.*)</div>$',content,re.S)
   if d:
    first=re.match(r'\s*(<p>.*?</p>)(.*)',d.group(1),re.S)
    if first:
     content=content[:d.start()]+'<div class="hero-description">'+first.group(1)+'</div>'
     tail='<div class="photo-hero-extra">'+first.group(2)+'</div>'
  return '<section class="hero inner-hero photo-inner-hero"><div class="shell"><div class="photo-hero-grid"><div class="photo-hero-copy">'+content+'</div>'+photo(selected,'interior-hero-photo',True,sizes='inner')+'</div>'+tail+'</div></section>'
 body=re.sub(r'<section class="hero inner-hero"><div class="shell">(.*?)</div></section>',hero,body,count=1,flags=re.S)
 # Every case card receives only the corresponding case's primary image.
 def casecard(m):
  s=m.group();u=re.search(r'<h[23]><a href="([^"]+)"',s)
  if not u or u.group(1) not in case_paths:return s
  x=cp(case_paths[u.group(1)])
  img=f'<a class="case-image-link" href="{u.group(1)}">'+picture(x['src'],x['caption'],sizes='card')+'</a>'
  return s.replace('class="case-card filter-card"','class="case-card filter-card with-photo"').replace('<div class="case-top">',img+'<div class="case-top">',1)
 body=re.sub(r'<article class="case-card filter-card".*?</article>',casecard,body,flags=re.S)
 # Real portraits, names matched directly to the source page's alt labels.
 def person(m):
  s=m.group();name=re.search(r'<h[23]>(.*?)</h[23]>',s).group(1)
  if name in M['team']:
   s=re.sub(r'<svg.*?</svg>',picture(M['team'][name]['src'],name,cls='team-portrait',sizes='portrait'),s,count=1,flags=re.S)
  return s
 body=re.sub(r'<article class="person-card">.*?</article>',person,body,flags=re.S)
 def section(anchor,xs):
  nonlocal body
  pattern=r'(<section\b[^>]*id="'+re.escape(anchor)+r'"[^>]*>)(.*?)(</section>)'
  def put(m):
   s=m.group(2)
   pos=s.rfind('</div></div>')
   if pos>=0:s=s[:pos]+grid(xs)+s[pos:]
   return m.group(1)+s+m.group(3)
  body=re.sub(pattern,put,body,count=1,flags=re.S)
 if path=='/technology/':
  for anchor,indices in {'foundation':[0,1,2,3,4,5],'frame':[19,20],'cover':[22,24,25],'insulation':[23],'gates':[21],'heating':[13,14,15,16,17,18],'ventilation':[6,7],'power':[8,9],'fire':[10,11,12],'cranes':[26,27,28]}.items():section(anchor,[T[i] for i in indices])
 if path=='/production/':
  for anchor,indices in {'section-1':[2,3],'section-2':[1],'section-4':[4,5]}.items():section(anchor,[P[i] for i in indices])
 if path=='/dostavka/':section('section-1',[P[4]]);section('section-2',[P[5]])
 if path=='/montazh/':section('section-2',M['cases']['P09'][1:3])
 if path=='/proektirovanie/':section('section-2',[dict(P[0],caption='Каркасная конструкция · иллюстрация производителя')])
 if path=='/contacts/':section('section-2',O[1:3])
 if path=='/about/':section('section-1',[P[1],P[2]])
 if path=='/career/':section('section-1',[O[2]])
 if path=='/materials/pokrytie-angara/':
  for n,i in [(1,22),(2,24),(3,25)]:section('section-'+str(n),[T[i]])
 if path=='/materials/teplyy-angar/':section('section-1',[T[23],T[24]]);section('section-2',[T[13],T[14]])
 if path=='/materials/podgotovka-ploshchadki/':section('section-1',[T[0],T[3]])
 if path=='/materials/proverka-proizvodstva/':section('section-1',[P[2],P[3]]);section('section-4',[P[4]])
 # Product/category cards use identified completed examples, never imaginary stock.
 if path=='/angary/':
  cats={'Склад':'P14','Ремонтная мастерская':'P05','Производство':'P26','Техника':'P20','Спорт':'P15'}
  def solution(m):
   s=m.group();title=re.search(r'<h[23]>(.*?)</h[23]>',s).group(1)
   if title not in cats:return s
   x=cp(cats[title]);return s.replace('<article class="info-card">','<article class="info-card illustrated-solution">'+photo(x,'solution-photo'),1)
  body=re.sub(r'<article class="info-card">.*?</article>',solution,body,flags=re.S)
 # Photos on each individual case, with full-size viewing.
 if id:
  gallery='<section class="section case-gallery-section"><div class="shell"><p class="eyebrow">Фотографии объекта</p><h2>'+e(p['h1'])+'</h2>'+grid(M['cases'][id],'case-gallery')+'</div></section>'
  body=body.replace('<section class="contact-banner"',gallery+'<section class="contact-banner"',1)
 if path=='/gallery/':
  groups=[('Металлоконструкции',M['gallery']['Цех металлоконструкций']),('Тентовый цех',M['gallery']['Тентовый цех']),('Офис',O),('Проекты',[cp(k) for k in ['P01','P07','P09','P14','P15','P20']])]
  albums='<section class="section"><div class="shell filter-section gallery-albums"><div class="filters" role="group" aria-label="Разделы галереи">'+''.join(f'<button type="button" data-filter="{c}" aria-pressed="{str(i==0).lower()}">{c}</button>' for i,c in enumerate(['Все']+[x[0] for x in groups]))+'</div><p class="filter-status" role="status"></p><div class="album-grid">'
  for category,xs in groups:
   for x in xs:albums+=f'<div class="filter-card" data-category="{category}">'+photo(x,sizes='grid-3')+'</div>'
  albums+='</div></div></section>'
  body=body.replace('<section class="contact-banner"',albums+'<section class="contact-banner"',1)
  # Category links jump to the actual gallery instead of leaving the page.
  body=body.replace('class="gallery-albums"','class="gallery-albums"')
  body=body.replace('class="section"><div class="shell filter-section gallery-albums"','class="section" id="albums"><div class="shell filter-section gallery-albums"')
  body=re.sub(r'(<a class="gallery-card" href=")[^"]+',r'\1#albums',body)
 if path=='/materials/':
  def articlecard(m):
   s=m.group();u=re.search(r'href="([^"]+)"',s).group(1);x=hero_by_url.get(u)
   if not x:return s
   return s.replace('class="list-card"','class="list-card material-photo-card"').replace('<span>',picture(x['src'],x['caption'],sizes='thumb')+'<span>',1)
  body=re.sub(r'<a class="list-card".*?</a>',articlecard,body,flags=re.S)
 return body
