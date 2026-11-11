#!/usr/bin/env python3
"""A slim "Craft Suite / Home" strip across the top of a Craft Suite app: backstrip.py DOCROOT

The user asked (2026-11-10) for a way back on every page, the Craft Suite included -- earlier
(2026-10-11) these apps were served with no Slippy chrome at all, so this is the ONLY addition:
one 28 px bar, nothing else restyled. The app's canvas is a full-window egui UI with its own menu
bar at the very top, so the bar never floats over it: the page's canvas is moved to start under
the bar (found by the first <canvas id> in index.html -- three apps style `canvas` generically and
PDFCraft keeps its canvas in the page flow, so the rule targets the element itself).

Idempotent: the block is marked and replaced on a re-run. sync.sh runs it on every install, after
mobilefit.py; run it by hand on a live docroot via a staged copy.
"""
import pathlib
import re
import sys

H = 28
START, END = "<!-- slippylabs:backstrip -->", "<!-- /slippylabs:backstrip -->"


def block(canvas_id):
    return f"""{START}
<style>
#sl-cs-strip{{position:fixed;top:0;left:0;right:0;height:{H}px;z-index:2147483000;display:flex;align-items:center;gap:4px;padding:0 8px;box-sizing:border-box;background:#17181c;border-bottom:1px solid #2c2f36;font:600 13px/1 system-ui,-apple-system,"Segoe UI",sans-serif}}
#sl-cs-strip a{{color:#d6d8de;text-decoration:none;padding:5px 9px;border-radius:5px;white-space:nowrap}}
#sl-cs-strip a:hover,#sl-cs-strip a:focus-visible{{background:#2a2d35;color:#fff;outline:none}}
#sl-cs-strip span{{color:#4a4e58}}
#{canvas_id}{{position:absolute !important;top:{H}px !important;left:0 !important;right:auto !important;bottom:auto !important;width:100% !important;height:calc(100% - {H}px) !important}}
@media print{{#sl-cs-strip{{display:none}}}}
</style>
<nav id="sl-cs-strip" aria-label="Slippy Labs"><a href="https://crafts.slippylabs.com/">&larr; Craft Suite</a><span aria-hidden="true">&middot;</span><a href="https://slippylabs.com/">&#8962; Home</a></nav>
{END}"""


def fix(root):
    p = pathlib.Path(root) / "index.html"
    s = p.read_text(encoding="utf-8")
    m = re.search(r'<canvas\b[^>]*\bid="([^"]+)"', s)
    if not m:
        raise SystemExit(f"{p}: no <canvas id> to move under the strip")
    s = re.sub(re.escape(START) + r".*?" + re.escape(END) + r"\n?", "", s, flags=re.S)
    i = s.index("<body")
    j = s.index(">", i) + 1
    s = s[:j] + "\n" + block(m.group(1)) + s[j:]
    p.write_text(s, encoding="utf-8")
    print(f"{p}: strip above #{m.group(1)}")


if __name__ == "__main__":
    for r in sys.argv[1:]:
        fix(r)
