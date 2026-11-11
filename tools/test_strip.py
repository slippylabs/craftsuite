#!/usr/bin/env python3
"""The "Craft Suite / Home" strip (backstrip.py) on every app, at the ORIGIN (Cloudflare bypassed):
two links, the app's canvas starting right under the 28 px strip and running to the bottom, nothing
covering the app's own menu bar, and no page errors.

    /home/slippy/projects/medievalmmo-dev/venv/bin/python tools/test_strip.py [app ...]
"""
import os, sys
from playwright.sync_api import sync_playwright

HERE = os.path.dirname(os.path.abspath(__file__))
APPS = [l.split()[0] for l in open(os.path.join(HERE, "..", "apps.txt")) if l.strip() and not l.startswith("#")]
ONLY = [a for a in sys.argv[1:] if not a.startswith("-")]
fails = passes = 0


def check(ok, msg, detail=""):
    global fails, passes
    if ok: passes += 1
    else: fails += 1
    print(("  ok   " if ok else "  FAIL ") + msg + ("" if ok or not detail else "  (%s)" % detail))


with sync_playwright() as p:
    b = p.chromium.launch(args=["--host-resolver-rules=MAP *.slippylabs.com 127.0.0.1:443", "--use-gl=angle", "--use-angle=swiftshader", "--enable-unsafe-swiftshader"])
    for app in (ONLY or APPS):
        pg = b.new_page(viewport={"width": 1280, "height": 800})
        errs = []
        pg.on("pageerror", lambda e: errs.append(str(e)[:100]))
        pg.goto("https://%s.slippylabs.com/" % app, wait_until="load", timeout=120000)
        pg.wait_for_timeout(1500)
        links = pg.evaluate("[...document.querySelectorAll('#sl-cs-strip a')].map(a => [a.textContent.trim(), a.href])")
        check([l[1] for l in links] == ["https://crafts.slippylabs.com/", "https://slippylabs.com/"], "%s: strip links to the Craft Suite and Home" % app, str(links))
        box = pg.evaluate("""(() => { const s = document.getElementById('sl-cs-strip'), c = document.querySelector('canvas');
            if (!s || !c) return null; const a = s.getBoundingClientRect(), r = c.getBoundingClientRect();
            return [a.top, a.height, r.top, r.bottom, r.width, innerHeight, innerWidth]; })()""")
        check(box and box[0] == 0 and box[1] == 28 and abs(box[2] - 28) < 1 and abs(box[3] - box[5]) < 1 and abs(box[4] - box[6]) < 1,
              "%s: the canvas starts under the strip and fills the rest" % app, str(box))
        check(not errs, "%s: no page errors" % app, str(errs[:2]))
        pg.close()
    b.close()
print("\nstrip: %d passed, %d failed" % (passes, fails))
sys.exit(1 if fails else 0)
