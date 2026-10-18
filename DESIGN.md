# Landing page artwork

The statistics homepage takes inspiration from [Duna](https://duna.com/): a luminous painterly landscape, charcoal typography, rounded controls, and a soft fade into a warm light page. The current landscape is original artwork created with the built-in GPT Image tool. The Blade logo, app screenshot, and all translated statistics content are retained.

Current generated assets:

- `assets/daylight-lake.webp` — desktop, 1536 × 1024.
- `assets/daylight-lake-mobile.webp` — mobile, 900 × 600.

The two WebP files are optimized encodings of the same original image. Responsive preload media queries select the appropriate asset. The former night-sky artwork remains available in the asset history.

## Final generation prompt

> Use case: stylized-concept. Asset type: original light website hero background for Blade Statistics, panoramic editorial landscape, 3:2 landscape image that will be displayed across a wide desktop banner. Primary request: a luminous hand-painted spring landscape in warm morning light, sophisticated soft gouache and colored-pencil illustration with subtle paper grain. Scene: a tranquil winding lake in a rolling meadow, low distant rounded mountains, soft butter-yellow and pale apricot clouds in a very light powder-blue and warm ivory sky, muted sage grasses and tiny cream wildflowers near the far left and right edges, delicate lavender and blue-gray mountains reflected in pale peach and silver water. Composition: expansive airy panorama, mountain horizon near the upper middle, small natural details toward the lateral edges, broad very pale reflective water through the lower center, the bottom quarter dissolving gently into near-white warm ivory #f8f7f3 paper. The central and lower middle need quiet bright low-detail negative space for large charcoal website typography that will be added in code. Mood: calm, open, sunlit, optimistic, refined. Restrained pastel palette, no dark shadows, no neon, no oversaturated colors, no night sky, no moon, no stars. This is standalone artwork, no website interface or graphic elements. No lettering, no text, no logos, no buildings, no people, no watermark. Create a unique composition, not a copy of any existing website.

## Motion

A gentle one-time background settle, staggered hero text entrances, scroll reveals, method-chip hovers, and FAQ transitions. All motion respects `prefers-reduced-motion`; content stays visible without JavaScript.

## Build and deploy

Edit `src/shell.html` and `assets/landing.css`, then run `python3 build.py`. Commit the source, generated pages, and assets and push `master` to publish through GitHub Pages at https://bladestatistics.com/. Stylesheet URLs include a content hash so visual changes reach returning visitors.
