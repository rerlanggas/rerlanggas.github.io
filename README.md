# Rian Erlangga Saputra — Personal Website

Personal portfolio website for Rian Erlangga Saputra, Senior iOS Developer based in Jakarta, Indonesia.

## Structure

```
.
├── index.html                      # Entire site — markup, CSS, and JS inline
├── 404.html                        # Not-found page (GitHub Pages serves automatically)
├── og-image.jpg                    # Social sharing preview
├── sitemap.xml                     # SEO sitemap
├── robots.txt                      # Search engine instructions
├── google*.html                    # Google Search Console verification
└── assets/
    ├── photo.jpg                   # Profile photo
    ├── video/
    │   ├── dark_video.mp4          # Hero background loop (dark theme)
    │   ├── light_video.mp4         # Hero background loop (light theme)
    │   ├── poster-dark.jpg         # First-paint still for the dark loop
    │   └── poster-light.jpg        # First-paint still for the light loop
    ├── photo.webp                  # Profile photo (served); photo.jpg is the master
    ├── logos/                      # 8 app logos
    ├── screenshots/                # 8 masters (.jpg) + full-size .webp for the lightbox
    │   └── thumb/                  # One sliced app screen per app, used by the cards
    └── tech/                       # 8 tech stack icons (SVG)
```

## Images

The `.jpg` files in `assets/screenshots/` are the original **App Store submission
sheets** — four portrait screens side by side on a light canvas. They are masters
and are never served.

Two derivatives are served:

- `screenshots/*.webp` — the whole sheet, loaded only when the lightbox opens
- `screenshots/thumb/*.webp` — **a single screen sliced out of the sheet**, shown
  on the portfolio card

The card thumbnail is a single screen on purpose. Scaling the whole four-up sheet
into a small box produced sliced-off phones, white gutter stripes, and the large
white bands some sheets carry at the bottom.

`tools/slice_screens.py` finds the panels (ffmpeg decodes, the analysis is plain
Python — no Pillow needed) and records which panel each app uses:

```sh
python3 tools/slice_screens.py detect      # list detected panels per sheet
python3 tools/slice_screens.py candidates  # write every panel to /tmp/panels to review
python3 tools/slice_screens.py build       # write the chosen thumbnails
```

After replacing a master, run `detect`, then `candidates`, **look at the panels**,
update the `CHOICE` map at the top of the script, and run `build`. Panels flagged
`CLIPPED` touch the canvas edge and are usually cut off in the master — though a
panel that legitimately starts at x=0 is flagged too, so confirm by eye.

The lightbox copies and the profile photo are plain conversions:

```sh
for f in assets/screenshots/*.jpg; do
  cwebp -q 82 "$f" -o "assets/screenshots/$(basename "$f" .jpg).webp"
done
cwebp -q 82 -resize 500 0 assets/photo.jpg -o assets/photo.webp
```

## Fonts

Deliberately no web font. The system stack (`-apple-system` → SF Pro on Apple
devices, Roboto on Android, Segoe UI on Windows) renders with zero network cost.
An earlier build loaded Inter from Google Fonts; it was a render-blocking request
and its swap-in reflowed the hero, which was responsible for a 0.747 CLS score.
Adding a web font back will reintroduce both problems unless it is self-hosted,
preloaded, and set to `font-display: optional`.

## Hero video

The hero plays a full-bleed looping render behind the intro text. One `<video>`
element is reused and its `src` is swapped by `syncHeroVideo()` in `index.html`
whenever the theme changes, so only the matching file is ever downloaded.

If you replace a render, keep the two filenames and drop the new files into
`assets/video/` — no other change is needed.

### Re-exporting a render

Source renders come out of the 3D tool at ~2.5 MB each with an audio track that
the site never plays. Run each new export through these two commands (requires
`ffmpeg`, install with `brew install ffmpeg`):

```sh
# 1. Strip audio, re-encode. +faststart lets playback begin before the
#    download finishes. Roughly halves the file with no visible loss.
ffmpeg -i SOURCE.mp4 -an -c:v libx264 -crf 26 -preset slow \
       -pix_fmt yuv420p -movflags +faststart assets/video/dark_video.mp4

# 2. Poster frame. Do NOT use frame 0 — both renders start on an empty
#    background and animate their elements in. Sample the settled composition:
#    ~5s for the dark render, ~9s for the light one.
ffmpeg -ss 5 -i SOURCE.mp4 -frames:v 1 -q:v 5 assets/video/poster-dark.jpg
```

WebM/VP9 versions were tried and deliberately dropped: for the dark render VP9
came out both larger and lower quality than x264 (the loop is mostly flat black,
which x264 compresses extremely well), so the extra files were not worth it.

## Local development

```sh
python3 -m http.server 8000
```

Then open <http://localhost:8000>. Serving over HTTP (rather than opening
`index.html` directly) matters — `file://` blocks the video from loading.

## Deploy

Push to the `main` branch of the `rerlanggas.github.io` repository; GitHub Pages
serves the root directly. Preserve the folder structure above.
