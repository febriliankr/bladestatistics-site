#!/usr/bin/env python3
"""Render one static page per locale from src/shell.html + content/*.json.

English builds to /index.html, every other locale to /<code>/index.html.
Run `python3 build.py` after editing any content file, then commit the output.

One source, two domains. bladestatistics.com is built into the repository
root and served by GitHub Pages. blade.skalatec.com is the same site with a
broader English pitch, built into skalatec/dist/ (not committed) and served
by the Cloudflare Worker in skalatec/. Canonical URLs on both point at
bladestatistics.com, so search engines treat it as the primary site.
"""

import html
import hashlib
import json
import pathlib
import shutil
import sys

ROOT = pathlib.Path(__file__).parent
SITE = "https://bladestatistics.com"

# Per-domain differences. "overrides" names a content file merged over the
# English copy, so a domain can reword a few strings without its own locale.
SITES = {
    "bladestatistics": {
        "out": ROOT,
        "overrides": None,
        "workflowsHref": "https://blade.skalatec.com/#workflows",
    },
    "skalatec": {
        "out": ROOT / "skalatec" / "dist",
        "overrides": "skalatec.en.json",
        "workflowsHref": "#workflows",
    },
}

SIGN_IN = {
    "en": "Sign in", "es": "Iniciar sesión", "pt": "Entrar", "fr": "Se connecter",
    "de": "Anmelden", "it": "Accedi", "id": "Masuk", "ru": "Войти",
    "ar": "تسجيل الدخول", "hi": "साइन इन", "zh": "登录", "ja": "ログイン", "ko": "로그인",
}

# order controls the switcher menu; English first, then by native name
ORDER = ["en", "es", "pt", "fr", "de", "it", "id", "ru", "ar", "hi", "zh", "ja", "ko"]

MAC_SVG = (
    '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12.152 6.896c-.948 0-2.415-1.078-3.96-1.04-2.04.027-3.91 '
    '1.183-4.961 3.014-2.117 3.675-.546 9.103 1.519 12.09 1.013 1.454 2.208 3.09 3.792 3.039 1.52-.065 2.09-.987 '
    '3.935-.987 1.831 0 2.35.987 3.96.948 1.637-.026 2.676-1.48 3.676-2.948 1.156-1.688 1.636-3.325 1.662-3.415-.039'
    '-.013-3.182-1.221-3.22-4.857-.026-3.04 2.48-4.494 2.597-4.559-1.429-2.09-3.623-2.324-4.39-2.376-2-.156-3.675 '
    '1.09-4.61 1.09zM15.53 3.83c.843-1.012 1.4-2.427 1.245-3.83-1.207.052-2.662.805-3.532 1.818-.78.896-1.454 '
    '2.338-1.273 3.714 1.338.104 2.715-.688 3.559-1.701"/></svg>'
)
WIN_SVG = (
    '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M2 3.5 10.6 2.3v9.2H2V3.5zm10.2-1.4L22 .8v10.7h-9.8V2.1zM2 '
    '13.1h8.6v9.2L2 21.1v-8zm10.2 0H22v10.7l-9.8-1.3v-9.4z"/></svg>'
)

# Meta pixel for bladestatistics.com, owned by the "Blade Statistics" business.
# The id is public by design — it ships in client JS on every page — so it
# lives here rather than in an env var. Nothing else about the ads setup
# belongs in this repo: it is public, and access tokens never go in it.
PIXEL_ID = "1373789871610184"

PIXEL_SCRIPT = """<script>
!function(f,b,e,v,n,t,s)
{if(f.fbq)return;n=f.fbq=function(){n.callMethod?
n.callMethod.apply(n,arguments):n.queue.push(arguments)};
if(!f._fbq)f._fbq=n;n.push=n;n.loaded=!0;n.version='2.0';
n.queue=[];t=b.createElement(e);t.async=!0;
t.src=v;s=b.getElementsByTagName(e)[0];
s.parentNode.insertBefore(t,s)}(window,document,'script',
'https://connect.facebook.net/en_US/fbevents.js');
fbq('init', '%(pixel)s');
fbq('track', 'PageView');
</script>
<noscript><img height="1" width="1" style="display:none" alt=""
src="https://www.facebook.com/tr?id=%(pixel)s&ev=PageView&noscript=1" /></noscript>"""

