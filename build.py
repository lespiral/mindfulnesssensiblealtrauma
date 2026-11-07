#!/usr/bin/env python3
"""Genera la web estàtica de Mindfulness Sensible al Trauma a la carpeta docs/.

Ús:  python3 build.py

El mateix sistema que espiralosona.com (lespiral/espiralosona): dades en JSON, plantilles Jinja i un sol full d'estils.

- data/site.json: el nom, l'adreça pública, el menú, el contacte, les reserves, el peu i la pàgina d'inici.
- data/pages/<adreça>.json: una pàgina per fitxer (vegeu el README).
- data/articles/<adreça>.json: un article per fitxer → /<adreça>/ ("title", "date", "author", "image", "body").
  Un article amb una data futura no surt fins aquell dia (quan es torni a generar la web).
- Les imatges: a les dades s'escriu el nom del fitxer (p. ex. "01-inicio.jpg").
  Si el fitxer és a src/img/fotos/, surt la imatge; si no, surt un requadre
  marcat «Imatge pendent» i el fitxer s'apunta a IMATGES-PENDENTS.md.

L'adreça pública i si la web ha de sortir als cercadors es configuren a data/site.json,
a "publish": {"url": ..., "index": true/false}.
"""
import json, re, shutil, sys, time, unicodedata
from pathlib import Path
from urllib.parse import urlparse
from jinja2 import Environment, FileSystemLoader, select_autoescape
from markupsafe import Markup, escape

ROOT = Path(__file__).resolve().parent
DATA, SRC, OUT = ROOT / "data", ROOT / "src", ROOT / "docs"
IMG, FOTOS = SRC / "img", SRC / "img" / "fotos"

ICONS = json.loads((SRC / "icons.json").read_text(encoding="utf-8"))

# Tipus de secció que saben pintar les plantilles (src/templates/parts.html, macro «section»)
SECTION_TYPES = {"text", "cards", "pillars", "list", "faq", "note", "cta", "contact", "booking", "anchor",
                 "quote", "steps", "video", "team", "articles", "instagram"}

errors = []
pending_imgs = {}     # fitxer → {"orig": ..., "pages": set()}
current_page = [""]


def icon(name, cls=None):
    if name not in ICONS:
        errors.append(f"{current_page[0]}: la icona {name!r} no és a src/icons.json")
        return ""
    vb = ICONS.get(name + "__vb", "0 0 256 256")
    c = "i" + (" " + cls if cls else "")
    return Markup(f'<svg class="{c}" viewBox="{vb}" fill="currentColor" aria-hidden="true" focusable="false">{ICONS[name]}</svg>')


def slugify(s):
    s = s.replace("l·l", "ll").replace("L·L", "LL")
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")


def pic(path):
    """Una imatge de les dades: "01-inicio.jpg" → la foto de src/img/fotos/01-inicio.jpg si hi és,
    o un requadre «Imagen pendiente» si encara no."""
    if not path:
        return None
    if isinstance(path, dict):
        path = path.get("src")
    name = path.split("/")[-1]
    local = FOTOS / name
    if local.exists():
        return {"ok": True, "src": "fotos/" + name, "name": name}
    p = pending_imgs.setdefault(name, {"orig": "", "pages": set()})
    p["pages"].add(current_page[0])
    return {"ok": False, "name": name, "orig": p["orig"]}


BOLD = re.compile(r"\*\*(.+?)\*\*")
KEEP = ("id", "href", "icon", "type", "band", "image", "photo", "youtube", "map", "style", "align", "layout", "list_icon", "cols", "panel", "phases", "seconds", "start", "stop", "idle", "button")


