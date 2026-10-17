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
- Touch devices get a one-time "best on a desktop" notice (dismissed per app,
  remembered in localStorage when it is available). It is sized from
  visualViewport.scale, because the page is laid out 1280 px wide and a
  fixed CSS size would be tiny in portrait and huge in landscape.

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
(function () {{
  if (!matchMedia('(pointer: coarse)').matches) return;
  var KEY = 'slippylabs:desktop-notice-dismissed';
  try {{ if (localStorage.getItem(KEY)) return; }} catch (e) {{}}
  function show() {{
    var app = (document.title || 'This app').split(/[\\s\\u2014|-]/)[0] || 'This app';
    var wrap = document.createElement('div');
    wrap.id = 'slippylabs-desktop-notice';
    wrap.setAttribute('role', 'dialog');
    wrap.setAttribute('aria-modal', 'true');
    wrap.setAttribute('aria-labelledby', 'sl-dn-title');
    wrap.innerHTML =
      '<div class="sl-dn-card">' +
      '<div class="sl-dn-title" id="sl-dn-title">Best on a desktop</div>' +
      '<p>' + app.replace(/[<>&]/g, '') + ' is a full desktop editor. It runs on a phone, but a bigger screen with a mouse and keyboard makes it much easier to use.</p>' +
      '<button type="button">Continue anyway</button>' +
      '</div>';
    var css = document.createElement('style');
    css.textContent =
      '#slippylabs-desktop-notice{{position:fixed;inset:0;z-index:2147483647;display:flex;align-items:center;justify-content:center;background:rgba(0,0,0,.55);font-family:system-ui,-apple-system,"Segoe UI",Roboto,sans-serif}}' +
      '#slippylabs-desktop-notice .sl-dn-card{{box-sizing:border-box;width:22em;max-width:90%;background:#1d1f24;color:#e8e8ea;border:1px solid #3a3d45;border-radius:.75em;padding:1.25em 1.25em 1em;box-shadow:0 .5em 2em rgba(0,0,0,.5)}}' +
      '#slippylabs-desktop-notice .sl-dn-title{{font-weight:700;font-size:1.2em;margin:0 0 .5em}}' +
      '#slippylabs-desktop-notice p{{margin:0 0 1em;line-height:1.45}}' +
      '#slippylabs-desktop-notice button{{display:block;width:100%;min-height:2.75em;font:inherit;font-weight:600;border:0;border-radius:.5em;background:#3b82f6;color:#fff;cursor:pointer}}';
    function size() {{
      var z = (window.visualViewport && visualViewport.scale) || 1;
      wrap.style.fontSize = (16 / z) + 'px';
    }}
    size();
    if (window.visualViewport) visualViewport.addEventListener('resize', size);
    var btn = wrap.querySelector('button');
    function close(e) {{
      if (e) {{ e.preventDefault(); e.stopPropagation(); }}
      try {{ localStorage.setItem(KEY, '1'); }} catch (err) {{}}
      if (window.visualViewport) visualViewport.removeEventListener('resize', size);
      wrap.remove(); css.remove();
    }}
    btn.addEventListener('click', close);
    btn.addEventListener('touchend', close);
    ['pointerdown', 'touchstart', 'mousedown', 'keydown'].forEach(function (t) {{
      wrap.addEventListener(t, function (e) {{ e.stopPropagation(); }});
    }});
    document.head.appendChild(css);
    document.body.appendChild(wrap);
    btn.focus();
  }}
  if (document.body) show(); else document.addEventListener('DOMContentLoaded', show);
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
