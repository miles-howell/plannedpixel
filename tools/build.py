#!/usr/bin/env python3
"""Build the project pages from data/projects.json.

Writes:
  projects/<slug>.html   one page per project
  index.html             only the parts between <!-- BEGIN x --> / <!-- END x --> markers:
                         the featured cards, the workshop table and the project count

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


def card(project):
    """A featured project on the homepage."""
    return f"""<article class="card" data-updated="{esc(project['updated'])}">
<div class="card-head"><p class="card-kind">{esc(project['kind'])}</p><span class="new" hidden>NEW</span></div>
<h3 class="card-title"><a href="projects/{project['slug']}.html">{esc(project['title'])}</a></h3>
<p class="summary">{esc(project['summary'])}</p>
{tags(project)}
</article>"""


def row(project):
    """Every other project, as a row in the homepage's workshop table."""
    return (
        f'<tr data-updated="{esc(project["updated"])}">'
        f'<th scope="row"><a href="projects/{project["slug"]}.html">{esc(project["title"])}</a><span class="new" hidden>NEW</span></th>'
        f'<td>{esc(project["summary"])}</td>'
        f'<td class="year">{esc(project["year"])}</td></tr>'
    )


def topbar(root):
    return f"""<header class="container">
<div class="topbar">
<a class="brand" href="{root}index.html"><span class="brand-mark" aria-hidden="true"><i class="ink"></i><i class="ink"></i><i class="gold"></i><i class="ink"></i><i class="pink"></i><i class="ink"></i><i class="ink"></i><i></i><i></i></span>MILES HOWELL</a>
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

<main id="main" class="container" data-updated="{esc(project['updated'])}">
<p class="crumbs"><a href="{root}index.html">Home</a> / <a href="{root}index.html#workshop">Workshop</a> / {esc(title)}</p>
<div class="project-head">
<div class="card-head"><p class="project-kind">{esc(project['kind'])}</p><span class="new" hidden>NEW</span></div>
<h1 class="project-title">{esc(title)}</h1>
<p class="project-lede">{esc(project['summary'])}</p>
</div>
<div class="pixels" aria-hidden="true"><i style="background: #0b0d33"></i><i style="background: #2b2bb0"></i><i style="background: #7d7dff"></i><i style="background: #ff4fc8"></i><i style="background: #ffd400"></i><i style="background: #6fd94a"></i></div>
<div class="project-layout">
<div class="project-main">
<div class="project-body">
{body}
</div>
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


def main():
    projects = json.loads((ROOT / "data" / "projects.json").read_text(encoding="utf-8"))
    slugs = [p["slug"] for p in projects]
    if len(set(slugs)) != len(slugs):
        sys.exit("duplicate slugs in data/projects.json")
    for p in projects:
        if p["access"] not in ACCESS:
            sys.exit(f"{p['slug']}: unknown access {p['access']!r}")

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

    print(f"built {total} project pages and index.html")


if __name__ == "__main__":
    main()