LANG_SCRIPT = """<script>
// Runs before anything paints, so nobody sees the wrong language flash past.
// A pick from the switcher is stored and outranks the browser's preference.
(function () {
  var LOCALES = %(locales)s;
  var CURRENT = "%(current)s";
  function go(code) {
    if (code === CURRENT || LOCALES.indexOf(code) === -1) return false;
    location.replace((code === "en" ? "/" : "/" + code + "/") + location.hash);
    return true;
  }
  var stored = null;
  try { stored = localStorage.getItem("bladeLang"); } catch (e) {}
  if (stored) { go(stored); return; }
  // Sniff once per session. Otherwise a visitor who navigates back to a
  // deliberately shared translation gets bounced away from it again.
  try {
    if (sessionStorage.getItem("bladeLangSniffed")) return;
    sessionStorage.setItem("bladeLangSniffed", "1");
  } catch (e) {}
  var tags = navigator.languages || [navigator.language || ""];
  for (var i = 0; i < tags.length; i++) {
    var base = String(tags[i]).toLowerCase().split("-")[0];
    if (base === "in") base = "id";  // legacy code some browsers still send
    if (LOCALES.indexOf(base) !== -1) { go(base); return; }
  }
})();
</script>"""


def load(code):
    return json.loads((ROOT / "content" / f"{code}.json").read_text(encoding="utf-8"))


def attr(text):
    """Content strings carry inline markup; attributes must not."""
    return html.escape(html.unescape(str(text)).replace("<code>", "").replace("</code>", ""), quote=True)


def facts_block(c):
    return "\n".join(
        f'    <div><b>{v}</b><span>{label}</span></div>' for v, label in c["facts"]
    )


def rows_block(c):
    out = []
    for label, other, blade in c["spss"]["rows"]:
        out.append(
            "          <tr>\n"
            f"            <td>{label}</td>\n"
            f"            <td>{other}</td>\n"
            f"            <td>{blade}</td>\n"
            "          </tr>"
        )
    return "\n".join(out)


def steps_block(c):
    out = []
    for step in c["how"]["steps"]:
        quote = f'\n        <p class="quote">{step["quote"]}</p>' if step.get("quote") else ""
        out.append(
            '      <li class="reveal">\n'
            f'        <h3>{step["h3"]}</h3>\n'
            f'        <p>{step["p"]}</p>{quote}\n'
            "      </li>"
        )
    return "\n".join(out)


def families_block(c):
    out = []
    for fam in c["methods"]["families"]:
        chips = "".join(f"<span>{x}</span>" for x in fam["chips"])
        out.append(
            '    <div class="fam reveal">\n'
            f'      <h3>{fam["h3"]}</h3>\n'
            f'      <div class="chips">{chips}</div>\n'
            "    </div>"
        )
    return "\n".join(out)


def points_block(c):
    out = []
    for pt in c["trust"]["points"]:
        extra = f'\n      <p>{pt["p2"]}</p>' if pt.get("p2") else ""
        out.append(
            '    <div class="point reveal">\n'
            f'      <h3>{pt["h3"]}</h3>\n'
            f'      <p>{pt["p"]}</p>{extra}\n'
            "    </div>"
        )
    return "\n".join(out)


def release_block(c):
    out = []
    for item in c["release"]["items"]:
        out.append(
            '    <li class="reveal">\n'
            f'      <h3>{item["h3"]}</h3>\n'
            f'      <p>{item["p"]}</p>\n'
            "    </li>"
        )
    return "\n".join(out)


def faq_block(c):
    out = []
    for q, a in c["faq"]["items"]:
        out.append(
            '    <details class="reveal">\n'
            f"      <summary>{q}</summary>\n"
            f"      <p>{a}</p>\n"
            "    </details>"
        )
    return "\n".join(out)


