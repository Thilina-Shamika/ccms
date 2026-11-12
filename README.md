# CCMS website

Static site served with GitHub Pages. Every page is generated, so edit the sources and rebuild rather than editing the `index.html` files directly.

## Layout

- `src/` holds the shared parts:
  - `styles.css`: all page styles
  - `logic.js`: page behaviour (light beam, menu, team plan tool, FAQ, booking form)
  - `cta-footer.html`: the booking section and footer
  - `home-hero.html`, `teamplan-card.html` and `sections/`: homepage content
  - `digital-section.html`: the Digital page content
- `tools/content.py` holds the copy for the RPO, service, industry, Why Sri Lanka and case study pages.
- `tools/build.py` assembles everything into `index.html` files, plus `sitemap.xml` and `robots.txt`.
- `assets/`, `support.js` and `vendor/` are the images and the runtime that renders the pages.

## Build

```bash
python3 tools/build.py
```

## Local preview

```bash
python3 -m http.server 8000
```

Then open http://localhost:8000.

## Deploying

Commit the rebuilt files and push to `main`. GitHub Pages serves from the repository root.

When the site moves to ccmsltd.com, change `BASE_URL` in `tools/content.py` and rebuild, so canonical links, structured data and the sitemap use the new domain.
