#!/usr/bin/env python3
"""Render one static page per locale from src/shell.html + content/*.json.

English builds to /index.html, every other locale to /<code>/index.html.
Run `python3 build.py` after editing any content file, then commit the output.
"""

import html
import json
import pathlib
import shutil
import sys

ROOT = pathlib.Path(__file__).parent
SITE = "https://bladestatistics.com"

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


def render(code, c, shell, css, locales, names):
    body = shell
    canonical = f"{SITE}/" if code == "en" else f"{SITE}/{code}/"

    scalars = {
        "lang": c["lang"],
        "dir": c.get("dir", "ltr"),
        "canonical": canonical,
        "ogLocale": c["ogLocale"],
        "css": css,
        "svgMac": MAC_SVG,
        "svgWin": WIN_SVG,
        "langLabel": c["langLabel"],
        "alternates": alternates_block(locales),
        "blockFacts": facts_block(c),
        "blockRows": rows_block(c),
        "blockSteps": steps_block(c),
        "blockFamilies": families_block(c),
        "blockPoints": points_block(c),
        "blockFaq": faq_block(c),
        "blockLangs": langs_block(code, names),
        "ctaStrings": json.dumps(
            {"downloadFor": c["cta"]["downloadFor"], "version": c["cta"]["version"]},
            ensure_ascii=False,
        ),
        "langScript": LANG_SCRIPT
        % {"locales": json.dumps(ORDER), "current": code},
    }
    for section in ("meta", "hero", "cta", "shot", "spss", "how", "methods", "trust", "get", "faq", "footer"):
        for key, value in c[section].items():
            if isinstance(value, str):
                scalars[f"{section}.{key}"] = value
    for key, value in c["trust"]["cross"].items():
        scalars[f"cross.{key}"] = value

    for key in ("meta.title", "meta.description", "meta.ogTitle", "meta.ogDescription", "shot.alt", "cta.more"):
        scalars[key] = attr(scalars[key])

    for key, value in scalars.items():
        body = body.replace("{{" + key + "}}", str(value))

    leftover = body.split("{{")[1:]
    if leftover:
        name = leftover[0].split("}}")[0]
        sys.exit(code + ": unresolved placeholder {{" + name + "}}")
    return body


def main():
    shell = (ROOT / "src" / "shell.html").read_text(encoding="utf-8")
    css = (ROOT / "src" / "_css.html").read_text(encoding="utf-8")
    locales = {code: load(code) for code in ORDER}
    names = {code: locales[code]["name"] for code in ORDER}

    for code in ORDER:
        page = render(code, locales[code], shell, css, locales, names)
        if code == "en":
            out = ROOT / "index.html"
        else:
            (ROOT / code).mkdir(exist_ok=True)
            out = ROOT / code / "index.html"
        out.write_text(page, encoding="utf-8")
        print(f"  {code:3} -> {out.relative_to(ROOT)}  ({len(page) // 1024} KB)")

    urls = "\n".join(
        "  <url><loc>%s</loc></url>" % (SITE + "/" if code == "en" else f"{SITE}/{code}/")
        for code in ORDER
    )
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
    print("  sitemap.xml, robots.txt")

    # locales that were dropped from ORDER should not linger as stale pages
    for path in ROOT.iterdir():
        if path.is_dir() and len(path.name) == 2 and path.name not in ORDER:
            shutil.rmtree(path)
            print(f"  removed stale {path.name}/")


if __name__ == "__main__":
    main()
