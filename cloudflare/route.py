#!/usr/bin/env python3
"""Switch only the website hostnames to the R2 Worker, with a saved rollback."""
import json, os, pathlib, sys, urllib.request
ROOT=pathlib.Path(__file__).resolve().parent
BACKUP=ROOT/'rollback-dns.json'
BASE='https://api.cloudflare.com/client/v4'
HEADERS={'X-Auth-Key':os.environ['CLOUDFLARE_GLOBAL_API_KEY'], 'X-Auth-Email':os.environ['CLOUDFLARE_EMAIL'], 'Content-Type':'application/json'}
HOSTS={'bladestatistics.com','www.bladestatistics.com'}
PATTERNS={h+'/*' for h in HOSTS}
def api(method,path,data=None):
 req=urllib.request.Request(BASE+path,data=None if data is None else json.dumps(data).encode(),headers=HEADERS,method=method)
 with urllib.request.urlopen(req,timeout=30) as r:
  result=json.load(r)
  if not result.get('success'):raise RuntimeError(result.get('errors'))
  return result.get('result')
if '--rollback' in sys.argv:
 state=json.loads(BACKUP.read_text()); zone=state['zone_id']
 for route in api('GET',f'/zones/{zone}/workers/routes'):
  if route['pattern'] in PATTERNS and route.get('script')=='blade-website':
   old=next((r for r in state['routes'] if r['pattern']==route['pattern']),None)
   if old: api('PUT',f'/zones/{zone}/workers/routes/{route["id"]}',{'pattern':old['pattern'],'script':old.get('script')})
   else: api('DELETE',f'/zones/{zone}/workers/routes/{route["id"]}')
 for r in state['records']:
  api('PATCH',f'/zones/{zone}/dns_records/{r["id"]}',{'proxied':r['proxied'],'ttl':r['ttl']})
 print('Restored previous website routing and DNS proxy settings; R2 files retained.')
 sys.exit()
zones=api('GET','/zones?name=bladestatistics.com')
assert len(zones)==1 and zones[0]['status']=='active'
zone=zones[0]['id']
records=[r for r in api('GET',f'/zones/{zone}/dns_records') if r['name'] in HOSTS and r['type'] in {'A','AAAA','CNAME'}]
assert {r['name'] for r in records}==HOSTS
routes=[r for r in api('GET',f'/zones/{zone}/workers/routes') if r['pattern'] in PATTERNS]
assert all(r.get('script') in {None,'blade-website'} for r in routes),'Existing route belongs to another Worker'
if not BACKUP.exists(): BACKUP.write_text(json.dumps({'zone_id':zone,'records':records,'routes':routes},indent=2)+'\n')
for pattern in sorted(PATTERNS):
 existing=next((r for r in routes if r['pattern']==pattern),None)
 body={'pattern':pattern,'script':'blade-website'}
 if existing: api('PUT',f'/zones/{zone}/workers/routes/{existing["id"]}',body)
 else: api('POST',f'/zones/{zone}/workers/routes',body)
 print('Routed '+pattern+' to blade-website',flush=True)
for record in records:
 api('PATCH',f'/zones/{zone}/dns_records/{record["id"]}',{'proxied':True,'ttl':1})
 print('Enabled Cloudflare proxy for '+record['name']+' ('+record['type']+')',flush=True)
config_path=ROOT/'wrangler.jsonc';config=json.loads(config_path.read_text())
config['routes']=[{'pattern':pattern,'zone_name':'bladestatistics.com'} for pattern in sorted(PATTERNS)]
config_path.write_text(json.dumps(config,indent=2)+'\n')
print('Website cutover complete. Original DNS targets and other subdomains are unchanged.')
