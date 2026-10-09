# plannedpixel.com

Miles Howell's corner of the web: a webring-style showcase of projects, styled like a late-90s homepage.

Every project has its own page, and each page is a stop on **the Planned Pixel Ring**. The prev/next links at the bottom walk through every project and back to the homepage.

The site is plain static HTML, CSS and a little JavaScript. There's no build step on deploy.

## Layout

| Path | What it is |
|---|---|
| `index.html` | Homepage, written by hand apart from the generated blocks between `<!-- BEGIN … -->` / `<!-- END … -->` markers |
| `projects/*.html` | One page per project, **generated**; don't edit by hand |
| `data/projects.json` | The project list. Its order is the ring order |
| `tools/build.py` | Generates the project pages, `js/ring.js` and the homepage's workshop cards and ring links |
| `css/style.css` | The Starfield Shrine theme |
| `js/site.js` | Extras: NEW! badges, the random ring stop, the per-browser visit counter |
| `img/button-88x31.png` | The 88×31 link-back button |
| `404.html` | "Lost in space" page |

## Adding or changing a project

1. Edit `data/projects.json`. Each entry needs `slug`, `title`, `kind`, `summary`, `tags`, `access` (`public`, `private`, `work` or `collab`), `year`, `updated` (YYYY-MM-DD), `links`, `body` (HTML paragraphs) and `highlights`.
2. Run `python3 tools/build.py` (standard library only).
3. Commit the data change together with the regenerated files.

A card shows a blinking **NEW!** badge while its `updated` date is less than 45 days old.

## Preview locally

```bash
python3 -m http.server 8000
```

Then open http://localhost:8000.
