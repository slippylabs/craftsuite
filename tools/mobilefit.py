#!/usr/bin/env python3
"""Make a Craft Suite app usable on a phone: mobilefit.py DOCROOT

Every app is a desktop-class egui UI drawn into one full-window canvas. Below
about 1280 CSS px its panels have fixed widths that no longer fit: menus cut
off, the document area shrinks to a sliver, and welcome text wraps one letter
per line. So index.html's viewport tag is replaced with a 1280 px layout
viewport. A phone then lays the app out exactly as a small desktop and scales
it to the screen; desktop browsers ignore the tag, so nothing changes there.

Two things come with it:

- devicePixelRatio is scaled by the page zoom. eframe sizes its canvas as CSS
  size x devicePixelRatio, so a 1280 px layout on a 2.6x phone would ask for a
  3360 px wide canvas (about 3360 x 6800 in portrait) to show on a 1080 px
  screen. Reporting DPR x zoom (never below 1) renders at the screen's real
  resolution instead. It's a getter, so rotating the phone re-reads it.
  eframe takes its UI scale from devicePixelRatio but, where the browser has
  it (Chrome), its canvas size from ResizeObserver's devicePixelContentBoxSize,
  which ignores the override. The two would disagree and the UI would draw
  into a corner of the canvas, so on touch devices that property is hidden
  and eframe falls back to CSS size x devicePixelRatio, as it does on Safari.
  Desktop keeps it (pixel-exact canvases at fractional scaling). Headless
  Chrome's device emulation does not scale that box, so only a real phone
  shows the mismatch.
- Inputs get a 16 px font. iOS zooms into any focused field smaller than
  that, and eframe focuses a hidden text field whenever the keyboard opens.

Idempotent: the block is marked and replaced on a re-run. sync.sh runs it on
every install; run it by hand on a live docroot via a staged copy.
"""
import pathlib
import re
import sys

WIDTH = 1280
START, END = '<!-- slippylabs:mobilefit -->', '<!-- /slippylabs:mobilefit -->'
BLOCK = f'''{START}
<meta name="viewport" content="width={WIDTH}, user-scalable=no">
<style>input, textarea, select {{ font-size: 16px !important; }} html {{ -webkit-text-size-adjust: 100%; }}</style>
<script>
(function () {{
  var d = Object.getOwnPropertyDescriptor(window, 'devicePixelRatio') ||
          Object.getOwnPropertyDescriptor(Window.prototype, 'devicePixelRatio');
  if (!d || !d.get || !window.visualViewport) return;
  if (matchMedia('(pointer: coarse)').matches && window.ResizeObserverEntry)
    delete ResizeObserverEntry.prototype.devicePixelContentBoxSize;
  Object.defineProperty(window, 'devicePixelRatio', {{
    configurable: true,
    get: function () {{
      var r = d.get.call(window), z = Math.min(1, visualViewport.scale || 1);
      return Math.max(1, r * z);
    }}
  }});
}})();
</script>
{END}'''


def fit(html):
    if START in html:
        return re.sub(re.escape(START) + r'.*?' + re.escape(END), lambda m: BLOCK, html, flags=re.S)
    new, n = re.subn(r'<meta\s+name="viewport"[^>]*>', lambda m: BLOCK, html, count=1)
    if n != 1:
        sys.exit('mobilefit: no viewport meta to replace')
    return new


def main():
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    page = pathlib.Path(sys.argv[1]) / 'index.html'
    html = page.read_text()
    out = fit(html)
    if 'name="viewport"' in out.replace(BLOCK, ''):
        sys.exit('mobilefit: a second viewport meta survived')
    page.write_text(out)


if __name__ == '__main__':
    main()
