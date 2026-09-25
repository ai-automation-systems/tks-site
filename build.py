from pathlib import Path
import re,json,html,shutil,datetime,os
from home_photo import apply_home_photos
from all_photos import apply_all_photos
from identity import apply_identity
ROOT=Path(__file__).resolve().parent
SOURCE=(ROOT/'content/source.txt').read_text()

# Переключатель индексации: снимает noindex, открывает robots.txt и строит sitemap.xml.
# Включать только после замены SITE на настоящий домен: от него считаются canonical, og-теги и sitemap.
PUBLISH=False
SITE='https://tentsbv.ru'
# Плавающая кнопка обратной связи. Ссылка на профиль MAX — из приложения (аватар, QR-код, «Поделиться»).
TG_URL='https://t.me/+79309183075'
MAX_URL='https://max.ru/u/f9LHodD0cOKQBGliDNw6x-4RhdUvum-wPFsfeLLjZmzKhFHcrkmc59rNsNM'
YEAR=datetime.date.today().year
# Префикс для предпросмотра на адресе вида github.io/название/. На своём домене оставить пустым.
BASE=os.environ.get('SITE_BASE','').rstrip('/')
def rebase(t):
 if not BASE:return t
 t=re.sub(r'(href|src|action)="/(?!/)',lambda m:f'{m.group(1)}="{BASE}/',t)
 t=re.sub(r'srcset="([^"]*)"',lambda m:'srcset="'+','.join((BASE+x.strip() if x.strip().startswith('/') else x) for x in m.group(1).split(','))+'"',t)
 return t
# Порядок важен: токены объявляются до компонентов.
CSS_PARTS=['tokens.css','style.css','home-photo.css','all-photos.css','brand.css','fab.css','touch.css']
def e(s): return html.escape(str(s),quote=True)
def val(s,k,default=''):
 m=re.search(r'^'+re.escape(k)+r': (.*)$',s,re.M);return m.group(1).strip() if m else default
pages=[]
main=SOURCE.split('1. ГОТОВЫЕ ТЕКСТЫ СТРАНИЦ',1)[1].split('2. ОБЩИЕ ФОРМЫ',1)[0]
for match in re.finditer(r'СТРАНИЦА (\d+)\. ([^\n]+)\n(.*?)(?=СТРАНИЦА |\Z)',main,re.S):
 n,label,body=match.groups();pages.append(dict(id=n,label=label,url=val(body,'URL'),title=val(body,'Title'),description=val(body,'Description'),h1=val(body,'H1'),body=body))
cases={}
casebody=SOURCE.split('ПРОЕКТ P01',1)[1].split('3.2. Карточки',1)[0]
for m in re.finditer(r'ПРОЕКТ (P\d+)\n(.*?)(?=ПРОЕКТ P|\Z)','ПРОЕКТ P01'+casebody,re.S):
 id,b=m.groups(); cases[id]=dict(id=id,url=val(b,'URL'),title=val(b,'Title'),description=val(b,'Description'),h1=val(b,'H1'),text=val(b,'Текст'),params=val(b,'Параметры'),loads=val(b,'Районирование в карточке источника'),body=b)
stock=[]
for m in re.finditer(r'КАРТОЧКА (G\d+): ([^\n]+)\n(.*?)(?=КАРТОЧКА G|\n=|\Z)',SOURCE.split('3.2. Карточки',1)[1].split('4. SEO',1)[0],re.S):
 id,title,b=m.groups();stock.append(dict(id=id,title=title,purpose=val(b,'Назначение по источнику'),loads=val(b,'Параметры районирования по источнику')))
