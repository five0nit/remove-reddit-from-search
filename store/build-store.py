"""Render the original listing assets and package the canonical extension."""
from hashlib import sha256
from io import BytesIO
import json
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'extension'
OUT = ROOT / 'store'
INK = '#172923'
PAPER = '#F5F0E3'
ACID = '#DBF38F'


def filter_mark():
    # 96×96 tile within a 128×128 canvas; render at 4× for clean edges.
    scale = 4
    image = Image.new('RGBA', (128 * scale,) * 2)
    draw = ImageDraw.Draw(image)
    draw.rounded_rectangle(tuple(v * scale for v in (16, 16, 111, 111)), 22 * scale, fill=INK)
    for (left, right, top), color in zip(((40, 88, 43), (47, 81, 59), (57, 71, 75)), (PAPER, PAPER, ACID)):
        draw.rounded_rectangle(tuple(v * scale for v in (left, top, right, top + 8)), 4 * scale, fill=color)
    return image.resize((128, 128), Image.Resampling.LANCZOS)


def png(image):
    data = BytesIO()
    image.save(data, 'PNG', optimize=True)
    return data.getvalue()


def tile(icon, title):
    im = Image.new('RGB', (440, 280), PAPER)
    draw = ImageDraw.Draw(im)
    small_icon = icon.resize((104, 104), Image.Resampling.LANCZOS)
    im.paste(small_icon, (320, 10), small_icon)
    draw.rounded_rectangle((28, 30, 63, 36), radius=3, fill=INK)
    title_font = ImageFont.truetype('DejaVuSans-Bold.ttf', 25)
    left, top, right, bottom = draw.textbbox((28, 113), title, font=title_font)
    assert 28 <= left < right <= 412 and 114 <= top < bottom <= 151
    draw.text((28, 113), title, font=title_font, fill=INK)
    draw.text((30, 155), 'Filter Reddit links', font=ImageFont.truetype('DejaVuSans.ttf', 26), fill=INK)
    draw.text((30, 190), 'from Google results.', font=ImageFont.truetype('DejaVuSans.ttf', 26), fill=INK)
    draw.line((30, 245, 410, 245), fill='#A7AF9C', width=1)
    return im


def package(path, files):
    with ZipFile(path, 'w', compression=ZIP_DEFLATED) as archive:
        for name, content in files.items():
            item = ZipInfo(name)
            item.external_attr = 0o100644 << 16
            archive.writestr(item, content, compress_type=ZIP_DEFLATED, compresslevel=9)
    with ZipFile(path) as archive:
        assert archive.testzip() is None
        assert archive.namelist() == list(files)
        assert all(archive.read(name) == content for name, content in files.items())
    print(f'{path.name}  SHA-256 {sha256(path.read_bytes()).hexdigest()}')


def main():
    manifest = json.loads((SOURCE / 'manifest.json').read_text())
    title = manifest['name']
    assert title == 'remove reddit from search' and manifest['manifest_version'] == 3
    slug = title.replace(' ', '-')
    icon = filter_mark()
    promo = tile(icon, title)
    assert icon.size == (128, 128) and icon.getpixel((0, 0))[3] == 0
    assert promo.size == (440, 280) and promo.mode == 'RGB'
    icon_bytes = png(icon)
    (OUT / 'icon128.png').write_bytes(icon_bytes)
    (OUT / 'promo440x280.png').write_bytes(png(promo))
    manifest['icons'] = {'128': 'icon128.png'}
    files = {
        'manifest.json': (json.dumps(manifest, indent=2) + '\n').encode(),
        'filter-search.js': (SOURCE / 'filter-search.js').read_bytes(),
        'icon128.png': icon_bytes,
    }
    store_zip = OUT / f'{slug}-store.zip'
    package(store_zip, files)
    package(ROOT / f'{slug}.zip', {
        f'{slug}/{name}': content
        for name, content in {**files, 'README.md': (SOURCE / 'README.md').read_bytes()}.items()
    })
    package(OUT / f'{slug}-submission-kit.zip', {
        name: (OUT / name).read_bytes()
        for name in (store_zip.name, 'icon128.png', 'promo440x280.png', 'listing.md', 'privacy.html')
    })


if __name__ == '__main__':
    main()
