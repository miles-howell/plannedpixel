#!/usr/bin/env python3
"""Build the Planned Pixel Ring from data/projects.json.

Writes:
  projects/<slug>.html   one page per project, each a stop on the ring
  js/ring.js             the ring order, used by the "random" button
  index.html             only the parts between <!-- BEGIN x --> / <!-- END x --> markers:
                         the workshop cards, the project count and the ring links

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
<meta name="theme-color" content="#04051a">
<meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(description)}">
<meta property="og:type" content="website">
<meta property="og:url" content="{SITE_URL}/{path}">
<link rel="icon" href="{root}img/favicon.svg" type="image/svg+xml">
<link rel="icon" href="{root}img/favicon.ico" sizes="any">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Silkscreen:wght@400;700&amp;display=swap" rel="stylesheet">
<link rel="stylesheet" href="{root}css/style.css">
</head>"""


def tags(project):
    items = "".join(f'<li class="tag">{esc(t)}</li>' for t in project["tags"])
    return f'<ul class="tags" aria-label="Built with">{items}</ul>'


def access(project):
    label, cls = ACCESS[project["access"]]
    return f'<span class="{cls}">[{esc(label)}]</span>'


def card(project):
    return f"""<article class="card" data-updated="{esc(project['updated'])}">
<div class="card-head"><h3 class="card-title"><a href="projects/{project['slug']}.html">{esc(project['title'])}</a></h3><span class="new" hidden>NEW!</span></div>
<p>{esc(project['summary'])}</p>
{tags(project)}
<div class="meta">{access(project)}<span>{esc(project['year'])}</span></div>
</article>"""


def ring_link(target, root, rel):
    """A prev/next button. target=None means the homepage."""
    if target is None:
        href, label = f"{root}index.html", "home"
    else:
        href, label = f"{root}projects/{target['slug']}.html", target["title"]
    text = f"« {esc(label)}" if rel == "prev" else f"{esc(label)} »"
    return f'<a class="ring-btn" href="{href}" rel="{rel}">{text}</a>'


def ring_nav(prev, nxt, root):
    return f"""<nav class="ring-nav" aria-label="Webring">
{ring_link(prev, root, "prev")}
<a class="ring-btn" href="{root}index.html#workshop" data-ring-random>random</a>
<a class="ring-btn" href="{root}index.html#workshop">list all</a>
{ring_link(nxt, root, "next")}
</nav>"""


def ring_footer_text(root):
    return (
        '<p class="ring-foot">a ring of one person\'s projects: every project is a stop · '
        f'<a href="mailto:{EMAIL}?subject=Guestbook">sign my guestbook</a> · '
        "© 2026 Miles Howell · best viewed in any browser</p>"
    )


def project_page(project, number, total, prev, nxt):
    root = "../"
    slug = project["slug"]
    title = project["title"]
    label, cls = ACCESS[project["access"]]
    body = "\n".join(f"<p>{para}</p>" for para in project["body"])

    highlights = ""
    if project["highlights"]:
        items = "\n".join(f"<li>{h}</li>" for h in project["highlights"])
        highlights = f'<h2 class="h2">~ highlights ~</h2>\n<ul class="highlights">\n{items}\n</ul>'

    if project["links"]:
        buttons = "\n".join(
            f'<a class="ring-btn" href="{esc(link["url"])}" target="_blank" rel="noopener noreferrer">{esc(link["label"])} »</a>'
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
<body data-ring="{slug}" data-root="{root}">
<a class="skip" href="#main">Skip to content</a>
<div class="wrap">

<header class="panel site-head compact">
<div class="kicker">~*~ stop {number} of {total} on the planned pixel ring ~*~</div>
<p class="site-title"><a href="{root}index.html">MILES HOWELL</a></p>
</header>

<main id="main" class="panel panel-pad" data-updated="{esc(project['updated'])}">
<p class="crumbs"><a href="{root}index.html">home</a> » <a href="{root}index.html#workshop">the workshop</a> » {esc(title)}</p>
<div class="card-head" style="margin-top: 18px"><p class="project-kind">{esc(project['kind'])}</p><span class="new" hidden>NEW!</span></div>
<h1 class="project-title">{esc(title)}</h1>
<p class="project-lede">{esc(project['summary'])}</p>
<dl class="facts">
<div><dt>access:</dt><dd class="{cls}">{esc(label)}</dd></div>
<div><dt>year:</dt><dd>{esc(project['year'])}</dd></div>
<div><dt>built with:</dt><dd>{esc(", ".join(project['tags']))}</dd></div>
</dl>
<div class="project-body">
{body}
</div>
{highlights}
{links}
</main>

<footer class="panel ring" id="ring">
<p class="small" style="margin: 0">you are at stop {number} of {total} on</p>
<h2 class="ring-title">✦ THE PLANNED PIXEL RING ✦</h2>
{ring_nav(prev, nxt, root)}
{ring_footer_text(root)}
</footer>

</div>
<script src="{root}js/ring.js"></script>
<script src="{root}js/site.js"></script>
</body>
</html>
"""


def replace_between(text, name, content):
    pattern = re.compile(rf"(<!-- BEGIN {name} -->)(.*?)(<!-- END {name} -->)", re.S)
    if not pattern.search(text):
        sys.exit(f"index.html is missing the <!-- BEGIN {name} --> / <!-- END {name} --> markers")
    return pattern.sub(lambda m: f"{m.group(1)}{content}{m.group(3)}", text, count=1)


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
    for i, project in enumerate(projects):
        prev = projects[i - 1] if i > 0 else None
        nxt = projects[i + 1] if i < total - 1 else None
        page = project_page(project, i + 1, total, prev, nxt)
        (out_dir / f"{project['slug']}.html").write_text(page, encoding="utf-8")

    for stale in out_dir.glob("*.html"):
        if stale.stem not in slugs:
            stale.unlink()
            print(f"removed stale page {stale.name}")

    (ROOT / "js" / "ring.js").write_text(
        "// Generated by tools/build.py from data/projects.json. Don't edit by hand.\n"
        f"window.PP_RING = {json.dumps(slugs, indent=2)};\n",
        encoding="utf-8",
    )

    index_path = ROOT / "index.html"
    index = index_path.read_text(encoding="utf-8")
    cards = "\n\n".join(card(p) for p in projects)
    index = replace_between(index, "workshop", f"\n{cards}\n")
    index = replace_between(index, "count", str(total))
    index = replace_between(index, "ring", f"\n{ring_nav(projects[-1], projects[0], '')}\n")
    index_path.write_text(index, encoding="utf-8")

    print(f"built {total} project pages, js/ring.js and index.html")


if __name__ == "__main__":
    main()
