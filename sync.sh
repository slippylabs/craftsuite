#!/usr/bin/env bash
# Install or update the Craft Suite web builds.
#
#   sync.sh                 update every app in apps.txt whose live copy is
#                           not the latest upstream release
#   sync.sh photocraft ...  only these apps
#   sync.sh --force ...     reinstall even if the version already matches
#   sync.sh --rebuild ...   rebuild the version that is live now instead of
#                           moving to the latest release (after a patch
#                           change)
#   sync.sh --vhosts        render deploy/<app>.slippylabs.conf from the
#                           template (does not touch /etc/nginx)
#
# Each app is a static site from its GitHub release's <app>-web-<ver>.zip:
# index.html, a wasm-bindgen glue module and one hash-named .wasm. Nothing
# here runs the downloaded code; it is checked against the release's
# SHA256SUMS, unpacked, precompressed and swapped into /var/www.
set -euo pipefail
cd "$(dirname "$0")"

FORCE=0
REBUILD=0
VHOSTS=0
WANT=()
for a in "$@"; do
  case "$a" in
    --force) FORCE=1 ;;
    --rebuild) REBUILD=1 FORCE=1 ;;
    --vhosts) VHOSTS=1 ;;
    -h|--help) sed -n '2,18p' "$0"; exit 0 ;;
    -*) echo "unknown option $a" >&2; exit 2 ;;
    *) WANT+=("$a") ;;
  esac
done

title() {
  case "$1" in
    cadcraft) echo CADCraft ;;
    pdfcraft) echo PdfCraft ;;
    *) local s=${1%craft}; echo "${s^}Craft" ;;
  esac
}

