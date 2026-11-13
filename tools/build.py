#!/usr/bin/env python3
"""Build the project pages from data/projects.json.

Writes:
  projects/<slug>.html   one page per project, with the project's image at the top
  index.html             only the parts between <!-- BEGIN x --> / <!-- END x --> markers:
                         the featured cards, the workshop table and the project count
  sitemap.xml            the home page, every project page and the legal pages, with lastmod dates

Links to a project carry data-preview="<image>", which js/site.js shows as a hover preview.

Run it after editing data/projects.json:

    python3 tools/build.py

Standard library only. The output is plain static HTML, so nothing needs building on deploy.
"""
import html
import json
import re
import sys
from pathlib import Path
from urllib.parse import quote

ROOT = Path(__file__).resolve().parent.parent
SITE_URL = "https://plannedpixel.com"
GA_ID = "G-6P5LRT54KQ"
EMAIL = "miles@plannedpixel.com"

ACCESS = {
    "public": ("public", "access-public"),
    "private": ("private", "access-private"),
    "work": ("private · work", "access-private"),
    "collab": ("private · collab", "access-private"),
}

PRIVATE_NOTE = {
    "private": "This one lives in a private repo.",
    "work": "This was a private engagement, so the code isn't public.",
    "collab": "This is a private repo I share with my partners.",
}


def esc(text):
    return html.escape(text, quote=True)


def head(title, description, path, root):
    return f"""<!doctype html>
<html lang="en">
<head>
<!-- Google tag (gtag.js) -->
<script async src="https://www.googletagmanager.com/gtag/js?id={GA_ID}"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){{dataLayer.push(arguments);}}
  gtag('js', new Date());
  gtag('config', '{GA_ID}');
</script>

<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)}</title>
<meta name="description" content="{esc(description)}">
<meta name="theme-color" content="#f6f6fb">
<meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(description)}">
<meta property="og:type" content="website">
<meta property="og:url" content="{SITE_URL}/{path}">
<link rel="icon" href="{root}img/favicon.svg" type="image/svg+xml">
<link rel="icon" href="{root}img/favicon.ico" sizes="any">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&amp;family=Silkscreen:wght@400;700&amp;display=swap" rel="stylesheet">
<link rel="stylesheet" href="{root}css/style.css">
</head>"""


def tags(project):
    items = "".join(f'<li class="tag">{esc(t)}</li>' for t in project["tags"])
    return f'<ul class="tags" aria-label="Built with">{items}</ul>'


def preview(project):
    """The data-preview attribute js/site.js turns into a hover preview, for links on the homepage."""
    return f' data-preview="{esc(project["image"])}"'


def card(project):
    """A featured project on the homepage."""
    return f"""<article class="card">
<div class="card-head"><p class="card-kind">{esc(project['kind'])}</p></div>
<h3 class="card-title"><a href="projects/{project['slug']}.html"{preview(project)}>{esc(project['title'])}</a></h3>
<p class="summary">{esc(project['summary'])}</p>
{tags(project)}
</article>"""


def row(project):
    """Every other project, as a row in the homepage's workshop table."""
    return (
        f'<tr>'
        f'<th scope="row"><a href="projects/{project["slug"]}.html"{preview(project)}>{esc(project["title"])}</a></th>'
        f'<td>{esc(project["summary"])}</td>'
        f'<td class="year">{esc(project["year"])}</td></tr>'
    )


