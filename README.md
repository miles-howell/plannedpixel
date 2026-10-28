# plannedpixel.com

Miles Howell's corner of the web: a showcase of projects, with a clean light theme and late-90s touches: pixel fonts and 88×31 buttons.

The site is plain static HTML, CSS and a little JavaScript. There's no build step on deploy.

## Layout

| Path | What it is |
|---|---|
| `index.html` | Homepage, written by hand apart from the generated blocks between `<!-- BEGIN … -->` / `<!-- END … -->` markers |
| `projects/*.html` | One page per project, **generated**; don't edit by hand |
| `data/projects.json` | The project list |
| `tools/build.py` | Generates the project pages and the homepage's featured cards, workshop table and project count |
| `css/style.css` | The Daylight Pixel theme |
| `js/site.js` | Extras: NEW badges and project image previews on hover |
| `img/projects/` | One 16:10 image per project (1600×1000 WebP, or SVG) |
| `img/button-88x31.png` | The 88×31 link-back button |
| `404.html` | "Lost in space" page |

## Adding or changing a project

1. Edit `data/projects.json`. Each entry needs `slug`, `title`, `kind`, `summary`, `tags`, `access` (`public`, `private`, `work` or `collab`), `year`, `updated` (YYYY-MM-DD), `links`, `body` (HTML paragraphs), `highlights`, `image` (a path under `img/projects/`) and `image_alt`. `image_caption` is optional. Add `"featured": true` to show a project as a card on the homepage; the rest go in the workshop table.
2. Run `python3 tools/build.py` (standard library only).
3. Commit the data change together with the regenerated files.

A project shows a **NEW** badge while its `updated` date is less than 45 days old.

The image sits at the top of the project page, and shows as a preview when you hover or focus a link to the project on the homepage. Links the build generates get the preview automatically; a hand-written link gets one with `data-preview="img/projects/<file>"`. Keep images 16:10 so the preview and the page don't jump.

## Preview locally

```bash
python3 -m http.server 8000
```

Then open http://localhost:8000.
