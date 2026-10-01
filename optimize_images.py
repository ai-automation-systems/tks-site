"""Responsive derivatives for every photo: AVIF + WebP at several widths, plus a blur-up placeholder.

Originals are never modified. Output goes to img/opt/ and content/image-manifest.json,
which all_photos.py and home_photo.py read to emit srcset/sizes/width/height.
Re-running is incremental: existing derivatives are reused unless the source is newer.
"""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import json, base64, io, sys
from PIL import Image

ROOT = Path(__file__).resolve().parent
SRC_DIRS = [ROOT/'img', ROOT/'img/library', ROOT/'img/generated', ROOT/'img/projects-2026']
OUT = ROOT/'img/opt'
WIDTHS = [400, 800, 1200, 1600]
EXT = {'.jpg', '.jpeg', '.png', '.webp'}
OUT.mkdir(parents=True, exist_ok=True)

def sources():
    seen = []
    for d in SRC_DIRS:
        for p in sorted(d.iterdir()):
            if p.is_file() and p.suffix.lower() in EXT and OUT not in p.parents:
                seen.append(p)
    return seen

def lqip(im):
    """Tiny blurred placeholder, inlined as a data URI."""
    t = im.copy()
    t.thumbnail((20, 20), Image.LANCZOS)
    buf = io.BytesIO()
    t.convert('RGB').save(buf, 'WEBP', quality=32, method=6)
    return 'data:image/webp;base64,' + base64.b64encode(buf.getvalue()).decode()

def process(p):
    rel = '/' + p.relative_to(ROOT).as_posix()
    try:
        im = Image.open(p)
        im.load()
    except Exception as exc:
        return rel, None, f'{p.name}: {exc}'
    if im.mode not in ('RGB', 'RGBA'):
        im = im.convert('RGBA' if 'A' in im.mode else 'RGB')
    w0, h0 = im.size
    targets = sorted({w for w in WIDTHS if w < w0} | {min(w0, 1600)})
    variants = {'avif': [], 'webp': []}
    # У снимков из подпапок generated/ и projects-2026 имена совпадают с корневыми (production, repair…) — добавляем префикс папки.
    stem = p.stem if p.parent in (ROOT/'img', ROOT/'img/library') else f'{p.parent.name}-{p.stem}'
    for w in targets:
        h = max(1, round(h0 * w / w0))
        resized = im if w == w0 else im.resize((w, h), Image.LANCZOS)
        for fmt, ext, kw in (('AVIF', 'avif', dict(quality=58)),
                             ('WEBP', 'webp', dict(quality=82, method=6))):
            dest = OUT/f'{stem}-{w}.{ext}'
            if not dest.exists() or dest.stat().st_mtime < p.stat().st_mtime:
                out = resized
                if fmt == 'AVIF' and out.mode == 'RGBA':
                    out = out.convert('RGB')
                out.save(dest, fmt, **kw)
            variants[ext].append([w, '/' + dest.relative_to(ROOT).as_posix()])
    return rel, dict(w=w0, h=h0, variants=variants, lqip=lqip(im)), None

def main():
    files = sources()
    manifest, errors = {}, []
    with ThreadPoolExecutor(max_workers=8) as pool:
        for n, (rel, data, err) in enumerate(pool.map(process, files), 1):
            if err:
                errors.append(err)
            else:
                manifest[rel] = data
            if n % 25 == 0:
                print(f'  {n}/{len(files)}', flush=True)
    (ROOT/'content/image-manifest.json').write_text(
        json.dumps(manifest, ensure_ascii=False, indent=1))
    before = sum(p.stat().st_size for p in files)
    after = sum(p.stat().st_size for p in OUT.iterdir())
    print(f'\nИсходники:   {before/1048576:6.1f} МБ  ({len(files)} файлов)')
    print(f'Производные: {after/1048576:6.1f} МБ  ({len(list(OUT.iterdir()))} файлов)')
    smallest = sum(min(p.stat().st_size for p in OUT.glob(f'{Path(f).stem}-*.avif'))
                   for f in files if list(OUT.glob(f'{Path(f).stem}-*.avif')))
    print(f'Мобильный набор (мин. AVIF по каждому фото): {smallest/1048576:.1f} МБ')
    for e in errors:
        print('ОШИБКА', e, file=sys.stderr)

if __name__ == '__main__':
    main()