def topbar(root):
    return f"""<header class="container">
<div class="topbar">
<div class="brand-group"><a class="brand" href="{root}index.html"><span class="brand-mark" aria-hidden="true"><i class="ink"></i><i class="ink"></i><i class="gold"></i><i class="ink"></i><i class="pink"></i><i class="ink"></i><i class="ink"></i><i></i><i></i></span>MILES HOWELL</a><span class="social"><a target="_blank" rel="noopener noreferrer" href="https://github.com/miles-howell" aria-label="Miles on GitHub"><svg viewBox="0 0 24 24" width="22" height="22" aria-hidden="true" fill="currentColor"><path d="M12 .5a11.5 11.5 0 0 0-3.64 22.41c.58.1.79-.25.79-.56v-2c-3.2.7-3.88-1.37-3.88-1.37-.52-1.33-1.28-1.69-1.28-1.69-1.04-.71.08-.7.08-.7 1.16.08 1.77 1.19 1.77 1.19 1.03 1.76 2.7 1.25 3.36.96.1-.75.4-1.25.73-1.54-2.55-.29-5.24-1.28-5.24-5.69 0-1.26.45-2.28 1.19-3.09-.12-.29-.52-1.46.11-3.05 0 0 .97-.31 3.17 1.18a11 11 0 0 1 5.78 0c2.2-1.49 3.17-1.18 3.17-1.18.63 1.59.23 2.76.11 3.05.74.81 1.19 1.83 1.19 3.09 0 4.42-2.69 5.39-5.25 5.68.41.36.78 1.06.78 2.14v3.17c0 .31.21.67.8.56A11.5 11.5 0 0 0 12 .5z"/></svg></a><a target="_blank" rel="noopener noreferrer" href="https://www.linkedin.com/in/miles-howell-pxl" aria-label="Miles on LinkedIn"><svg viewBox="0 0 24 24" width="22" height="22" aria-hidden="true" fill="currentColor"><path d="M20.45 20.45h-3.56v-5.57c0-1.33-.03-3.04-1.85-3.04-1.86 0-2.14 1.45-2.14 2.94v5.67H9.34V9h3.41v1.56h.05c.48-.9 1.64-1.85 3.37-1.85 3.6 0 4.27 2.37 4.27 5.46v6.28zM5.34 7.43a2.06 2.06 0 1 1 0-4.13 2.06 2.06 0 0 1 0 4.13zM7.12 20.45H3.56V9h3.56v11.45zM22.22 0H1.77C.79 0 0 .77 0 1.73v20.54C0 23.23.79 24 1.77 24h20.45c.98 0 1.78-.77 1.78-1.73V1.73C24 .77 23.2 0 22.22 0z"/></svg></a></span></div>
<nav class="site-nav" aria-label="Site">
<a href="{root}index.html#work">Work</a>
<a href="{root}index.html#workshop">Projects</a>
<a href="{root}index.html#about">About</a>
<a href="mailto:{EMAIL}">Contact</a>
</nav>
</div>
</header>"""


def project_page(project):
    root = "../"
    slug = project["slug"]
    title = project["title"]
    label, cls = ACCESS[project["access"]]
    body = "\n".join(f"<p>{para}</p>" for para in project["body"])

    highlights = ""
    if project["highlights"]:
        items = "\n".join(f"<li>{h}</li>" for h in project["highlights"])
        highlights = f'<h2 class="h2">Highlights</h2>\n<ul class="highlights">\n{items}\n</ul>'

    table = ""
    if project.get("table"):
        t = project["table"]
        header = "".join(f'<th scope="col">{c}</th>' for c in t["columns"])
        rows = "\n".join(
            f'<tr><th scope="row">{r[0]}</th>' + "".join(f"<td>{c}</td>" for c in r[1:]) + "</tr>"
            for r in t["rows"]
        )
        note = f'\n<p class="data-note">{t["note"]}</p>' if t.get("note") else ""
        table = (
            f'\n<h2 class="h2">{esc(t["title"])}</h2>\n'
            f'<div class="data-table">\n<table>\n<thead><tr>{header}</tr></thead>\n<tbody>\n{rows}\n</tbody>\n</table>\n</div>{note}'
        )

    caption = ""
    if project.get("image_caption"):
        caption = f'\n<figcaption>{esc(project["image_caption"])}</figcaption>'
    figure = (
        f'<figure class="project-shot">\n'
        f'<img src="{root}{esc(project["image"])}" alt="{esc(project["image_alt"])}" width="1600" height="1000">'
        f"{caption}\n</figure>"
    )

    if project["links"]:
        buttons = "\n".join(
            f'<a class="btn" href="{esc(link["url"])}" target="_blank" rel="noopener noreferrer">{esc(link["label"])} →</a>'
            for link in project["links"]
        )
        links = f'<div class="project-links">\n{buttons}\n</div>'
    else:
        subject = quote(f"About {title}")
        links = (
            f'<p class="private-note">{PRIVATE_NOTE[project["access"]]} '
            f'<a href="mailto:{EMAIL}?subject={subject}">Ask me about it</a>.</p>'
        )

    return f"""{head(f"{title} · Miles Howell · Planned Pixel", project["summary"], f"projects/{slug}.html", root)}
<body data-root="{root}">
<a class="skip" href="#main">Skip to content</a>
{topbar(root)}

<main id="main" class="container">
<p class="crumbs"><a href="{root}index.html">Home</a> / <a href="{root}index.html#workshop">Workshop</a> / {esc(title)}</p>
<div class="project-head">
<div class="card-head"><p class="project-kind">{esc(project['kind'])}</p></div>
<h1 class="project-title">{esc(title)}</h1>
<p class="project-lede">{esc(project['summary'])}</p>
</div>
<div class="pixels" aria-hidden="true"><i style="background: #0b0d33"></i><i style="background: #2b2bb0"></i><i style="background: #7d7dff"></i><i style="background: #ff4fc8"></i><i style="background: #ffd400"></i><i style="background: #6fd94a"></i></div>
<div class="project-layout">
<div class="project-main">
{figure}
<div class="project-body">
{body}
</div>{table}
{highlights}
{links}
</div>
<dl class="facts">
<div><dt>Access</dt><dd class="{cls}">{esc(label)}</dd></div>
<div><dt>Year</dt><dd>{esc(project['year'])}</dd></div>
<div><dt>Built with</dt><dd>{esc(", ".join(project['tags']))}</dd></div>
</dl>
</div>

</main>

<footer class="container site-foot">
<div class="foot-line">
<span>© 2026 Miles Howell · best viewed in any browser</span>
<a href="mailto:{EMAIL}">{EMAIL}</a>
<span class="foot-links"><a href="{root}privacy.html">Privacy</a> <a href="{root}terms.html">Terms</a></span>
<a target="_blank" rel="noopener noreferrer" href="https://github.com/sponsors/miles-howell">♥ Sponsor</a>
</div>
</footer>
<script src="{root}js/site.js"></script>
</body>
</html>
"""