def langs_block(active, names):
    out = []
    for code in ORDER:
        href = "/" if code == "en" else f"/{code}/"
        current = ' aria-current="true"' if code == active else ""
        out.append(f'        <a href="{href}" data-lang="{code}"{current}>{names[code]}</a>')
    return "\n".join(out)


def alternates_block(locales):
    out = []
    for code in ORDER:
        href = f"{SITE}/" if code == "en" else f"{SITE}/{code}/"
        out.append(f'<link rel="alternate" hreflang="{locales[code]["lang"]}" href="{href}" />')
    out.append(f'<link rel="alternate" hreflang="x-default" href="{SITE}/" />')
    return "\n".join(out)


def merge(base, extra):
    out = dict(base)
    for key, value in extra.items():
        out[key] = merge(base[key], value) if isinstance(value, dict) and isinstance(base.get(key), dict) else value
    return out


FLOW_CSS = """  <style>
    .flow-section { padding-bottom: 112px; }
    .flow-head {
      display: flex; justify-content: space-between; align-items: flex-end; gap: 50px;
      border-top: 1px solid var(--line); padding-top: 80px; margin-bottom: 40px;
    }
    .flow-head h2 { max-width: 560px; margin-bottom: 0; }
    .flow-head p { max-width: 400px; margin: 0; font-size: 17px; color: var(--muted); }
    .flow-steps {
      display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 20px;
      list-style: none; margin: 0; padding: 0;
    }
    .flow-step { border: 1px solid var(--line); border-radius: 20px; background: var(--panel); padding: 28px; }
    .flow-label {
      display: block; margin-bottom: 40px; color: #5f6858; font-size: 12px; letter-spacing: 0.1em;
      text-transform: uppercase; font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
    }
    .flow-step h3 { margin: 0 0 10px; font-size: 21px; font-weight: 500; letter-spacing: -0.03em; }
    .flow-step p { margin: 0; color: var(--muted); font-size: 15px; line-height: 1.75; }
    .flow-step code {
      font-family: ui-monospace, SFMono-Regular, Menlo, monospace; font-size: 0.85em;
      background: #eceee6; border-radius: 5px; padding: 1px 5px;
    }
    @media (max-width: 900px) {
      .flow-head { display: block; }
      .flow-head p { margin-top: 18px; }
      .flow-steps { grid-template-columns: minmax(0, 1fr); }
      .flow-label { margin-bottom: 18px; }
    }
    @media (max-width: 640px) {
      .flow-section { padding-bottom: 65px; }
      .flow-head { padding-top: 50px; margin-bottom: 27px; }
      .flow-head p { font-size: 15px; line-height: 1.75; }
      .flow-step { padding: 22px; border-radius: 16px; }
    }
  </style>
"""


def workflows_block(c):
    """Only content that defines "workflows" gets the section."""
    w = c.get("workflows")
    if not w:
        return ""
    steps = "\n".join(
        '      <li class="flow-step">\n'
        f'        <span class="flow-label">{st["label"]}</span>\n'
        f'        <h3>{st["title"]}</h3>\n'
        f'        <p>{st["text"]}</p>\n'
        "      </li>"
        for st in w["steps"]
    )
    return (
        FLOW_CSS
        + '  <section class="flow-section wrap" id="workflows" aria-labelledby="flow-title">\n'
        '    <div class="flow-head reveal">\n'
        f'      <h2 id="flow-title">{w["title"]}</h2>\n'
        f'      <p>{w["text"]}</p>\n'
        "    </div>\n"
        f'    <ol class="flow-steps reveal">\n{steps}\n    </ol>\n'
        "  </section>"
    )


