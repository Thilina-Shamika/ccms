# CCMS — Home

Static site served with GitHub Pages.

- `index.html` — the page (exported design component)
- `assets/` — images
- `support.js`, `vendor/` — runtime that renders the page

## Local preview

```bash
python3 -m http.server 8000
```

Then open http://localhost:8000.

## Deploying

Pushed to `main`; GitHub Pages serves from the repository root
(Settings → Pages → Source: Deploy from a branch → `main` / `/ (root)`).