labels={'/':'Главная','/angary/':'Ангары','/angary/sklady/':'Склады','/angary/remontnye-masterskie/':'Ремонтные мастерские','/angary/proizvodstvennye/':'Производственные ангары','/angary/dlya-tehniki/':'Ангары для техники','/angary/sportivnye/':'Спортивные сооружения','/angary/selskohozyaystvennye/':'Сельскохозяйственные ангары','/angary/gotovye/':'Готовые ангары','/technology/':'Технологии','/proektirovanie/':'Проектирование','/production/':'Производство','/montazh/':'Монтаж и шеф-монтаж','/dostavka/':'Доставка','/process/':'Как проходит работа','/raschet/':'Расчёт стоимости','/about/':'О компании','/tendery/':'Тендеры','/contacts/':'Контакты','/projects/':'Проекты','/about/team/':'Команда','/career/':'Карьера','/gallery/':'Галерея','/materials/':'Полезные материалы','/review/':'Все страницы'}
anchors={'foundation':'Основание','frame':'Каркас','cover':'Покрытие','insulation':'Утепление','gates':'Ворота','heating':'Отопление','ventilation':'Вентиляция','power':'Электроснабжение','fire':'Пожарные системы','cranes':'Кран-балки','loads':'Нагрузки','visit':'Посетить производство'}
for p in pages: labels.setdefault(p['url'],p['h1'])
for p in cases.values(): labels[p['url']]=p['h1']
icons={
 'hangar':'<path d="M3 21V8l9-5 9 5v13M3 9h18M8 21V12h8v9M1 21h22"/>',
 'box':'<path d="m12 3 9 5v9l-9 5-9-5V8l9-5Zm0 9v10M3 8l9 4 9-4M8 5l9 5v5"/>',
 'tool':'<path d="M14 5a5 5 0 0 0-6 6l-6 6 5 5 6-6a5 5 0 0 0 6-7l-4 4-4-4 3-4Z"/>',
 'factory':'<path d="M3 21V10l6 3V8l6 5V3h5l1 18H3ZM6 17h2m3 0h2m3 0h2"/>',
 'truck':'<path d="M2 4h12v13H2V4Zm12 5h4l4 4v4h-8M17 9v4h5"/><circle cx="6" cy="19" r="2"/><circle cx="18" cy="19" r="2"/>',
 'sport':'<circle cx="12" cy="12" r="9"/><path d="M3 12h18M12 3v18M5 5c9 5 9 9 14 14M5 19c9-5 9-9 14-14"/>',
 'leaf':'<path d="M4 20 17 7M4 16C0 5 12 2 21 3c1 12-8 20-17 13Zm5-2 1-5m0 3 5 1"/>',
 'ruler':'<path d="m3 16 13-13 5 5L8 21l-5-5Zm5-5 3 3m1-7 3 3m1-7 3 3"/>',
 'layers':'<path d="m12 3 10 6-10 6L2 9l10-6Zm-10 12 10 6 10-6M2 12l10 6 10-6"/>',
 'check':'<path d="m5 12 4 4 10-10M21 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h10"/>',
 'pin':'<path d="M20 10c0 6-8 12-8 12S4 16 4 10a8 8 0 1 1 16 0Z"/><circle cx="12" cy="10" r="3"/>',
 'doc':'<path d="M5 2h9l5 5v15H5V2Zm9 0v6h5M8 12h8M8 16h8M8 19h5"/>',
 'arrow':'<path d="M4 12h16m-6-6 6 6-6 6"/>',
 'person':'<circle cx="12" cy="7" r="4"/><path d="M4 22v-4a8 8 0 0 1 16 0v4"/>',
 'snow':'<path d="M12 2v20M3 7l18 10M3 17 21 7M9 3l3 3 3-3M9 21l3-3 3 3M3 10l4-1-1-4M18 19l-1-4 4-1M3 14l4 1-1 4M18 5l-1 4 4 1"/>',
 'gear':'<path d="M9 3h6l1 4 4 1 2 5-3 3v4l-5 2-3-3-4 1-3-4 1-4L2 9l3-4h4V3Z"/><circle cx="12" cy="12" r="3"/>',
 # Ниже — замена типографских глифов ⌄ ↗ ↓ + на векторные иконки: они не зависят от того,
 # какой шрифт подставит система, и наследуют цвет и толщину линий остального интерфейса.
 'chevron':'<path d="m6 9 6 6 6-6"/>',
 'sun':'<circle cx="12" cy="12" r="4"/><path d="M12 2v2m0 16v2M2 12h2m16 0h2M4.9 4.9l1.4 1.4m11.4 11.4 1.4 1.4M19.1 4.9l-1.4 1.4M6.3 17.7l-1.4 1.4"/>',
 'moon':'<path d="M21 13A9 9 0 1 1 11 3a7 7 0 0 0 10 10Z"/>',
 'phone':'<path d="M22 16.9v3a2 2 0 0 1-2.2 2 19.8 19.8 0 0 1-8.6-3.1 19.5 19.5 0 0 1-6-6A19.8 19.8 0 0 1 2.1 4.2 2 2 0 0 1 4.1 2h3a2 2 0 0 1 2 1.7c.1 1 .4 1.9.7 2.8a2 2 0 0 1-.4 2.1L8.1 9.9a16 16 0 0 0 6 6l1.3-1.3a2 2 0 0 1 2.1-.4c.9.3 1.8.6 2.8.7a2 2 0 0 1 1.7 2Z"/>',
 'external':'<path d="M7 17 17 7M9 7h8v8"/>',
 'download':'<path d="M12 3v12m-5-5 5 5 5-5M4 19h16"/>',
 'plus':'<path d="M12 5v14M5 12h14"/>',
 'send':'<path d="M22 2 11 13M22 2l-7 20-4-9-9-4 20-7Z"/>',
 'vk':'<path d="M3 5h4c0 5 2 8 4 8V5h4v4c2 0 3-2 4-4h3c-1 3-3 5-4 6 1 1 3 3 4 6h-4c-1-2-2-3-3-3v3h-4c-5 0-8-5-8-12Z"/>'}
def icon(name='hangar'): return '<svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.45" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'+icons.get(name,icons['hangar'])+'</svg>'
def link(label,url,cls='text-link'):
 return f'<a class="{cls}" href="{e(url)}">{e(label)}{icon("arrow")}</a>'
def named_url(url):
 base,_,anchor=url.partition('#');return anchors.get(anchor,labels.get(base,base))
def resolve(s):
 s=s.strip().rstrip('.')
 m=re.search(r'P\d{2}',s)
 if m and m.group() in cases:return cases[m.group()]['url']
 if s.startswith(('/','http','tel:','mailto:','#')):return s
 return '#request'
def inline(s):
 # Display related projects by real title, not internal identifiers.
 s=e(s)
 for id,c in cases.items(): s=re.sub(r'\b'+id+r'\b',f'<a href="{c["url"]}">{e(c["h1"])}</a>',s)
 return s

