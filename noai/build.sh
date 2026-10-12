#!/usr/bin/env bash
# Build an ArtCraft app's web zip from source with its AI features removed.
#
#   noai/build.sh <app> <repo> <tag> <outdir>
#
# Clones <repo> at <tag>, applies noai/<app>.py (which fails if any edit no
# longer matches upstream), checks out the craft-fonts commit the release
# workflow pins, and runs the app's own packaging/web/package.sh -- the same
# recipe its release CI uses. Prints the path of the zip it wrote.
#
# Needs: rustup target wasm32-unknown-unknown, wasm-bindgen-cli matching the
# app's pin, binaryen wasm-opt, and trunk (pdfcraft) on PATH. The build runs
# in a user scope capped at 9 GB with no swap, at nice 15: this box has hung
# on memory pressure before, and a fat-LTO wasm link is the biggest thing it
# does.
set -euo pipefail
app=$1 repo=$2 tag=$3 out=$4
HERE="$(cd "$(dirname "$0")" && pwd)"
export PATH="$HOME/.local/bin:$HOME/.cargo/bin:$PATH"

work=$(mktemp -d /var/tmp/noai-build.XXXXXX)
trap 'rm -rf "$work"' EXIT
git clone -q --depth 1 --branch "$tag" "https://github.com/$repo" "$work/src" 2>/dev/null
python3 -E -s "$HERE/$app.py" "$work/src" >&2

fonts=$(grep -A3 'repository: storytold/craft-fonts' "$work/src/.github/workflows/release.yml" 2>/dev/null |
  grep -oE 'ref: [0-9a-f]{40}' | head -1 | cut -d' ' -f2 || true)
if [ -n "$fonts" ]; then
  git clone -q --filter=blob:none https://github.com/storytold/craft-fonts "$work/fonts"
  git -C "$work/fonts" checkout -q "$fonts"
  export CRAFT_FONTS_DIR="$work/fonts" CRAFT_FONTS_REQUIRED=1
fi

export CARGO_BUILD_JOBS=${CARGO_BUILD_JOBS:-3}
# One target dir per app that outlives the build, so a rebuild recompiles
# only what the patch or a new release touched (~5 min, not ~22).
export CARGO_TARGET_DIR=/var/tmp/noai-target/$app
mkdir -p "$CARGO_TARGET_DIR"
case $app in
  effectcraft)
    # Its 58 MB module's LTO link is the biggest allocation this box makes.
    # On a box already deep in swap, systemd-oomd killed it twice at that
    # step (peak 3.7 GB, under the scope's cap -- the kill is for user.slice
    # PRESSURE). Without cross-crate LTO the link is far lighter; wasm-opt
    # still optimises the result.
    export CARGO_PROFILE_RELEASE_LTO=false CARGO_PROFILE_RELEASE_CODEGEN_UNITS=16 ;;
esac
( cd "$work/src" &&
  systemd-run --user --scope -q -p MemoryMax=9G -p MemorySwapMax=0 \
    nice -n 15 bash packaging/web/package.sh ) >&2

zip=$(ls "$work/src/dist/release/$app-web-"*.zip | head -1)
mkdir -p "$out"
cp "$zip" "$out/"
echo "$out/$(basename "$zip")"
