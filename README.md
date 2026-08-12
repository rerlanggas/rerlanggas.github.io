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
    │   └── thumb/                  # Small .webp used by the portfolio grid
    └── tech/                       # 8 tech stack icons (SVG)
```

## Images

The portfolio grid and the lightbox load different files. The grid uses the small
`thumb/*.webp`; the full-size `*.webp` is fetched only when a screenshot is
opened. The `.jpg` files are kept as masters and are never served.

Regenerate after replacing a master (needs `brew install webp`):

```sh
for f in assets/screenshots/*.jpg; do
  b=$(basename "$f" .jpg)
  cwebp -q 78 -resize 1000 0 "$f" -o "assets/screenshots/thumb/$b.webp"   # grid
  cwebp -q 82            "$f" -o "assets/screenshots/$b.webp"             # lightbox
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
