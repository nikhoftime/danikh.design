#!/usr/bin/env python3
"""Turns originals/ (full-size files from Framer) into web-sized files in media/.
Images -> WebP (max 2000px wide). GIFs and MP4s -> silent looping H.264 MP4 (max 1600px wide)."""
import os, subprocess, sys
from concurrent.futures import ThreadPoolExecutor
from PIL import Image
Image.MAX_IMAGE_PIXELS = None
SRC, OUT = 'originals', 'media'
os.makedirs(OUT, exist_ok=True)
def out_name(n):
    stem, ext = os.path.splitext(n)
    return stem + ('.mp4' if ext.lower() in ('.gif', '.mp4') else '.webp')
def do(n):
    src, dst = os.path.join(SRC, n), os.path.join(OUT, out_name(n))
    if os.path.exists(dst): return
    ext = os.path.splitext(n)[1].lower()
    if ext in ('.gif', '.mp4'):
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', src, '-vf',
            "scale='min(1600,iw)':-2:flags=lanczos,fps=30,format=yuv420p",
            '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '27', '-c:a', 'aac', '-b:a', '96k', '-movflags', '+faststart', dst], check=True)
    else:
        im = Image.open(src); im.load()
        im = im.convert('RGBA' if im.mode in ('RGBA', 'LA', 'P') else 'RGB')
        if im.width > 2000: im = im.resize((2000, round(im.height * 2000 / im.width)), Image.LANCZOS)
        im.save(dst, 'WEBP', quality=82, method=5)
with ThreadPoolExecutor(2) as ex: list(ex.map(do, sorted(os.listdir(SRC))))
print('done')

# Small covers for the work grid
import glob, json
os.makedirs(os.path.join(OUT, 'thumb'), exist_ok=True)
for f in glob.glob('content/*.txt'):
    for l in open(f):
        if l.startswith('COVER '):
            n = l.split()[1]; dst = os.path.join(OUT, 'thumb', os.path.splitext(n)[0] + '.webp')
            if not os.path.exists(dst):
                im = Image.open(os.path.join(OUT, out_name(n))).convert('RGB')
                im.thumbnail((1000, 1000), Image.LANCZOS); im.save(dst, 'WEBP', quality=80, method=5)

# Manifest: size of every file and whether a video has sound (used by build.py)
man = {}
for n in sorted(os.listdir(SRC)):
    p = os.path.join(OUT, out_name(n))
    if p.endswith('.mp4'):
        r = subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'stream=codec_type,width,height', '-of', 'json', p], capture_output=True, text=True)
        st = json.loads(r.stdout)['streams']
        v = next(s for s in st if s['codec_type'] == 'video')
        man[n] = {'file': out_name(n), 'w': v['width'], 'h': v['height'], 'audio': any(s['codec_type'] == 'audio' for s in st)}
    else:
        w, h = Image.open(p).size
        man[n] = {'file': out_name(n), 'w': w, 'h': h}
json.dump(man, open(os.path.join(OUT, 'manifest.json'), 'w'), indent=1)
print('manifest', len(man))
