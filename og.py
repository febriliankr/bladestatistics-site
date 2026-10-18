#!/usr/bin/env python3
"""Render the 1200x630 share images in share/<code>.jpg from the hero copy.

Each image is the homepage hero in miniature: the daylight lake artwork,
the logo, and that locale's headline and lede. Needs Google Chrome and
Pillow. Run it after changing hero copy, then run build.py.
"""

import html
import http.server
import json
import subprocess
import tempfile
import threading
from pathlib import Path

from PIL import Image

from build import ORDER

ROOT = Path(__file__).resolve().parent
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
PORT = 8799

TEMPLATE = """<!doctype html>
<html lang="{lang}" dir="{dir}">
<meta charset="utf-8" />
<style>
  * {{ box-sizing: border-box; }}
  html, body {{ margin: 0; width: 1200px; height: 630px; overflow: hidden; }}
  body {{
    position: relative;
    display: flex;
    flex-direction: column;
    justify-content: flex-end;
    align-items: center;
    padding: 0 90px 92px;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Inter, "Noto Sans", sans-serif;
    color: #242a23;
    text-align: center;
    background: #fff url(/assets/daylight-lake.webp) center 30% / cover no-repeat;
  }}
  body::before {{
    content: "";
    position: absolute;
    inset: 0;
    background: linear-gradient(180deg, #fff0 0%, #fff0 18%, #fffc 52%, #fff 78%);
  }}
  .brand, h1, p {{ position: relative; }}
  .brand {{
    position: absolute;
    top: 46px;
    inset-inline-start: 56px;
    display: flex;
    align-items: center;
    gap: 12px;
    font-size: 30px;
    font-weight: 600;
    letter-spacing: -0.04em;
    color: #192715;
  }}
  .brand img {{ width: 44px; height: 44px; }}
  h1 {{
    max-width: 980px;
    margin: 0 0 22px;
    font-size: 66px;
    line-height: 1.06;
    font-weight: 430;
    letter-spacing: -0.05em;
    text-wrap: balance;
  }}
  h1 em {{ font-style: normal; color: #303c2c; }}
  h1, p {{ word-break: auto-phrase; }}
  p {{
    max-width: 760px;
    margin: 0;
    font-size: 25px;
    line-height: 1.5;
    color: #5d6559;
    text-wrap: balance;
  }}
</style>
<div class="brand"><img src="/logo.png" alt="" />Blade</div>
<h1>{h1a}<em>{h1em}</em>{h1b}</h1>
<p>{lede}</p>
</html>
"""


def main():
    class Quiet(http.server.SimpleHTTPRequestHandler):
        def log_message(self, *args):
            pass

    server = http.server.ThreadingHTTPServer(
        ("127.0.0.1", PORT), lambda *a: Quiet(*a, directory=str(ROOT))
    )
    threading.Thread(target=server.serve_forever, daemon=True).start()
    out_dir = ROOT / "share"
    out_dir.mkdir(exist_ok=True)
    try:
        with tempfile.TemporaryDirectory(dir=ROOT) as tmp:
            for code in ORDER:
                hero = json.loads((ROOT / "content" / f"{code}.json").read_text(encoding="utf-8"))["hero"]
                page = TEMPLATE.format(
                    lang=code,
                    dir="rtl" if code == "ar" else "ltr",
                    **{k: html.escape(hero[k]) for k in ("h1a", "h1em", "h1b", "lede")},
                )
                src = Path(tmp) / f"{code}.html"
                src.write_text(page, encoding="utf-8")
                shot = Path(tmp) / f"{code}.png"
                subprocess.run(
                    [CHROME, "--headless=new", "--disable-gpu", "--hide-scrollbars",
                     "--window-size=1200,630", "--virtual-time-budget=2000",
                     f"--screenshot={shot}", f"http://127.0.0.1:{PORT}/{Path(tmp).name}/{code}.html"],
                    check=True, capture_output=True,
                )
                Image.open(shot).convert("RGB").save(out_dir / f"{code}.jpg", quality=86, optimize=True)
                print(f"  {code:3} -> share/{code}.jpg")
    finally:
        server.shutdown()


if __name__ == "__main__":
    main()
