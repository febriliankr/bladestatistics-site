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

## Page structure

The homepage has a hero, an interactive app preview, a compact workspace section, an illustrated R section, and a download footer. All thirteen languages use this structure. Short page copy lives under `simple` in each content file.

`assets/landing.css` styles the homepage. Pricing and legal pages retain `src/_css.html`. The build adds a hash of the homepage CSS and JavaScript to both asset URLs.

## Artwork and previews

The landscapes and four app previews were generated with GPT Image. The previews are labelled as illustrations. `DESIGN.md` contains the prompts and asset paths.

## Motion and interaction

The preview uses native disclosure controls. `assets/landing.js` changes the image when a step opens. Without JavaScript, all three preview images are shown.

Hero entrances and section reveals respect reduced motion. The download dropdown can cross the hero boundary and remains above the following section.

## Releases

Download links point at `dl.skalatec.com` (Cloudflare R2), the same builds the
workflows page at blade.skalatec.com serves. A new desktop version means editing
the four `.dl a` hrefs and sizes in `src/shell.html`, then the version in each
`content/*.json` under `get.h2`.