def render(code, c, shell, css, locales, names, site):
    body = shell
    canonical = f"{SITE}/" if code == "en" else f"{SITE}/{code}/"

    scalars = {
        "lang": c["lang"],
        "dir": c.get("dir", "ltr"),
        "canonical": canonical,
        "ogLocale": c["ogLocale"],
        "css": css,
        "designVersion": design_version(),
        "svgMac": MAC_SVG,
        "svgWin": WIN_SVG,
        "langLabel": c["langLabel"],
        "alternates": alternates_block(locales),
        "blockFacts": facts_block(c),
        "blockRows": rows_block(c),
        "blockSteps": steps_block(c),
        "blockFamilies": families_block(c),
        "blockPoints": points_block(c),
        "blockRelease": release_block(c),
        "blockFaq": faq_block(c),
        "blockLangs": langs_block(code, names),
        "blockWorkflows": workflows_block(c),
        "workflowsHref": site["workflowsHref"],
        "nav.signIn": SIGN_IN[code],
        "ctaStrings": json.dumps(
            {"downloadFor": c["cta"]["downloadFor"], "version": c["cta"]["version"]},
            ensure_ascii=False,
        ),
        "langScript": LANG_SCRIPT
        % {"locales": json.dumps(ORDER), "current": code},
        "pixel": PIXEL_SCRIPT % {"pixel": PIXEL_ID},
    }
    for section in ("meta", "hero", "cta", "shot", "spss", "how", "methods", "trust", "release", "get", "faq", "footer", "simple"):
        for key, value in c[section].items():
            if isinstance(value, str):
                scalars[f"{section}.{key}"] = value
    for key, value in c["trust"]["cross"].items():
        scalars[f"cross.{key}"] = value

    for key in ("meta.title", "meta.description", "meta.ogTitle", "meta.ogDescription", "shot.alt", "cta.more", "simple.ask", "simple.results", "simple.script", "simple.workspaceAlt", "simple.replay", "simple.videoPlay", "simple.figureOpen", "simple.figureClose", "simple.figurePrev", "simple.figureNext"):
        scalars[key] = attr(scalars[key])

    for key, value in scalars.items():
        body = body.replace("{{" + key + "}}", str(value))

    leftover = body.split("{{")[1:]
    if leftover:
        name = leftover[0].split("}}")[0]
        sys.exit(code + ": unresolved placeholder {{" + name + "}}")
    return body


# Standalone pages are English-only for now. The legal wording stays in one
# reviewed language until a human translates it.
PAGES = {
    "support": "support.html",
    "pricing": "pricing.html",
    "privacy": "privacy.html",
    "data-deletion": "data-deletion.html",
    "terms": "terms.html",
}


# Account and billing pages: built for both domains, kept out of the sitemap.
# Paths are relative to the site root.
HIDDEN_PAGES = {
    "login/index.html": "login.html",
    "account/index.html": "account.html",
    "billing/success.html": "billing-success.html",
    "billing/cancel.html": "billing-cancel.html",
}


def design_version():
    """Cache-busting hash for the shared homepage stylesheet and script."""
    assets = ROOT / "assets"
    return hashlib.sha256((assets / "landing.css").read_bytes() + (assets / "landing.js").read_bytes()).hexdigest()[:12]


# The demo deck reuses the homepage's mock windows, charts, and plan cards,
# lifted from the rendered English page so the two can never drift apart.
DEMO_BLOCKS = {
    "ask": '<div class="app-preview mock ask-demo" id="preview-ask"',
    "results": '<div class="app-preview mock" id="preview-results"',
    "script": '<div class="app-preview mock script-demo" id="preview-script"',
    "workspace": '<div class="mock ws-mock"',
    "pain": '<figure class="pain reveal">',
    "plans": '<div class="plans reveal">',
}


def extract_element(html, start):
    """The element that begins with `start`, through its matching close tag."""
    i = html.index(start)
    tag = start[1:].split()[0].rstrip(">")
    depth, pos = 0, i
    while True:
        opening = html.find("<" + tag, pos)
        closing = html.find("</" + tag + ">", pos)
        if opening != -1 and opening < closing:
            depth += 1
            pos = opening + len(tag) + 1
        else:
            depth -= 1
            pos = closing + len(tag) + 3
            if depth == 0:
                return html[i:pos]


def demo_blocks(en_page):
    blocks = {}
    for key, start in DEMO_BLOCKS.items():
        block = extract_element(en_page, start)
        first, rest = block.split(">", 1)
        blocks["block." + key] = first.replace(" hidden", "").replace(" reveal", "") + ">" + rest
    return blocks


