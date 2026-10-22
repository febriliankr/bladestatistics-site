#!/usr/bin/env python3
"""Publish an immutable public build to R2, then atomically switch the Worker."""
import concurrent.futures, hashlib, json, mimetypes, os, pathlib, subprocess, sys, urllib.error, urllib.parse, urllib.request
ROOT = pathlib.Path(__file__).resolve().parent
ACCOUNT = os.environ['CLOUDFLARE_ACCOUNT_ID']
TOKEN = os.environ['CLOUDFLARE_API_TOKEN']
BUCKET = 'blade-website'
API = f'https://api.cloudflare.com/client/v4/accounts/{ACCOUNT}/r2/buckets/{BUCKET}'

def api(method, url, data=None):
    headers = {'Authorization': 'Bearer '+TOKEN}
    if data is not None: headers['Content-Type'] = 'application/json'
    req = urllib.request.Request(url, data=None if data is None else json.dumps(data).encode(), headers=headers, method=method)
    with urllib.request.urlopen(req, timeout=30) as response:
        result = json.load(response)
        if not result.get('success'): raise RuntimeError(result.get('errors'))
        return result.get('result')

subprocess.run([sys.executable, str(ROOT/'build.py')], check=True)
subprocess.run(['node', '--test', str(ROOT/'worker.test.mjs')], check=True)
manifest = json.loads((ROOT/'release.json').read_text())
release = manifest['release']
try: api('GET', API)
except urllib.error.HTTPError as error:
    if error.code != 404: raise
    api('POST', API.rsplit('/', 1)[0], {'name': BUCKET})

def put(item):
    relative, expected = item
    file = ROOT/'dist'/relative
    if hashlib.sha256(file.read_bytes()).hexdigest() != expected:
        raise RuntimeError('Build changed during publication: '+relative)
    key = f'releases/{release}/{relative}'
    mime = mimetypes.guess_type(relative)[0] or 'application/octet-stream'
    config = f'header = "Authorization: Bearer {TOKEN}"\n'
    result = subprocess.run(['curl','--config','-','--fail-with-body','--silent','--show-error',
        '--retry','3','--retry-all-errors','--max-time','180','--connect-timeout','20',
        '--request','PUT','--header','Content-Type: '+mime,'--upload-file',str(file),
        API+'/objects/'+urllib.parse.quote(key, safe='/')], input=config, text=True, capture_output=True)
    if result.returncode: raise RuntimeError('R2 upload failed for '+relative+': '+result.stderr[:300])
    response = json.loads(result.stdout)
    if not response.get('success'): raise RuntimeError('R2 rejected '+relative+': '+str(response.get('errors')))
    return relative

with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
    uploaded = list(pool.map(put, manifest['files'].items()))
print(f'Uploaded {len(uploaded)} files to r2://{BUCKET}/releases/{release}/', flush=True)
config_path = ROOT/'wrangler.jsonc'
config = json.loads(config_path.read_text())
old = config['vars']['SITE_RELEASE']
config['vars']['SITE_RELEASE'] = release
config_path.write_text(json.dumps(config, indent=2)+'\n')
child_env = os.environ.copy()
# Public routes need zone permissions. The existing global key is kept solely
# in the local secret store/environment; it is never written into the config.
if config.get('routes') and child_env.get('CLOUDFLARE_GLOBAL_API_KEY'):
    child_env['CLOUDFLARE_API_KEY'] = child_env['CLOUDFLARE_GLOBAL_API_KEY']
    child_env.pop('CLOUDFLARE_API_TOKEN', None)
try:
    subprocess.run(['npx','--yes','wrangler@4.130.0','deploy','--config',str(config_path)], cwd=ROOT, env=child_env, check=True)
except BaseException:
    config['vars']['SITE_RELEASE'] = old
    config_path.write_text(json.dumps(config, indent=2)+'\n')
    raise
print('Published website release '+release, flush=True)
