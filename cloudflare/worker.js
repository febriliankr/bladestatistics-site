const TYPES = {
  html: 'text/html; charset=utf-8', css: 'text/css; charset=utf-8',
  js: 'text/javascript; charset=utf-8', json: 'application/json; charset=utf-8',
  txt: 'text/plain; charset=utf-8', xml: 'application/xml; charset=utf-8',
  svg: 'image/svg+xml', png: 'image/png', jpg: 'image/jpeg', jpeg: 'image/jpeg',
  webp: 'image/webp', ico: 'image/x-icon', woff: 'font/woff', woff2: 'font/woff2',
}

export default {
  async fetch(request, env) {
    const url = new URL(request.url)
    if (url.protocol === 'http:' || url.hostname === 'www.bladestatistics.com') {
      url.protocol = 'https:'
      if (url.hostname === 'www.bladestatistics.com') url.hostname = 'bladestatistics.com'
      return Response.redirect(url.toString(), 301)
    }
    if (!['GET', 'HEAD'].includes(request.method)) {
      return new Response('Method not allowed', { status: 405, headers: { Allow: 'GET, HEAD' } })
    }
    let pathname
    try { pathname = decodeURIComponent(url.pathname) } catch {
      return new Response('Invalid path', { status: 400 })
    }
    if (pathname.includes('\\') || pathname.includes('\0') || pathname.split('/').some(p => p.startsWith('.'))) {
      return new Response('Not found', { status: 404 })
    }
    const path = pathname.replace(/^\/+/, '')
    const candidates = path.endsWith('/') || !path
      ? [`${path}index.html`]
      : /\.[^/]+$/.test(path) ? [path] : [`${path}/index.html`, `${path}.html`]
    let object, key
    for (const candidate of candidates) {
      key = candidate
      object = await env.SITE.get(`releases/${env.SITE_RELEASE}/${key}`)
      if (object) break
    }
    if (!object) return new Response('Not found', { status: 404, headers: { 'Cache-Control': 'no-store' } })
    if (key.endsWith('/index.html') && !pathname.endsWith('/') && !pathname.endsWith('/index.html')) {
      url.pathname += '/'
      return Response.redirect(url.toString(), 301)
    }
    const headers = new Headers()
    object.writeHttpMetadata(headers)
    headers.set('Content-Type', TYPES[key.split('.').pop()] || 'application/octet-stream')
    headers.set('ETag', object.httpEtag)
    headers.set('Last-Modified', object.uploaded.toUTCString())
    headers.set('X-Content-Type-Options', 'nosniff')
    headers.set('Strict-Transport-Security', 'max-age=31536000')
    headers.set('X-Blade-Site-Release', env.SITE_RELEASE)
    headers.set('Cache-Control', /^(login|account|billing)\//.test(key)
      ? 'no-store' : key.endsWith('.html') ? 'public, max-age=0, must-revalidate' : 'public, max-age=3600')
    const matches = request.headers.get('If-None-Match')?.split(',').some(tag => {
      const value = tag.trim().replace(/^W\//, '')
      return value === '*' || value === object.httpEtag
    })
    if (matches) return new Response(null, { status: 304, headers })
    headers.set('Content-Length', String(object.size))
    return new Response(request.method === 'HEAD' ? null : object.body, { headers })
  },
}