def render_doc(src, css, doc_css, extra=None):
    page = (ROOT / "src" / src).read_text(encoding="utf-8")
    for key, value in (extra or {}).items():
        page = page.replace("{{" + key + "}}", value)
    page = (
        page.replace("{{css}}", css)
        .replace("{{docCss}}", doc_css)
        .replace("{{pixel}}", PIXEL_SCRIPT % {"pixel": PIXEL_ID})
        .replace("{{designVersion}}", design_version())
    )
    leftover = page.split("{{")[1:]
    if leftover:
        sys.exit(src + ": unresolved placeholder {{" + leftover[0].split("}}")[0] + "}}")
    return page


def build_site(key, site, shell, css, doc_css, base_locales, names):
    out_root = site["out"]
    out_root.mkdir(parents=True, exist_ok=True)
    locales = dict(base_locales)
    if site["overrides"]:
        extra = json.loads((ROOT / "content" / site["overrides"]).read_text(encoding="utf-8"))
        locales["en"] = merge(locales["en"], extra)

    for code in ORDER:
        page = render(code, locales[code], shell, css, locales, names, site)
        if code == "en":
            en_page = page
        out = out_root / "index.html" if code == "en" else out_root / code / "index.html"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(page, encoding="utf-8")
        print(f"  {key:15} {code:3} -> {out.relative_to(ROOT)}  ({len(page) // 1024} KB)")

    for name, src in PAGES.items():
        (out_root / name).mkdir(parents=True, exist_ok=True)
        (out_root / name / "index.html").write_text(render_doc(src, css, doc_css), encoding="utf-8")
    for path, src in HIDDEN_PAGES.items():
        (out_root / path).parent.mkdir(parents=True, exist_ok=True)
        (out_root / path).write_text(render_doc(src, css, doc_css), encoding="utf-8")
    (out_root / "demo").mkdir(parents=True, exist_ok=True)
    (out_root / "demo" / "index.html").write_text(
        render_doc("demo.html", css, doc_css, demo_blocks(en_page)), encoding="utf-8"
    )
    print(f"  {key:15} pages -> {', '.join(list(PAGES) + list(HIDDEN_PAGES))}, demo/index.html")

    # locales that were dropped from ORDER should not linger as stale pages
    for path in out_root.iterdir():
        if path.is_dir() and len(path.name) == 2 and path.name not in ORDER:
            shutil.rmtree(path)
            print(f"  removed stale {path.relative_to(ROOT)}/")


def copy_static(out_root):
    """The second domain needs the files GitHub Pages serves from the repo root."""
    for name in ("assets", "app.png", "logo.png"):
        src = ROOT / name
        dst = out_root / name
        if src.is_dir():
            shutil.copytree(src, dst, dirs_exist_ok=True)
        else:
            shutil.copy2(src, dst)


def main():
    shell = (ROOT / "src" / "shell.html").read_text(encoding="utf-8")
    css = (ROOT / "src" / "_css.html").read_text(encoding="utf-8")
    doc_css = (ROOT / "src" / "_doc-css.html").read_text(encoding="utf-8")
    locales = {code: load(code) for code in ORDER}
    names = {code: locales[code]["name"] for code in ORDER}

    for key, site in SITES.items():
        build_site(key, site, shell, css, doc_css, locales, names)
    copy_static(SITES["skalatec"]["out"])

    urls = "\n".join(
        "  <url><loc>%s</loc></url>" % (SITE + "/" if code == "en" else f"{SITE}/{code}/")
        for code in ORDER
    ) + "".join(f"\n  <url><loc>{SITE}/{name}</loc></url>" for name in PAGES)
    (ROOT / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + urls
        + "\n</urlset>\n",
        encoding="utf-8",
    )
    (ROOT / "robots.txt").write_text(
        f"User-agent: *\nAllow: /\nSitemap: {SITE}/sitemap.xml\n", encoding="utf-8"
    )
    # The mirror points crawlers at the primary site's sitemap.
    (SITES["skalatec"]["out"] / "robots.txt").write_text(
        f"User-agent: *\nAllow: /\nSitemap: {SITE}/sitemap.xml\n", encoding="utf-8"
    )
    print("  sitemap.xml, robots.txt")


if __name__ == "__main__":
    main()
