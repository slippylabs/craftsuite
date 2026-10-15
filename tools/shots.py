#!/usr/bin/env python3
"""Hub card banners for the Craft Suite apps.

    shots.py crafts   ~/crafts.slippylabs.com/shots  # all twelve
    shots.py music    ~/music.slippylabs.com/shots   # SoundCraft; then tools/stamp_shots.py there
    shots.py crafts DIR photocraft vectorcraft    # just these

Each app is booted headlessly against the LOCAL origin (so a fresh install
can be photographed before Cloudflare has seen it), left to settle on its own
start screen, and written as a 640x360 <app>.webp. There is nothing to drive:
every app opens on a start screen or a bundled demo document that is already
the picture worth showing. Run with the Playwright venv:

    ~/projects/medievalmmo-dev/venv/bin/python tools/shots.py crafts DIR

Then regenerate the hub's shots-manifest.js and bump its ?v= (see the hub's
README). Exits non-zero if any app fails to boot.
"""
import io
import pathlib
import sys

from PIL import Image
from playwright.sync_api import sync_playwright

ROOT = pathlib.Path(__file__).resolve().parent.parent

# The overlay each app removes (or hides) once its wasm is running.
LOADING = "document.querySelector('[id$=\"_loading\"], #loading')"


def apps_for(hub):
    out = []
    for line in (ROOT / 'apps.txt').read_text().splitlines():
        f = line.split()
        if f and not f[0].startswith('#') and hub in f[2].split(','):
            out.append(f[0])
    return out


def main():
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    hub, dest = sys.argv[1], pathlib.Path(sys.argv[2])
    apps = sys.argv[3:] or apps_for(hub)
    bad = []
    with sync_playwright() as p:
        b = p.chromium.launch(args=[
            '--host-resolver-rules=MAP *.slippylabs.com 127.0.0.1',
            # WebGL2 with no GPU on the box
            '--use-angle=swiftshader', '--enable-unsafe-swiftshader',
            '--ignore-gpu-blocklist'])
        for a in apps:
            ctx = b.new_context(viewport={'width': 1280, 'height': 720},
                                ignore_https_errors=True)
            pg = ctx.new_page()
            failed = []
            pg.on('requestfailed', lambda r: failed.append(r.url))
            pg.goto(f'https://{a}.slippylabs.com/', wait_until='load', timeout=120000)
            try:
                pg.wait_for_function(
                    f"!{LOADING} || getComputedStyle({LOADING}).display === 'none'",
                    timeout=120000)
            except Exception:
                bad.append(f'{a}: never left its loading screen')
                ctx.close()
                continue
            pg.wait_for_timeout(4000)   # first frames, demo documents, fonts
            if failed:
                bad.append(f'{a}: failed requests {failed[:3]}')
            im = Image.open(io.BytesIO(pg.screenshot())).convert('RGB')
            im.resize((640, 360), Image.LANCZOS).save(dest / f'{a}.webp', quality=86)
            print(f'{dest / a}.webp')
            ctx.close()
        b.close()
    if bad:
        sys.exit('\n'.join(bad))


if __name__ == '__main__':
    main()