# Подсказки автозаполнения по имени поля: без них браузер не предлагает сохранённые данные.
AUTOFILL={'name':'name','phone':'tel','email':'email','company':'organization','location':'address-level2'}
def field(label,name,type='text',required=False,options=None,wide=False):
 attrs=f'name="{name}" id="{{uid}}-{name}"'+(' required' if required else '')
 lab=f'<label class="field {"wide" if wide else ""}"><span>{e(label)}{(" <em>*</em>" if required else "")}</span>'
 if options: ctrl=f'<select {attrs}>'+''.join(f'<option value="{e(v)}">{e(v)}</option>' for v in options)+'</select>'
 elif type=='textarea': ctrl=f'<textarea {attrs} rows="3"></textarea>'
 else:
  extra=(' min="0" step="any" inputmode="decimal"' if type=='number' else '')
  ac=AUTOFILL.get(name)
  ctrl=f'<input {attrs} type="{type}"'+extra+(f' autocomplete="{ac}"' if ac else '')+'>'
 return lab+ctrl+'</label>'
PURPOSES=['Не определено','Склад','Ремонтная мастерская','Производство','Техника','Спорт','Сельское хозяйство','Другое']
def form(mode='short',uid='request-form',button=None):
 fs=field('Ваше имя','name',required=True)+field('Телефон','phone','tel',True)
 if mode in ('quote','brief','tender'): fs+=field('Электронная почта','email','email')
 if mode in ('brief','tender'):fs+=field('Компания','company')
 if mode in ('quote','brief'):
  fs+=field('Назначение ангара','purpose',options=PURPOSES)+field('Место строительства','location')
  for name,label in [('width','Ширина, м'),('length','Длина, м'),('height','Высота внешней стены, м')]:fs+=field(label,name,'number')
 if mode=='brief':
  fs+=field('Высота в рабочей зоне, м','working-height','number')
  for label,name,opts in [('Температурный режим','climate',['Нужна консультация','Холодное помещение','Отапливаемое помещение']),('Покрытие','cover',['Нужна помощь с подбором','ПВХ','Сэндвич-панели','Профлист']),('Тип ворот','gate-type',['Не определён','Распашные','Откатные','Секционные']),('Основание','foundation',['Пока нет данных','Есть готовое','Требуется проектное решение']),('Работы','works',['Требуется обсуждение','Изготовление и доставка','Изготовление, доставка и монтаж','Шеф-монтаж'])]:fs+=field(label,name,options=opts)
  fs+=field('Ворота: количество, ширина и высота','gates')+field('Грунт и существующая площадка','ground','textarea',wide=True)
  fs+='<fieldset class="wide systems"><legend>Инженерные системы</legend>'+''.join(f'<label><input type="checkbox" name="systems" value="{e(s)}">{e(s)}</label>' for s in ['Отопление','Вентиляция','Освещение','Электроснабжение','Пожарная сигнализация','Пожаротушение','Кран-балка','Другое оборудование'])+'</fieldset>'
  fs+=field('Кран-балка: грузоподъёмность и операции','crane','textarea',wide=True)+field('Пожелания по срокам и особые требования','timing','textarea',wide=True)
 if mode=='tender':fs+=field('Ссылка или номер закупки','tender',wide=True)
 fs+=field('Комментарий' if mode!='short' else 'Несколько слов о задаче','comment','textarea',wide=True)
 if mode!='short':fs+='<label class="field wide file-field"><span>Прикрепить техническое задание'+(' или план площадки' if mode=='brief' else '')+'</span><input type="file" name="attachment" accept=".pdf,.doc,.docx,.xls,.xlsx,.dwg,.dxf,.zip,.rar,.jpg,.jpeg,.png,image/*,application/pdf"><button class="remove-file" type="button" hidden>Удалить файл</button></label>'
 button=button or {'short':'Обсудить проект','quote':'Получить предварительный расчёт','brief':'Отправить задание на расчёт','tender':'Отправить запрос в тендерный отдел'}[mode]
 return f'<form class="form form-{mode}" id="{uid}"><div class="form-grid">'+fs.replace('{uid}',uid)+f'</div><p class="form-context" hidden></p><div class="form-bottom"><button class="button" type="submit">{e(button)}{icon("arrow")}</button><p class="preview-note">Макет формы: данные никуда не отправляются.</p></div><p class="form-status" role="status" hidden></p></form>'

def casecat(id):
 if id in ['P02','P03','P05','P06','P07','P08','P09','P10','P11','P12','P23','P24']:return 'Ремонтные мастерские'
 if id in ['P04','P13','P14','P18','P19','P25']:return 'Склады'
 if id in ['P17','P21','P22','P26']:return 'Производство'
 if id in ['P20','P27']:return 'Техника'
 if id=='P15':return 'Спорт'
 return 'Другие объекты'
def casecard(id,h='h3'):
 c=cases[id]; cat=casecat(id); ci={'Склады':'box','Ремонтные мастерские':'tool','Производство':'factory','Техника':'truck','Спорт':'sport'}.get(cat,'hangar')
 return f'<article class="case-card filter-card" data-category="{cat}"><div class="case-top">{icon(ci)}<span>{cat}</span></div><{h}><a href="{c["url"]}">{e(c["h1"])}</a></{h}><p>{e(c["description"])}</p>'+ (f'<div class="case-dimensions">{e(c["params"].split(";")[0])}<small>ширина × длина × высота внешней стены</small></div>' if c['params'] else '')+link('Посмотреть решение',c['url'])+'</article>'
