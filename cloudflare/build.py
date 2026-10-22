#!/usr/bin/env python3
"""Stage only public website files, and derive an immutable R2 release id."""
import hashlib, importlib.util, json, pathlib, shutil, subprocess, sys
ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / 'cloudflare' / 'dist'
subprocess.run([sys.executable, str(ROOT / 'build.py')], cwd=ROOT, check=True)
spec = importlib.util.spec_from_file_location('blade_site', ROOT / 'build.py')
site = importlib.util.module_from_spec(spec)
spec.loader.exec_module(site)
if OUT.exists(): shutil.rmtree(OUT)
OUT.mkdir()
public = ['index.html', 'robots.txt', 'sitemap.xml', 'assets', 'share', 'app.png', 'logo.png', 'demo']
public += [code for code in site.ORDER if code != 'en'] + list(site.PAGES)
public += sorted({str(pathlib.PurePosixPath(p).parts[0]) for p in site.HIDDEN_PAGES})
for name in public:
    source, target = ROOT / name, OUT / name
    if source.is_dir(): shutil.copytree(source, target)
    else: shutil.copy2(source, target)
files = {p.relative_to(OUT).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
         for p in sorted(OUT.rglob('*')) if p.is_file()}
assert not any(p.startswith('.') or '/.' in p or pathlib.Path(p).suffix not in
               {'.html', '.css', '.js', '.json', '.xml', '.txt', '.svg', '.png', '.jpg', '.jpeg', '.webp', '.ico', '.woff', '.woff2'} for p in files)
manifest = json.dumps(files, sort_keys=True, separators=(',', ':'))
release = hashlib.sha256(manifest.encode()).hexdigest()[:20]
(ROOT / 'cloudflare' / 'release.json').write_text(json.dumps({'release': release, 'files': files}, indent=2)+'\n')
print(f'R2 website release {release}: {len(files)} public files')
