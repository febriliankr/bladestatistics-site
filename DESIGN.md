# Landing page artwork

The statistics homepage takes inspiration from [Duna](https://duna.com/): a painterly landscape, generous typography and spacing, rounded controls, and restrained motion. All new landscape artwork is original, created with the built-in GPT Image tool. No reference-site assets are used. The existing Blade logo, application screenshot, and translated statistics content are retained.

Generated asset files:

- `assets/night-sky.webp` — 1536 × 1024, desktop, 162,590 bytes.
- `assets/night-sky-mobile.webp` — 900 × 600, mobile, 46,604 bytes.

Both are WebP encodings of the same generated artwork. The mobile image uses a right-aligned focal point to keep the crescent visible. Responsive preload media queries avoid downloading both variants.

## Final generation prompt

> Use case: stylized-concept. Asset type: original full-width website hero background for Blade, a desktop work and analysis agent. Create a beautifully art-directed, painterly panoramic night landscape, wide 3:2 landscape composition designed to be cropped to a 16:9 banner. Deep midnight indigo sky with scattered tiny ivory stars, a small luminous crescent moon in the upper right, softly brushed wisps of blue-gray clouds. Rolling distant mountains and a still winding lake reflecting muted silver moonlight, dark pine silhouettes framing the far edges, subtle wild grasses in the foreground. The lower third has inky navy shadows that can fade seamlessly into a #090f1c web background. The central sky and center foreground should be calm low-detail negative space for white website typography overlaid later. Atmospheric hand-painted gouache and colored-pencil texture, restrained soft grain, sophisticated editorial illustration, natural landscape, quiet wonder and warmth. Palette: ink blue, slate indigo, silver, tiny muted warm cream highlights. The mountain horizon stays near the lower third. No lettering, no text, no logos, no buildings, no people, no interface, no watermark. Generate an original image, not a copy of any existing website.

## Motion

The hero fades in with a gentle background settle and slowly twinkling stars. Existing scroll reveals, method-chip hovers, and FAQ transitions remain. All motion respects `prefers-reduced-motion`; the full content stays visible without JavaScript.

## Build and deploy

Edit `src/shell.html` and `assets/landing.css`, then run `python3 build.py`. Commit the source, generated pages, and assets and push `master` to publish through GitHub Pages at https://bladestatistics.com/.
