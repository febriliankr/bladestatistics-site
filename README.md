# bladestatistics.com

Static landing page for Blade, the agentic statistical analysis desktop app.
Served by GitHub Pages from `master`, custom domain in `CNAME`.

- `index.html` — the whole site, inline CSS and JS, no build step.
- `app.png`, `logo.png` — assets.
- Download links point at `dl.skalatec.com` (Cloudflare R2), same builds the
  workflows page at blade.skalatec.com serves.

Edit `index.html` and push; Pages redeploys on its own. When a new desktop
version ships, update the four `.dl a` hrefs, their sizes, and the version in
the download heading.