def filters(categories):
 return '<div class="filters" role="group" aria-label="Фильтр по назначению">'+''.join(f'<button type="button" data-filter="{e(c)}" aria-pressed="{str(i==0).lower()}">{e(c)}</button>' for i,c in enumerate(categories))+'</div><p class="filter-status" role="status"></p>'

def parse_page(p):
 body=p['body']; start=body.index('H1:'); lines=body[start:].splitlines();sections=[];cur={'title':'','lines':[],'anchor':''};sections.append(cur)
 for l in lines[1:]:
  l=l.strip()
  if not l or l.startswith(('-', '=')) and not l.startswith('— '):continue
  if l.startswith('H2: '):cur={'title':l[4:],'lines':[],'anchor':''};sections.append(cur)
  elif l.startswith('Якорь: '):cur['anchor']=l[7:]
  elif l in ['Первый экран','Финальный блок']:continue
  else:cur['lines'].append(l)
 for i,s in enumerate(sections):s['anchor']=s['anchor'] or ('section-'+str(i))
 return sections

home_sections=parse_page(pages[0]);home_cards=[l for l in home_sections[1]['lines'] if l.startswith('Карточка')]

def cards(lines):
 out=''
 for i,l in enumerate(lines):
  m=re.match(r'Карточка «(.*?)»: (.*)',l)
  if m:title,b=m.groups()
  else:
   b=re.sub(r'^Карточка \d+: ','',l);title,b=b.split('. ',1) if '. ' in b else (b,'')
  target='';cta='Подробнее'
  if '→' in b:
   b,target=b.rsplit('→',1); target=resolve(target)
   cm=re.search(r'Ссылка «(.*?)»',b)
   if cm:cta=cm.group(1);b=b[:cm.start()].strip()
   b=b.strip()
  ci=['box','tool','factory','truck','sport','leaf'][i%6] if title in ['Склад','Ремонтная мастерская','Производство','Техника','Спорт','Сельское хозяйство'] else ['layers','ruler','gear'][i%3]
  out+=f'<article class="info-card">{icon(ci)}<h3>{e(title)}</h3><p>{inline(b)}</p>'+(link(cta,target) if target else '')+'</article>'
 return '<div class="card-grid">'+out+'</div>'

