# Craft Suite

The twelve [ArtCraft](https://getartcraft.com/) "Crafting Apps", hosted on
slippylabs.com each on its own subdomain, with no AI features and no links
out to the ArtCraft community (see below).
This repo is only the glue: the app list, an install/update script and the
nginx vhosts. The apps themselves are open source (Apache-2.0 / MIT) and are
built and released by [storytold](https://github.com/storytold); none of their
code lives here.

| App | Subdomain | Listed on |
|---|---|---|
| PhotoCraft (image editor) | photocraft.slippylabs.com | art.slippylabs.com |
| VectorCraft (vector illustration) | vectorcraft.slippylabs.com | art |
| LightCraft (photo library + raw developer) * | lightcraft.slippylabs.com | art |
| FilmCraft (video editor) * | filmcraft.slippylabs.com | art |
| EffectCraft (motion graphics) * | effectcraft.slippylabs.com | art |
| DesignCraft (page layout) | designcraft.slippylabs.com | art |
| WordCraft (word processor) | wordcraft.slippylabs.com | projects.slippylabs.com |
| GridCraft (spreadsheets) | gridcraft.slippylabs.com | projects |
| PdfCraft (PDF workbench) * | pdfcraft.slippylabs.com | projects |
| DeckCraft (slides) | deckcraft.slippylabs.com | projects |
| CADCraft (CAD + drafting) | cadcraft.slippylabs.com | projects |
| SoundCraft (DAW) | soundcraft.slippylabs.com | music |

Every app is built here from source with its promo links removed; \* also
with its AI features removed.

## No promo links

Upstream, every app links out to the ArtCraft community and project: a
Discord pill in the header or title bar, "Join our Discord" buttons on the
Home/start screen and in About, Help-menu entries for Discord, getartcraft.com,
the app's page, its GitHub repo and issue tracker (and, in some, help docs
that only open GitHub), and contributors' GitHub profiles in About >
Contributors. None of that belongs on a hosted copy, so `noai/build.sh` builds
every app from source with `delink/<app>.py` applied, which removes those
buttons, menu items and commands. Contributor names stay, as plain text, and so
do the licence and copyright lines. Three apps' sample content plugged the app
(DeckCraft's sample deck, FilmCraft's Credits template, WordCraft's sample
document and its LaTeX export header); those lines go too.

Each patch ends with `scrub()` (`noai/_patch.py`), which blanks every
remaining promo URL in the source -- link tables, tooltips and every
language's translation of them -- so nothing left in the app can open one.

## No AI

No app here may use AI. The rule: an AI feature inside an app is taken out;
an app that is mostly AI (ArtCraft's own AI image/video studio) is not hosted.

Four apps ship AI features, so their builds also apply a patch,
`noai/<app>.py`, that removes those features:

| App | What the patch removes |
|---|---|
| LightCraft | AI Denoise (controls and Settings tab), the Object and Describe AI masks, face detection and recognition (People view, face boxes, Faces settings, face-model dialog) and every `denoise.*`/`faces.*` command. The Subject/Sky/Background masks are classical heuristics and stay. |
| FilmCraft | Speech-to-text (the Transcribe button, Transcribe Sequence, auto-transcribe, the Transcription settings, model downloads) and the Kokoro "natural voices" with their download. Imported transcripts and the built-in formant voices are not AI and stay. |
| EffectCraft | The MobileSAM and MediaPipe networks (compiled out), their Settings pages and the `roto.model.*`/`face.model.*` commands. Roto Brush and face tracking keep their classical engines. |
| PdfCraft | OCR (the ocrs/rten neural recogniser and the Scan & OCR tools) and the bring-your-own-model AI assistant. |

Each patch names the exact upstream text it replaces and fails if that text
has moved, so a new release can't quietly keep a feature the patch used to
remove. These are modified builds of Apache-2.0/MIT software; the
modifications are the patches in `delink/` and `noai/`.

`sync.sh` then checks every build before it goes live, and refuses it,
leaving the live build alone, if:

- **`ML_CODE`**: the wasm contains compiled machine-learning code. Rust keeps
  the source path of anything that can panic, so a linked ML runtime or AI
  module shows up by path (`/rten-0.26.0/src/...`, `crates/faces/src/...`).
  Applies to every app.
- **`AI_NAMES`**: the build names an AI feature or model format. Applies only
  to the eight apps that never had one (no `noai/<app>.py`); a patched app
  keeps those names as dead text in its translation tables after the feature
  is gone.
- **`PROMO`**: the build still contains a Discord invite, a getartcraft.com
  URL or a storytold GitHub URL (the craft-fonts repo, named in font
  attribution, excepted). Applies to every app.

Building needs the `wasm32-unknown-unknown` target, `wasm-bindgen-cli` at the
version the app pins, binaryen's `wasm-opt`, Trunk and `zip`. A first build
takes 18-25 minutes (a few with a warm `/var/tmp/noai-target/<app>`) and runs
in a no-swap, nice-15 user scope capped at 4 GB (`NOAI_MEM_MAX`). Run them
one at a time.

Each one is a static site: an `index.html`, a wasm-bindgen glue module and a
single WebAssembly binary of 13-56 MB. Everything runs in the visitor's
browser; there is no server-side code and nothing is uploaded.

## Updating

```sh
./sync.sh                # every app whose live copy is behind its latest release
./sync.sh photocraft     # just one
./sync.sh --force ...    # reinstall the same version
./sync.sh --rebuild ...  # rebuild the live version (after a patch change)
```

Rows marked `src` in `apps.txt` (all of them) are built from source instead
of downloaded and recorded as `<tag>+src`. A new upstream release has to get
past both patches -- `sub()` fails if the text it removes has moved -- and the
three checks; fix the patch, don't loosen a check.

For each app it reads the latest GitHub release and either builds it (`src`)
or downloads `<app>-web-<ver>.zip` and checks it against the release's
`SHA256SUMS.txt`. It refuses any absolute or `..`
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
~/projects/medievalmmo-dev/venv/bin/python tools/shots.py music ~/music.slippylabs.com/shots
```

boots each app against the local origin, waits for its loading overlay to go,
and writes a 640x360 `<app>.webp` of its start screen. Then regenerate that
hub's `shots-manifest.js` and bump its `?v=` (the music hub bakes hashes
into its HTML instead: run its `tools/stamp_shots.py`).

## nginx

`deploy/vhost.tmpl` renders to one `deploy/<app>.slippylabs.conf` per app:

```sh
./sync.sh --vhosts
sudo cp deploy/*craft.slippylabs.conf /etc/nginx/sites-available/
# then ln -sf each into sites-enabled, nginx -t, reload
```

Hash-named files (`<app>-web-<hash>_bg.wasm` and its `.js`) are cached for a
year as `immutable`; everything else is `no-cache`. Builds that ship an
unhashed module and glue (LightCraft, FilmCraft, EffectCraft) get them renamed
by `sync.sh` to `<name>-<sha256/16>` with every reference rewritten, so every
app's big files are content-addressed and a new release always has new names.

## Cloudflare

Cloudflare does not cache `.wasm` by default, so without a rule every first
visit is served from the origin. One Cache Rule covers the suite (added
2026-10-12: URI Full wildcard `https://*craft.slippylabs.com/*.wasm`, eligible
for cache, defaults for the rest; the dashboard's "no proxied record for
craft.slippylabs.com" warning is expected):
*hostname ends with `craft.slippylabs.com` and URI path ends with `.wasm`* →
eligible for cache, respect origin TTL.

## Credits

All of these apps are © their authors at
[github.com/storytold](https://github.com/storytold), licensed Apache-2.0 or
MIT; each docroot keeps the licence and notice files from its release.
