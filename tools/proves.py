#!/usr/bin/env python3
"""Prova totes les pàgines de docs/ en mòbil i en ordinador.

Ús:  python3 tools/proves.py [carpeta-de-captures] [--captures]

- Serveix docs/ a http://localhost:8765/ i l'obre amb Playwright (Chrome de /usr/bin/google-chrome),
  bloquejant tot el que no sigui localhost (lletres de Google, mapes, YouTube).
- Per a cada pàgina i amplada: errors de JavaScript, scroll lateral i enllaços interns que no porten enlloc.
- Amb --captures, desa una captura de pàgina sencera de cada pàgina i amplada.
"""
import asyncio, json, sys, threading, functools
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
from urllib.parse import urlparse, unquote

ROOT = Path(__file__).resolve().parent.parent
DOCS = ROOT / "docs"
PORT = 8765
SIZES = [("ordinador", 1440, 900, False), ("mobil", 390, 844, True)]


class Quiet(SimpleHTTPRequestHandler):
    def log_message(self, *a):
        pass


def serve():
    h = functools.partial(Quiet, directory=str(DOCS))
    ThreadingHTTPServer(("127.0.0.1", PORT), h).serve_forever()


def pages():
    out = []
    for f in sorted(DOCS.rglob("index.html")):
        rel = f.parent.relative_to(DOCS).as_posix()
        txt = f.read_text(encoding="utf-8")
        if 'http-equiv="refresh"' in txt:
            continue
        out.append("" if rel == "." else rel + "/")
    return out


def exists(path):
    p = DOCS / unquote(path).lstrip("/")
    return p.is_file() or (p / "index.html").is_file()


async def main(shots, capture):
    from playwright.async_api import async_playwright
    threading.Thread(target=serve, daemon=True).start()
    report, bad_links = {}, set()
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path="/usr/bin/google-chrome", args=["--no-sandbox"])
        for name, w, h, mobile in SIZES:
            ctx = await b.new_context(viewport={"width": w, "height": h}, is_mobile=mobile, has_touch=mobile)
            await ctx.route("**/*", lambda r: r.continue_() if urlparse(r.request.url).hostname in ("localhost", "127.0.0.1") else r.abort())
            for path in pages():
                page = await ctx.new_page()
                errs = []
                page.on("pageerror", lambda e: errs.append(str(e)))
                await page.goto(f"http://localhost:{PORT}/{path}")
                await page.wait_for_timeout(250)
                hgt = await page.evaluate("document.body.scrollHeight")
                for y in range(0, hgt, 700):
                    await page.evaluate(f"window.scrollTo(0,{y})")
                    await page.wait_for_timeout(25)
                await page.evaluate("window.scrollTo(0,0)")
                await page.wait_for_timeout(150)
                info = await page.evaluate("""() => {
                  const de = document.documentElement;
                  const links = [...document.querySelectorAll('a[href]')].map(a => a.href).filter(h => h.startsWith(location.origin));
                  return {sw: de.scrollWidth, cw: de.clientWidth, links, hidden: document.querySelectorAll('.js .reveal:not(.is-in)').length};
                }""")
                for l in info["links"]:
                    u = urlparse(l)
                    if not exists(u.path):
                        bad_links.add(f"{path or '/'} → {u.path}")
                r = report.setdefault(path or "/", {})
                r[name] = {"scroll_lateral": info["sw"] > info["cw"], "errors_js": errs, "sense_mostrar": info["hidden"]}
                if capture:
                    shots.mkdir(parents=True, exist_ok=True)
                    fn = (path.strip("/").replace("/", "_") or "inici") + f"-{name}.png"
                    await page.screenshot(path=str(shots / fn), full_page=True)
                await page.close()
            await ctx.close()
        await b.close()
    problems = {k: v for k, v in report.items() if any(x["scroll_lateral"] or x["errors_js"] or x["sense_mostrar"] for x in v.values())}
    print(json.dumps({"pagines": len(report), "amb_problemes": problems, "enllacos_trencats": sorted(bad_links)}, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    asyncio.run(main(Path(args[0]) if args else ROOT / "captures", "--captures" in sys.argv))