def render_lines(lines,p,section=''):
 out=[];i=0;path=p['url']
 while i<len(lines):
  l=lines[i];i+=1
  if l.startswith(('Служебно:','Источники:','Навигация по странице:','Кнопка карточки:','Фильтры:')):continue
  if l.startswith('Карточка '):
   group=[l]
   while i<len(lines) and lines[i].startswith('Карточка '):group.append(lines[i]);i+=1
   out.append(cards(group));continue
  if l.startswith('Вопрос:'):
   q=l[8:];a=''
   if i<len(lines) and lines[i].startswith('Ответ:'):a=lines[i][7:];i+=1
   out.append(f'<details class="faq"><summary>{e(q)}'+icon('plus')+f'</summary><div><p>{e(a)}</p></div></details>');continue
  if l.startswith('H3:'):
   title=l[4:];paras=[]
   while i<len(lines) and lines[i].startswith('Текст:'):paras.append('<p>'+inline(lines[i][7:])+'</p>');i+=1
   out.append(f'<article class="feature"><div>{icon("layers")}</div><div><h3>{e(title)}</h3>'+''.join(paras)+'</div></article>');continue
  if l=='Короткая форма:':
   while i<len(lines) and (lines[i].startswith('— ') or lines[i].startswith('Кнопка:')):i+=1
   out.append(form('quote','quote-form'));continue
  if l=='Поля расширенной формы:':
   while i<len(lines) and (re.match(r'^\d+\.',lines[i]) or lines[i].startswith('Кнопка:')):i+=1
   out.append(form('brief','brief-form'));continue
  if l.startswith('Поля формы:'):
   out.append(form('tender','request'));i+=1 if i<len(lines) and lines[i].startswith('Кнопка:') else 0;continue
  if l=='Карточки:' and path=='/about/team/':
   people=[]
   while i<len(lines) and lines[i].startswith('— '):
    name,role=lines[i][2:].rstrip('.').split(' — ',1);people.append(f'<article class="person-card">{icon("person")}<h2>{e(name)}</h2><p>{e(role)}</p></article>');i+=1
   out.append('<div class="card-grid team-grid">'+''.join(people)+'</div>');continue
  if l.startswith('Категории:'):
   cats=l.partition(':')[2].strip().rstrip('.').split(' / ')
   out.append('<div class="gallery-grid">'+''.join(f'<a class="gallery-card" href="{("/projects/" if c=="Проекты" else "/production/" if c!="Офис" else "/contacts/")}">{icon("factory" if c!="Проекты" else "hangar")}<h2>{e(c)}</h2>{icon("arrow")}</a>' for c in cats)+'</div>');continue
  if l.startswith(('Кнопка:','Вторая кнопка:','Ссылка:','Вторая ссылка:')):
   k,v=l.split(':',1);v=v.strip()
   if '→' in v: label,target=v.split('→',1);out.append(link(label.strip(),resolve(target),'button' if k=='Кнопка' else 'text-link'))
   # Unlinked buttons belong to actual form already rendered.
   continue
  if l.startswith(('Связанные страницы:','Ссылки:')):
   urls=re.findall(r'/[\w/#-]+',l)
   ids=re.findall(r'P\d{2}',l)
   if ids:out.append('<div class="case-grid">'+''.join(casecard(id) for id in ids if id in cases and id!='P04')+'</div>')
   else:out.append('<div class="related-links">'+''.join(link(named_url(u),u) for u in urls)+'</div>')
   continue
  if l.startswith('Короткие факты'):
   group=[]
   while i<len(lines) and lines[i].startswith('— '):group.append(lines[i][2:]);i+=1
   out.append('<div class="fact-strip">'+''.join(f'<div>{icon(ic)}<p>{e(t)}</p></div>' for t,ic in zip(group,['ruler','factory','tool','check']))+'</div>');continue
  if l.startswith('— ') or re.match(r'^\d+\. ',l):
   group=[l]
   ordered=bool(re.match(r'^\d+\.',l))
   while i<len(lines) and (re.match(r'^\d+\. ',lines[i]) if ordered else lines[i].startswith('— ')):group.append(lines[i]);i+=1
   if any('→' in x for x in group):
    links=[]
    for x in group:
     if '→' in x:
      t,u=x.lstrip('— ').rsplit('→',1);links.append(f'<a class="list-card" href="{e(resolve(u))}"><span>{inline(t.strip().rstrip("."))}</span>{icon("arrow")}</a>')
     else:links.append('<p>'+inline(x[2:])+'</p>')
    out.append('<div class="link-list">'+''.join(links)+'</div>')
   elif ordered:
    out.append('<ol class="steps">'+''.join('<li><span>'+str(n+1).zfill(2)+'</span><p>'+inline(re.sub(r'^\d+\. ','',x))+'</p></li>' for n,x in enumerate(group))+'</ol>')
   else:out.append('<ul class="bullet-list">'+''.join('<li>'+inline(x[2:])+'</li>' for x in group)+'</ul>')
   continue
  if l in ['Карточки:']:continue
  if l.startswith('Текст:'):out.append('<p>'+inline(l[7:])+'</p>');continue
  if l.startswith(('Подпись:','Пояснение:')):out.append('<p class="caption">'+inline(l.partition(':')[2].strip())+'</p>');continue
  if l.startswith('Подзаголовок формы:'):out.append('<h2 class="form-title">'+e(l.partition(':')[2].strip())+'</h2>');continue
  if l.startswith('E-mail:'):
   email=l.partition(':')[2].strip().rstrip('.');out.append(f'<p class="contact-value"><a href="mailto:{e(email)}">{e(email)}</a></p>');continue
  if l.startswith('Телефон:'):
   out.append('<p class="contact-value"><a href="tel:+78006004626">'+e(l.partition(':')[2].strip().rstrip('.'))+'</a></p>');continue
  out.append('<p>'+inline(l)+'</p>')
 return '\n'.join(out)

def header(path):
 def navitem(url,children=None):
  active=' aria-current="page"' if path==url else ''
  if children:
   return f'<div class="nav-group"><a href="{url}"{active}>{labels[url]}</a><button class="submenu-toggle" type="button" aria-expanded="false" aria-label="Раздел {labels[url]}">'+icon('chevron')+'</button><div class="submenu">'+''.join(f'<a href="{u}">{e(labels[u])}</a>' for u in children)+'</div></div>'
  return f'<a href="{url}"{active}>{labels[url]}</a>'
 bar=''
 # Телефон лежит внутри <nav>: на десктопе он справа, на узком экране попадает в раскрытое меню.
 contact='<div class="header-contact"><a href="tel:+78006004626">8 800 600-46-26</a><a href="/raschet/">Рассчитать ангар'+icon('external')+'</a></div>'
 theme='<button class="theme-toggle" type="button" aria-label="Переключить тему" title="Переключить тему">'+icon('sun').replace('class="icon"','class="icon icon-sun"')+icon('moon').replace('class="icon"','class="icon icon-moon"')+'</button>'
 burger='<button class="menu-toggle" type="button" aria-expanded="false" aria-controls="navigation" aria-label="Открыть меню"><span></span><span></span></button>'
 return '<a class="skip" href="#main">Перейти к содержанию</a>'+bar+'<header class="header"><div class="shell header-inner"><a class="brand" href="/" aria-label="Тентовые конструкции — главная">'+icon('hangar')+'<span>ТЕНТОВЫЕ<br>КОНСТРУКЦИИ</span></a><nav id="navigation" class="nav" aria-label="Главная навигация"><div class="nav-links">'+navitem('/angary/',['/angary/']+list(labels.keys())[2:8]+['/angary/gotovye/'])+navitem('/technology/',['/technology/','/proektirovanie/','/montazh/','/dostavka/','/process/'])+navitem('/projects/')+navitem('/production/')+navitem('/about/',['/about/','/about/team/','/career/','/materials/','/gallery/','/tendery/'])+navitem('/contacts/')+'</div>'+contact+'</nav><div class="header-actions">'+theme+burger+'</div></div></header>'
