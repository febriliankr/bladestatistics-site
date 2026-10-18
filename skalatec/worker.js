// The account token can't flip the zone's "Always Use HTTPS", so the redirect
// lives here. Everything else is static files from ./dist, including the
// billing return pages Xendit sends buyers back to.
const MOVED = {
  // The old workflow site linked to a separate statistics page. The whole
  // site is that page now.
  '/statistics': '/',
  '/statistics.html': '/',
}

export default {
  async fetch(request, env) {
    const url = new URL(request.url)
    if (url.protocol === 'http:') {
      url.protocol = 'https:'
      return Response.redirect(url.toString(), 301)
    }
    if (MOVED[url.pathname]) {
      url.pathname = MOVED[url.pathname]
      return Response.redirect(url.toString(), 301)
    }
    const res = await env.ASSETS.fetch(request)
    const out = new Response(res.body, res)
    out.headers.set('Strict-Transport-Security', 'max-age=31536000')
    if (url.pathname.startsWith('/billing/')) out.headers.set('Cache-Control', 'no-store')
    return out
  },
}
