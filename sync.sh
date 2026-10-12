#!/usr/bin/env bash
# Install or update the Craft Suite web builds.
#
#   sync.sh                 update every app in apps.txt whose live copy is
#                           not the latest upstream release
#   sync.sh photocraft ...  only these apps
#   sync.sh --force ...     reinstall even if the version already matches
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
VHOSTS=0
WANT=()
for a in "$@"; do
  case "$a" in
    --force) FORCE=1 ;;
    --vhosts) VHOSTS=1 ;;
    -h|--help) sed -n '2,15p' "$0"; exit 0 ;;
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

AI_MARKERS='whisper|kokoro|mobilesam|mediapipe|onnxruntime|\.onnx\b|\.safetensors|\brten\b|\bocrs\b|burn_tensor|burn_core|AI Denoise|AI assistant|Bring your own model'

WORK=$(mktemp -d /var/tmp/craft.XXXXXX)
trap 'rm -rf "$WORK"' EXIT

# Read the list on fd 3: gh and sudo inside the loop would otherwise eat stdin.
while read -r app repo hub <&3; do
  [ -n "$app" ] && wanted "$app" || continue
  live=/var/www/$app.slippylabs.com
  tag=$(gh release view -R "$repo" --json tagName -q .tagName)
  ver=${tag#v}
  have=$(sudo cat "$live/.version" 2>/dev/null || true)
  if [ "$FORCE" = 0 ] && [ "$have" = "$tag" ]; then
    echo "$app: $tag already live"
    continue
  fi
  echo "$app: ${have:-none} -> $tag"

  d=$WORK/$app
  mkdir -p "$d/dl" "$d/x"
  zip=$app-web-$ver.zip
  gh release download "$tag" -R "$repo" -p "$zip" -p SHA256SUMS.txt -D "$d/dl"
  sum=$(awk -v f="$zip" '$2 == f || $2 == "*"f { print $1 }' "$d/dl/SHA256SUMS.txt")
  if [ -z "$sum" ]; then echo "$app: $zip is not in SHA256SUMS.txt" >&2; exit 1; fi
  echo "$sum  $d/dl/$zip" | sha256sum -c --quiet -

  # A release zip is untrusted input: refuse absolute or parent paths rather
  # than relying on unzip's own sanitising.
  if unzip -Z1 "$d/dl/$zip" | grep -qE '(^/|(^|/)\.\.(/|$))'; then
    echo "$app: $zip holds an unsafe path" >&2; exit 1
  fi
  unzip -q "$d/dl/$zip" -d "$d/x"
  src=$d/x/$app-web-$ver
  [ -f "$src/index.html" ] || { echo "$app: no index.html in $zip" >&2; exit 1; }

  # No app here may use AI. A release that adds it is refused and the live
  # build is left alone. The markers are ML runtimes, model formats and the
  # feature names that the four removed apps carried (see apps.txt); "onnx"
  # alone is too loose -- deckcraft's binary holds the bytes "OnnXX".
  ai=$(find "$src" -type f \( -name '*.wasm' -o -name '*.js' \) -exec strings -n 4 {} + |
    LC_ALL=C grep -o -i -E "$AI_MARKERS" | sort -u | paste -sd, - || true)
  if [ -n "$ai" ]; then
    echo "$app: $tag REFUSED -- AI markers in the build: $ai" >&2
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
  find "$src" -type f \( -name '*.wasm' -o -name '*.js' -o -name '*.html' \
    -o -name '*.otf' -o -name '*.ttf' -o -name '*.json' \) -exec gzip -9kfn {} +
  echo "$tag" > "$src/.version"
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
  echo "$app: $tag installed ($(sudo du -sh "$live" | cut -f1))"
done 3< <(grep -v '^#' apps.txt)