def mobile_cta():
 # Постоянный доступ к звонку и расчёту на телефоне: в шапке для них нет места.
 return '<div class="mobile-cta"><a class="cta-call" href="tel:+78006004626">'+icon('phone')+'8 800 600-46-26</a><a class="cta-quote" href="/raschet/">Рассчитать ангар</a></div>'
def footer():
 return '<footer class="footer"><div class="shell footer-grid"><div><a class="brand" href="/">'+icon('hangar')+'<span>ТЕНТОВЫЕ<br>КОНСТРУКЦИИ</span></a><p>Проектируем, производим и монтируем каркасные ангары. Производство в Иркутске, доставка по России.</p></div><div class="footer-links">'+''.join(f'<a href="{u}">{e(labels[u])}</a>' for u in ['/angary/','/technology/','/projects/','/production/','/tendery/','/materials/','/about/team/','/career/','/gallery/'])+'</div><div class="footer-contact"><a href="tel:+78006004626">'+icon('phone')+'8 800 600-46-26</a><a href="mailto:info@tentsbv.ru">info@tentsbv.ru</a><p>664056, Иркутск,<br>ул. Безбокова, д. 30/6, 6 этаж.</p><p>Пн–пт, 8:00–17:00<br>Иркутское время, UTC+8</p><div class="social"><a href="https://t.me/tentsbv_sale" target="_blank" rel="noopener">Telegram'+icon('external')+'</a><a href="https://vk.com/tentsbv" target="_blank" rel="noopener">ВКонтакте'+icon('external')+'</a></div></div></div><div class="shell footer-bottom"><span>© '+str(YEAR)+' Тентовые конструкции</span></div></footer>'

from img_tag import best as img_best

# CSS собирается до генерации страниц: в ссылки подставляется хеш содержимого,
# иначе браузер продолжит отдавать старую версию из кэша после обновления сайта.
(ROOT/'css/site.css').write_text('\n'.join((ROOT/'css'/part).read_text() for part in CSS_PARTS).replace('url(/fonts/','url('+BASE+'/fonts/'))
def stamp(path):
 import hashlib
 return hashlib.md5((ROOT/path).read_bytes()).hexdigest()[:8]
CSS_V=stamp('css/site.css')
JS_V=stamp('js/main.js')

def share_image():
 # Превью для мессенджеров: снимок цеха шириной 1200px, чтобы карточка не обрезалась.
 return img_best('/img/production.jpg',1200)

# Тема применяется до первой отрисовки, иначе при загрузке мигает светлый фон.
THEME_BOOT='<script>(function(){try{var t=localStorage.getItem("theme");if(t)document.documentElement.dataset.theme=t;}catch(e){}})()</script>'

def jsonld(p):
 org={'@context':'https://schema.org','@type':'Organization','name':'Тентовые конструкции','url':SITE,'telephone':'+7 800 600-46-26','email':'info@tentsbv.ru','address':{'@type':'PostalAddress','postalCode':'664056','addressLocality':'Иркутск','streetAddress':'ул. Безбокова, д. 30/6, 6 этаж'},'sameAs':['https://t.me/tentsbv_sale','https://vk.com/tentsbv']}
 crumbs=[{'@type':'ListItem','position':1,'name':'Главная','item':SITE+'/'}]
 if p['url']!='/':crumbs.append({'@type':'ListItem','position':2,'name':labels.get(p['url'],p.get('h1','')),'item':SITE+p['url']})
 data=[org,{'@context':'https://schema.org','@type':'BreadcrumbList','itemListElement':crumbs}]
 return '<script type="application/ld+json">'+json.dumps(data,ensure_ascii=False)+'</script>'

def head(p):
 url=SITE+p['url'];title=e(p['title']);desc=e(p.get('description',''))
 share=SITE+share_image()
 tags=['<meta charset="utf-8">','<meta name="viewport" content="width=device-width,initial-scale=1">']
 tags.append('<meta name="robots" content="index,follow">' if PUBLISH else '<meta name="robots" content="noindex,nofollow">')
 tags+=['<meta name="theme-color" media="(prefers-color-scheme:light)" content="#eaf4ff">',
  '<meta name="theme-color" media="(prefers-color-scheme:dark)" content="#0e1826">',
  f'<title>{title}</title>',f'<meta name="description" content="{desc}">',
  f'<link rel="canonical" href="{url}">',
  # Превью для мессенджеров и соцсетей: без этих тегов ссылка приходит голой.
  '<meta property="og:type" content="website">','<meta property="og:locale" content="ru_RU">',
  '<meta property="og:site_name" content="Тентовые конструкции">',
  f'<meta property="og:title" content="{title}">',f'<meta property="og:description" content="{desc}">',
  f'<meta property="og:url" content="{url}">',f'<meta property="og:image" content="{share}">',
  '<meta name="twitter:card" content="summary_large_image">',
  '<link rel="icon" href="/favicon.svg" type="image/svg+xml">',
  '<link rel="preload" href="/fonts/manrope-cyrillic.woff2" as="font" type="font/woff2" crossorigin>',
  '<link rel="preload" href="/fonts/manrope-latin.woff2" as="font" type="font/woff2" crossorigin>',
  f'<link rel="stylesheet" href="/css/site.css?v={CSS_V}">',f'<script defer src="/js/main.js?v={JS_V}"></script>',THEME_BOOT,jsonld(p)]
 return ''.join(tags)

