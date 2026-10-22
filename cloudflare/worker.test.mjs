import test from 'node:test'
import assert from 'node:assert/strict'
import worker from './worker.js'
const release = 'test-release'
const pages = new Map([
  ['index.html', 'home'], ['id/index.html', 'locale'], ['pricing/index.html', 'pricing'],
  ['login/index.html', 'login'], ['account/index.html', 'account'],
  ['billing/success.html', 'paid'], ['assets/auth.js', 'javascript'], ['robots.txt', 'robots'],
])
function env() {
  return { SITE_RELEASE: release, SITE: { async get(key) {
    assert.ok(key.startsWith(`releases/${release}/`))
    const text = pages.get(key.slice(`releases/${release}/`.length))
    return text ? { body: text, size: Buffer.byteLength(text), httpEtag: '"example"',
      uploaded: new Date('2026-10-23T00:00:00Z'), writeHttpMetadata() {} } : null
  } } }
}
const fetch = (path, options) => worker.fetch(new Request('https://bladestatistics.com'+path, options), env())
test('serves root, translated pages, assets, and clean billing return URLs', async () => {
  for (const [path, expected] of [['/','home'],['/id/','locale'],['/billing/success?session=1','paid'],['/robots.txt','robots']]) {
    const r=await fetch(path); assert.equal(r.status,200); assert.equal(await r.text(),expected)
    assert.equal(r.headers.get('x-blade-site-release'),release)
  }
  assert.equal((await fetch('/assets/auth.js')).headers.get('content-type'),'text/javascript; charset=utf-8')
})
test('canonical directory redirects preserve query parameters', async () => {
  const r=await fetch('/pricing?plan=pro');assert.equal(r.status,301)
  assert.equal(r.headers.get('location'),'https://bladestatistics.com/pricing/?plan=pro')
})
test('HTTP and www redirect to HTTPS apex', async () => {
  for (const origin of ['http://bladestatistics.com','https://www.bladestatistics.com']) {
    const r=await worker.fetch(new Request(origin+'/id/?x=1'),env())
    assert.equal(r.status,301);assert.equal(r.headers.get('location'),'https://bladestatistics.com/id/?x=1')
  }
})
test('account and billing pages are never cached', async () => {
  for(const p of ['/login/','/account/','/billing/success'])assert.equal((await fetch(p)).headers.get('cache-control'),'no-store')
})
test('HEAD has metadata and no body; ETags support weak and list conditions', async () => {
  const h=await fetch('/',{method:'HEAD'});assert.equal(await h.text(),'');assert.equal(h.headers.get('content-length'),'4')
  for(const value of ['"example"','W/"example"','"old", "example"','*']) {
    const r=await fetch('/',{headers:{'If-None-Match':value}});assert.equal(r.status,304);assert.equal(await r.text(),'')
  }
})
test('unknown paths and source files return 404; POST cannot write to R2', async () => {
  for(const p of ['/missing','/src/shell.html','/.git/config','/%2Eenv','/%00'])assert.equal((await fetch(p)).status,404)
  const r=await fetch('/',{method:'POST'});assert.equal(r.status,405);assert.equal(r.headers.get('allow'),'GET, HEAD')
})
test('malformed percent escapes return 400', async () => assert.equal((await fetch('/%zz')).status,400))