wanted() {
  [ ${#WANT[@]} -eq 0 ] && return 0
  local w; for w in "${WANT[@]}"; do [ "$w" = "$1" ] && return 0; done
  return 1
}

if [ "$VHOSTS" = 1 ]; then
  grep -v '^#' apps.txt | while read -r app repo hub; do
    [ -n "$app" ] && wanted "$app" || continue
    sed -e "s/@APP@/$app/g" -e "s/@TITLE@/$(title "$app")/g" deploy/vhost.tmpl \
      > "deploy/$app.slippylabs.conf"
    echo "deploy/$app.slippylabs.conf"
  done
  exit 0
fi

# No app here may use AI, checked two ways (see the loop below).
#
# ML_CODE: compiled machine-learning code. Rust keeps the source path of
# every function that can panic, so a linked ML runtime or AI module leaves
# its path in the wasm (".../rten-0.26.0/src/...", "crates/segment/src/
# mobilesam.rs"). The leading "/" keeps crates like i_key_sort-0.11.0 from
# matching "ort". Applies to every app.
ML_CODE='/(candle-(core|nn|transformers)|rten(-[a-z]+)?|ocrs|ort(-sys)?|burn(-[a-z]+)?|tract-[a-z]+|onnxruntime[a-z-]*)-[0-9][0-9.]*/src|crates/(speech/src/whisper|tts/src/kokoro|segment/src/(mobilesam|mediapipe|tflite|nn|pt)\.rs|denoise/src|faces/src)'
# AI_NAMES: AI feature names and model formats. Applies to apps used as
# had none (no noai/<app>.py), so a name means a release added one. NOT to
# the noai ones: their patches remove the features, but the names survive
# as dead text (every language's "Automatically transcribe clips" in the
# i18n tables), so for those ML_CODE is the proof.
# PROMO: the ArtCraft community and project links -- the Discord invite,
# getartcraft.com, the GitHub repo and its issue tracker -- that every app
# shows in its header, Home, About and Help menu. delink/<app>.py removes
# them; any URL left in the build means a button or menu item still opens
# one. (The UI text, "Join the ArtCraft Discord", can survive in translation
# tables, so the URL is the proof.) The craft-fonts repo is named only in the
# font attribution, which stays.
PROMO='discord\.(gg|com)/|getartcraft\.com|github\.com/storytold/[a-z-]*'
AI_NAMES='whisper|kokoro|mobilesam|mediapipe|onnxruntime|\.onnx\b|\.safetensors|\brten\b|\bocrs\b|burn_tensor|burn_core|AI Denoise|AI assistant|Bring your own model'

WORK=$(mktemp -d /var/tmp/craft.XXXXXX)
trap 'rm -rf "$WORK"' EXIT

# Read the list on fd 3: gh and sudo inside the loop would otherwise eat stdin.
while read -r app repo hub mode <&3; do
  [ -n "$app" ] && wanted "$app" || continue
  live=/var/www/$app.slippylabs.com
  have=$(sudo cat "$live/.version" 2>/dev/null || true)
  if [ "$REBUILD" = 1 ] && [ -n "$have" ]; then
    tag=${have%%+*}
  else
    tag=$(gh release view -R "$repo" --json tagName -q .tagName)
  fi
  ver=${tag#v}
  # A source-built app is recorded as "<tag>+src", so a later switch between
  # the upstream zip and our build is never mistaken for "already live".
  want=$tag
  [ "${mode:-}" = src ] && want=$tag+src
  if [ "$FORCE" = 0 ] && [ "$have" = "$want" ]; then
    echo "$app: $want already live"
    continue
  fi
  echo "$app: ${have:-none} -> $want"

  d=$WORK/$app
  mkdir -p "$d/dl" "$d/x"
  zip=$app-web-$ver.zip
  if [ "${mode:-}" = src ]; then
    # Upstream's zip carries promo links (and for some, AI features); build
    # it ourselves with them taken out (delink/<app>.py, noai/<app>.py).
    # This takes minutes, not seconds.
    built=$(noai/build.sh "$app" "$repo" "$tag" "$d/dl")
    [ "$(basename "$built")" = "$zip" ] || { echo "$app: build wrote $built, expected $zip" >&2; exit 1; }
  else
    gh release download "$tag" -R "$repo" -p "$zip" -p SHA256SUMS.txt -D "$d/dl"
    sum=$(awk -v f="$zip" '$2 == f || $2 == "*"f { print $1 }' "$d/dl/SHA256SUMS.txt")
    if [ -z "$sum" ]; then echo "$app: $zip is not in SHA256SUMS.txt" >&2; exit 1; fi
    echo "$sum  $d/dl/$zip" | sha256sum -c --quiet -
  fi

  # A release zip is untrusted input: refuse absolute or parent paths rather
  # than relying on unzip's own sanitising.
  if unzip -Z1 "$d/dl/$zip" | grep -qE '(^/|(^|/)\.\.(/|$))'; then
    echo "$app: $zip holds an unsafe path" >&2; exit 1
  fi
  unzip -q "$d/dl/$zip" -d "$d/x"
  src=$d/x/$app-web-$ver
  [ -f "$src/index.html" ] || { echo "$app: no index.html in $zip" >&2; exit 1; }

  # No app here may use AI or link out to the ArtCraft community: a build
  # that does -- an upstream release that adds it, or a patch that missed
  # something -- is refused and the live build is left alone.
  strs=$(find "$src" -type f \( -name '*.wasm' -o -name '*.js' \) -exec strings -n 4 {} +)
  ai=$(LC_ALL=C grep -o -E "$ML_CODE" <<<"$strs" | sort -u | paste -sd, - || true)
  if [ -z "$ai" ] && [ ! -f "noai/$app.py" ]; then
    ai=$(LC_ALL=C grep -o -i -E "$AI_NAMES" <<<"$strs" | sort -u | paste -sd, - || true)
  fi
  if [ -n "$ai" ]; then
    echo "$app: $want REFUSED -- AI in the build: $ai" >&2
    exit 1
  fi
  promo=$(LC_ALL=C grep -o -i -E "$PROMO" <<<"$strs" | grep -v -i 'storytold/craft-fonts' | sort -u | paste -sd, - || true)
  if [ -n "$promo" ]; then
    echo "$app: $want REFUSED -- promo links in the build: $promo" >&2
    exit 1
  fi

  # Host-specific samples and docs; nginx is configured by deploy/ instead.
  rm -f "$src/README.md" "$src/HOSTING.md" "$src/_headers" "$src/.htaccess"
  # LightCraft 0.6.0's zip also carries its whole cargo target dir -- rlibs,
  # build-script binaries, proc-macro .so files, ~150 MB none of which the
  # page loads. Drop it wherever it turns up.
  rm -rf "$src/.fingerprint" "$src/build" "$src/deps" "$src/incremental" \
    "$src/examples" "$src"/.cargo-*lock
  # Some builds ship .br/.gz copies. This nginx has no brotli module, and our
  # own gzip replaces theirs so every app is compressed the same way.
  find "$src" -type f -name '*.br' -delete
  # Some builds (lightcraft, filmcraft, effectcraft) keep the same module and
  # glue names in every release, so they can only be served no-cache -- and
  # Cloudflare's zone Browser Cache TTL still lets a browser hold them 4 h,
  # long enough to pair an old glue with a new module after an update. Give
  # the pair content-hashed names like the Trunk builds have, and rewrite the
  # text files that name them (index.html, worker.js, the glue, a service
  # worker's precache list). The binaries only name worker.js and
  # audio-worklet.js, which stay as they are.
  for w in "$src"/*_bg.wasm; do
    [ -e "$w" ] || continue
    base=$(basename "$w" _bg.wasm)
    [[ $base =~ -[0-9a-f]{8,}$ ]] && continue    # already hashed
    [ -f "$src/$base.js" ] || continue
    new=$base-$(cat "$w" "$src/$base.js" | sha256sum | cut -c1-16)
    mv "$w" "$src/${new}_bg.wasm"
    mv "$src/$base.js" "$src/$new.js"
    find "$src" -type f \( -name '*.html' -o -name '*.js' -o -name '*.webmanifest' -o -name '*.json' \) \
      -exec sed -i -e "s/${base}_bg\.wasm/${new}_bg.wasm/g" -e "s/${base}\.js/${new}.js/g" {} +
    if grep -rqs -e "${base}_bg\.wasm" -e "${base}\.js" "$src" --include='*.html' --include='*.js' --include='*.webmanifest' --include='*.json'; then
      echo "$app: a reference to $base survived the rename" >&2; exit 1
    fi
  done
  find "$src" -type f \( -name '*.wasm' -o -name '*.js' -o -name '*.html' \
    -o -name '*.otf' -o -name '*.ttf' -o -name '*.json' \) -exec gzip -9kfn {} +
  echo "$want" > "$src/.version"
  find "$src" -type d -exec chmod 755 {} +
  find "$src" -type f -exec chmod 644 {} +

  # Stage and delete OUTSIDE /var/www, and only rename into it. gzip-static-watch
  # reacts to every write there: it would gzip a half-copied 56 MB wasm itself,
  # and racing an rm -rf it leaves orphaned .gz files behind (see the studio's
  # tools/deploy.sh). $WORK is on the same filesystem, so these are renames.
  sudo chown -R root:root "$src"
  if [ -d "$live" ]; then
    # One rename swaps the two trees, so a visitor never sees a half-copied
    # site; the old build ends up in $WORK to be deleted with it.
    sudo mv --exchange -T "$src" "$live"
    sudo rm -rf "$src"
  else
    sudo mv -T "$src" "$live"
  fi
  rm -rf "$d"
  echo "$app: $want installed ($(sudo du -sh "$live" | cut -f1))"
done 3< <(grep -v '^#' apps.txt)
