# Rian Erlangga Saputra — Personal Website

Personal portfolio website for Rian Erlangga Saputra, Senior iOS Developer based in Jakarta, Indonesia.

## Structure

```
.
├── index.html                      # Entire site — markup, CSS, and JS inline
├── og-image.jpg                    # Social sharing preview
├── sitemap.xml                     # SEO sitemap
├── robots.txt                      # Search engine instructions
├── google*.html                    # Google Search Console verification
└── assets/
    ├── photo.jpg                   # Profile photo
    ├── video/
    │   ├── dark_video.mp4          # Hero background loop (dark theme)
    │   └── light_video.mp4         # Hero background loop (light theme)
    ├── logos/                      # 8 app logos
    ├── screenshots/                # 8 app screenshots
    └── tech/                       # 8 tech stack icons (SVG)
```

## Hero video

The hero plays a full-bleed looping render behind the intro text. One `<video>`
element is reused and its `src` is swapped by `syncHeroVideo()` in `index.html`
whenever the theme changes, so only the matching file is ever downloaded.

If you replace a render, keep the two filenames and drop the new files into
`assets/video/` — no other change is needed.

## Local development

```sh
python3 -m http.server 8000
```

Then open <http://localhost:8000>. Serving over HTTP (rather than opening
`index.html` directly) matters — `file://` blocks the video from loading.

## Deploy

Push to the `main` branch of the `rerlanggas.github.io` repository; GitHub Pages
serves the root directly. Preserve the folder structure above.