def fab():
 chat='<svg class="icon fab-chat" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M21 12a8 8 0 0 1-11.6 7.1L4 20.5l1.5-4.6A8 8 0 1 1 21 12Z"/><path d="M8.5 11.5h.01M12 11.5h.01M15.5 11.5h.01" stroke-width="2.4"/></svg>'
 close='<svg class="icon fab-close" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M18 6 6 18M6 6l12 12"/></svg>'
 def link(url,logo,name,note):
  return f'<a class="fab-link" href="{url}" target="_blank" rel="noopener"><img src="/img/logos/{logo}.svg" alt="" width="40" height="40" loading="lazy" decoding="async"><span class="fab-text"><strong>{name}</strong><small>{note}</small></span></a>'
 return ('<div class="fab" data-fab><div class="fab-menu" id="fab-menu" role="group" aria-label="Написать нам">'
  +link(TG_URL,'telegram','Telegram','Написать в чат')+link(MAX_URL,'max','MAX','Написать в чат')
  +'</div><button class="fab-toggle" type="button" aria-expanded="false" aria-controls="fab-menu" aria-label="Написать нам"><span class="fab-tip">Написать нам</span>'+chat+close+'</button></div>')
def layout(p,body):
 body=apply_all_photos(p,body)
 return '<!DOCTYPE html>\n<html lang="ru"><head>'+head(p)+'</head><body class="'+('home-page' if p['url']=='/' else 'inner-page')+'">'+header(p['url'])+'<main id="main">'+body+'</main>'+footer()+mobile_cta()+fab()+'</body></html>'
def write(url,content):
 dest=ROOT/url.strip('/')/'index.html';dest.parent.mkdir(parents=True,exist_ok=True);dest.write_text(rebase(apply_identity(content)))

def build_page(p):
 path=p['url'];ss=parse_page(p);hero=ss.pop(0);home=path=='/'
 eyebrow=val(p['body'],'Надзаголовок') if home else labels[path]
 hero_lines=hero['lines'];facts=''
 if home:
  idx=next(i for i,l in enumerate(hero_lines) if l.startswith('Короткие факты'))
  facts=render_lines(hero_lines[idx:],p);hero_lines=hero_lines[:idx]
 # Gallery intentionally shows text categories; no photographic claims fabricated.
 breadcrumb='' if home else '<div class="breadcrumbs"><a href="/">Главная</a><span>/</span><span>'+e(labels[path])+'</span></div>'
 herohtml=render_lines(hero_lines,p)
 iswide=path in ['/about/team/','/gallery/','/materials/','/raschet/']
 if home:
  right='<aside class="hero-panel"><div class="panel-label">'+icon('ruler')+'Ваш будущий ангар</div><h2>Начнём<br>с вашей задачи</h2><p>Оставьте контакт и несколько слов о задаче. Уточним параметры и состав работ.</p>'+form('short','hero-form')+'<a class="brief-link" href="/raschet/#brief">Есть готовое ТЗ? Передайте параметры ↗</a></aside>'
  body='<section class="hero home-hero"><div class="shell hero-grid"><div class="hero-copy"><p class="eyebrow">'+e(eyebrow)+'</p><h1>'+e(p['h1'])+'</h1><div class="hero-description">'+herohtml+'</div></div>'+right+'</div></section><div class="shell">'+facts+'</div>'
 else:
  body='<section class="hero inner-hero"><div class="shell">'+breadcrumb+'<p class="eyebrow">'+e(eyebrow)+'</p><h1>'+e(p['h1'])+'</h1><div class="hero-description '+('wide-hero' if iswide else '')+'">'+herohtml+'</div></div></section>'
 if path=='/projects/':
  # На /projects/ карточки — содержимое верхнего уровня, поэтому h2: иначе после h1 идёт сразу h3.
  body+='<section class="section"><div class="shell filter-section">'+filters(['Все','Склады','Ремонтные мастерские','Производство','Техника','Спорт','Другие объекты'])+'<div class="case-grid">'+''.join(casecard(id,'h2') for id in cases if id!='P04')+'</div></div></section>'
 if path=='/technology/':
  body+='<nav class="section-nav" aria-label="Разделы комплектации"><div class="shell">'+''.join(f'<a href="#{s["anchor"]}">{e(anchors.get(s["anchor"],s["title"]))}</a>' for s in ss if s['anchor'] in anchors)+'<a href="#loads">Нагрузки</a></div></nav>'
  ss.insert(-1,dict(title='Нагрузки зависят от места строительства',anchor='loads',lines=[re.search(r'H2: Нагрузки зависят.*?\nЯкорь: loads\n(Текст: [^\n]+)',SOURCE,re.S).group(1)]))
 for n,s in enumerate(ss):
  lines=s['lines'];content=render_lines(lines,p,s['anchor'])
  if path=='/angary/' and s['title']=='Выберите назначение':content+=cards(home_cards)
  if path=='/angary/gotovye/' and s['title']=='Выберите размеры и исполнение':
   content+='<div class="filter-section">'+filters(['Все','Склад','РММ'])+'<div class="card-grid stock-grid">'
   for g in stock:
    if g['id']=='G09':continue
    content+=f'<article class="stock-card filter-card" data-category="{g["purpose"].rstrip(".")}">{icon("hangar")}<p class="eyebrow">{e(g["purpose"].rstrip("."))} · по запросу</p><h3>{e(g["title"])}</h3><p>Прямостенная конструкция с двускатной крышей. Уточним доступность комплекта и проверим соответствие условиям вашей площадки.</p>'+(f'<p class="caption">{e(g["loads"])}</p>' if g['loads'] else '')+link('Уточнить наличие и комплектацию','/raschet/?ready='+g['id'])+'</article>'
   content+='</div></div>'
  full=home or '<div class="card-grid' in content or '<div class="case-grid' in content or '<form' in content or '<ol class="steps"' in content
  classes='section '+('section-tint ' if n%2==0 else '')+('section-full' if full else 'section-split')
  body+=f'<section class="{classes}" id="{s["anchor"]}"><div class="shell section-layout"><div class="section-heading"><p class="section-number">{str(n+1).zfill(2)} / {e(labels[path] if not home else "Тентовые конструкции")}</p><h2>{e(s["title"])}</h2></div><div class="section-content">{content}</div></div></section>'
 if path not in ['/','/raschet/','/tendery/']:
  body+='<section class="contact-banner" id="request"><div class="shell"><div><p class="eyebrow">Ваш проект</p><h2>Обсудим ваш ангар</h2><p>Оставьте контакт и несколько слов о задаче. Уточним параметры и состав работ.</p></div>'+form('short','end-form')+'</div></section>'
 if home:body=apply_home_photos(body,form)
 return layout(p,body)

