# Craft Suite

Eight of the [ArtCraft](https://getartcraft.com/) "Crafting Apps", hosted on
slippylabs.com each on its own subdomain, exactly as their authors ship them.
This repo is only the glue: the app list, an install/update script and the
nginx vhosts. The apps themselves are open source (Apache-2.0 / MIT) and are
built and released by [storytold](https://github.com/storytold); none of their
code lives here.

| App | Subdomain | Listed on |
|---|---|---|
| PhotoCraft (image editor) | photocraft.slippylabs.com | art.slippylabs.com |
| VectorCraft (vector illustration) | vectorcraft.slippylabs.com | art |
| DesignCraft (page layout) | designcraft.slippylabs.com | art |
| WordCraft (word processor) | wordcraft.slippylabs.com | projects.slippylabs.com |
| GridCraft (spreadsheets) | gridcraft.slippylabs.com | projects |
| DeckCraft (slides) | deckcraft.slippylabs.com | projects |
| CADCraft (CAD + drafting) | cadcraft.slippylabs.com | projects |
| SoundCraft (DAW) | soundcraft.slippylabs.com | projects |

## No AI

None of the apps here may use AI. Four of the twelve ArtCraft apps ship AI
features (all opt-in, but present), so they are not hosted, and their
subdomains 301 to the hub that used to list them (`deploy/retired.conf`):

| Removed | Its AI |
|---|---|
| LightCraft | AI Denoise (an installable ONNX/safetensors model) |
| FilmCraft | Whisper speech-to-text and Kokoro voices, downloaded from Hugging Face |
| EffectCraft | MobileSAM Roto Brush and MediaPipe face tracking |
| PdfCraft | Neural OCR (ocrs/rten) and a bring-your-own-model AI assistant |

`sync.sh` enforces it: before swapping a build in, it scans the wasm and glue
for ML runtimes, model formats and those feature names (`AI_MARKERS`) and
refuses the release, leaving the live build alone, if any turn up. PhotoCraft's
Select Subject and Content-Aware Fill are classical algorithms and pass.

Each one is a static site: an `index.html`, a wasm-bindgen glue module and a
single WebAssembly binary of 13-56 MB. Everything runs in the visitor's
browser; there is no server-side code and nothing is uploaded.

## Updating

```sh
./sync.sh                # every app whose live copy is behind its latest release
./sync.sh photocraft     # just one
./sync.sh --force ...    # reinstall the same version
```

For each app it reads the latest GitHub release, downloads `<app>-web-<ver>.zip`,
checks it against the release's `SHA256SUMS.txt`, refuses any absolute or `..`
path in the zip, strips docs, host samples and stray build output, writes a
`.gz` beside every `.wasm`/`.js`/`.html`/font (served by nginx's `gzip_static`,
so a 25-56 MB binary is never compressed per request), and swaps the new tree
into `/var/www/<app>.slippylabs.com` with a single `mv --exchange`. Staging and
deletion happen in `/var/tmp` (same filesystem), never inside `/var/www`, where
gzip-static-watch would react to every half-written file.
The installed tag is recorded in `.version` there.

## Hub banners

```sh
~/projects/medievalmmo-dev/venv/bin/python tools/shots.py art ~/art.slippylabs.com/shots
~/projects/medievalmmo-dev/venv/bin/python tools/shots.py projects ~/projects.slippylabs.com/shots
```

boots each app against the local origin, waits for its loading overlay to go,
and writes a 640x360 `<app>.webp` of its start screen. Then regenerate that
hub's `shots-manifest.js` and bump its `?v=`.

## nginx

`deploy/vhost.tmpl` renders to one `deploy/<app>.slippylabs.conf` per app:

```sh
./sync.sh --vhosts
sudo cp deploy/*craft.slippylabs.conf /etc/nginx/sites-available/
# then ln -sf each into sites-enabled, nginx -t, reload
```

Hash-named files (`<app>-web-<hash>_bg.wasm` and its `.js`) are cached for a
year as `immutable`; everything else is `no-cache`, because some ArtCraft
builds keep the same file names across releases.

## Cloudflare

Cloudflare does not cache `.wasm` by default, so without a rule every first
visit is served from the origin. One Cache Rule covers the suite:
*hostname ends with `craft.slippylabs.com` and URI path ends with `.wasm`* →
eligible for cache, respect origin TTL.

## Credits

All of these apps are © their authors at
[github.com/storytold](https://github.com/storytold), licensed Apache-2.0 or
MIT; each docroot keeps the licence and notice files from its release.
