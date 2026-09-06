# bladestatistics.com

Static landing page for Blade, the agentic statistical analysis desktop app.
Served by GitHub Pages from `master`, custom domain in `CNAME`.

## Layout

- `src/shell.html`: the page template, with `{{placeholders}}`.
- `src/_css.html`: the `<style>` block, shared by every locale.
- `content/<code>.json`: all the text for one language.
- `build.py`: renders every locale, plus `sitemap.xml` and `robots.txt`.
- `index.html` and `<code>/index.html`: generated output, committed so Pages
  needs no CI.
- `app.png`, `logo.png`: assets, referenced with absolute paths so the
  subdirectory builds find them.

## Editing

Change `content/*.json` or `src/*`, then run the build and commit both the
source and the generated pages:

```
python3 build.py
```

Never hand-edit `index.html` or a `<code>/index.html`. The next build overwrites
it.

## Languages

English is the root; the twelve translations live in two-letter directories.
`ORDER` in `build.py` controls the switcher menu and the `hreflang` tags. Adding
a language means dropping in a content file and adding its code to that list.
Arabic sets `"dir": "rtl"` and the stylesheet uses logical properties, so the
layout mirrors on its own.

Every page carries a small script in `<head>` that runs before the first paint.
A visitor whose browser prefers another available language is sent there once
per session. Choosing from the switcher in the top bar stores the pick in
`localStorage`, and a stored pick outranks the browser preference from then on.

## Theme

The palette follows the device through `prefers-color-scheme`. Both themes are
defined as custom properties on `:root`, with the light values in one media
query. Brand orange is too weak for small text on white, so `--brand-ink` and
`--brand-btn` carry darker values in light mode.

## Releases

Download links point at `dl.skalatec.com` (Cloudflare R2), the same builds the
workflows page at blade.skalatec.com serves. A new desktop version means editing
the four `.dl a` hrefs and sizes in `src/shell.html`, then the version in each
`content/*.json` under `get.h2`.