def bold(v):
    """**text** en qualsevol text d'una secció → negreta. Recorre llistes, targetes i preguntes."""
    if isinstance(v, Markup):
        return Markup(BOLD.sub(r"<strong>\1</strong>", str(v))) if "**" in v else v
    if isinstance(v, str):
        return Markup(BOLD.sub(r"<strong>\1</strong>", str(escape(v)))) if "**" in v else v
    if isinstance(v, list):
        return [bold(x) for x in v]
    if isinstance(v, tuple):
        return tuple(bold(x) for x in v)
    if isinstance(v, dict):
        return {k: (bold(x) if k not in KEEP else x) for k, x in v.items()}
    return v


def htmlify(v):
    """Amb "html": true a la secció, els textos poden portar HTML (enllaços, negretes)."""
    if isinstance(v, str):
        return Markup(v)
    if isinstance(v, list):
        return [htmlify(x) for x in v]
    if isinstance(v, dict):
        return {k: (htmlify(x) if k not in KEEP and k not in ("button", "title") else x) for k, x in v.items()}
    return v


def prepare_sections(sections, where):
    ids = []
    for i, s in enumerate(sections or []):
        t = s.get("type")
        if t not in SECTION_TYPES:
            errors.append(f"{where}: la secció {i + 1} té un tipus desconegut ({t!r}). Tipus possibles: {', '.join(sorted(SECTION_TYPES))}")
            continue
        s["id"] = s.get("id") or (slugify(s["title"]) if s.get("title") else f"seccio-{i + 1}")
        ids.append(s["id"])
        if s.get("html"):
            for k in ("paragraphs", "list", "after", "items", "intro", "before", "blocks"):
                if k in s:
                    s[k] = htmlify(s[k])
        if t == "faq":
            s["items"] = [(q, Markup(a), slugify(q)) for q, a in s.get("items", [])]
        for it in s.get("items", []) if t in ("cards", "pillars", "team", "steps", "contact", "booking") else []:
            if isinstance(it, dict) and it.get("icon") and it["icon"] not in ICONS:
                errors.append(f"{where}: la icona {it['icon']!r} no és a src/icons.json")
        for k in list(s):
            if k not in KEEP:
                s[k] = bold(s[k])
    dup = {i for i in ids if ids.count(i) > 1}
    if dup:
        errors.append(f"{where}: seccions amb el mateix id {sorted(dup)}: posa'ls un \"id\" diferent")
    return sections or []


site = json.loads((DATA / "site.json").read_text(encoding="utf-8"))
SITE_URL = site["publish"]["url"].rstrip("/") + "/"
NOINDEX = not site["publish"].get("index", False)
BASE = urlparse(SITE_URL).path or "/"   # /espiralosona/ a GitHub Pages, / amb domini propi