for p in pages:write(p['url'],build_page(p))
for id,c in cases.items():
 if id=='P04':continue
 b='<section class="hero inner-hero"><div class="shell"><div class="breadcrumbs"><a href="/">Главная</a><span>/</span><a href="/projects/">Проекты</a></div><p class="eyebrow">'+e(casecat(id))+'</p><h1>'+e(c['h1'])+'</h1></div></section><section class="section"><div class="shell project-layout"><div><h2>Задача и решение</h2><p class="project-copy">'+e(c['text'])+'</p>'+link('Рассчитать похожий ангар','/raschet/?project='+id,'button')+'</div><aside class="project-spec">'+icon('ruler')+'<h2>Параметры объекта</h2>'+(f'<p class="dimension">{e(c["params"].split(";")[0])}</p><p>Ширина × длина × высота внешней стены</p>' if c['params'] else '<p>Для подбора размеров передайте параметры вашего объекта.</p>')+(f'<p class="caption">{e(c["loads"])}</p>' if c['loads'] else '')+'</aside></div></section><section class="contact-banner" id="request"><div class="shell"><div><p class="eyebrow">Следующий шаг</p><h2>Нужен похожий объект?</h2><p>Опишите, что должно отличаться: размеры, место строительства, покрытие или оборудование.</p></div>'+form('short','case-form','Рассчитать похожий ангар')+'</div></section>'
 write(c['url'],layout(c,b))
(ROOT/'js/content-map.json').write_text(json.dumps({id:dict(title=c['h1'],url=c['url']) for id,c in cases.items()},ensure_ascii=False,indent=2))
(ROOT/'content/manifest.json').write_text(json.dumps(dict(pages=[dict(url=p['url'],title=p['h1']) for p in pages],projects=[dict(id=id,url=c['url'],title=c['h1']) for id,c in cases.items() if id!='P04'],stock=stock,excluded=['P04','G09']),ensure_ascii=False,indent=2))


notfound='<section class="hero inner-hero"><div class="shell"><p class="eyebrow">Ошибка 404</p><h1>Страница не найдена</h1><div class="hero-description"><p>Возможно, ссылка устарела или адрес набран с ошибкой. Вернитесь на главную или выберите раздел в меню.</p><a class="button" href="/">На главную'+icon('arrow')+'</a></div></div></section>'
(ROOT/'404.html').write_text(rebase(apply_identity(layout(dict(url='/404.html',title='Страница не найдена | Тентовые конструкции'),notfound)).replace('<meta name="robots" content="index,follow">','<meta name="robots" content="noindex,nofollow">').replace('<link rel="canonical" href="'+SITE+'/404.html">','')))
all_urls=[p['url'] for p in pages]+[c['url'] for id,c in cases.items() if id!='P04']
if PUBLISH:
 (ROOT/'robots.txt').write_text(f'User-agent: *\nAllow: /\n\nSitemap: {SITE}/sitemap.xml\n')
 today=datetime.date.today().isoformat()
 (ROOT/'sitemap.xml').write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'+''.join(f'<url><loc>{SITE}{u}</loc><lastmod>{today}</lastmod></url>\n' for u in all_urls)+'</urlset>\n')
else:
 (ROOT/'robots.txt').write_text('User-agent: *\nDisallow: /\n')
 (ROOT/'sitemap.xml').unlink(missing_ok=True)

css_kb=(ROOT/'css/site.css').stat().st_size/1024
print(f'Built {len(pages)} main pages, {len(cases)-1} project pages and 404.')
print(f'CSS собран в css/site.css ({css_kb:.1f} КБ из {len(CSS_PARTS)} частей).')
print('Режим публикации ВКЛЮЧЁН.' if PUBLISH else 'Режим предпросмотра: noindex и robots закрыты до выбора домена. Для публикации — PUBLISH=True и настоящий SITE.')
