# Landing page design

The shorter statistics homepage follows the section layouts of [Duna](https://duna.com/). It uses a landscape hero, one interactive product preview, a compact workspace preview, a compact leadership section, and an image-based download footer.

All new artwork was created with the built-in GPT Image tool. No Duna images or source code were copied. The app panels are labelled as illustrative previews.

## Generated assets

| Use              | Workspace paths                                                     |
| ---------------- | ------------------------------------------------------------------- |
| Hero             | `assets/daylight-lake.webp`, `assets/daylight-lake-mobile.webp`     |
| Archived middle section | `assets/analysis-clouds.webp`, `assets/analysis-clouds-mobile.webp` |
| Footer           | `assets/footer-garden.webp`, `assets/footer-garden-mobile.webp`     |
| Data preview     | `assets/preview-ask.webp`                                           |
| Results preview  | `assets/preview-results.webp`                                       |
| Workspace preview | `assets/preview-workspace.webp` |
| R script preview | `assets/preview-script.webp`                                        |

The middle and footer originals are 1536 × 1024. Their mobile versions are 900 × 600. The previews are optimized to 1100 × 1100.

## Final prompts

### clouds

> Use case: stylized-concept. Asset type: original full-width illustrated website section background for Blade Statistics. Create a wide 3:2 panoramic hand-painted gouache sky, like an illustration on textured watercolor paper. A large calm opening of muted dusty teal-blue sky occupies the central 60 percent. Soft ivory and warm pale-cream cumulus clouds frame the far left and right and gently curve along the lower corners. Subtle sunlit edges and pencil texture, airy open space, refined restrained color, natural clouds. The center should be an even medium muted blue, sufficiently dark for white website text to be overlaid later. Keep cloud highlights near the edges. Do not include a sun disk, moon, stars, objects, symbols, sparkles, gradients as a graphic effect, interface, lettering, logos, or watermark. This is original natural landscape artwork, no copies of any existing site's composition.

### footer

> Use case: stylized-concept. Asset type: original image-based website footer background, wide 3:2 landscape for Blade Statistics. A serene hand-painted gouache lakeside garden in warm late-afternoon light, consistent with a delicate pastel mountain-and-lake illustration. Silver-sage willow branches frame the upper left and right edges, low meadows and distant muted blue hills surround a broad pale still lake. Small warm cream wildflowers at the extreme bottom edges. The broad center must remain very bright warm ivory and pale silver with minimal detail so dark typography and download buttons can be overlaid later. Landscape details stay toward the lower third and lateral edges. Subtle paper grain, colored-pencil details, soft natural painterly edges. Palette: sage green, soft butter yellow, powder blue, warm ivory, pale terracotta accents. Gentle inviting daylight, no dark shadows. No text, no letters, no logos, no UI, no people, no sparkle symbols, no watermark. Original composition.

### ask

> Use case: ui-mockup. Asset type: standalone product preview illustration for a statistics desktop app. Square composition 1:1 on solid warm gray-green #eceee7 background. A single flat, front-facing white desktop application panel centered with ample empty margin, subtle 12px rounded corners, very fine pale-gray border and tiny natural shadow. No overlapping panels, no 3D perspective, no glass effect. Panel title 'Blade'. A small orange rounded-square app mark in the upper left. The main content shows a file row 'study.csv', then a very clean compact data table with just three columns 'group', 'baseline', 'score' and six numeric sample rows. Below the table, a single simple prompt input reading 'Compare the two groups.' with a tiny send arrow. Typography is crisp small dark charcoal sans-serif. Muted sage and orange accents only, off-white surfaces. This is a polished illustrative app preview, not a website mockup. Render exact simple text, no other labels, no outer browser, no neon, no gradients, no sparkles, no decorative objects, no watermark.

### results

> Use case: ui-mockup. Asset type: standalone product preview illustration for a statistics desktop app. Square composition 1:1 on solid warm gray-green #eceee7 background. A single flat front-facing white report panel centered with ample empty margin, subtle 12px rounded corners, very fine pale-gray border and tiny natural shadow. No overlapping panels, no 3D perspective, no glass effect. Small top bar title 'Blade', small orange rounded-square app mark at left. Main heading 'Group comparison'. A beautifully restrained report chart with two groups of sage green and muted terracotta dots with horizontal mean lines, labeled only 'Control' and 'Treatment', delicate axes, generous white space. Below, a narrow pale sage confirmation row 'Assumptions checked', and a small file row 'results.csv'. The chart uses illustrative sample data, not a claim about real treatment. Crisp charcoal sans-serif text. Muted sage and orange accents only, off-white surfaces. This is a polished illustrative app preview, not a full website. No other labels, no browser frame, no neon, no gradients, no sparkles, no decorative objects, no watermark.

### script

> Use case: ui-mockup. Asset type: standalone product preview illustration for a statistics desktop app. Square composition 1:1 on solid warm gray-green #eceee7 background. A single flat front-facing white code editor panel centered with ample empty margin, subtle 12px rounded corners, very fine pale-gray border and tiny natural shadow. No overlapping panels, no 3D perspective, no glass effect. Small top bar title 'Blade', small orange rounded-square app mark at left. Editor tab reads 'analysis.R'. Render just three readable R code lines in a restrained monospace font: 'study <- read.csv("study.csv")', 'fit <- lm(score ~ group, data = study)', 'summary(fit)'. Small muted line numbers. Sage green syntax accents and muted terracotta string accents on warm white. Beneath the editor, a clean compact file row with a simple document icon, label 'analysis.R', and a small green check mark. Keep the composition very minimal and legible. This is a polished illustrative app preview, not a website. No other labels, no browser frame, no neon, no gradients, no sparkles, no decorative objects, no watermark.

### workspace

> Use case: ui-mockup.
Asset type: compact landscape thumbnail for the workspace management section of Blade Statistics.
Create a beautiful restrained front-facing desktop app preview on a solid warm pale stone background #f2eee6. A single wide white application window, delicate border, softly rounded corners and extremely subtle natural shadow, centered with generous margins. Flat 2D, crisp dark charcoal sans-serif typography. Narrow warm-white sidebar on the left, main workspace file list on the right.
Text verbatim: small app title "Blade"; sidebar heading "Workspaces"; two simple folder rows "Study A" (selected with pale sage highlight) and "Study B"; main title "Study A"; three spacious file rows "study.csv", "analysis.R", "results.csv", each with a small understated file icon. No other words or data. Tiny warm orange square app mark. Fine neutral dividers, small sage accents. Clear hierarchy and ample white space. Aspect ratio 3:2 landscape. Keep every label legible, no tiny dense details. No floating or overlapping cards, no browser frame, no gradients, no glow, no sparkles, no perspective, no 3D, no people, no decorative objects, no watermarks. This is an original illustrative product thumbnail, matching a quiet natural landscape website.

The workspace preview is optimized to 1200 × 800 and labelled as illustrative.

## Implementation

Native disclosure controls select the three app previews. Text remains accessible in HTML. The generated previews use sample data and are not screenshots of a real analysis.

Downloads retain OS detection, four architecture choices, keyboard navigation, and conversion tracking. The hero clips only its artwork so the menu remains visible over later sections.

All thirteen locales use short translated copy. The full content remains available without JavaScript, and motion follows the reduced-motion setting.

## Build and deployment

Run `python3 build.py`, commit the source and generated pages, then push `master`. GitHub Pages serves https://bladestatistics.com/.

## Leadership section

The two cards use the names and titles supplied by the site owner: Febrilian, CEO of Skala, and Elvan Wiyarta, CEO of Risetku. Their sample quotes are visibly labelled as placeholders in every locale. They are not presented as verified testimonials. The cloud section was removed from the homepage; its generated artwork is retained in the repository.

The profile photos were downloaded from the owner-supplied Instagram profiles on October 18, 2026: [Febrilian](https://www.instagram.com/febrilian/) and [Elvan Wiyarta](https://www.instagram.com/elvanwiyarta/). The original JPEGs are stored at `assets/febrilian-profile.jpg` and `assets/elvan-wiyarta-profile.jpg`. They are displayed as 64-pixel circular portraits and are not AI-generated.

## Moonlit theme

Generated with the built-in imagegen tool from `assets/daylight-lake.webp`.
The optimized outputs are `assets/moonlit-lake.webp` (1536 × 1024) and
`assets/moonlit-lake-mobile.webp` (900 × 600). The same artwork is used by
Blade Desktop as `login-landscape-dark.webp` and
`login-landscape-dark-mobile.webp`.

Final prompt:

> Use case: lighting-weather. Edit target: the supplied painterly alpine lake background for the Blade landing page and desktop app. Create its dark nighttime counterpart, preserving the exact landscape composition, lake shore geometry, mountain silhouettes, foreground flowers and rocks, soft hand-painted watercolor texture, and wide 3:2 framing. Change only the time of day and illumination: deep midnight indigo sky with subtle scattered stars and soft moonlit clouds, blue-silver highlights on distant peaks and still lake reflections, muted blue-green shore vegetation. Overall dark, calm, elegant and legible behind white UI text. The lower quarter should softly dissolve into a solid near-black navy #10141c, matching how the daylight version fades into cream. No text, no logos, no UI, no large new objects; preserve the scenery. Output landscape 1536x1024.

The landing page follows the device color scheme, supports a remembered
light/dark toggle, and follows later device-theme changes until a visitor
makes an explicit choice. Without JavaScript it follows the device theme.

### Softer moonlit revision

The active dark artwork is `assets/moonlit-lake-soft.webp` and
`assets/moonlit-lake-soft-mobile.webp`. Desktop uses the same optimized images
as `login-landscape-dark-soft.webp` and `login-landscape-dark-soft-mobile.webp`.
Generated with the built-in imagegen tool, using the original moonlit image as
the edit target. Final prompt:

> Use case: style-transfer. Edit target: supplied moonlit lake artwork used behind UI text. Make this same nighttime landscape substantially softer and quieter, with much subtler detail. Preserve the exact composition, moon position and scale, mountain and shoreline geometry, 1536x1024 framing and dark navy bottom fade. Use broad, delicate watercolor washes with misty atmospheric edges, lower local contrast, muted desaturated slate-blue tones. Simplify mountain textures, trees, foreground flowers, rocks, water ripples and cloud edges into gentle suggested shapes. Stars should be very sparse and faint. Give the moon a diffused, subdued glow with minimal visible surface detail; its reflection should be soft and restrained. Retain enough shape to read as a lake and mountains at night. Calm, airy painterly softness, not a digital blur or fog filter; no crisp microtexture, no dramatic highlights, no text, no UI. Bottom quarter fades to near-black navy #10141c.