def replace_between(text, name, content):
    pattern = re.compile(rf"(<!-- BEGIN {name} -->)(.*?)(<!-- END {name} -->)", re.S)
    if not pattern.search(text):
        sys.exit(f"index.html is missing the <!-- BEGIN {name} --> / <!-- END {name} --> markers")
    return pattern.sub(lambda m: f"{m.group(1)}{content}{m.group(3)}", text)


def legal_date(name):
    """The date in a legal page's <time datetime="..."> element."""
    text = (ROOT / name).read_text(encoding="utf-8")
    match = re.search(r'<p class="legal-date">.*?<time datetime="(\d{4}-\d{2}-\d{2})"', text, re.S)
    if not match:
        sys.exit(f"{name}: couldn't find its Last updated date")
    return match.group(1)


def sitemap(projects):
    """sitemap.xml: home, project pages and legal pages. 404.html is left out on purpose."""
    pages = [("", max(p["updated"] for p in projects))]
    pages += [(f"projects/{p['slug']}.html", p["updated"]) for p in projects]
    pages += [(name, legal_date(name)) for name in ("privacy.html", "terms.html")]
    urls = "\n".join(
        f"  <url><loc>{SITE_URL}/{path}</loc><lastmod>{date}</lastmod></url>" for path, date in pages
    )
    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        f"{urls}\n"
        "</urlset>\n"
    )


def main():
    projects = json.loads((ROOT / "data" / "projects.json").read_text(encoding="utf-8"))
    slugs = [p["slug"] for p in projects]
    if len(set(slugs)) != len(slugs):
        sys.exit("duplicate slugs in data/projects.json")
    for p in projects:
        if p["access"] not in ACCESS:
            sys.exit(f"{p['slug']}: unknown access {p['access']!r}")
        if not p.get("image") or not p.get("image_alt"):
            sys.exit(f"{p['slug']}: needs an image and image_alt")
        if not (ROOT / p["image"]).is_file():
            sys.exit(f"{p['slug']}: image {p['image']} not found")

    total = len(projects)
    out_dir = ROOT / "projects"
    out_dir.mkdir(exist_ok=True)
    for project in projects:
        page = project_page(project)
        (out_dir / f"{project['slug']}.html").write_text(page, encoding="utf-8")

    for stale in out_dir.glob("*.html"):
        if stale.stem not in slugs:
            stale.unlink()
            print(f"removed stale page {stale.name}")

    index_path = ROOT / "index.html"
    index = index_path.read_text(encoding="utf-8")
    featured = [p for p in projects if p.get("featured")]
    rest = [p for p in projects if not p.get("featured")]
    cards = "\n\n".join(card(p) for p in featured)
    rows = "\n".join(row(p) for p in rest)
    index = replace_between(index, "featured", f"\n{cards}\n")
    index = replace_between(index, "workshop", f"\n{rows}\n")
    index = replace_between(index, "count", str(total))
    index_path.write_text(index, encoding="utf-8")

    (ROOT / "sitemap.xml").write_text(sitemap(projects), encoding="utf-8")

    print(f"built {total} project pages, index.html and sitemap.xml")


if __name__ == "__main__":
    main()