home = site["home"]
home["sections"] = prepare_sections(home.get("sections"), "data/site.json (home)")
pages = []
for f in sorted((DATA / "pages").glob("*.json")):
    try:
        p = json.loads(f.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        errors.append(f"{f.relative_to(ROOT)}: el JSON no és correcte ({e})")
        continue
    p.setdefault("slug", f.stem)
    if p["slug"] != f.stem:
        errors.append(f"{f.relative_to(ROOT)}: el camp slug ({p['slug']}) ha de ser igual que el nom del fitxer")
    p["sections"] = prepare_sections(p.get("sections"), str(f.relative_to(ROOT)))
    for k in ("kicker", "lead", "sub"):
        if p.get(k):
            p[k] = bold(p[k])
    pages.append(p)
slugs = {p["slug"] for p in pages}

# Articles: data/articles/<adreça>.json → /<adreça>/. "body": paràgrafs (text) i {"h2": ...}, {"h3": ...} o {"note": ...}.
# Amb "html": true, els paràgrafs poden portar enllaços. Els que tenen una data futura encara no es publiquen.
MESOS = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"]


def data_llarga(iso):
    y, m, d = (int(x) for x in iso.split("-"))
    return f"{d} de {MESOS[m - 1]} de {y}"


TODAY = time.strftime("%Y-%m-%d")
articles, n_future = [], 0
for f in sorted((DATA / "articles").glob("*.json")) if (DATA / "articles").exists() else []:
    try:
        a = json.loads(f.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        errors.append(f"{f.relative_to(ROOT)}: el JSON no és correcte ({e})")
        continue
    a["slug"] = f.stem
    if a["slug"] in slugs:
        errors.append(f"{f.relative_to(ROOT)}: ja hi ha una pàgina amb l'adreça /{a['slug']}/")
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", a.get("date", "")):
        errors.append(f"{f.relative_to(ROOT)}: \"date\" ha de ser AAAA-MM-DD")
        continue
    if a["date"] > TODAY:
        n_future += 1
        continue
    a["date_text"] = data_llarga(a["date"])
    texts = [b for b in a["body"] if isinstance(b, str)]
    plain = re.sub(r"<[^>]+>|\*\*", "", texts[0])
    a["summary"] = a.get("summary") or (plain if len(plain) <= 230 else plain[:230].rsplit(" ", 1)[0] + "…")
    a["words"] = sum(len(re.sub(r"<[^>]+>", "", b).split()) for b in texts)
    conv = (lambda x: Markup(x)) if a.get("html") else bold
    a["body"] = [conv(b) if isinstance(b, str) else {k: conv(v) for k, v in b.items()} for b in a["body"]]
    articles.append(a)
articles.sort(key=lambda a: a["date"], reverse=True)

# El menú només pot portar a pàgines que existeixen (o a l'inici, "")
for n in site.get("nav", []):
    for item in [n] + n.get("children", []):
        if item.get("slug") not in slugs | {""} and not item.get("href"):
            errors.append(f"data/site.json (nav): «{item.get('title')}» porta a /{item.get('slug')}/, però no hi ha la pàgina")

if errors:
    print("No s'ha generat la web. Cal arreglar:", *("- " + e for e in errors), sep="\n")
    sys.exit(1)


def cap(s):
    """La primera lletra en majúscula."""
    if not s:
        return s
    out = re.sub(r"^([¿¡«“\"'(]*)(\w)", lambda m: m.group(1) + m.group(2).upper(), str(s), count=1)
    return Markup(out) if isinstance(s, Markup) else out


def youtube_id(u):
    m = re.search(r"(?:youtu\.be/|v=|embed/|shorts/)([\w-]{11})", u or "")
    return m.group(1) if m else ""


env = Environment(loader=FileSystemLoader(SRC / "templates"), autoescape=select_autoescape(["html"]), trim_blocks=True, lstrip_blocks=True)
env.filters["cap"] = cap
env.filters["bold"] = bold
env.filters["ytid"] = youtube_id
env.globals.update(icon=icon, pic=pic, site=site, noindex=NOINDEX, version=str(int(time.time())), articles=articles,
                   logo=(IMG / "logo.png").exists(), favicon=(IMG / "favicon-48.png").exists())

PAGES = []


def render(template, path, slug=None, **ctx):
    current_page[0] = "/" + (path + "/" if path and not path.endswith(".html") else path)
    depth = len([p for p in path.split("/") if p])
    root = ctx.pop("root", "../" * depth)
    canonical = None if path.endswith(".html") else SITE_URL + (path + "/" if path else "")
    if canonical:
        PAGES.append(canonical)
    out = env.get_template(template).render(root=root, aroot=root, canonical=canonical, **ctx)
    dest = OUT / path / "index.html" if not path.endswith(".html") else OUT / path
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(out, encoding="utf-8")
    return out


if OUT.exists():
    shutil.rmtree(OUT)
OUT.mkdir()

pending = render("home.html", "", "", section="", h=home, page_title=home.get("seo_title"), page_description=home.get("description")).count("[PENDENT]")
for p in pages:
    pending += render("page.html", p["slug"], p["slug"], section=p.get("menu") or p["slug"], page_title=p.get("seo_title") or p["title"],
                      page_description=p.get("description") or p.get("lead"), page=p).count("[PENDENT]")
art_section = next((p["slug"] for p in pages if any(s.get("type") == "articles" for s in p["sections"])), "")
for a in articles:
    pending += render("article.html", a["slug"], a["slug"], section=art_section, page_title=a["title"],
                      page_description=a.get("description") or a["summary"], article=a, articles_slug=art_section).count("[PENDENT]")
render("404.html", "404.html", page_title="Página no encontrada", root=BASE)

# Adreces antigues (del Google Sites) que ja no són una pàgina: porten a la nova.
# A data/site.json, "redirects": {"adreça-antiga": "pagina/#seccio" o "https://..."} ("" és l'inici)
REDIRECT = """<!doctype html>
<html lang="es"><head><meta charset="utf-8"><meta name="robots" content="noindex">
<title>{title}</title><link rel="canonical" href="{to}"><meta http-equiv="refresh" content="0; url={to}">
</head><body><p>Esta página ha cambiado de dirección: <a href="{to}">{to}</a></p></body></html>
"""
n_redirects = 0
for old, to in (site.get("redirects") or {}).items():
    old = old.strip("/")
    if old in slugs or old in {a["slug"] for a in articles}:
        errors.append(f"data/site.json (redirects): /{old}/ és una pàgina de la web; no pot portar a una altra")
        continue
    if not to.startswith("http"):
        page = to.split("#")[0].strip("/")
        if page and page not in slugs:
            errors.append(f"data/site.json (redirects): /{old}/ porta a /{page}/, que no existeix")
            continue
        to = SITE_URL + to.lstrip("/")
    dest = OUT / old / "index.html"
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(REDIRECT.format(title=site["name"], to=to), encoding="utf-8")
    n_redirects += 1
if errors:
    print("No s'ha generat la web. Cal arreglar:", *("- " + e for e in errors), sep="\n")
    shutil.rmtree(OUT)
    sys.exit(1)

(OUT / "assets").mkdir(exist_ok=True)
shutil.copy(SRC / "site.css", OUT / "assets" / "site.css")
shutil.copy(SRC / "site.js", OUT / "assets" / "site.js")
if IMG.exists():
    shutil.copytree(IMG, OUT / "assets" / "img")
(OUT / ".nojekyll").write_text("")
if NOINDEX:
    (OUT / "robots.txt").write_text("User-agent: *\nDisallow: /\n")
else:
    (OUT / "robots.txt").write_text(f"User-agent: *\nAllow: /\n\nSitemap: {SITE_URL}sitemap.xml\n")
    today = time.strftime("%Y-%m-%d")
    urls = "".join(f"  <url><loc>{u}</loc><lastmod>{today}</lastmod></url>\n" for u in PAGES)
    (OUT / "sitemap.xml").write_text(f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{urls}</urlset>\n', encoding="utf-8")
if (ROOT / "CNAME").exists():
    shutil.copy(ROOT / "CNAME", OUT / "CNAME")

# La llista d'imatges que falten, per pujar-les (amb el mateix nom) a src/img/fotos/
lines = ["# Imatges pendents", "",
         "Aquestes imatges surten com a requadre «Imagen pendiente» a la web. Per posar-les, desa cada fitxer",
         "a `src/img/fotos/` amb el nom de la primera columna i torna a generar la web (`python3 build.py`).", "",
         "| Fitxer | On surt |", "|---|---|"]
for name, p in sorted(pending_imgs.items()):
    lines.append(f"| `{name}` | {', '.join(sorted(p['pages']))} |")
(ROOT / "IMATGES-PENDENTS.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

print(f"Fet: {len(pages) + 1} pàgines; {len(articles)} articles publicats ({n_future} programats); {n_redirects} adreces antigues redirigides; {len(pending_imgs)} imatges pendents; "
      f"{pending} marques [PENDENT]. adreça={SITE_URL} cercadors={'no' if NOINDEX else 'sí'}")
