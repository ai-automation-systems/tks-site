"""Единая сборка <picture> по манифесту из optimize_images.py.

Отдаёт AVIF с запасным WebP, проставляет реальные width/height (убирает сдвиг вёрстки)
и подкладывает размытую миниатюру, пока грузится полноразмерный файл.
Если манифеста нет, возвращается обычный <img> на исходный файл.
"""
from pathlib import Path
import json, html

ROOT = Path(__file__).resolve().parent
_manifest_path = ROOT/'content/image-manifest.json'
MANIFEST = json.loads(_manifest_path.read_text()) if _manifest_path.exists() else {}

# Ширины показа для типовых мест вёрстки — браузер по ним выбирает вариант из srcset.
SIZES = {
    'hero':     '(min-width:1024px) 46vw,(min-width:768px) 60vw,100vw',
    'inner':    '(min-width:1024px) 44vw,(min-width:768px) 60vw,100vw',
    'grid-3':   '(min-width:1024px) 31vw,(min-width:768px) 46vw,100vw',
    'grid-2':   '(min-width:768px) 46vw,100vw',
    'card':     '(min-width:768px) 46vw,100vw',
    'thumb':    '180px',
    'portrait': '150px',
    'full':     '100vw',
}


def e(s):
    return html.escape(str(s), quote=True)


def picture(src, alt, cls='', sizes='grid-3', eager=False, attrs=''):
    """<picture> с AVIF/WebP-наборами. eager=True — для изображения первого экрана."""
    m = MANIFEST.get(src)
    sizes_attr = SIZES.get(sizes, sizes)
    loading = 'eager" fetchpriority="high' if eager else 'lazy'
    cls_attr = f' class="{e(cls)}"' if cls else ''
    if not m:
        return (f'<img src="{e(src)}" alt="{e(alt)}" loading="{loading}" '
                f'decoding="async"{cls_attr} {attrs}>')
    avif = ','.join(f'{p} {w}w' for w, p in m['variants']['avif'])
    webp = ','.join(f'{p} {w}w' for w, p in m['variants']['webp'])
    fallback = m['variants']['webp'][-1][1]
    style = (f'background-image:url({m["lqip"]});background-size:cover;'
             f'background-position:center')
    return (f'<picture>'
            f'<source type="image/avif" srcset="{avif}" sizes="{sizes_attr}">'
            f'<source type="image/webp" srcset="{webp}" sizes="{sizes_attr}">'
            f'<img src="{fallback}" alt="{e(alt)}" width="{m["w"]}" height="{m["h"]}" '
            f'loading="{loading}" decoding="async" style="{style}"{cls_attr} {attrs}>'
            f'</picture>')


def natural(src):
    """Натуральный размер исходника — нужен, чтобы просмотрщик не растягивал мелкие фото."""
    m = MANIFEST.get(src)
    return (m['w'], m['h']) if m else (0, 0)


def best(src, width=1600):
    """Путь к варианту не шире width — для ссылки «увеличить»."""
    m = MANIFEST.get(src)
    if not m:
        return src
    fits = [p for w, p in m['variants']['webp'] if w <= width]
    return fits[-1] if fits else m['variants']['webp'][0][1]
